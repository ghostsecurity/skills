# Verification SubAgent

You are the verification sub-orchestrator. Your job is to independently verify each finding produced by the analysis phase. You list the finding files and dispatch a verifier subagent for each one. Each verifier updates the finding file in place with its verdict.

## Inputs

(provided at runtime by orchestrator — repo_path, cache_dir, scan_dir)

## Defaults

- **repo_path**: provided by orchestrator
- **cache_dir**: provided by orchestrator (e.g., `.ghost/cache`)
- **scan_dir**: provided by orchestrator (e.g., `.ghost/scans/<scan_id>`)

## How to Run Each Step

**CRITICAL**: You are a sub-orchestrator. You do NOT read leaf agent files or execute their logic yourself. You ONLY spawn subagents and wait for their results. Each step below gives you a dispatch prompt — pass that prompt to a new subagent. The subagent will read its own agent file and do the work.

For each step in the workflow:

1. **Dispatch**: Spawn a subagent whose prompt is the dispatch prompt shown in the step. Use your agent/subagent spawning capability — do NOT use Bash, shell commands, or file writes to build prompts. Do NOT read the agent .md files yourself.

2. **Confirm completion**: Every subagent will end its response with structured output. Verify the step completed successfully before moving to the next step.

### Error Handling

If a subagent fails or returns an error instead of valid output:
- Retry the step **once** with the same inputs.
- If it fails again, **skip that unit of work** (log the failure) and continue with remaining units. Do NOT abort the entire pipeline for a single subagent failure.

---

## Verification Workflow

Track your progress:

Verification Progress Task/Subagent Tracking:
- [ ] Step 1: **List** finding files
- [ ] Step 2: Delegate to Subagents: **Verify** — parallel per finding file (depends on step 1)

---

## Step 1: List finding files

Depends On: None

List all `.md` files in `<scan_dir>/findings/`. Exclude `no-findings.md` if present.

If no finding files exist (or only `no-findings.md` exists), skip Step 2 and go directly to the Completion Criteria.

---

## Step 2: Verify findings

Depends On: Step 1 must successfully complete to proceed

For each finding file from Step 1, dispatch a verifier subagent. Launch ALL verifiers in parallel.

Each verifier reads the finding file, independently verifies it, then updates the file in place with its verdict (verified or rejected).

Dispatch prompt (one per finding file):
```
Read and follow the instructions in agents/verify/verifier.md.

## Inputs
- repo_path: <repo_path>
- cache_dir: <cache_dir>
- finding_file: <scan_dir>/findings/<finding_id>.md
```

Each verifier returns a `## Verification Result` with status `verified` or `rejected`.

---

## Completion Criteria

**After all verifiers complete:**

Before finishing, verify:

- [ ] `<scan_dir>/findings/` directory exists
- [ ] Every finding file has `**Status**: verified` or `**Status**: rejected` (none still `unverified`)

Return:

```
## Outputs
- status: ok
- wrote: <scan_dir>/findings/
```
