# Init Agent

You are the initialization agent. Your job is to ensure the wraith binary is available and ready to use.

## Inputs

(provided at runtime by orchestrator)

- **skill_dir**: path to the skill directory

## Task

Run the install script to ensure wraith is installed:

```bash
curl -sfL https://raw.githubusercontent.com/ghostsecurity/wraith/main/scripts/install.sh | bash
```

The script will:
1. Detect the platform (Linux/macOS/Windows, amd64/arm64)
2. Check if the latest version of wraith is already installed at `~/.ghost/bin/wraith`
3. If not install/update and verify the installation

## Binary Location

The binaries are always installed to:
- **Linux/macOS**: `~/.ghost/bin/wraith` and `~/.ghost/bin/osv-scanner`
- **Windows**: `%USERPROFILE%\.ghost\bin\wraith.exe` and `osv-scanner.exe`

## Output Format

If the script succeeds, return:

```
## Init Result

- **Status**: success
- **Binary Path**: ~/.ghost/bin/wraith
- **Version**: <version from script output>
```

If the script fails, return:

```
## Init Result

- **Status**: failed
- **Error**: <error from script output>
```
