package cli

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
	"github.com/slay-check/slay-check/internal/config"
	"github.com/slay-check/slay-check/internal/github"
	"github.com/slay-check/slay-check/internal/review"
)

// App represents the CLI application
type App struct {
	config *config.Config
	rootCmd *cobra.Command
}

// NewApp creates a new CLI application
func NewApp(cfg *config.Config) *App {
	app := &App{
		config: cfg,
	}

	app.rootCmd = &cobra.Command{
		Use:   "slay-check",
		Short: "AI-powered code review tool",
		Long:  "Slay Check is a high-performance AI code review tool for GitHub Actions and local development.",
	}

	// Add subcommands
	app.rootCmd.AddCommand(app.reviewCommand())
	app.rootCmd.AddCommand(app.configCommand())
	app.rootCmd.AddCommand(app.versionCommand())

	return app
}

// Execute runs the CLI application
func (a *App) Execute() error {
	return a.rootCmd.Execute()
}

// reviewCommand creates the review command
func (a *App) reviewCommand() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "review",
		Short: "Review code changes",
		Long:  "Analyze code changes using AI to provide comprehensive code review feedback.",
		RunE:  a.runReview,
	}

	cmd.Flags().IntP("pr", "p", 0, "Pull request number to review")
	cmd.Flags().StringP("repo", "r", "", "Repository in format owner/repo")
	cmd.Flags().StringP("base", "b", "main", "Base branch for comparison")
	cmd.Flags().StringP("head", "h", "", "Head branch or commit")
	cmd.Flags().BoolP("local", "l", false, "Review local changes (git diff)")

	return cmd
}

// configCommand creates the config command
func (a *App) configCommand() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "config",
		Short: "Configuration management",
		Long:  "Manage Slay Check configuration settings.",
	}

	cmd.AddCommand(&cobra.Command{
		Use:   "init",
		Short: "Initialize configuration file",
		RunE:  a.initConfig,
	})

	cmd.AddCommand(&cobra.Command{
		Use:   "show",
		Short: "Show current configuration",
		RunE:  a.showConfig,
	})

	return cmd
}

// versionCommand creates the version command
func (a *App) versionCommand() *cobra.Command {
	return &cobra.Command{
		Use:   "version",
		Short: "Show version information",
		Run: func(cmd *cobra.Command, args []string) {
			fmt.Println("Slay Check v1.0.0")
			fmt.Println("Built with Go")
		},
	}
}

// runReview executes the review command
func (a *App) runReview(cmd *cobra.Command, args []string) error {
	pr, _ := cmd.Flags().GetInt("pr")
	repo, _ := cmd.Flags().GetString("repo")
	base, _ := cmd.Flags().GetString("base")
	head, _ := cmd.Flags().GetString("head")
	local, _ := cmd.Flags().GetBool("local")

	if local {
		return a.reviewLocalChanges()
	}

	if pr > 0 {
		return a.reviewPullRequest(pr, repo)
	}

	return fmt.Errorf("please specify either --pr for pull request review or --local for local changes")
}

// reviewLocalChanges reviews local git changes
func (a *App) reviewLocalChanges() error {
	fmt.Println("Reviewing local changes...")
	
	// TODO: Implement local git diff analysis
	// This would involve:
	// 1. Running git diff to get changes
	// 2. Parsing the diff
	// 3. Running AI review
	// 4. Displaying results
	
	return fmt.Errorf("local review not yet implemented")
}

// reviewPullRequest reviews a GitHub pull request
func (a *App) reviewPullRequest(prNumber int, repo string) error {
	fmt.Printf("Reviewing pull request #%d in %s...\n", prNumber, repo)
	
	// Initialize GitHub client
	githubClient, err := github.NewClient(a.config.GitHubToken)
	if err != nil {
		return fmt.Errorf("failed to create GitHub client: %w", err)
	}

	// Get PR details
	pr, err := githubClient.GetPullRequest(repo, prNumber)
	if err != nil {
		return fmt.Errorf("failed to get pull request: %w", err)
	}

	// Initialize review engine
	reviewEngine, err := review.NewEngine(a.config)
	if err != nil {
		return fmt.Errorf("failed to create review engine: %w", err)
	}

	// Perform review
	reviewResult, err := reviewEngine.ReviewPullRequest(pr)
	if err != nil {
		return fmt.Errorf("review failed: %w", err)
	}

	// Display results
	fmt.Println("\n=== Review Results ===")
	fmt.Printf("Files reviewed: %d\n", len(reviewResult.Files))
	fmt.Printf("Issues found: %d\n", len(reviewResult.Issues))
	fmt.Printf("Overall score: %.1f/10\n", reviewResult.Score)

	// Post comments to PR if not dry run
	if !a.config.DryRun {
		err = githubClient.PostReviewComments(repo, prNumber, reviewResult)
		if err != nil {
			return fmt.Errorf("failed to post review comments: %w", err)
		}
		fmt.Println("Review comments posted to pull request")
	} else {
		fmt.Println("Dry run mode - no comments posted")
	}

	return nil
}

// initConfig initializes the configuration file
func (a *App) initConfig(cmd *cobra.Command, args []string) error {
	configPath := "slay-check.yaml"
	
	if _, err := os.Stat(configPath); err == nil {
		fmt.Printf("Configuration file %s already exists\n", configPath)
		return nil
	}

	err := a.config.Save(configPath)
	if err != nil {
		return fmt.Errorf("failed to save configuration: %w", err)
	}

	fmt.Printf("Configuration file created: %s\n", configPath)
	fmt.Println("Please edit the file and add your API tokens:")
	fmt.Println("- ai_token: Your AI provider API token")
	fmt.Println("- github_token: Your GitHub personal access token")

	return nil
}

// showConfig displays the current configuration
func (a *App) showConfig(cmd *cobra.Command, args []string) error {
	fmt.Println("Current Configuration:")
	fmt.Printf("AI Provider: %s\n", a.config.AIProvider)
	fmt.Printf("Review Criteria:\n")
	fmt.Printf("  - Analyze Problem: %t\n", a.config.ReviewCriteria.AnalyzeProblem)
	fmt.Printf("  - Algorithm Analysis: %t\n", a.config.ReviewCriteria.AlgorithmAnalysis)
	fmt.Printf("  - Best Approaches: %t\n", a.config.ReviewCriteria.BestApproaches)
	fmt.Printf("  - Complexity Analysis: %t\n", a.config.ReviewCriteria.ComplexityAnalysis)
	fmt.Printf("  - Risk Assessment: %t\n", a.config.ReviewCriteria.RiskAssessment)
	fmt.Printf("  - Security Review: %t\n", a.config.ReviewCriteria.SecurityReview)
	fmt.Printf("  - Performance Review: %t\n", a.config.ReviewCriteria.PerformanceReview)
	fmt.Printf("Max File Size: %d lines\n", a.config.MaxFileSize)
	fmt.Printf("Max Files Per PR: %d\n", a.config.MaxFilesPerPR)
	fmt.Printf("Verbose: %t\n", a.config.Verbose)
	fmt.Printf("Dry Run: %t\n", a.config.DryRun)

	return nil
}
