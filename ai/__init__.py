"""
AI provider implementations for Slay Check.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from enum import Enum


class IssueType(str, Enum):
    """Types of code issues."""
    BUG = "bug"
    PERFORMANCE = "performance"
    SECURITY = "security"
    STYLE = "style"
    COMPLEXITY = "complexity"
    MAINTAINABILITY = "maintainability"


class Severity(str, Enum):
    """Issue severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Issue(BaseModel):
    """A code issue found by AI."""
    
    type: IssueType
    severity: Severity
    line: Optional[int] = None
    message: str
    suggestion: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)


class Complexity(BaseModel):
    """Code complexity analysis."""
    
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
    """Response from AI code review."""
    
    analysis: str
    score: float = Field(ge=0.0, le=10.0)
    issues: List[Issue] = []
    suggestions: List[str] = []
    complexity: Optional[Complexity] = None
    confidence: float = Field(ge=0.0, le=1.0)


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    def review_code(self, request: ReviewRequest) -> ReviewResponse:
        """Review code and return analysis."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get provider name."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available."""
        pass
