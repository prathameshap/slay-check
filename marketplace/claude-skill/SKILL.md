---
name: slay-check
description: AI code review with Slay Check — local git diffs, staged changes, and single-file review via MCP or CLI.
---

# Slay Check

Help the user run **Slay Check** for AI-powered code review on their machine or in CI.

## When to use

- The user wants a structured review of **local changes**, **staged** changes, or a **specific file**.
- They use **Slay Check** (`slay-check` CLI) or the **MCP server** (`slay-check-mcp`) with Claude Desktop / Cursor.

## Setup (user)

1. Install: `pip install "slay-check[mcp]"` (MCP) or `pip install slay-check` (CLI only).
2. Configure provider: `slay-check config init` or environment variables (`SLAY_CHECK_AI_PROVIDER`, `SLAY_CHECK_AI_TOKEN`, etc.). See project README.
3. **MCP**: Add `slay-check-mcp` to the MCP config (see `docs/mcp.md` in the repo).

## What to run

| Goal | Command / tool |
|------|----------------|
| Unstaged diff | `slay-check review --local` or MCP tool `slay_check_review_unstaged` |
| Staged diff | `slay-check review --local --staged` or `slay_check_review_staged` |
| One file | MCP tool `slay_check_review_file` with `file_path` |

## Behavior

- Prefer **MCP tools** when the user is in Claude Desktop / Cursor with MCP enabled.
- Otherwise suggest the **CLI** commands above.
- Do not invent API keys; point the user to `slay-check.yaml` / `.env` / GitHub Actions secrets for CI.

## Links

- Repository: https://github.com/prathameshap/slay-check
- MCP setup: `docs/mcp.md` in the repo
