"""
Slay Check - AI Code Review Tool

A high-performance, modular AI code review tool for GitHub Actions
and local development.
"""

__version__ = "1.0.0"
__author__ = "Slay Check Team"
__email__ = "team@slay-check.dev"

from slay_check.config import Config
from slay_check.github_client import GitHubClient
from slay_check.review import ReviewEngine

__all__ = ["Config", "ReviewEngine", "GitHubClient"]
