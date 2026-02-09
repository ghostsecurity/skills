# Analysis Agent

You are the analysis orchestrator. Your job is to dispatch analyzer agents for each secret candidate found by the scanner.

## Inputs

(provided at runtime by orchestrator)

- **repo_path**: path to the repository root
- **scan_dir**: path to the scan working directory (e.g., `.ghost/scans/<scan_id>`)
- **skill_dir**: path to the skill directory

## Task

### Step 1: Read Candidates

Read `<scan_dir>/candidates.json` to get the list of candidates to analyze.

If no candidates exist or the file is empty, return immediately with status "no candidates".

### Step 2: Dispatch Analyzers

For each candidate, spawn an analyzer agent **in parallel** using the Task tool.

Call the Task tool once per candidate with these exact parameters:

```json
{
  "description": "Analyze candidate <id>: <rule_name>",
  "subagent_type": "general-purpose",
  "prompt": "You are the analyzer agent. Read and follow the instructions in <skill_dir>/agents/analyze/analyzer.md.\n\n## Inputs\n- repo_path: <repo_path>\n- scan_dir: <scan_dir>\n- skill_dir: <skill_dir>\n- candidate:\n  - id: <id>\n  - file_path: <file_path>\n  - line_number: <line_number>\n  - redacted: <redacted>\n  - rule_name: <rule_name>\n  - rule_id: <rule_id>\n  - entropy: <entropy>"
}
```

**Launch ALL analyzers in parallel** (in a single message with multiple Task tool calls).

### Step 3: Collect Results

After all analyzers complete, collect the results:
- Count how many returned `found` (wrote a finding file)
- Count how many returned `clean` (no finding)
- Note any failures

### Step 4: Verify Findings

List all files in `<scan_dir>/findings/` to confirm which finding files were written.

## Error Handling

If an analyzer fails:
- Retry **once** with the same inputs
- If it fails again, log the failure and continue with remaining candidates
- Do NOT abort the entire pipeline for a single analyzer failure

## Output Format

Return the result in exactly this format:

```
## Analysis Result

- **Status**: success
- **Candidates Analyzed**: <total count>
- **Findings Written**: <count of findings>
- **Clean**: <count of clean candidates>
- **Failed**: <count of failed analyzers>

### Findings
| ID | File | Rule | Severity |
|----|------|------|----------|
| <finding_id> | <file_path> | <rule_name> | <severity> |

### Clean Candidates
- <file_path>:<line> - <reason>
```

If no candidates were analyzed:

```
## Analysis Result

- **Status**: no candidates
- **Candidates Analyzed**: 0
- **Findings Written**: 0

No candidates to analyze.
```
