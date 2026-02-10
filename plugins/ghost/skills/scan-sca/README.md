# Ghost SCA Scanner

AI-powered Software Composition Analysis (SCA) scanner that detects exploitable vulnerabilities in your dependencies. Uses [wraith](https://github.com/ghostsecurity/wraith) for vulnerability detection with AI analysis to filter false positives.

## What Makes This Different

Traditional SCA tools report every CVE found in your dependency tree, leading to alert fatigue. **Ghost SCA uses AI to analyze each vulnerability and determine if it's actually exploitable** in your codebase.

**Key Features**:
- Scans all major package ecosystems (Go, npm, PyPI, RubyGems, Cargo, Maven, Composer)
- AI-powered exploitability analysis filters false positives
- Traces user input to vulnerable code paths
- Detects mitigating controls and configuration
- Provides actionable remediation guidance

## Usage

```
/ghost:scan-sca [path-to-scan]
```

Examples:
```
/ghost:scan-sca .                    # Scan current directory
/ghost:scan-sca ./backend            # Scan specific directory
/ghost:scan-sca /path/to/repo        # Scan absolute path
```

The scanner will automatically discover all lockfiles in the repository.

## How It Works

1. **Initialize**: Downloads/verifies wraith binary (includes osv-scanner)
2. **Discover**: Finds all dependency lockfiles in your repository
3. **Scan**: Runs wraith to detect vulnerabilities from OSV database (500,000+ CVEs)
4. **Analyze**: AI agents evaluate each vulnerability for:
   - Is the vulnerable package/function actually used?
   - Can user input reach the vulnerable code?
   - Is this production code or test-only?
   - Are there mitigating controls in place?
5. **Report**: Generates detailed findings only for exploitable vulnerabilities

## Prerequisites

The skill requires the `wraith` binary. It will be installed automatically via one of two methods:

### Option 1: GitHub Releases (default)

If the [wraith repository](https://github.com/ghostsecurity/wraith) is reachable, the binary is downloaded automatically from GitHub releases.

### Option 2: Local Fallback

If GitHub is unavailable (network issues, air-gapped environment), place release artifacts in the fallback directory:

| Platform | Fallback Directory |
|----------|-------------------|
| Linux/macOS | `~/.ghost/releases/latest/` |
| Windows | `%USERPROFILE%\.ghost\releases\latest\` |

Required files (for your platform):
```
~/.ghost/releases/latest/
├── wraith_linux_amd64.tar.gz
├── wraith_linux_arm64.tar.gz
├── wraith_darwin_amd64.tar.gz
├── wraith_darwin_arm64.tar.gz
└── wraith_windows_amd64.zip
```

You only need the file for your platform. Each archive contains both `wraith` and `osv-scanner` binaries.

## Supported Platforms

- Linux (amd64, arm64)
- macOS (amd64/Intel, arm64/Apple Silicon)
- Windows (amd64) - via Git Bash, WSL, or MSYS2

## Supported Ecosystems

The scanner automatically detects and scans these lockfile formats:

**Go**:
- `go.mod`, `go.sum`

**JavaScript/TypeScript (npm)**:
- `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`

**Python**:
- `uv.lock`, `poetry.lock`, `Pipfile.lock`, `requirements.txt`

**Ruby**:
- `Gemfile.lock`

**Rust**:
- `Cargo.lock`

**Java/Kotlin**:
- `pom.xml`, `gradle.lockfile`

**PHP**:
- `composer.lock`

## Output

Results are saved to `.ghost/scans/<timestamp>/`:
```
.ghost/scans/20260209-143052/
├── lockfiles.json        # Discovered lockfiles
├── scan-1.json           # Raw wraith output (per lockfile)
├── scan-2.json
├── candidates.json       # All vulnerabilities detected
├── findings/             # Exploitable vulnerabilities only
│   └── <finding-id>.md
└── report.md             # Comprehensive summary report
```

## Example Output

```
## Scan Summary
- Lockfiles Scanned: 2
- Packages Scanned: 145
- Vulnerabilities Detected: 12 (raw)
- Confirmed Findings: 3 (exploitable)
- False Positives Filtered: 9 (75%)

### Top Findings
1. HIGH: lodash@4.17.15 - CVE-2020-8203 - Exploitable via /api/settings
2. HIGH: axios@0.19.0 - CVE-2020-28168 - SSRF in webhook handler
3. MEDIUM: minimist@1.2.5 - CVE-2021-44906 - Prototype pollution in CLI parser
```

## False Positive Filtering

The AI analyzer filters vulnerabilities that are:
- **Not actually used**: Package imported but vulnerable function not called
- **Test/dev dependencies only**: Not included in production builds
- **Effectively mitigated**: Validation wrappers, WAF rules, configuration changes
- **Version overrides**: Using patched fork despite lockfile version

## Remediation Guidance

Each exploitable finding includes:
- Specific upgrade commands for your package manager
- Testing checklist for affected functionality
- Alternative remediation if upgrade not possible
- Estimated effort (hours/days)
- Links to CVE details and advisories

Example:
```bash
# Go
go get golang.org/x/crypto@v0.1.0
go mod tidy

# npm
npm install lodash@4.17.21
npm audit

# Python (poetry)
poetry add requests@2.31.0
poetry lock
```

## Severity Levels

The scanner uses contextual severity based on exploitability:

- **HIGH**: Actively exploitable, user input reaches vulnerable code
- **MEDIUM**: Exploitable with certain conditions or limited impact
- **LOW**: Theoretical vulnerability, difficult to exploit or minimal impact

Base CVSS scores are adjusted based on actual exploitability in your codebase.

## Privacy & Security

- All analysis happens locally - no code or vulnerability data sent to external services
- Only OSV database lookups are performed by wraith (standard practice)
- No telemetry or usage tracking
- Findings stay in your `.ghost/` directory

## Offline Mode

For air-gapped environments, wraith supports offline scanning:

1. Download vulnerability database once:
   ```bash
   wraith download-db
   ```

2. Scan using local database:
   ```bash
   wraith scan --offline go.mod
   ```

The skill can be configured to use offline mode if needed.

## Integration with CI/CD

To integrate into your CI/CD pipeline:

1. Install the skill in your CI environment
2. Run scans on every PR or commit
3. Fail builds on HIGH severity findings
4. Generate reports as artifacts

Example GitHub Actions:
```yaml
- name: Run SCA Scan
  run: claude-code /ghost:scan-sca

- name: Check for HIGH findings
  run: |
    if grep -q "Severity: HIGH" .ghost/scans/*/report.md; then
      echo "HIGH severity vulnerabilities found!"
      exit 1
    fi
```

## Limitations

- Requires lockfiles to be committed (doesn't scan based on manifest files alone)
- Analysis quality depends on code readability and complexity
- May require manual review for complex data flows
- Initial scan may take several minutes on large repositories

## Troubleshooting

**No lockfiles found**:
- Ensure lockfiles are committed to version control
- Check that you're using supported package managers
- Verify you're scanning the correct directory

**Installation fails**:
- Check network access to github.com/ghostsecurity/wraith
- Try local fallback method (see Prerequisites)
- Verify platform support (Linux/macOS/Windows)

**Too many false positives**:
- The AI analysis should filter most false positives automatically
- If you see genuine false positives, they may need manual configuration
- Consider using custom osv-scanner.toml to ignore specific vulnerabilities

## Learn More

- [Wraith Documentation](https://github.com/ghostsecurity/wraith)
- [OSV Database](https://osv.dev)
- [Ghost Security](https://ghost.security)

---

*Powered by Wraith and AI Exploitability Analysis*
