#!/usr/bin/env python3
"""
Debug script to test PR comment posting.
"""

import os
import sys
from slay_check.config import Config
from slay_check.review import ReviewEngine

def debug_comment_posting():
    """Debug comment posting functionality."""
    try:
        # Load configuration
        config = Config.load()
        
        # Get GitHub context
        repo = os.getenv("GITHUB_REPOSITORY")
        pr_number_str = os.getenv("GITHUB_PR_NUMBER")
        
        if not repo or not pr_number_str:
            print("Error: GITHUB_REPOSITORY and GITHUB_PR_NUMBER environment variables required")
            return
        
        pr_number = int(pr_number_str)
        
        print(f"=== Debug Comment Posting ===")
        print(f"Repository: {repo}")
        print(f"PR Number: {pr_number}")
        print(f"Dry Run: {config.dry_run}")
        print(f"GitHub Token Set: {bool(config.github_token)}")
        print(f"AI Token Set: {bool(config.ai_token)}")
        
        # Initialize review engine
        review_engine = ReviewEngine(config)
        
        # Perform review
        print(f"\n=== Performing Review ===")
        result = review_engine.review_pull_request(repo, pr_number)
        
        print(f"Files reviewed: {len(result.files)}")
        print(f"Issues found: {len(result.issues)}")
        print(f"Overall score: {result.score:.1f}/10")
        
        # Show what would be posted
        print(f"\n=== Comments to Post ===")
        comment_count = 0
        for file_review in result.files:
            for issue in file_review.issues:
                if issue.line:
                    comment_count += 1
                    print(f"Comment {comment_count}: {file_review.filename}:{issue.line} - {issue.severity} {issue.type}")
        
        print(f"Total comments to post: {comment_count}")
        print(f"Summary length: {len(result.summary)} characters")
        
        # Test posting
        if not config.dry_run:
            print(f"\n=== Posting Comments ===")
            review_engine.post_review_comments(repo, pr_number, result)
        else:
            print(f"\n=== Dry Run Mode ===")
            print("Comments would be posted but dry_run is enabled")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_comment_posting()
