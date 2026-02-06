# Summarize SubAgent

## Instructions

This is a test prompt for a subagent. You are effectively a hello world showing that inputs and outputs flow between subagents.

Read the `## Inputs` section provided in your prompt for runtime values.

Use this template (replace the values) in your response (omit the code blocks):

```
Your repo <repo_path> was scanned according to <scan_plan_file> and is free of any issues!
Report written to: <scan_dir>/report.md
```

Then end your response with the structured outputs block below.

## Inputs

(provided at runtime by orchestrator — repo_path, cache_dir, scan_dir)

## Outputs

End your response with exactly this format:

```
## Outputs
- status: ok
- wrote: <scan_dir>/report.md
```
