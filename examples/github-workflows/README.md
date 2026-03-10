# Example GitHub Actions workflows

Copy any of these workflow files into your repository's `.github/workflows/` to customize how Slay Check runs on pull requests.

## Provider-specific workflows

Each file is a ready-to-use workflow for a single AI provider. Pick the one that matches the API key you have.

| File | Provider | Required secret | Default model |
|------|----------|-----------------|---------------|
| **slay-check-anthropic.yml** | Anthropic (Claude) | `ANTHROPIC_API_KEY` | `claude-3-sonnet-20240229` |
| **slay-check-openai.yml** | OpenAI | `OPENAI_API_KEY` | `gpt-4o` |
| **slay-check-google.yml** | Google AI (Gemini) | `GOOGLE_AI_API_KEY` | `gemini-pro` |
| **slay-check-perplexity.yml** | Perplexity AI | `PERPLEXITY_API_KEY` | `sonar-pro` |
| **slay-check-custom-http.yml** | Custom HTTP endpoint | `SLAY_CHECK_AI_TOKEN` (optional) | — |

Override the model via the `SLAY_CHECK_AI_MODEL` repository variable without editing the workflow file.

## Other example workflows

| File | Use case |
|------|----------|
| **slay-check-forked.yml** | Run Slay Check from your own fork (e.g. to test changes before release). Set `YOUR_USERNAME` and secrets: `SLAY_CHECK_TOKEN`, `SLAY_CHECK_AI_TOKEN`. |
| **slay-check-environment.yml** | Different provider and thresholds for "development" (feature-branch PRs) vs "production" (PRs targeting main). Needs `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GITHUB_TOKEN`. |
| **slay-check-debug.yml** | Debug mode: verbose logs, dry run, no comments posted. Use when troubleshooting token or setup issues. |
| **slay-check-multi-provider.yml** | Choose provider by PR label: `security` → Anthropic, `performance` → OpenAI, otherwise Google. Needs `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_AI_API_KEY`, `GITHUB_TOKEN`. |

The main repo uses the standard workflow in [.github/workflows/slay-check.yml](../../.github/workflows/slay-check.yml); these examples are optional variants.

To choose what gets reviewed (security only, performance, etc.), set repository variables or add `slay-check.yaml`: use `review_preset: security` or `review_focus: [security, performance]`. See [Configuration](https://github.com/prathameshap/slay-check#configuration) and [GitHub Action docs](../../docs/github-action.md) for defaults and all options.
