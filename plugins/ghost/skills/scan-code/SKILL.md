---
name: scan-code
description: |
  Ghost Security - Static application security testing (SAST) scanner.
  Runs a multi-phase analysis pipeline that performs a code security vulnerability analysis.
  Supports full-repo scans and commit-diff scans.
  Use when the user wants to scan code with ghost for security vulnerabilities
allowed-tools: Read, Glob, Grep, Bash, Task, TodoRead, TodoWrite, TaskCreate, TaskUpdate, TaskGet, TaskList
argument-hint: "[provided-extra-details]"
disable-model-invocation: true
user-invocable: true
---

# Ghost Security Code Scanner — Orchestrator

You are the top-level orchestrator. Your ONLY job is to call the Task tool 5 times to spawn subagents to do the actual work. Each step below gives you the exact Task tool parameters to use. Do not do the work yourself. Do not launch the "scan-code" skill from here (nested runs of scan-code) as /scan-code is already running.

## Defaults

- **repo_path**: the current working directory
- **cache_dir**: `.ghost/cache`
- **scan_dir**: `.ghost/scans/<scan_id>`
- **scan_id**: `YYYYMMDD-HHMMSS` timestamp

$ARGUMENTS

Any values provided above override the defaults.

---

## Execution

### Step 0: Setup

Run this Bash command to generate scan_id, create the scan directory, and locate the skill files:
```
scan_id=$(date +%Y%m%d-%H%M%S) && mkdir -p .ghost/scans/$scan_id && skill_dir=$(find . -path '*/.claude/skills/scan-code/SKILL.md' -o -path '*/.claude/plugins/*/skills/*/skills/scan-code/SKILL.md' 2>/dev/null | head -1 | xargs dirname) && echo "scan_id=$scan_id skill_dir=$skill_dir"
```

Store `scan_id`, compute `scan_dir` = `<repo_path>/.ghost/scans/<scan_id>`, and store `skill_dir` (the absolute path to the skill directory containing `agents/`, `criteria/`, etc.).

After this step, your only remaining tool is Task. Do not use Bash, Read, Grep, Glob, or any other tool for Steps 1–5.

### Step 1: Gather codebase context

Call the Task tool with these exact parameters (replace placeholders with actual values) to get a subagent to gather codebase context:
```json
{
  "description": "Gather codebase context",
  "subagent_type": "general-purpose",
  "prompt": "You are the context agent. Read and follow the instructions in <skill_dir>/agents/context/agent.md.\n\n## Inputs\n- repo_path: <repo_path>\n- cache_dir: <cache_dir>\n- skill_dir: <skill_dir>"
}
```

### Step 2: Plan what to scan

Call the Task tool with these exact parameters (replace placeholders with actual values, omit base_commit/head_commit lines if not in arguments) to get a subagent to plan what to scan:
```json
{
  "description": "Plan what to scan",
  "subagent_type": "general-purpose",
  "prompt": "You are the plan agent. Read and follow the instructions in <skill_dir>/agents/plan/agent.md.\n\n## Inputs\n- repo_path: <repo_path>\n- cache_dir: <cache_dir>\n- scan_dir: <scan_dir>\n- skill_dir: <skill_dir>\n- base_commit: <base_commit>\n- head_commit: <head_commit>"
}
```

### Step 3: Analyze code for vulnerabilities

Call the Task tool with these exact parameters (replace placeholders with actual values) to get a subagent to analyze code for vulnerabilities:
```json
{
  "description": "Analyze code for vulnerabilities",
  "subagent_type": "general-purpose",
  "prompt": "You are the analysis agent. Read and follow the instructions in <skill_dir>/agents/analyze/agent.md.\n\n## Inputs\n- repo_path: <repo_path>\n- cache_dir: <cache_dir>\n- scan_dir: <scan_dir>\n- skill_dir: <skill_dir>"
}
```

### Step 4: Verify findings

Call the Task tool with these exact parameters (replace placeholders with actual values) to get a subagent to verify findings:
```json
{
  "description": "Verify findings",
  "subagent_type": "general-purpose",
  "prompt": "You are the verification agent. Read and follow the instructions in <skill_dir>/agents/verify/agent.md.\n\n## Inputs\n- repo_path: <repo_path>\n- cache_dir: <cache_dir>\n- scan_dir: <scan_dir>\n- skill_dir: <skill_dir>"
}
```

### Step 5: Summarize results

Call the Task tool with these exact parameters (replace placeholders with actual values) to get a subagent to summarize results:
```json
{
  "description": "Summarize results",
  "subagent_type": "general-purpose",
  "prompt": "You are the summarize agent. Read and follow the instructions in <skill_dir>/agents/summarize/agent.md.\n\n## Inputs\n- repo_path: <repo_path>\n- cache_dir: <cache_dir>\n- scan_dir: <scan_dir>\n- skill_dir: <skill_dir>"
}
```

After executing all the tasks, report the scan results to the user.

---

## Error handling

If any Task call fails, retry it **once**. If it fails again, stop and report the failure.
