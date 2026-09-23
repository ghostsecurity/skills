# Exo Workflow Skill

The `ghost-exo` skill builds, improves, and debugs workflows on [exo](https://ghostsecurity.ai), an agent orchestration platform.

## Installation (Claude Code)

Install the plugin from the Ghost Security marketplace:

```
/plugin marketplace add ghostsecurity/skills
/plugin install exo@ghost-security
```

## Usage

Connect your exo MCP server, then run:

```
/ghost-exo     # Turn an idea into a workflow, iterate on an existing one, or diagnose a failed run
```

The skill routes each request to one of three intents:

- **BUILD** takes a rough idea through interrogation, assessment, and resource creation in dependency order.
- **IMPROVE** runs the observe-and-iterate loop over recent runs behind two approval gates.
- **DEBUG** diagnoses a single failed run by walking the dependency graph of everything it touched.

## Feedback, Feature Requests, and Issues

[Open an Issue](https://github.com/ghostsecurity/skills/issues/new) per the [Contributing](../../.github/CONTRIBUTING.md) guidelines.
