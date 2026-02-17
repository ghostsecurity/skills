---
name: "ghost-scan-secrets"
description: |
  Ghost Security - Secrets and credentials scanner. Scans codebase for leaked API keys, tokens, passwords, and sensitive data. Detects hardcoded secrets and generates findings with severity and remediation guidance. Use when the user asks to check for leaked secrets, scan for credentials, find hardcoded API keys or passwords, detect exposed .env values, or audit code for sensitive data exposure.
allowed-tools: Read, Glob, Grep, Bash, Task, TodoRead, TodoWrite
argument-hint: "[path-to-scan]"
license: apache-2.0
metadata:
  version: 1.1.0
---

# Ghost Security Secrets Scanner — Orchestrator

You are the top-level orchestrator for secrets scanning. Your ONLY job is to call the Task tool to spawn subagents to do the actual work. Each step below gives you the exact Task tool parameters to use. Do not do the work yourself.

## Defaults

- **repo_path**: the current working directory
- **scan_dir**: `~/.ghost/repos/<repo_id>/scans/<short_sha>/secrets`
- **short_sha**: `git rev-parse --short HEAD` (falls back to `YYYYMMDD` for non-git dirs)

$ARGUMENTS

Any values provided above override the defaults.

---

## Execution

1. **Setup** — compute paths and create output directories
2. **Initialize Poltergeist** — install the poltergeist binary
3. **Scan for Secrets** — run poltergeist against the codebase
4. **Analyze Candidates** — assess each candidate for confirmation
5. **Summarize Results** — generate the final scan report

### Step 0: Setup

Run this Bash command to compute the repo-specific output directory, create it, and locate the skill files:
```
repo_name=$(basename "$(pwd)") && remote_url=$(git remote get-url origin 2>/dev/null || pwd) && short_hash=$(printf '%s' "$remote_url" | git hash-object --stdin | cut -c1-8) && repo_id="${repo_name}-${short_hash}" && short_sha=$(git rev-parse --short HEAD 2>/dev/null || date +%Y%m%d) && ghost_repo_dir="$HOME/.ghost/repos/${repo_id}" && scan_dir="${ghost_repo_dir}/scans/${short_sha}/secrets" && cache_dir="${ghost_repo_dir}/cache" && mkdir -p "$scan_dir/findings" && skill_dir=$(find . -path '*skills/scan-secrets/SKILL.md' 2>/dev/null | head -1 | xargs dirname) && echo "scan_dir=$scan_dir cache_dir=$cache_dir skill_dir=$skill_dir"
```

Store `scan_dir` (the absolute path under `~/.ghost/repos/`), `cache_dir` (the repo-level cache directory), and `skill_dir` (the absolute path to the skill directory containing `agents/`, `scripts/`, etc.).

After this step, your only remaining tool is Task. Do not use Bash, Read, Grep, Glob, or any other tool for Steps 1–4.

### Step 1: Initialize Poltergeist

Call the Task tool to initialize the poltergeist binary:
```json
{
  "description": "Initialize poltergeist binary",
  "subagent_type": "general-purpose",
  "prompt": "You are the init agent. Read and follow the instructions in <skill_dir>/agents/init/agent.md.\n\n## Inputs\n- skill_dir: <skill_dir>"
}
```

The init agent installs poltergeist to `~/.ghost/bin/poltergeist` (or `poltergeist.exe` on Windows).

### Step 2: Scan for Secrets

Call the Task tool to run the poltergeist scanner:
```json
{
  "description": "Scan for secret candidates",
  "subagent_type": "general-purpose",
  "prompt": "You are the scan agent. Read and follow the instructions in <skill_dir>/agents/scan/agent.md.\n\n## Inputs\n- repo_path: <repo_path>\n- scan_dir: <scan_dir>"
}
```

The scan agent returns the candidate count and writes `<scan_dir>/candidates.json`.

**If candidate count is 0**: Skip to Step 4 (Summarize) with no findings.

### Step 3: Analyze Candidates

Call the Task tool to analyze the candidates:
```json
{
  "description": "Analyze secret candidates",
  "subagent_type": "general-purpose",
  "prompt": "You are the analysis agent. Read and follow the instructions in <skill_dir>/agents/analyze/agent.md.\n\n## Inputs\n- repo_path: <repo_path>\n- scan_dir: <scan_dir>\n- skill_dir: <skill_dir>\n- cache_dir: <cache_dir>"
}
```

The analysis agent spawns parallel analyzers for each candidate and writes finding files to `<scan_dir>/findings/`.

### Step 4: Summarize Results

Call the Task tool to summarize the findings:
```json
{
  "description": "Summarize scan results",
  "subagent_type": "general-purpose",
  "prompt": "You are the summarize agent. Read and follow the instructions in <skill_dir>/agents/summarize/agent.md.\n\n## Inputs\n- repo_path: <repo_path>\n- scan_dir: <scan_dir>\n- skill_dir: <skill_dir>\n- cache_dir: <cache_dir>"
}
```

After executing all the tasks, report the scan results to the user.

---

## Error Handling

If any Task call fails, retry it **once**. If it fails again, stop and report the failure.
