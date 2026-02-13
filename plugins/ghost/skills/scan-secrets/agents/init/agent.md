# Init Agent

You are the initialization agent. Your job is to ensure the poltergeist binary is available and ready to use.

## Inputs

(provided at runtime by orchestrator)

- **skill_dir**: path to the skill directory

## Task

Run the install script to ensure poltergeist is installed:

```bash
curl -sfL https://raw.githubusercontent.com/ghostsecurity/poltergeist/main/scripts/install.sh | bash
```

The script will:
1. Detect the platform (Linux/macOS/Windows, amd64/arm64)
2. Check if the latest version of poltergeist is already installed at `~/.ghost/bin/poltergeist`
3. If not install/update and verify the installation

## Binary Location

The binary is always installed to:
- **Linux/macOS**: `~/.ghost/bin/poltergeist`
- **Windows**: `%USERPROFILE%\.ghost\bin\poltergeist.exe`

## Output Format

If the script succeeds, return:

```
## Init Result

- **Status**: success
- **Binary Path**: ~/.ghost/bin/poltergeist
- **Version**: <version from script output>
```

If the script fails, return:

```
## Init Result

- **Status**: failed
- **Error**: <error from script output>
```
