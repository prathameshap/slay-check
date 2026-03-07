"""
Tests for Slay Check AI providers.
"""

from slay_check.ai.anthropic import AnthropicProvider
from slay_check.ai.base import (
    Complexity,
    Issue,
    IssueType,
    ReviewRequest,
    ReviewResponse,
    Severity,
)
from slay_check.ai.custom_http import CustomHTTPProvider
from slay_check.ai.google import GoogleAIProvider
from slay_check.ai.openai import OpenAIProvider
from slay_check.ai.perplexity import PerplexityProvider


def test_review_request():
    """Test ReviewRequest model."""
    request = ReviewRequest(
        code="print(\"hello\")",
        language="python",
        file_path="test.py",
        context="Test context",
    )

    assert request.code == "print(\"hello\")"
    assert request.language == "python"
    assert request.file_path == "test.py"
    assert request.context == "Test context"


def test_review_response():
    """Test ReviewResponse model."""
    issue = Issue(
        type=IssueType.BUG,
        severity=Severity.HIGH,
        line=10,
        message="Test issue",
        suggestion="Fix it",
        confidence=0.9,
    )

    complexity = Complexity(
        time_complexity="O(n)",
        space_complexity="O(1)",
        cyclomatic_complexity=3,
        maintainability="good",
    )

    response = ReviewResponse(
        analysis="Test analysis",
        score=8.5,
        issues=[issue],
        suggestions=["Suggestion 1", "Suggestion 2"],
        complexity=complexity,
        confidence=0.85,
    )

    assert response.analysis == "Test analysis"
    assert response.score == 8.5
    assert len(response.issues) == 1
    assert len(response.suggestions) == 2
    assert response.complexity.time_complexity == "O(n)"
    assert response.confidence == 0.85


def test_openai_provider():
    """Test OpenAI provider."""
    provider = OpenAIProvider("test-key", "gpt-4")

    assert provider.get_name() == "openai"
    assert provider.is_available() is True

    # Test with empty key
    provider_empty = OpenAIProvider("")
    assert provider_empty.is_available() is False


def test_anthropic_provider():
    """Test Anthropic provider."""
    provider = AnthropicProvider("test-key", "claude-3-sonnet-20240229")

    assert provider.get_name() == "anthropic"
    assert provider.is_available() is True

    # Test with empty key
    provider_empty = AnthropicProvider("")
    assert provider_empty.is_available() is False


def test_google_provider():
    """Test Google AI provider."""
    provider = GoogleAIProvider("test-key", "gemini-pro")

    assert provider.get_name() == "google"
    assert provider.is_available() is True

    # Test with empty key
    provider_empty = GoogleAIProvider("")
    assert provider_empty.is_available() is False


def test_perplexity_provider():
    """Test Perplexity provider."""
    provider = PerplexityProvider("test-key", "sonar-pro")

    assert provider.get_name() == "perplexity"
    assert provider.is_available() is True
    assert provider.model == "sonar-pro"

    provider_empty = PerplexityProvider("")
    assert provider_empty.is_available() is False


def test_custom_http_provider():
    """Test Custom HTTP provider."""
    provider = CustomHTTPProvider(
        endpoint="https://api.example.com/review", api_key="test-key"
    )

    assert provider.get_name() == "custom_http"
    assert provider.is_available() is True

    provider_empty = CustomHTTPProvider(endpoint="")
    assert provider_empty.is_available() is False
