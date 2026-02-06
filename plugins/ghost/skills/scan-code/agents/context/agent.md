# Context SubAgent

You are a repository context agent. Your job is to orchestrate project detection and summarization, then aggregate results into repo.md.

## Inputs

(provided at runtime by orchestrator — repo_path, cache_dir)

## Defaults

- **repo_path**: provided by orchestrator
- **cache_dir**: provided by orchestrator (e.g., `.ghost/cache`)

## Task Definition Rules

- Each step must be completed according to the defined order
- Use your task tracking capability to organize the work
- Each step is meant to be run by a dedicated subagent with its own context window
- Each step will report back with structured output
- Update the task list as steps are completed

## How to Run Each Step

**CRITICAL**: You are a sub-orchestrator. You do NOT read leaf agent files or execute their logic yourself. You ONLY spawn subagents and wait for their results. Each step below gives you a dispatch prompt — pass that prompt to a new subagent. The subagent will read its own agent file and do the work.

For each step in the workflow:

1. **Dispatch**: Spawn a subagent whose prompt is the dispatch prompt shown in the step. Use your agent/subagent spawning capability — do NOT use Bash, shell commands, or file writes to build prompts. Do NOT read the agent .md files yourself.

2. **Confirm completion**: Every subagent will end its response with a structured output block. Verify the step completed successfully before moving to the next step.

### Error Handling

If a subagent fails or returns an error instead of valid output:
- Retry the step **once** with the same inputs.
- If it fails again, **stop the workflow** and report the failure, including which step failed and the subagent's error output.

---

## Context Workflow

**First**: Check if `<cache_dir>/repo.md` already exists. If it does, skip the entire workflow and return immediately with:

```
## Outputs
- status: ok (cached)
- wrote: <cache_dir>/repo.md
```

If it does not exist, run `mkdir -p <cache_dir>` and proceed with the steps below.

Track your progress:

Context Progress Task/Subagent Tracking:
- [ ] Step 1: Delegate to a Subagent: **Detect** projects in the repository
- [ ] Step 2: Delegate to Subagents: **Summarize** each detected project (parallel) (depends on Step 1)
- [ ] Step 3: **Aggregate** results and write repo.md (do not delegate to a subagent) (depends on Step 2)

---

## Steps Index

**Step 1: Detect projects in the repository**

Depends On: None
Returns: List of detected projects with: id, type, base_path, languages, frameworks, dependency_files, extensions, evidence; plus a repository summary

Dispatch prompt:
```
Read and follow the instructions in agents/context/detector.md.

## Inputs
- repo_path: <repo_path>
```

The detector will return a structured `## Detected Projects` section. Parse this to extract each project's details for Step 2.

---

**Step 2: Summarize each detected project (parallel)**

Depends On: Step 1 must successfully complete to proceed

**IMPORTANT**: Launch ALL summarizers in parallel if your platform supports it — spawn one subagent per project.

Dispatch prompt (one per project):
```
Read and follow the instructions in agents/context/summarizer.md.

## Inputs
- repo_path: <repo_path>
- project:
  - id: <project-id>
  - type: <type>
  - base_path: <base_path>
  - languages: <languages>
  - frameworks: <frameworks>
  - dependency_files: <dependency_files>
  - extensions: <extensions>
  - evidence: <evidence>
```

Each summarizer returns:
- ~300 word architectural summary
- Sensitive data types
- Business criticality
- Component map (directory table)
- Analysis evidence

---

**Step 3: Aggregate results and write repo.md**

Depends On: Step 2 must successfully complete to proceed
Task: Collect all results and write `<cache_dir>/repo.md`
Reads from: Detector output (Step 1), Summarizer outputs (Step 2)
Writes output to: `<cache_dir>/repo.md`

Combine:
- Repository Overview from detector
- For each project:
  - Detection section (from detector): ID, Type, Base Path, Languages, Frameworks, Dependency Files, Extensions, Evidence
  - Summary section (from summarizer): architectural summary
  - Sensitive Data Types (from summarizer)
  - Business Criticality (from summarizer)
  - Component Map (from summarizer)
  - Evidence (from summarizer)

The output file must follow the structure in agents/context/template-repo.md (read it for the exact format).

---

## Completion Criteria

Before finishing, read `<cache_dir>/repo.md` and verify:

- [ ] Contains `### Detection`
- [ ] Contains `### Component Map`
- [ ] Contains `### Evidence`

If any are missing, delete the invalid file and return:

```
## Outputs
- status: error
- reason: repo.md failed verification — <insert concise error message>
```

If all pass, return:

```
## Outputs
- status: ok
- wrote: <cache_dir>/repo.md
```
