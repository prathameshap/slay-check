"""
Tests for Slay Check AI providers.
"""

import pytest
from unittest.mock import Mock, patch

from slay_check.ai.base import ReviewRequest, ReviewResponse, Issue, IssueType, Severity, Complexity
from slay_check.ai.openai import OpenAIProvider
from slay_check.ai.anthropic import AnthropicProvider
from slay_check.ai.google import GoogleAIProvider


def test_review_request():
    """Test ReviewRequest model."""
    request = ReviewRequest(
        code="print(\"hello\")",
        language="python",
        file_path="test.py",
        context="Test context"
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
        confidence=0.9
    )

    complexity = Complexity(
        time_complexity="O(n)",
        space_complexity="O(1)",
        cyclomatic_complexity=3,
        maintainability="good"
    )

    response = ReviewResponse(
        analysis="Test analysis",
        score=8.5,
        issues=[issue],
        suggestions=["Suggestion 1", "Suggestion 2"],
        complexity=complexity,
        confidence=0.85
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


@patch("slay_check.ai.openai.AsyncOpenAI")
def test_openai_review_code(mock_openai):
    """Test OpenAI code review."""
    # Mock the OpenAI client
    mock_client = Mock()
    mock_openai.return_value = mock_client

    # Mock the response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "{\"analysis\": \"Test analysis\", \"score\": 8.5, \"issues\": [], \"suggestions\": [], \"complexity\": {}, \"confidence\": 0.8}"
    mock_client.chat.completions.create.return_value = mock_response

    provider = OpenAIProvider("test-key")
    request = ReviewRequest(
        code="print(\"hello\")",
        language="python",
        file_path="test.py"
    )

    response = provider.review_code(request)

    assert response.analysis == "Test analysis"
    assert response.score == 8.5
    assert response.confidence == 0.8


@patch("slay_check.ai.anthropic.AsyncAnthropic")
def test_anthropic_review_code(mock_anthropic):
    """Test Anthropic code review."""
    # Mock the Anthropic client
    mock_client = Mock()
    mock_anthropic.return_value = mock_client

    # Mock the response
    mock_response = Mock()
    mock_response.content = [Mock()]
    mock_response.content[0].text = "{\"analysis\": \"Test analysis\", \"score\": 8.5, \"issues\": [], \"suggestions\": [], \"complexity\": {}, \"confidence\": 0.8}"
    mock_client.messages.create.return_value = mock_response

    provider = AnthropicProvider("test-key")
    request = ReviewRequest(
        code="print(\"hello\")",
        language="python",
        file_path="test.py"
    )

    response = provider.review_code(request)

    assert response.analysis == "Test analysis"
    assert response.score == 8.5
    assert response.confidence == 0.8


@patch("slay_check.ai.google.genai")
def test_google_review_code(mock_genai):
    """Test Google AI code review."""
    # Mock the Google AI client
    mock_model = Mock()
    mock_genai.GenerativeModel.return_value = mock_model

    # Mock the response
    mock_response = Mock()
    mock_response.text = "{\"analysis\": \"Test analysis\", \"score\": 8.5, \"issues\": [], \"suggestions\": [], \"complexity\": {}, \"confidence\": 0.8}"
    mock_model.generate_content_async.return_value = mock_response

    provider = GoogleAIProvider("test-key")
    request = ReviewRequest(
        code="print(\"hello\")",
        language="python",
        file_path="test.py"
    )

    response = provider.review_code(request)

    assert response.analysis == "Test analysis"
    assert response.score == 8.5
    assert response.confidence == 0.8
