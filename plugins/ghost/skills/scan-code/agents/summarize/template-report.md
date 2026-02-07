# Security Scan Report

## Scan Overview
- **Scan ID**: <scan_id>
- **Mode**: <fresh|incremental>
- **Date**: <timestamp>
- **Projects Scanned**: <count>

## Executive Summary
<2-4 sentence overview of findings: total count, severity breakdown, most critical issues. If no verified findings, state that the scan completed cleanly.>

## Findings Summary
| Severity | Count |
|----------|-------|
| High     | <n>   |
| Medium   | <n>   |
| Low      | <n>   |
| **Total**| <n>   |

## What to Address

[Instructions: Top 1-5 (ideally no more than 3) risks that require fixng now because they are trivially exploitable with minimal skill/guessing and high impact, ordered by exploitability and impact. Note any findings that chain together (e.g. missing auth + injection on the same endpoint). If nothing is exploitable: "No directly exploitable vulnerabilities were identified in this scan." Use the list format here:]

1. **<Finding Title>** — `<file>:<line>` — <1-2 sentences: what an attacker can do, what's at stake. If it compounds with another finding, say which and how.>
2. ...

## Findings by Project

### Project: <project_id>

#### <Finding Title>
- **ID**: <finding_id>
- **Severity**: <severity>
- **CWE**: <cwe>
- **Vector**: <vector>
- **Location**: <file>:<line> (`<function>`)
- **Description**: <description>
- **Vulnerable Code**: <code block>
- **Remediation**: <remediation>
- **Fixed Code**: <code block>

[repeat per finding, ordered high → medium → low]

---

## Scan Statistics
- Vectors scanned: <from plan.md>
- Findings produced: <total before verification>
- Verified: <count>
- Rejected: <count>

## Rejected Findings
| ID | Title | Severity | Rejection Reason |
|----|-------|----------|------------------|
| <finding_id> | <title> | <severity> | <reason> |
