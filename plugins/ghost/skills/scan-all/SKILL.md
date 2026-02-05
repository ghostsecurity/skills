---
name: ghost:scan-all
description: Ghost comprehensive codebase scan for vulnerabilities and secrets
agent: true
model: sonnet
---

Create a task list for invoking these two skills in parallel
1. ghost:scan-code - looks for code flaws
2. ghost:scan-secrets - looks for secrets/keys/tokens/sensitive data in codebases

Summarize the outputs concisely.
