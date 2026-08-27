# Intent: improve

The observe-and-iterate loop on an existing workflow. Read the last N runs (default 3), walk their step and tool events, find 1 to 2 things worth changing across the whole run set, propose them in plain language, and on explicit agreement apply each through the matching write primitive. On a second explicit agreement, trigger a rerun, fold it into the run set, and reevaluate. Iterate until the user says the workflow is good. Failures in the run set are signal, not an exception, so fold their diagnosis into the proposal set rather than handing the user off.

The shared substrate, namely the read and write primitives, the DTO discovery discipline, the inline-debug note, and the production and secret safety rules, is in `resources/common.md`. Read it first if you have not.

## Inputs

- A workflow name, resolved to a workflow_id via `list_resources('workflow')`. Never ask the user for an ID, because they have a name. Exact-then-substring, and multiple matches means list candidates and stop.
- Optional N, the number of recent runs, default 3.
- An optional user hypothesis such as "feels slow on step 2" or "the output keeps drifting", which biases which signals to weight without letting you skip the walk.

## What improvement means

Four signal categories, three across the run set and one within a single run.

Correctness, from failed runs: any run whose terminal status is failure, or whose events show errors that resolved only after retries. For each, run the debug walk inline (see step 4). A failure in 1 of 3 runs is also a consistency signal, pointing at flakiness rather than a universal break.

Efficiency, from cross-run aggregates: total tokens per run, total duration, per-step tokens and duration, tool-call count per step, retry or error counts that still resolved, and idle gaps between steps that change no state.

Consistency, from cross-run variance: whether each run used the same tools in roughly the same order, whether per-step durations sit in a tight band, whether each run hit the same skill versions, whether output shapes match, and whether any run took a path the others did not.

Within-run inefficiency: repeated tool calls with identical arguments, long stretches of model output with no tool use and no state change, steps whose token budget is disproportionate to the work, and prompts dragged up by context the task does not need.

Outliers are where proposals come from. Two runs that look identical and a third that diverges is a stronger signal than three that are uniformly mediocre, because the divergence points at something the workflow does not control.

## Where the biggest wins come from

### Remove thought from the LLM

The single most valuable transformation is moving work out of the model and into deterministic code, because the model is the most expensive and least reliable component. Patterns to look for, roughly by frequency:

- A step running two or more CLI commands back to back as separate tool calls, where one shell script would do it in one call.
- A workflow chaining two or more scripts across steps, where one script taking the right arguments collapses them into one step.
- A model turn that exists mainly to parse a blob of command output, where filtering at the previous step leaves only the fields the next turn needs.
- A model turn that tracks variables, paths, or state across the run, where externalizing that into a file or an env var removes the bookkeeping.
- A model turn that picks between options a script could pick with a conditional.
- Long repeated context blocks in prompts that exist only because the previous step did not extract the needed part.

Name which lever a proposal pulls. When a proposal pulls none but still matters, such as a missing handoff, a failed-run fix, or a consistency tightening, say so explicitly.

### Good, Better, Best

Every proposal names the rung the workflow is on and the rung it moves toward.

- Good: works roughly 80% of the time, spends turns and tokens on sequencing, parsing, and state-tracking the model should not be doing, and leans on a strong model to paper over its own ambiguity.
- Better: works roughly 90% of the time, hands the deterministic parts to purpose-built scripts, and runs on a modest model because the structure does the work.
- Best: works roughly 98% of the time, is token-efficient, composes scripts cleanly, and reserves the model for judgment, open-ended synthesis, and natural-language interaction.

The rubric is directional. A workflow can be Good on step 1 and Best on step 2, so frame proposals at the step level when the evidence supports it.

## Procedure

1. Resolve the workflow name to an ID. Multiple matches means list candidates and stop.

2. Gather the run set via `list_runs(workflow_id, limit=N)`. Fewer than N means work with what exists and note the smaller sample. Fewer than 2 means consistency signals are unavailable, so fall back to within-run analysis and say the proposal is weaker.

3. Walk each run with `get_run` and `summarize_run_events` for each, plus `list_run_children`, and the same pair on each child. The goal is a per-run, per-step shape naming tokens, duration, tool-call count, errors-resolved-to-success, and the distinct tools used.

4. Diagnose failed runs inline. For each failed run in the set, read the debug walk in `intents/debug.md` and run it against that run_id, then fold the resulting diagnosis into the proposal set. Do not invoke debug as a skill. Read the file and execute it inline, per the inline-debug note in common.md. If you choose to skip a diagnosis, that run stays an opaque failure: it still informs the consistency signal but cannot motivate a failure-fix proposal.

5. Drill where surviving runs look interesting via `get_run_events` on the outliers the step 3 summary flagged. Filter to tool_use and text for efficiency, to step_started, step_finished, and error for composition or consistency. Page with after_sequence.

6. Synthesize 1 to 2 proposals from any category. Each names a specific target (skill, task, workflow step, env binding, model on a task, credential), a specific change, the evidence from the run set, the current and target rung on Good/Better/Best, and which thought-removal lever it pulls or why it still matters if none. When proposals tie on evidence, prefer the one that pulls a lever. If nothing meaningful surfaces, say so and stop, because a made-up low-value change is worse than none.

7. First gate, agreement on the change. One message with the proposals, their evidence, the target type and ID, and a before-and-after for the field. Ask for explicit go-ahead on which to apply. Treat ambiguity as no, and a partial yes as exactly that. For a credential write, fold the LLM-context exposure warning into this same message and request the value in the reply.

8. Apply the agreed change through the write primitive from common.md. If both were agreed, apply in the order the user listed and capture each result. Capture every resource ID and version ID for the change log. One write per proposal, even when bundled.

9. Second gate, agreement on the rerun. A short message naming what was applied, asking whether to trigger a rerun now. Wait for explicit yes. No, or wants-to-inspect-first, exits applied_no_rerun.

10. Trigger the rerun via `trigger_workflow_run(workflow_id)`. Capture the new run_id. Wait for terminal status with a bounded poll.

11. Fold the new run into the set and return to step 3, dropping the oldest if the set is larger than N. The newest run matters most for judging whether the change helped.

12. Stop when the user says so.

## Report

At the end of every loop, including a mid-iteration stop:

- Outcome: user_satisfied, user_declined, applied_no_rerun, no_proposal, or cap_reached.
- Change log: one row per applied write, in order, naming the iteration, target, primitive, resource ID, and for skill content the new version_id plus bundle size.
- Run trail: every run_id analyzed and every run_id triggered, in order, with status and duration.
- Last evaluation: the most recent run set's efficiency and consistency signals, which is what the user judges when they say good enough.

## Stop conditions

- Declines all proposals at the first gate with no qualifier: user_declined.
- Accepts changes but declines the rerun: applied_no_rerun.
- Says the workflow is good: user_satisfied.
- Nothing worth changing: no_proposal, with the run-set summary as the rationale.
- Rerun not terminal within the bounded poll: cap_reached, reporting the in-flight run_id.
- Workflow name resolves to multiple candidates: stop after step 1 and ask which.

## Sharp edges

- Two gates per iteration, never one. The change gate is the user owning whether the change is right, and the rerun gate is the user owning when their workflow runs against real resources. Collapsing them surprises the user.
- One write per proposal, even when bundled, so the change log attributes the next run's behavior to the right change.
- Skill edits go through `scripts/exo-skill.py --profile <name>` so file contents never serialize as tool-call arguments and land in the workspace you are already on. The MCP `create_skill_version({skill_id, files, base_version_id?})` path is the fallback and carries the full-bundle token cost. Skill versions are not reachable through the generic CRUD tools. Either way no skill is deleted and no environment is rebound.
- Failures are signal. Diagnose them inline via intents/debug.md and fold the report into the proposal set rather than aborting or handing the user off.
- Do not propose without evidence from the run set. "This prompt could be tighter" is not a proposal. "Step 2 averaged 4200 tokens, roughly 3000 of them the unchanged context block from step 1, and dropping that block cuts step 2 input by about 70%" is a proposal.
- A proposal that moves nothing up a rung is polish, not improvement. Label it polish at the first gate if the user asked for one anyway.
- Prefer thought-removal proposals, because moving work out of the model cuts tokens, latency, and variance and usually opens a cheaper model, which other improvements rarely all do.
- Outlier-driven beats average-driven. Two consistent runs and one divergent is sharper than three uniformly varying.
- The bound environment at run time may differ from the workflow's current binding if rebound since. Write to the one the analyzed runs used, captured in step 3.
- "The rerun looks better" is not the user being satisfied. Wait for explicit confirmation before user_satisfied.
