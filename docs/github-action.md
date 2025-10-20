# Slay Check GitHub Action

A GitHub Action for automated AI-powered code review using Slay Check.

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
          
      - name: Set up Go
        uses: actions/setup-go@v4
        with:
          go-version: '1.21'
          
      - name: Build Slay Check
        run: |
          go mod download
          go build -o slay-check ./cmd/github-action
          
      - name: Run Slay Check
        env:
          GITHUB_REPOSITORY: ${{ github.repository }}
          GITHUB_PR_NUMBER: ${{ github.event.pull_request.number }}
          SLAY_CHECK_AI_TOKEN: ${{ secrets.SLAY_CHECK_AI_TOKEN }}
          SLAY_CHECK_GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          ./slay-check
```

### Required Secrets

Add these secrets to your repository:

- `SLAY_CHECK_AI_TOKEN`: Your AI provider API token (OpenAI, Anthropic, etc.)
- `GITHUB_TOKEN`: Automatically provided by GitHub Actions

### Optional Variables

You can set these as repository variables:

- `SLAY_CHECK_AI_PROVIDER`: AI provider to use (default: `openai`)
- `SLAY_CHECK_VERBOSE`: Enable verbose logging (default: `false`)
- `SLAY_CHECK_DRY_RUN`: Don't post comments, just show results (default: `false`)

### Configuration

Create a `slay-check.yaml` file in your repository root to customize the review criteria:

```yaml
ai_provider: openai
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

## Features

- **Automated Reviews**: Runs on every pull request
- **Configurable Criteria**: Customize what gets reviewed
- **Multiple AI Providers**: Support for OpenAI, Anthropic, and more
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
