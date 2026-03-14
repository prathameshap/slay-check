"""
Ollama provider implementation for Slay Check.

Ollama runs open-source models locally and exposes an OpenAI-compatible API
at http://localhost:11434/v1.  No API key or internet connection required.
"""

import asyncio
import json
import logging

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

logger = logging.getLogger(__name__)

DEFAULT_OLLAMA_URL = "http://localhost:11434/v1"
DEFAULT_OLLAMA_MODEL = "llama3"


class OllamaProvider(AIProvider):
    """Ollama provider — local models, no API key required."""

    def __init__(
        self,
        model: str = DEFAULT_OLLAMA_MODEL,
        base_url: str = DEFAULT_OLLAMA_URL,
    ):
        self.model = model
        self.base_url = base_url
        self.client = AsyncOpenAI(
            api_key="ollama",  # Ollama ignores the key but openai lib requires one
            base_url=self.base_url,
        )

    def get_name(self) -> str:
        return "ollama"

    def is_available(self) -> bool:
        """Check if Ollama is reachable."""
        try:
            import httpx

            resp = httpx.get(
                self.base_url.replace("/v1", ""),
                timeout=3.0,
            )
            return resp.status_code == 200
        except Exception:
            return False

    def review_code(self, request: ReviewRequest) -> ReviewResponse:
        """Review code using a local Ollama model."""
        return asyncio.run(self._review_code_async(request))

    async def _review_code_async(self, request: ReviewRequest) -> ReviewResponse:
        """Async implementation of code review."""
        prompt = self._build_prompt(request)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert code reviewer. Analyze the "
                            "provided code and give comprehensive feedback."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=request.temperature or 0.3,
            )

            content = response.choices[0].message.content
            return self._parse_response(content)

        except Exception as e:
            return ReviewResponse(
                analysis=f"Error during review: {e}",
                score=5.0,
                issues=[],
                suggestions=[],
                complexity=Complexity(),
                confidence=0.0,
            )

    # ------------------------------------------------------------------
    # Prompt & parsing — identical to OpenAIProvider (shared logic).
    # ------------------------------------------------------------------

    def _build_prompt(self, request: ReviewRequest) -> str:
        """Build the review prompt."""
        prompt = f"Please review the following {request.language} code:\n\n"
        prompt += f"File: {request.file_path}\n\n"

        if request.context:
            prompt += f"Context: {request.context}\n\n"

        prompt += "Code:\n```" + request.language + "\n" + request.code + "\n```\n\n"

        prompt += "Please analyze the code based on these criteria:\n"

        if request.criteria.get("analyze_problem", True):
            prompt += "- Analyze the problem the code is solving\n"
        if request.criteria.get("algorithm_analysis", True):
            prompt += "- Analyze the algorithm used\n"
        if request.criteria.get("best_approaches", True):
            prompt += "- Suggest best approaches\n"
        if request.criteria.get("complexity_analysis", True):
            prompt += "- Analyze time and space complexity\n"
        if request.criteria.get("risk_assessment", True):
            prompt += "- Identify risks and potential issues\n"
        if request.criteria.get("security_review", True):
            prompt += "- Review for security vulnerabilities\n"
        if request.criteria.get("performance_review", True):
            prompt += "- Review for performance issues\n"

        prompt += "\nProvide your analysis in JSON format with this structure:\n"
        prompt += """{
  "analysis": "Detailed analysis of the code",
  "score": 8.5,
  "issues": [
    {
      "type": "performance",
      "severity": "medium",
      "line": 10,
      "message": "Inefficient loop",
      "suggestion": "Use a more efficient algorithm",
      "confidence": 0.9
    }
  ],
  "suggestions": ["Suggestion 1", "Suggestion 2"],
  "complexity": {
    "time_complexity": "O(n)",
    "space_complexity": "O(1)",
    "cyclomatic_complexity": 5,
    "maintainability": "good"
  },
  "confidence": 0.85
}"""
        return prompt

    def _parse_response(self, content: str) -> ReviewResponse:
        """Parse model response into ReviewResponse."""
        try:
            cleaned = content.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            json_start = cleaned.find("{")
            json_end = cleaned.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                json_content = cleaned[json_start:json_end]
            else:
                json_content = cleaned

            data = json.loads(json_content)

            issues = []
            for issue_data in data.get("issues", []):
                issues.append(
                    Issue(
                        type=IssueType(issue_data.get("type", "style")),
                        severity=Severity(issue_data.get("severity", "low")),
                        line=issue_data.get("line"),
                        message=issue_data.get("message", ""),
                        suggestion=issue_data.get("suggestion"),
                        confidence=issue_data.get("confidence", 0.7),
                    )
                )

            cdata = data.get("complexity", {})
            complexity = Complexity(
                time_complexity=cdata.get("time_complexity"),
                space_complexity=cdata.get("space_complexity"),
                cyclomatic_complexity=cdata.get("cyclomatic_complexity"),
                maintainability=cdata.get("maintainability"),
            )

            return ReviewResponse(
                analysis=data.get("analysis", cleaned),
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
