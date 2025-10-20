"""
Review engine for Slay Check.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
import re

from .config import Config
from .github_client import GitHubClient, PullRequestInfo, PullRequestFileInfo, ReviewComment
from .ai.base import ReviewRequest, ReviewResponse, Issue, IssueType, Severity
from .ai.openai import OpenAIProvider
from .ai.anthropic import AnthropicProvider
from .ai.google import GoogleAIProvider


class FileReview:
    """Review result for a single file."""
    
    def __init__(self, filename: str, language: str, score: float, 
                 issues: List[Issue], suggestions: List[str], 
                 complexity: Any, analysis: str):
        self.filename = filename
        self.language = language
        self.score = score
        self.issues = issues
        self.suggestions = suggestions
        self.complexity = complexity
        self.analysis = analysis


class ReviewResult:
    """Result of a code review."""
    
    def __init__(self, pull_request: PullRequestInfo, files: List[FileReview], 
                 issues: List[Issue], score: float, summary: str, duration: float):
        self.pull_request = pull_request
        self.files = files
        self.issues = issues
        self.score = score
        self.summary = summary
        self.duration = duration


class ReviewEngine:
    """Main review engine for Slay Check."""
    
    def __init__(self, config: Config):
        self.config = config
        self.github_client = GitHubClient(config.github_token)
        self.ai_provider = self._create_ai_provider()
    
    def _create_ai_provider(self):
        """Create AI provider based on configuration."""
        if self.config.ai_provider == "openai":
            return OpenAIProvider(
                api_key=self.config.ai_token,
                model=self.config.ai_model or "gpt-4o",
                base_url=self.config.ai_base_url
            )
        elif self.config.ai_provider == "anthropic":
            return AnthropicProvider(
                api_key=self.config.ai_token,
                model=self.config.ai_model or "claude-3-sonnet-20240229",
                base_url=self.config.ai_base_url
            )
        elif self.config.ai_provider == "google":
            return GoogleAIProvider(
                api_key=self.config.ai_token,
                model=self.config.ai_model or "gemini-pro"
            )
        else:
            raise ValueError(f"Unsupported AI provider: {self.config.ai_provider}")
    
    def review_pull_request(self, repo: str, pr_number: int) -> ReviewResult:
        """Review a pull request."""
        start_time = time.time()
        
        # Get pull request information
        pr_info = self.github_client.get_pull_request(repo, pr_number)
        
        # Filter files
        filtered_files = self._filter_files(pr_info.files)
        
        if not filtered_files:
            return ReviewResult(
                pull_request=pr_info,
                files=[],
                issues=[],
                score=0.0,
                summary="No files to review after filtering",
                duration=time.time() - start_time
            )
        
        # Review each file
        file_reviews = []
        all_issues = []
        
        for file_info in filtered_files:
            try:
                file_review = self._review_file(file_info, pr_info)
                file_reviews.append(file_review)
                all_issues.extend(file_review.issues)
            except Exception as e:
                print(f"Warning: Failed to review file {file_info.filename}: {e}")
                continue
        
        # Calculate overall score
        if file_reviews:
            total_score = sum(fr.score for fr in file_reviews)
            overall_score = total_score / len(file_reviews)
        else:
            overall_score = 0.0
        
        # Generate summary
        summary = self._generate_summary(file_reviews, all_issues, overall_score)
        
        duration = time.time() - start_time
        
        return ReviewResult(
            pull_request=pr_info,
            files=file_reviews,
            issues=all_issues,
            score=overall_score,
            summary=summary,
            duration=duration
        )
    
    def _filter_files(self, files: List[PullRequestFileInfo]) -> List[PullRequestFileInfo]:
        """Filter files based on configuration."""
        filtered = []
        
        for file_info in files:
            # Skip if file is too large
            if file_info.changes > self.config.max_file_size:
                continue
            
            # Skip if matches exclude patterns
            if self.config.should_exclude_file(file_info.filename):
                continue
            
            # Skip deleted files
            if file_info.status == "removed":
                continue
            
            filtered.append(file_info)
        
        # Limit number of files
        if len(filtered) > self.config.max_files_per_pr:
            filtered = filtered[:self.config.max_files_per_pr]
        
        return filtered
    
    def _review_file(self, file_info: PullRequestFileInfo, pr_info: PullRequestInfo) -> FileReview:
        """Review a single file."""
        # Detect language
        language = self._detect_language(file_info.filename)
        
        # Extract code from patch
        code = self._extract_code_from_patch(file_info.patch)
        
        if not code:
            return FileReview(
                filename=file_info.filename,
                language=language,
                score=5.0,
                issues=[],
                suggestions=["No code changes detected"],
                complexity=None,
                analysis="No code changes to review"
            )
        
        # Prepare review request
        request = ReviewRequest(
            code=code,
            language=language,
            file_path=file_info.filename,
            context=f"PR #{pr_info.number}: {pr_info.title}",
            criteria={
                "analyze_problem": self.config.review_criteria.analyze_problem,
                "algorithm_analysis": self.config.review_criteria.algorithm_analysis,
                "best_approaches": self.config.review_criteria.best_approaches,
                "complexity_analysis": self.config.review_criteria.complexity_analysis,
                "risk_assessment": self.config.review_criteria.risk_assessment,
                "security_review": self.config.review_criteria.security_review,
                "performance_review": self.config.review_criteria.performance_review,
            },
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature
        )
        
        # Get AI review
        response = self.ai_provider.review_code(request)
        
        return FileReview(
            filename=file_info.filename,
            language=language,
            score=response.score,
            issues=response.issues,
            suggestions=response.suggestions,
            complexity=response.complexity,
            analysis=response.analysis
        )
    
    def _detect_language(self, filename: str) -> str:
        """Detect programming language from filename."""
        extension = Path(filename).suffix.lower()
        
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".go": "go",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".cs": "csharp",
            ".php": "php",
            ".rb": "ruby",
            ".rs": "rust",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".sh": "bash",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".json": "json",
            ".xml": "xml",
            ".html": "html",
            ".css": "css",
            ".scss": "scss",
            ".sql": "sql",
            ".md": "markdown",
            ".txt": "text",
        }
        
        return language_map.get(extension, "text")
    
    def _extract_code_from_patch(self, patch: Optional[str]) -> str:
        """Extract code from git patch."""
        if not patch:
            return ""
        
        lines = patch.split("\n")
        code_lines = []
        
        for line in lines:
            if line.startswith("+") and not line.startswith("+++"):
                # Remove the + prefix and add the line
                code_lines.append(line[1:])
        
        return "\n".join(code_lines)
    
    def _generate_summary(self, file_reviews: List[FileReview], 
                         issues: List[Issue], score: float) -> str:
        """Generate a summary of the review."""
        summary = f"## Code Review Summary\n\n"
        summary += f"**Overall Score:** {score:.1f}/10\n\n"
        summary += f"**Files Reviewed:** {len(file_reviews)}\n"
        summary += f"**Issues Found:** {len(issues)}\n\n"
        
        if issues:
            summary += "### Issues by Severity\n"
            
            severity_count = {}
            for issue in issues:
                severity_count[issue.severity] = severity_count.get(issue.severity, 0) + 1
            
            for severity, count in severity_count.items():
                summary += f"- **{severity.title()}:** {count}\n"
            summary += "\n"
        
        summary += "### Top Suggestions\n"
        suggestion_count = 0
        for file_review in file_reviews:
            for suggestion in file_review.suggestions:
                if suggestion_count >= 5:
                    break
                summary += f"- {suggestion}\n"
                suggestion_count += 1
            if suggestion_count >= 5:
                break
        
        return summary
    
    def post_review_comments(self, repo: str, pr_number: int, result: ReviewResult) -> None:
        """Post review comments to GitHub."""
        if self.config.dry_run:
            print("Dry run mode - no comments posted")
            return
        
        comments = []
        
        for file_review in result.files:
            for issue in file_review.issues:
                if issue.line:
                    comment = ReviewComment(
                        path=file_review.filename,
                        line=issue.line,
                        body=f"**{issue.severity.title()} {issue.type.title()} Issue**\n\n{issue.message}\n\n**Suggestion:** {issue.suggestion or 'No suggestion provided'}",
                        severity=issue.severity,
                        issue_type=issue.type
                    )
                    comments.append(comment)
        
        if comments:
            self.github_client.post_review_comments(repo, pr_number, comments)
        
        # Post overall review
        self.github_client.create_review(
            repo, pr_number, result.summary, "COMMENT"
        )
