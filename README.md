# Slay Check

> AI-powered code review tool for GitHub Actions and local development

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-ready-orange.svg)](.github/workflows)

Slay Check provides intelligent code reviews using multiple AI providers (OpenAI, Anthropic, Google AI) with configurable analysis criteria including problem analysis, algorithm review, complexity assessment, and risk evaluation.

## Features

- ** Multi-AI Support**: OpenAI GPT-4, Anthropic Claude, Google Gemini
- ** GitHub Actions Ready**: Automated PR reviews
- ** CLI Interface**: Local development support
- ** Configurable Analysis**: Customize review criteria
- ** Comprehensive Scoring**: Detailed feedback with actionable suggestions
- ** Security Focused**: Built-in security and risk assessment

##  Quick Start

### GitHub Actions

1. **Add workflow** (`.github/workflows/slay-check.yml`):

```yaml
name: Slay Check
on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install git+https://github.com/prathameshap/slay-check.git
      - run: python -m slay_check.github_action
        env:
          SLAY_CHECK_AI_TOKEN: ${{ secrets.SLAY_CHECK_AI_TOKEN }}
          SLAY_CHECK_GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

2. **Add secrets**:
   - `SLAY_CHECK_AI_TOKEN`: Your AI provider API key

### Local Development

```bash
# Install
pip install git+https://github.com/prathameshap/slay-check.git

# Configure
export SLAY_CHECK_AI_TOKEN="your-token"

# Review local changes
python -m slay_check.cli review --local
```

## ⚙️ Configuration

Create `slay-check.yaml` in your repository:

```yaml
# AI Provider
ai_provider: openai  # openai, anthropic, google
ai_model: gpt-4o     # Model to use

# Analysis Criteria
review_criteria:
  analyze_problem: true      # Problem analysis
  algorithm_analysis: true   # Algorithm review
  best_approaches: true      # Alternative approaches
  complexity_analysis: true # Time/space complexity
  risk_assessment: true     # Risk evaluation
  security_review: true     # Security analysis
  performance_review: true  # Performance analysis

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

## AI Providers

| Provider | Models | Best For |
|----------|--------|----------|
| **OpenAI** | GPT-4o, GPT-4, GPT-3.5-turbo | General code review |
| **Anthropic** | Claude-3-Sonnet, Claude-3-Opus | Security analysis |
| **Google AI** | Gemini-Pro | Performance optimization |

## Documentation

- **[Setup Guide](docs/setup-guide.md)** - Complete installation instructions
- **[GitHub Actions](docs/github-action.md)** - Workflow configuration
- **[Local Development](docs/local-development.md)** - CLI usage
- **[Forking Guide](docs/forking-guide.md)** - Custom implementations
- **[AI Response Control](docs/ai-response-control.md)** - Token limits & strictness

## Development

```bash
# Clone and install
git clone https://github.com/prathameshap/slay-check.git
cd slay-check
pip install -e .

# Run tests
pytest

# Build package
python -m build
```

## Performance

- **Startup Time**: <1 second
- **Small PR** (1-5 files): <90 seconds
- **Medium PR** (5-15 files): <4 minutes
- **Large PR** (15+ files): <12 minutes
- **Memory Usage**: <500MB peak

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/prathameshap/slay-check/issues)
- **Discussions**: [GitHub Discussions](https://github.com/prathameshap/slay-check/discussions)

---

**Built with a vibe for the developer community**