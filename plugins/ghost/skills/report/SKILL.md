---
description: "Ghost Security — combined security report. Aggregates findings from all scan skills (scan-deps, scan-secrets, scan-code) into a single prioritized report focused on the highest risk, highest confidence issues."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Combined Security Report

You aggregate findings from all scan skills (scan-deps, scan-secrets, scan-code) into a single prioritized report. Do all work yourself — do not spawn subagents or delegate.

$ARGUMENTS

---

## Step 0: Setup

Run this Bash command to compute paths:
```bash
repo_name=$(basename "$(pwd)") && remote_url=$(git remote get-url origin 2>/dev/null || pwd) && short_hash=$(printf '%s' "$remote_url" | git hash-object --stdin | cut -c1-8) && repo_id="${repo_name}-${short_hash}" && short_sha=$(git rev-parse --short HEAD 2>/dev/null || date +%Y%m%d) && ghost_repo_dir="$HOME/.ghost/repos/${repo_id}" && scans_dir="${ghost_repo_dir}/scans/${short_sha}" && cache_dir="${ghost_repo_dir}/cache" && skill_dir=$(find . -path '*/skills/report/SKILL.md' 2>/dev/null | head -1 | xargs dirname) && echo "scans_dir=$scans_dir cache_dir=$cache_dir skill_dir=$skill_dir"
```

Store `scans_dir` (commit-level scan directory), `cache_dir`, and `skill_dir`.

---

## Cache Check

If `<scans_dir>/report.md` already exists, show:

```
Combined security report is at: <scans_dir>/report.md
```

And stop. Do not regenerate it.

---

## Step 1: Read Repo Context

Read `<cache_dir>/repo.md` if it exists. Extract:
- Business criticality
- Sensitive data types
- Component map

If it does not exist, continue without it — this is not an error.

---

## Step 2: Discover Scan Results

List the contents of `<scans_dir>` to see which scan-type directories exist. Recognized types:
- `deps/` — SCA / dependency vulnerability scan
- `secrets/` — secrets and credentials scan
- `code/` — code security scan (SAST)

If none of these directories exist, report an error:

```
No scan results found in <scans_dir>. Run one or more scan skills first:
  /ghost:scan-deps
  /ghost:scan-secrets
  /ghost:scan-code
```

And stop.

---

## Step 3: Collect Findings

For each scan type that exists, glob `<scans_dir>/<type>/findings/*.md` and read each finding file **in full**. Retain the complete markdown body of every finding — the report will inline this content directly so readers never need to open individual finding files.

From each finding, also extract these metadata fields for filtering and sorting:

- **ID** — from `## Metadata` → `ID`
- **Type** — the scan type (`deps`, `secrets`, or `code`)
- **Severity** — from `## Metadata` → `Severity` (high, medium, low)
- **Status** — from `## Metadata` → `Status` (e.g., confirmed-exploitable, unverified, verified, rejected, clean)

---

## Step 4: Filter and Sort

**Filter:** Keep only high-confidence findings:
- For `deps` findings: status is `confirmed-exploitable`
- For `secrets` findings: status is NOT `clean` and NOT `rejected`
- For `code` findings: status is `verified` or `unverified` (NOT `rejected`)

**Exclude** any finding with status `clean`, `rejected`, or `false-positive`.

**Sort** the remaining findings:
1. By severity: high first, then medium, then low
2. Within same severity: deps before secrets before code

---

## Step 5: Read Per-Scan Reports

For `deps` and `secrets` scan types, read `<scans_dir>/<type>/report.md` if present. Extract:
- Statistics (candidates scanned, confirmed findings, false positives filtered)
- Executive summary highlights

Note: `code` does not produce a `report.md`. For code scan coverage, count the finding files in `<scans_dir>/code/findings/` directly. The "Candidates Scanned" count is the total number of finding files (all statuses). "Confirmed Findings" is the count with status `verified`, `confirmed`, or `unverified`. "False Positives Filtered" is the count with status `rejected`. Do NOT count clean file analyses from the nomination/analysis funnel — those never became findings.

If a per-scan report does not exist for deps or secrets, note it as unavailable.

---

## Step 6: Generate Report

1. Read `<skill_dir>/report-template.md`
2. Populate the template with collected data:
   - Fill Scan Information with repository name, commit SHA, date, and which scans ran
   - Write Executive Summary using repo context and aggregated findings
   - For Critical & High findings (severity = high): inline the substantive content from each finding file directly into the report — include code snippets, assessment tables, remediation commands, and all relevant detail so the report is fully self-contained
   - For Medium findings: write a full subsection per finding with description, location, code context, and remediation (not a condensed table)
   - Omit low-severity findings (they remain in per-scan finding files only)
   - Fill Scan Coverage table from per-scan report statistics (for code, use finding file counts from Step 5)
   - Add a brief methodology note per scan type that ran (1-2 sentences drawn from per-scan reports)
   - Do NOT include links to per-scan reports or individual finding files — all content is inlined
3. Write the report to `<scans_dir>/report.md`

---

## Step 7: Show Output

```
Combined security report is at: <scans_dir>/report.md
```
