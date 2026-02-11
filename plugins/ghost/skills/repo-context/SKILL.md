---
description: "Ghost repoistory/repo context builder. Gathers background codebase context about the contents and structure of the repository and outputs it to a file called repo.md as context to other skills performing code security analysis."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Repository Context Builder

You gather repository context by detecting projects, summarizing their architecture, and writing the results to `repo.md`. Do all work yourself — do not spawn subagents or delegate.

## Inputs

Parse these from `$ARGUMENTS` (key=value pairs):
- **repo_path**: path to the repository root
- **cache_dir**: path to the cache directory (defaults to `~/.ghost/repos/<repo_id>/cache`)

$ARGUMENTS

If `cache_dir` is not provided, compute it:
```bash
repo_name=$(basename "$(pwd)") && remote_url=$(git remote get-url origin 2>/dev/null || pwd) && short_hash=$(printf '%s' "$remote_url" | git hash-object --stdin | cut -c1-8) && repo_id="${repo_name}-${short_hash}" && cache_dir="$HOME/.ghost/repos/${repo_id}/cache" && echo "cache_dir=$cache_dir"
```

## Tool Restrictions

Do NOT use WebFetch or WebSearch. All work must use only local files in the repository.

## Setup

Discover this skill's own directory so you can reference agent files:
```bash
skill_dir=$(find . -path '*/skills/repo-context/SKILL.md' 2>/dev/null | head -1 | xargs dirname)
echo "skill_dir=$skill_dir"
```

---

## Check Cache First

Check if `<cache_dir>/repo.md` already exists. If it does, skip everything and return:

```
Repository context is at: <cache_dir>/repo.md
```

If it does not exist, run `mkdir -p <cache_dir>` and continue.

---

## Step 1: Detect Projects

Read `<skill_dir>/detector.md` and follow its instructions against `<repo_path>`. This will produce a list of detected projects and a repository summary.

Save the full detection output — you'll need each project's details for Step 2.

## Step 2: Summarize Each Project

Read `<skill_dir>/summarizer.md`. Then, for EACH project detected in Step 1, follow the summarizer instructions using that project's details (id, type, base_path, languages, frameworks, dependency_files, extensions, evidence) as inputs.

Collect the summary result for each project.

## Step 3: Write repo.md

Combine the detection and summary results into `<cache_dir>/repo.md`. Read `<skill_dir>/template-repo.md` for the exact output format.

For each project, include:
- Detection section (from Step 1): ID, Type, Base Path, Languages, Frameworks, Dependency Files, Extensions, Evidence
- Summary section (from Step 2): architectural summary, Sensitive Data Types, Business Criticality, Component Map, Evidence

## Step 4: Show Output

```
Repository context is at: <cache_dir>/repo.md

```