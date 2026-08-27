# Assessing a Workflow for Agent Fit

A one-page guide for judging whether a piece of work is a good candidate to hand to an AI agent, meaning an LLM with tools.

## The core idea

Two questions decide whether work belongs with an agent. The first is whether the work is even within an agent's reach, since an agent perceives and acts through text and tools rather than the physical world. The second, which only matters once the first is satisfied, is whether the work is worth handing off and shaped so the agent can succeed. We capture the first as a gate and the rest as four scored dimensions, and the best-fit work is where all of them hold at once.

## The five criteria

| Criterion | What it measures |
|---|---|
| **Reachable** | How much of what the work needs to read and to change is available through the agent's tools rather than the physical world or undocumented knowledge. This is the gate. If it fails, nothing else matters. |
| **Repeatable** | How closely the work follows a pattern the model has seen many times. Patterned, conventional work is in-distribution and is what models are reliably good at. |
| **Valuable** | How worth doing it is to offload the work, counting both how often it recurs and how much expensive human time it currently burns. |
| **Verifiable** | How cheaply and objectively the result can be checked once produced, whether by a test, a tool, a quick diff, or a human reviewer downstream. This is the linchpin, because a probabilistic agent needs a check to iterate against and to be trusted. |
| **Concrete** | How clearly the inputs and the definition of done are specified, so the agent can start cleanly and knows when it is finished. |

## The scoring scale

Each criterion is scored on a single unipolar scale that runs in one direction from none to total.

| Anchor | Score |
|---|:---:|
| Not at all | 0 |
| Slightly | 1 |
| Moderately | 2 |
| Very | 3 |
| Completely | 4 |

## Scoring a workflow step

Break the workflow into its steps and give each step its own five-by-five grid, marking where each criterion lands. Read it left to right. The further right the marks, the better the fit, and any mark in the 0 or 1 column is a red flag that points to the part of the work a human still needs to own.

| Attribute | 0 None | 1 Slight | 2 Mod | 3 Very | 4 Full |
|---|:---:|:---:|:---:|:---:|:---:|
| Reachable | | | | ● | |
| Repeatable | | | | ● | |
| Valuable | | | | | ● |
| Verifiable | | | | | ● |
| Concrete | | | | | ● |

## Reading the result

The hand-off threshold is Very, meaning a score of 3 on every criterion. A step whose marks all sit at or beyond the 3 column is one you can delegate with confidence. A step with a mark at Moderately or below has a weak spot worth addressing before you trust it.

A low verifiability score does not disqualify a step on its own, because verification can be supplied externally. A downstream human review of the step's output is itself a cheap, objective check, so placing a single human-review gate at the end of a chain often rescues the judgment-heavy steps and turns the whole workflow into a safe agent-drafts and human-approves pattern.

```
   step 1  →  step 2  →  step 3  →  step 4  ──▶  [ HUMAN REVIEW ]  ──▶  approve / send back
   (agent)    (agent)    (agent)    (agent)        verification gate
```
