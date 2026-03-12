"""
OpenAI provider implementation for Slay Check.
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


class OpenAIProvider(AIProvider):
    """OpenAI provider for code review."""

    def __init__(
        self, api_key: str, model: str = "gpt-4o", base_url: Optional[str] = None
    ):
        # Allow custom base URL for OpenAI-compatible APIs
        if base_url:
            self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.api_key = api_key
        self.base_url = base_url

    def get_name(self) -> str:
        return "openai"

    def is_available(self) -> bool:
        return bool(self.api_key)

    def review_code(self, request: ReviewRequest) -> ReviewResponse:
        """Review code using OpenAI."""
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
                            "You are an expert code reviewer. Analyze the provided "
                            "code and give comprehensive feedback."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=request.max_tokens or 4000,
                temperature=request.temperature or 0.3,
            )

            content = response.choices[0].message.content
            return self._parse_response(content)

        except Exception as e:
            return ReviewResponse(
                analysis=f"Error during review: {str(e)}",
                score=5.0,
                issues=[],
                suggestions=[],
                complexity=Complexity(),
                confidence=0.0,
            )

    def _build_prompt(self, request: ReviewRequest) -> str:
        """Build the prompt for code review."""
        prompt = f"Please review the following {request.language} code:\n\n"
        prompt += f"File: {request.file_path}\n\n"

        if request.context:
            prompt += f"Context: {request.context}\n\n"

        prompt += "Code:\n```" + request.language + "\n" + request.code + "\n```\n\n"

        prompt += "Please analyze the code based on these criteria:\n"
        prompt += "\nThings to consider:\n"
        prompt += "1. Analyze the problem the code is solving\n"
        prompt += "2. Algorithm used for the logic\n"
        prompt += "3. Plausible best approaches for the code\n"
        prompt += "4. Time and space complexity for the code written\n"
        prompt += "5. Which would be the best approach for the current scenario\n"
        prompt += "6. Risks for using the new approach\n"

        # Add specific review criteria if enabled
        if request.criteria.get("analyze_problem", True):
            prompt += "\n- Analyze the problem the code is solving\n"
        if request.criteria.get("algorithm_analysis", True):
            prompt += "- Analyze the algorithm used for the logic\n"
        if request.criteria.get("best_approaches", True):
            prompt += "- Suggest plausible best approaches for the code\n"
        if request.criteria.get("complexity_analysis", True):
            prompt += "- Analyze time and space complexity\n"
        if request.criteria.get("risk_assessment", True):
            prompt += "- Identify risks and potential issues\n"
        if request.criteria.get("security_review", True):
            prompt += "- Review for security vulnerabilities\n"
        if request.criteria.get("performance_review", True):
            prompt += "- Review for performance issues\n"

        # Enhanced algorithm and complexity analysis instructions with prioritization
        if request.criteria.get("algorithm_analysis", True) or request.criteria.get(
            "complexity_analysis", True
        ):
            prompt += "\n\nALGORITHM & COMPLEXITY ANALYSIS (PRIORITY):\n"
            prompt += "Focus on these critical aspects:\n"
            prompt += "1. Algorithm identification and efficiency\n"
            prompt += "2. Time complexity (Big O notation)\n"
            prompt += "3. Space complexity (Big O notation)\n"
            prompt += "4. Performance bottlenecks\n"
            prompt += "5. Alternative approaches if current is inefficient\n"

        prompt += "\nREVIEW PRIORITIZATION:\n"
        prompt += "Focus on the most critical issues first:\n"
        prompt += "1. CRITICAL: Security vulnerabilities, bugs, performance issues\n"
        prompt += "2. HIGH: Algorithm inefficiency, complexity problems\n"
        prompt += "3. MEDIUM: Code style, best practices\n"
        prompt += "4. LOW: Minor improvements, documentation\n"

        prompt += "\nIMPORTANT: You MUST find specific issues in the code. "
        prompt += "Even if the code is good, look for:\n"
        prompt += "- Code style improvements\n"
        prompt += "- Performance optimizations\n"
        prompt += "- Best practice violations\n"
        prompt += "- Potential bugs or edge cases\n"
        prompt += "- Security considerations\n"
        prompt += "- Maintainability improvements\n"
        prompt += "\nPlease provide your analysis in JSON format with this structure:\n"
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
    "time_complexity": "O(n²)",
    "space_complexity": "O(1)",
    "cyclomatic_complexity": 5,
    "maintainability": "good"
  },
  "confidence": 0.85
}"""

        return prompt

    def _parse_response(self, content: str) -> ReviewResponse:
        """Parse OpenAI response into ReviewResponse."""
        try:
            # Clean the content - remove markdown code blocks if present
            cleaned_content = content.strip()
            if cleaned_content.startswith("```json"):
                cleaned_content = cleaned_content[7:]  # Remove ```json
            if cleaned_content.startswith("```"):
                cleaned_content = cleaned_content[3:]  # Remove ```
            if cleaned_content.endswith("```"):
                cleaned_content = cleaned_content[:-3]  # Remove trailing ```
            cleaned_content = cleaned_content.strip()

            # Extract JSON from content (handle extra data after JSON)
            json_start = cleaned_content.find("{")
            json_end = cleaned_content.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                json_content = cleaned_content[json_start:json_end]
            else:
                json_content = cleaned_content

            # Try to parse as JSON
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

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            # If JSON parsing fails, try to extract information from text
            print(f"JSON parsing failed: {e}")
            print(f"AI Response: {content[:500]}...")

            # Try to extract score from text
            score = 7.0
            if "score" in content.lower():
                import re

                score_match = re.search(r"score[:\s]*(\d+\.?\d*)", content.lower())
                if score_match:
                    score = float(score_match.group(1))

            # Create a basic response with the raw analysis
            return ReviewResponse(
                analysis=content,
                score=score,
                issues=[],  # No specific issues extracted
                suggestions=[],  # No specific suggestions extracted
                complexity=Complexity(),
                confidence=0.5,  # Lower confidence due to parsing failure
            )
