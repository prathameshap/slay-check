# Slay Check - AI Code Review Tool

A high-performance, modular AI code review tool designed for GitHub Actions and local development.

## Features

- 🤖 **Multi-AI Provider Support**: OpenAI, Anthropic, Google AI, and more
- ⚡ **High Performance**: Built with Go for optimal speed and memory efficiency
- 🔧 **Configurable Review Criteria**: Customize review parameters via YAML
- 🚀 **GitHub Actions Ready**: Seamless integration with GitHub workflows
- 💻 **CLI Support**: Run reviews locally during development
- 📊 **Comprehensive Analysis**: Code quality, complexity, security, and best practices

## Quick Start

### GitHub Actions Setup

1. Create `.github/workflows/slay-check.yml`:

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
      - name: Run Slay Check
        uses: slay-check/slay-check@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          ai-provider: openai
          ai-token: ${{ secrets.OPENAI_API_KEY }}
```

2. Add your AI provider token to repository secrets

### Local Development

```bash
# Install
go install github.com/slay-check/slay-check@latest

# Run review on current changes
slay-check review

# Run review on specific PR
slay-check review --pr 123
```

## Configuration

Create `slay-check.yaml` in your repository root:

```yaml
ai_provider: openai
review_criteria:
  analyze_problem: true
  algorithm_analysis: true
  best_approaches: true
  complexity_analysis: true
  risk_assessment: true
  
exclude_patterns:
  - "*.md"
  - "*.txt"
  - "vendor/*"
  
max_file_size: 10000
max_files_per_pr: 50
```

## Supported AI Providers

- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google AI (Gemini)
- Azure OpenAI
- Custom API endpoints

## Performance

- **Startup Time**: <100ms
- **Small PR**: <60 seconds
- **Medium PR**: <3 minutes
- **Large PR**: <8 minutes
- **Memory Usage**: <300MB peak

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.