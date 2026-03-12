#!/usr/bin/env python3
"""
GitHub Action entry point for Slay Check.
"""

import os
import sys

from slay_check.config import Config
from slay_check.review import ReviewEngine


def main():
    """Main entry point for GitHub Action."""
    try:
        # Load configuration
        config = Config.load()

        # Get GitHub context from environment variables
        repo = os.getenv("GITHUB_REPOSITORY")
        if not repo:
            print("Error: GITHUB_REPOSITORY environment variable is required")
            sys.exit(1)

        pr_number_str = os.getenv("GITHUB_PR_NUMBER")
        if not pr_number_str:
            print("Error: GITHUB_PR_NUMBER environment variable is required")
            sys.exit(1)

        try:
            pr_number = int(pr_number_str)
        except ValueError:
            print(f"Error: Invalid PR number: {pr_number_str}")
            sys.exit(1)

        # Initialize review engine
        review_engine = ReviewEngine(config)

        # Perform review
        print(f"Starting review of PR #{pr_number}: {repo}")

        result = review_engine.review_pull_request(repo, pr_number)

        # Display results
        print("\n=== Review Results ===")
        print(f"Files reviewed: {len(result.files)}")
        print(f"Issues found: {len(result.issues)}")
        print(f"Overall score: {result.score:.1f}/10")
        print(f"Duration: {result.duration:.2f}s")

        # Post comments to PR if not dry run
        if not config.dry_run:
            review_engine.post_review_comments(repo, pr_number, result)
            print("Review comments posted to pull request")
        else:
            print("Dry run mode - no comments posted")

        # Set GitHub Actions outputs
        set_output("score", f"{result.score:.1f}")
        set_output("files_reviewed", str(len(result.files)))
        set_output("issues_found", str(len(result.issues)))
        set_output("duration", f"{result.duration:.2f}s")

        # Check if review passed thresholds
        if result.score < config.min_score_threshold:
            print(
                f"Review failed: Score {result.score:.1f} below threshold "
                f"{config.min_score_threshold}"
            )
            sys.exit(1)

        # Count critical issues
        critical_issues = sum(
            1 for issue in result.issues if issue.severity == "critical"
        )

        if critical_issues > config.critical_issues_limit:
            print(
                f"Review failed: {critical_issues} critical issues exceed limit "
                f"{config.critical_issues_limit}"
            )
            sys.exit(1)

        print("Review completed successfully!")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def set_output(name: str, value: str):
    """Set a GitHub Actions output"""
    output_file = os.getenv("GITHUB_OUTPUT")
    if output_file:
        try:
            with open(output_file, "a") as f:
                f.write(f"{name}={value}\n")
        except Exception:
            pass  # Ignore errors setting outputs


if __name__ == "__main__":
    main()
