# Scan Plan

## Scan Mode
[fresh | incremental]

## Commit Range
- Base: [commit or "n/a"]
- Head: [commit or "n/a"]

---

## Project: [base_path] ([type])
- **Criticality**: [high|medium|low]
- **Languages**: [comma-separated]
- **Frameworks**: [comma-separated]
- **Sensitive Data**: [comma-separated or "none"]
- **Status**: [new|existing]

### Scan Reasoning
[2-3 sentences from planner. Format depends on mode:]
[INCREMENTAL: "Component X (crit:0.85, sig:high) needs [agent] scan because [mapping reason]"]
[FRESH: "New [type] project with [framework] and [criticality] criticality needs [agent] scan"]
[ZERO SCANS: "No security-relevant changes detected — no scans recommended"]

### Change Summary
(from diff analyzer, or "Fresh scan — no prior baseline")
[1-2 sentence summary]

### Recommended Scans
(may be empty — valid for projects with no security-relevant changes)

| Priority | Agent | Reason |
|----------|-------|--------|
| P1 | [agent_name] | [reason] |

### Changed Components
(incremental only — omit entire section for fresh scans)

| Component | Type | Criticality | Significance | +Lines | -Lines |
|-----------|------|-------------|--------------|--------|--------|
| [name] | [type] | [crit] | [sig] | [add] | [del] |

### Unmapped Files
(incremental only, if any — omit if none)
- [file_path]

---

## Project: [next project]
[same structure repeats — EVERY project gets an entry]
