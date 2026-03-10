# Setup Guide

Complete installation and configuration guide for Slay Check.

## Prerequisites

- GitHub repository
- AI provider API key (OpenAI, Anthropic, or Google AI)
- GitHub personal access token (for private repositories)

## Step 1: Get AI Provider API Key

### OpenAI
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Navigate to **API Keys**
3. Click **Create new secret key**
4. Copy the key (starts with `sk-`)

### Anthropic Claude
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Navigate to **API Keys**
3. Click **Create Key**
4. Copy the key (starts with `sk-ant-`)

### Google AI
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Navigate to **API Keys**
3. Click **Create API Key**
4. Copy the key

## Step 2: Set Up Repository Secrets

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `SLAY_CHECK_AI_TOKEN` | Your AI API key | OpenAI, Anthropic, or Google AI key |
| `SLAY_CHECK_TOKEN` | Your GitHub PAT | Only needed for private repositories |

## Step 3: Create GitHub Actions Workflow

Create `.github/workflows/slay-check.yml` in your repository:

### Basic Setup (Main Repository)

```yaml
name: Slay Check - AI Code Review
on:
  pull_request:
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
          python-version: '3.11'
          
      - name: Install Slay Check
        run: |
          pip install git+https://github.com/YOUR_USERNAME/slay-check.git
          
      - name: Run Slay Check
        env:
          GITHUB_REPOSITORY: ${{ github.repository }}
          GITHUB_PR_NUMBER: ${{ github.event.pull_request.number }}
          SLAY_CHECK_AI_TOKEN: ${{ secrets.SLAY_CHECK_AI_TOKEN }}
          SLAY_CHECK_GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python -m slay_check.github_action
```

### Fork Setup (Custom Repository)

```yaml
name: Slay Check - AI Code Review
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  slay-check:
    runs-on: ubuntu-latest
    if: github.event.pull_request.draft == false
    
    steps:
      - name: Checkout your repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      - name: Checkout Slay Check (your fork)
        uses: actions/checkout@v4
        with:
          repository: YOUR_USERNAME/slay-check
          path: slay-check
          token: ${{ secrets.SLAY_CHECK_TOKEN }}
          
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install Slay Check from fork
        run: |
          cd slay-check
          pip install -e .
          
      - name: Run Slay Check
        env:
          GITHUB_REPOSITORY: ${{ github.repository }}
          GITHUB_PR_NUMBER: ${{ github.event.pull_request.number }}
          SLAY_CHECK_AI_TOKEN: ${{ secrets.SLAY_CHECK_AI_TOKEN }}
          SLAY_CHECK_GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python -m slay_check.github_action
```

## Step 4: Configure Slay Check (Optional)

Create `slay-check.yaml` in your repository root to customize behavior.

### Choose what gets reviewed

**Preset** (one word):

```yaml
# One of: full (default), standard, minimal, security, performance
review_preset: security
```

**Or focus** (only these criteria):

```yaml
review_focus:
  - security
  - performance
  - complexity
```

**Environment variables:** `SLAY_CHECK_REVIEW_PRESET=security` or `SLAY_CHECK_REVIEW_FOCUS=security,performance`

### Full configuration (optional)

```yaml
# AI Provider Configuration
ai_provider: openai  # Options: openai, anthropic, google, perplexity, cursor, http, custom_http
ai_model: gpt-4o     # Default: gpt-4o

# Review: use preset/focus above, or set each criterion explicitly
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
  - "*.pyc"

# Performance Limits (defaults: 10000, 50)
max_file_size: 10000
max_files_per_pr: 50

# Behavior (defaults: false, false)
verbose: false
dry_run: false

# Review Thresholds (defaults: 6.0, 3)
min_score_threshold: 6.0
critical_issues_limit: 3
```

**Defaults:** If you omit `review_preset` and `review_focus`, all criteria are enabled (full review). See [README Configuration](https://github.com/prathameshap/slay-check#configuration) for the full default values table.

## Step 5: Test Your Setup

1. Create a test pull request in your repository
2. Check the **Actions** tab to see Slay Check running
3. Look for review comments on your PR
4. Check the workflow logs if there are any issues

## Advanced Configurations

### Multi-Provider Setup

Use different AI providers for different types of reviews:

```yaml
# In your workflow, you can set different providers:
- name: Security Review
  env:
    SLAY_CHECK_AI_PROVIDER: anthropic
    SLAY_CHECK_AI_TOKEN: ${{ secrets.ANTHROPIC_API_KEY }}
    
- name: Performance Review  
  env:
    SLAY_CHECK_AI_PROVIDER: openai
    SLAY_CHECK_AI_TOKEN: ${{ secrets.OPENAI_API_KEY }}
```

### Environment-Specific Reviews

Different settings for different branches:

```yaml
# Development branch - more lenient
- name: Development Review
  if: github.ref != 'refs/heads/main'
  env:
    SLAY_CHECK_MIN_SCORE_THRESHOLD: 5.0
    SLAY_CHECK_CRITICAL_ISSUES_LIMIT: 10
    SLAY_CHECK_DRY_RUN: true

# Main branch - strict
- name: Production Review
  if: github.ref == 'refs/heads/main'
  env:
    SLAY_CHECK_MIN_SCORE_THRESHOLD: 7.0
    SLAY_CHECK_CRITICAL_ISSUES_LIMIT: 2
    SLAY_CHECK_DRY_RUN: false
```

## Troubleshooting

### Common Issues

#### 1. "AI token is required"
- Check that `SLAY_CHECK_AI_TOKEN` is set in repository secrets
- Verify the token is valid and has proper permissions

#### 2. "Repository not found"
- For private repositories, ensure `SLAY_CHECK_TOKEN` is set
- Check that the repository name is correct in the workflow

#### 3. "Permission denied"
- Verify GitHub token has `repo` scope
- Check that the token hasn't expired

#### 4. "No files to review"
- Check exclude patterns in configuration
- Verify files aren't too large (exceed `max_file_size`)
- Ensure files have actual code changes

### Debug Mode

Enable verbose logging to troubleshoot:

```yaml
env:
  SLAY_CHECK_VERBOSE: true
```

### Dry Run Mode

Test without posting comments:

```yaml
env:
  SLAY_CHECK_DRY_RUN: true
```

## Local Development

Install Slay Check locally for testing:

```bash
# Install from GitHub
pip install git+https://x-access-token:${{ secrets.GITHUB_TOKEN }}@github.com/prathameshap/slay-check.git

# Or install from your fork
pip install git+https://x-access-token:${{ secrets.GITHUB_TOKEN }}@github.com/prathameshap/slay-check.git

# Initialize configuration
slay-check config init

# Review a specific PR
slay-check review --pr 123 --repo owner/repo
```

## Support

- **Issues**: [GitHub Issues](https://github.com/prathameshap/slay-check/issues)
- **Documentation**: [GitHub Wiki](https://github.com/prathameshap/slay-check/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/prathameshap/slay-check/discussions)

## Next Steps

- Customize review criteria for your team
- Set up different configurations for different environments
- Contribute improvements back to the main repository
- Share your custom configurations with the community
