"""Local review orchestration (shared by CLI and MCP)."""

from __future__ import annotations

from pathlib import Path
from typing import List

from .config import Config
from .git_diff import get_local_git_diff, split_unified_diff_by_file
from .github_client import PullRequestFileInfo, PullRequestInfo
from .review import FileReview, ReviewEngine, ReviewResult


def _local_pr_placeholder() -> PullRequestInfo:
    return PullRequestInfo(
        number=0,
        title="Local changes",
        body=None,
        state="local",
        base_ref="",
        head_ref="",
        files=[],
        owner="",
        repo="",
        author="",
        created_at="",
        updated_at="",
    )


def perform_local_git_review(config: Config, *, staged: bool = False) -> str:
    """Run Slay Check on local git diff; return markdown for the assistant / user."""
    diff = get_local_git_diff(staged=staged)
    if not diff.strip():
        return "No local changes detected (git diff is empty)."

    by_file = split_unified_diff_by_file(diff)
    if not by_file:
        return "No file patches found in git diff output."

    file_infos: List[PullRequestFileInfo] = []
    for filename, patch in by_file.items():
        additions = sum(
            1
            for line in patch.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        )
        deletions = sum(
            1
            for line in patch.splitlines()
            if line.startswith("-") and not line.startswith("---")
        )
        changes = additions + deletions
        file_infos.append(
            PullRequestFileInfo(
                filename=filename,
                status="modified",
                additions=additions,
                deletions=deletions,
                changes=changes,
                patch=patch,
            )
        )

    return _run_reviews_and_format(config, file_infos)


def patch_for_whole_file(display_path: str, content: str) -> str:
    """Build a minimal unified diff so the review engine sees all lines as additions."""
    lines = content.splitlines()
    n = len(lines)
    header = [
        f"diff --git a/{display_path} b/{display_path}",
        f"--- a/{display_path}",
        f"+++ b/{display_path}",
        f"@@ -0,0 +1,{n} @@",
    ]
    body = [f"+{line}" for line in lines]
    return "\n".join(header + body)


def perform_file_review(
    config: Config, path: str, *, working_dir: Path | None = None
) -> str:
    """Review a single file from disk as a full-file diff."""
    base = working_dir or Path.cwd()
    p = (base / path).resolve()
    if not p.is_file():
        return f"Error: not a regular file: {p}"

    try:
        display = str(p.relative_to(Path.cwd())).replace("\\", "/")
    except ValueError:
        display = str(p).replace("\\", "/")

    content = p.read_text(encoding="utf-8", errors="replace")
    patch = patch_for_whole_file(display, content)
    ln = len(content.splitlines())
    fi = PullRequestFileInfo(
        filename=display,
        status="modified",
        additions=ln,
        deletions=0,
        changes=ln,
        patch=patch,
    )
    return _run_reviews_and_format(config, [fi])


def _run_reviews_and_format(
    config: Config, file_infos: List[PullRequestFileInfo]
) -> str:
    pr_info = _local_pr_placeholder()
    engine = ReviewEngine(config)
    filtered = engine._filter_files(file_infos)
    if not filtered:
        return "No files to review after filtering (check exclude_patterns and limits)."

    file_reviews: List[FileReview] = []
    all_issues = []
    for fi in filtered:
        try:
            fr = engine._review_file(fi, pr_info)
            file_reviews.append(fr)
            all_issues.extend(fr.issues)
        except Exception as e:
            return f"Review failed for `{fi.filename}`: {e}"

    overall = (
        sum(fr.score for fr in file_reviews) / len(file_reviews)
        if file_reviews
        else 0.0
    )
    summary = engine._generate_summary(file_reviews, all_issues, overall)
    result = ReviewResult(
        pull_request=pr_info,
        files=file_reviews,
        issues=all_issues,
        score=overall,
        summary=summary,
        duration=0.0,
    )
    return engine._build_single_comment_body(result)
