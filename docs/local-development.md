# Local Development Guide

How to use Slay Check on your machine (no GitHub Actions required).

## Prerequisites

- Python 3.11+
- Git
- **One of:**
  - **Ollama** (free, local) — [install Ollama](https://ollama.com), then `ollama pull llama3`. No API key needed.
  - **GitHub Models** (free) — uses your existing GitHub PAT.
  - AI provider API key (OpenAI, Anthropic, Google AI, Perplexity)
- GitHub personal access token (only needed for `--pr` reviews, **not** for `--local`)

## Installation

```bash
# Option 1 — install from GitHub (recommended)
pip install git+https://github.com/prathameshap/slay-check.git

# Option 2 — editable install for contributing
git clone https://github.com/prathameshap/slay-check.git
cd slay-check
pip install -e ".[dev]"
```

## Set tokens

**macOS / Linux:**

```bash
export SLAY_CHECK_AI_TOKEN="your-ai-key"
export SLAY_CHECK_GITHUB_TOKEN="your-github-pat"   # only for --pr reviews
```

**Windows (PowerShell):**

```powershell
$env:SLAY_CHECK_AI_TOKEN = "your-ai-key"
$env:SLAY_CHECK_GITHUB_TOKEN = "your-github-pat"
```

Or create a `.env` file in your project root (auto-loaded by Slay Check):

```
SLAY_CHECK_AI_TOKEN=your-ai-key
SLAY_CHECK_GITHUB_TOKEN=your-github-pat
```

To avoid re-exporting in every terminal, set them in your IDE:
**VS Code / Cursor** → Settings → search "terminal env" → add tokens to `terminal.integrated.env.*`.

## Usage

### Free local reviews (no API key)

**Ollama (completely free, offline):**

```bash
ollama pull llama3                     # download model once
export SLAY_CHECK_AI_PROVIDER=ollama   # or set in slay-check.yaml
slay-check review --local
```

**GitHub Models (free with GitHub account):**

```bash
export SLAY_CHECK_AI_PROVIDER=github
export SLAY_CHECK_AI_TOKEN="ghp_your-github-pat"
slay-check review --local
```

### Review local changes (no GitHub token needed)

```bash
# Unstaged changes (git diff)
slay-check review --local

# Staged changes (git diff --cached)
slay-check review --local --staged

# Both default to --dry-run (no posting)
```

### Review a pull request

```bash
slay-check review --repo owner/repo --pr 42
slay-check review --repo owner/repo --pr 42 --dry-run --verbose
```

### Initialize config (interactive wizard)

```bash
slay-check config init
```

## Configuration

See [README — Configuration](https://github.com/prathameshap/slay-check#configuration) for presets, focus lists, and full YAML reference.

Quick example:

```yaml
review_preset: security      # or: full, standard, minimal, performance
dry_run: true                 # safe for local dev
verbose: true
```

## Troubleshooting

| Error | Fix |
|-------|-----|
| `AI token is required` | Set `SLAY_CHECK_AI_TOKEN` (env var or `.env`). |
| `GitHub token is required` | Set `SLAY_CHECK_GITHUB_TOKEN`, or use `--local` which doesn't need it. |
| `No files to review` | Check `exclude_patterns` in config; try `--verbose`. |
| `Provider not found` | Verify `ai_provider` in `slay-check.yaml`. Supported: `openai`, `anthropic`, `google`, `perplexity`, `ollama`, `github`, `custom_http`. |
| API rate limits | Reduce `max_files_per_pr` or switch provider. |

### Debug mode

```bash
slay-check review --pr 42 --repo owner/repo --verbose --dry-run
```

## IDE integration

### VS Code / Cursor

```json
{
  "terminal.integrated.env.osx": {
    "SLAY_CHECK_AI_TOKEN": "your-token",
    "SLAY_CHECK_GITHUB_TOKEN": "your-token"
  },
  "terminal.integrated.env.windows": {
    "SLAY_CHECK_AI_TOKEN": "your-token",
    "SLAY_CHECK_GITHUB_TOKEN": "your-token"
  }
}
```

### Pre-commit hook

```bash
#!/bin/bash
slay-check review --local
if [ $? -ne 0 ]; then
  echo "Review failed. Please fix issues before committing."
  exit 1
fi
```
