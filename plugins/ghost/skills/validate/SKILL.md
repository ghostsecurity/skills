---
name: validate
description: This skill should be used when the user asks to "validate a finding", "check if a vulnerability is real", "triage a security finding", "confirm a vulnerability", "determine if a finding is a true positive or false positive", or provides a security finding for review. It guides systematic validation of security vulnerability findings through code analysis and optional live application testing.
---

# Security Finding Validation

Validate whether a security vulnerability finding is a true positive (real, exploitable vulnerability) or a false positive (incorrectly flagged, not exploitable). Produce a clear determination with supporting evidence.

## Input

A finding can be provided in any of these ways:

1. **As a file path**: The user provides a path to a markdown/JSON/text file containing the finding
2. **As pasted text**: The user pastes the finding directly in the conversation
3. **Not yet provided**: If the user invokes the skill without providing a finding, ask them to either paste the finding text or provide a file path

Key fields to extract from the finding (not all will be present):

- **ID / Title**: Identifier and summary
- **Severity / Exploit Feasibility**: Risk assessment
- **Vector / Agent**: Vulnerability class (e.g. BFLA, BOLA, IDOR, XSS, SQLi)
- **Repo / Source URL**: Where the vulnerable code lives
- **File Path / Line Number / Method Name**: Exact location
- **Endpoints**: HTTP methods and paths affected
- **Description**: What the vulnerability is
- **Exploit Walkthrough**: How an attacker would exploit it
- **Vulnerable Code / Fixed Code**: The before/after code
- **Remediation**: Suggested fix
- **Validation Evidence**: Additional analysis made by the vulnerability scanning agent

## Validation Workflow

### Step 1: Understand the Finding

Read the finding thoroughly. Identify:
- The vulnerability class (BFLA, BOLA, XSS, SQLi, SSRF, etc.)
- The specific claim being made (what authorization check is missing, what input is unsanitized, etc.)
- The affected endpoint and HTTP method
- The code location

### Step 2: Analyze the Source Code

If a repo URL or local source is available, clone or read the relevant files:

1. Read the vulnerable file at the specified line number
2. Read all supporting files listed in the finding
3. Trace the request flow from route registration through middleware to the handler
4. Verify the specific claim: does the code actually lack the check described?

Key questions to answer through code analysis:

- **Is the endpoint reachable?** Trace from route registration to confirm the handler is mounted and accessible
- **Is authentication enforced?** Check middleware chain for auth requirements
- **Is the authorization check actually missing?** Compare what the code checks vs. what it should check
- **Are there indirect protections?** Look for checks in middleware, helper functions, or ORM-level constraints that the scanner may have missed
- **Is the vulnerable code path reachable?** Follow control flow to confirm the vulnerable branch executes under the described conditions

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

Produce a summary including:

1. **Determination**: True Positive, False Positive, or Inconclusive
2. **Confidence**: High, Medium, or Low
3. **Evidence Summary**: Key findings from code review and/or live testing
4. **Code Analysis**: Specific lines and logic that support the determination
5. **Live Test Results** (if performed): Request/response pairs demonstrating the behavior
6. **Recommendation**: Fix if true positive, close if false positive, gather more info if inconclusive

## Vulnerability Class Reference

### Authorization Flaws (BFLA/BOLA/IDOR)

Look for:
- Missing ownership checks in database queries (e.g., no `UserId` in WHERE clause)
- Inconsistent authorization between similar operations (e.g., destination checked but source not checked)
- Direct object references without access control
- Horizontal privilege escalation (accessing other users' resources)
- Vertical privilege escalation (accessing admin functions)

### Injection (SQLi/XSS/Command Injection)

Look for:
- Unsanitized user input in queries, templates, or system commands
- Missing parameterized queries or prepared statements
- Reflected or stored user input without encoding

### Authentication Flaws

Look for:
- Missing authentication middleware on protected routes
- Bypassable auth checks (e.g., checking only one of multiple auth paths)
- Session management issues
