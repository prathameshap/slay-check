package review

import (
	"context"
	"fmt"
	"path/filepath"
	"strings"
	"time"

	"github.com/slay-check/slay-check/internal/ai"
	"github.com/slay-check/slay-check/internal/config"
	"github.com/slay-check/slay-check/internal/github"
)

// Engine handles the code review process
type Engine struct {
	config      *config.Config
	aiManager   *ai.Manager
	githubClient *github.Client
}

// ReviewResult represents the result of a code review
type ReviewResult struct {
	PullRequest *github.PullRequest `json:"pull_request"`
	Files       []FileReview         `json:"files"`
	Issues      []ai.Issue           `json:"issues"`
	Score       float64              `json:"score"`
	Summary     string               `json:"summary"`
	Duration    time.Duration        `json:"duration"`
}

// FileReview represents the review of a single file
type FileReview struct {
	Filename    string      `json:"filename"`
	Language    string      `json:"language"`
	Score       float64     `json:"score"`
	Issues      []ai.Issue  `json:"issues"`
	Suggestions []string    `json:"suggestions"`
	Complexity  ai.Complexity `json:"complexity"`
	Analysis    string      `json:"analysis"`
}

// NewEngine creates a new review engine
func NewEngine(cfg *config.Config) (*Engine, error) {
	// Initialize AI manager
	aiManager := ai.NewManager()
	
	// Register AI providers based on configuration
	switch cfg.AIProvider {
	case "openai":
		provider := ai.NewOpenAIProvider(cfg.AIToken, "gpt-4")
		aiManager.RegisterProvider("openai", provider)
		aiManager.SetDefaultProvider("openai")
	case "anthropic":
		provider := ai.NewAnthropicProvider(cfg.AIToken, "claude-3-sonnet-20240229")
		aiManager.RegisterProvider("anthropic", provider)
		aiManager.SetDefaultProvider("anthropic")
	default:
		return nil, fmt.Errorf("unsupported AI provider: %s", cfg.AIProvider)
	}

	// Initialize GitHub client
	githubClient, err := github.NewClient(cfg.GitHubToken)
	if err != nil {
		return nil, fmt.Errorf("failed to create GitHub client: %w", err)
	}

	return &Engine{
		config:      cfg,
		aiManager:   aiManager,
		githubClient: githubClient,
	}, nil
}

// ReviewPullRequest reviews a pull request
func (e *Engine) ReviewPullRequest(pr *github.PullRequest) (*ReviewResult, error) {
	startTime := time.Now()
	
	result := &ReviewResult{
		PullRequest: pr,
		Files:       make([]FileReview, 0),
		Issues:      make([]ai.Issue, 0),
		Score:       0.0,
		Summary:     "",
	}

	// Filter files based on configuration
	filteredFiles := e.filterFiles(pr.Files)
	
	if len(filteredFiles) == 0 {
		result.Summary = "No files to review after filtering"
		result.Duration = time.Since(startTime)
		return result, nil
	}

	// Review each file
	totalScore := 0.0
	fileCount := 0

	for _, file := range filteredFiles {
		fileReview, err := e.reviewFile(file, pr)
		if err != nil {
			fmt.Printf("Warning: Failed to review file %s: %v\n", file.Filename, err)
			continue
		}

		result.Files = append(result.Files, *fileReview)
		result.Issues = append(result.Issues, fileReview.Issues...)
		
		totalScore += fileReview.Score
		fileCount++
	}

	// Calculate overall score
	if fileCount > 0 {
		result.Score = totalScore / float64(fileCount)
	}

	// Generate summary
	result.Summary = e.generateSummary(result)
	result.Duration = time.Since(startTime)

	return result, nil
}

// filterFiles filters files based on configuration
func (e *Engine) filterFiles(files []github.PullRequestFile) []github.PullRequestFile {
	var filtered []github.PullRequestFile

	for _, file := range files {
		// Skip if file is too large
		if file.Changes > e.config.MaxFileSize {
			continue
		}

		// Skip if matches exclude patterns
		if e.shouldExcludeFile(file.Filename) {
			continue
		}

		// Skip deleted files
		if file.Status == "removed" {
			continue
		}

		filtered = append(filtered, file)
	}

	// Limit number of files
	if len(filtered) > e.config.MaxFilesPerPR {
		filtered = filtered[:e.config.MaxFilesPerPR]
	}

	return filtered
}

// shouldExcludeFile checks if a file should be excluded
func (e *Engine) shouldExcludeFile(filename string) bool {
	for _, pattern := range e.config.ExcludePatterns {
		matched, _ := filepath.Match(pattern, filename)
		if matched {
			return true
		}
	}
	return false
}

// reviewFile reviews a single file
func (e *Engine) reviewFile(file github.PullRequestFile, pr *github.PullRequest) (*FileReview, error) {
	// Determine language from file extension
	language := e.detectLanguage(file.Filename)
	
	// Extract code from patch
	code := e.extractCodeFromPatch(file.Patch)
	
	if code == "" {
		return &FileReview{
			Filename: file.Filename,
			Language: language,
			Score:    5.0,
			Issues:   []ai.Issue{},
			Suggestions: []string{"No code changes detected"},
			Complexity: ai.Complexity{Maintainability: "unknown"},
			Analysis: "No code changes to review",
		}, nil
	}

	// Prepare review request
	request := ai.ReviewRequest{
		Code:     code,
		Language: language,
		FilePath: file.Filename,
		Context:  fmt.Sprintf("PR #%d: %s", pr.Number, pr.Title),
		Criteria: ai.ReviewCriteria{
			AnalyzeProblem:     e.config.ReviewCriteria.AnalyzeProblem,
			AlgorithmAnalysis:  e.config.ReviewCriteria.AlgorithmAnalysis,
			BestApproaches:     e.config.ReviewCriteria.BestApproaches,
			ComplexityAnalysis: e.config.ReviewCriteria.ComplexityAnalysis,
			RiskAssessment:     e.config.ReviewCriteria.RiskAssessment,
			SecurityReview:     e.config.ReviewCriteria.SecurityReview,
			PerformanceReview:  e.config.ReviewCriteria.PerformanceReview,
		},
		MaxTokens:   4000,
		Temperature: 0.3,
	}

	// Get AI review
	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()

	response, err := e.aiManager.ReviewCode(ctx, e.config.AIProvider, request)
	if err != nil {
		return nil, fmt.Errorf("AI review failed: %w", err)
	}

	// Create file review
	fileReview := &FileReview{
		Filename:    file.Filename,
		Language:    language,
		Score:       response.Score,
		Issues:      response.Issues,
		Suggestions: response.Suggestions,
		Complexity:  response.Complexity,
		Analysis:    response.Analysis,
	}

	return fileReview, nil
}

// detectLanguage detects the programming language from filename
func (e *Engine) detectLanguage(filename string) string {
	ext := strings.ToLower(filepath.Ext(filename))
	
	languageMap := map[string]string{
		".go":   "go",
		".js":   "javascript",
		".ts":   "typescript",
		".py":   "python",
		".java": "java",
		".cpp":  "cpp",
		".c":    "c",
		".cs":   "csharp",
		".php":  "php",
		".rb":   "ruby",
		".rs":   "rust",
		".swift": "swift",
		".kt":   "kotlin",
		".scala": "scala",
		".sh":   "bash",
		".yaml": "yaml",
		".yml":  "yaml",
		".json": "json",
		".xml":  "xml",
		".html": "html",
		".css":  "css",
		".scss": "scss",
		".sql":  "sql",
		".md":   "markdown",
		".txt":  "text",
	}

	if lang, exists := languageMap[ext]; exists {
		return lang
	}
	
	return "text"
}

// extractCodeFromPatch extracts code from git patch
func (e *Engine) extractCodeFromPatch(patch string) string {
	if patch == "" {
		return ""
	}

	lines := strings.Split(patch, "\n")
	var codeLines []string

	for _, line := range lines {
		if strings.HasPrefix(line, "+") && !strings.HasPrefix(line, "+++") {
			// Remove the + prefix and add the line
			codeLines = append(codeLines, line[1:])
		}
	}

	return strings.Join(codeLines, "\n")
}

// generateSummary generates a summary of the review
func (e *Engine) generateSummary(result *ReviewResult) string {
	summary := fmt.Sprintf("## Code Review Summary\n\n")
	summary += fmt.Sprintf("**Overall Score:** %.1f/10\n\n", result.Score)
	summary += fmt.Sprintf("**Files Reviewed:** %d\n", len(result.Files))
	summary += fmt.Sprintf("**Issues Found:** %d\n\n", len(result.Issues))

	if len(result.Issues) > 0 {
		summary += "### Issues by Severity\n"
		
		severityCount := make(map[string]int)
		for _, issue := range result.Issues {
			severityCount[issue.Severity]++
		}

		for severity, count := range severityCount {
			summary += fmt.Sprintf("- **%s:** %d\n", strings.Title(severity), count)
		}
		summary += "\n"
	}

	summary += "### Top Suggestions\n"
	suggestionCount := 0
	for _, file := range result.Files {
		for _, suggestion := range file.Suggestions {
			if suggestionCount >= 5 {
				break
			}
			summary += fmt.Sprintf("- %s\n", suggestion)
			suggestionCount++
		}
		if suggestionCount >= 5 {
			break
		}
	}

	return summary
}
