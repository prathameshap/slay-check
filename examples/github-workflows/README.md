# Example GitHub Actions workflows

Copy any of these workflow files into your repository’s `.github/workflows/` to customize how Slay Check runs on pull requests.

| File | Use case |
|------|----------|
| **slay-check-forked.yml** | Run Slay Check from your own fork (e.g. to test changes before release). Set `YOUR_USERNAME` and secrets: `SLAY_CHECK_TOKEN`, `SLAY_CHECK_AI_TOKEN`. |
| **slay-check-environment.yml** | Different provider and thresholds for “development” (feature-branch PRs) vs “production” (PRs targeting main). Needs `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GITHUB_TOKEN`. |
| **slay-check-debug.yml** | Debug mode: verbose logs, dry run, no comments posted. Use when troubleshooting token or setup issues. |
| **slay-check-multi-provider.yml** | Choose provider by PR label: `security` → Anthropic, `performance` → OpenAI, otherwise Google. Needs `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_AI_API_KEY`, `GITHUB_TOKEN`. |

The main repo uses the standard workflow in [.github/workflows/slay-check.yml](../../.github/workflows/slay-check.yml); these examples are optional variants.
