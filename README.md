# Ghost Security Skills/Plugin Marketplace

Plugin marketplace repository for [Ghost Security](https://ghost.security)'s AI-native application security skills for Claude Code.

## Install

Install the skills plugin using the marketplace capability within Claude Code:

```
/plugin marketplace add ghostsecurity/skills
/plugin install ghost@ghost-security
```

Or from outside Claude Code:

```
claude plugin marketplace add ghostsecurity/skills
claude plugin install ghost@ghost-security
```

## Comprehensive Documentation

Full documentation, tutorials, and video guides at [ghostsecurity.ai](https://ghostsecurity.ai).

## Skills in this Repository Marketplace

[Ghost Plugin (with skills)](plugins/ghost/README.md).

| Skill | Description |
|-------|-------------|
| `ghost:repo-context` | Build shared repository context (business criticality, sensitive data, component map) |
| `ghost:scan-deps` | Exploitability analysis of dependency vulnerabilities (SCA) |
| `ghost:scan-secrets` | Context assessment of detected secrets and credentials |
| `ghost:scan-code` | AI-powered detection of code security issues (SAST) |
| `ghost:report` | Combined security report across all scan results |
| `ghost:validate` | Dynamic validation of findings against a live application (DAST) |

## Contributions, Feedback, Feature Requests, and Issues

Contributions are welcome! Please open a pull request or issue on this repository.

- **Docs**: [ghostsecurity.ai](https://ghostsecurity.ai)
- **Skills**: [This repository](https://github.com/ghostsecurity/skills/issues)
- **Reaper**: [ghostsecurity/reaper](https://github.com/ghostsecurity/reaper/issues)
- **Wraith**: [ghostsecurity/wraith](https://github.com/ghostsecurity/wraith/issues)
- **Poltergeist**: [ghostsecurity/poltergeist](https://github.com/ghostsecurity/poltergeist/issues)

## License

This repository is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.
