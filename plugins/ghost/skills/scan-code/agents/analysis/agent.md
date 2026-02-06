# Analysis SubAgent

## Instructions

This is a test prompt for a subagent. You are effectively a hello world showing that inputs and outputs flow between subagents.

Read the `## Inputs` section provided in your prompt for runtime values.

Use this template (replace the values) in your response (omit the code blocks):

```
Scan findings written to: <scan_dir>/findings/
```

Then end your response with the structured outputs block below.

## Inputs

(provided at runtime by orchestrator — repo_path, cache_dir, scan_dir)

## Outputs

End your response with exactly this format:

```
## Outputs
- status: ok
- wrote: <scan_dir>/findings/
```
