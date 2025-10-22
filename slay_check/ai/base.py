"""
Base AI provider interface for Slay Check.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum


class IssueType(str, Enum):
    """Types of issues that can be found."""
    BUG = "bug"
    SECURITY = "security"
    PERFORMANCE = "performance"
    STYLE = "style"
    COMPLEXITY = "complexity"
    MAINTAINABILITY = "maintainability"
    ACCESSIBILITY = "accessibility"
    BEST_PRACTICE = "best_practice"
    DOCUMENTATION = "documentation"
    SYNTAX = "syntax"
    CONFIGURATION = "configuration"
    LOGIC = "logic"
    DESIGN = "design"


class Severity(str, Enum):
    """Severity levels for issues."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Issue(BaseModel):
    """An issue found during code review."""
    type: IssueType
    severity: Severity
    line: Optional[int] = None
    message: str
    suggestion: Optional[str] = None
    confidence: float = 0.7


class Complexity(BaseModel):
    """Complexity analysis results."""
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None
    cyclomatic_complexity: Optional[int] = None
    maintainability: Optional[str] = None


class ReviewRequest(BaseModel):
    """Request for code review."""
    code: str
    language: str
    file_path: str
    context: Optional[str] = None
    criteria: Dict[str, bool] = {}
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None


class ReviewResponse(BaseModel):
    """Response from code review."""
    analysis: str
    score: float
    issues: List[Issue]
    suggestions: List[str]
    complexity: Complexity
    confidence: float


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the AI provider."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the AI provider is available."""
        pass
    
    @abstractmethod
    def review_code(self, request: ReviewRequest) -> ReviewResponse:
        """Review code and return analysis."""
        pass
