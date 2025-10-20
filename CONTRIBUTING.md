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

- Python 3.11 or later
- Git
- pip (Python package manager)
- Docker (for testing)

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/slay-check.git
   cd slay-check
   ```

2. **Set up development environment**
   ```bash
   pip install -e .
   pip install -r requirements-dev.txt  # If available
   ```

3. **Run tests**
   ```bash
   pytest
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
pytest

# Run tests with coverage
pytest --cov=slay_check

# Run specific test file
pytest tests/test_config.py

# Test CLI
slay-check --help

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

Create a pull request with:
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
    
    Handles various file formats and returns an error if processing fails.
    
    Args:
        filename: The path to the file to process
        
    Returns:
        A Result object containing the processed data
        
    Raises:
        ValueError: If the file cannot be processed
        FileNotFoundError: If the file does not exist
        
    Example:
        >>> result = process_file("example.py")
        >>> print(result.success)
        True
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

def test_review_with_mock_provider(mock_ai_provider):
    """Test review with mocked AI provider."""
    result = review_code("test.py", mock_ai_provider)
    assert result.score == 8.5
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
- [ ] Version bumped in pyproject.toml
- [ ] Release notes prepared
- [ ] GitHub release created

### Creating a Release

1. Update version in `pyproject.toml`
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

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/slay-check/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/slay-check/discussions)
- **Discord**: [Slay Check Discord](https://discord.gg/slay-check)

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

Thank you for contributing to Slay Check! 🚀