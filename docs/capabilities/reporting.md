# Reporting

The `ghost-report` skill aggregates findings from dependency, secret, and code scans into a single document prioritized by actual risk, not just CVSS scores.

<div align="center">
<img src="https://media.ghostsecurity.ai/skills/report.gif" alt="Running the ghost-report skill" width="800">
</div>

## How it works

The skill reads findings from all completed scans and produces a single prioritized Markdown document.

### Collection

The skill discovers which scans have been run by checking for output directories:

- `deps/findings/` -- dependency vulnerability findings
- `secrets/findings/` -- leaked secret findings
- `code/findings/` -- code analysis findings

Each finding file is read in full, and metadata is extracted: ID, type, severity, status, and validation evidence.

### Filtering

Not everything makes it into the report:

- **Dependency findings** must have status `confirmed-exploitable` (AI analysis confirmed the vulnerability is reachable)
- **Secret findings** must not be `clean` or `rejected` (AI assessment determined it's a real risk)
- **Code findings** must be `verified` or `unverified`. Rejected findings are excluded.

Only findings that survived AI analysis appear in the final output.

### Prioritization

Findings are sorted by:

1. **Severity** -- high, then medium (low-severity findings are omitted from the combined report)
2. **Type** -- dependencies, then secrets, then code findings

Severity isn't just the CVE's CVSS score. For dependency findings, it's the AI-assessed contextual severity that factors in exploitability. For code findings, it's the verified severity based on criteria validation.

## Report structure

The generated `report.md` follows a consistent structure:

### Executive summary

One to two paragraphs covering the overall security posture: how many scans ran, what was found, which areas are clean, and what needs attention. The summary references the repository context (business criticality, sensitive data types) to frame findings in terms of business impact.

### Critical and high findings

Each finding is inlined in full. The report includes:

- Vulnerability description
- Affected file and line number
- Vulnerable code snippet
- Severity and CWE classification
- Exploitability assessment
- Remediation guidance with corrected code

The report is self-contained. You can hand it to a developer and they have everything they need to understand and fix the issue.

### Medium findings

Medium-severity findings get full subsections too.

### Scan coverage

A table showing what each scan covered:

| Scan type | Status | Candidates | Confirmed | False positives |
|---|---|---|---|---|
| Dependencies | Completed | 12 | 3 | 9 |
| Secrets | Completed | 8 | 2 | 6 |
| Code | Completed | 25 | 5 | 20 |

### Methodology

Brief notes on what each scan covered and how: which tools were used, what depth was selected for code analysis, and any relevant configuration.

## Generating a report

After running one or more scans:

```shell
claude "/ghost-report"
```

The report is written to `~/.ghost/repos/<repo_id>/scans/<commit_sha>/report.md` and cached. Regenerating it on the same commit returns the cached version.

If you haven't run any scans yet, the report skill will tell you and suggest running the appropriate scans first.

---

Previous: [Live validation](live-validation.md) | Next: [Poltergeist](../tools/poltergeist.md) | [Docs home](../../README.md#documentation)
