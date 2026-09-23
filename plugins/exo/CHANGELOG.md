# Changelog

## 1.0.0 - 2026-09-23

Initial release of the `exo` plugin. The `ghost-exo` skill previously shipped in the `ghost` plugin.

### Skills

- **ghost-exo** - One front door for building, improving, and debugging workflows on [exo](https://ghostsecurity.ai), an agent orchestration platform. Routes a request to one of three intents. BUILD takes a rough idea through interrogation, assessment, and resource creation in dependency order. IMPROVE runs the observe-and-iterate loop over recent runs behind two approval gates. DEBUG diagnoses a single failed run by walking the dependency graph of everything it touched. Bundles `scripts/exo-skill.py`, which moves skill bundles over REST so file contents never serialize as tool-call arguments. Harness-neutral: the bundle names no harness, and on first use it registers the exo MCP server for whichever harness is running it.
