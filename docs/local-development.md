# Local Development Guide

This guide covers how to use Slay Check for local development and testing.

## Prerequisites

- Go 1.21 or later
- Git
- AI provider API token (OpenAI, Anthropic, etc.)
- GitHub personal access token (for PR reviews)

## Installation

### Option 1: Build from Source

```bash
git clone https://github.com/slay-check/slay-check.git
cd slay-check
go build -o slay-check ./cmd/slay-check
```

### Option 2: Install via Go

```bash
go install github.com/slay-check/slay-check@latest
```

## Configuration

### 1. Initialize Configuration

```bash
slay-check config init
```

This creates a `slay-check.yaml` file in your current directory.

### 2. Set Environment Variables

```bash
export SLAY_CHECK_AI_TOKEN="your-ai-token"
export SLAY_CHECK_GITHUB_TOKEN="your-github-token"
```

Or create a `.env` file:

```bash
SLAY_CHECK_AI_TOKEN=your-ai-token
SLAY_CHECK_GITHUB_TOKEN=your-github-token
```

### 3. Customize Configuration

Edit `slay-check.yaml` to match your preferences:

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
  - "testdata/*"

max_file_size: 5000
max_files_per_pr: 20
verbose: true
dry_run: true  # Don't post comments during development
```

## Usage

### Review Local Changes

Review your current git changes:

```bash
slay-check review --local
```

This will:
1. Get the current git diff
2. Analyze changed files
3. Display review results
4. Not post any comments (dry run mode)

### Review Specific Pull Request

```bash
slay-check review --pr 123 --repo owner/repo
```

### Review with Custom Branches

```bash
slay-check review --base main --head feature-branch
```

### Verbose Output

Get detailed information about the review process:

```bash
slay-check review --pr 123 --verbose
```

## Development Workflow

### 1. Make Changes

```bash
git checkout -b feature/new-feature
# Make your changes
git add .
git commit -m "Add new feature"
```

### 2. Review Before Push

```bash
slay-check review --local
```

### 3. Push and Create PR

```bash
git push origin feature/new-feature
# Create PR on GitHub
```

### 4. Review PR

```bash
slay-check review --pr 123 --repo owner/repo
```

## Configuration Examples

### Development Configuration

```yaml
ai_provider: openai
review_criteria:
  analyze_problem: true
  algorithm_analysis: true
  best_approaches: true
  complexity_analysis: true
  risk_assessment: true
  security_review: false      # Skip security review in dev
  performance_review: true
exclude_patterns:
  - "*.md"
  - "*.txt"
  - "vendor/*"
  - "testdata/*"
max_file_size: 5000
max_files_per_pr: 20
verbose: true
dry_run: true
min_score_threshold: 5.0
critical_issues_limit: 10
```

### Production Configuration

```yaml
ai_provider: openai
review_criteria:
  analyze_problem: true
  algorithm_analysis: true
  best_approaches: true
  complexity_analysis: true
  risk_assessment: true
  security_review: true       # Enable security review
  performance_review: true
exclude_patterns:
  - "*.md"
  - "*.txt"
  - "vendor/*"
  - "node_modules/*"
  - "*.min.js"
  - "*.min.css"
max_file_size: 10000
max_files_per_pr: 50
verbose: false
dry_run: false
min_score_threshold: 7.0
critical_issues_limit: 3
```

### Security-Focused Configuration

```yaml
ai_provider: anthropic       # Use Claude for security
review_criteria:
  analyze_problem: true
  algorithm_analysis: false
  best_approaches: true
  complexity_analysis: false
  risk_assessment: true
  security_review: true       # Focus on security
  performance_review: false
exclude_patterns:
  - "*.md"
  - "*.txt"
  - "vendor/*"
  - "testdata/*"
max_file_size: 15000
max_files_per_pr: 30
verbose: true
dry_run: false
min_score_threshold: 8.0
critical_issues_limit: 1
```

## Troubleshooting

### Common Issues

#### 1. "AI token is required"

Make sure you've set the `SLAY_CHECK_AI_TOKEN` environment variable:

```bash
export SLAY_CHECK_AI_TOKEN="your-token"
```

#### 2. "GitHub token is required"

Set the `SLAY_CHECK_GITHUB_TOKEN` environment variable:

```bash
export SLAY_CHECK_GITHUB_TOKEN="your-token"
```

#### 3. "Provider not found"

Check your `ai_provider` setting in `slay-check.yaml`. Supported providers:
- `openai`
- `anthropic`

#### 4. "No files to review"

This can happen if:
- All files are excluded by patterns
- Files are too large (exceed `max_file_size`)
- No changes detected

Check your configuration and try with `--verbose` flag.

#### 5. API Rate Limits

If you hit rate limits:
- Reduce `max_files_per_pr`
- Increase delays between requests
- Use a different AI provider

### Debug Mode

Enable debug logging:

```bash
export SLAY_CHECK_VERBOSE=true
slay-check review --pr 123 --verbose
```

### Dry Run Mode

Test without posting comments:

```bash
export SLAY_CHECK_DRY_RUN=true
slay-check review --pr 123
```

## Best Practices

### 1. Use Dry Run for Development

Always use `dry_run: true` when developing locally to avoid posting comments.

### 2. Set Appropriate Limits

Adjust `max_file_size` and `max_files_per_pr` based on your project size.

### 3. Exclude Unnecessary Files

Add patterns to `exclude_patterns` to skip files that don't need review.

### 4. Use Different Configurations

Create different configurations for different environments (dev, staging, prod).

### 5. Monitor Performance

Use `--verbose` flag to monitor review performance and identify bottlenecks.

## Integration with IDEs

### VS Code

Add to your VS Code settings:

```json
{
  "terminal.integrated.env.osx": {
    "SLAY_CHECK_AI_TOKEN": "your-token",
    "SLAY_CHECK_GITHUB_TOKEN": "your-token"
  }
}
```

### JetBrains IDEs

Add environment variables in Run/Debug configurations.

## Scripts and Automation

### Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
slay-check review --local
if [ $? -ne 0 ]; then
  echo "Review failed. Please fix issues before committing."
  exit 1
fi
```

### CI/CD Integration

Use in your CI pipeline:

```yaml
- name: Run Slay Check
  run: |
    slay-check review --pr ${{ github.event.pull_request.number }} --repo ${{ github.repository }}
```
