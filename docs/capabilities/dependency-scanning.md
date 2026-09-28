# Dependency scanning

The `ghost-scan-deps` skill combines Wraith's CVE database lookups with AI exploitability analysis to separate the CVEs that matter from the ones that don't.

<div align="center">
<img src="https://media.ghostsecurity.ai/skills/scan-deps.gif" alt="Running the ghost-scan-deps skill" width="800">
</div>

## Four-phase workflow

### Phase 1: Discovery

The skill scans your repository for these lockfiles: `go.mod`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `uv.lock`, `poetry.lock`, `Pipfile.lock`, `requirements.txt`, `Gemfile.lock`, `Cargo.lock`, `pom.xml`, `gradle.lockfile`, and `composer.lock`. Each lockfile represents a dependency graph to analyze.

### Phase 2: Scanning with Wraith

Wraith runs against each discovered lockfile, querying the [OSV database](https://osv.dev/). The output is a list of packages with known vulnerabilities. Each vulnerability carries its advisory ID, summary, details, CVSS vector, CVE identifiers, and reference links.

### Phase 3: AI exploitability analysis

For each vulnerability found, an AI analyzer examines your actual codebase:

- Is the vulnerable function called? Many CVEs affect specific functions within a package. If your code never calls that function, the CVE isn't exploitable.
- Can user input reach the vulnerable code path? A vulnerable parsing function that only processes trusted internal data carries lower risk than one handling user uploads.
- Is this a production dependency or a dev/test dependency? Vulnerabilities in test tooling rarely affect production security.
- Are mitigations already in place? Middleware, input validation, or configuration changes might already neutralize the vulnerability.

### Phase 4: Summary

The skill generates a report with coverage statistics, confirmed exploitable findings, and filtered false positives, along with the reasoning behind each determination.

## Supported ecosystems

The skill maps these lockfiles to ecosystems. Wraith scans each one against the OSV database:

| Ecosystem | Lockfiles |
|---|---|
| Go | `go.mod` |
| JavaScript/TypeScript (npm) | `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` |
| Python | `uv.lock`, `poetry.lock`, `Pipfile.lock`, `requirements.txt` |
| Ruby | `Gemfile.lock` |
| Rust | `Cargo.lock` |
| Java/Kotlin | `pom.xml`, `gradle.lockfile` |
| PHP | `composer.lock` |

Wraith detects the ecosystem from the lockfile name. Each lockfile must keep its standard filename.

## Example

```shell
claude "scan my dependencies for known vulnerabilities"
```

Ghost Security AppSec Skills will:

1. Discover all lockfiles in your repository
2. Run Wraith against each one
3. Analyze exploitability for each CVE found
4. Write confirmed findings to `~/.ghost/repos/<repo_id>/scans/<sha>/deps/findings/`
5. Generate a summary report

A typical finding includes the CVE, the affected package, and an exploitability assessment:

```text
Finding: CVE-2024-XXXXX in lodash@4.17.20
Severity: HIGH (CVSS 9.1) → MEDIUM (contextual)
Package: lodash 4.17.20 (npm)
Fix available: Upgrade to 4.17.21

Exploitability assessment: The vulnerability affects lodash.template()
  which is called in src/email/renderer.js:42. However, the template
  string is hardcoded. User input does not reach the vulnerable
  function. Contextual severity reduced from HIGH to MEDIUM.

Remediation: Upgrade lodash to 4.17.21. While the current usage
  is not directly exploitable, the fix is a patch version bump
  with no breaking changes.
```

## Offline mode

Wraith supports fully offline scanning. Download the vulnerability database once, then scan without network access:

```shell
wraith download-db
wraith scan --offline go.mod
```

Useful for air-gapped environments or CI pipelines where you want deterministic, network-independent results.

## License scanning

Wraith can also scan dependency licenses and check them against an allowlist:

```shell
wraith scan --license-allowlist MIT,Apache-2.0 go.mod
```

Packages with licenses not on the allowlist are flagged as violations. This runs alongside vulnerability scanning in a single pass.

For full tool documentation including CLI reference and output formats, see [Wraith](../tools/wraith.md).

---

Previous: [Secret scanning](secret-scanning.md) | Next: [Code analysis](code-analysis.md) | [Docs home](../../README.md#documentation)
