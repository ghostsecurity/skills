# Ghost Security AppSec Skills

AI-native application security scanning, validation, and remediation skills for Claude Code.

## Installation

```
/plugin marketplace add ghostsecurity/skills
/plugin install ghost@ghost-security
```

## Skills

| Skill | Description |
|-------|-------------|
| `ghost-repo-context` | Build shared repository context (business criticality, sensitive data, component map) |
| `ghost-scan-deps` | Exploitability analysis of dependency vulnerabilities (SCA) |
| `ghost-scan-secrets` | Context assessment of detected secrets and credentials |
| `ghost-scan-code` | AI-powered detection of code security issues (SAST) |
| `ghost-report` | Combined security report across all scan results |
| `ghost-validate` | Dynamic validation of findings against a live application (DAST) |
| `ghost-proxy` | HTTP proxy for the `ghost-validate` skill |

## Documentation

See the [repository README](../../README.md) and [Installation and usage](../../docs/installation.md).

## Feedback, Feature Requests, and Issues

- **Skills**: [This repository](https://github.com/ghostsecurity/skills/issues)
- **Reaper**: [ghostsecurity/reaper](https://github.com/ghostsecurity/reaper/issues)
- **Wraith**: [ghostsecurity/wraith](https://github.com/ghostsecurity/wraith/issues)
- **Poltergeist**: [ghostsecurity/poltergeist](https://github.com/ghostsecurity/poltergeist/issues)
