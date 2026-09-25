# Changelog

## 1.2.0 - 2026-09-25

Lets a build start from an agent template in the ghostsecurity.ai catalog. The website hands a user one prompt that names the template slug.

### Skills

- **ghost-exo** - The build intent accepts an agent template slug. It fetches `https://ghostsecurity.ai/agents/<slug>.md` and offers the template's outcome, steps, and requirements as proposed defaults in the interrogation.
- **ghost-exo** - The blueprint records the agent template slug and the URL it came from.

## 1.1.0 - 2026-09-23

Teaches the exo skill the runtime contract every workflow step runs under. A first build no longer has to guess how to emit metrics or where to save output.

### Skills

- **ghost-exo** - Adds a runtime contract to the shared substrate. It covers durable output in `$EXO_OUTPUT_DIR` with the `output.txt` fallback, `exo-metric` emission with task-scoped keys that roll up to the workflow run, `exo-done` completion, and workflow memory at `$EXO_AGENT_MEMORY_PATH`.
- **ghost-exo** - The build intent asks once for the script language, recommends python3, and keeps shell for small scripts with no data handling. It also asks whether scripts need third-party packages.
- **ghost-exo** - The build intent treats durable files as optional. When the blueprint names files, the first run checks that the capture holds them.
- **ghost-exo** - The improve intent detects repeated work across runs and proposes workflow memory to skip items already handled.
- **ghost-exo** - Environment token credentials are created with the `REPLACE_IN_UI` placeholder, and the build waits for the user to set the real value in the UI.

## 1.0.0 - 2026-09-23

Initial release of the `exo` plugin. The `ghost-exo` skill previously shipped in the `ghost` plugin.

### Skills

- **ghost-exo** - One front door for building, improving, and debugging workflows on [exo](https://ghostsecurity.ai), an agent orchestration platform. Routes a request to one of three intents. BUILD takes a rough idea through interrogation, assessment, and resource creation in dependency order. IMPROVE runs the observe-and-iterate loop over recent runs behind two approval gates. DEBUG diagnoses a single failed run by walking the dependency graph of everything it touched. Bundles `scripts/exo-skill.py`, which moves skill bundles over REST so file contents never serialize as tool-call arguments. Harness-neutral: the bundle names no harness, and on first use it registers the exo MCP server for whichever harness is running it.
