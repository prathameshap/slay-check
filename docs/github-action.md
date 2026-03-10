# Slay Check GitHub Action

A GitHub Action for automated AI-powered code review using Slay Check. All review feedback is posted as a single comment on the PR.

## Usage

### Basic Setup

Create `.github/workflows/slay-check.yml` in your repository:

```yaml
name: Slay Check - AI Code Review
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  slay-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install Slay Check
        run: |
          pip install git+https://x-access-token:${{ secrets.GITHUB_TOKEN }}@github.com/prathameshap/slay-check.git
          
      - name: Run Slay Check
        env:
          GITHUB_REPOSITORY: ${{ github.repository }}
          GITHUB_PR_NUMBER: ${{ github.event.pull_request.number }}
          SLAY_CHECK_AI_TOKEN: ${{ secrets.SLAY_CHECK_AI_TOKEN }}
          SLAY_CHECK_GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python -m slay_check.github_action
```

### Required Secrets

Add these secrets to your repository:

- `SLAY_CHECK_AI_TOKEN`: Your AI provider API token (OpenAI, Anthropic, Google AI)
- `GITHUB_TOKEN`: Automatically provided by GitHub Actions

### Optional Variables

You can set these as repository variables:

- `SLAY_CHECK_AI_PROVIDER`: AI provider to use (default: `openai`)  
  - Supported values: `openai`, `anthropic`, `google`, `perplexity`, `cursor`, `http` (custom HTTP endpoint)
- `SLAY_CHECK_AI_MODEL`: Model name/ID for the chosen provider (e.g. `gpt-4o`, `claude-3-sonnet-20240229`, `gemini-pro`, `sonar-pro` for Perplexity)
- `SLAY_CHECK_AI_BASE_URL`: Custom API base URL (used for OpenAI-/Anthropic-compatible or custom HTTP endpoints)
- `SLAY_CHECK_VERBOSE`: Enable verbose logging (default: `false`)
- `SLAY_CHECK_DRY_RUN`: Don't post comments, just show results (default: `false`)
- `SLAY_CHECK_REVIEW_PRESET`: Preset for what to review: `full`, `standard`, `minimal`, `security`, `performance` (default: full)
- `SLAY_CHECK_REVIEW_FOCUS`: Comma-separated criteria to enable, e.g. `security,performance` (overrides preset if both set)

### Configuration

Create a `slay-check.yaml` file in your repository root to customize the review criteria and provider.

**Easy: preset or focus**

```yaml
# One-word preset: full | standard | minimal | security | performance
review_preset: security
```

Or choose only the areas you want:

```yaml
review_focus:
  - security
  - performance
  - complexity
```

**Full control:** set each criterion explicitly:

```yaml
ai_provider: openai  # openai | anthropic | google | perplexity | cursor | http
review_criteria:
  analyze_problem: true
  algorithm_analysis: true
  best_approaches: true
  complexity_analysis: true
  risk_assessment: true
  security_review: true
  performance_review: true

exclude_patterns:
  - "*.md"
  - "*.txt"
  - "vendor/*"
  - "node_modules/*"

max_file_size: 10000
max_files_per_pr: 50
min_score_threshold: 6.0
critical_issues_limit: 3
```

**Defaults:** If you omit `review_preset` and `review_focus`, all review criteria are enabled (full review). Defaults include `ai_provider: openai`, `ai_model: gpt-4o`, `max_tokens: 4000`, `temperature: 0.3`, `min_score_threshold: 6.0`, `critical_issues_limit: 3`, `max_file_size: 10000`, `max_files_per_pr: 50`. See [README Configuration](https://github.com/prathameshap/slay-check#configuration) for the full default values table.

#### Perplexity

Use [Perplexity AI](https://docs.perplexity.ai/) for code review (same API shape as OpenAI):

```yaml
ai_provider: perplexity
ai_model: sonar-pro   # or sonar, sonar-deep-research, sonar-reasoning-pro
ai_token: <PERPLEXITY_API_KEY>
```

Set `SLAY_CHECK_AI_PROVIDER=perplexity` and `SLAY_CHECK_AI_MODEL=sonar-pro` (or use `slay-check.yaml` as above).

#### Cursor

Cursor does not expose a simple “chat completion” API; it offers [Cloud Agents](https://cursor.com/docs/cloud-agent/api/overview) for repo-level tasks. To use a Cursor-backed or internal gateway that returns Slay Check–style JSON, use the **Custom HTTP** provider:

```yaml
ai_provider: cursor
ai_base_url: https://your-cursor-gateway.example.com/review
ai_token: <your-token>
```

Slay Check will `POST` the same JSON as for [Custom HTTP](#custom-http-provider) and expect the same response shape.

#### Custom HTTP provider

To use a completely custom HTTP API for reviews, set:

```yaml
ai_provider: http
ai_base_url: https://your-internal-endpoint.example.com/review
ai_token: your-internal-api-token  # optional; sent as Authorization: Bearer <token>
```

Slay Check will POST JSON with this shape:

```json
{
  "code": "<string>",
  "language": "<string>",
  "file_path": "<string>",
  "context": "<string or null>",
  "criteria": { "analyze_problem": true, "...": true },
  "max_tokens": 4000,
  "temperature": 0.3
}
```

Your endpoint should return JSON in the standard review format:

```json
{
  "analysis": "Detailed analysis of the code",
  "score": 8.5,
  "issues": [
    {
      "type": "performance",
      "severity": "medium",
      "line": 10,
      "message": "Inefficient loop",
      "suggestion": "Use a more efficient algorithm",
      "confidence": 0.9
    }
  ],
  "suggestions": ["Suggestion 1", "Suggestion 2"],
  "complexity": {
    "time_complexity": "O(n²)",
    "space_complexity": "O(1)",
    "cyclomatic_complexity": 5,
    "maintainability": "good"
  },
  "confidence": 0.85
}
```

## Features

- **Single comment**: Full review (summary + per-file issues and suggestions) in one PR comment
- **Automated Reviews**: Runs on every pull request
- **Configurable Criteria**: Customize what gets reviewed
- **Multiple AI Providers**: OpenAI, Anthropic, Google AI, Perplexity, Cursor (custom HTTP), and any custom HTTP endpoint
- **Smart Filtering**: Exclude files and patterns you don't want reviewed
- **Performance Limits**: Control file size and count limits
- **Score Thresholds**: Set minimum scores and issue limits
- **Detailed Feedback**: Comprehensive analysis and suggestions

## Outputs

The action sets these outputs:

- `score`: Overall review score (0-10)
- `files_reviewed`: Number of files reviewed
- `issues_found`: Number of issues found
- `duration`: Review duration

## Failure Conditions

The action will fail if:

- Overall score is below `min_score_threshold`
- Number of critical issues exceeds `critical_issues_limit`
- AI API calls fail
- GitHub API calls fail

## Examples

### Security-Focused Review

```yaml
review_criteria:
  security_review: true
  risk_assessment: true
  analyze_problem: false
  algorithm_analysis: false
  best_approaches: true
  complexity_analysis: false
  performance_review: false

min_score_threshold: 8.0
critical_issues_limit: 1
```

### Performance-Focused Review

```yaml
review_criteria:
  performance_review: true
  algorithm_analysis: true
  complexity_analysis: true
  best_approaches: true
  security_review: false
  risk_assessment: false
  analyze_problem: false

max_file_size: 20000
max_files_per_pr: 100
```

### Development Mode

```yaml
verbose: true
dry_run: true
min_score_threshold: 5.0
critical_issues_limit: 10
```
