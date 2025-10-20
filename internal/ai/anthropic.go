package ai

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

// AnthropicProvider implements the Provider interface for Anthropic Claude
type AnthropicProvider struct {
	apiKey  string
	baseURL string
	client  *http.Client
	model   string
}

// NewAnthropicProvider creates a new Anthropic provider
func NewAnthropicProvider(apiKey, model string) *AnthropicProvider {
	if model == "" {
		model = "claude-3-sonnet-20240229"
	}
	
	return &AnthropicProvider{
		apiKey:  apiKey,
		baseURL: "https://api.anthropic.com/v1",
		client: &http.Client{
			Timeout: 60 * time.Second,
		},
		model: model,
	}
}

// GetName returns the provider name
func (p *AnthropicProvider) GetName() string {
	return "anthropic"
}

// IsAvailable checks if the provider is available
func (p *AnthropicProvider) IsAvailable() bool {
	return p.apiKey != ""
}

// ReviewCode reviews code using Anthropic Claude
func (p *AnthropicProvider) ReviewCode(ctx context.Context, request ReviewRequest) (*ReviewResponse, error) {
	prompt := p.buildPrompt(request)
	
	anthropicRequest := AnthropicRequest{
		Model:     p.model,
		MaxTokens: request.MaxTokens,
		Messages: []AnthropicMessage{
			{
				Role:    "user",
				Content: prompt,
			},
		},
	}

	if anthropicRequest.MaxTokens == 0 {
		anthropicRequest.MaxTokens = 4000
	}

	response, err := p.makeRequest(ctx, anthropicRequest)
	if err != nil {
		return nil, fmt.Errorf("Anthropic API request failed: %w", err)
	}

	return p.parseResponse(response)
}

// buildPrompt builds the prompt for code review
func (p *AnthropicProvider) buildPrompt(request ReviewRequest) string {
	prompt := fmt.Sprintf("Please review the following %s code:\n\n", request.Language)
	prompt += fmt.Sprintf("File: %s\n\n", request.FilePath)
	
	if request.Context != "" {
		prompt += fmt.Sprintf("Context: %s\n\n", request.Context)
	}
	
	prompt += "Code:\n```" + request.Language + "\n" + request.Code + "\n```\n\n"
	
	prompt += "Please analyze the code based on these criteria:\n"
	
	if request.Criteria.AnalyzeProblem {
		prompt += "- Analyze the problem the code is solving\n"
	}
	if request.Criteria.AlgorithmAnalysis {
		prompt += "- Analyze the algorithm used for the logic\n"
	}
	if request.Criteria.BestApproaches {
		prompt += "- Suggest plausible best approaches for the code\n"
	}
	if request.Criteria.ComplexityAnalysis {
		prompt += "- Analyze time and space complexity\n"
	}
	if request.Criteria.RiskAssessment {
		prompt += "- Identify risks and potential issues\n"
	}
	if request.Criteria.SecurityReview {
		prompt += "- Review for security vulnerabilities\n"
	}
	if request.Criteria.PerformanceReview {
		prompt += "- Review for performance issues\n"
	}
	
	prompt += "\nPlease provide your analysis in JSON format with the following structure:\n"
	prompt += `{
  "analysis": "Detailed analysis of the code",
  "score": 8.5,
  "issues": [
    {
      "type": "performance",
      "severity": "medium",
      "line": 10,
      "message": "Inefficient loop",
      "suggestion": "Use a more efficient algorithm",
      "confidence": 0.9
    }
  ],
  "suggestions": ["Suggestion 1", "Suggestion 2"],
  "complexity": {
    "time_complexity": "O(n²)",
    "space_complexity": "O(1)",
    "cyclomatic_complexity": 5,
    "maintainability": "good"
  },
  "confidence": 0.85
}`
	
	return prompt
}

// makeRequest makes a request to Anthropic API
func (p *AnthropicProvider) makeRequest(ctx context.Context, request AnthropicRequest) (*AnthropicResponse, error) {
	jsonData, err := json.Marshal(request)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "POST", p.baseURL+"/messages", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("x-api-key", p.apiKey)
	req.Header.Set("anthropic-version", "2023-06-01")

	resp, err := p.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to make request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("API request failed with status %d: %s", resp.StatusCode, string(body))
	}

	var response AnthropicResponse
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return &response, nil
}

// parseResponse parses Anthropic response into ReviewResponse
func (p *AnthropicProvider) parseResponse(response *AnthropicResponse) (*ReviewResponse, error) {
	if len(response.Content) == 0 {
		return nil, fmt.Errorf("no response from Anthropic")
	}

	content := response.Content[0].Text
	
	// Try to parse as JSON first
	var reviewResp ReviewResponse
	if err := json.Unmarshal([]byte(content), &reviewResp); err == nil {
		return &reviewResp, nil
	}

	// If JSON parsing fails, create a basic response
	return &ReviewResponse{
		Analysis: content,
		Score:    7.0, // Default score
		Issues:   []Issue{},
		Suggestions: []string{},
		Complexity: Complexity{
			Maintainability: "unknown",
		},
		Confidence: 0.7,
	}, nil
}

// Anthropic API types
type AnthropicRequest struct {
	Model     string              `json:"model"`
	MaxTokens int                 `json:"max_tokens"`
	Messages  []AnthropicMessage  `json:"messages"`
}

type AnthropicMessage struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type AnthropicResponse struct {
	Content []AnthropicContent `json:"content"`
}

type AnthropicContent struct {
	Text string `json:"text"`
}
