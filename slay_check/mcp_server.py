"""MCP (Model Context Protocol) server for Slay Check — exposes local code review tools."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path


def _load_config():
    from slay_check.config import Config

    # Never post to GitHub from MCP tools; this is local review only.
    if os.getenv("SLAY_CHECK_DRY_RUN") is None:
        os.environ["SLAY_CHECK_DRY_RUN"] = "true"
    config = Config.load()
    config.validate(require_github_token=False)
    return config


def main() -> None:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        print(
            "The 'mcp' package is required. Install with: pip install 'slay-check[mcp]'",
            file=sys.stderr,
        )
        raise SystemExit(1)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    mcp = FastMCP(
        "Slay Check",
        instructions=(
            "Run AI code reviews via Slay Check: unstaged/staged git diff, or a single "
            "file path. Configure providers with slay-check.yaml, .env, or SLAY_CHECK_* "
            "environment variables."
        ),
    )

    @mcp.tool(
        name="slay_check_review_unstaged",
        description=(
            "Review unstaged local changes (equivalent to `git diff`). "
            "Requires API keys / Ollama as configured for Slay Check."
        ),
    )
    def review_unstaged() -> str:
        from slay_check.local_review import perform_local_git_review

        cfg = _load_config()
        return perform_local_git_review(cfg, staged=False)

    @mcp.tool(
        name="slay_check_review_staged",
        description=(
            "Review staged changes (equivalent to `git diff --cached`). "
            "Requires API keys / Ollama as configured for Slay Check."
        ),
    )
    def review_staged() -> str:
        from slay_check.local_review import perform_local_git_review

        cfg = _load_config()
        return perform_local_git_review(cfg, staged=True)

    @mcp.tool(
        name="slay_check_review_file",
        description=(
            "Review the current contents of one file (path relative to the workspace root)."
        ),
    )
    def review_file(file_path: str) -> str:
        from slay_check.local_review import perform_file_review

        cfg = _load_config()
        wd = Path(os.getenv("SLAY_CHECK_WORKDIR", ".")).resolve()
        return perform_file_review(cfg, file_path, working_dir=wd)

    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
