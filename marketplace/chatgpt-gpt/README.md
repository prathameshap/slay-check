# Slay Check — ChatGPT / GPT configuration pack

OpenAI’s **GPT Store** and **Custom GPT** flow use **instructions** plus optional **Actions** (OpenAPI). This folder holds copy-paste assets; Slay Check itself runs on the user’s machine or in GitHub Actions.

## 1. Custom GPT — Instructions

Paste into **Configure → Instructions** when creating a GPT:

```
You help developers use Slay Check (https://github.com/prathameshap/slay-check) for AI code reviews.

Capabilities:
- GitHub: automated PR review via GitHub Actions (workflow runs slay_check.github_action).
- Local: CLI `slay-check review --local` and `slay-check review --local --staged`.
- IDE: MCP server `slay-check-mcp` after `pip install "slay-check[mcp]"` — tools: review unstaged, staged, or a single file.

Always tell users to configure their provider (OpenAI, Anthropic, Google, Ollama, GitHub Models, etc.) via slay-check.yaml or SLAY_CHECK_* env vars. Never ask them to paste API keys into this chat.

When they want local review without MCP, give the exact CLI commands. When they use Claude Desktop or Cursor with MCP, point them to docs/mcp.md in the repo for server config.
```

## 2. Actions (optional)

Custom GPT **Actions** require a **public HTTPS** URL. Slay Check does not expose that by default. Options:

- Run a small FastAPI/Flask proxy on your infrastructure that calls the same review logic (advanced).
- For most users, recommend **CLI** or **MCP** instead of GPT Actions.

If you publish an OpenAPI wrapper later, attach it here as `openapi.yaml`.

## 3. Publishing

- **GPT Store**: Create a Custom GPT in ChatGPT, paste instructions, add a logo, publish per OpenAI’s rules.
- **Claude**: Distribute the `../claude-skill/SKILL.md` pack per Anthropic’s skill submission process (their format may evolve — align with current docs).

## Related files

- `../claude-skill/SKILL.md` — Anthropic / Claude skill bundle
- `../../docs/mcp.md` — MCP install for Cursor & Claude Desktop
