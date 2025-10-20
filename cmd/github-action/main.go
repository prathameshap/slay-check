package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"

	"github.com/slay-check/slay-check/internal/config"
	"github.com/slay-check/slay-check/internal/github"
	"github.com/slay-check/slay-check/internal/review"
)

func main() {
	// Load configuration
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("Failed to load configuration: %v", err)
	}

	// Get GitHub context from environment variables
	repo := os.Getenv("GITHUB_REPOSITORY")
	if repo == "" {
		log.Fatal("GITHUB_REPOSITORY environment variable is required")
	}

	prNumberStr := os.Getenv("GITHUB_PR_NUMBER")
	if prNumberStr == "" {
		// Try to get from GitHub context
		eventName := os.Getenv("GITHUB_EVENT_NAME")
		if eventName == "pull_request" {
			// Parse PR number from GitHub context
			prNumberStr = os.Getenv("GITHUB_EVENT_PATH")
			if prNumberStr != "" {
				// This would need to be parsed from the event file
				// For now, we'll require it to be set explicitly
			}
		}
	}

	if prNumberStr == "" {
		log.Fatal("GITHUB_PR_NUMBER environment variable is required")
	}

	prNumber, err := strconv.Atoi(prNumberStr)
	if err != nil {
		log.Fatalf("Invalid PR number: %v", err)
	}

	// Initialize GitHub client
	githubClient, err := github.NewClient(cfg.GitHubToken)
	if err != nil {
		log.Fatalf("Failed to create GitHub client: %v", err)
	}

	// Get pull request details
	pr, err := githubClient.GetPullRequest(repo, prNumber)
	if err != nil {
		log.Fatalf("Failed to get pull request: %v", err)
	}

	// Initialize review engine
	reviewEngine, err := review.NewEngine(cfg)
	if err != nil {
		log.Fatalf("Failed to create review engine: %v", err)
	}

	// Perform review
	fmt.Printf("Starting review of PR #%d: %s\n", pr.Number, pr.Title)
	
	reviewResult, err := reviewEngine.ReviewPullRequest(pr)
	if err != nil {
		log.Fatalf("Review failed: %v", err)
	}

	// Display results
	fmt.Printf("\n=== Review Results ===\n")
	fmt.Printf("Files reviewed: %d\n", len(reviewResult.Files))
	fmt.Printf("Issues found: %d\n", len(reviewResult.Issues))
	fmt.Printf("Overall score: %.1f/10\n", reviewResult.Score)
	fmt.Printf("Duration: %v\n", reviewResult.Duration)

	// Post comments to PR if not dry run
	if !cfg.DryRun {
		err = githubClient.PostReviewComments(repo, prNumber, reviewResult)
		if err != nil {
			log.Fatalf("Failed to post review comments: %v", err)
		}
		fmt.Println("Review comments posted to pull request")
	} else {
		fmt.Println("Dry run mode - no comments posted")
	}

	// Set GitHub Actions outputs
	setOutput("score", fmt.Sprintf("%.1f", reviewResult.Score))
	setOutput("files_reviewed", fmt.Sprintf("%d", len(reviewResult.Files)))
	setOutput("issues_found", fmt.Sprintf("%d", len(reviewResult.Issues)))
	setOutput("duration", reviewResult.Duration.String())

	// Check if review passed thresholds
	if reviewResult.Score < cfg.MinScoreThreshold {
		fmt.Printf("Review failed: Score %.1f below threshold %.1f\n", 
			reviewResult.Score, cfg.MinScoreThreshold)
		os.Exit(1)
	}

	// Count critical issues
	criticalIssues := 0
	for _, issue := range reviewResult.Issues {
		if issue.Severity == "critical" {
			criticalIssues++
		}
	}

	if criticalIssues > cfg.CriticalIssuesLimit {
		fmt.Printf("Review failed: %d critical issues exceed limit %d\n", 
			criticalIssues, cfg.CriticalIssuesLimit)
		os.Exit(1)
	}

	fmt.Println("Review completed successfully!")
}

// setOutput sets a GitHub Actions output
func setOutput(name, value string) {
	outputFile := os.Getenv("GITHUB_OUTPUT")
	if outputFile != "" {
		f, err := os.OpenFile(outputFile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
		if err == nil {
			fmt.Fprintf(f, "%s=%s\n", name, value)
			f.Close()
		}
	}
}
