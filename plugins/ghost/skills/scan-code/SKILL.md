---
name: "ghost:scan-code"
description: "Find security issues in a repository by planning and executing targeted vulnerability scans."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
argument-hint: "[depth=quick]"
---

# Find Issues

You find security issues in a repository. This skill plans which vulnerability vectors to scan, then executes those scans against each project.

## Inputs

- **depth**: `quick` (default), `balanced`, or `full` — override via `$ARGUMENTS`

$ARGUMENTS

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

---

## Step 2: Plan Scans

If `$scan_dir/plan.md` already exists, skip to the next step.

Otherwise, run the planner using [scripts/loop.sh](scripts/loop.sh):

```bash
bash <path-to-loop.sh> $scan_dir planner.md "- depth: <depth>" 1 $cache_dir
```

Use a 10-minute timeout. If the command times out, re-run it — the script resumes from where it left off.

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
bash <path-to-loop.sh> $scan_dir nominator.md "- depth: <depth>" 5 $cache_dir
```

Use a 10-minute timeout. If the command times out, re-run it — the script resumes from where it left off.

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

Use a 10-minute timeout. If the command times out, re-run it — the script resumes from where it left off.

---

## Step 5: Verify Findings

List all `.md` files in `$scan_dir/findings/`. If none exist, write a `no-findings.md` summary and stop.

Using [scripts/loop.sh](scripts/loop.sh):

```bash
bash <path-to-loop.sh> $scan_dir verifier.md "" 5 $cache_dir
```

Use a 10-minute timeout. If the command times out, re-run it — the script resumes from where it left off.

---

## Completion

After all steps complete, report the scan results:

1. List all finding files in `$scan_dir/findings/`
2. Count verified vs rejected findings
3. Present a summary to the user
