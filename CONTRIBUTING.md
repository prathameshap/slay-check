# Contributing to Slay Check

Thank you for your interest in contributing to Slay Check! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Process](#contributing-process)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Guidelines](#documentation-guidelines)
- [Release Process](#release-process)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

## Getting Started

### Prerequisites

- Go 1.21 or later
- Git
- Make (optional, for build scripts)
- Docker (for testing)

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/slay-check.git
   cd slay-check
   ```

2. **Set up development environment**
   ```bash
   go mod download
   go build ./...
   ```

3. **Run tests**
   ```bash
   go test ./...
   ```

4. **Set up environment variables**
   ```bash
   export SLAY_CHECK_AI_TOKEN="your-test-token"
   export SLAY_CHECK_GITHUB_TOKEN="your-test-token"
   ```

## Contributing Process

### 1. Create an Issue

Before starting work, please create an issue to discuss:
- Bug reports
- Feature requests
- Performance improvements
- Documentation updates

### 2. Fork and Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 3. Make Changes

Follow the [Code Style Guidelines](#code-style-guidelines) and [Testing Guidelines](#testing-guidelines).

### 4. Test Your Changes

```bash
# Run all tests
go test ./...

# Run tests with coverage
go test -cover ./...

# Run integration tests
go test -tags=integration ./...

# Test CLI
go build -o slay-check ./cmd/slay-check
./slay-check --help

# Test GitHub Action
go build -o slay-check ./cmd/github-action
```

### 5. Update Documentation

Update relevant documentation:
- README.md
- API documentation
- Configuration examples
- User guides

### 6. Commit Changes

Use conventional commit messages:

```
feat: add support for custom AI providers
fix: resolve memory leak in review engine
docs: update installation instructions
test: add unit tests for config validation
```

### 7. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Create a pull request with:
- Clear description of changes
- Reference to related issues
- Screenshots (if applicable)
- Test results

## Code Style Guidelines

### Go Style

- Follow [Effective Go](https://golang.org/doc/effective_go.html)
- Use `gofmt` for formatting
- Use `golint` for linting
- Use `go vet` for static analysis

### Naming Conventions

- Use descriptive names
- Use camelCase for variables and functions
- Use PascalCase for exported types and functions
- Use snake_case for configuration keys

### Error Handling

```go
// Good
if err != nil {
    return fmt.Errorf("failed to process file %s: %w", filename, err)
}

// Bad
if err != nil {
    return err
}
```

### Documentation

- Document all exported functions
- Use Go doc comments
- Include examples for complex functions

```go
// ProcessFile processes a file and returns the result.
// It handles various file formats and returns an error if processing fails.
//
// Example:
//   result, err := ProcessFile("example.go")
//   if err != nil {
//       log.Fatal(err)
//   }
func ProcessFile(filename string) (*Result, error) {
    // implementation
}
```

## Testing Guidelines

### Unit Tests

- Write tests for all new functionality
- Aim for >80% code coverage
- Use table-driven tests where appropriate
- Mock external dependencies

```go
func TestProcessFile(t *testing.T) {
    tests := []struct {
        name     string
        filename string
        want     *Result
        wantErr  bool
    }{
        {
            name:     "valid file",
            filename: "test.go",
            want:     &Result{Success: true},
            wantErr:  false,
        },
        {
            name:     "invalid file",
            filename: "nonexistent.go",
            want:     nil,
            wantErr:  true,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := ProcessFile(tt.filename)
            if (err != nil) != tt.wantErr {
                t.Errorf("ProcessFile() error = %v, wantErr %v", err, tt.wantErr)
                return
            }
            if !reflect.DeepEqual(got, tt.want) {
                t.Errorf("ProcessFile() = %v, want %v", got, tt.want)
            }
        })
    }
}
```

### Integration Tests

- Test with real AI providers (use test tokens)
- Test GitHub API integration
- Test end-to-end workflows

```go
//go:build integration

func TestReviewPullRequest(t *testing.T) {
    // Integration test implementation
}
```

### Test Data

- Use realistic test data
- Include edge cases
- Use fixtures for complex data

## Documentation Guidelines

### README Updates

- Update feature lists
- Update installation instructions
- Update usage examples
- Update configuration examples

### API Documentation

- Document all public APIs
- Include parameter descriptions
- Include return value descriptions
- Include error conditions

### Configuration Documentation

- Document all configuration options
- Include examples
- Include default values
- Include validation rules

## Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version bumped
- [ ] Release notes prepared
- [ ] GitHub release created

### Creating a Release

1. Update version in `go.mod`
2. Update changelog
3. Create release branch
4. Create GitHub release
5. Tag release
6. Update documentation

## Areas for Contribution

### High Priority

- **New AI Providers**: Add support for more AI providers
- **Performance Improvements**: Optimize memory usage and speed
- **Better Error Handling**: Improve error messages and recovery
- **More Review Criteria**: Add new analysis types
- **UI Improvements**: Better CLI output and formatting

### Medium Priority

- **Configuration Validation**: Better config validation
- **Caching**: Implement intelligent caching
- **Parallel Processing**: Improve concurrent processing
- **Metrics**: Add performance metrics
- **Plugins**: Plugin system for extensions

### Low Priority

- **Web Interface**: Web-based configuration
- **Database Integration**: Store review history
- **Notifications**: Slack/email notifications
- **Custom Rules**: User-defined review rules

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/slay-check/slay-check/issues)
- **Discussions**: [GitHub Discussions](https://github.com/slay-check/slay-check/discussions)
- **Discord**: [Slay Check Discord](https://discord.gg/slay-check)

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

Thank you for contributing to Slay Check! 🚀
