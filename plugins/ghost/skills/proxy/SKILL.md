---
name: "ghost-proxy"
description: Starts and controls the reaper MITM proxy to capture, inspect, search, and replay HTTP/HTTPS traffic between clients and servers. Capabilities include starting/stopping the proxy scoped to specific domains, viewing captured request/response logs, searching traffic by method/path/status/host, and inspecting full raw HTTP entries for security analysis. Use when the user asks to "start the proxy", "capture traffic", "intercept requests", "inspect HTTP traffic", "search captured requests", or "view request/response".
license: apache-2.0
metadata:
  version: 1.1.0
---

# Reaper MITM Proxy

Reaper is a CLI-based MITM HTTPS proxy for application security testing. It intercepts, logs, and allows inspection of HTTP/HTTPS traffic flowing through it. Use it to capture live request/response pairs for security validation.

## Prerequisites

Before using any reaper command, make sure the latest version of the binary is installed:

```bash
curl -sfL https://raw.githubusercontent.com/ghostsecurity/reaper/main/scripts/install.sh | bash
```

All `reaper` commands in this document should be invoked as `~/.ghost/bin/reaper` unless `~/.ghost/bin` is on `PATH`.

## Quick Reference

| Command | Purpose |
|---------|---------|
| `reaper start --domains example.com` | Start proxy (foreground) |
| `reaper start --domains example.com -d` | Start proxy (daemon) |
| `reaper logs` | Show recent captured entries |
| `reaper search --method POST --path /api/*` | Search captured traffic |
| `reaper get <id>` | Show full request + response |
| `reaper req <id>` | Show raw HTTP request only |
| `reaper res <id>` | Show raw HTTP response only |
| `reaper stop` | Stop the daemon |

## Starting the Proxy

Start reaper scoped to the target domain(s). At least one `--domains` or `--hosts` flag is required.

```bash
# Intercept all traffic to example.com and its subdomains
reaper start --domains example.com

# Multiple domains
reaper start --domains example.com,api.internal.co

# Exact hostname matching
reaper start --hosts api.example.com

# Both domain suffix and exact host matching
reaper start --domains example.com --hosts special.internal.co

# Custom port (default: 8443)
reaper start --domains example.com --port 9090

# Run as background daemon
reaper start --domains example.com -d
```

**Scope behavior**:
- `--domains`: Suffix match. `example.com` matches `example.com`, `api.example.com`, `sub.api.example.com`
- `--hosts`: Exact match. `api.example.com` matches only `api.example.com`
- Traffic outside scope passes through transparently without logging

## Routing Traffic Through the Proxy

Configure the HTTP client to use the proxy. The default listen address is `localhost:8443`.

```bash
# curl
curl -x http://localhost:8443 -k https://api.example.com/endpoint

# Environment variables (works with many tools)
export http_proxy=http://localhost:8443
export https_proxy=http://localhost:8443

# Python requests
import requests
requests.get("https://api.example.com/endpoint",
             proxies={"http": "http://localhost:8443", "https": "http://localhost:8443"},
             verify=False)
```

The `-k` / `verify=False` flag is needed because reaper generates its own CA certificate at startup for MITM TLS interception.

## Viewing Captured Traffic

### Recent Entries

```bash
# Show last 50 entries (default)
reaper logs

# Show last 200 entries
reaper logs -n 200
```

Output columns: `ID`, `METHOD`, `HOST`, `PATH`, `STATUS`, `MS`, `REQ` (request body size), `RES` (response body size).

### Searching

```bash
# By HTTP method
reaper search --method POST

# By host (supports * wildcard)
reaper search --host *.api.example.com

# By domain suffix
reaper search --domains example.com

# By path prefix (supports * wildcard)
reaper search --path /api/v3/transfer

# By status code
reaper search --status 200

# Combined filters
reaper search --method POST --path /api/v3/* --status 200 -n 50
```

### Inspecting Individual Entries

```bash
# Full request and response (raw HTTP)
reaper get 42

# Request only
reaper req 42

# Response only
reaper res 42
```

Output is raw HTTP/1.1 format including headers and body, suitable for analysis or replay.

## Stopping the Proxy

```bash
reaper stop
```

## Common Workflows

### Validate a Security Finding

When used with the `validate` skill (may need to collaborate with the user to setup the test environment):

1. Start reaper scoped to the application domain
2. Verify traffic is being captured by running `reaper logs` — at least one entry should appear after routing a test request through the proxy
3. If no entries appear, verify proxy settings and domain scope match the target
4. Authenticate (or ask the user to authenticate) as a normal user and exercise the vulnerable endpoint legitimately
5. Search for the captured request to understand the expected request format
6. Craft and send a malicious request that exercises the exploit described in the finding
7. Inspect the response to determine if the exploit succeeded
8. Use `reaper get <id>` to capture the full request/response as evidence

## Data Storage

All data is stored in `~/.reaper/`:
- `reaper.db` - SQLite database with captured entries
- `reaper.sock` - Unix socket for CLI-to-daemon IPC
- `reaper.pid` - Daemon process ID

The CA certificate is generated fresh in memory on each start and is not persisted.
