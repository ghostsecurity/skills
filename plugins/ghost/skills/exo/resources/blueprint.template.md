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
- Durable artifact a run leaves: {{ARTIFACT}}

## Steps

For each step, in order:

### Step {{N}}: {{STEP_NAME}}

- Single responsibility: {{WHAT}}
- Emits metric: `{{STEP_METRIC}}`
- Inputs: {{INPUTS}}
- Outputs and handoff seam to next step: file `{{PATH}}`, metric keys `{{KEYS}}`
- Skill: {{reuse skill_id ... | author new ...}}
- Model: {{MODEL}}
- Credentials: {{CREDS}}
- Env vars: {{VARS}}
- Tools: {{TOOLS}}
- Judgment versus deterministic split: {{what the LLM does versus what a script does}}

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
