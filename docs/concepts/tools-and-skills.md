# Tools and skills

Ghost Security AppSec Skills have a two-layer architecture: **tools** produce ground truth, **skills** add AI judgment. Understanding this separation is key to understanding how Ghost Security AppSec Skills work.

## Tools

Tools are standalone Go binaries. Each one does a single job, runs fast, and produces structured output. They don't require AI or an API key to function. Wraith queries the OSV database over the network unless you run it with `--offline`.

| Tool | Job | Output |
|---|---|---|
| [Poltergeist](../tools/poltergeist.md) | Scan files for leaked secrets | Pattern matches with entropy scores |
| [Wraith](../tools/wraith.md) | Scan lockfiles for known CVEs | Vulnerability records from the OSV database |
| [Reaper](../tools/reaper.md) | Intercept HTTPS traffic | Full request/response pairs stored in SQLite |

Tools are deterministic. Given the same input, they produce the same output every time. Wraith results change only as the OSV database gains new advisories. This makes their results auditable, reproducible, and trustworthy as a foundation for AI analysis.

You can run each tool directly from the command line without the skills layer:

```shell
# Scan for secrets
poltergeist /path/to/code

# Scan a lockfile for vulnerabilities
wraith scan go.mod

# Start a proxy scoped to a domain
reaper start --domains example.com
```

## Skills

Skills are AI orchestration prompts that compose tools with reasoning. They're defined as Markdown files in the [skills repository](https://github.com/ghostsecurity/skills) and run in Claude Code.

A skill interprets tool output, examines surrounding context, and makes judgments that tools alone can't make.

For example, when the `ghost-scan-secrets` skill finds a match:

1. **Poltergeist** reports: "Line 42 of `config.js` matches rule `ghost.openai.1`"
2. **The skill** reads the file, examines the context, and determines: "This is a placeholder value in a test fixture. The actual key is loaded from an environment variable in production"

The tool provides the data. The skill provides the judgment. In many cases that judgement results in a drastic reduction in what would otherwise be false positive alerts.

### Available skills

| Skill | Uses tool | What it does |
|---|---|---|
| `ghost-repo-context` | -- | Builds shared context about repository structure, business criticality, and sensitive data types |
| `ghost-scan-deps` | Wraith | Discovers lockfiles, scans for CVEs, then AI-analyzes whether each vulnerability is actually exploitable |
| `ghost-scan-secrets` | Poltergeist | Scans for secrets, then AI-assesses whether each match is a real leaked credential |
| `ghost-scan-code` | -- | AI-native SAST: plans attack vectors, nominates files, performs deep analysis, verifies findings |
| `ghost-report` | -- | Aggregates findings from all scans into a single prioritized report |
| `ghost-validate` | Reaper | Validates individual findings through code tracing and optional live traffic testing |
| `ghost-proxy` | Reaper | Manages the Reaper proxy lifecycle (start, stop, search, inspect) |

## Why two layers?

AI is powerful but not infallible. Separating tools from skills gives you the best of both.

**Tools give you reliability.** A pattern match is a pattern match. A CVE lookup is a CVE lookup. These operations are fast, deterministic, and don't hallucinate.

**Skills give you intelligence.** Is this CVE reachable? Is this secret real? Is this code path exploitable? These questions require contextual reasoning that AI excels at.

When a skill reports a finding, you can always trace it back to the underlying tool output. The AI judgment is additive: it filters and enriches, but the raw data is always there.

## Exorcist: the exception

Exorcist is the AppSec Skills code analysis engine, and it's the one tool that doesn't have a standalone binary. It's implemented entirely as the `ghost-scan-code` skill, because code vulnerability analysis is inherently an AI-native task.

Traditional SAST tools pattern-match against known vulnerability signatures. Exorcist performs AI-native analysis: it plans attack vectors based on your application type, nominates candidate files, traces data flows, checks for mitigations, and verifies findings independently.

There's no binary to produce "ground truth" because the analysis itself requires understanding intent, context, and business logic. The [Exorcist](../tools/exorcist.md) page has the full details.

---

Previous: [Installation and usage](../installation.md) | Next: [The scan lifecycle](scan-lifecycle.md) | [Docs home](../../README.md#documentation)
