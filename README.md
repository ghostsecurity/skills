# Ghost Security Skills

This repository is the Ghost Security plugin marketplace for Claude Code. It ships two plugins: Ghost Security AppSec Skills (`ghost`) and Ghost Security Exo (`exo`).

## Installation

With Claude Code:

```
claude plugin marketplace add ghostsecurity/skills
claude plugin install ghost@ghost-security
claude plugin install exo@ghost-security
claude
```
<div align="center">
<img src="https://media.ghostsecurity.ai/skills/installation.gif" alt="Installing the Ghost Security AppSec Skills plugin" width="800">
</div>

Alternatively, install the plugins within Claude Code:

```
/plugin marketplace add ghostsecurity/skills
/plugin install ghost@ghost-security
/plugin install exo@ghost-security
```

Install only the plugins you need. If the install summary asks for it, run `/reload-plugins` to activate the plugin.

See [Installation and usage](docs/installation.md) for loading the plugins without installing them, where data is stored, and updating.

## Ghost Security AppSec Skills

Ghost Security AppSec Skills are an agent-native application security plugin for [Claude Code](https://code.claude.com). They give your AI coding agent the tools and skills to find vulnerabilities, prove they're real, and fix them, all inside your existing development workflow.

| Tool | What it does |
|---|---|
| [Poltergeist](docs/tools/poltergeist.md) | Secret scanner with dual-engine pattern matching and entropy analysis. |
| [Wraith](docs/tools/wraith.md) | Dependency scanner powered by the OSV database. |
| [Reaper](docs/tools/reaper.md) | MITM HTTPS proxy for live vulnerability validation. |
| [Exorcist](docs/tools/exorcist.md) | AI-powered code analysis covering 102 vulnerability types. |

These four tools are composed by an AI skills layer that orchestrates them into a complete security pipeline, from discovery to proof to fix. Get started with the [installation and usage guide](docs/installation.md).

| Skill | Description |
|-------|-------------|
| `ghost-repo-context` | Build shared repository context (business criticality, sensitive data, component map) |
| `ghost-scan-deps` | Exploitability analysis of dependency vulnerabilities (SCA) |
| `ghost-scan-secrets` | Context assessment of detected secrets and credentials |
| `ghost-scan-code` | AI-powered detection of code security issues (SAST) |
| `ghost-report` | Combined security report across all scan results |
| `ghost-validate` | Dynamic validation of findings against a live application (DAST) |
| `ghost-proxy` | HTTP proxy for the `ghost-validate` skill |

### How Ghost Security AppSec Skills work

Ghost Security AppSec Skills are built on a simple idea: **real tools produce real data, and AI adds judgment on top.**

Poltergeist, Wraith, and Reaper are standalone binaries that each do one job well. Poltergeist scans for secrets. Wraith scans dependencies. Reaper captures live traffic. These are deterministic tools that produce structured, reliable output.

The AI layer comes in through **AI skills**, orchestration prompts that compose these tools with reasoning. A skill runs Poltergeist, reads the results, examines the surrounding code, and tells you whether each match is a real leaked credential or a benign artifact that can be ignored.

This two-layer architecture means:

- **Ground truth comes from tools.** Pattern matches, CVE lookups, and traffic captures are deterministic and auditable.
- **Judgment comes from AI.** Exploitability analysis, context assessment, and prioritization use the same reasoning a security engineer would.
- **You get findings, not alerts.** Every result includes context about why it matters and what to do about it.

Ghost Security AppSec Skills follow a three-stage loop: **find, validate, fix.** Scanners find candidates, AI analyzes each candidate for exploitability, and findings include remediation guidance your agent can apply directly. Read more about [how the scan lifecycle works](docs/concepts/scan-lifecycle.md).

### Open source and composable

Ghost Security AppSec Skills and their underlying tools are fully open source. Everything is available for inspection and contribution.

The tools can also be used standalone. You can use Poltergeist for secret scanning without touching the rest of the skills. The skills compose them into a pipeline, but the pipeline is optional. Use as much or as little as your workflow needs.

- **Poltergeist, Wraith, and Reaper** are Go binaries distributed via GitHub releases
- **Skills** are prompt files that run in Claude Code
- **Rules** and **criteria** are YAML files you can extend, customize, or replace
- **Results** stay on your machine and are cached to speed up subsequent runs. Wraith queries the OSV database over the network to look up vulnerabilities.

## Ghost Security Exo

The `ghost-exo` skill builds, improves, and debugs workflows on [exo](https://ghostsecurity.ai), an agent orchestration platform. It routes each request to one of three intents: build, improve, or debug. See [Ghost Security Exo](docs/exo.md) for connecting the exo MCP server and using each intent.

## Documentation

**Getting started**

- [Installation and usage](docs/installation.md)

**How it works**

- [Tools and skills](docs/concepts/tools-and-skills.md)
- [The scan lifecycle](docs/concepts/scan-lifecycle.md)

**Capabilities**

- [Secret scanning](docs/capabilities/secret-scanning.md)
- [Dependency scanning](docs/capabilities/dependency-scanning.md)
- [Code analysis](docs/capabilities/code-analysis.md)
- [Live validation](docs/capabilities/live-validation.md)
- [Reporting](docs/capabilities/reporting.md)

**Tools**

- [Poltergeist](docs/tools/poltergeist.md)
- [Wraith](docs/tools/wraith.md)
- [Reaper](docs/tools/reaper.md)
- [Exorcist](docs/tools/exorcist.md)

**Community**

- [Contributing](docs/community/contributing.md)
- [Architecture](docs/community/architecture.md)

**Ghost Security Exo**

- [Ghost Security Exo](docs/exo.md)

## Contributions, Feedback, Feature Requests, and Issues

[Open an Issue](https://github.com/ghostsecurity/skills/issues/new) per the [Contributing](.github/CONTRIBUTING.md) guidelines and [Code of Conduct](.github/CODE_OF_CONDUCT.md)

## License

This repository is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.
