"""
Tests for Slay Check CLI.
"""

from unittest.mock import Mock, patch

from click.testing import CliRunner

from slay_check import __version__
from slay_check.cli import cli, config, review


def test_cli_version():
    """Test CLI version command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["version"])

    assert result.exit_code == 0
    assert f"Slay Check v{__version__}" in result.output


def test_config_init():
    """Test config init command."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(config, ["init"])

        assert result.exit_code == 0
        assert "Configuration file created" in result.output


def test_config_show():
    """Test config show command."""
    runner = CliRunner()

    with patch("slay_check.cli.Config.load") as mock_load:
        mock_config = Mock()
        mock_config.ai_provider = "openai"
        mock_config.review_criteria.analyze_problem = True
        mock_config.max_file_size = 10000
        mock_load.return_value = mock_config

        result = runner.invoke(config, ["show"])

        assert result.exit_code == 0
        assert "Current Configuration" in result.output


def test_review_missing_args():
    """Test review command with missing arguments."""
    runner = CliRunner()

    result = runner.invoke(review, [])

    assert result.exit_code == 1
    assert "slay-check quick" in result.output


def test_review_local():
    """Test review local command."""
    runner = CliRunner()

    with (
        patch("slay_check.cli.Config.load") as mock_load,
        patch(
            "slay_check.cli.perform_local_git_review",
            return_value="No local changes detected (git diff is empty).",
        ),
    ):
        mock_config = Mock()
        mock_config.validate.return_value = None
        mock_config.verbose = False
        mock_config.dry_run = False
        mock_config.github_token = ""
        mock_config.ai_token = "test"
        mock_config.ai_provider = "openai"
        mock_config.ai_model = "gpt-4o"
        mock_config.ai_base_url = None
        mock_load.return_value = mock_config

        result = runner.invoke(review, ["--local"])

        assert result.exit_code == 0
        assert "Reviewing" in result.output


def test_review_pr():
    """Test review PR command."""
    runner = CliRunner()

    with (
        patch("slay_check.cli.Config.load") as mock_load,
        patch("slay_check.cli.ReviewEngine") as mock_engine,
    ):

        mock_config = Mock()
        mock_config.validate.return_value = None
        mock_config.verbose = False
        mock_config.dry_run = False
        mock_load.return_value = mock_config

        mock_review_engine = Mock()
        mock_result = Mock()
        mock_result.files = []
        mock_result.issues = []
        mock_result.score = 8.5
        mock_result.duration = 1.5
        mock_review_engine.review_pull_request.return_value = mock_result
        mock_engine.return_value = mock_review_engine

        result = runner.invoke(review, ["--pr", "123", "--repo", "owner/repo"])

        assert result.exit_code == 0
        assert "Reviewing pull request" in result.output


def test_cli_no_args_shows_welcome():
    """Bare `slay-check` prints quick start."""
    runner = CliRunner()
    result = runner.invoke(cli, [])
    assert result.exit_code == 0
    assert "Slay Check" in result.output
    assert "setup" in result.output.lower()
