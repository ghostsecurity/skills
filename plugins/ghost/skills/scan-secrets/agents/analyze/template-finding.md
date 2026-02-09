# Secret Finding: <title>

## Metadata
- **ID**: <finding_id>
- **Type**: secret
- **Rule**: <rule_name>
- **Rule ID**: <rule_id>
- **Severity**: <critical|high|medium|low>
- **Status**: unverified

## Location
- **File**: <relative/path/to/file>
- **Line**: <line_number>

## Description
<2-4 sentences describing the leaked secret and its risk. Explain what type of secret this is, what service it grants access to, and the potential impact if compromised.>

## Secret Details
- **Value**: <redacted value - NEVER include the full secret>
- **Secret Type**: <e.g., API Key, Database Password, Private Key, OAuth Token>
- **Entropy**: <entropy value>

## Context
```<language>
<5-10 lines of code surrounding the secret, with the secret line highlighted>
```

## Risk Assessment
| Factor | Assessment |
|--------|------------|
| Real Secret | Yes - <brief evidence> |
| Hardcoded | Yes - <is it a literal value or from env/config?> |
| Production Code Path | Yes - <is this test code or production code?> |
| Exposure Evidence | <description of how/where the secret is exposed> |

## Remediation

<2-4 sentences with specific actions to remediate this finding:>

1. **Rotate the secret immediately** - The exposed credential should be considered compromised
2. **Remove from source code** - Move the secret to environment variables or a secrets manager
3. **Scrub git history** - If the secret was ever committed, it remains in git history
4. **Audit access logs** - Check if the secret was used by unauthorized parties

## References
- Rule documentation: <link if available>
- CWE-798: Use of Hard-coded Credentials
- CWE-259: Use of Hard-coded Password
