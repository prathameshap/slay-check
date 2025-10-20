"""
Configuration management for Slay Check.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml
from pydantic import BaseModel, Field


class ReviewCriteria(BaseModel):
    """Review criteria configuration."""
    
    analyze_problem: bool = True
    algorithm_analysis: bool = True
    best_approaches: bool = True
    complexity_analysis: bool = True
    risk_assessment: bool = True
    security_review: bool = True
    performance_review: bool = True


class Config(BaseModel):
    """Main configuration class."""
    
    # AI Provider Configuration
    ai_provider: str = Field(default="openai", description="AI provider to use")
    ai_token: str = Field(default="", description="AI provider API token")
    ai_model: Optional[str] = Field(default=None, description="AI model to use")
    
    # GitHub Configuration
    github_token: str = Field(default="", description="GitHub personal access token")
    
    # Review Configuration
    review_criteria: ReviewCriteria = Field(default_factory=ReviewCriteria)
    
    # File Filtering
    exclude_patterns: List[str] = Field(
        default_factory=lambda: [
            "*.md", "*.txt", "vendor/*", "node_modules/*", 
            "*.min.js", "*.min.css", "*.lock", "*.log", 
            "*.tmp", "testdata/*"
        ]
    )
    
    # Performance Limits
    max_file_size: int = Field(default=10000, description="Maximum lines per file")
    max_files_per_pr: int = Field(default=50, description="Maximum files per PR")
    
    # Behavior
    verbose: bool = Field(default=False, description="Enable verbose logging")
    dry_run: bool = Field(default=False, description="Don't post comments")
    
    # AI Configuration
    max_tokens: int = Field(default=4000, description="Maximum tokens for AI response")
    temperature: float = Field(default=0.3, description="AI response temperature")
    
    # Review Thresholds
    min_score_threshold: float = Field(default=6.0, description="Minimum score to pass")
    critical_issues_limit: int = Field(default=3, description="Maximum critical issues")
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "Config":
        """Load configuration from file and environment variables."""
        config_data = {}
        
        # Load from file if exists
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f) or {}
        
        # Load from default locations
        default_paths = [
            "slay-check.yaml",
            "slay-check.yml",
            Path.home() / ".slay-check" / "config.yaml",
            Path.home() / ".slay-check" / "config.yml",
        ]
        
        for path in default_paths:
            if Path(path).exists():
                with open(path, 'r') as f:
                    config_data = yaml.safe_load(f) or {}
                break
        
        # Override with environment variables
        env_overrides = {
            "ai_provider": os.getenv("SLAY_CHECK_AI_PROVIDER"),
            "ai_token": os.getenv("SLAY_CHECK_AI_TOKEN"),
            "github_token": os.getenv("SLAY_CHECK_GITHUB_TOKEN"),
            "verbose": os.getenv("SLAY_CHECK_VERBOSE", "").lower() == "true",
            "dry_run": os.getenv("SLAY_CHECK_DRY_RUN", "").lower() == "true",
        }
        
        # Remove None values
        env_overrides = {k: v for k, v in env_overrides.items() if v is not None}
        config_data.update(env_overrides)
        
        return cls(**config_data)
    
    def save(self, config_path: str) -> None:
        """Save configuration to file."""
        config_dict = self.model_dump()
        
        # Create directory if it doesn't exist
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
    
    def validate(self) -> None:
        """Validate configuration."""
        if not self.ai_token:
            raise ValueError("AI token is required")
        
        if not self.github_token:
            raise ValueError("GitHub token is required")
        
        if self.ai_provider not in ["openai", "anthropic", "google"]:
            raise ValueError(f"Unsupported AI provider: {self.ai_provider}")
        
        if self.temperature < 0.0 or self.temperature > 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")
        
        if self.max_tokens <= 0:
            raise ValueError("Max tokens must be positive")
        
        if self.min_score_threshold < 0.0 or self.min_score_threshold > 10.0:
            raise ValueError("Min score threshold must be between 0.0 and 10.0")
    
    def should_exclude_file(self, filename: str) -> bool:
        """Check if a file should be excluded based on patterns."""
        from fnmatch import fnmatch
        
        for pattern in self.exclude_patterns:
            if fnmatch(filename, pattern):
                return True
        return False
