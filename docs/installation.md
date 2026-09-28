# Installation and usage

Ghost Security AppSec Skills ship as the `ghost` Claude Code plugin. This guide covers installation, available skills, and configuration. Ghost Security Exo ships as the separate `exo` plugin. See [Ghost Security Exo](exo.md) for its usage.

## Quick start

You need [Claude Code](https://code.claude.com).

Install the plugins:

```shell
claude plugin marketplace add ghostsecurity/skills
claude plugin install ghost@ghost-security
claude plugin install exo@ghost-security
```

Install only the plugins you need.

Then launch `claude` from within your repository and run the skills in the recommended order:

```
/ghost-repo-context   # Build a shared repository context used by all the scan skills
/ghost-scan-deps      # Exploitability analysis of dependency vulnerabilities (SCA)
/ghost-scan-secrets   # Context assessment of detected secrets and credentials
/ghost-scan-code      # AI-powered detection of code security issues (SAST)
/ghost-report         # Combined security report across all scan results
/ghost-validate       # Dynamic/live validation against a live application (DAST)
```

Run `/ghost-repo-context` first. Run the three scans next. Then generate the combined report with `/ghost-report` and validate findings with `/ghost-validate`.

The skills install the latest tool binaries automatically when they run. You should see the skill activate, scan your codebase, and report its findings.

## Available skills

Once installed, you have access to these skills in Claude Code:

| Skill | What it does |
|---|---|
| `ghost-repo-context` | Builds shared context about your repository structure and criticality |
| `ghost-scan-deps` | Scans dependencies for known vulnerabilities using Wraith |
| `ghost-scan-secrets` | Scans for leaked secrets and credentials using Poltergeist |
| `ghost-scan-code` | AI-powered code analysis for 102 vulnerability types |
| `ghost-report` | Aggregates findings into a prioritized security report |
| `ghost-validate` | Validates individual findings through code analysis and optional live testing |
| `ghost-proxy` | Manages the Reaper MITM proxy for traffic capture |

You can invoke skills directly or let Claude Code choose the right skills based on your request.

## Alternative methods

### Installation from inside Claude Code

```shell
/plugin marketplace add ghostsecurity/skills
/plugin install ghost@ghost-security
/plugin install exo@ghost-security
```

If the install summary asks for it, run `/reload-plugins` to activate the plugins.

### Usage without installing the plugin

Clone the skills repo and load the plugin directory with `--plugin-dir`:

```shell
git clone https://github.com/ghostsecurity/skills.git ~/.ghost/skills
claude --plugin-dir ~/.ghost/skills/plugins/ghost
```

For Ghost Security Exo, load `~/.ghost/skills/plugins/exo` instead:

```shell
claude --plugin-dir ~/.ghost/skills/plugins/exo
```

The skills install the tool binaries (`poltergeist`, `wraith`, `reaper`) automatically when they run. To install them manually, see the [Poltergeist](tools/poltergeist.md), [Wraith](tools/wraith.md), and [Reaper](tools/reaper.md) tool pages.

## Data storage

Ghost Security AppSec Skills store all data locally:

| Path | Contents |
|---|---|
| `~/.ghost/bin/` | Tool binaries (poltergeist, wraith, osv-scanner, reaper) |
| `~/.ghost/repos/` | Cached repository context and scan results |
| `~/.ghost/reaper/` | Reaper proxy database and runtime files |

Scan results are stored per repository and commit SHA. The repository context and the combined report are reused when they already exist. See [Caching and incremental runs](concepts/scan-lifecycle.md#caching-and-incremental-runs) for details.

## Updating

To update the Ghost Security AppSec Skills plugin to the latest version:

```shell
claude plugin update ghost@ghost-security
```

For Ghost Security Exo, run `claude plugin update exo@ghost-security`. Restart Claude Code to apply an update.

The `ghost-scan-deps`, `ghost-scan-secrets`, and `ghost-proxy` skills install the latest tool binaries when they run.

---

Previous: [Ghost Security Skills](../README.md) | Next: [Tools and skills](concepts/tools-and-skills.md) | [Docs home](../README.md#documentation)
