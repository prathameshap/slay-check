#!/usr/bin/env python3
"""
Test script to show the new AI prompt structure.
"""

import os
import sys
from slay_check.config import Config
from slay_check.ai.openai import OpenAIProvider
from slay_check.ai.base import ReviewRequest

def test_new_prompt():
    """Test the new AI prompt structure."""
    try:
        # Load configuration
        config = Config.load()
        
        print(f"=== Testing New AI Prompt Structure ===")
        print(f"AI Provider: {config.ai_provider}")
        print(f"AI Model: {config.ai_model}")
        print(f"AI Token Set: {bool(config.ai_token)}")
        
        # Initialize AI provider
        ai_provider = OpenAIProvider(config.ai_token, config.ai_model)
        
        # Create a test request
        test_code = """
def find_maximum(numbers):
    max_num = numbers[0]
    for i in range(1, len(numbers)):
        if numbers[i] > max_num:
            max_num = numbers[i]
    return max_num
"""
        
        test_request = ReviewRequest(
            code=test_code,
            language="python",
            file_path="test.py",
            context="Test function for maximum finding",
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
        
        # Show the prompt that will be sent
        print(f"\n=== Generated Prompt ===")
        prompt = ai_provider._build_prompt(test_request)
        print(prompt)
        
        print(f"\n=== Testing AI Response ===")
        response = ai_provider.review_code(test_request)
        
        print(f"Score: {response.score:.1f}/10")
        print(f"Issues Found: {len(response.issues)}")
        print(f"Analysis: {response.analysis[:500]}...")
        
        if response.issues:
            print(f"\nIssues:")
            for i, issue in enumerate(response.issues, 1):
                print(f"  {i}. {issue.severity} {issue.type} - {issue.message}")
                if issue.suggestion:
                    print(f"     Suggestion: {issue.suggestion}")
        else:
            print("No specific issues found")
            
        if response.complexity:
            print(f"\nComplexity Analysis:")
            print(f"  Time Complexity: {response.complexity.time_complexity}")
            print(f"  Space Complexity: {response.complexity.space_complexity}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_prompt()
