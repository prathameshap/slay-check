"""Git unified-diff helpers for local reviews (CLI, MCP)."""

from __future__ import annotations

import subprocess
from typing import Optional


def get_local_git_diff(*, staged: bool = False) -> str:
    """Return `git diff` output as a unified diff string."""
    cmd = ["git", "diff", "--no-color"]
    if staged:
        cmd.append("--cached")
    try:
        result = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
        )
        return result.stdout or ""
    except Exception as e:
        raise RuntimeError(f"Failed to run git diff: {e}") from e


def split_unified_diff_by_file(diff_text: str) -> dict[str, str]:
    """Split `git diff` output into per-file patches keyed by file path."""
    files: dict[str, list[str]] = {}
    current_file: Optional[str] = None

    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            parts = line.split()
            if len(parts) >= 4:
                b_path = parts[3]
                if b_path.startswith("b/"):
                    current_file = b_path[2:]
                else:
                    current_file = b_path
                files.setdefault(current_file, []).append(line)
            else:
                current_file = None
            continue

        if current_file is None:
            continue
        files[current_file].append(line)

    return {k: "\n".join(v) for k, v in files.items()}
