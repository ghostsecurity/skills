# Contributing to Ghost Security's Skills

Thanks for your interest in contributing to these skills! Here's how to get started.

## How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b my-feature`)
3. Make your changes
4. Submit a pull request

## Development Setup

Prerequisites: claude code, bash, git

```bash
git clone https://github.com/<your-fork>/skills.git
cd path/to/local/repo/on/disk
claude --plugin_dir=path/to/fork/of/skills
```

## Running the Skill(s)

```
/ghost:<skill-name>
```

## Pull Requests

- Keep PRs focused on a single change
- Write clear, descriptive commit messages
- Add tests for new functionality
- Ensure `make test` and `make lint` pass

## Reporting Bugs

Open a [GitHub Issue](https://github.com/ghostsecurity/skills/issues) with:

- Steps to reproduce
- Expected vs actual behavior
- Skills/plugin version
- Claude Code version
- OS and environment details

## Suggesting Features

Open a [GitHub Issue](https://github.com/ghostsecurity/skills/issues) describing:

- The use case or problem
- Your proposed solution (if any)

## License

By contributing, you agree that your contributions will be licensed under the [Apache License 2.0](../LICENSE).
