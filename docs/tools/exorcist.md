# Exorcist

Exorcist is the AppSec Skills code analysis engine. It reads code like a security engineer: planning attack vectors, tracing data flows, checking for mitigations, and verifying findings independently.

## How it works

Exorcist is implemented entirely as the `ghost-scan-code` skill. There's no standalone binary. Code vulnerability analysis requires understanding intent, context, and business logic, so the "tool" is the AI itself, guided by structured criteria and a multi-phase pipeline.

The pipeline has four phases: plan, nominate, analyze, and verify. [Code analysis](../capabilities/code-analysis.md#four-phase-analysis) describes each phase, the depth modes, scoping overrides, and library scanning.

## Vulnerability coverage

The criteria files group vectors by platform, then by agent. Scan plans and findings use the agent and vector keys below. [Code analysis](../capabilities/code-analysis.md#vulnerability-coverage) gives the totals by platform.

### Backend

| Category | Vulnerabilities |
|---|---|
| Injection (`injection`) | Command injection (`command-injection`), SQL injection (`sql-injection`), NoSQL injection (`nosql-injection`), XPath injection (`xpath-injection`), XML injection (`xml-injection`), template injection (`template-injection`), prompt injection (`prompt-injection`) |
| Authorization (`authz`) | Broken Object Level Authorization (`bola`), Broken Function Level Authorization (`bfla`), privilege escalation (`privesc`), mass assignment (`mass-assignment`) |
| Authentication (`authn`) | Broken authentication (`broken-authn`), weak password requirements (`weak-password`), missing MFA (`missing-mfa`), insecure session management (`insecure-session`), JWT implementation flaws (`jwt-impl`), cookie security issues (`cookie-security`), credential stuffing vulnerabilities (`credential-stuffing`), missing authentication (`missing-authn`) |
| Cryptography (`crypto`) | Weak encryption algorithms (`weak-encryption`), insecure random number generation (`insecure-random`), weak hashing (`weak-hashing`), missing encryption at rest (`missing-encryption-rest`), improper certificate validation (`improper-cert-validation`) |
| Data exposure (`data_exposure`) | Sensitive data in logs (`sensitive-logging`), sensitive error messages (`sensitive-errors`), stack traces in production (`stack-trace-prod`), exposed debug endpoints (`debug-endpoints`), information disclosure (`info-disclosure`), user enumeration (`enumeration`) |
| Request forgery (`request_forgery`) | Server-Side Request Forgery (`ssrf`) |
| API security (`api_security`) | Missing rate limiting (`missing-rate-limit`), missing input validation (`missing-input-validation`), CSRF (`csrf`), excessive data exposure (`excessive-data-exposure`) |
| Serialization (`serialization`) | Unsafe deserialization (`unsafe-deserialization`), XML External Entity injection (`xxe`), object injection (`object-injection`) |
| File handling (`file_handling`) | Path traversal (`path-traversal`), arbitrary file upload (`arbitrary-upload`), unrestricted file types (`unrestricted-file-type`), file inclusion (`file-inclusion`) |
| Business logic (`business_logic`) | Race conditions (`race-condition`), workflow bypasses (`workflow-bypass`), signup flow abuse (`signup-flow`), password reset vulnerabilities (`password-reset-vuln`), weak verification tokens (`weak-verification-token`) |

### Frontend

| Category | Vulnerabilities |
|---|---|
| XSS (`xss`) | DOM XSS (`dom-xss`), mutation XSS (`mxss`) |
| Injection (`injection`) | CSS injection (`css-injection`) |
| Authentication (`authn`) | Insecure token storage (`insecure-token-storage`), token URL exposure (`token-url-exposure`) |
| Authorization (`authz`) | Client-side authorization bypass (`client-authz-bypass`) |
| Data exposure (`data_exposure`) | Sensitive client-side code (`sensitive-client-code`), console data leakage (`console-sensitive`), sourcemap exposure (`sourcemap-exposure`) |
| Cryptography (`crypto`) | Client-side crypto implementation (`client-crypto-impl`), weak randomness (`weak-random`) |
| Third-party risks (`third_party_risks`) | Missing subresource integrity (`missing-sri`) |
| Navigation (`open_redirect`) | Client-side open redirect (`client-open-redirect`) |
| Messaging (`postmessage`) | Missing postMessage origin validation (`missing-origin-validation`) |
| Prototype pollution (`prototype_pollution`) | Prototype pollution (`prototype-manipulation`) |

### Mobile

| Category | Vulnerabilities |
|---|---|
| Data storage (`insecure_data_storage`) | Unencrypted local storage (`unencrypted-local`), sensitive logs (`sensitive-logs`), keychain misuse (`keychain-misuse`), SQLite encryption gaps (`sqlite-encryption`), backup exposure (`backup-exposure`) |
| Network security (`insecure_communication`) | Missing certificate pinning (`missing-cert-pinning`), cleartext traffic (`cleartext-traffic`), weak TLS (`weak-tls`) |
| Authentication (`authn`) | Biometric bypass (`biometric-bypass`), missing root/jailbreak detection (`missing-root-detection`), insecure sessions (`insecure-session`) |
| Cryptography (`crypto`) | Weak encryption (`weak-encryption`), insecure key storage (`insecure-key-storage`), custom crypto implementations (`custom-crypto`) |
| Code tampering (`code_tampering`) | Missing obfuscation (`missing-obfuscation`), debug mode enabled (`debug-enabled`), insecure IPC (`insecure-ipc`), exported components (`exported-component`) |
| Reverse engineering (`reverse_engineering`) | Hardcoded secrets (`hardcoded-secret`), API keys in code (`api-in-code`), logic exposure (`logic-exposure`), missing anti-tamper (`missing-anti-tamper`) |
| Platform-specific (`platform_specific`) | Insecure deep links (`insecure-deeplink`), intent manipulation (`intent-manipulation`), URL scheme hijacking (`url-scheme-hijack`), WebView vulnerabilities (`webview-vuln`) |

### Library

| Category | Vulnerabilities |
|---|---|
| Injection (`injection`) | Command injection (`command-injection`), template injection (`template-injection`) |
| Prototype pollution (`prototype_pollution`) | Prototype pollution (`proto-pollution`), property injection (`property-injection`) |
| Unsafe execution (`unsafe_execution`) | Eval injection (`eval-injection`), unsafe deserialization (`unsafe-deserialization`), unsafe YAML loading (`unsafe-yaml`) |
| Path handling (`path_handling`) | Path traversal (`path-traversal`), zip slip (`zip-slip`) |
| ReDoS (`redos`) | Catastrophic backtracking (`catastrophic-backtracking`) |
| XXE (`xxe`) | XML external entity processing (`xml-external-entity`) |
| Request forgery (`request_forgery`) | Server-Side Request Forgery (`ssrf`) |
| Cryptography (`crypto`) | Weak randomness (`weak-random`), weak hashing (`weak-hashing`) |

## Criteria format

All vulnerability criteria are defined in YAML and fully inspectable. Each file nests the agent, then the vector, then the vector's fields. Each vector specifies `candidates`, `cwe`, and `criteria`. Most also give a `severity` map. When a vector has none, the analyzer assesses severity from the demonstrated impact and states that basis in the finding:

- **`candidates`** -- what to look for when nominating files
- **`cwe`** -- Common Weakness Enumeration identifier
- **`severity`** -- what constitutes high, medium, and low severity for this specific vulnerability
- **`criteria`** -- the specific conditions that must ALL be true for a finding to be genuine

Example (SQL injection), excerpted from `criteria/backend.yaml`:

```yaml
injection:
  sql-injection:
    candidates: "Files with: raw SQL queries (db.Query, execute, ExecuteReader, query()), query builders with string concatenation (WHERE/ORDER BY), dynamic table/column names, string formatting in SQL (%s, fmt.Sprintf, f-strings)"
    cwe: "CWE-89"
    severity:
      high: "Full database access, authentication bypass, or data exfiltration"
      medium: "Limited data exposure or read-only injection"
      low: "Injection in non-sensitive tables or constrained context"
    criteria:
      - "User-controlled input reaches a SQL query without proper parameterization"
      - "Query uses string concatenation or interpolation instead of parameterized queries or prepared statements"
      - "Input is not validated or sanitized before being used in the query"
      - "Vulnerable code path is reachable remotely over network protocols (HTTP/S, API requests, gRPC, WebSocket) without requiring direct server, container, or filesystem access"
```

These criteria are atomic and auditable.

## Finding format

Each finding is a Markdown file at `findings/<finding_id>.md` in the scan directory. The analyzer writes it from `prompts/template-finding.md` with the status `unverified`. The verifier then sets the status to `verified` or `rejected` and fills in the verification fields.

The finding ID is `<base_path_slug>--<agent>--<vector>--<class>--<method>`. The base path slug replaces `/` with `-` and `.` with `root`. The class is `global` when the code has no class or module.

| Section | Contents |
|---|---|
| Metadata | ID, Project, Project Type, Agent, Vector, CWE, Severity, Status |
| Location | File, Line, Function |
| Description | 2 to 4 sentences describing the vulnerability |
| Vulnerable Code | The vulnerable snippet, 5 to 15 lines |
| Remediation | 2 to 4 sentences of fix guidance |
| Fixed Code | The corrected snippet |
| Validation Evidence | One row per criterion, with its code evidence |
| Verification | Verdict, Reason, Verified By, Criteria Confirmed. A verified finding adds Severity Reason. A rejected finding adds Rejection Category. |

[Code analysis](../capabilities/code-analysis.md#example) shows a complete finding. It also lists the [rejection categories](../capabilities/code-analysis.md#phase-4-independent-verification).

## Running Exorcist

Through Claude Code:

```shell
# Quick scan (default)
claude "/ghost-scan-code"

# Balanced scan
claude "/ghost-scan-code depth=balanced"

# Full scan (asks for confirmation first)
claude "/ghost-scan-code depth=full"
```

Results are written to `~/.ghost/repos/<repo_id>/scans/<commit_sha>/code/findings/`.

For workflow details on how code analysis fits into the full pipeline, see [Code analysis](../capabilities/code-analysis.md).

## Adding/Modifying vulnerability criteria

Exorcist's vulnerability criteria are defined in YAML files at [`plugins/ghost/skills/scan-code/criteria/`](../../plugins/ghost/skills/scan-code/criteria/):

- `backend.yaml` -- backend vulnerability vectors
- `frontend.yaml` -- frontend vulnerability vectors
- `mobile.yaml` -- mobile vulnerability vectors
- `library.yaml` -- library vulnerability vectors
- `index.yaml` -- index of valid agent-vector combinations for each project type. The planner selects only vectors listed here. Edit it by hand.

Each vector defines candidates (what to look for), a CWE mapping, and validation criteria (conditions that must all be true for a genuine finding). Most also define severity descriptions.

To add a new vulnerability type:

1. Add the vector definition to the appropriate platform YAML file
2. Update `index.yaml` with the new agent-vector mapping
3. Test by running `/ghost-scan-code` against a project with known instances of the vulnerability

---

Previous: [Reaper](reaper.md) | Next: [Contributing](../community/contributing.md) | [Docs home](../../README.md#documentation)
