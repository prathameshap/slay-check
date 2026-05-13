# Slay Check MCP (Model Context Protocol)

Run Slay Check as an MCP server so **Claude Desktop**, **Cursor**, and other MCP clients can call review tools without using the terminal manually.

## Install

```bash
pip install "slay-check[mcp]"
# or from a clone:
pip install -e ".[mcp]"
```

Configure your AI provider the same way as the CLI (`slay-check.yaml`, `.env`, or `SLAY_CHECK_*` variables).

## Tools

| Tool | Description |
|------|-------------|
| `slay_check_review_unstaged` | Review `git diff` (unstaged changes) |
| `slay_check_review_staged` | Review `git diff --cached` (staged changes) |
| `slay_check_review_file` | Review a single file by path (relative to workspace) |

Optional: set `SLAY_CHECK_WORKDIR` if the server’s current working directory should not be the repo root.

## Cursor

Add to your MCP settings (e.g. **Cursor Settings → MCP**) a server entry:

```json
{
  "mcpServers": {
    "slay-check": {
      "command": "slay-check-mcp",
      "args": [],
      "env": {}
    }
  }
}
```

Use the full path to `slay-check-mcp` if it is not on `PATH` (e.g. Windows: path to Scripts).

## Claude Desktop

Add under `claude_desktop_config.json` (location varies by OS):

```json
{
  "mcpServers": {
    "slay-check": {
      "command": "slay-check-mcp",
      "args": []
    }
  }
}
```

Restart Claude Desktop after editing.

## Notes

- The MCP server sets `SLAY_CHECK_DRY_RUN=true` by default so reviews never post GitHub comments.
- You still need network access to your chosen AI provider (or Ollama locally).
