"""
CLI interface for Slay Check.
"""

import os
import sys
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .config import Config
from .github_client import GitHubClient
from .review import ReviewEngine

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Slay Check - AI Code Review Tool"""
    pass


@cli.group()
def config():
    """Configuration management"""
    pass


@config.command("init")
@click.option("--path", default="slay-check.yaml", help="Configuration file path")
def init_config(path: str):
    """Initialize configuration file"""
    if os.path.exists(path):
        console.print(f"[yellow]Configuration file {path} already exists[/yellow]")
        return

    config = Config()
    config.save(path)

    console.print(f"[green]Configuration file created: {path}[/green]")
    console.print("\n[yellow]Please edit the file and add your API tokens:[/yellow]")
    console.print("- ai_token: Your AI provider API token")
    console.print("- github_token: Your GitHub personal access token")


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
@click.option("--verbose", is_flag=True, help="Enable verbose output")
@click.option("--dry-run", is_flag=True, help="Don't post comments, just show results")
def review(
    pr: Optional[int], repo: Optional[str], local: bool, verbose: bool, dry_run: bool
):
    """Review code changes"""
    try:
        # Load configuration
        config = Config.load()

        # Override with CLI options
        if verbose:
            config.verbose = True
        if dry_run:
            config.dry_run = True

        if not local and not (pr and repo):
            console.print(
                "[red]Please specify either --pr and --repo for pull request review or --local for local changes[/red]"
            )
            sys.exit(1)

        # Validate configuration
        config.validate()

        if local:
            review_local_changes(config)
        else:
            review_pull_request(config, repo, pr)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def review_local_changes(config: Config):
    """Review local git changes"""
    console.print("[yellow]Reviewing local changes...[/yellow]")

    # TODO: Implement local git diff analysis
    # This would involve:
    # 1. Running git diff to get changes
    # 2. Parsing the diff
    # 3. Running AI review
    # 4. Displaying results

    console.print("[red]Local review not yet implemented[/red]")


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
    console.print("Slay Check v1.0.0")
    console.print("Built with Python")


def main():
    """Main entry point for CLI"""
    cli()


if __name__ == "__main__":
    main()
