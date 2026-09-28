# Secret scanning

The `ghost-scan-secrets` skill combines Poltergeist's pattern matching with AI context assessment to find real secrets and filter out noise.

<div align="center">
<img src="https://media.ghostsecurity.ai/skills/scan-secrets.gif" alt="Running the ghost-scan-secrets skill" width="800">
</div>

## Two-phase approach

### Phase 1: Pattern matching with Poltergeist

Poltergeist scans every file in your codebase against 163 built-in rules covering API keys, tokens, certificates, and credentials across 108 providers. It uses a dual-engine architecture (Hyperscan for speed, Go regex for precision) and entropy analysis to filter out low-randomness matches.

The output is a set of candidates: matches that syntactically look like secrets, with entropy scores and rule metadata.

### Phase 2: AI context assessment

For each candidate, the skill spawns an AI analyzer that examines the surrounding code:

- Is this a real secret or a placeholder? Test values like `sk-test-xxxx` or `your-api-key-here` are filtered out.
- Is it hardcoded or loaded from an environment variable? A file that reads `os.Getenv("API_KEY")` is handled differently than one with a literal key in the source.
- Is this production code or a test fixture? Secrets in test files, example configs, and documentation may be intentional.
- Is there evidence of exposure? A key that also appears in git history or logs carries higher risk.

The result is a set of confirmed findings with severity assessments and remediation guidance.

## What Poltergeist detects

Poltergeist's 163 built-in rules cover:

| Category | Examples |
|---|---|
| Cloud providers | AWS access keys, Azure storage keys, Google Cloud API keys |
| AI services | OpenAI, Anthropic, Cohere, Mistral, Hugging Face, Stability AI |
| Git platforms | GitHub PATs, GitLab tokens, Bitbucket app passwords |
| CI/CD | Docker Hub PATs, Pulumi tokens, Fly.io keys |
| Communication | Slack tokens, Telegram bot tokens, Twilio |
| Databases | PostgreSQL and MySQL connection strings with credentials |
| Payment | Stripe API keys, Plaid API keys |
| Certificates | Private keys (RSA, SSH), multi-line key detection |
| Generic | Tokens, secrets, passwords, and JWTs in variable declarations |

Each rule includes an entropy threshold tuned to its specific pattern, reducing false positives from low-randomness matches. For example, a generic password rule requires lower entropy (3.5 bits) than an AWS session token (5.5 bits), because password patterns are inherently less random.

## Example

```shell
claude "scan this project for leaked secrets"
```

Ghost Security AppSec Skills will:

1. Run Poltergeist against your codebase
2. Parse the candidates from the Poltergeist output
3. Spawn parallel analyzers for each candidate
4. Write confirmed findings to `~/.ghost/repos/<repo_id>/scans/<sha>/secrets/findings/`
5. Generate a summary report

A typical finding looks like:

```text
Finding: Hardcoded OpenAI API key in production config
Severity: HIGH
File: src/config/api.ts:15
Match: sk-proj-0JdlO*****vSYA (redacted)
Assessment: Real API key hardcoded in production configuration file.
  Environment variable loading exists in .env.example but this file
  contains the actual key value. Key has high entropy (5.2 bits)
  matching OpenAI's format.
Remediation: Move the key to an environment variable and add the
  file to .gitignore. Rotate the exposed key immediately.
```

## Automatic redaction

Poltergeist automatically redacts secrets in its output, showing only a prefix and suffix of each match (e.g., `sk-proj-0JdlO*****vSYA`). Scan results are safe to share, commit, or include in reports without exposing actual secret values.

The `-dnr` (do not redact) flag is available for cases where you need to see the full match, but it's off by default.

For full tool documentation including CLI reference, rule format, and engine architecture, see [Poltergeist](../tools/poltergeist.md).

---

Previous: [The scan lifecycle](../concepts/scan-lifecycle.md) | Next: [Dependency scanning](dependency-scanning.md) | [Docs home](../../README.md#documentation)
