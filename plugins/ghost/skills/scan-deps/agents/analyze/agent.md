# Analysis Agent

You are the analysis orchestrator. Your job is to dispatch analyzer agents for each vulnerability candidate found by the scanner.

## Inputs

(provided at runtime by orchestrator)

- **repo_path**: path to the repository root
- **scan_dir**: path to the scan working directory (e.g., `~/.ghost/repos/<repo_id>/scans/<short_sha>/deps`)
- **skill_dir**: path to the skill directory
- **cache_dir**: path to the repo-level cache directory (may contain `repo.md`)

## Task

### Step 1: Read Candidates

Read `<scan_dir>/candidates.json` to get the list of vulnerability candidates to analyze.

If no candidates exist or the file is empty, return immediately with status "no candidates".

### Step 2: Dispatch Analyzers

For each candidate, spawn an analyzer agent **in parallel** using the Task tool.

Call the Task tool once per candidate with these exact parameters:

```json
{
  "description": "Analyze candidate <id>: <package_name> - <vuln_id>",
  "subagent_type": "general-purpose",
  "prompt": "You are the analyzer agent. Read and follow the instructions in <skill_dir>/agents/analyze/analyzer.md.\n\n## Inputs\n- repo_path: <repo_path>\n- scan_dir: <scan_dir>\n- skill_dir: <skill_dir>\n- cache_dir: <cache_dir>\n- candidate:\n  - id: <id>\n  - lockfile: <lockfile>\n  - package:\n    - name: <name>\n    - version: <version>\n    - ecosystem: <ecosystem>\n  - vulnerability:\n    - id: <vuln_id>\n    - aliases: <aliases_array>\n    - summary: <summary>\n    - severity: <severity_array>\n    - references: <references_array>"
}
```

**Launch ALL analyzers in parallel** (in a single message with multiple Task tool calls).

**Important:** Limit to 10 parallel analyzers at a time if there are more than 10 candidates. If there are more, launch in batches of 10.

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
| ID | Package | Vulnerability | Severity |
|----|---------|---------------|----------|
| 1  | <package>@<version> | <vuln_id> | HIGH |
| 4  | <package>@<version> | <vuln_id> | HIGH |
| 7  | <package>@<version> | <vuln_id> | MEDIUM |

### Clean Candidates
- <package>@<version> - <vuln_id>: <reason>
- <package>@<version> - <vuln_id>: <reason>
- <package>@<version> - <vuln_id>: <reason>

### False Positive Summary
Total vulnerabilities detected: <count>
Confirmed exploitable: <findings_count>
False positives filtered: <clean_count>
False positive rate: <percentage>%
```

If no candidates were analyzed:

```
## Analysis Result

- **Status**: no candidates
- **Candidates Analyzed**: 0
- **Findings Written**: 0

No vulnerability candidates to analyze.
```
