---
name: find-issues
description: "Find security issues in a repository by planning and executing targeted vulnerability scans."
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
argument-hint: "[depth=quick]"
---

# Find Issues

You find security issues in a repository. This skill plans which vulnerability vectors to scan, then executes those scans against each project.

## Inputs

- **depth**: `quick` (default), `balanced`, or `full` — override via `$ARGUMENTS`

$ARGUMENTS

---

## Step 1: Setup

Generate a scan_id and locate the skill directory:
```bash
scan_id=$(git rev-parse --short HEAD) && mkdir -p .ghost/scans/$scan_id
skill_dir=$(dirname $(find .claude/skills -name "loop.sh" -path "*/find-issues/*" | head -1))/..
```

1. Read `.ghost/cache/repo.md` — if missing, **stop** and report: "Error: repo.md not found. Run the repo-context skill first."
2. Read `$skill_dir/criteria/index.yaml` to get the valid agent→vector mappings per project type
3. Set `depth` to `quick` if not provided

---

## Step 2: Plan Scans

If `.ghost/scans/$scan_id/plan.md` already exists, skip to the next step.

Otherwise, run the planner:

```bash
bash $skill_dir/scripts/loop.sh .ghost/scans/$scan_id planner.md "- depth: <depth>"
```

Use a 10-minute timeout. If the command times out, re-run it — the script resumes from where it left off.

---

## Step 3: Nominate Files

If `.ghost/scans/$scan_id/nominations.md` does not exist, generate it by reading `.ghost/scans/$scan_id/plan.md` and for each project section (`## Project: <base_path> (<type>)`), parse the Recommended Scans table. For each row, extract the Agent and Vector columns. Write `.ghost/scans/$scan_id/nominations.md` - one line per (project, agent, vector) combination. Skip projects with empty scan tables.

```markdown
# Nominations

- [ ] <base_path> (<type>) | <agent> | <vector>
- [ ] <base_path> (<type>) | <agent> | <vector>
...
```

If `.ghost/scans/$scan_id/nominations.md` already exists, change every top level task `- [x]` to `- [ ]`. Keep all indented lines/subtasks beneath each item unchanged.

### Run nomination script

```bash
bash $skill_dir/scripts/loop.sh .ghost/scans/$scan_id nominator.md "- depth: <depth>" 5
```

Use a 10-minute timeout. If the command times out, re-run it — the script resumes from where it left off.

---

## Step 4: Analyze Nominated Files

Read `.ghost/scans/$scan_id/nominations.md`. For each candidate file under a checked `- [x]` line, append to `.ghost/scans/$scan_id/analyses.md` (skip candidates already listed in `analyses.md`).

```
- [ ] <base_path> (<type>) | <agent> | <vector> | <candidate_file>
```

Create the findings directory:
```bash
mkdir -p .ghost/scans/$scan_id/findings
```

### Run analysis script

```bash
bash $skill_dir/scripts/loop.sh .ghost/scans/$scan_id analyzer.md "" 5
```

Use a 10-minute timeout. If the command times out, re-run it — the script resumes from where it left off.

---

## Step 5: Verify Findings

List all `.md` files in `.ghost/scans/$scan_id/findings/`. If none exist, write a `no-findings.md` summary and stop.

```bash
bash $skill_dir/scripts/loop.sh .ghost/scans/$scan_id verifier.md "" 5
```

Use a 10-minute timeout. If the command times out, re-run it — the script resumes from where it left off.

---

## Completion

After all steps complete, report the scan results:

1. List all finding files in `.ghost/scans/$scan_id/findings/`
2. Count verified vs rejected findings
3. Present a summary to the user