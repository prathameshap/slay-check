# Setup Guide

Complete guide for getting Slay Check running in GitHub Actions.

For **local CLI** usage, see [Local Development](local-development.md).
For **configuration** (presets, providers, YAML reference), see [README — Configuration](https://github.com/prathameshap/slay-check#configuration).

## Step 1: Get an AI Provider API Key

| Provider | Where to get a key |
|----------|--------------------|
| **OpenAI** | [platform.openai.com](https://platform.openai.com/) → API Keys → Create new secret key (starts with `sk-`) |
| **Anthropic** | [console.anthropic.com](https://console.anthropic.com/) → API Keys → Create Key (starts with `sk-ant-`) |
| **Google AI** | [aistudio.google.com](https://aistudio.google.com/) → API Keys → Create API Key |
| **Perplexity** | [docs.perplexity.ai](https://docs.perplexity.ai/) → API Keys |
| **Ollama** (free, local) | No key needed — [install Ollama](https://ollama.com), run `ollama pull llama3.2`, set `ai_provider: ollama` |
| **GitHub Models** (free) | Only if you choose GitHub Models as the AI provider, use your existing GitHub PAT and set `ai_provider: github` |

Slay Check itself is installed from the public `prathameshap/slay-check` repository, so users do not need to create a GitHub token just to install or run the GitHub Actions templates.

## Step 2: Add Repository Secrets

1. Go to your repo on GitHub → **Settings** → **Secrets and variables** → **Actions**.
2. Click **New repository secret** and add:

| Secret | Value | Notes |
|--------|-------|-------|
| Your provider key (e.g. `OPENAI_API_KEY`) | The key from Step 1 | Name must match the workflow template you choose |
| `GITHUB_TOKEN` | (automatic) | Provided by GitHub Actions; no action needed |

## Step 3: Copy a Workflow Template

Copy one file from [`examples/github-workflows/`](../examples/github-workflows/) into your repo's `.github/workflows/`. Pick the template that matches your provider:

| File | Provider | Secret required |
|------|----------|-----------------|
| `slay-check-openai.yml` | OpenAI | `OPENAI_API_KEY` |
| `slay-check-anthropic.yml` | Anthropic | `ANTHROPIC_API_KEY` |
| `slay-check-google.yml` | Google AI | `GOOGLE_AI_API_KEY` |
| `slay-check-perplexity.yml` | Perplexity | `PERPLEXITY_API_KEY` |
| `slay-check-custom-http.yml` | Custom endpoint | `SLAY_CHECK_AI_TOKEN` (optional) |

For advanced setups (forks, multi-provider, environment-specific), see [examples/github-workflows/README.md](../examples/github-workflows/README.md).

## Step 4: Configure (Optional)

Create `slay-check.yaml` in your repo root:

```yaml
review_preset: security   # full | standard | minimal | security | performance
```

Or use environment variables: `SLAY_CHECK_REVIEW_PRESET=security`.

See [README — Configuration](https://github.com/prathameshap/slay-check#configuration) for the full YAML reference, presets, focus lists, and defaults.

## Step 5: Test

1. Open a pull request.
2. Check the **Actions** tab — Slay Check should run.
3. Look for a review comment on the PR.
4. If something fails, check the workflow logs; common fixes are in [Troubleshooting](#troubleshooting) below.

## Troubleshooting

| Error | Fix |
|-------|-----|
| `AI token is required` | Verify the secret name matches what the workflow template expects (e.g. `OPENAI_API_KEY`). |
| `Repository not found` | Verify the repository URL/name. A PAT is only needed when checking out a private fork or private dependency. |
| `Permission denied` | For normal public Slay Check workflows, use the automatic `${{ secrets.GITHUB_TOKEN }}`. For private forks, use a PAT with the minimum required repository access. |
| `No files to review` | Check `exclude_patterns`; verify files have code changes and aren't too large. |

### Debug mode

Add these env vars to the workflow step:

```yaml
env:
  SLAY_CHECK_VERBOSE: "true"
  SLAY_CHECK_DRY_RUN: "true"
```

## Support

- [GitHub Issues](https://github.com/prathameshap/slay-check/issues)
- [GitHub Discussions](https://github.com/prathameshap/slay-check/discussions)
