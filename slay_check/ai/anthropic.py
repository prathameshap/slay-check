"""
Anthropic provider implementation for Slay Check.
"""

import json
import asyncio
from typing import Dict, Any, Optional
from anthropic import AsyncAnthropic
from .base import AIProvider, ReviewRequest, ReviewResponse, Issue, IssueType, Severity, Complexity


class AnthropicProvider(AIProvider):
    """Anthropic provider for code review."""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229", base_url: Optional[str] = None):
        # Allow custom base URL for Anthropic-compatible APIs
        if base_url:
            self.client = AsyncAnthropic(api_key=api_key, base_url=base_url)
        else:
            self.client = AsyncAnthropic(api_key=api_key)
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
    
    def get_name(self) -> str:
        return "anthropic"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def review_code(self, request: ReviewRequest) -> ReviewResponse:
        """Review code using Anthropic."""
        return asyncio.run(self._review_code_async(request))
    
    async def _review_code_async(self, request: ReviewRequest) -> ReviewResponse:
        """Async implementation of code review."""
        prompt = self._build_prompt(request)
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=request.max_tokens or 4000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            content = response.content[0].text
            return self._parse_response(content)
            
        except Exception as e:
            return ReviewResponse(
                analysis=f"Error during review: {str(e)}",
                score=5.0,
                issues=[],
                suggestions=[],
                complexity=Complexity(),
                confidence=0.0
            )
    
    def _build_prompt(self, request: ReviewRequest) -> str:
        """Build the prompt for code review."""
        prompt = f"Please review the following {request.language} code:\n\n"
        prompt += f"File: {request.file_path}\n\n"
        
        if request.context:
            prompt += f"Context: {request.context}\n\n"
        
        prompt += "Code:\n```" + request.language + "\n" + request.code + "\n```\n\n"
        
        prompt += "Please analyze the code based on these criteria:\n"
        
        if request.criteria.get("analyze_problem", True):
            prompt += "- Analyze the problem the code is solving\n"
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
        
        prompt += "\nPlease provide your analysis in JSON format with the following structure:\n"
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
        """Parse Anthropic response into ReviewResponse."""
        try:
            # Try to parse as JSON first
            data = json.loads(content)
            
            issues = []
            for issue_data in data.get("issues", []):
                issue = Issue(
                    type=IssueType(issue_data.get("type", "style")),
                    severity=Severity(issue_data.get("severity", "low")),
                    line=issue_data.get("line"),
                    message=issue_data.get("message", ""),
                    suggestion=issue_data.get("suggestion"),
                    confidence=issue_data.get("confidence", 0.7)
                )
                issues.append(issue)
            
            complexity_data = data.get("complexity", {})
            complexity = Complexity(
                time_complexity=complexity_data.get("time_complexity"),
                space_complexity=complexity_data.get("space_complexity"),
                cyclomatic_complexity=complexity_data.get("cyclomatic_complexity"),
                maintainability=complexity_data.get("maintainability")
            )
            
            return ReviewResponse(
                analysis=data.get("analysis", content),
                score=float(data.get("score", 7.0)),
                issues=issues,
                suggestions=data.get("suggestions", []),
                complexity=complexity,
                confidence=float(data.get("confidence", 0.7))
            )
            
        except (json.JSONDecodeError, ValueError, KeyError):
            # If JSON parsing fails, create a basic response
            return ReviewResponse(
                analysis=content,
                score=7.0,
                issues=[],
                suggestions=[],
                complexity=Complexity(),
                confidence=0.7
            )
