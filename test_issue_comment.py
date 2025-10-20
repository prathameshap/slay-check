#!/usr/bin/env python3
"""
Test script to verify issue comment posting works.
"""

import os
import sys
from slay_check.config import Config
from slay_check.github_client import GitHubClient

def test_issue_comment():
    """Test posting an issue comment."""
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
        
        print(f"=== Testing Issue Comment Posting ===")
        print(f"Repository: {repo}")
        print(f"PR Number: {pr_number}")
        print(f"GitHub Token Set: {bool(config.github_token)}")
        
        # Initialize GitHub client
        github_client = GitHubClient(config.github_token)
        
        # Test comment
        test_body = """## 🤖 Slay Check Test Comment

This is a test comment to verify that issue comments are working properly.

**Test Details:**
- ✅ Comment posting: Working
- ✅ Visibility: Should be visible in Comments section
- ✅ Format: Markdown supported

If you can see this comment, the issue comment posting is working correctly! 🎉
"""
        
        # Post test comment
        print(f"\n=== Posting Test Comment ===")
        github_client.create_issue_comment(repo, pr_number, test_body)
        print("Test comment posted successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_issue_comment()
