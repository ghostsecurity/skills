# Wraith

Wraith is the dependency scanner in Ghost Security AppSec Skills. It scans lockfiles for known vulnerabilities using the OSV database, supporting every major package ecosystem with offline mode and license scanning.

## Architecture

Wraith wraps [osv-scanner](https://github.com/google/osv-scanner), Google's open-source vulnerability scanner, with a streamlined CLI and Go library interface. When you scan a lockfile:

1. Wraith parses the lockfile to extract all packages and versions
2. Each package is queried against the OSV database for known vulnerabilities
3. OSV returns CVE identifiers, CVSS severity scores, affected version ranges, and fixed versions. The Go library returns all of them. The CLI output keeps the advisory ID, summary, details, CVSS vector, CVEs, and reference URLs
4. Output is formatted for the requested format (text, JSON, or Markdown)

The OSV database aggregates vulnerabilities from multiple sources: the National Vulnerability Database, GitHub Security Advisories, and ecosystem-specific databases.

## Key features

- **Multi-ecosystem support** -- Go, npm, PyPI, Ruby, Rust, Java, PHP, .NET, Dart, and more
- **Offline mode** -- download the vulnerability database once, scan without network access
- **License scanning** -- detect dependency licenses and check against an allowlist
- **Multiple output formats** -- colored text, JSON, and Markdown
- **Go library** -- use Wraith programmatically in your own tools

## CLI reference

### Commands

#### wraith scan

Scan a lockfile for known vulnerabilities.

```shell
wraith scan [flags] <lockfile>
```

| Flag | Default | Description |
|---|---|---|
| `--format` | `text` | Output format: `text`, `json`, `md`/`markdown` |
| `--output` | -- | Write output to file (auto-detects markdown from `.md` extension) |
| `--no-color` | `false` | Disable colored output |
| `--offline` | `false` | Scan using only local vulnerability database |
| `--download-db` | `false` | Download/refresh local database before scanning |
| `--config` | -- | Path to custom osv-scanner config file |
| `--licenses` | `false` | Enable license scanning |
| `--license-allowlist` | -- | Comma-separated list of allowed licenses |

#### wraith download-db

Download or refresh the local vulnerability database for offline scanning.

```shell
wraith download-db
```

#### wraith version

Show version information.

```shell
wraith version
```

### Examples

```shell
# Scan a Go module
wraith scan go.mod

# Scan with JSON output for CI/CD
wraith scan --format json package-lock.json

# Generate a Markdown report
wraith scan --output report.md Gemfile.lock

# Offline scanning (download database first)
wraith download-db
wraith scan --offline go.mod

# Scan with license checking
wraith scan --licenses go.mod

# Check licenses against an allowlist
wraith scan --license-allowlist MIT,Apache-2.0,BSD-3-Clause go.mod
```

### Output formats

**Text** (default) -- colored terminal output with package grouping. This sample shows 3 of 12 entries:

```text
──────────────────────────────────────────────────
 SCAN SUMMARY
──────────────────────────────────────────────────

Packages scanned: 1
Vulnerabilities:  12
Affected packages: 1

● jinja2 2.10.0 (PyPI)
  └─ PYSEC-2019-217
     CVEs: CVE-2019-10906
  └─ GHSA-462w-v97r-4m45
     Jinja2 sandbox escape via string formatting
     CVEs: CVE-2019-10906
  └─ GHSA-h5c8-rqwp-cp95
     Jinja vulnerable to HTML attribute injection when passing user input as keys ...
     CVEs: CVE-2024-22195

! Review and address the issues above.
```

**JSON** -- structured output with full vulnerability details:

```json
{
  "package_count": 1,
  "vulnerability_count": 1,
  "results": [
    {
      "Package": "jinja2",
      "Version": "2.10.0",
      "Ecosystem": "PyPI",
      "FoundVulnerabilities": [
        {
          "ID": "GHSA-h5c8-rqwp-cp95",
          "Summary": "Jinja vulnerable to HTML attribute injection when passing user input as keys to xmlattr filter",
          "Details": "The `xmlattr` filter in affected versions of Jinja accepts keys containing spaces. XML/HTML attributes cannot contain...",
          "Severity": "CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N",
          "CVEs": [
            "CVE-2024-22195"
          ],
          "References": [
            "https://github.com/pallets/jinja/security/advisories/GHSA-h5c8-rqwp-cp95",
            "https://nvd.nist.gov/vuln/detail/CVE-2024-22195"
          ]
        }
      ]
    }
  ]
}
```

This sample is trimmed to one vulnerability with a shortened `Details` field. `results` lists only the packages that have vulnerabilities. `Severity` is a single CVSS vector string, empty when the advisory has none. `Summary` can be empty. License scanning adds `license_summary`. An allowlist adds `license_violation_count` and `license_violations` when a package violates it.

**Markdown** -- report format with summary table, vulnerability details, and references.

### Exit codes

- `0` -- no vulnerabilities or license violations found
- `1` -- vulnerabilities or license violations found, or the scan failed

## Supported lockfiles

| Ecosystem | Lockfiles |
|---|---|
| Go | `go.mod` |
| Node.js (npm) | `package-lock.json` |
| Node.js (Yarn) | `yarn.lock` |
| Node.js (pnpm) | `pnpm-lock.yaml` |
| Python (pip) | `requirements.txt` |
| Python (Poetry) | `poetry.lock` |
| Python (Pipenv) | `Pipfile.lock` |
| Python (uv) | `uv.lock` |
| Ruby | `Gemfile.lock` |
| Rust | `Cargo.lock` |
| Java (Maven) | `pom.xml` |
| Java (Gradle) | `gradle.lockfile` |
| PHP | `composer.lock` |
| Dart | `pubspec.lock` |

Wraith detects the ecosystem from the lockfile name. Each lockfile must keep its standard filename.

## Offline mode

For air-gapped environments or deterministic CI pipelines:

```shell
# Download the database (requires network)
wraith download-db

# Scan without network access
wraith scan --offline go.mod
```

The local database is stored in the system's standard cache location. Refresh it at any time with `wraith download-db`.

To download and scan in a single command:

```shell
wraith scan --offline --download-db go.mod
```

## License scanning

Wraith can scan dependency licenses alongside vulnerabilities:

```shell
# Show license summary
wraith scan --licenses go.mod

# Check against an allowlist
wraith scan --license-allowlist MIT,Apache-2.0 go.mod
```

When using an allowlist, any package with a license not on the list is flagged as a violation. License violations trigger the same exit code `1` as vulnerabilities, making it easy to use in CI/CD gates.

## Skill integration

When used through the `ghost-scan-deps` skill, Wraith's vulnerability data feeds into AI exploitability analysis. The skill assesses each CVE against your actual codebase: Is the vulnerable function called? Can user input reach it? Is this a production dependency? See [Dependency scanning](../capabilities/dependency-scanning.md) for details.

---

Previous: [Poltergeist](poltergeist.md) | Next: [Reaper](reaper.md) | [Docs home](../../README.md#documentation)
