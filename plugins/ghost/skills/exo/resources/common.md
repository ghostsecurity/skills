# common.md: the exo MCP substrate

Shared by all three intents: the read primitives for walking runs, the DTO discovery discipline, the write primitives for changing resources, the unprobeable nodes, the in-bundle invocation note, and the production and secret safety rules. Read this before any intent recipe.

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
- `get_skill_version(skill_id, version_id, with_content)` returns a skill bundle's files.
- `list_approval_requests(run_id)` returns the pending and resolved approval gates for a run.
- `query_observability(category='events', run_id, ...)` gives a cross-run log view. Bucketed `traffic` observability cannot be filtered by run ID.

## The dependency graph

Every run depends on a chain of resources, and a run-level failure can originate in any of them:

workflow definition, then step or child run, then task, then skill and its active version, then environment, then credential, then model, with the runner, agent, credential proxy, and gateway dispatch alongside.

Pivot IDs to harvest from `get_run` and from failure-event payloads: `workflow_id`, `task_id`, `source_id`, `execution_id`, `parent_run_id`, every child via `list_run_children`, `runner_id`, `agent_id`, `environment_id`, the effective model, and `started_at` and `finished_at` for the observability window.

Proxy requests attributed to a run surface in `get_run_events` as `traffic_accepted` or `traffic_blocked`, and the payloads can carry `credential_id`, host, path, status, and error code. There is no MCP query for raw credential-use rows. Read credential metadata with `get_resource` and mark secret validity unprobed unless the events prove the result.

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
| Skill content | Use the bundled CLI, passing `--profile <mcp-server-name>` on every call so it targets the workspace you are already on. `python3 scripts/exo-skill.py --profile <name> download <skill> --out <dir>`, edit files, then `python3 scripts/exo-skill.py --profile <name> upload <skill> --folder <dir> --activate`. The CLI moves bundles over REST so file contents never serialize as tool-call arguments. A brand-new skill uses `python3 scripts/exo-skill.py --profile <name> create --folder <dir>`. The MCP fallback is `create_skill_version({skill_id, files: [{path, content}], base_version_id?})`, which auto-activates the new version. There is no separate `activate_skill_version` call, because that tool is rollback-only. Passing `base_version_id` sends only the changed files as an overlay, and omitting it requires the complete bundle. Either way the file contents serialize as tool-call arguments, which is the token cost the CLI exists to avoid. Either path keeps the environment's skill_ref pointing at the same skill_id with no rebind. |
| Tool binding | Update the owning `environment` through the discovered DTO. Tool bindings are a field on the environment, not a resource of their own. |
| Environment | Create or update through the discovered DTO. References creds, model, skill_refs, tool_bindings, and env vars. Surface only the keys being added or changed, and never print values for keys whose names suggest secret material. |
| Task | Create or update through the discovered DTO. The execution mode lives here, and metric definitions live on the nested `task_metric` resource. Set exactly one of `instruction`, which pairs an agent with a model, or `entrypoint`, where the runner execs the command via `sh -c` from the workspace dir with no LLM. Under `entrypoint`, exit 0 completes the run, stdout is the run output, and `model_id` must be unset. Entrypoint paths differ by source: skill scripts are workspace-relative, as in `python ./.agents/skills/<skill>/resources/script.py`, and environment files are read-only under `$EXO_RESOURCES_DIR` and need an interpreter prefix. |
| Workflow | Create or update through the discovered DTO. Composes steps in order. When changing composition, surface a structural diff at the gate, not just the new array. |

Skill iteration is strictly additive in v1: create a new skill version and activate it, never delete a skill or a version, and never unbind and rebind an environment.

## Unprobeable nodes

Some nodes have no MCP probe or write path: runner identity and lifecycle, cert revocations, raw credential-use rows, and agent internals. When a diagnosis converges on one of these, name it, record the pivot IDs for the operator, and mark it unprobed rather than guessing. There is no workspace write surface for them.

## Why improve reads debug inline

Invoking another skill from inside a skill does not reliably return control to the caller. That is the reason the three intents live in one bundle rather than three skills. When the improve recipe needs a failed-run diagnosis, it reads `intents/debug.md` and runs that walk inline, which is a file read and not a skill invocation, so control never leaves the recipe. Do not invoke any skill from within an intent. Read the file and execute it.

## Production and secret safety

- Require an explicit answer before any production write and before any production run trigger. A blueprint approval counts only when it enumerates both the writes and the one manual run.
- Keep credential values out of logs, diffs, manifests, and reports.
- Do not switch workspaces after approval. Restart orientation if the target changes.
