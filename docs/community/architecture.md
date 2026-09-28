# Architecture

The architecture of Ghost Security AppSec Skills separates deterministic tools from AI judgment. This page covers the technical design and how everything fits together.

## Design principles

**Tools are standalone.** Each tool is a Go binary that does one job. No tool depends on another Ghost tool or on the skills layer. Wraith runs the `osv-scanner` binary that ships with it, and it queries the OSV API unless `--offline` is set. You can use Poltergeist, Wraith, or Reaper independently without installing Ghost Security AppSec Skills.

**Skills are composable.** Each skill can run independently or as part of a pipeline. Skills read artifacts from previous skills when available (e.g., `ghost-scan-code` reads the repo context from `repo-context`) but degrade gracefully when they're missing.

**Results stay local.** Poltergeist's rules are embedded in the binary. Wraith queries the OSV API by default and uses a local copy of the OSV database only with `--offline`. The `ghost-scan-deps` skill runs Wraith without `--offline`. Skills cache results to the local filesystem.

**Output is auditable.** Every finding traces back to specific tool output and specific criteria. You can always inspect the raw Poltergeist matches, the raw Wraith CVE data, or the specific criteria that triggered an Exorcist finding.

## Tool architecture

All three Go tools follow similar patterns:

### CLI structure

- **Poltergeist** -- single command with flags (`poltergeist [flags] <path>`)
- **Wraith** -- subcommands (`wraith scan`, `wraith download-db`, `wraith version`)
- **Reaper** -- subcommands (`reaper start`, `reaper search`, `reaper get`, `reaper stop`)

### Output formats

Poltergeist and Wraith support three output formats:

| Format | Use case |
|---|---|
| Text | Interactive terminal use |
| JSON | Programmatic consumption, skill integration |
| Markdown | Reports, documentation, issue tracking |

Reaper prints tables and raw HTTP.

JSON is the primary integration format. The scan skills parse JSON output from Poltergeist and Wraith.

### Binary distribution

Tools are distributed as precompiled binaries via GitHub Releases and installed to `~/.ghost/bin/`. The skills layer handles automatic binary download and verification during initialization.

## Skill architecture

### Skill definition format

Each skill is a `SKILL.md` file that defines:

- **Tool restrictions** -- which Claude Code tools the skill can use (Read, Write, Glob, Grep, Bash, Task)
- **Execution pipeline** -- numbered steps the skill follows
- **Input/output contracts** -- what the skill reads and what it produces
- **Sub-agent definitions** -- for multi-agent skills, references to agent prompt files

### Multi-agent patterns

Skills use three architectural patterns:

**Orchestrator + sub-agents** (ghost-scan-deps, ghost-scan-secrets) -- a read-only orchestrator spawns sub-agents via the Task tool. Each sub-agent reads its instructions from a prompt file in the skill directory. The orchestrator coordinates but doesn't do the work directly.

```text
Orchestrator (SKILL.md)
├── Task -> Init agent (agents/init/agent.md)
├── Task -> Discover agent (agents/discover/agent.md)    # ghost-scan-deps only
├── Task -> Scan agent (agents/scan/agent.md)
├── Task -> Analyze agent (agents/analyze/agent.md)
└── Task -> Summarize agent (agents/summarize/agent.md)
```

`ghost-scan-secrets` has no discover agent. Its agents are init, scan, analyze, and summarize.

**Loop-based funnel** (ghost-scan-code) -- the skill runs each stage through `scripts/loop.sh`. The script starts a separate `claude -p` worker for each work item. The planner runs as one worker. The nominator, analyzer, and verifier stages run up to 5 workers in parallel. Progress is tracked in checkpoint files (plan.md, nominations.md, analyses.md) so work can resume after timeouts.

**Interactive workflow** (validate) -- a single agent with step-by-step execution and optional user interaction. Reads findings, traces code, and optionally uses Reaper for live testing.

## Data Structure

### Cache and Results

```text
~/.ghost/
├── bin/                              # Tool binaries
│   ├── poltergeist
│   ├── wraith
│   ├── osv-scanner                   # Installed with Wraith
│   └── reaper
└── repos/
    └── <repo_id>/                    # Per-repository
        ├── cache/
        │   └── repo.md               # Repository context (shared)
        └── scans/
            └── <commit_sha>/         # Per-commit
                ├── deps/
                │   ├── lockfiles.json
                │   ├── candidates.json
                │   ├── findings/
                │   └── report.md
                ├── secrets/
                │   ├── candidates.json
                │   ├── findings/
                │   └── report.md
                ├── code/
                │   ├── plan.md
                │   ├── nominations.md
                │   ├── analyses.md
                │   └── findings/
                └── report.md         # Combined report
```

**repo_id** is computed from the repository name and remote URL hash, ensuring unique caching per repository.

**commit_sha** (short) provides per-commit isolation. A new commit gets a new scan directory. On the same commit, `ghost-report` returns the existing report and `ghost-scan-code` resumes from its checkpoint files. `ghost-scan-deps` and `ghost-scan-secrets` run again. `repo.md` is cached per repository, so `ghost-repo-context` reuses it across commits.

### Data flow between skills

The `repo-context` output is shared context that informs all scans. It's required for `ghost-scan-code` (to plan which vulnerability vectors to check) and opportunistically loaded when present by the other skills to enrich context (but isn't required for basic operation).

## Reaper internals

Reaper has a distinct architecture due to its daemon-based design:

### Components

```text
CLI ──── Unix socket ──── Daemon
                            ├── HTTP proxy server
                            ├── TLS interception (in-memory CA)
                            ├── Scope filter
                            └── SQLite storage
```

### IPC protocol

The CLI and daemon communicate via JSON messages over a Unix domain socket at `~/.ghost/reaper/reaper.sock`:

- **Request**: `{"command": "search", "params": {"method": "POST", "limit": 50}}`
- **Response**: `{"ok": true, "data": [...]}`

Commands: `logs`, `search`, `get`, `req`, `res`, `tail`, `clear`, `shutdown`, `ping`

### TLS interception

1. Client sends CONNECT request to proxy
2. Proxy hijacks the TCP connection and responds with 200
3. If in-scope: proxy starts TLS with a generated per-host cert
4. If out-of-scope: proxy blindly relays bytes between client and server (transparent pass-through)
5. Per-host certificates are cached in a `sync.Map` for performance

## Design rationale

**Go for tools.** Single-binary distribution, fast startup, cross-platform compilation. Poltergeist and Reaper have no runtime dependencies. Wraith ships with the `osv-scanner` binary it runs.

**Markdown for skills.** Skills are prompts. Markdown is human-readable, version-controllable, and doesn't require a build step.

**Tool/skill split.** Deterministic tools provide a reliable foundation. Pattern matches, CVE lookups, and traffic captures produce the same output for the same input. Wraith results change only as the OSV database gains new advisories. The AI layer adds judgment and context, but the underlying data is always verifiable.

---

Previous: [Contributing](contributing.md) | Next: [Ghost Security Exo](../exo.md) | [Docs home](../../README.md#documentation)
