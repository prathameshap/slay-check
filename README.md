# Slay Check

> **Slay Check** — AI-powered code review for GitHub Actions and local development

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-AGPL%20v3%20%7C%20Apache%202.0%20%7C%20GPL%20v3-green.svg)](LICENSE-APACHE)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-ready-orange.svg)](.github/workflows)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/prathameshap/slay-check/badge)](https://scorecard.dev/viewer/?uri=github.com/prathameshap/slay-check)

**Slay Check** gives you a single, comprehensive AI review comment on every pull request. It supports multiple AI providers (OpenAI, Anthropic, Google AI) with configurable criteria: problem analysis, algorithm review, complexity, and risk evaluation.

## Features

- **Multi-AI Support**: OpenAI GPT-4, Anthropic Claude, Google Gemini
- **GitHub Actions Ready**: Automated PR reviews
- **Single comment**: Full review (summary + per-file details) in one PR comment
- **CLI Interface**: Local development support
- **Configurable Analysis**: Customize review criteria
- **Comprehensive Scoring**: Detailed feedback with actionable suggestions
- **Security Focused**: Built-in security and risk assessment

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
- **[Repo issues & technical debt](docs/REPO_ISSUES.md)** - Known issues and contribution ideas
- **[Rust conversion analysis](docs/RUST_CONVERSION_ANALYSIS.md)** - Why the project stays in Python
- **[Project & milestones](docs/project-and-milestones.md)** - How maintainers configure the GitHub Project and milestones
- **[Milestone issues](docs/milestone-issues.md)** - Copy-paste issue text for V 0.0.1, V 0.0.2, V 0.1.0
- **[Licensing](docs/licensing.md)** - Version-based open source and future-version terms

**Open source & project health:** Security and best-practice scores are tracked by [OpenSSF Scorecard](https://scorecard.dev/viewer/?uri=github.com/prathameshap/slay-check). Results run on every push to `main` and weekly; the badge above links to the latest report.

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

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines, including our **branching strategy** (same as [Zed](https://github.com/zed-industries/zed): single `main` branch, all changes via PRs). By participating, you agree to our [Code of Conduct](CODE_OF_CONDUCT.md).

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

**Slay Check** uses a conditional open source license:

- **Versions 1.0.0 and earlier** (including all 0.x.x pre-releases) are offered under a multi-license setup. You may use, modify, and distribute those versions under **any one** of:
  - **[GNU Affero General Public License v3](LICENSE-AGPL)** (AGPL-3.0)
  - **[Apache License 2.0](LICENSE-APACHE)** (Apache-2.0)
  - **[GNU General Public License v3](LICENSE-GPL)** (GPL-3.0)
- **Versions after 1.0.0** may be released under different terms. The copyright holder reserves the right to publish future versions under a commercial or other license; use of those versions will be subject to the terms announced for each release.

See the [LICENSE scope and full text](LICENSE-APACHE) in the repository.

## Security

Please report security issues as described in [SECURITY.md](SECURITY.md).

## Support

- **Issues**: [GitHub Issues](https://github.com/prathameshap/slay-check/issues)
- **Discussions**: [GitHub Discussions](https://github.com/prathameshap/slay-check/discussions)

---

**Slay Check** — built for the developer community
