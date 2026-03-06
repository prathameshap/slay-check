"""
Perplexity AI provider implementation for Slay Check.

Uses the Perplexity API (OpenAI-compatible) at https://api.perplexity.ai.
Models: sonar, sonar-pro, sonar-deep-research, sonar-reasoning-pro
"""

import asyncio
import json
from typing import Optional

from openai import AsyncOpenAI

from .base import (
    AIProvider,
    Complexity,
    Issue,
    IssueType,
    ReviewRequest,
    ReviewResponse,
    Severity,
)
from .openai import OpenAIProvider


# Reuse OpenAI's prompt builder and response parser; only endpoint and default model differ.
PERPLEXITY_BASE_URL = "https://api.perplexity.ai"
DEFAULT_MODEL = "sonar-pro"


class PerplexityProvider(OpenAIProvider):
    """Perplexity AI provider for code review (OpenAI-compatible API)."""

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        base_url: Optional[str] = None,
    ):
        url = base_url or PERPLEXITY_BASE_URL
        super().__init__(api_key=api_key, model=model, base_url=url)

    def get_name(self) -> str:
        return "perplexity"

    def _parse_response(self, content: str) -> ReviewResponse:
        """Parse Perplexity response (same JSON shape as OpenAI)."""
        try:
            cleaned_content = content.strip()
            if cleaned_content.startswith("```json"):
                cleaned_content = cleaned_content[7:]
            if cleaned_content.startswith("```"):
                cleaned_content = cleaned_content[3:]
            if cleaned_content.endswith("```"):
                cleaned_content = cleaned_content[:-3]
            cleaned_content = cleaned_content.strip()

            json_start = cleaned_content.find("{")
            json_end = cleaned_content.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                json_content = cleaned_content[json_start:json_end]
            else:
                json_content = cleaned_content

            data = json.loads(json_content)

            issues = []
            for issue_data in data.get("issues", []):
                issue = Issue(
                    type=IssueType(issue_data.get("type", "style")),
                    severity=Severity(issue_data.get("severity", "low")),
                    line=issue_data.get("line"),
                    message=issue_data.get("message", ""),
                    suggestion=issue_data.get("suggestion"),
                    confidence=issue_data.get("confidence", 0.7),
                )
                issues.append(issue)

            complexity_data = data.get("complexity", {})
            complexity = Complexity(
                time_complexity=complexity_data.get("time_complexity"),
                space_complexity=complexity_data.get("space_complexity"),
                cyclomatic_complexity=complexity_data.get("cyclomatic_complexity"),
                maintainability=complexity_data.get("maintainability"),
            )

            return ReviewResponse(
                analysis=data.get("analysis", cleaned_content),
                score=float(data.get("score", 7.0)),
                issues=issues,
                suggestions=data.get("suggestions", []),
                complexity=complexity,
                confidence=float(data.get("confidence", 0.7)),
            )

        except (json.JSONDecodeError, ValueError, KeyError):
            return ReviewResponse(
                analysis=content,
                score=7.0,
                issues=[],
                suggestions=[],
                complexity=Complexity(),
                confidence=0.5,
            )

