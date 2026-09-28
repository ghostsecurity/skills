# Code analysis

The `ghost-scan-code` skill (Exorcist) performs AI-native static analysis. It traces data flows, checks for mitigations, and only reports findings when all criteria for a genuine vulnerability are met.

<div align="center">
<img src="https://media.ghostsecurity.ai/skills/scan-code.gif" alt="Running the ghost-scan-code skill" width="800">
</div>

## Pattern matching is not enough

Pattern-matching SAST catches known vulnerability patterns (like `query("SELECT * FROM users WHERE id = " + userId)`) but misses everything that doesn't match a signature. Business logic flaws, authorization bypasses, and novel attack vectors are invisible to it.

Traditional SAST tools also over-report. Every SQL query with string concatenation gets flagged, even when parameterized queries are used elsewhere in the same handler, or when input validation middleware runs upstream.

## Four-phase analysis

The skill starts from the repository context. If the context is missing, the skill runs `ghost-repo-context` first.

### Phase 1: Plan attack vectors

Based on the repository context (project type, frameworks, sensitive data types, business criticality), the planner selects which vulnerability vectors to check. This is informed by structured criteria files that define vulnerability types for backend, frontend, mobile, and library projects. Projects of type `iac` and `cli` get zero scans.

The depth setting controls how many vectors to check and how many candidate files to nominate for each vector:

| Depth | Vectors per project | Candidate files per vector | Best for |
|---|---|---|---|
| `quick` (default) | Top 3 | 3 | Fast feedback during development |
| `balanced` | Top 5 | 5 | Regular security reviews |
| `full` | Top 10 | 10 | Comprehensive audits |

A `full` scan uses significantly more tokens. The skill warns you and asks you to confirm before it starts. If you decline, the skill runs a `balanced` scan.

### Phase 2: Nominate candidate files

For each selected vector, a fast triage pass identifies candidate files using pattern matching (using `Grep`/`Glob` tools). The goal is to find files that *might* contain vulnerabilities, not to analyze them.

The nominator looks for signals like SQL query builders, authentication middleware, file upload handlers, or cryptographic function calls.

### Phase 3: Deep analysis

Each nominated file gets thorough analysis that traces data flows from user input to dangerous sinks:

- **Input tracing** -- where does user-controlled data enter this code path?
- **Sink identification** -- where could that data cause harm (database queries, file operations, response rendering)?
- **Mitigation checking** -- are there parameterized queries, input validation, escaping functions, or middleware that neutralize the threat?
- **Related files** -- the analyzer follows imports into 2 to 3 related files. It reads no more than 5 files in total.
- **Criteria validation** -- every finding must satisfy all criteria defined for its vulnerability type. These criteria are specific and auditable (e.g., "User-controlled input reaches SQL query without parameterization" AND "Query uses string concatenation" AND "Input not validated or sanitized" AND "Vulnerable code reachable remotely").

A finding is only reported when **all** criteria are met. Missing even one criterion (like "input validation exists") means the vulnerable condition therefore does NOT exist.

The analyzer writes remediation guidance and a corrected code snippet into each finding.

### Phase 4: Independent verification

Each finding goes through a second, independent analysis pass. The verifier re-reads the source code, confirms each criterion with specific code evidence, and checks for mitigations the analyzer might have missed.

Findings are classified as **verified** or **rejected**, with detailed reasoning. Rejection categories include: theoretical (possible but not practically exploitable), mitigated (protection exists), false positive (criteria not actually met), unreachable (code path can't be triggered), or best-practice-only (not a real vulnerability).

## Scoping overrides

Arguments after `/ghost-scan-code` can customize the scan. The skill passes them to the planning and nomination phases.

- The planner accepts a specific set of vectors, a custom vector count, or areas to focus on. These override the depth defaults.
- The nominator accepts specific candidate files, a custom candidate file count, or areas to focus on.
- Deep analysis and verification take no overrides.

## Library scanning

`ghost-repo-context` classifies a project as `library` when it is a reusable package, SDK, or module with no application entry point. The library criteria cover JS/TS, Python, and Go libraries.

A library has no network entry point. The consumer passes attacker-controlled data to public library functions. A library finding is reachable when a public API function accepts that data and the data flows to a sink.

The phases adapt to this trust model:

- The planner ranks prototype pollution highest for JS/TS libraries. It ranks unsafe deserialization and unsafe YAML loading highest for Python libraries.
- The planner skips prototype pollution for Python and Go libraries. It skips ReDoS for Go. Go's `regexp` package uses RE2 and runs in linear time.
- The nominator finds the public API surface first, such as `index.ts` or `__init__.py`. Files exported from the entry point get higher priority.
- The analyzer and the verifier accept only mitigations in the library's own code, such as key filtering, safe defaults, or path normalization.

## Vulnerability coverage

Exorcist covers 102 vulnerability types organized by platform:

| Platform | Categories | Vectors | Examples |
|---|---|---|---|
| Backend | 10 | 47 | SQL injection, BOLA, SSRF, race conditions, insecure deserialization |
| Frontend | 10 | 15 | DOM XSS, prototype pollution, open redirects, missing SRI |
| Mobile | 7 | 26 | Missing certificate pinning, insecure data storage, WebView vulnerabilities |
| Library | 8 | 14 | Prototype pollution, unsafe YAML loading, zip slip, ReDoS |

All criteria are defined in YAML files and are fully inspectable in the [skills repository](../../plugins/ghost/skills/scan-code/criteria/). See [Exorcist](../tools/exorcist.md#vulnerability-coverage) for every vector by platform.

## Example

```shell
claude "run a code security analysis on this project"
```

For a deeper analysis:

```shell
claude "/ghost-scan-code depth=full"
```

A typical finding looks like:

````markdown
# Finding: SQL Injection in Account Handler

## Metadata
- **ID**: root--injection--sql-injection--account-handler--get-account
- **Project**: . (backend)
- **Project Type**: backend
- **Agent**: injection
- **Vector**: sql-injection
- **CWE**: CWE-89
- **Severity**: high
- **Status**: verified

## Location
- **File**: src/handlers/account.go
- **Line**: 87
- **Function**: GetAccount

## Description
The GetAccount handler constructs a SQL query using string
concatenation with user-supplied input from the URL parameter.

## Vulnerable Code
```go
rows, err := db.Query("SELECT * FROM accounts WHERE id = " + accountId)
```

## Remediation
Use parameterized queries to prevent SQL injection.

## Fixed Code
```go
rows, err := db.Query("SELECT * FROM accounts WHERE id = ?", accountId)
```

## Validation Evidence
| # | Criterion | Evidence |
|---|-----------|----------|
| 1 | User input reaches query | accountId from URL param (line 82) |
| 2 | String concatenation used | Direct concat on line 87 |
| 3 | No input validation | No sanitization between param and query |
| 4 | Remotely reachable | GET /api/accounts/:id route (router.go:45) |

## Verification
- **Verdict**: verified
- **Reason**: All criteria confirmed with code evidence
- **Severity Reason**: Remotely reachable input controls a query on the accounts table, which gives full database access.
- **Verified By**: verifier
- **Criteria Confirmed**: 4/4
````

For full documentation of the analysis engine, criteria format, and finding format, see [Exorcist](../tools/exorcist.md).

---

Previous: [Dependency scanning](dependency-scanning.md) | Next: [Live validation](live-validation.md) | [Docs home](../../README.md#documentation)
