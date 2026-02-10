---
name: ghost:scan-sca
description: |
  Ghost Security - Software Composition Analysis scanner.
  Scans dependency lockfiles for known vulnerabilities.
allowed-tools: Read, Glob, Grep, Bash, Task, TodoRead, TodoWrite
argument-hint: "[path-to-scan]"
disable-model-invocation: true
user-invocable: true
---

# Ghost Security SCA Scanner — Orchestrator

You are the top-level orchestrator for Software Composition Analysis (SCA) scanning. Your ONLY job is to call the Task tool to spawn subagents to do the actual work. Each step below gives you the exact Task tool parameters to use. Do not do the work yourself.

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
scan_id=$(date +%Y%m%d-%H%M%S) && mkdir -p .ghost/scans/$scan_id/findings && skill_dir=$(find . -path '*skills/scan-sca/SKILL.md' 2>/dev/null | head -1 | xargs dirname) && echo "scan_id=$scan_id skill_dir=$skill_dir"
```

Store `scan_id`, compute `scan_dir` = `<repo_path>/.ghost/scans/<scan_id>`, and store `skill_dir` (the absolute path to the skill directory containing `agents/`, `scripts/`, etc.).

After this step, your only remaining tool is Task. Do not use Bash, Read, Grep, Glob, or any other tool for Steps 1–5.

### Step 1: Initialize Wraith

Call the Task tool to initialize the wraith binary:
```json
{
  "description": "Initialize wraith binary",
  "subagent_type": "general-purpose",
  "prompt": "You are the init agent. Read and follow the instructions in <skill_dir>/agents/init/agent.md.\n\n## Inputs\n- skill_dir: <skill_dir>"
}
```

The init agent installs wraith to `~/.ghost/bin/wraith` (or `wraith.exe` on Windows).

### Step 2: Discover Lockfiles

Call the Task tool to discover lockfiles in the repository:
```json
{
  "description": "Discover lockfiles",
  "subagent_type": "general-purpose",
  "prompt": "You are the discover agent. Read and follow the instructions in <skill_dir>/agents/discover/agent.md.\n\n## Inputs\n- repo_path: <repo_path>\n- scan_dir: <scan_dir>\n- scan_id: <scan_id>"
}
```

The discover agent finds all lockfiles (go.mod, package-lock.json, etc.) and writes `<scan_dir>/lockfiles.json`.

**If lockfile count is 0**: Skip to Step 5 (Summarize) with no lockfiles found.

### Step 3: Scan for Vulnerabilities

Call the Task tool to run the wraith scanner:
```json
{
  "description": "Scan for vulnerabilities",
  "subagent_type": "general-purpose",
  "prompt": "You are the scan agent. Read and follow the instructions in <skill_dir>/agents/scan/agent.md.\n\n## Inputs\n- repo_path: <repo_path>\n- scan_dir: <scan_dir>"
}
```

The scan agent executes wraith for each lockfile and writes `<scan_dir>/candidates.json`.

**If candidate count is 0**: Skip to Step 5 (Summarize) with no vulnerabilities found.

### Step 4: Analyze Candidates

Call the Task tool to analyze the vulnerability candidates:
```json
{
  "description": "Analyze vulnerability candidates",
  "subagent_type": "general-purpose",
  "prompt": "You are the analysis agent. Read and follow the instructions in <skill_dir>/agents/analyze/agent.md.\n\n## Inputs\n- repo_path: <repo_path>\n- scan_dir: <scan_dir>\n- skill_dir: <skill_dir>"
}
```

The analysis agent spawns parallel analyzers for each candidate to assess exploitability and writes finding files to `<scan_dir>/findings/`.

### Step 5: Summarize Results

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
