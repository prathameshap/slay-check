# Slay Check

> **Slay Check** — AI-powered code review for GitHub Actions and local development

**TL;DR** — Copy the workflow below into `.github/workflows/slay-check.yml`, add the `SLAY_CHECK_AI_TOKEN` secret (your AI provider key), and open a PR. You’ll get one AI review comment per PR. Optional: set provider/model via variables or a `slay-check.yaml` file.

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-AGPL%20v3%20%7C%20GPL%20v3-green.svg)](LICENSE-AGPL)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-ready-orange.svg)](.github/workflows)

**Slay Check** gives you a single, comprehensive AI review comment on every pull request. It supports multiple AI providers (OpenAI, Anthropic, Google Gemini, Perplexity, and Custom HTTP) with configurable criteria: problem analysis, algorithm review, complexity, and risk evaluation.

## Features

- **Multi-AI Support**: OpenAI GPT-4, Anthropic Claude, Google Gemini, Perplexity AI
- **GitHub Actions Ready**: Automated PR reviews
- **Single comment**: Full review (summary + per-file details) in one PR comment
- **CLI Interface**: Local development support
- **Configurable Analysis**: Customize review criteria
- **Comprehensive Scoring**: Detailed feedback with actionable suggestions
- **Security Focused**: Built-in security and risk assessment

## Quick Start

### GitHub Actions (3 steps)

1. **Add a workflow** — Create `.github/workflows/slay-check.yml` and paste the workflow below. The install step uses `GITHUB_TOKEN` so the job can clone this repo; you only add your AI key in step 2.

```yaml
name: Slay Check - AI Code Review
on:
  pull_request:
    types: [opened, synchronize, reopened]
  pull_request_target:
    types: [opened, synchronize, reopened]

jobs:
  slay-check:
    runs-on: ubuntu-latest
    if: github.event.pull_request.draft == false
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install Slay Check
        run: pip install git+https://x-access-token:${{ secrets.GITHUB_TOKEN }}@github.com/prathameshap/slay-check.git
      - name: Run Slay Check
        env:
          GITHUB_REPOSITORY: ${{ github.repository }}
          GITHUB_PR_NUMBER: ${{ github.event.pull_request.number }}
          GITHUB_EVENT_NAME: ${{ github.event_name }}
          SLAY_CHECK_AI_PROVIDER: ${{ vars.SLAY_CHECK_AI_PROVIDER || 'openai' }}
          SLAY_CHECK_AI_MODEL: ${{ vars.SLAY_CHECK_AI_MODEL || 'gpt-4o' }}
          SLAY_CHECK_AI_BASE_URL: ${{ vars.SLAY_CHECK_AI_BASE_URL || 'https://api.openai.com/v1/' }}
          SLAY_CHECK_AI_TOKEN: ${{ secrets.SLAY_CHECK_AI_TOKEN }}
          SLAY_CHECK_GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SLAY_CHECK_VERBOSE: ${{ vars.SLAY_CHECK_VERBOSE || 'false' }}
          SLAY_CHECK_DRY_RUN: ${{ vars.SLAY_CHECK_DRY_RUN || 'false' }}
        run: python -m slay_check.github_action
```

2. **Add repository secrets** (Settings → Secrets and variables → Actions):
   - **`SLAY_CHECK_AI_TOKEN`** — Your AI provider API key (OpenAI, Anthropic, Google, Perplexity, etc.).
   - **`GITHUB_TOKEN`** — Provided automatically; no need to create it.

3. **Open a PR** — On every non-draft pull request, the workflow runs, reviews changed files with your AI provider, and posts **one comment** with the full review.

**Optional:** Set repository **variables** (Settings → Variables) or add a `slay-check.yaml` in the repo root:
   - `SLAY_CHECK_AI_PROVIDER`: `openai` | `anthropic` | `google` | `perplexity` | `cursor` | `http` | `custom_http`
   - `SLAY_CHECK_AI_MODEL`: e.g. `gpt-4o`, `claude-3-sonnet-20240229`, `gemini-2.0-flash`, `sonar-pro`
   - `SLAY_CHECK_AI_BASE_URL`: for custom/OpenAI-compatible endpoints
   - `SLAY_CHECK_VERBOSE`: `true` | `false`
   - `SLAY_CHECK_DRY_RUN`: `true` to run without posting comments
   - `SLAY_CHECK_REVIEW_PRESET`: `full` | `standard` | `minimal` | `security` | `performance` — what to review (see [Configuration](#configuration))
   - `SLAY_CHECK_REVIEW_FOCUS`: comma-separated list, e.g. `security,performance` — only these criteria

**Where the review appears**  
Slay Check posts **one comment** per PR. By default it’s an **issue comment** (main conversation under "Conversation"). To use a **PR review** comment instead, set `use_issue_comments: false` in `slay-check.yaml`. The comment includes the summary, per-file analysis, issues, and suggestions.

**Provider-specific workflows:** Ready-made workflows per provider live in [examples/github-workflows/](examples/github-workflows/). Copy the one you need into `.github/workflows/` and set the matching secret.

| Workflow file | Provider | Secret required |
|---------------|----------|-----------------|
| `slay-check-anthropic.yml` | Anthropic (Claude) | `ANTHROPIC_API_KEY` |
| `slay-check-openai.yml` | OpenAI (GPT) | `OPENAI_API_KEY` |
| `slay-check-google.yml` | Google AI (Gemini) | `GOOGLE_AI_API_KEY` |
| `slay-check-perplexity.yml` | Perplexity AI | `PERPLEXITY_API_KEY` |
| `slay-check-custom-http.yml` | Custom HTTP endpoint | `SLAY_CHECK_AI_TOKEN` (optional) |

For more options (run from a fork, environment-specific or label-based workflows), see [docs/github-action.md](docs/github-action.md) and [examples/github-workflows/](examples/github-workflows/).

### Local Development

**From VS Code or Cursor**  
Open the integrated terminal and run Slay Check from your project (or from a clone of this repo):

```bash
# Install (once)
pip install git+https://github.com/prathameshap/slay-check.git

# Set tokens (or use slay-check.yaml / .env)
export SLAY_CHECK_AI_TOKEN="your-ai-key"
export SLAY_CHECK_GITHUB_TOKEN="your-github-pat"

# Review a PR (results in terminal; add --dry-run to avoid posting)
slay-check review --repo owner/repo --pr 42
```

To avoid re-exporting tokens in every terminal, you can set them in the IDE: **VS Code** → Settings → search “terminal env” → add `SLAY_CHECK_AI_TOKEN` and `SLAY_CHECK_GITHUB_TOKEN` to `terminal.integrated.env.*`. In **Cursor**, the same settings apply. There is no VS Code/Cursor extension yet; the CLI is the way to “call” the repo from the IDE.

```bash
# Review local changes (when implemented)
python -m slay_check.cli review --local
```

## Configuration

Create `slay-check.yaml` in your repository (or use environment variables).

### Choose what gets reviewed

**Easiest: use a preset** — one word to focus the review:

```yaml
# One of: full (default), standard, minimal, security, performance
review_preset: security
```

| Preset | What's reviewed |
|--------|------------------|
| `full` | Everything (problem, algorithm, best approaches, complexity, risk, security, performance) |
| `standard` | Same as full but skip problem analysis |
| `minimal` | Security + performance only |
| `security` | Security + risk only |
| `performance` | Algorithm, best approaches, complexity, performance |

**Or pick specific areas** with a list (only these are enabled):

```yaml
review_focus:
  - security
  - performance
  - complexity
```

Allowed focus names: `problem`, `algorithm`, `best_approaches`, `complexity`, `risk`, `security`, `performance`.

**Environment variables:** `SLAY_CHECK_REVIEW_PRESET=security` or `SLAY_CHECK_REVIEW_FOCUS=security,performance` (comma-separated).

**Advanced:** set each criterion explicitly with `review_criteria`:

```yaml
# AI Provider
ai_provider: openai  # openai, anthropic, google, perplexity, custom_http
ai_model: gpt-4o     # Model to use (e.g. gpt-4o, claude-3-sonnet-20240229, gemini-2.0-flash, sonar-pro)

# Analysis Criteria (optional; use preset or focus above for simplicity)
review_criteria:
  analyze_problem: true
  algorithm_analysis: true
  best_approaches: true
  complexity_analysis: true
  risk_assessment: true
  security_review: true
  performance_review: true

# File Filtering
exclude_patterns:
  - "*.md"
  - "*.txt"
  - "vendor/*"
  - "node_modules/*"
  - "__pycache__/*"

# Performance Limits
max_file_size: 10000
max_files_per_pr: 50

# Review Thresholds
min_score_threshold: 6.0
critical_issues_limit: 3
```

### Default values

If you don't set `review_preset` or `review_focus`, the default is **full** (all review criteria enabled). Other defaults:

| Option | Default | Description |
|--------|---------|-------------|
| `ai_provider` | `openai` | AI provider |
| `ai_model` | `gpt-4o` | Model name |
| `review_preset` | *(none → full)* | Preset when not set |
| `review_criteria` | all `true` | When no preset/focus |
| `max_file_size` | `10000` | Max lines per file |
| `max_files_per_pr` | `50` | Max files reviewed per PR |
| `max_tokens` | `4000` | Max tokens per AI response |
| `temperature` | `0.3` | Model temperature |
| `min_score_threshold` | `6.0` | Min score to pass (0–10) |
| `critical_issues_limit` | `3` | Max critical issues allowed |
| `verbose` | `false` | Verbose logging |
| `dry_run` | `false` | Don't post comments |
| `use_issue_comments` | `true` | Post as PR issue comment |

## AI Providers

| Provider | Models / endpoints (examples) | Best For |
|----------|-------------------------------|----------|
| **OpenAI** | GPT-4 family (e.g. `gpt-4o`), or any compatible chat/completions model | General code review |
| **Anthropic** | Claude 3 family (e.g. `claude-3-sonnet-20240229`) | Security and risk-focused analysis |
| **Google AI** | Gemini family (e.g. `gemini-2.0-flash`) | Performance / efficiency analysis |
| **Perplexity** | `sonar`, `sonar-pro`, `sonar-deep-research`, `sonar-reasoning-pro` | Fast, grounded code review |
| **Cursor** | Use **Custom HTTP** with your Cursor-backed or internal gateway URL (see [Custom HTTP](docs/github-action.md#custom-http-provider)) | Teams using Cursor or Cursor-compatible endpoints |
| **Custom HTTP** | Any HTTP endpoint that accepts the Slay Check review JSON and returns the standard response schema | Enterprise / internal models and gateways |

## Documentation

**Where to go next:**

| Goal | Doc |
|------|-----|
| Run in GitHub Actions | [GitHub Actions](docs/github-action.md) |
| Run locally (CLI) | [Local Development](docs/local-development.md) |
| Full setup (secrets, keys, troubleshooting) | [Setup Guide](docs/setup-guide.md) |
| Customize review (presets, providers) | [Configuration](#configuration) below |
| Fork or contribute | [CONTRIBUTING.md](CONTRIBUTING.md) |

**More:** [AI Response Control](docs/ai-response-control.md) · [Forking Guide](docs/forking-guide.md) · [Repo issues & tech debt](docs/REPO_ISSUES.md) · [Licensing](docs/licensing.md)

**Open source & project health:** Security and best-practice scores are tracked by [OpenSSF Scorecard](https://scorecard.dev/viewer/?uri=github.com/prathameshap/slay-check). Results run on every push to `main` and weekly; the badge above links to the latest report.

## Development

```bash
# Clone and install
git clone https://github.com/prathameshap/slay-check.git
cd slay-check
pip install -e ".[dev]"

# Run tests (all providers mocked; no API keys needed)
pytest

# Build package
python -m build
```

### Testing all services

**1. Unit tests (no real APIs)**  
Uses mocks for every provider. No tokens required.

```bash
pip install -e ".[dev]"
export SLAY_CHECK_AI_TOKEN=dummy
export SLAY_CHECK_GITHUB_TOKEN=dummy
pytest tests/ -v
```

- **All tests:** `pytest tests/ -v`
- **AI providers only:** `pytest tests/test_ai.py -v`
- **Config only:** `pytest tests/test_config.py -v`
- **CLI only:** `pytest tests/test_cli.py -v`
- **With coverage:** `pytest tests/ --cov=slay_check --cov-report=term-missing`

**2. Lint (same as CI)**  
```bash
black --check slay_check tests
isort --check-only slay_check tests
flake8 slay_check tests
```

**3. Manual test against real APIs**  
To hit real OpenAI/Anthropic/Google/Perplexity/HTTP endpoints, run the CLI with real tokens and `--dry-run` so nothing is posted to GitHub:

```bash
export SLAY_CHECK_AI_TOKEN="your-openai-key"
export SLAY_CHECK_GITHUB_TOKEN="your-github-pat"
# Optional: SLAY_CHECK_AI_PROVIDER=anthropic (default: openai)

slay-check review --repo owner/repo --pr <PR_NUMBER> --dry-run --verbose
```

Repeat with different `SLAY_CHECK_AI_PROVIDER` (and corresponding token) to test each provider. For **custom HTTP**, set `SLAY_CHECK_AI_PROVIDER=custom_http` and `SLAY_CHECK_AI_BASE_URL` to your endpoint; the token is sent as `Authorization: Bearer <token>`.

## Performance

- **Startup Time**: <1 second
- **Small PR** (1-5 files): <90 seconds
- **Medium PR** (5-15 files): <4 minutes
- **Large PR** (15+ files): <12 minutes
- **Memory Usage**: <500MB peak

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines, including our **branching strategy** (single `main` branch, all changes via PRs). By participating, you agree to our [Code of Conduct](CODE_OF_CONDUCT.md).

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Contributors

This project tracks contributors with [All Contributors](https://allcontributors.org). To add yourself after a merged PR, comment `@all-contributors please add @your-username for code/docs/tests` on the PR or an issue, or run `npx all-contributors add <username> <contribution-type>` locally (see [.all-contributorsrc](.all-contributorsrc)).

<!-- ALL-CONTRIBUTORS-LIST:START -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

## License

**Slay Check** is dual-licensed for **v1.0.0 and earlier**: [AGPL-3.0](LICENSE-AGPL) for enterprises, [GPL-3.0](LICENSE-GPL) for individuals. Redistribution must be free of charge. Versions after 1.0.0 may use different terms. Full details: [Licensing](docs/licensing.md) and the LICENSE files.

## Security

Please report security issues as described in [SECURITY.md](SECURITY.md).

## Support

- **Something wrong?** See [Troubleshooting](docs/setup-guide.md#troubleshooting) in the setup guide.
- **Issues**: [GitHub Issues](https://github.com/prathameshap/slay-check/issues)
- **Discussions**: [GitHub Discussions](https://github.com/prathameshap/slay-check/discussions)

---

**Slay Check** — built for the developer community
