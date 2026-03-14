"""
Slay Check - AI Code Review Tool

A high-performance, modular AI code review tool for GitHub Actions
and local development.
"""

__version__ = "0.0.1"
__author__ = "prathamesh pawar"
__email__ = "prathameshp131@gmail.com"

from slay_check.config import Config
from slay_check.github_client import GitHubClient
from slay_check.review import ReviewEngine

__all__ = ["Config", "ReviewEngine", "GitHubClient"]
