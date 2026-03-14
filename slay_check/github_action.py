#!/usr/bin/env python3
"""
GitHub Action entry point for Slay Check.
"""

import logging
import os
import sys

from slay_check.config import Config
from slay_check.review import ReviewEngine

logger = logging.getLogger(__name__)


def main():
    """Main entry point for GitHub Action."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    try:
        config = Config.load()

        repo = os.getenv("GITHUB_REPOSITORY")
        if not repo:
            logger.error(
                "GITHUB_REPOSITORY is not set. This entry point is designed "
                "to run inside GitHub Actions."
            )
            sys.exit(1)

        pr_number_str = os.getenv("GITHUB_PR_NUMBER")
        if not pr_number_str:
            logger.error(
                "GITHUB_PR_NUMBER is not set. Make sure your workflow passes "
                "github.event.pull_request.number."
            )
            sys.exit(1)

        try:
            pr_number = int(pr_number_str)
        except ValueError:
            logger.error("Invalid PR number: %s", pr_number_str)
            sys.exit(1)

        review_engine = ReviewEngine(config)

        logger.info("Starting review of PR #%d: %s", pr_number, repo)
        result = review_engine.review_pull_request(repo, pr_number)

        logger.info("=== Review Results ===")
        logger.info("Files reviewed: %d", len(result.files))
        logger.info("Issues found: %d", len(result.issues))
        logger.info("Overall score: %.1f/10", result.score)
        logger.info("Duration: %.2fs", result.duration)

        if not config.dry_run:
            review_engine.post_review_comments(repo, pr_number, result)
            logger.info("Review comments posted to pull request")
        else:
            logger.info("Dry run mode - no comments posted")

        set_output("score", f"{result.score:.1f}")
        set_output("files_reviewed", str(len(result.files)))
        set_output("issues_found", str(len(result.issues)))
        set_output("duration", f"{result.duration:.2f}s")

        if result.score < config.min_score_threshold:
            logger.error(
                "Review failed: Score %.1f below threshold %.1f",
                result.score,
                config.min_score_threshold,
            )
            sys.exit(1)

        critical_issues = sum(
            1 for issue in result.issues if issue.severity == "critical"
        )
        if critical_issues > config.critical_issues_limit:
            logger.error(
                "Review failed: %d critical issues exceed limit %d",
                critical_issues,
                config.critical_issues_limit,
            )
            sys.exit(1)

        logger.info("Review completed successfully!")

    except Exception as e:
        logger.error("Error: %s", e)
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
