---
name: ghost:scan-secrets
description: |
  Ghost Security - Secrets and credentials scanner.
  Scans codebase for leaked API keys, tokens, passwords, and sensitive data.
  Uses poltergeist scanner with AI-powered false positive reduction.
allowed-tools: Read, Glob, Grep, Bash, Task, TodoRead, TodoWrite
argument-hint: "[path-to-scan]"
disable-model-invocation: true
user-invocable: true
---

# Ghost Security Secrets Scanner — Orchestrator

You are the top-level orchestrator for secrets scanning. Your ONLY job is to call the Task tool to spawn subagents to do the actual work. Each step below gives you the exact Task tool parameters to use. Do not do the work yourself.

## Defaults

- **repo_path**: the current working directory
- **scan_dir**: `.ghost/scans/<scan_id>`
- **scan_id**: `YYYYMMDD-HHMMSS` timestamp

$ARGUMENTS

Any values provided above override the defaults.

---

## Execution

### Step 0: Setup

Run this Bash command to generate scan_id, create the scan directory, and locate the skill files:
```
scan_id=$(date +%Y%m%d-%H%M%S) && mkdir -p .ghost/scans/$scan_id/findings && skill_dir=$(find . -path '*skills/scan-secrets/SKILL.md' 2>/dev/null | head -1 | xargs dirname) && echo "scan_id=$scan_id skill_dir=$skill_dir"
```

Store `scan_id`, compute `scan_dir` = `<repo_path>/.ghost/scans/<scan_id>`, and store `skill_dir` (the absolute path to the skill directory containing `agents/`, `scripts/`, etc.).

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
  "prompt": "You are the analysis agent. Read and follow the instructions in <skill_dir>/agents/analyze/agent.md.\n\n## Inputs\n- repo_path: <repo_path>\n- scan_dir: <scan_dir>\n- skill_dir: <skill_dir>"
}
```

The analysis agent spawns parallel analyzers for each candidate and writes finding files to `<scan_dir>/findings/`.

### Step 4: Summarize Results

Call the Task tool to summarize the findings:
```json
{
  "description": "Summarize scan results",
  "subagent_type": "general-purpose",
  "prompt": "You are the summarize agent. Read and follow the instructions in <skill_dir>/agents/summarize/agent.md.\n\n## Inputs\n- repo_path: <repo_path>\n- scan_dir: <scan_dir>\n- skill_dir: <skill_dir>"
}
```

After executing all the tasks, report the scan results to the user.

---

## Error Handling

If any Task call fails, retry it **once**. If it fails again, stop and report the failure.
