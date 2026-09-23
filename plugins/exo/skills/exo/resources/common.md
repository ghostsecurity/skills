# common.md: the exo MCP substrate

Shared by all three intents: the read primitives for walking runs, the worker capability rules, the DTO discovery discipline, the write primitives for changing resources, the unprobeable nodes, the in-bundle invocation note, and the production and secret safety rules. Read this before any intent recipe.

## Orientation

Every intent talks to one exo workspace through that workspace's MCP server. Several connections may be present, so confirm which one you are on before acting, per the connection rules in `SKILL.md`. If you do not know the workspace ID, call `whoami` first. It is the only tool callable without a workspace context. If the exo MCP tools are absent or `whoami` fails, read `resources/bootstrap.md` and follow it before going further. The `workspace_id` it returns travels as the `X-Workspace-Id` header, which the server configuration supplies. Later tool calls do not accept it as an argument.

## Read primitives (walking runs)

- `list_resources(type, parent_id?)` returns every resource of a type in the workspace. The response key is the plural of the type.
- `get_resource(type, id, parent_id?)` returns one resource. For a skill, this is the cheapest way to find its `active_version_id`.
- Nested resources such as `task_metric` require `parent_id` on both calls.
- `list_runs(workflow_id, ...)` returns a workflow's runs, most recent first, with optional status and since filters.
- `get_run(run_id)` returns one run's metadata: status, timing, token usage, environment, effective model, and whether it is still active or terminal.
- `summarize_run_events(run_id)` returns a compact aggregate of one run: counts per event type, distinct tool calls with counts, distinct errors with one sample each, and token totals. Call this BEFORE get_run_events to decide whether to drill in at all and which event types to fetch.
- `get_run_events(run_id, event_types=[...])` returns the raw event stream, filtered. Never page this without an event_types filter. Page with after_sequence.
- `list_run_children(run_id)` returns the child runs of a multi-step run, one per executed step. Each child is a first-class run with its own runner, environment, task, agent, and model. Recurse into children rather than treating them as opaque payloads on a step event.
- `get_skill_version(skill_id, version_id, with_content)` returns a skill bundle's files. Its `manifest` carries the `requires`, `warnings`, and `addon_suggestion` the import recorded for that version.
- `list_worker_capabilities()` returns what the instance's workers can run. See Worker capabilities below.
- `list_approval_requests(run_id)` returns the pending and resolved approval gates for a run.
- `query_observability(category='events', run_id, ...)` gives a cross-run log view. Bucketed `traffic` observability cannot be filtered by run ID.

## The dependency graph

Every run depends on a chain of resources, and a run-level failure can originate in any of them:

workflow definition, then step or child run, then task, then skill and its active version, then environment, then credential, then model, with the runner, the worker pool and image it belongs to, agent, credential proxy, and gateway dispatch alongside.

Pivot IDs to harvest from `get_run` and from failure-event payloads: `workflow_id`, `task_id`, `source_id`, `execution_id`, `parent_run_id`, every child via `list_run_children`, `runner_id`, `agent_id`, `environment_id`, `required_capabilities`, the effective model, and `started_at` and `finished_at` for the observability window.

Proxy requests attributed to a run surface in `get_run_events` as `traffic_accepted` or `traffic_blocked`, and the payloads can carry `credential_id`, host, path, status, and error code. There is no MCP query for raw credential-use rows. Read credential metadata with `get_resource` and mark secret validity unprobed unless the events prove the result.

## Worker capabilities

Workers do not all carry the same command line tools. Each worker pool runs its own image, and a capability names a tool set an image provides, such as `aws` or `gcloud`. A run goes only to a worker that provides every capability it requires. The requirement is the union of three things: the `requires` of every skill the environment binds, the environment's own `required_capabilities`, and what its credentials imply. A run that requires nothing can land on any worker, so a skill that uses a tool without declaring it breaks the day a leaner pool is added.

`list_worker_capabilities` returns the whole picture in one call:

- `base_tools`: commands every worker image carries. They need no capability.
- `pools`: each pool with its `live_workers`, its configured `replicas`, the capabilities its image provides, and the tools its workers report, with versions.
- `capabilities`: every capability a skill or environment may require. `provided_by` lists the pools that can serve it right now. An empty list means it exists in the catalog but no pool can serve it.
- `addons_available`: whether a new add-on can be built on this instance, with `addons_unavailable_reason` when it cannot.
- `guidance`: the steps to reason in, how to write `requires`, and the exact `exo-addon.json` shape with a worked example. Follow it rather than a remembered shape, because it changes with the instance.

Resolve every command line tool a skill runs, in this order:

1. The tool is in `base_tools`: declare nothing.
2. A capability provides it: list that capability under `metadata.requires` in the skill's `SKILL.md`, even when every pool provides it today.
3. Neither holds. Read `addons_available` before going further, because it decides whether the fleet can change at all.

When `addons_available` is true, a platform admin can change what the workers carry:

- The catalog lists the capability but `provided_by` is empty: still require it, and record what the platform admin has to do, in the skill's description and in your report. That is adding the add-on to a pool, or giving workers to a pool that already has it but sits at `replicas` 0.
- No capability covers the tool: add an `exo-addon.json` to the bundle in the shape `guidance` gives, pin every version, and require its capability. The file is a suggestion and does nothing on its own. A platform admin creates the add-on from it and adds it to a pool.

When `addons_available` is false, the fleet is fixed. This is the case on the demo edition and on an instance without the in-stack updater, and `addons_unavailable_reason` says which. Nobody can add an add-on or change a pool there, so a capability with an empty `provided_by` stays unserved however the catalog lists it. Use only `base_tools` and what a pool already provides. Do not require a capability no pool provides and do not include an `exo-addon.json`, because a skill that does either can never run on that instance. Design around the tools that are listed, or tell the user the instance cannot support the tool.

Every step of a workflow runs on the worker its first step lands on. The run requires the union of what all its steps need, so one pool has to provide all of it. Two capabilities that live in different pools cannot serve one workflow.

A trigger whose requirements no pool can serve is refused with `no connected worker provides the capabilities this run requires`, naming what is missing, and no run is created. A pool counts as able to serve while it has a live worker or is configured with replicas above zero.

Creating add-ons and managing pools have no MCP surface. Where `addons_available` is true, a platform admin does both in the app, under System. Name the capability and the change needed, and hand that to the user. Where it is false, there is no change to hand over, so say that the instance cannot run the tool.

## Write primitives (the fix and build surface)

Each resource layer maps to one write path. A build creates these from the leaves of the graph upward. An improvement changes exactly one of them per pass.

Discover the DTO before you write. `describe_resources` is authoritative for the resource-type slugs the generic CRUD tools accept, so call it when a slug below does not resolve rather than guessing. `describe_resource(type)` returns the accepted create and update fields for one type. Call it before every unfamiliar create and before every update.

To create: call `describe_resource(type)`, build the body from `create_body` fields only, include every required field, then call `create_resource(type, body, parent_id?)`.

To update: call `describe_resource(type)`, read the current resource with `get_resource(type, id, parent_id?)`, build a full replacement body from `update_body` fields only that carries every required existing value, change the one field you mean to change, show that semantic diff at the approval gate, then call `update_resource(type, id, body, parent_id?)`.

`update_resource` is a full-replacement PUT, not a partial patch. A one-field body wipes every field it omits. Do not send one unless the discovered DTO permits it, and do not round-trip computed response fields back into the body. Nested resources such as `task_metric` take a `parent_id` and are not reachable through the parent's DTO.

| Target | Write path |
|---|---|
| Credential | Reuse by ID where one fits. Otherwise create through the discovered DTO. New secret values pass through the LLM context, so warn in the same message that requests the paste. Prefer having the user set the value in the UI. |
| Model | Reuse the workspace default unless a new provider is genuinely needed. Otherwise create through the discovered DTO. |
| Skill content | Before writing a skill that runs a command line tool, resolve the tool by the Worker capabilities procedure above and declare what it needs under `metadata.requires`. After every create or upload, read the `requires`, `warnings`, and `addon_suggestion` the CLI prints (the MCP fallback returns `warnings` and `addon_suggestion` on its response). A warning names a `requires` entry that is not a capability or an `exo-addon.json` the instance could not use, so fix the bundle and upload again before building on it. Use the bundled CLI, passing `--profile <mcp-server-name>` on every call so it targets the workspace you are already on. `python3 scripts/exo-skill.py --profile <name> download <skill> --out <dir>`, edit files, then `python3 scripts/exo-skill.py --profile <name> upload <skill> --folder <dir> --activate`. The CLI moves bundles over REST so file contents never serialize as tool-call arguments. A brand-new skill uses `python3 scripts/exo-skill.py --profile <name> create --folder <dir>`. The MCP fallback is `create_skill_version({skill_id, files: [{path, content}], base_version_id?})`, which auto-activates the new version. There is no separate `activate_skill_version` call, because that tool is rollback-only. Passing `base_version_id` sends only the changed files as an overlay, and omitting it requires the complete bundle. Either way the file contents serialize as tool-call arguments, which is the token cost the CLI exists to avoid. Either path keeps the environment's skill_ref pointing at the same skill_id with no rebind. |
| Tool binding | Update the owning `environment` through the discovered DTO. Tool bindings are a field on the environment, not a resource of their own. |
| Environment | Create or update through the discovered DTO. References creds, model, skill_refs, tool_bindings, and env vars. `required_capabilities` adds to what the bound skills already require. Prefer declaring a tool on the skill that runs it, and use this field only for a tool no bound skill owns. Surface only the keys being added or changed, and never print values for keys whose names suggest secret material. |
| Task | Create or update through the discovered DTO. The execution mode lives here, and metric definitions live on the nested `task_metric` resource. Set exactly one of `instruction`, which pairs an agent with a model, or `entrypoint`, where the runner execs the command via `sh -c` from the workspace dir with no LLM. Under `entrypoint`, exit 0 completes the run, stdout is the run output, and `model_id` must be unset. Entrypoint paths are workspace-relative skill scripts, as in `python ./.agents/skills/<skill>/resources/script.py`; prefix with an interpreter unless the script is executable. |
| Workflow | Create or update through the discovered DTO. Composes steps in order. When changing composition, surface a structural diff at the gate, not just the new array. |

Skill iteration is strictly additive in v1: create a new skill version and activate it, never delete a skill or a version, and never unbind and rebind an environment.

## Unprobeable nodes

Some nodes have no MCP probe or write path: runner identity and lifecycle, cert revocations, raw credential-use rows, and agent internals. Worker pools and add-ons are readable through `list_worker_capabilities` but have no write path. When a diagnosis converges on one of these, name it, record the pivot IDs for the operator, and mark it unprobed rather than guessing. There is no workspace write surface for them.

## Why improve reads debug inline

Invoking another skill from inside a skill does not reliably return control to the caller. That is the reason the three intents live in one bundle rather than three skills. When the improve recipe needs a failed-run diagnosis, it reads `intents/debug.md` and runs that walk inline, which is a file read and not a skill invocation, so control never leaves the recipe. Do not invoke any skill from within an intent. Read the file and execute it.

## Production and secret safety

- Require an explicit answer before any production write and before any production run trigger. A blueprint approval counts only when it enumerates both the writes and the one manual run.
- Keep credential values out of logs, diffs, manifests, and reports.
- Do not switch workspaces after approval. Restart orientation if the target changes.
