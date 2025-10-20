#!/usr/bin/env python3
"""
Debug script to test AI response parsing and issue detection.
"""

import os
import sys
from slay_check.config import Config
from slay_check.review import ReviewEngine
from slay_check.ai.openai import OpenAIProvider
from slay_check.ai.base import ReviewRequest

def test_ai_response_parsing():
    """Test AI response parsing and issue detection."""
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
        
        print(f"=== Testing AI Response Parsing ===")
        print(f"Repository: {repo}")
        print(f"PR Number: {pr_number}")
        print(f"AI Token Set: {bool(config.ai_token)}")
        print(f"AI Provider: {config.ai_provider}")
        print(f"AI Model: {config.ai_model}")
        
        # Initialize review engine
        review_engine = ReviewEngine(config)
        
        # Perform review
        print(f"\n=== Performing Review ===")
        result = review_engine.review_pull_request(repo, pr_number)
        
        print(f"\n=== Review Results ===")
        print(f"Files reviewed: {len(result.files)}")
        print(f"Issues found: {len(result.issues)}")
        print(f"Overall score: {result.score:.1f}/10")
        
        # Show detailed file results
        for i, file_review in enumerate(result.files, 1):
            print(f"\n--- File {i}: {file_review.filename} ---")
            print(f"Score: {file_review.score:.1f}/10")
            print(f"Issues: {len(file_review.issues)}")
            print(f"Analysis: {file_review.analysis[:200]}...")
            
            if file_review.issues:
                for j, issue in enumerate(file_review.issues, 1):
                    print(f"  Issue {j}: {issue.severity} {issue.type} - {issue.message}")
            else:
                print("  No specific issues found")
        
        # Test AI provider directly
        print(f"\n=== Testing AI Provider Directly ===")
        ai_provider = OpenAIProvider(config.ai_token, config.ai_model)
        
        # Create a test request
        test_code = """
def calculate_sum(numbers):
    total = 0
    for i in range(len(numbers)):
        total = total + numbers[i]
    return total
"""
        
        test_request = ReviewRequest(
            code=test_code,
            language="python",
            file_path="test.py",
            context="Test function for debugging",
            criteria={
                "analyze_problem": True,
                "algorithm_analysis": True,
                "best_approaches": True,
                "complexity_analysis": True,
                "risk_assessment": True,
                "security_review": True,
                "performance_review": True,
            },
            max_tokens=config.max_tokens,
            temperature=config.temperature
        )
        
        print("Testing with sample code...")
        response = ai_provider.review_code(test_request)
        
        print(f"Test Response Score: {response.score:.1f}/10")
        print(f"Test Response Issues: {len(response.issues)}")
        print(f"Test Response Analysis: {response.analysis[:300]}...")
        
        if response.issues:
            for i, issue in enumerate(response.issues, 1):
                print(f"  Test Issue {i}: {issue.severity} {issue.type} - {issue.message}")
        else:
            print("  No issues found in test response")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_response_parsing()
