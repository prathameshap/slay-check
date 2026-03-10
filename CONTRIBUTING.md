# Contributing to Slay Check

Thank you for your interest in contributing to Slay Check! This document provides guidelines for contributing to the project.

## Branching strategy

We use the following branching model:

- **Single long-lived branch:** `main` is the default and only permanent branch. All releases and production code live on `main`.
- **All changes via pull requests:** No direct pushes to `main`. Create a branch from `main`, make your changes, then open a PR targeting `main`.
- **Branch naming:** Use short, descriptive branches such as `feature/short-description` or `fix/short-description`. Keep the change focused so the PR stays small.
- **Stay up to date:** Before opening or updating a PR, rebase (or merge) your branch on the latest `main` so the PR is clean and easy to review.

```bash
# Start from an up-to-date main
git fetch origin
git checkout main
git pull origin main

# Create your branch
git checkout -b feature/your-feature-name   # or fix/your-bug-fix

# After making changes, keep in sync with main
git fetch origin
git rebase origin/main   # or: git merge origin/main
```

## Quick Start

### Prerequisites

- Python 3.11+
- Git
- AI provider API key (for testing)

### Development Setup

```bash
# Fork and clone
git clone https://github.com/your-username/slay-check.git
cd slay-check

# Install in development mode
pip install -e .

# Set up environment (see README for full config: preset, focus, defaults)
export SLAY_CHECK_AI_TOKEN="your-test-token"
export SLAY_CHECK_GITHUB_TOKEN="your-test-token"

# Run tests
pytest
```

## Contributing Process

### 1. Create an Issue

Before starting work, create an issue to discuss:
- Bug reports
- Feature requests
- Performance improvements
- Documentation updates

### 2. Fork and Branch

Create a branch from `main` (see [Branching strategy](#branching-strategy) above):

```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 3. Make Changes

Follow the [Code Style Guidelines](#code-style-guidelines) and [Testing Guidelines](#testing-guidelines).

### 4. Test Your Changes

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=slay_check

# Test CLI
python -m slay_check.cli --help

# Test GitHub Action
python -m slay_check.github_action --help
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

Create a pull request **targeting `main`** with:
- Clear description of changes
- Reference to related issues
- Screenshots (if applicable)
- Test results

## Code Style Guidelines

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Use `black` for formatting
- Use `flake8` for linting
- Use `mypy` for type checking

### Naming Conventions

- Use descriptive names
- Use snake_case for variables and functions
- Use PascalCase for classes
- Use UPPER_CASE for constants

### Error Handling

```python
# Good
try:
    result = process_file(filename)
except FileNotFoundError as e:
    raise ValueError(f"Failed to process file {filename}: {e}") from e

# Bad
try:
    result = process_file(filename)
except Exception as e:
    return None
```

### Documentation

- Document all public functions and classes
- Use docstrings following PEP 257
- Include type hints for all parameters and return values

```python
def process_file(filename: str) -> Result:
    """Process a file and return the result.
    
    Args:
        filename: The path to the file to process
        
    Returns:
        A Result object containing the processed data
        
    Raises:
        ValueError: If the file cannot be processed
        FileNotFoundError: If the file does not exist
    """
    # implementation
```

## Testing Guidelines

### Unit Tests

- Write tests for all new functionality
- Aim for >80% code coverage
- Use pytest fixtures for test data
- Mock external dependencies

```python
import pytest
from unittest.mock import Mock, patch

def test_process_file():
    """Test file processing functionality."""
    # Test with valid file
    result = process_file("test.py")
    assert result.success is True
    
    # Test with invalid file
    with pytest.raises(ValueError):
        process_file("nonexistent.py")

@pytest.fixture
def mock_ai_provider():
    """Mock AI provider for testing."""
    provider = Mock()
    provider.review_code.return_value = ReviewResponse(
        analysis="Test analysis",
        score=8.5,
        issues=[],
        suggestions=[],
        complexity=Complexity(),
        confidence=0.8
    )
    return provider
```

### Integration Tests

- Test with real AI providers (use test tokens)
- Test GitHub API integration
- Test end-to-end workflows

```python
@pytest.mark.integration
def test_review_pull_request():
    """Integration test for pull request review."""
    # Integration test implementation
    pass
```

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
- [ ] Version bumped in pyproject.toml
- [ ] Release notes prepared
- [ ] GitHub release created

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

- **Issues**: [GitHub Issues](https://github.com/prathameshap/slay-check/issues)
- **Discussions**: [GitHub Discussions](https://github.com/prathameshap/slay-check/discussions)

## Recognition

Contributors will be recognized in:
- README.md contributors section (via [All Contributors](https://allcontributors.org); see [README](README.md#contributors))
- Release notes
- GitHub contributors page

To have the All Contributors table updated, invite [@all-contributors](https://github.com/all-contributors/all-contributors) in a comment, e.g. `@all-contributors please add @username for code`.

Thank you for contributing to Slay Check!