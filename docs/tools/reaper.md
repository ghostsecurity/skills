# Reaper

Reaper is the MITM HTTPS proxy in Ghost Security AppSec Skills. It intercepts in-scope traffic, stores full request/response pairs in a local SQLite database, and provides a CLI for searching and inspecting captured data.

## Architecture

Reaper runs as a local HTTPS proxy that performs man-in-the-middle interception on in-scope domains:

1. **CA generation** -- on startup, Reaper creates an ephemeral self-signed Certificate Authority in memory
2. **TLS interception** -- for in-scope domains, Reaper dynamically generates per-host certificates signed by the CA, allowing it to decrypt and inspect HTTPS traffic (client requests still must ignore certificate warnings)
3. **Selective capture** -- only traffic to in-scope domains is intercepted and logged. Out-of-scope traffic passes through transparently
4. **SQLite storage** -- every intercepted request and response is stored locally with full headers, bodies, timing, and metadata
5. **CLI access** -- search, filter, and inspect captured traffic from the command line

All data is stored at `~/.ghost/reaper/`: the SQLite database, Unix domain socket for IPC, and a PID file for daemon management.

## Key features

- **Selective interception** -- scope by domain suffix or exact hostname. Only in-scope traffic is captured
- **Full capture** -- complete request and response including headers, bodies, and timing
- **Daemon mode** -- run in the background with CLI access to search and inspect traffic
- **In-memory CA** -- certificates generated fresh on each start, never persisted to disk
- **Per-host certificate caching** -- generated certificates are cached in memory for performance
- **CLI search and filter** -- find traffic by method, host, path, status code, or domain

## CLI reference

### reaper start

Start the MITM proxy.

```shell
reaper start [flags]
```

| Flag | Default | Description |
|---|---|---|
| `--domains` | -- | Domain suffixes to intercept (e.g., `example.com` matches `api.example.com`) |
| `--hosts` | -- | Exact hostnames to intercept |
| `--port` | `8443` | Proxy listen port |
| `-d`, `--daemon` | `false` | Run as background daemon |

Requires at least one `--domains` or `--hosts` flag. Both options accept comma separated lists.

```shell
# Start in foreground, intercepting all traffic to example.com and subdomains
reaper start --domains example.com

# Start as daemon on custom port
reaper start --domains example.com,example.net --port 9090 --daemon

# Scope to specific hosts
reaper start --hosts api.example.com,webhook.internal --daemon
```

In foreground mode, Reaper prints live traffic events:

```text
14:32:05 ⇄ GET https://api.example.com/users 200 245ms
14:32:06 = GET http://cdn.other.com/style.css 200 89ms
```

`⇄` marks an intercepted request. `=` marks an out-of-scope plain HTTP request. Out-of-scope HTTPS tunnels print nothing.

### reaper search

Search captured traffic with filters.

```shell
reaper search [flags]
```

| Flag | Default | Description |
|---|---|---|
| `--method` | -- | Filter by HTTP method (exact match) |
| `--host` | -- | Filter by hostname (supports `*` wildcard) |
| `--domains` | -- | Filter by domain suffix |
| `--path` | -- | Filter by path (prefix match or `*` wildcard) |
| `--status` | -- | Filter by HTTP status code |
| `-n`, `--limit` | `100` | Maximum results |

```shell
# Find all POST requests
reaper search --method POST

# Find requests to a specific path
reaper search --path "/api/v1/users*"

# Find errors on a domain
reaper search --domains example.com --status 500

# Find requests to any subdomain
reaper search --host "*.api.example.com"
```

Output is a table with columns: `ID`, `METHOD`, `HOST`, `PATH`, `STATUS`, `MS`, `REQ` (size), `RES` (size).

### reaper get

Show full request and response for a captured entry.

```shell
reaper get <id>
```

Prints the complete HTTP request (method, headers, body) followed by the complete HTTP response (status, headers, body).

### reaper req

Show only the raw HTTP request for an entry.

```shell
reaper req <id>
```

### reaper res

Show only the raw HTTP response for an entry.

```shell
reaper res <id>
```

### reaper logs

Show recent proxy log entries.

```shell
reaper logs [flags]
```

| Flag | Default | Description |
|---|---|---|
| `-n`, `--number` | `50` | Number of entries to show |

### reaper tail

Stream new proxy log entries in real time.

```shell
reaper tail
```

Prints one line per new entry with the time, method, URL, status code, and duration. It checks for new entries every 500 milliseconds. Press Ctrl+C to stop.

### reaper clear

Delete all captured entries from the database.

```shell
reaper clear
```

### reaper stop

Stop the running daemon.

```shell
reaper stop
```

Gracefully shuts down the proxy, closes the database, and removes the socket and PID files.

### reaper version

Show version information.

```shell
reaper version
```

## Scope configuration

Reaper uses two scoping mechanisms:

**Domain suffix matching** (`--domains`) -- matches the domain and all subdomains:
- `--domains example.com` matches `example.com`, `api.example.com`, `v1.api.example.com`

**Exact host matching** (`--hosts`) -- matches only the specified hostname:
- `--hosts api.example.com` matches `api.example.com` only, not `v2.api.example.com`

Traffic outside the configured scope passes through transparently. Reaper relays the bytes without decrypting or inspecting them.

## Data storage

All captured data is stored locally at `~/.ghost/reaper/`:

| File | Purpose |
|---|---|
| `reaper.db` | SQLite database with captured requests and responses |
| `reaper.sock` | Unix domain socket for CLI-to-daemon IPC |
| `reaper.pid` | Daemon process ID |

Each captured entry includes:

- HTTP method, scheme, host, path, and query string
- Full request headers and body
- HTTP status code
- Full response headers and body
- Timestamp and round-trip duration in milliseconds

## Daemon vs foreground

**Foreground mode** -- the proxy runs in your terminal, prints live traffic events, and stops when you press Ctrl+C.

**Daemon mode** -- the proxy runs in the background. Use the CLI commands (`search`, `get`, `logs`, `tail`, `clear`, `stop`) to interact with it. Use daemon mode for automated workflows and skill integration.

In daemon mode, the parent process detaches the proxy into its own session and waits for the Unix socket to become available before exiting. The CLI communicates with the daemon via JSON messages over the socket.

## Skill integration

Two skills in Ghost Security AppSec Skills use Reaper:

**`ghost-proxy`** manages the Reaper lifecycle (start, stop, search, inspect). **`ghost-validate`** uses Reaper for live vulnerability validation: start a proxy, authenticate, exercise a vulnerable endpoint, modify the request to attempt an exploit, and inspect the response.

See [Live validation](../capabilities/live-validation.md) for details.

---

Previous: [Wraith](wraith.md) | Next: [Exorcist](exorcist.md) | [Docs home](../../README.md#documentation)
