---
name: "ghost-exo"
description: The single interface for building, improving, and debugging exo workflows. Routes to one of three intents. BUILD takes a rough idea through interrogation, assessment, resource creation in dependency order, and one manual run, then hands off. IMPROVE runs the observe-and-iterate loop over recent runs, proposing and applying changes behind two gates. DEBUG diagnoses one failed or misbehaving run by walking the dependency graph of everything it touched. Use whenever the user wants to create a new exo workflow, iterate on or improve an existing one, or find out why a specific run failed.
license: apache-2.0
metadata:
  version: 1.0.0
---

# exo

One front door for the exo workflow lifecycle. This skill is a router. It classifies the request into one of three intents, loads the shared substrate, then loads the matching intent recipe and follows it.

## Prerequisites

Exo is an agent workflow platform. Every intent drives it through an exo MCP server.

## Pick the connection

Several exo connections coexist normally, one per workspace, sometimes several on one deployment. Enumerate the exo MCP servers this session has before doing anything else.

With exactly one, use it. With more than one, ask which through the structured question tool and stop until the user answers, because a wrong guess writes to the wrong workspace. Do not switch connections partway through an intent. Start over if the target changes.

Call `whoami` on the chosen server. It confirms the connection and returns the workspace ID. Report that ID so the user can see which workspace they are about to change. If no exo MCP tools are present or `whoami` fails, read `resources/bootstrap.md` and follow it, then call `whoami` again. Do not classify an intent until it succeeds.

`scripts/exo-skill.py` reaches the same workspace over REST, and it has to reach the same one. It reads `EXO_API_URL`, `EXO_API_KEY`, and `EXO_WORKSPACE_ID` from the process environment, falling back to the profile named by `--profile`, which is the file `${XDG_CONFIG_HOME:-~/.config}/exo/<name>.env`. Pass `--profile` with the name of the MCP server you chose on every call, so the two cannot point at different workspaces.

## Always read first

Read `resources/common.md`. It holds the shared substrate every intent uses: the run-walking read primitives, the DTO discovery discipline, the resource write primitives, the unprobeable nodes, and the note on why the improve intent reads the debug recipe inline rather than invoking it.

## Classify the intent

| If the request is about | Intent | Read |
|---|---|---|
| Why a specific run failed, what went wrong with a run_id, diagnosing one run | debug | `intents/debug.md` |
| Improving, iterating on, tightening, or speeding up an existing workflow over its recent runs | improve | `intents/improve.md` |
| Turning an idea into a new workflow, building, creating, or scaffolding a workflow | build | `intents/build.md` |

Pick exactly one. If the request is genuinely ambiguous between intents, ask the user which one in a single question rather than guessing.

## User interaction

Put every question to the user through the harness's structured question tool, whatever it is called here. Free-text prose questions with bullet lists or "Q1/Q2/Q3" prompts are not allowed, even when the question feels open-ended. Bucket open areas into concrete options and let the user type a custom answer instead. Batch related questions into one call so the user answers a structured form rather than a thread of replies. Respect the current limits of the tool you have, and ask directly in prose only when no structured tool is available or the answer is inherently free-form, such as a name, a metric, or a path. This applies to intent disambiguation, the build interrogation in `intents/build.md`, the proposal and rerun gates in `intents/improve.md`, and any candidate-disambiguation prompt in `intents/debug.md`.

Require an explicit answer at every approval, production write, credential, and rerun gate. Never attach auto-resolution to those questions.

The boundaries between intents are intentional gates, not friction to remove. A build that ends in a first run does not auto-continue into improve, because the user owns when to cross from constructing to iterating. An improve pass that finds a failed run reads the debug walk inline rather than switching intents, because the diagnosis is a sub-procedure of the loop, not a separate request.

## Paths

All paths in the intent files are relative to this skill's root directory: `scripts/` for executables, `resources/` for shared docs and templates, `intents/` for the three recipes. `agents/` holds per-harness interface metadata that no recipe reads.
