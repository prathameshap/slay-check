package github

import (
	"context"
	"fmt"
	"strings"

	"github.com/google/go-github/v56/github"
	"golang.org/x/oauth2"
)

// Client wraps the GitHub client with additional functionality
type Client struct {
	client *github.Client
	ctx    context.Context
}

// NewClient creates a new GitHub client
func NewClient(token string) (*Client, error) {
	if token == "" {
		return nil, fmt.Errorf("GitHub token is required")
	}

	ctx := context.Background()
	ts := oauth2.StaticTokenSource(
		&oauth2.Token{AccessToken: token},
	)
	tc := oauth2.NewClient(ctx, ts)

	return &Client{
		client: github.NewClient(tc),
		ctx:    ctx,
	}, nil
}

// PullRequest represents a GitHub pull request
type PullRequest struct {
	Number    int               `json:"number"`
	Title     string            `json:"title"`
	Body      string            `json:"body"`
	State     string            `json:"state"`
	BaseRef   string            `json:"base_ref"`
	HeadRef   string            `json:"head_ref"`
	Files     []PullRequestFile `json:"files"`
	Owner     string            `json:"owner"`
	Repo      string            `json:"repo"`
	Author    string            `json:"author"`
	CreatedAt string            `json:"created_at"`
	UpdatedAt string            `json:"updated_at"`
}

// PullRequestFile represents a file in a pull request
type PullRequestFile struct {
	Filename     string `json:"filename"`
	Status       string `json:"status"`
	Additions    int    `json:"additions"`
	Deletions    int    `json:"deletions"`
	Changes      int    `json:"changes"`
	Patch        string `json:"patch"`
	RawURL       string `json:"raw_url"`
	BlobURL      string `json:"blob_url"`
	ContentsURL  string `json:"contents_url"`
	PreviousFilename string `json:"previous_filename,omitempty"`
}

// ReviewComment represents a review comment
type ReviewComment struct {
	Path     string `json:"path"`
	Line     int    `json:"line"`
	Body     string `json:"body"`
	Severity string `json:"severity"`
	Type     string `json:"type"`
}

// GetPullRequest retrieves a pull request and its files
func (c *Client) GetPullRequest(repo string, prNumber int) (*PullRequest, error) {
	owner, repoName, err := parseRepo(repo)
	if err != nil {
		return nil, err
	}

	// Get PR details
	pr, _, err := c.client.PullRequests.Get(c.ctx, owner, repoName, prNumber)
	if err != nil {
		return nil, fmt.Errorf("failed to get pull request: %w", err)
	}

	// Get PR files
	files, _, err := c.client.PullRequests.ListFiles(c.ctx, owner, repoName, prNumber, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to get pull request files: %w", err)
	}

	// Convert to our format
	pullRequest := &PullRequest{
		Number:    pr.GetNumber(),
		Title:     pr.GetTitle(),
		Body:      pr.GetBody(),
		State:     pr.GetState(),
		BaseRef:   pr.GetBase().GetRef(),
		HeadRef:   pr.GetHead().GetRef(),
		Owner:     owner,
		Repo:      repoName,
		Author:    pr.GetUser().GetLogin(),
		CreatedAt: pr.GetCreatedAt().Format("2006-01-02T15:04:05Z"),
		UpdatedAt: pr.GetUpdatedAt().Format("2006-01-02T15:04:05Z"),
		Files:     make([]PullRequestFile, len(files)),
	}

	// Convert files
	for i, file := range files {
		pullRequest.Files[i] = PullRequestFile{
			Filename:         file.GetFilename(),
			Status:           file.GetStatus(),
			Additions:        file.GetAdditions(),
			Deletions:        file.GetDeletions(),
			Changes:          file.GetChanges(),
			Patch:            file.GetPatch(),
			RawURL:           file.GetRawURL(),
			BlobURL:          file.GetBlobURL(),
			ContentsURL:      file.GetContentsURL(),
			PreviousFilename: file.GetPreviousFilename(),
		}
	}

	return pullRequest, nil
}

// PostReviewComments posts review comments to a pull request
func (c *Client) PostReviewComments(repo string, prNumber int, reviewResult interface{}) error {
	owner, repoName, err := parseRepo(repo)
	if err != nil {
		return err
	}

	// TODO: Implement posting review comments
	// This would involve:
	// 1. Converting review results to GitHub review comments
	// 2. Posting comments using GitHub API
	// 3. Handling rate limiting and errors

	fmt.Printf("Posting review comments to %s/%s PR #%d\n", owner, repoName, prNumber)
	return nil
}

// GetFileContent retrieves the content of a file
func (c *Client) GetFileContent(owner, repo, path, ref string) (string, error) {
	fileContent, _, _, err := c.client.Repositories.GetContents(c.ctx, owner, repo, path, &github.RepositoryContentGetOptions{
		Ref: ref,
	})
	if err != nil {
		return "", fmt.Errorf("failed to get file content: %w", err)
	}

	content, err := fileContent.GetContent()
	if err != nil {
		return "", fmt.Errorf("failed to decode file content: %w", err)
	}

	return content, nil
}

// CreateReview creates a pull request review
func (c *Client) CreateReview(owner, repo string, prNumber int, event, body string, comments []*github.DraftReviewComment) error {
	review := &github.PullRequestReviewRequest{
		Event:    github.String(event), // "COMMENT", "APPROVE", "REQUEST_CHANGES"
		Body:     github.String(body),
		Comments: comments,
	}

	_, _, err := c.client.PullRequests.CreateReview(c.ctx, owner, repo, prNumber, review)
	if err != nil {
		return fmt.Errorf("failed to create review: %w", err)
	}

	return nil
}

// parseRepo parses a repository string in format "owner/repo"
func parseRepo(repo string) (owner, repoName string, err error) {
	parts := strings.Split(repo, "/")
	if len(parts) != 2 {
		return "", "", fmt.Errorf("invalid repository format: %s (expected owner/repo)", repo)
	}
	return parts[0], parts[1], nil
}
