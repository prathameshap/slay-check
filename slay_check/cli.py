"""
CLI interface for Slay Check.
"""

import os
import subprocess
import sys
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .config import Config
from .github_client import PullRequestFileInfo, PullRequestInfo
from .review import ReviewEngine

console = Console()


@click.group()
@click.version_option(version=__version__)
def cli():
    """Slay Check - AI powered code review tool.

    \b
    Quick start:
      slay-check review --local              # review unstaged git diff
      slay-check review --local --staged     # review staged changes
      slay-check review --repo o/r --pr 42   # review a GitHub PR
      slay-check config init                 # create slay-check.yaml
      slay-check config show                 # display current config
    """
    pass


@cli.group()
def config():
    """Manage slay-check.yaml configuration."""
    pass


@config.command("init")
@click.option("--path", default="slay-check.yaml", help="Configuration file path")
def init_config(path: str):
    """Initialize configuration file (interactive wizard)."""
    if os.path.exists(path):
        console.print(f"[yellow]Configuration file {path} already exists[/yellow]")
        return

    # If running in a non-interactive context (e.g. CI), write a sensible default
    # config without prompting. This keeps `slay-check config init` script-friendly.
    if not sys.stdin.isatty():
        provider = "openai"
        ai_model = "gpt-4o"
        review_preset = "standard"
        use_issue_comments = True
        dry_run = False
        config_data = {
            "ai_provider": provider,
            "ai_model": ai_model,
            "review_preset": review_preset,
            "use_issue_comments": use_issue_comments,
            "dry_run": dry_run,
        }
    else:
        console.print(Panel.fit("Slay Check config wizard", style="cyan"))

        provider = click.prompt(
            "AI provider",
            type=click.Choice(
                [
                    "openai",
                    "anthropic",
                    "google",
                    "perplexity",
                    "ollama",
                    "github",
                    "custom_http",
                ],
                case_sensitive=False,
            ),
            default="openai",
            show_default=True,
        ).lower()

        model_default = {
            "openai": "gpt-4o",
            "anthropic": "claude-sonnet-4-6",
            "google": "gemini-2.5-flash",
            "perplexity": "sonar-pro",
            "ollama": "llama3.2",
            "github": "gpt-4o",
            "custom_http": "",
        }.get(provider, "")

        ai_model = click.prompt(
            "Model (leave empty to use default)",
            default=model_default,
            show_default=True if model_default else False,
        ).strip()

        review_preset = click.prompt(
            "Review preset",
            type=click.Choice(
                ["full", "standard", "minimal", "security", "performance"],
                case_sensitive=False,
            ),
            default="standard",
            show_default=True,
        ).lower()

        post_as = click.prompt(
            "Post review as",
            type=click.Choice(["issue_comment", "pr_review"], case_sensitive=False),
            default="issue_comment",
            show_default=True,
        ).lower()
        use_issue_comments = post_as == "issue_comment"

        dry_run = click.confirm("Dry run (do not post comment)?", default=False)

        config_data = {
            "ai_provider": provider,
            "review_preset": review_preset,
            "use_issue_comments": use_issue_comments,
            "dry_run": dry_run,
        }

        if ai_model:
            config_data["ai_model"] = ai_model

        if provider == "custom_http":
            endpoint = click.prompt("Custom HTTP endpoint URL", type=str).strip()
            config_data["ai_base_url"] = endpoint

    # Write YAML without embedding secrets. Tokens should be set via env/secrets.
    with open(path, "w", encoding="utf-8") as f:
        import yaml

        yaml.dump(config_data, f, default_flow_style=False, indent=2, sort_keys=False)

    console.print(f"[green]Configuration file created: {path}[/green]")
    console.print("\n[yellow]Next steps:[/yellow]")
    console.print(
        "- Add your AI token as an environment variable or GitHub secret: "
        "SLAY_CHECK_AI_TOKEN"
    )
    console.print(
        "- For PR reviews/comments, set SLAY_CHECK_GITHUB_TOKEN "
        "(in Actions, use GITHUB_TOKEN)"
    )
    console.print(
        "- Optional: override provider/model via environment variables at runtime"
    )


@config.command("show")
def show_config():
    """Show current configuration"""
    try:
        config = Config.load()

        table = Table(title="Current Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("AI Provider", config.ai_provider)
        table.add_row("Review Criteria", "")
        table.add_row(
            "  - Analyze Problem", str(config.review_criteria.analyze_problem)
        )
        table.add_row(
            "  - Algorithm Analysis", str(config.review_criteria.algorithm_analysis)
        )
        table.add_row(
            "  - Best Approaches", str(config.review_criteria.best_approaches)
        )
        table.add_row(
            "  - Complexity Analysis", str(config.review_criteria.complexity_analysis)
        )
        table.add_row(
            "  - Risk Assessment", str(config.review_criteria.risk_assessment)
        )
        table.add_row(
            "  - Security Review", str(config.review_criteria.security_review)
        )
        table.add_row(
            "  - Performance Review", str(config.review_criteria.performance_review)
        )
        table.add_row("Max File Size", str(config.max_file_size))
        table.add_row("Max Files Per PR", str(config.max_files_per_pr))
        table.add_row("Verbose", str(config.verbose))
        table.add_row("Dry Run", str(config.dry_run))

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")


@cli.command("review")
@click.option("--pr", type=int, help="Pull request number to review")
@click.option("--repo", help="Repository in format owner/repo")
@click.option("--local", is_flag=True, help="Review local changes (git diff)")
@click.option(
    "--staged",
    is_flag=True,
    help="Review staged changes only (git diff --cached). Implies --local.",
)
@click.option("--verbose", is_flag=True, help="Enable verbose output")
@click.option("--dry-run", is_flag=True, help="Don't post comments, just show results")
def review(
    pr: Optional[int],
    repo: Optional[str],
    local: bool,
    staged: bool,
    verbose: bool,
    dry_run: bool,
):
    """Review code changes.

    \b
    Examples:
      slay-check review --local                 # review unstaged changes
      slay-check review --local --staged        # review staged changes
      slay-check review --repo owner/repo --pr 42
      slay-check review --repo o/r --pr 42 --dry-run --verbose
    """
    try:
        if staged:
            local = True

        # Load configuration
        config = Config.load()

        # Override with CLI options
        if verbose:
            config.verbose = True
        if dry_run:
            config.dry_run = True

        _configure_logging(config.verbose)

        if not local and not (pr and repo):
            console.print(
                "[red]Please specify either --pr and --repo for pull request "
                "review or --local for local changes[/red]"
            )
            sys.exit(1)

        # Validate configuration
        config.validate(require_github_token=not local)

        if local:
            review_local_changes(config, staged=staged)
        else:
            review_pull_request(config, repo, pr)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def review_local_changes(config: Config, *, staged: bool = False):
    """Review local git changes"""
    label = "staged" if staged else "unstaged"
    console.print(f"[yellow]Reviewing {label} local changes...[/yellow]")
    diff = _get_local_git_diff(staged=staged)
    if not diff.strip():
        console.print("[green]No local changes detected (git diff is empty).[/green]")
        return

    pr_info = PullRequestInfo(
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

    files = _split_unified_diff_by_file(diff)
    if not files:
        console.print("[yellow]No file patches found in git diff output.[/yellow]")
        return

    file_infos = []
    for filename, patch in files.items():
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

    review_engine = ReviewEngine(config)
    filtered = review_engine._filter_files(file_infos)  # reuse same filter logic
    if not filtered:
        console.print("[yellow]No files to review after filtering.[/yellow]")
        return

    file_reviews = []
    all_issues = []
    for file_info in filtered:
        file_review = review_engine._review_file(file_info, pr_info)
        file_reviews.append(file_review)
        all_issues.extend(file_review.issues)

    overall_score = (
        sum(fr.score for fr in file_reviews) / len(file_reviews)
        if file_reviews
        else 0.0
    )
    summary = review_engine._generate_summary(file_reviews, all_issues, overall_score)

    console.print("\n[bold green]=== Local Review Results ===[/bold green]")
    console.print(f"Files reviewed: {len(file_reviews)}")
    console.print(f"Issues found: {len(all_issues)}")
    console.print(f"Overall score: {overall_score:.1f}/10\n")
    console.print(summary)


def _get_local_git_diff(*, staged: bool = False) -> str:
    """Get the local git diff as a unified diff string."""
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


def _split_unified_diff_by_file(diff_text: str) -> dict[str, str]:
    """Split `git diff` output into per-file patches keyed by file path."""
    files: dict[str, list[str]] = {}
    current_file: Optional[str] = None

    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            # Example: diff --git a/path b/path
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


def _configure_logging(verbose: bool) -> None:
    import logging

    level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def review_pull_request(config: Config, repo: str, pr_number: int):
    """Review a GitHub pull request"""
    console.print(f"[yellow]Reviewing pull request #{pr_number} in {repo}...[/yellow]")

    # Initialize review engine
    review_engine = ReviewEngine(config)

    # Perform review
    result = review_engine.review_pull_request(repo, pr_number)

    # Display results
    console.print("\n[bold green]=== Review Results ===[/bold green]")
    console.print(f"Files reviewed: {len(result.files)}")
    console.print(f"Issues found: {len(result.issues)}")
    console.print(f"Overall score: {result.score:.1f}/10")
    console.print(f"Duration: {result.duration:.2f}s")

    # Show file details
    if result.files:
        table = Table(title="File Reviews")
        table.add_column("File", style="cyan")
        table.add_column("Language", style="green")
        table.add_column("Score", style="yellow")
        table.add_column("Issues", style="red")

        for file_review in result.files:
            table.add_row(
                file_review.filename,
                file_review.language,
                f"{file_review.score:.1f}",
                str(len(file_review.issues)),
            )

        console.print(table)

    # Show issues
    if result.issues:
        console.print("\n[bold red]Issues Found:[/bold red]")
        for issue in result.issues:
            console.print(f"- [{issue.severity.upper()}] {issue.type}: {issue.message}")
            if issue.suggestion:
                console.print(f"  Suggestion: {issue.suggestion}")

    # Post comments to PR if not dry run
    if not config.dry_run:
        try:
            review_engine.post_review_comments(repo, pr_number, result)
            console.print("\n[green]Review comments posted to pull request[/green]")
        except Exception as e:
            console.print(f"\n[red]Failed to post review comments: {e}[/red]")
    else:
        console.print("\n[yellow]Dry run mode - no comments posted[/yellow]")


@cli.command("version")
def version():
    """Show version information"""
    console.print(f"Slay Check v{__version__}")
    console.print("Built with Python")


def main():
    """Main entry point for CLI"""
    cli()


if __name__ == "__main__":
    main()
