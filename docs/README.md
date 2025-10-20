# Slay Check - AI Code Review Tool

A high-performance, modular AI code review tool designed for GitHub Actions and local development. Built with Go for optimal speed and memory efficiency.

## 🚀 Features

- **🤖 Multi-AI Provider Support**: OpenAI, Anthropic, Google AI, and more
- **⚡ High Performance**: Built with Go for optimal speed and memory efficiency
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
go install github.com/slay-check/slay-check@latest

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
git clone https://github.com/slay-check/slay-check.git
cd slay-check
go build -o slay-check ./cmd/slay-check
```

### Using Go Install

```bash
go install github.com/slay-check/slay-check@latest
```

### Using GitHub Releases

Download the latest release from [GitHub Releases](https://github.com/slay-check/slay-check/releases).

## ⚙️ Configuration

### Configuration File

Create `slay-check.yaml` in your repository root or home directory:

```yaml
# AI Provider Configuration
ai_provider: openai  # Options: openai, anthropic
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

### Adding Custom Providers

You can extend the tool by implementing the `ai.Provider` interface:

```go
type CustomProvider struct {
    // Your implementation
}

func (p *CustomProvider) ReviewCode(ctx context.Context, request ai.ReviewRequest) (*ai.ReviewResponse, error) {
    // Your implementation
}

func (p *CustomProvider) GetName() string {
    return "custom"
}

func (p *CustomProvider) IsAvailable() bool {
    return true
}
```

## 📊 Performance

### Benchmarks

| Language | Startup Time | Memory Usage | Execution Speed |
|----------|-------------|--------------|-----------------|
| **Go** | 20-100ms | 10-30MB | Very Fast |
| Python | 200-1000ms | 50-150MB | Moderate |
| Node.js | 100-500ms | 30-80MB | Fast |

### Performance Targets

- **Startup Time**: <100ms
- **Small PR** (1-5 files, <200 lines): <60 seconds
- **Medium PR** (5-15 files, 200-1000 lines): <3 minutes
- **Large PR** (15+ files, 1000+ lines): <8 minutes
- **Memory Usage**: <300MB peak

### Optimization Features

- **Parallel Processing**: Analyze multiple files simultaneously
- **Chunking**: Split large files into smaller chunks for AI
- **Caching**: Cache similar code patterns
- **Incremental Analysis**: Only analyze changed lines
- **Smart Filtering**: Skip files that don't need review

## 🔧 Development

### Project Structure

```
slay-check/
├── cmd/
│   ├── slay-check/          # CLI application
│   └── github-action/       # GitHub Action entry point
├── internal/
│   ├── ai/                  # AI provider implementations
│   ├── cli/                 # CLI interface
│   ├── config/              # Configuration management
│   ├── github/              # GitHub API integration
│   └── review/              # Review engine
├── config/                  # Configuration examples
├── docs/                    # Documentation
├── tests/                   # Tests
└── .github/workflows/       # GitHub Actions
```

### Building

```bash
# Build CLI
go build -o slay-check ./cmd/slay-check

# Build GitHub Action
go build -o slay-check ./cmd/github-action

# Build all
make build
```

### Testing

```bash
# Run tests
go test ./...

# Run tests with coverage
go test -cover ./...

# Run integration tests
go test -tags=integration ./...
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

- Follow Go conventions
- Use `gofmt` for formatting
- Add tests for new features
- Update documentation

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/slay-check/slay-check/issues)
- **Discussions**: [GitHub Discussions](https://github.com/slay-check/slay-check/discussions)
- **Documentation**: [GitHub Wiki](https://github.com/slay-check/slay-check/wiki)

## 🙏 Acknowledgments

- Built with [Go](https://golang.org/)
- Uses [GitHub API](https://docs.github.com/en/rest)
- Supports [OpenAI API](https://platform.openai.com/)
- Supports [Anthropic API](https://docs.anthropic.com/)
- Inspired by modern code review practices
