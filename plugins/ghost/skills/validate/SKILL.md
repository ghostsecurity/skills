---
name: "ghost-validate"
description: This skill should be used when the user asks to "validate a finding", "check if a vulnerability is real", "triage a security finding", "confirm a vulnerability", "determine if a finding is a true positive or false positive", or provides a security finding for review. It validates security vulnerability findings by tracing data flows, verifying exploit conditions, analyzing security controls, and optionally testing attack vectors against a live application.
license: apache-2.0
metadata:
  version: 1.1.0
---

# Security Finding Validation

Determine whether a security finding is a true positive or false positive. Produce a determination with supporting evidence.

## Input

The user provides a finding as a file path or pasted text. If neither is provided, ask for one.

Extract: vulnerability class, specific claim, affected endpoint, code location, and any existing validation evidence.

## Validation Workflow

### Step 1: Understand the Finding

Identify:
- The vulnerability class (BFLA, BOLA, XSS, SQLi, SSRF, etc.)
- The specific claim being made (what authorization check is missing, what input is unsanitized, etc.)
- The affected endpoint and HTTP method
- The code location

### Step 2: Analyze the Source Code

1. Read the vulnerable file at the specified line number and all supporting files
2. Trace the request flow from route registration through middleware to the handler
3. Verify the specific claim — does the code actually lack the described check?
4. Look for indirect protections (middleware, helpers, ORM constraints) the scanner may have missed
5. Confirm the vulnerable code path is reachable under the described conditions

### Step 3: Live Validation (When Available)

If a live instance of the application is accessible and the vulnerability can be confirmed through live interaction, use the `proxy` skill to confirm exploitability:

1. Start reaper proxy scoped to the target domain
2. Authenticate (or have the user authenticate) as a legitimate user and capture a valid request to the vulnerable endpoint
3. Replay or modify the request to attempt the exploit described in the finding
4. Compare the response to expected behavior:
   - Does the unauthorized action succeed? (true positive)
   - Does the server reject it with 401/403/404? (false positive)
5. Capture the request/response pair as evidence using `reaper get <id>`

### Step 4: Make Determination

Classify the finding as one of:

- **True Positive**: The vulnerability exists and is exploitable. The code lacks the described protection and the endpoint is reachable.
- **True Positive (Confirmed)**: Same as above, plus live testing demonstrated successful exploitation.
- **False Positive**: The vulnerability does not exist. Provide the specific reason (indirect protection found, code path unreachable, etc.).
- **Inconclusive**: Cannot determine without additional information. Specify what is needed.

### Step 5: Report

Output a summary in the following format:

1. **Determination**: True Positive, False Positive, or Inconclusive
2. **Confidence**: High, Medium, or Low
3. **Evidence Summary**: Key findings from code review and/or live testing
4. **Code Analysis**: Specific lines and logic that support the determination
5. **Live Test Results** (if performed): Request/response pairs demonstrating the behavior
6. **Recommendation**: Fix if true positive, close if false positive, gather more info if inconclusive

Example:

```
## Validation Result
- **Determination**: True Positive
- **Confidence**: High
- **Evidence**: Handler at routes/transfers.go:142 queries transfers by ID without checking ownership. No middleware or ORM-level constraint enforces user scoping.
- **Recommendation**: Add ownership check — include user_id in the WHERE clause.
```

### Step 6: Persist Results

If the finding was provided as a file path, ask the user if they would like to append the validation details to the original finding file. If they agree, append a `## Validation` section to the file containing the determination, confidence, evidence summary, and recommendation.

## Vulnerability Class Reference

See `VULNERABILITY_PATTERNS.md` in this skill directory for patterns to look for when validating authorization flaws (BFLA/BOLA/IDOR), injection (SQLi/XSS), and authentication flaws.
