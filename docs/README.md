# Slay Check - AI Code Review Tool

A high-performance, modular AI code review tool designed for GitHub Actions and local development. Built with Python for excellent AI ecosystem support and rapid development.

## 🚀 Features

- **🤖 Multi-AI Provider Support**: OpenAI, Anthropic, Google AI, and more
- **⚡ Fast Development**: Built with Python for rapid development and maintenance
- **🔧 Configurable Review Criteria**: Customize review parameters via YAML
- **🚀 GitHub Actions Ready**: Seamless integration with GitHub workflows
- **💻 CLI Support**: Run reviews locally during development
- **📊 Comprehensive Analysis**: Code quality, complexity, security, and best practices
- **🎯 Smart Filtering**: Exclude files and patterns you don't want reviewed
- **📈 Performance Limits**: Control file size and count limits
- **🎚️ Score Thresholds**: Set minimum scores and issue limits

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [GitHub Actions](#github-actions)
- [CLI Commands](#cli-commands)
- [AI Providers](#ai-providers)
- [Performance](#performance)
- [Contributing](#contributing)
- [License](#license)

## 🏃 Quick Start

### GitHub Actions Setup

1. **Add the workflow** to `.github/workflows/slay-check.yml`:

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

2. **Add secrets** to your repository:
   - `SLAY_CHECK_AI_TOKEN`: Your AI provider API token
   - `GITHUB_TOKEN`: Automatically provided by GitHub Actions

3. **Create configuration** file `slay-check.yaml` in your repository root:

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
```

### Local Development

```bash
# Install
pip install git+https://github.com/YOUR_USERNAME/slay-check.git

# Initialize configuration
slay-check config init

# Review current changes
slay-check review --local

# Review specific PR
slay-check review --pr 123 --repo owner/repo
```

## 📦 Installation

### From Source

```bash
git clone https://github.com/YOUR_USERNAME/slay-check.git
cd slay-check
pip install -e .
```

### Using pip

```bash
pip install git+https://github.com/YOUR_USERNAME/slay-check.git
```

### Using GitHub Releases

Download the latest release from [GitHub Releases](https://github.com/YOUR_USERNAME/slay-check/releases).

## ⚙️ Configuration

### Configuration File

Create `slay-check.yaml` in your repository root or home directory:

```yaml
# AI Provider Configuration
ai_provider: openai  # Options: openai, anthropic, google
ai_token: ""  # Set via environment variable SLAY_CHECK_AI_TOKEN

# GitHub Configuration  
github_token: ""  # Set via environment variable SLAY_CHECK_GITHUB_TOKEN

# Review Criteria - Enable/disable specific analysis types
review_criteria:
  analyze_problem: true      # Analyze the problem the code is solving
  algorithm_analysis: true   # Analyze the algorithm used for the logic
  best_approaches: true      # Suggest plausible best approaches
  complexity_analysis: true  # Analyze time and space complexity
  risk_assessment: true      # Identify risks and potential issues
  security_review: true      # Review for security vulnerabilities
  performance_review: true   # Review for performance issues

# File Filtering
exclude_patterns:
  - "*.md"                    # Exclude markdown files
  - "*.txt"                   # Exclude text files
  - "vendor/*"                # Exclude vendor directories
  - "node_modules/*"          # Exclude node modules
  - "*.min.js"                # Exclude minified JavaScript
  - "*.min.css"               # Exclude minified CSS
  - "*.lock"                  # Exclude lock files
  - "*.log"                   # Exclude log files
  - "*.tmp"                   # Exclude temporary files
  - "testdata/*"              # Exclude test data
  - "__pycache__/*"           # Exclude Python cache
  - "*.pyc"                   # Exclude Python bytecode

# Performance Limits
max_file_size: 10000          # Maximum lines per file to review
max_files_per_pr: 50          # Maximum files per PR to review

# Behavior
verbose: false                # Enable verbose logging
dry_run: false                # Don't post comments, just show results

# AI Model Configuration (optional)
ai_model: ""                  # Override default model
max_tokens: 4000              # Maximum tokens for AI response
temperature: 0.3              # AI response temperature (0.0-1.0)

# Review Thresholds
min_score_threshold: 6.0       # Minimum score to pass review
critical_issues_limit: 3      # Maximum critical issues allowed
```

### Environment Variables

- `SLAY_CHECK_AI_PROVIDER`: AI provider to use
- `SLAY_CHECK_AI_TOKEN`: AI provider API token
- `SLAY_CHECK_GITHUB_TOKEN`: GitHub personal access token
- `SLAY_CHECK_VERBOSE`: Enable verbose logging
- `SLAY_CHECK_DRY_RUN`: Don't post comments, just show results

## 🎯 Usage

### CLI Commands

#### Review Commands

```bash
# Review local changes (git diff)
slay-check review --local

# Review specific pull request
slay-check review --pr 123 --repo owner/repo

# Review with custom base/head
slay-check review --base main --head feature-branch

# Review with verbose output
slay-check review --pr 123 --verbose
```

#### Configuration Commands

```bash
# Initialize configuration file
slay-check config init

# Show current configuration
slay-check config show

# Show version information
slay-check version
```

### GitHub Actions

The tool automatically runs on pull requests when configured. See [GitHub Actions Documentation](docs/github-action.md) for detailed setup instructions.

## 🤖 AI Providers

### OpenAI

```yaml
ai_provider: openai
ai_token: "sk-..."
```

**Models:**
- `gpt-4` (default)
- `gpt-4-turbo`
- `gpt-3.5-turbo`

### Anthropic Claude

```yaml
ai_provider: anthropic
ai_token: "sk-ant-..."
```

**Models:**
- `claude-3-sonnet-20240229` (default)
- `claude-3-opus-20240229`
- `claude-3-haiku-20240307`

### Google AI

```yaml
ai_provider: google
ai_token: "your-google-ai-key"
```

**Models:**
- `gemini-pro` (default)
- `gemini-pro-vision`

### Adding Custom Providers

You can extend the tool by implementing the `AIProvider` interface:

```python
from slay_check.ai.base import AIProvider, ReviewRequest, ReviewResponse

class CustomProvider(AIProvider):
    def get_name(self) -> str:
        return "custom"
    
    def is_available(self) -> bool:
        return True
    
    def review_code(self, request: ReviewRequest) -> ReviewResponse:
        # Your implementation
        return ReviewResponse(
            analysis="Custom AI analysis",
            score=8.5,
            issues=[],
            suggestions=[],
            complexity=Complexity(),
            confidence=0.8
        )
```

## 📊 Performance

### Benchmarks

| Language | Startup Time | Memory Usage | Execution Speed |
|----------|-------------|--------------|-----------------|
| **Python** | 200-1000ms | 50-150MB | Moderate |
| Go | 20-100ms | 10-30MB | Very Fast |
| Node.js | 100-500ms | 30-80MB | Fast |

### Performance Targets

- **Startup Time**: <1 second
- **Small PR** (1-5 files, <200 lines): <90 seconds
- **Medium PR** (5-15 files, 200-1000 lines): <4 minutes
- **Large PR** (15+ files, 1000+ lines): <12 minutes
- **Memory Usage**: <500MB peak

### Optimization Features

- **Async Processing**: Analyze multiple files simultaneously
- **Chunking**: Split large files into smaller chunks for AI
- **Caching**: Cache similar code patterns
- **Incremental Analysis**: Only analyze changed lines
- **Smart Filtering**: Skip files that don't need review

## 🔧 Development

### Project Structure

```
slay-check/
├── slay_check/              # Python package
│   ├── __init__.py
│   ├── cli.py               # CLI interface
│   ├── config.py            # Configuration management
│   ├── github.py            # GitHub API integration
│   ├── review.py            # Review engine
│   ├── github_action.py     # GitHub Action entry point
│   └── ai/                  # AI provider implementations
│       ├── __init__.py
│       ├── base.py          # Base AI provider interface
│       ├── openai.py        # OpenAI implementation
│       ├── anthropic.py     # Anthropic implementation
│       └── google.py        # Google AI implementation
├── tests/                   # Tests
├── config/                  # Configuration examples
├── docs/                    # Documentation
├── pyproject.toml          # Project configuration
├── requirements.txt        # Dependencies
└── .github/workflows/       # GitHub Actions
```

### Building

```bash
# Install in development mode
pip install -e .

# Build package
python -m build

# Install from built package
pip install dist/slay_check-*.whl
```

### Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=slay_check

# Run specific test file
pytest tests/test_config.py
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code Style

- Follow Python conventions (PEP 8)
- Use `black` for formatting
- Add tests for new features
- Update documentation

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/slay-check/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/slay-check/discussions)
- **Documentation**: [GitHub Wiki](https://github.com/YOUR_USERNAME/slay-check/wiki)

## 🙏 Acknowledgments

- Built with [Python](https://python.org/)
- Uses [GitHub API](https://docs.github.com/en/rest)
- Supports [OpenAI API](https://platform.openai.com/)
- Supports [Anthropic API](https://docs.anthropic.com/)
- Supports [Google AI API](https://ai.google.dev/)
- Inspired by modern code review practices