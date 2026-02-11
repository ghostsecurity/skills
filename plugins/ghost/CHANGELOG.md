# Changelog

## 1.0.0 — 2025-02-13

Initial release of the Ghost Security skills plugin for Claude Code.

### Skills

- **ghost:report** — Combined security report. Aggregates findings from all scan skills into a single prioritized report focused on the highest risk, highest confidence issues.
- **ghost:repo-context** — Repository context builder. Generates a shared `repo.md` profile with business criticality, sensitive data types, frameworks, and a component map used by all scan skills.
- **ghost:scan-deps** — Software Composition Analysis (SCA). Scans dependency lockfiles for known vulnerabilities using [wraith](https://github.com/ghostsecurity/wraith), then runs AI exploitability analysis to filter false positives.
- **ghost:scan-secrets** — Secrets and credentials scanner. Detects leaked API keys, tokens, and passwords using [poltergeist](https://github.com/ghostsecurity/poltergeist), then runs AI context assessment to filter false positives.
- **ghost:scan-code** — Static Application Security Testing (SAST). AI-powered code-level vulnerability detection using repository context for targeted analysis.
- **ghost:validate** — Dynamic validation (DAST). Validates scan findings against a live application using [reaper](https://github.com/ghostsecurity/reaper) as an intercepting proxy.
