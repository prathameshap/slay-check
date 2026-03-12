"""
Tests for Slay Check CLI.
"""

from unittest.mock import Mock, patch

from click.testing import CliRunner

from slay_check.cli import cli, config, review


def test_cli_version():
    """Test CLI version command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["version"])

    assert result.exit_code == 0
    assert "Slay Check v1.0.0" in result.output


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
    assert "Please specify either" in result.output


def test_review_local():
    """Test review local command."""
    runner = CliRunner()

    with patch("slay_check.cli.Config.load") as mock_load:
        mock_config = Mock()
        mock_config.validate.return_value = None
        mock_config.verbose = False
        mock_config.dry_run = False
        mock_load.return_value = mock_config

        result = runner.invoke(review, ["--local"])

        assert result.exit_code == 0
        assert "Reviewing local changes" in result.output


def test_review_pr():
    """Test review PR command."""
    runner = CliRunner()

    with patch("slay_check.cli.Config.load") as mock_load, patch(
        "slay_check.cli.ReviewEngine"
    ) as mock_engine:

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
