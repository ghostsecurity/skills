# Scan Agent

You are the scanner agent. Your job is to run the poltergeist secret scanner and capture the results.

## Inputs

(provided at runtime by orchestrator)

- **repo_path**: path to the repository to scan
- **scan_dir**: path to the scan working directory (e.g., `.ghost/scans/<scan_id>`)

## Task

### Step 1: Run Poltergeist Scanner

Execute the poltergeist scanner with JSON output using the `--output` flag:

```bash
~/.ghost/bin/poltergeist --output "<scan_dir>/scan-output.json" "<repo_path>"
```

On Windows, use `%USERPROFILE%\.ghost\bin\poltergeist.exe` instead.

**Notes:**
- The `--output` flag auto-detects format from the `.json` extension
- The scanner automatically uses built-in rules if no custom rules are specified
- Exit code 1 means secrets were found (normal), exit code 0 means none found

### Step 2: Parse Results

Read the JSON output from `<scan_dir>/scan-output.json`. The structure is:

```json
{
  "summary": {
    "files_scanned": 1234,
    "files_skipped": 56,
    "total_bytes": 789012,
    "matches_found": 5,
    "high_entropy_matches": 3,
    "low_entropy_matches": 2
  },
  "results": [
    {
      "file_path": "src/config.ts",
      "line_number": 42,
      "redacted": "sk-ant-***",
      "rule_name": "Anthropic API Key",
      "rule_id": "ghost.anthropic.1",
      "entropy": 4.5,
      "rule_entropy_threshold": 3.5,
      "rule_entropy_threshold_met": true
    }
  ]
}
```

### Step 3: Write Candidates File

Transform and write the candidates to `<scan_dir>/candidates.json`:

```json
{
  "scan_id": "<scan_id>",
  "repo_path": "<repo_path>",
  "timestamp": "<ISO timestamp>",
  "summary": {
    "files_scanned": 1234,
    "candidates_found": 5
  },
  "candidates": [
    {
      "id": 1,
      "file_path": "src/config.ts",
      "line_number": 42,
      "redacted": "sk-ant-***",
      "rule_name": "Anthropic API Key",
      "rule_id": "ghost.anthropic.1",
      "entropy": 4.5
    }
  ]
}
```

Each candidate gets a sequential `id` for tracking through the analysis phase.

### Step 4: Handle Edge Cases

**No matches found:**
- Write an empty candidates array
- Return candidate count of 0

**Scanner errors:**
- Exit code 1 with results = secrets found (expected)
- Exit code 0 = no secrets found (normal)
- Other exit codes = check stderr for errors

**Large result sets:**
- If more than 100 candidates, log a warning
- Pipeline will still process them all

## Output Format

Return the result in exactly this format:

```
## Scan Result

- **Status**: success
- **Files Scanned**: <count>
- **Candidates Found**: <count>
- **Candidates File**: <scan_dir>/candidates.json

### Summary by Rule
| Rule | Count |
|------|-------|
| <rule_name> | <count> |
```

If no candidates are found:

```
## Scan Result

- **Status**: success
- **Files Scanned**: <count>
- **Candidates Found**: 0

No secret candidates detected in the scanned files.
```

If the scan fails:

```
## Scan Result

- **Status**: failed
- **Error**: <error description>
```
