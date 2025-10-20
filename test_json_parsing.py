#!/usr/bin/env python3
"""
Test script to verify JSON parsing fix for markdown-wrapped JSON responses.
"""

import json
from slay_check.ai.openai import OpenAIProvider
from slay_check.ai.base import ReviewRequest

def test_json_parsing():
    """Test the JSON parsing fix for markdown-wrapped responses."""
    
    # Test cases with different JSON wrapping formats
    test_cases = [
        # Case 1: JSON wrapped in ```json blocks
        """```json
{
  "analysis": "Test analysis",
  "score": 8.5,
  "issues": [
    {
      "type": "performance",
      "severity": "medium",
      "line": 10,
      "message": "Inefficient loop",
      "suggestion": "Use a more efficient algorithm"
    }
  ],
  "suggestions": ["Suggestion 1"],
  "complexity": {
    "time_complexity": "O(n²)",
    "space_complexity": "O(1)"
  },
  "confidence": 0.85
}
```""",
        
        # Case 2: JSON wrapped in ``` blocks
        """```
{
  "analysis": "Test analysis 2",
  "score": 7.0,
  "issues": [],
  "suggestions": [],
  "complexity": {
    "time_complexity": "O(n)",
    "space_complexity": "O(1)"
  },
  "confidence": 0.7
}
```""",
        
        # Case 3: Raw JSON (no wrapping)
        """{
  "analysis": "Test analysis 3",
  "score": 9.0,
  "issues": [
    {
      "type": "style",
      "severity": "low",
      "line": 5,
      "message": "Minor style issue",
      "suggestion": "Improve formatting"
    }
  ],
  "suggestions": ["Suggestion 1", "Suggestion 2"],
  "complexity": {
    "time_complexity": "O(log n)",
    "space_complexity": "O(log n)"
  },
  "confidence": 0.9
}""",
        
        # Case 4: Malformed JSON (should fallback gracefully)
        """```json
{
  "analysis": "Test analysis 4",
  "score": 6.0,
  "issues": [
    {
      "type": "bug",
      "severity": "high",
      "line": 15,
      "message": "Potential bug",
      "suggestion": "Fix the logic"
    }
  ],
  "suggestions": ["Fix the bug"],
  "complexity": {
    "time_complexity": "O(n)",
    "space_complexity": "O(n)"
  },
  "confidence": 0.8
}
```"""
    ]
    
    # Create a mock OpenAI provider for testing
    provider = OpenAIProvider("dummy-token", "gpt-4o")
    
    print("=== Testing JSON Parsing Fix ===\n")
    
    for i, test_content in enumerate(test_cases, 1):
        print(f"Test Case {i}:")
        print(f"Input: {test_content[:100]}...")
        
        try:
            # Test the parsing method directly
            response = provider._parse_response(test_content)
            
            print(f"✅ Parsing successful!")
            print(f"   Score: {response.score}")
            print(f"   Issues: {len(response.issues)}")
            print(f"   Analysis: {response.analysis[:50]}...")
            print(f"   Confidence: {response.confidence}")
            
            if response.issues:
                print(f"   Issues found:")
                for j, issue in enumerate(response.issues, 1):
                    print(f"     {j}. {issue.severity} {issue.type} - {issue.message}")
            
            if response.complexity and response.complexity.time_complexity:
                print(f"   Time Complexity: {response.complexity.time_complexity}")
                print(f"   Space Complexity: {response.complexity.space_complexity}")
                
        except Exception as e:
            print(f"❌ Parsing failed: {e}")
        
        print()

def test_real_world_example():
    """Test with a real-world example from the user's error."""
    
    real_response = """```json
{
  "analysis": "The provided code is the `__init__.py` file for a Python package that implements various tree data structures, including binary search trees, AVL trees, heaps, and tries. This file is responsible for initializing the package and making specific classes available for import when the package is used. The code is well-structured and follows standard practices for package initialization in Python. However, there are a few areas where improvements can be made.",
  "score": 9.0,
  "issues": [
    {
      "type": "documentation",
      "severity": "low",
      "line": 1,
      "message": "Missing module docstring",
      "suggestion": "Add a comprehensive module docstring explaining the package purpose"
    },
    {
      "type": "style",
      "severity": "low",
      "line": 5,
      "message": "Consider adding type hints",
      "suggestion": "Add type hints for better code documentation"
    }
  ],
  "suggestions": [
    "Add comprehensive module documentation",
    "Consider adding type hints for better code clarity",
    "Add unit tests for the package initialization"
  ],
  "complexity": {
    "time_complexity": "O(1)",
    "space_complexity": "O(1)",
    "cyclomatic_complexity": 1,
    "maintainability": "excellent"
  },
  "confidence": 0.9
}
```"""
    
    print("=== Testing Real-World Example ===\n")
    
    provider = OpenAIProvider("dummy-token", "gpt-4o")
    
    try:
        response = provider._parse_response(real_response)
        
        print("✅ Real-world parsing successful!")
        print(f"Score: {response.score}")
        print(f"Issues: {len(response.issues)}")
        print(f"Analysis: {response.analysis[:100]}...")
        print(f"Confidence: {response.confidence}")
        
        if response.issues:
            print("\nIssues found:")
            for i, issue in enumerate(response.issues, 1):
                print(f"  {i}. {issue.severity} {issue.type} - {issue.message}")
                print(f"     Suggestion: {issue.suggestion}")
        
        if response.complexity:
            print(f"\nComplexity Analysis:")
            print(f"  Time Complexity: {response.complexity.time_complexity}")
            print(f"  Space Complexity: {response.complexity.space_complexity}")
            print(f"  Maintainability: {response.complexity.maintainability}")
            
    except Exception as e:
        print(f"❌ Real-world parsing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_json_parsing()
    print("\n" + "="*50 + "\n")
    test_real_world_example()
