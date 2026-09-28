# Ghost Security Exo

Ghost Security Exo is the `exo` Claude Code plugin. Its `ghost-exo` skill builds, improves, and debugs workflows on [exo](https://ghostsecurity.ai), an agent orchestration platform. You run `/ghost-exo` and describe what you want. The skill routes the request to one of three intents and drives exo through the exo MCP server.

## Install and connect

Install the plugin within Claude Code:

```
/plugin marketplace add ghostsecurity/skills
/plugin install exo@ghost-security
```

See [Installation and usage](installation.md) for the other install methods. Then run the skill:

```
/ghost-exo     # Turn an idea into a workflow, iterate on an existing one, or diagnose a failed run
```

### Choose a workspace

Each exo MCP server connects to one workspace. Several connections can coexist, sometimes several on one deployment. With one connection, the skill uses it. With more than one, the skill asks which one and waits for your answer. If it guessed, it could write to the wrong workspace. The skill does not switch connections partway through an intent. If the target changes, it starts over.

The skill then calls `whoami` on the chosen server. `whoami` confirms the connection and returns the workspace ID. The skill reports that ID so you can see which workspace it is about to change.

### Connect the MCP server

When no exo MCP tools are present, or `whoami` fails, the skill registers the server for you. The server is a streamable HTTP MCP server. It needs three values:

| Value | Key | Notes |
|---|---|---|
| Endpoint | `EXO_API_URL` | The workspace base URL. The skill appends `/api/v1/mcp`. |
| `Authorization` header | `EXO_API_KEY` | Sent as `Bearer <key>`. |
| `X-Workspace-Id` header | `EXO_WORKSPACE_ID` | The `ws_` identifier the key belongs to. |

The skill looks for these values before it concludes they are absent. A setup script can write a connection description file with a complete `mcpServers` entry, such as `exo-demo.mcp.json`, and a matching credential profile, such as `exo-demo.env`. The skill searches the working directory and `${XDG_CONFIG_HOME:-~/.config}/exo/`, then the environment. If a value is missing, the skill names it and stops. It never asks you to paste the key into the conversation. The key would then sit in the transcript.

The skill keeps the entry name from a connection description file. Otherwise it names the entry after the deployment and the workspace. It never modifies or removes an entry that points at a different endpoint or workspace. Before it writes, it shows you the exact entry and the exact file. It writes only after your explicit approval.

A harness usually loads MCP servers once, at session start. If `whoami` is still unavailable after the write, the skill asks you to restart the session.

### The credential profile

The bundled `scripts/exo-skill.py` moves skill bundles over REST. File contents then never pass as tool-call arguments. The script reads `EXO_API_URL`, `EXO_API_KEY`, and `EXO_WORKSPACE_ID` from the process environment. It falls back to the profile named by `--profile`. The profile is the file `${XDG_CONFIG_HOME:-~/.config}/exo/<name>.env`. The key names are the same in the profile and in the environment. The profile shares its name with the MCP server entry.

The skill passes `--profile` with the name of the chosen MCP server on every call. The script and the MCP server must reach the same workspace. A matching name keeps them from pointing at different workspaces.

## The three intents

The skill classifies each request into one intent. If the request is ambiguous, it asks you which one in a single question.

| Ask for | Intent |
|---|---|
| A new workflow from an idea, or a build from an agent template slug | Build |
| Improving, iterating on, tightening, or speeding up an existing workflow | Improve |
| Why a specific run failed | Debug |

The skill asks questions through the harness's structured question tool, with concrete options. You can type a custom answer. It asks in prose only when the answer is free-form, such as a name, a metric, or a path. Questions in the build interrogation also carry a recommended default. Every approval, production write, credential, and rerun gate needs your explicit answer. The skill never answers a gate for you.

The boundaries between intents are gates. A build that ends in a first run does not continue into improve. You decide when to move from building to iterating.

### Build

Ask for a new workflow and describe the idea. To start from a template, name an agent template slug from the [ghostsecurity.ai/agents](https://ghostsecurity.ai/agents/) catalog. A slug holds only lowercase letters, digits, and hyphens. The skill fetches `https://ghostsecurity.ai/agents/<slug>.md` and offers the template's outcome, steps, and requirements as proposed defaults. You confirm each default. If the fetch fails, the skill reports the slug and the status and asks whether to continue without a template.

The skill reads the workspace first. It catalogs the workflows, skills, environments, models, credentials, and tools you can reuse. It also reads what the workers can run. The interrogation then runs outcome-first:

1. The outcome and the metric the workflow emits. The metric is the one hard prerequisite. If you cannot name one, the skill helps you derive one and does not move on until it exists.
2. The trigger, the cadence, and the definition of done for one run, including any durable files.
3. The work as a linear sequence of steps, with the metric each step emits and the handoff between steps.
4. Per step: the script language, with python3 recommended, any third-party packages, the skill to reuse or author, the model, the credentials, and the command line tools.

The skill scores each step for agent fit and reshapes weak steps. It then writes `blueprint.md` under the working directory and presents it. The blueprint shows the outcome, the steps, the worker requirements, the metric chain, the scorecard, the reuse plan, and the build order. A template build also records the slug and its URL. The blueprint is the one approval before any write to the workspace.

After approval, the skill creates resources from the leaves up: credentials, models, skills, tool bindings, environments, tasks, then the workflow. It records every ID in `manifest.json` in the same directory, so an interrupted build resumes without duplicates. It prefers existing credentials. A new secret passes through the conversation only with a warning. An environment token credential is created with the placeholder `REPLACE_IN_UI`. You set the real value in the exo UI, and the build waits for your confirmation.

The skill checks that one worker pool can serve the workflow, then triggers one manual run. When the blueprint names durable files, it checks that the run captured them. It leaves the cron schedule unset. When you say the run is good, it hands you the exact call that enables the schedule. Going live is your action.

The report gives the outcome: `built_ran_handed_off`, `built_no_run`, `blueprint_only`, or `stopped`. It also gives the blueprint path, every resource ID, the worker requirements, the run ID, and the next step. A failed run points to debug. A working but mediocre run points to improve.

### Improve

Ask to improve a workflow by name. You never need its ID. You can set the number of recent runs to read. The default is 3. You can also give a hypothesis, such as "feels slow on step 2".

The skill walks every run and its steps. It looks for five signals: failed runs, efficiency, consistency across runs, repeated work, and inefficiency within a run. It diagnoses each failed run with the debug walk, inside the same loop. It then proposes one or two changes. Each proposal names the target, the change, the evidence from the runs, and a before-and-after. It also names the rung the workflow is on and the rung it moves toward:

- Good: works roughly 80% of the time and spends model turns on sequencing, parsing, and state.
- Better: works roughly 90% of the time, hands the deterministic parts to scripts, and runs on a modest model.
- Best: works roughly 98% of the time, is token-efficient, and reserves the model for judgment.

The largest wins move work out of the model and into scripts. If nothing meaningful surfaces, the skill says so and stops.

Each iteration has two gates. At the first, you choose which changes to apply. The skill treats an ambiguous answer as no. It applies each agreed change as its own write. At the second, you decide whether to rerun now. The skill folds the rerun into the run set and evaluates again. The loop continues until you say the workflow is good.

For repeated work, the skill can propose workflow memory, so a script skips items an earlier run already handled. Memory persists only when the workflow sets `memory_enabled: true`. The first run after you enable it starts empty and shows no saving. Judge the change on the run after that.

The report gives the outcome: `user_satisfied`, `user_declined`, `applied_no_rerun`, `no_proposal`, or `cap_reached`. It also gives a change log, the run trail, and the last evaluation.

### Debug

Ask why a run failed. Give a run ID or a workflow name. When you give both, the run ID wins. With only a name, the skill picks the most recent failed run, or the most recent run of any status, and says which. You can add a symptom to steer where it looks first.

The walk is read-only. It follows the dependency graph of everything the run touched. The graph covers the workflow definition, each child run, the task, the skill version, the environment, the credential, the model, the worker capabilities, the event stream, and the approvals. It does not stop at the first plausible cause. Some nodes have no MCP probe, such as runner identity and lifecycle, cert revocations, and agent internals. The skill records their IDs for an operator and marks them unprobed.

The report gives a one-line diagnosis, the failing nodes in timeline order, and citations. It gives a suggested fix only when the cause is a node the skill can act on, and it never applies the fix. Improve applies fixes. A coverage list marks every node clean, culprit, contributing, or unprobed. If the run is still active, the skill says so and stops.

When a trigger was refused, no run exists. The skill diagnoses from the workflow's tasks, environments, and skills.

## How workflows run

### Runtime contract

Every workflow step runs under four runner rules:

- **Output.** The runner sets `$EXO_OUTPUT_DIR` on workflow runs only. When a step writes nothing there, the runner saves the step's run output as `output.txt`. Only regular files are captured. The capture is dropped above 32 MiB or 4096 files.
- **Metrics.** A step emits metrics with `exo-metric emit key=value`. The runner drops any key that is not a metric defined on the step's task. A task fails with `required metrics not emitted` when it skips a defined key. Emitted values merge into the workflow run's `workflow_metrics`.
- **Completion.** An `instruction` task must run `exo-done` when it finishes, or the run fails. An `entrypoint` task completes on exit code 0.
- **Memory.** Memory is a SQLite database at `$EXO_AGENT_MEMORY_PATH`. It persists across runs only when the workflow sets `memory_enabled: true`. The runner saves it after each completed step, so a failed step's writes are lost. A database over 32 MiB is not saved.

Every workflow the skill builds emits its outcome metrics.

### Worker capabilities

Each worker pool runs its own image. A capability names a tool set an image provides, such as `aws` or `gcloud`. A run goes only to a worker that provides every capability the run requires. Tools in `base_tools` are on every worker and need no capability.

A skill declares each other tool it runs by capability under `metadata.requires` in its `SKILL.md`. A skill that runs a tool it never declared fails with a command-not-found error on a worker without it. Every step of a workflow runs on the worker its first step lands on, so one pool must provide what all steps need.

When no pool can serve a workflow, exo refuses the trigger with `no connected worker provides the capabilities this run requires` and creates no run. The skill names the missing capability and the change a platform admin makes in the exo app, under System. That change depends on `addons_available`. When it is true, the admin adds an add-on to a pool, or gives workers to a pool that already has the add-on but sits at `replicas` 0. An `exo-addon.json` in a skill bundle is only a suggestion for that add-on. When `addons_available` is false, as on the demo edition, the fleet is fixed. The skill then designs around the tools the workers already carry.

### Agent-fit assessment

The build intent scores each step on five criteria:

| Criterion | What it measures |
|---|---|
| Reachable | How much of what the work reads and changes is available through the agent's tools. On exo, a tool counts only when a worker carries it. |
| Repeatable | How closely the work follows a pattern the model has seen many times. |
| Valuable | How often the work recurs and how much expensive human time it burns. |
| Verifiable | How cheaply and objectively the result can be checked. |
| Concrete | How clearly the inputs and the definition of done are specified. |

Each criterion scores from 0 to 4: Not at all, Slightly, Moderately, Very, and Completely. Reachable is the gate. If it fails, nothing else matters. The hand-off threshold is 3 on every criterion. A step at 2 or below has a weak spot to fix. A human-review gate at the end of a chain can supply the check for a step with low verifiability. The assessment steers the design and never blocks it.

For the internals behind these rules, see [common.md](../plugins/exo/skills/exo/resources/common.md).

---

Previous: [Architecture](community/architecture.md) | [Docs home](../README.md#documentation)
