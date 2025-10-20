"""
GitHub integration for Slay Check.
"""

from typing import List, Optional, Dict, Any
from github import Github, PullRequest, PullRequestFile
from pydantic import BaseModel


class PullRequestInfo(BaseModel):
    """Information about a pull request."""
    
    number: int
    title: str
    body: Optional[str] = None
    state: str
    base_ref: str
    head_ref: str
    files: List["PullRequestFileInfo"] = []
    owner: str
    repo: str
    author: str
    created_at: str
    updated_at: str


class PullRequestFileInfo(BaseModel):
    """Information about a file in a pull request."""
    
    filename: str
    status: str
    additions: int
    deletions: int
    changes: int
    patch: Optional[str] = None
    raw_url: Optional[str] = None
    blob_url: Optional[str] = None
    contents_url: Optional[str] = None
    previous_filename: Optional[str] = None


class ReviewComment(BaseModel):
    """A review comment to post."""
    
    path: str
    line: int
    body: str
    severity: str
    issue_type: str


class GitHubClient:
    """GitHub client for Slay Check."""
    
    def __init__(self, token: str):
        self.github = Github(token)
        self.token = token
    
    def get_pull_request(self, repo: str, pr_number: int) -> PullRequestInfo:
        """Get pull request information."""
        try:
            # Parse repository name
            owner, repo_name = repo.split("/", 1)
            
            # Get repository
            repository = self.github.get_repo(repo)
            
            # Get pull request
            pr = repository.get_pull(pr_number)
            
            # Get files
            files = list(pr.get_files())
            
            # Convert files to our format
            file_infos = []
            for file in files:
                file_info = PullRequestFileInfo(
                    filename=file.filename,
                    status=file.status,
                    additions=file.additions,
                    deletions=file.deletions,
                    changes=file.changes,
                    patch=file.patch,
                    raw_url=file.raw_url,
                    blob_url=file.blob_url,
                    contents_url=file.contents_url,
                    previous_filename=file.previous_filename
                )
                file_infos.append(file_info)
            
            return PullRequestInfo(
                number=pr.number,
                title=pr.title,
                body=pr.body,
                state=pr.state,
                base_ref=pr.base.ref,
                head_ref=pr.head.ref,
                files=file_infos,
                owner=owner,
                repo=repo_name,
                author=pr.user.login,
                created_at=pr.created_at.isoformat(),
                updated_at=pr.updated_at.isoformat()
            )
            
        except Exception as e:
            raise Exception(f"Failed to get pull request: {str(e)}")
    
    def post_review_comments(self, repo: str, pr_number: int, comments: List[ReviewComment]) -> None:
        """Post review comments to a pull request."""
        try:
            # Parse repository name
            owner, repo_name = repo.split("/", 1)
            
            # Get repository
            repository = self.github.get_repo(repo)
            
            # Get pull request
            pr = repository.get_pull(pr_number)
            
            # Post comments
            for comment in comments:
                pr.create_review_comment(
                    body=comment.body,
                    commit=pr.head.sha,
                    path=comment.path,
                    line=comment.line
                )
                
        except Exception as e:
            raise Exception(f"Failed to post review comments: {str(e)}")
    
    def create_review(self, repo: str, pr_number: int, body: str, event: str = "COMMENT") -> None:
        """Create a pull request review."""
        try:
            # Parse repository name
            owner, repo_name = repo.split("/", 1)
            
            # Get repository
            repository = self.github.get_repo(repo)
            
            # Get pull request
            pr = repository.get_pull(pr_number)
            
            # Create review
            pr.create_review(
                body=body,
                event=event
            )
            
        except Exception as e:
            raise Exception(f"Failed to create review: {str(e)}")
    
    def get_file_content(self, repo: str, path: str, ref: str = "main") -> str:
        """Get file content from repository."""
        try:
            # Parse repository name
            owner, repo_name = repo.split("/", 1)
            
            # Get repository
            repository = self.github.get_repo(repo)
            
            # Get file content
            file_content = repository.get_contents(path, ref=ref)
            
            # Decode content
            if hasattr(file_content, 'decoded_content'):
                return file_content.decoded_content.decode('utf-8')
            else:
                return file_content.content.decode('utf-8')
                
        except Exception as e:
            raise Exception(f"Failed to get file content: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if GitHub client is available."""
        return bool(self.token)
