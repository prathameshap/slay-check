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

// OpenAIProvider implements the Provider interface for OpenAI
type OpenAIProvider struct {
	apiKey  string
	baseURL string
	client  *http.Client
	model   string
}

// NewOpenAIProvider creates a new OpenAI provider
func NewOpenAIProvider(apiKey, model string) *OpenAIProvider {
	if model == "" {
		model = "gpt-4"
	}
	
	return &OpenAIProvider{
		apiKey:  apiKey,
		baseURL: "https://api.openai.com/v1",
		client: &http.Client{
			Timeout: 60 * time.Second,
		},
		model: model,
	}
}

// GetName returns the provider name
func (p *OpenAIProvider) GetName() string {
	return "openai"
}

// IsAvailable checks if the provider is available
func (p *OpenAIProvider) IsAvailable() bool {
	return p.apiKey != ""
}

// ReviewCode reviews code using OpenAI
func (p *OpenAIProvider) ReviewCode(ctx context.Context, request ReviewRequest) (*ReviewResponse, error) {
	prompt := p.buildPrompt(request)
	
	openAIRequest := OpenAIRequest{
		Model:       p.model,
		Messages: []OpenAIMessage{
			{
				Role:    "system",
				Content: "You are an expert code reviewer. Analyze the provided code and give comprehensive feedback.",
			},
			{
				Role:    "user",
				Content: prompt,
			},
		},
		MaxTokens:   request.MaxTokens,
		Temperature: request.Temperature,
	}

	if openAIRequest.MaxTokens == 0 {
		openAIRequest.MaxTokens = 4000
	}
	if openAIRequest.Temperature == 0 {
		openAIRequest.Temperature = 0.3
	}

	response, err := p.makeRequest(ctx, openAIRequest)
	if err != nil {
		return nil, fmt.Errorf("OpenAI API request failed: %w", err)
	}

	return p.parseResponse(response)
}

// buildPrompt builds the prompt for code review
func (p *OpenAIProvider) buildPrompt(request ReviewRequest) string {
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

// makeRequest makes a request to OpenAI API
func (p *OpenAIProvider) makeRequest(ctx context.Context, request OpenAIRequest) (*OpenAIResponse, error) {
	jsonData, err := json.Marshal(request)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "POST", p.baseURL+"/chat/completions", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+p.apiKey)

	resp, err := p.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to make request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("API request failed with status %d: %s", resp.StatusCode, string(body))
	}

	var response OpenAIResponse
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return &response, nil
}

// parseResponse parses OpenAI response into ReviewResponse
func (p *OpenAIProvider) parseResponse(response *OpenAIResponse) (*ReviewResponse, error) {
	if len(response.Choices) == 0 {
		return nil, fmt.Errorf("no response from OpenAI")
	}

	content := response.Choices[0].Message.Content
	
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

// OpenAI API types
type OpenAIRequest struct {
	Model       string          `json:"model"`
	Messages    []OpenAIMessage `json:"messages"`
	MaxTokens   int             `json:"max_tokens,omitempty"`
	Temperature float64         `json:"temperature,omitempty"`
}

type OpenAIMessage struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type OpenAIResponse struct {
	Choices []OpenAIChoice `json:"choices"`
}

type OpenAIChoice struct {
	Message OpenAIMessage `json:"message"`
}
