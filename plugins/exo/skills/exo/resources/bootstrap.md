# Bootstrap: connecting the exo MCP server

Run this when the exo MCP tools are absent, or when `whoami` fails to reach the workspace. Skip it whenever `whoami` already returns a workspace ID.

## What the connection needs

Register a streamable HTTP MCP server in whatever way this harness registers one. It needs three things:

These key names are the same in a profile file and in the environment:

| Field | Key | Notes |
|---|---|---|
| Endpoint | `EXO_API_URL` | The workspace base URL. Append `/api/v1/mcp`. |
| `Authorization` header | `EXO_API_KEY` | Sent as `Bearer <key>`. |
| `X-Workspace-Id` header | `EXO_WORKSPACE_ID` | The `ws_` identifier the key belongs to. |

Those values arrive by whatever route set this instance up, so look before concluding they are absent. A setup script may have written a connection description file holding a complete `mcpServers` entry to copy verbatim, plus a matching credential profile under `${XDG_CONFIG_HOME:-~/.config}/exo/`. Those are commonly named for the connection, as in `exo-demo.mcp.json` and `exo-demo.env`. Failing that, the user may have exported the variables. Search the working directory and that config directory first, then fall back to the environment.

Report what you could not find, by name, and stop. Never ask the user to paste the key into the conversation, because it would then sit in the transcript. Point them at whichever source is missing instead.

## Name the entry, and leave the others alone

Several exo connections coexist normally. One workspace per entry, and a single deployment often serves more than one. Adding another is the usual case rather than a problem.

When a setup script wrote a connection description file, register under the exact name its `mcpServers` key uses, and never rename it. A credential profile of the same name sits beside it, and renaming one breaks the pair.

Otherwise name the entry after the deployment and the workspace it points at, following whatever convention the existing entries use. Never reuse a bare name like `exo`, because the next connection collides with it.

Never modify or remove an entry that points at a different endpoint or a different workspace. Rewrite an entry only when it already points at the same workspace you are configuring now.

Write the credentials as literal values in this entry. A variable reference cannot work here, because one process holds one value per variable name and several connections need several keys at once. The CLI profile described in `SKILL.md` is where variable indirection belongs.

## Find the mechanism before concluding there is none

Every harness that runs MCP tools can register an MCP server. Do the discovery rather than assuming:

1. Look at how this harness already stores MCP servers, and copy that shape. An existing entry is the most reliable template available, and one is usually there. Copy the structure only. Take no URL, no header value, and no credential reference from another entry, because pointing exo at another service's token sends that token to the exo endpoint.
2. Check the harness CLI for an MCP subcommand and read its help for the flags that set a URL, headers, and a bearer token.
3. Failing both, edit the config file directly in the format the existing entries use. Merge the new entry in. Never rewrite the file from scratch, and never remove or reorder anything you did not add.

Report that registration is impossible only after all three come up empty. Say which you tried.

Write to the narrowest scope the harness offers. Reach for a global or user-wide config only when there is no project-level or session-level alternative.

## The rules that constrain how

Write the key and the workspace ID as literal header values, and use the harness's field for literal headers rather than the one that names environment variables. Those two fields are separate, and the literal field expands nothing. Putting `${VAR}` in it sends that text to the server as the header, which reads as an invalid credential rather than as a mistake in the config.

Resolve the endpoint to a literal URL at write time. Do not template it. Harnesses differ here and at least one drops a server whose URL is not a valid absolute URL, silently and with no error, which produces a config that looks written and yields no tools.

## Gate the write

Editing a config file changes the user's machine outside this workspace, so it gets the same gate as a production write. Show the exact entry and the exact file it lands in, then require an explicit answer before writing. Proceed on approval, and stop on refusal without writing a partial entry.

## Verify

Call `whoami` and confirm it returns a workspace ID. Report that ID and continue to intent classification. An authentication failure here usually means a header carried template text instead of a resolved value, or the key belongs to a different workspace than the `X-Workspace-Id` header names. Recheck both before anything else.

A harness usually loads MCP servers once at session start, so a server registered mid-session may not appear until the user restarts. If `whoami` is still unavailable right after a successful write, say the config is in place and ask the user to restart the session. Do not rewrite the entry or try a different endpoint.
