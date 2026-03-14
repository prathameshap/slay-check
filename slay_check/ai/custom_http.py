"""
Custom HTTP provider implementation for Slay Check.

This provider lets enterprises plug in any HTTP endpoint that can accept a
standard Slay Check review request and return a JSON response in the same
shape as the built-in providers.
"""

from typing import Any, Dict, List, Optional

import httpx

from .base import (
    AIProvider,
    Complexity,
    Issue,
    IssueType,
    ReviewRequest,
    ReviewResponse,
    Severity,
)


class CustomHTTPProvider(AIProvider):
    """Generic HTTP-based provider for code review."""

    def __init__(
        self,
        endpoint: str,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.endpoint = endpoint
        self.api_key = api_key
        self.timeout = timeout

    def get_name(self) -> str:
        return "custom_http"

    def is_available(self) -> bool:
        return bool(self.endpoint)

    def review_code(self, request: ReviewRequest) -> ReviewResponse:
        """Review code by calling a custom HTTP endpoint."""
        if not self.endpoint:
            raise ValueError(
                "Custom HTTP endpoint is not configured (ai_base_url is empty)."
            )

        headers: Dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            # Authorization header; enterprises can use a different scheme server-side.
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload: Dict[str, Any] = {
            "code": request.code,
            "language": request.language,
            "file_path": request.file_path,
            "context": request.context,
            "criteria": request.criteria,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
        }

        try:
            response = httpx.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            return self._parse_response(data)
        except Exception as e:
            raise RuntimeError(f"Custom HTTP review error: {e}") from e

    def _parse_response(self, data: Dict[str, Any]) -> ReviewResponse:
        """Parse custom HTTP JSON response into ReviewResponse."""
        # We expect the same JSON schema as the built-in providers use:
        # {
        #   "analysis": str,
        #   "score": float,
        #   "issues": [...],
        #   "suggestions": [...],
        #   "complexity": {...},
        #   "confidence": float
        # }
        issues: List[Issue] = []
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

        complexity_data = data.get("complexity", {}) or {}
        complexity = Complexity(
            time_complexity=complexity_data.get("time_complexity"),
            space_complexity=complexity_data.get("space_complexity"),
            cyclomatic_complexity=complexity_data.get("cyclomatic_complexity"),
            maintainability=complexity_data.get("maintainability"),
        )

        return ReviewResponse(
            analysis=data.get("analysis", ""),
            score=float(data.get("score", 7.0)),
            issues=issues,
            suggestions=data.get("suggestions", []),
            complexity=complexity,
            confidence=float(data.get("confidence", 0.7)),
        )
