# Ghost Security Exo

The `ghost-exo` skill builds, improves, and debugs workflows on [exo](https://ghostsecurity.ai), an agent orchestration platform.

## Installation

```
/plugin marketplace add ghostsecurity/skills
/plugin install exo@ghost-security
```

## Usage

Run the skill. It connects the exo MCP server on first use if needed:

```
/ghost-exo     # Turn an idea into a workflow, iterate on an existing one, or diagnose a failed run
```

Name an agent template slug from [ghostsecurity.ai/agents](https://ghostsecurity.ai/agents/) to start a build from that template.

## Documentation

See [Ghost Security Exo](../../docs/exo.md) for connecting the MCP server, the three intents, and how workflows run.

## Feedback, Feature Requests, and Issues

[Open an Issue](https://github.com/ghostsecurity/skills/issues/new) per the [Contributing](../../.github/CONTRIBUTING.md) guidelines.
