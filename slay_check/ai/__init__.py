"""
AI provider implementations for Slay Check.
"""

from .anthropic import AnthropicProvider

# Import all classes from base module
from .base import (
    AIProvider,
    Complexity,
    Issue,
    IssueType,
    ReviewRequest,
    ReviewResponse,
    Severity,
)
from .custom_http import CustomHTTPProvider
from .openai import OpenAIProvider
from .perplexity import PerplexityProvider

try:
    from .google import GoogleAIProvider
except Exception:  # Optional dependency may be missing in some environments
    GoogleAIProvider = None  # type: ignore[assignment]

__all__ = [
    "IssueType",
    "Severity",
    "Issue",
    "Complexity",
    "ReviewRequest",
    "ReviewResponse",
    "AIProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "GoogleAIProvider",
    "PerplexityProvider",
    "CustomHTTPProvider",
]
