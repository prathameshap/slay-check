"""
Configuration management for Slay Check.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import BaseModel, Field

# Presets: choose what to review with one word.
REVIEW_PRESETS: Dict[str, Dict[str, bool]] = {
    "full": {
        "analyze_problem": True,
        "algorithm_analysis": True,
        "best_approaches": True,
        "complexity_analysis": True,
        "risk_assessment": True,
        "security_review": True,
        "performance_review": True,
    },
    "standard": {
        "analyze_problem": False,
        "algorithm_analysis": True,
        "best_approaches": True,
        "complexity_analysis": True,
        "risk_assessment": True,
        "security_review": True,
        "performance_review": True,
    },
    "minimal": {
        "analyze_problem": False,
        "algorithm_analysis": False,
        "best_approaches": False,
        "complexity_analysis": False,
        "risk_assessment": False,
        "security_review": True,
        "performance_review": True,
    },
    "security": {
        "analyze_problem": False,
        "algorithm_analysis": False,
        "best_approaches": False,
        "complexity_analysis": False,
        "risk_assessment": True,
        "security_review": True,
        "performance_review": False,
    },
    "performance": {
        "analyze_problem": False,
        "algorithm_analysis": True,
        "best_approaches": True,
        "complexity_analysis": True,
        "risk_assessment": False,
        "security_review": False,
        "performance_review": True,
    },
}

# Short names for review_focus (e.g. focus: [security, performance]).
FOCUS_ALIASES: Dict[str, str] = {
    "problem": "analyze_problem",
    "analyze_problem": "analyze_problem",
    "algorithm": "algorithm_analysis",
    "algorithm_analysis": "algorithm_analysis",
    "best_approaches": "best_approaches",
    "best_practices": "best_approaches",
    "complexity": "complexity_analysis",
    "complexity_analysis": "complexity_analysis",
    "risk": "risk_assessment",
    "risk_assessment": "risk_assessment",
    "security": "security_review",
    "security_review": "security_review",
    "performance": "performance_review",
    "performance_review": "performance_review",
}


def _preset_to_criteria(preset_name: str) -> Dict[str, bool]:
    """Return review_criteria dict for a preset. Default to full if unknown."""
    preset = preset_name.strip().lower()
    return REVIEW_PRESETS.get(preset, REVIEW_PRESETS["full"]).copy()


def _focus_to_criteria(focus_list: List[str]) -> Dict[str, bool]:
    """Build review_criteria from a list of focus names; only those are True."""
    all_keys = [
        "analyze_problem",
        "algorithm_analysis",
        "best_approaches",
        "complexity_analysis",
        "risk_assessment",
        "security_review",
        "performance_review",
    ]
    criteria = {k: False for k in all_keys}
    for name in focus_list:
        key = FOCUS_ALIASES.get(name.strip().lower(), name.strip().lower())
        if key in criteria:
            criteria[key] = True
    return criteria


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
    ai_model: Optional[str] = Field(default="gpt-4o", description="AI model to use")
    ai_base_url: Optional[str] = Field(
        default="https://api.openai.com/v1/", description="Custom API base URL"
    )

    # GitHub Configuration
    github_token: str = Field(default="", description="GitHub personal access token")

    # Review Configuration
    review_criteria: ReviewCriteria = Field(default_factory=ReviewCriteria)

    # File Filtering
    exclude_patterns: List[str] = Field(
        default_factory=lambda: [
            "*.md",
            "*.txt",
            "vendor/*",
            "node_modules/*",
            "*.min.js",
            "*.min.css",
            "*.lock",
            "*.log",
            "*.tmp",
            "testdata/*",
        ]
    )

    # Performance Limits
    max_file_size: int = Field(default=10000, description="Maximum lines per file")
    max_files_per_pr: int = Field(default=50, description="Maximum files per PR")

    # Behavior
    verbose: bool = Field(default=False, description="Enable verbose logging")
    dry_run: bool = Field(default=False, description="Don't post comments")
    use_issue_comments: bool = Field(
        default=True, description="Use issue comments instead of reviews (more visible)"
    )

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
            with open(config_path, "r") as f:
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
                with open(path, "r") as f:
                    config_data = yaml.safe_load(f) or {}
                break

        # Override with environment variables
        _verbose_env = os.getenv("SLAY_CHECK_VERBOSE")
        _dry_run_env = os.getenv("SLAY_CHECK_DRY_RUN")
        _use_issue_comments_env = os.getenv("SLAY_CHECK_USE_ISSUE_COMMENTS")
        _review_preset = os.getenv("SLAY_CHECK_REVIEW_PRESET")
        _review_focus = os.getenv("SLAY_CHECK_REVIEW_FOCUS")
        env_overrides = {
            "ai_provider": os.getenv("SLAY_CHECK_AI_PROVIDER"),
            "ai_token": os.getenv("SLAY_CHECK_AI_TOKEN"),
            "ai_model": os.getenv("SLAY_CHECK_AI_MODEL"),
            "ai_base_url": os.getenv("SLAY_CHECK_AI_BASE_URL"),
            "github_token": os.getenv("SLAY_CHECK_GITHUB_TOKEN"),
            "verbose": (
                _verbose_env.lower() == "true" if _verbose_env is not None else None
            ),
            "dry_run": (
                _dry_run_env.lower() == "true" if _dry_run_env is not None else None
            ),
            "use_issue_comments": (
                _use_issue_comments_env.lower() == "true"
                if _use_issue_comments_env is not None
                else None
            ),
            "review_preset": _review_preset,
            "review_focus": _review_focus.split(",") if _review_focus else None,
        }

        # Remove None values
        env_overrides = {k: v for k, v in env_overrides.items() if v is not None}
        config_data.update(env_overrides)

        # Resolve review_criteria from preset or focus (easy config for users)
        if "review_focus" in config_data:
            focus = config_data.pop("review_focus")
            if isinstance(focus, str):
                focus = [s.strip() for s in focus.split(",")]
            config_data["review_criteria"] = ReviewCriteria(**_focus_to_criteria(focus))
        elif "review_preset" in config_data:
            preset = config_data.pop("review_preset")
            preset_str = preset if isinstance(preset, str) else str(preset)
            config_data["review_criteria"] = ReviewCriteria(
                **_preset_to_criteria(preset_str)
            )

        return cls(**config_data)

    def save(self, config_path: str) -> None:
        """Save configuration to file."""
        config_dict = self.model_dump()

        # Create directory if it doesn't exist
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w") as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)

    def validate(self, *, require_github_token: bool = True) -> None:
        """Validate configuration.

        Args:
            require_github_token: When False, skip GitHub token requirement (useful for
                local-only flows that do not call the GitHub API).
        """
        if not self.ai_token:
            raise ValueError("AI token is required")

        if require_github_token and not self.github_token:
            raise ValueError("GitHub token is required")

        if self.ai_provider not in [
            "openai",
            "anthropic",
            "google",
            "perplexity",
            "cursor",
            "http",
            "custom_http",
        ]:
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
