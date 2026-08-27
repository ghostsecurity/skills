# Changelog

## 1.2.0 - 2026-08-26

Adds the `ghost-exo` skill for the exo workflow lifecycle.

### Skills

- **ghost-exo** - One front door for building, improving, and debugging workflows on [exo](https://ghostsecurity.ai), an agent orchestration platform. Routes a request to one of three intents. BUILD takes a rough idea through interrogation, assessment, and resource creation in dependency order. IMPROVE runs the observe-and-iterate loop over recent runs behind two approval gates. DEBUG diagnoses a single failed run by walking the dependency graph of everything it touched. Bundles `scripts/exo-skill.py`, which moves skill bundles over REST so file contents never serialize as tool-call arguments. Harness-neutral: the bundle names no harness, and on first use it registers the exo MCP server for whichever harness is running it.

## 1.1.0 - 2026-02-17

Plugin naming convention and compliance/passing scores according to tessl best practices. Instead of **plugin:skill-name** it's **plugin-skill-name**. When installed as a plugin in Claude Code, it will be invocable by **ghost-skill-name** as well as **plugin:skill-name**

## 1.0.0 — 2026-02-13

Initial release of the Ghost Security skills plugin for Claude Code.

### Skills

- **ghost:report** — Self-contained combined security report. Aggregates findings from all scan skills into a single prioritized report with all finding content inlined (code snippets, assessment tables, remediation commands). Medium findings get full subsections. Includes scan coverage with per-scan methodology notes.
- **ghost:repo-context** — Repository context builder. Generates a shared `repo.md` profile with business criticality, sensitive data types, frameworks, and a component map used by all scan skills.
- **ghost:scan-deps** — Software Composition Analysis (SCA). Scans dependency lockfiles for known vulnerabilities using [wraith](https://github.com/ghostsecurity/wraith), then runs AI exploitability analysis to filter false positives.
- **ghost:scan-secrets** — Secrets and credentials scanner. Detects leaked API keys, tokens, and passwords using [poltergeist](https://github.com/ghostsecurity/poltergeist), then runs AI context assessment to filter false positives.
- **ghost:scan-code** — Static Application Security Testing (SAST). AI-powered code-level vulnerability detection using repository context for targeted analysis.
- **ghost:validate** — Dynamic validation (DAST). Validates scan findings against a live application using [reaper](https://github.com/ghostsecurity/reaper) as an intercepting proxy.
