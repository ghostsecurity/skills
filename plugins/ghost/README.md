# Ghost's AI-native Application Security Skills

## Installation (Claude Code)

Quickly install the skills plugin using the marketplace capability in Claude Code:

```
/plugin marketplace add ghostsecurity/skills
/plugin install ghost@ghost-security
```

## Documentation

Full documentation, tutorials, and video usage guides are available at [ghostsecurity.ai](https://ghostsecurity.ai).

## Quick Start

1. Open Claude Code in your repository:
   ```
   cd /path/to/your/repo
   claude
   ```

2. Install the skills plugin if not already installed (see above).

3. Build repository context (recommended before scanning):
   ```
   /ghost:repo-context       # Build a shared repository context used by all the scan skills
   ```

4. Run scans to understand the security posture of your repository:
   ```
   /ghost:scan-deps     # Exploitability analysis of dependency vulnerabilities (SCA)
   /ghost:scan-secrets  # Context assessment of detected secrets and credentials 
   /ghost:scan-code     # AI-powered detection of code security issues (SAST)
   ```

5. Generate a combined security report:
   ```
   /ghost:report        # Combined security report across all scan results
   ```

6. Validate findings against a live application:
   ```
   /ghost:validate      # Dynamic/live validation against a live application (DAST)
   ```

## Contributing

Contributions are welcome! Please open a pull request or issue on this repository.

## Feedback, Feature Requests, and Issues

- **Skills**: [This repository](https://github.com/ghostsecurity/skills/issues)
- **Reaper**: [ghostsecurity/reaper](https://github.com/ghostsecurity/reaper/issues)
- **Wraith**: [ghostsecurity/wraith](https://github.com/ghostsecurity/wraith/issues)
- **Poltergeist**: [ghostsecurity/poltergeist](https://github.com/ghostsecurity/poltergeist/issues)
