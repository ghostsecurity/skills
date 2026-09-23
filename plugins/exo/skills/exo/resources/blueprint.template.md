# Workflow blueprint: {{WORKFLOW_NAME}}

## Outcome and measurement

- Security outcome: {{OUTCOME}}
- Headline metric emitted: `{{METRIC_KEY}}`
- SLI it feeds: {{SLI}}
- SLO target: {{SLO_TARGET}}
- Current baseline: {{BASELINE}}
- Good direction: {{higher or lower}} is better

## Trigger and unit of work

- Trigger: {{cron | webhook | manual}}, cadence {{CADENCE}}
- Cadence justified against the measurement window: {{WHY}}
- Definition of done for one run: {{DONE}}
- Durable files written to `$EXO_OUTPUT_DIR`: {{none, run output kept as `output.txt` | one line per file: `PATH` (md | json), written by step N, what it holds}}

## Steps

For each step, in order:

### Step {{N}}: {{STEP_NAME}}

- Single responsibility: {{WHAT}}
- Emits metric: `{{STEP_METRIC | none}}`, defined as a `task_metric` on this step's task and emitted per the runtime contract in `resources/common.md`
- Inputs: {{INPUTS}}
- Outputs and handoff seam to next step: file `{{PATH}}`, metric keys `{{KEYS}}`
- Skill: {{reuse skill_id ... | author new ...}}
- Model: {{MODEL}}
- Credentials: {{CREDS}}
- Env vars: {{VARS}}
- Tools: {{TOOLS}}
- Command line tools and the capability each needs: {{`tool` from base_tools | `tool` requires `capability`}}
- Judgment versus deterministic split: {{what the LLM does versus what a script does}}

## Worker requirements

Every step runs on the worker the first step lands on, so one pool has to provide all of this.

- Script language for new skills: {{python3 | node | sh | none, no new scripts}}, with {{standard library only | packages via add-on CAPABILITY}}
- Capabilities the workflow requires, across all steps: {{CAPABILITIES or none}}
- Pool that provides all of them: {{POOL or none yet}}
- Add-on suggested in a skill bundle (`exo-addon.json`): {{CAPABILITY and tool versions, or none}}
- Needed from a platform admin before the first run: {{nothing | create the suggested add-on | add CAPABILITY to a pool | give workers to POOL}}

If the last line is not "nothing", the build ends at built_no_run and the first run waits for that change.

## Metric chain

How the per-step metrics roll up to the headline SLI metric, and the by-construction check between them:

{{CHAIN}}

## Assessment scorecard

| Step | Reachable | Repeatable | Valuable | Verifiable | Concrete | Notes and steering applied |
|---|:--:|:--:|:--:|:--:|:--:|---|
| {{N}} | | | | | | |

Reachable is the gate. The others are advisory. Record any reshaping done to lift a weak dimension, and any human-review gate placed where Verifiable is weak.

## Resource plan (reuse versus create)

| Resource | Type | Reuse id or CREATE | Notes |
|---|---|---|---|
| | | | |

## Build sequence (dependency order)

1. Credentials
2. Models
3. Skills
4. Tool bindings
5. Environments
6. Tasks
7. Workflow, with the cron schedule left unset
