# Live validation

The `ghost-validate` skill combines code tracing with Reaper's MITM proxy to confirm whether a vulnerability is genuinely exploitable.

<div align="center">
<a href="https://www.youtube.com/watch?v=8Nzcs7bX1I4"><img src="https://media.ghostsecurity.ai/skills/validate.png" alt="Running the ghost-validate skill" width="800"></a>
</div>

## Static analysis has limits

Static analysis identifies a missing authorization check, a SQL query using string concatenation, or an endpoint that doesn't validate input. But many findings are theoretical: a middleware layer blocks the attack vector, the code path is unreachable from external input, or the deployment configuration neutralizes the risk.

Validation turns "might be vulnerable" into "is vulnerable" or "is not vulnerable."

## Two-stage validation

The `ghost-validate` skill works on individual findings:

### Stage 1: Code tracing

For each finding, the validator reads the vulnerable file and traces the complete request flow:

- **Route registration** -- how does the request reach this handler?
- **Middleware chain** -- what authentication, authorization, or validation middleware runs before the handler?
- **Handler logic** -- does the code actually behave as the finding claims?
- **Supporting files** -- what do imported functions, utility modules, and configuration files reveal?

### Stage 2: Live testing (optional)

When a running application is available, Ghost Security AppSec Skills can validate findings with real traffic:

1. **Start Reaper** -- a MITM proxy scoped to the application's domain
2. **Authenticate** -- make a legitimate request to establish a valid session
3. **Capture** -- exercise the vulnerable endpoint and capture the request/response
4. **Exploit** -- modify the captured request to attempt the attack (e.g., change a user ID for BOLA, add SQL syntax for injection)
5. **Verify** -- compare the response to expected behavior

Reaper captures full request/response pairs in a local SQLite database, providing evidence of whether the exploit worked.

## Validation verdicts

Each validation produces one of four determinations:

| Verdict | Meaning |
|---|---|
| **True positive** | Vulnerability exists. Code analysis confirms the flaw, and the endpoint is reachable without adequate protection. |
| **True positive (confirmed)** | Vulnerability exists AND live testing demonstrated successful exploitation. |
| **False positive** | Vulnerability does not exist. Code analysis found protections the original scan missed, or the code path is unreachable. |
| **Inconclusive** | Cannot determine without more information. Typically the application isn't running or the test environment isn't available. |

Each verdict comes with a confidence level (high, medium, low) and detailed evidence: specific code lines, middleware configurations, and (if live-tested) captured request/response pairs.

## What validation looks like

After running a code analysis scan, validate specific findings:

```shell
claude "validate the SQL injection finding in account handler"
```

Ghost Security AppSec Skills will trace the code path, check for middleware protections, and report:

```text
Validation: SQL Injection in GetAccount
Determination: True Positive
Confidence: High

Code Analysis:
- Route registered at /api/accounts/:id (router.go:45)
- No authentication middleware on this route
- No input validation on accountId parameter
- Query uses string concatenation (account.go:87)
- No parameterized query wrapper in the codebase

Recommendation: Fix. Use parameterized query and add
  input validation middleware to this route.
```

If a running application is available and Reaper is configured:

```text
Live Test Results:
- Authenticated as test user (session captured, entry #12)
- Sent normal request to /api/accounts/123 (entry #13, 200 OK)
- Sent payload /api/accounts/123' OR '1'='1 (entry #14, 200 OK)
- Response returned all account records instead of one
- Exploit confirmed: SQL injection is exploitable

Determination upgraded: True Positive (Confirmed)
```

## When to validate

Validation is most valuable for:

- High-severity findings where the cost of a false positive or false negative is high
- Authorization flaws (BOLA, BFLA) that are difficult to detect statically but straightforward to test with modified requests
- Injection vulnerabilities where middleware or framework protections might exist but weren't detected by static analysis
- Disputed findings where the development team believes a finding is a false positive

Low-severity findings and clear-cut issues (like hardcoded secrets) are typically actionable without additional proof.

For full proxy documentation, see [Reaper](../tools/reaper.md).

---

Previous: [Code analysis](code-analysis.md) | Next: [Reporting](reporting.md) | [Docs home](../../README.md#documentation)
