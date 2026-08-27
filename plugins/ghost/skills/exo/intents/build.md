# Intent: build

Take a rough idea and turn it into a live, well-formed workflow: orient, interrogate outcome-first, assess and steer, gate on a blueprint, create resources in dependency order, run once manually, and hand off. This intent owns research, plan, create, and one clean manual run. It does not own the iterate loop. When the first run is in hand, route the user to the improve intent, and route any failed run to the debug intent.

The shared substrate, namely the read and write primitives and the DTO discovery discipline, is in `resources/common.md`. The scoring rubric is in `resources/workflow-assessment.md`. The blueprint shape is in `resources/blueprint.template.md`. Read common.md first.

## Phase 0: Orient

Before talking to the user, call `whoami` and list the workspace resources: workflows, skills, environments, models, credentials, and tools. Hold a reuse catalog and a set of candidate template workflows. When a structurally similar workflow exists, you may offer to clone and adapt it as a skeleton, but only from Stage 3 onward, never to seed the outcome.

## Phase 1: Interrogate (research)

A fixed coverage checklist with adaptive phrasing. You may not leave this phase until every area is resolved, but skip what the user already answered and phrase each question in context. The order is outcome-first.

Every question in this phase goes through the harness's structured question tool (see the User interaction section of `SKILL.md`). Bucket each item below into concrete options with a recommended default, batch related items into a single call, and use multi-select where the choices are not mutually exclusive and the tool allows it. Do not ask any interrogation item as free-text prose.

### Stage 1: Outcome and measurement (the spine)

1. The one-line idea and the security outcome it advances.
2. The concrete metric the workflow will emit to feed that outcome's SLI. This is a hard prerequisite. If the user cannot name one, stay here and help derive a measurable metric from the outcome. Do not advance to decomposition until a metric exists.
3. The full ladder, recorded in the blueprint: the emitted metric key, the SLI it feeds, the SLO target, the current baseline, and the good direction. The workflow emits only the raw metric. The rollup lives in a dashboard elsewhere.

### Stage 2: Trigger and the unit of work

4. What fires the workflow and on what cadence, with the cadence justified against the outcome's measurement window rather than picked arbitrarily.
5. The definition of done for one run and the durable artifact it leaves.

### Stage 3: Decomposition into linear steps

6. Narrate the work from trigger to metric emission as a linear sequence. Workflows are linear step chains, not branching graphs.
7. Per step, the single responsibility and the measurement it emits.
8. The metric chain: show how the per-step metrics roll up to the headline metric, the way a leading-indicator count should equal an outcome count by construction. A chain that does not close, where a step emits a number nothing downstream consumes or reconciles against, is a design smell to surface here, before any wiring.
9. The handoff seam at every boundary, down to the exact file path and metric keys, since that seam is the only contract between steps.

### Stage 4: Per-step realization

10. The judgment-versus-deterministic split per step, applying the remove-thought lens, which decides how much is scripted skill versus prompt.
11. The skill per step, resolved interactively: reuse an existing skill by skill_id, or author a new one with `scripts/exo-skill.py --profile <name> create` (which auto-activates the first version). Discover existing skills first and offer reuse before authoring.
12. The model, credentials, env vars, and tools per step, reusing from the Phase 0 catalog by ID wherever a fit exists, and creating new only with the paste-through warning for secrets.

When a template was chosen in Phase 0, Stages 1 and 2 run identically. The template seeds step structure and wiring only from Stage 3 onward.

## Phase 2: Assess and steer

Score each step against `resources/workflow-assessment.md`. Reachable is the gate. Repeatable, Valuable, Verifiable, and Concrete are advisory. This never blocks, but wherever a dimension lands below the threshold, actively reshape the design toward something that would pass: split an overloaded step, move sequencing or parsing into a script, tighten vague inputs to lift Concrete, or place a human-review gate after a step whose Verifiable is weak. Fold the revised scores and reasoning into the blueprint. Weave this into Phase 1 so the design is already close to passing before the user sees the blueprint.

## Phase 3: Plan gate

Write `blueprint.md` under the working directory, for example `/tmp/exo-build/<slug>/blueprint.md`, using `resources/blueprint.template.md`, and present it. This is the one hard approval gate before any writes. It shows the outcome ladder, the step graph with per-step prompt, skill, model, environment, creds, vars, and metrics, the metric chain, the assessment scorecard, the reuse-versus-create plan, the handoff seams, and the dependency-ordered build sequence. The user approves once here, and only then do you touch the workspace.

## Phase 4: Build in dependency order

Create or wire resources from the leaves up, recording every resulting ID into `manifest.json` in the same working directory immediately after each create, so an interrupted build resumes without double-creating. Consult the manifest before every create. The order is credentials, models, skills, tool bindings, environments, tasks, then workflow. The write path for each is in common.md. Leave the workflow's cron schedule unset.

## Phase 5: First run

Trigger one manual run with `trigger_workflow_run`, wait for terminal status, and summarize by walking the child runs and their event summaries, using the read primitives in common.md. The cron schedule stays unset through this phase.

## Phase 6: Review gate and handoff

Present the run result and route. A failed or ugly run points the user to the debug intent on that run_id. A working but mediocre one points to the improve intent. When the user says it is good, hand them the exact call that enables the schedule and stop, leaving that final go-live action to them. Build that call with the update procedure in `resources/common.md`, so the body is a full replacement carrying the existing steps and not a lone `cron_schedule`.

## Report

- Outcome: built_ran_handed_off, built_no_run, blueprint_only, or stopped.
- Blueprint path and the manifest of every created or reused resource ID, by type.
- Run trail: the manual run_id with status and duration, if a run happened.
- Next step: the pointer to the improve or debug intent, and the exact call to enable the cron when ready.

## Stop conditions

- No nameable outcome metric: stay in Stage 1 until one exists.
- User declines the blueprint at the plan gate: blueprint_only, with the blueprint saved.
- A build write fails partway: the manifest holds what was created. Exit stopped and report the resume point.
- The manual run does not reach terminal status within a bounded wait: report the in-flight run_id.

## Sharp edges

- The cron is left off until the user enables it. The build never schedules a workflow.
- Secret material passes through context only with the warning, and only when no existing credential fits. Prefer reuse by ID.
- Route to the debug and improve intents as user-driven hops at the end. Within this intent you do not run their loops.
- Workflows are linear step chains, not DAGs. The decomposition must be a sequence.
- The manifest is the resume key. Consult it before every create, and never create a resource whose ID already sits in it.
- Template cloning rebinds every referenced ID. A cloned workflow must not inherit the source's creds, env, model, or skill_refs.
- The assessment steers but never blocks. The metric is the only hard prerequisite.
- The metric chain must close. A step emitting a number nothing downstream consumes is a smell to surface, not to wire.
