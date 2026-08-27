# Intent: debug

Diagnose one failed or misbehaving run end to end by walking the dependency graph of everything it touched until every reachable node is ruled out or named as the cause. The run event tape is one node, not the whole picture. This walk is read-only. It diagnoses and stops. It does not propose or apply fixes, which is the improve intent's job.

The shared substrate, namely the read primitives, the pivot IDs, the dependency graph, and the unprobeable nodes, is in `resources/common.md`. Read that first if you have not.

## Inputs

- A `run_id`, or a workflow name to resolve to one. The run_id wins when both are given.
- An optional user hypothesis or symptom, which biases which nodes to probe first but does not let you skip the walk.

## Nodes and their probes

Each node can fail and surface as a run-level error. Each has a probe that says whether it is healthy in the run's started_at..finished_at window. Walk all of them.

| Node | What it owns | Probe |
|---|---|---|
| Workflow definition | step order, step-to-task binding, concurrency, schedule | `get_resource('workflow', id)` |
| Step / child run | per-step environment, task, runner | `list_run_children(run_id)`, then recurse this whole procedure into each child |
| Task | instruction text or entrypoint command, skill binding, agent, model, environment binding | `get_resource('task', id)` |
| Skill + active version | SKILL.md entrypoint, prompt, scripts, required outputs | `get_resource('skill', id)` then `get_skill_version(skill_id, version_id)` |
| Environment | env vars, credential bindings, model defaults | `get_resource('environment', id)` |
| Credential | secret material, OAuth expiry, scope | `get_resource('credential', id)`, and `query_observability` for matching credential_uses rows in the window |
| Agent | binary version, prompt baseline | No MCP surface. There is no agent resource type, and run.agent_id is a free-form string. Infer health from whether the events show any agent activity at all |
| Model / LLM provider | provider, auth, rate limits, 5xx | `get_resource('model', id)` for the row, and error-event payloads in `get_run_events` for runtime failures |
| Runner identity | mTLS cert serial/CN, TTL, renewal | No MCP surface. Operator-side only. Capture run.runner_id for the operator |
| Runner lifecycle | heartbeats, WS connect/disconnect, OOM, restarts, slot assignment | No MCP surface. Runner host and gateway logs only |
| Cert revocation | revoked serials | No MCP surface. cert_revocations is an operator-side collection with no read path |
| Credential proxy | DNS allowlist hits, MITM token swap, upstream errors | `query_observability` filtered to the run_id over proxy logs |
| Gateway dispatch | run-queue assignment, runner-pool selection across step boundaries | `query_observability` filtered to the run_id and step transitions |
| Workflow event tape | step lifecycle, status, errors | `summarize_run_events(run_id)` then `get_run_events(run_id, event_types=[...])` |
| Tool surface | per-tool args/results, exit codes | `get_run_events(run_id, event_types=['tool_use','error'])` |
| Approvals | pending and resolved approval gates | `list_approval_requests` filtered by run_id |

Nodes marked No MCP surface cannot be probed from here. Record their pivot IDs in the report and mark them unprobed rather than guessing.

## Procedure

0. Resolve to a run_id if only a workflow name was given. `list_resources('workflow')`, exact-then-substring match. Multiple matches means list candidates and stop. Then `list_runs(workflow_id, limit=1, status='failed')`, falling back to the most recent of any status, and narrate the fallback.

1. `get_run(run_id)`. Capture every pivot ID. If the status is still active, stop and say so.

2. `summarize_run_events(run_id)`. Read the shape.

3. `get_run_events(run_id, event_types=[...])`. Include at least error and step_failed, plus whatever the summary flagged. Page with after_sequence until the failure events and their immediate predecessors are in hand. Harvest any new IDs from the failure payloads.

4. Walk the graph. For every node for which you now have an ID, run its probe over the window. For every step, recurse into its child run with this whole procedure. Do not stop at the first plausible cause, because failures layer, for example a content bug masking a credential rotation or a credential expiry masking a runner restart, so keep going until every reachable node is touched. Record an implicated node and keep walking.

5. Report:
   - One-line diagnosis, or a plain statement that the issue is not fully diagnosable here if it converges on an unprobeable node.
   - Failing nodes, ordered by when they fired in the timeline.
   - Citations: event sequence numbers, resource fields, observability results.
   - A suggested fix at the primitive level ONLY when the culprit is a node you can probe and act on. Do not apply it, because that is the improve intent. When the culprit is an unprobeable node, skip the fix.
   - Coverage list: every node marked clean, culprit, contributing, or unprobed with a reason. An honest unprobed beats a confident wrong answer.

## Stop conditions

- Run still active: stop after step 1.
- A node has no probe surface: mark it unprobed and continue. Never abandon the rest of the walk for one opaque node.
- Multiple contributors: report all of them, ordered by which fired first.

## Sharp edges

- Do not page raw events without an event_types filter.
- The bound environment at run time may differ from the workflow's current environment if it was rebound since. Cite the run's own IDs, not the workflow's current state.
- Child runs are first-class. Each has its own runner, environment, task, agent, and model. Recurse rather than treating them as opaque.
- If a node's probe shows it never received work, meaning zero tool calls, zero tokens, or sub-100ms on a step that should take seconds, the failure is upstream. Walk what was supposed to provision it before what it contains.
- Different step indices may bind to different environments and runner pools. Compare per-step environment_id when failures cluster on step boundaries.
- Probed-and-clean and did-not-probe are different states. Do not conflate them in the report.
