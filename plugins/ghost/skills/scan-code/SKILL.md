---
name: "ghost-scan-code"
description: "Ghost Security - SAST code scanner. Finds security vulnerabilities in source code by planning and executing targeted scans for issues like SQL injection, XSS, BOLA, BFLA, SSRF, and other OWASP categories. Supports applications (backend, frontend, mobile) and libraries (prototype pollution, unsafe deserialization, ReDoS, path traversal, zip slip). Use when the user asks for a code security audit, SAST scan, vulnerability scan of source code, or wants to find security flaws in a codebase or library."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
argument-hint: "[depth=quick]"
license: apache-2.0
metadata:
  version: 1.1.0
---

# Find Issues

You find security issues in a repository. This skill plans which vulnerability vectors to scan, then executes those scans against each project.

## Inputs

- **depth**: `quick` (default), `balanced`, or `full` — override via `$ARGUMENTS`

$ARGUMENTS

> **Note:** Arguments passed can be used to customize the scan workflow if provided. For example, if the user specifies a specific set of vectors, count of vectors, specific candidate files, areas to focus on, count of candidate files, etc., ensure the relevant details are passed to the relevant steps in the skill.

## Supporting files

- Loop script: [scripts/loop.sh](scripts/loop.sh)
- Scan criteria: [criteria/index.yaml](criteria/index.yaml)

---

## Step 1: Setup

Compute the repo-specific output directory:
```bash
repo_name=$(basename "$(pwd)") && remote_url=$(git remote get-url origin 2>/dev/null || pwd) && short_hash=$(printf '%s' "$remote_url" | git hash-object --stdin | cut -c1-8) && repo_id="${repo_name}-${short_hash}" && short_sha=$(git rev-parse --short HEAD 2>/dev/null || date +%Y%m%d) && ghost_repo_dir="$HOME/.ghost/repos/${repo_id}" && scan_dir="${ghost_repo_dir}/scans/${short_sha}/code" && cache_dir="${ghost_repo_dir}/cache" && mkdir -p "$scan_dir" && echo "scan_dir=$scan_dir cache_dir=$cache_dir"
```

1. Read `$cache_dir/repo.md` — if missing, run the repo-context skill first and then continue.
2. Read [criteria/index.yaml](criteria/index.yaml) to get the valid agent→vector mappings per project type
3. Set `depth` to `quick` if not provided
4. If `depth` is `full`, warn the user that a full scan uses significantly more tokens and ask them to confirm before proceeding. If they decline, fall back to `balanced`.

---

## Step 2: Plan Scans

If `$scan_dir/plan.md` already exists, skip to the next step.

Otherwise, run the planner using [scripts/loop.sh](scripts/loop.sh):

```bash
bash <path-to-loop.sh> $scan_dir planner.md "- depth: <depth>
- arguments: <relevant argument overrides if any, otherwise omit>" 1 $cache_dir
```

Use a 10-minute timeout. If the command times out, re-run it — the script resumes from where it left off. If it fails 3 times consecutively with the same error, stop and report the failure.

**Verify:** `$scan_dir/plan.md` exists and contains at least one `## Project:` section before proceeding.

---

## Step 3: Nominate Files

If `$scan_dir/nominations.md` does not exist, generate it by reading `$scan_dir/plan.md` and for each project section (`## Project: <base_path> (<type>)`), parse the Recommended Scans table. For each row, extract the Agent and Vector columns. Write `$scan_dir/nominations.md` - one line per (project, agent, vector) combination. Skip projects with empty scan tables.

```markdown
# Nominations

- [ ] <base_path> (<type>) | <agent> | <vector>
- [ ] <base_path> (<type>) | <agent> | <vector>
...
```

If `$scan_dir/nominations.md` already exists, change every top level task `- [x]` to `- [ ]`. Keep all indented lines/subtasks beneath each item unchanged.

### Run nomination script

Using [scripts/loop.sh](scripts/loop.sh):

```bash
bash <path-to-loop.sh> $scan_dir nominator.md "- depth: <depth>
- arguments: <relevant argument overrides if any, otherwise omit>" 5 $cache_dir
```

Use a 10-minute timeout. If the command times out, re-run it — the script resumes from where it left off. If it fails 3 times consecutively with the same error, stop and report the failure.

**Verify:** `$scan_dir/nominations.md` contains at least one `- [x]` line before proceeding.

---

## Step 4: Analyze Nominated Files

Read `$scan_dir/nominations.md`. For each candidate file under a checked `- [x]` line, append to `$scan_dir/analyses.md` (skip candidates already listed in `analyses.md`).

```
- [ ] <base_path> (<type>) | <agent> | <vector> | <candidate_file>
```

Create the findings directory:
```bash
mkdir -p $scan_dir/findings
```

### Run analysis script

Using [scripts/loop.sh](scripts/loop.sh):

```bash
bash <path-to-loop.sh> $scan_dir analyzer.md "" 5 $cache_dir
```

Use a 10-minute timeout. If the command times out, re-run it — the script resumes from where it left off. If it fails 3 times consecutively with the same error, stop and report the failure.

**Verify:** `$scan_dir/analyses.md` contains at least one `- [x]` line before proceeding.

---

## Step 5: Verify Findings

List all `.md` files in `$scan_dir/findings/`. If none exist, write a `no-findings.md` summary and stop.

Using [scripts/loop.sh](scripts/loop.sh):

```bash
bash <path-to-loop.sh> $scan_dir verifier.md "" 5 $cache_dir
```

Use a 10-minute timeout. If the command times out, re-run it — the script resumes from where it left off. If it fails 3 times consecutively with the same error, stop and report the failure.

---

## Completion

After all steps complete, report the scan results:

1. List all finding files in `$scan_dir/findings/`
2. Count verified vs rejected findings
3. Present a summary to the user
