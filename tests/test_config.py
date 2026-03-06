"""
Tests for Slay Check configuration.
"""

import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from slay_check.config import Config, ReviewCriteria


def test_default_config():
    """Test default configuration values."""
    config = Config()

    assert config.ai_provider == "openai"
    assert config.ai_token == ""
    assert config.github_token == ""
    assert config.max_file_size == 10000
    assert config.max_files_per_pr == 50
    assert config.verbose is False
    assert config.dry_run is False
    assert config.min_score_threshold == 6.0
    assert config.critical_issues_limit == 3


def test_review_criteria_defaults():
    """Test review criteria defaults."""
    criteria = ReviewCriteria()

    assert criteria.analyze_problem is True
    assert criteria.algorithm_analysis is True
    assert criteria.best_approaches is True
    assert criteria.complexity_analysis is True
    assert criteria.risk_assessment is True
    assert criteria.security_review is True
    assert criteria.performance_review is True


def test_config_validation():
    """Test configuration validation."""
    config = Config(
        ai_provider="openai", ai_token="test-token", github_token="github-token"
    )

    # Should not raise
    config.validate()

    # Test invalid AI provider
    config.ai_provider = "invalid"
    with pytest.raises(ValueError, match="Unsupported AI provider"):
        config.validate()

    # Test missing AI token
    config.ai_provider = "openai"
    config.ai_token = ""
    with pytest.raises(ValueError, match="AI token is required"):
        config.validate()

    # Test missing GitHub token
    config.ai_token = "test-token"
    config.github_token = ""
    with pytest.raises(ValueError, match="GitHub token is required"):
        config.validate()

    # Test invalid temperature
    config.github_token = "github-token"
    config.temperature = 1.5
    with pytest.raises(ValueError, match="Temperature must be between"):
        config.validate()

    # Test invalid max tokens
    config.temperature = 0.3
    config.max_tokens = -1
    with pytest.raises(ValueError, match="Max tokens must be positive"):
        config.validate()

    # Test invalid score threshold
    config.max_tokens = 4000
    config.min_score_threshold = 11.0
    with pytest.raises(ValueError, match="Min score threshold must be between"):
        config.validate()


def test_should_exclude_file():
    """Test file exclusion logic."""
    config = Config()

    # Test excluded files
    assert config.should_exclude_file("README.md") is True
    assert config.should_exclude_file("notes.txt") is True
    assert config.should_exclude_file("vendor/package/file.go") is True
    assert config.should_exclude_file("node_modules/package/index.js") is True

    # Test included files
    assert config.should_exclude_file("main.py") is False
    assert config.should_exclude_file("src/app.js") is False
    assert config.should_exclude_file("tests/test_file.py") is False


def test_config_save_load():
    """Test configuration save and load."""
    config = Config(
        ai_provider="anthropic",
        ai_token="test-token",
        github_token="github-token",
        verbose=True,
        dry_run=True,
    )

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        config_path = f.name

    try:
        # Save configuration
        config.save(config_path)

        # Load configuration without environment overrides interfering.
        # Mock Path.home so it doesn't fail when env is cleared (Windows needs USERPROFILE).
        with mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch.object(
                Path, "home", return_value=Path(config_path).resolve().parent
            ):
                loaded_config = Config.load(config_path)

        assert loaded_config.ai_provider == "anthropic"
        assert loaded_config.ai_token == "test-token"
        assert loaded_config.github_token == "github-token"
        assert loaded_config.verbose is True
        assert loaded_config.dry_run is True

    finally:
        # Clean up
        os.unlink(config_path)
