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

from . import __version__
from .config import Config
from .local_review import perform_local_git_review
from .review import ReviewEngine

console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version=__version__)
def cli(ctx: click.Context):
    """Slay Check — AI-powered code review (CLI, GitHub Actions, MCP).

    \b
    Fastest path (local, free, no API key):
      slay-check setup && slay-check quick

    Common commands:
      slay-check quick              # same as: review --local
      slay-check review --local     # review unstaged git changes
      slay-check review --repo o/r --pr 42
      slay-check config init       # interactive wizard
    """
    if ctx.invoked_subcommand is None and not _argv_requests_help():
        _print_welcome()


def _argv_requests_help() -> bool:
    return any(a in ("--help", "-h") for a in sys.argv[1:])


def _print_welcome() -> None:
    """Shown when you run `slay-check` with no subcommand."""
    console.print(
        Panel.fit(
            "[bold cyan]Slay Check[/bold cyan] — AI code review\n\n"
            "[bold]Fastest start (free, local):[/bold]\n"
            "  [green]slay-check setup[/green]   → writes "
            "[cyan]slay-check.yaml[/cyan] for Ollama\n"
            "  [green]slay-check quick[/green]    → reviews [dim]git diff[/dim] "
            "(need Ollama running)\n\n"
            "[bold]One-liners:[/bold]\n"
            "  [dim]slay-check review --local[/dim]           · unstaged changes\n"
            "  [dim]slay-check review --local --staged[/dim] · staged only\n"
            "  [dim]slay-check config init[/dim]             · full wizard\n\n"
            "Run [green]slay-check --help[/green] for all commands.",
            title="Quick start",
            border_style="cyan",
        )
    )


def _write_minimal_config(
    path: str, provider: str, *, review_preset: str = "standard"
) -> None:
    """Write a small slay-check.yaml without secrets (tokens via env)."""
    import yaml

    data: dict = {"review_preset": review_preset}
    pl = provider.lower()
    if pl in ("github", "github_models"):
        data["ai_provider"] = "github"
        data["ai_model"] = "gpt-4o"
    elif pl == "ollama":
        data["ai_provider"] = "ollama"
        data["ai_model"] = "llama3.2"
    elif pl == "openai":
        data["ai_provider"] = "openai"
        data["ai_model"] = "gpt-4o"
    else:
        data["ai_provider"] = pl

    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, indent=2, sort_keys=False)


@cli.command("setup")
@click.option(
    "--path", default="slay-check.yaml", help="Where to write the config file"
)
@click.option(
    "--provider",
    type=click.Choice(["ollama", "github", "openai"], case_sensitive=False),
    default="ollama",
    show_default=True,
    help="ollama = no cloud API key. github = GitHub Models (PAT). openai = OpenAI API key.",
)
def setup(path: str, provider: str):
    """Create minimal slay-check.yaml in one step (no prompts)."""
    if os.path.exists(path):
        console.print(f"[yellow]{path} already exists — not overwriting.[/yellow]")
        console.print("Remove the file or run [cyan]slay-check config init[/cyan].")
        return

    p = provider.lower()
    _write_minimal_config(path, p)

    console.print(f"[green]Wrote {path}[/green] ([cyan]{p}[/cyan])\n")
    if p == "ollama":
        console.print(
            "[bold]Next:[/bold] install Ollama from [link=https://ollama.com]"
            "ollama.com[/link], run [green]ollama pull llama3.2[/green], "
            "then [green]slay-check quick[/green]."
        )
    elif p == "github":
        console.print(
            "[bold]Next:[/bold] set a GitHub PAT (never commit secrets):\n"
            "  [dim]export SLAY_CHECK_AI_TOKEN=ghp_...[/dim]\n"
            "  [green]slay-check quick[/green]"
        )
    else:
        console.print(
            "[bold]Next:[/bold] set your OpenAI key:\n"
            "  [dim]export SLAY_CHECK_AI_TOKEN=sk-...[/dim]\n"
            "  [green]slay-check quick[/green]"
        )


@cli.command("quick")
@click.pass_context
@click.option(
    "--staged",
    is_flag=True,
    help="Review staged changes only (same as review --local --staged).",
)
@click.option("--verbose", is_flag=True, help="Verbose logging")
def quick_cmd(ctx: click.Context, staged: bool, verbose: bool):
    """Review local git diff — shortest command (same as: review --local)."""
    ctx.invoke(
        review,
        pr=None,
        repo=None,
        local=True,
        staged=staged,
        verbose=verbose,
        dry_run=False,
    )


@cli.group()
def config():
    """Manage slay-check.yaml configuration."""
    pass


@config.command("init")
@click.option("--path", default="slay-check.yaml", help="Configuration file path")
@click.option(
    "--quick",
    is_flag=True,
    help="Write minimal config in one step (same idea as: slay-check setup).",
)
@click.option(
    "--provider",
    type=click.Choice(["ollama", "github", "openai"], case_sensitive=False),
    default="ollama",
    show_default=True,
    help="Used with --quick only: backend to enable.",
)
def init_config(path: str, quick: bool, provider: str):
    """Initialize configuration file (interactive wizard, or use --quick)."""
    if os.path.exists(path):
        console.print(f"[yellow]Configuration file {path} already exists[/yellow]")
        return

    if quick:
        _write_minimal_config(path, provider.lower())
        console.print(f"[green]Wrote {path}[/green] ([cyan]{provider}[/cyan])")
        if provider.lower() == "ollama":
            console.print(
                "Next: [green]ollama pull llama3.2[/green] "
                "then [green]slay-check quick[/green]"
            )
        elif provider.lower() == "github":
            console.print(
                "Next: [dim]export SLAY_CHECK_AI_TOKEN=ghp_...[/dim] "
                "then [green]slay-check quick[/green]"
            )
        else:
            console.print(
                "Next: [dim]export SLAY_CHECK_AI_TOKEN=sk-...[/dim] "
                "then [green]slay-check quick[/green]"
            )
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
                Panel(
                    "Use one of:\n"
                    "  [green]slay-check quick[/green]              · review local "
                    "[dim]git diff[/dim]\n"
                    "  [green]slay-check review --local[/green]         · same as above\n"
                    "  [green]slay-check review --repo o/r --pr N[/green]"
                    "  · GitHub PR\n\n"
                    "[dim]First time? [green]slay-check setup[/green] "
                    "then [green]slay-check quick[/green][/dim]",
                    title="What to run",
                    border_style="cyan",
                )
            )
            sys.exit(1)

        # Validate configuration
        config.validate(require_github_token=not local)

        if local:
            review_local_changes(config, staged=staged)
        else:
            review_pull_request(config, repo, pr)

    except Exception as e:
        _print_friendly_error(e)
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def _print_friendly_error(exc: Exception) -> None:
    """Show copy-paste fixes for common setup mistakes."""
    msg = str(exc).lower()
    if "token" in msg or "api key" in msg:
        console.print(
            Panel(
                "[bold]Missing credentials[/bold]\n\n"
                "[dim]Free local (Ollama, no cloud key):[/dim]\n"
                "  [green]slay-check setup[/green]   # then: ollama pull llama3.2\n\n"
                "[dim]Cloud API:[/dim]\n"
                "  [dim]export SLAY_CHECK_AI_TOKEN=...[/dim]\n\n"
                "[dim]GitHub Models (free with PAT):[/dim]\n"
                "  [dim]export SLAY_CHECK_AI_PROVIDER=github[/dim]\n"
                "  [dim]export SLAY_CHECK_AI_TOKEN=ghp_...[/dim]",
                title="Tip",
                border_style="yellow",
            )
        )
    if "github token" in msg and "local" not in msg:
        console.print(
            "[dim]For PR review in terminal, set SLAY_CHECK_GITHUB_TOKEN. "
            "For local diff only, use [green]slay-check quick[/green] (no GitHub token)."
            "[/dim]\n"
        )


def review_local_changes(config: Config, *, staged: bool = False) -> None:
    """Review local git changes."""
    label = "staged" if staged else "unstaged"
    console.print(f"[yellow]Reviewing {label} local changes...[/yellow]")
    text = perform_local_git_review(config, staged=staged)
    console.print(text)

    if "No local changes" in text or "No file patches" in text:
        return
    console.print("\n[bold green]=== Local Review Complete ===[/bold green]")


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
