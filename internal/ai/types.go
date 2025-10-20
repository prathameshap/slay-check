package ai

import (
	"context"
	"fmt"
)

// Provider defines the interface for AI providers
type Provider interface {
	ReviewCode(ctx context.Context, request ReviewRequest) (*ReviewResponse, error)
	GetName() string
	IsAvailable() bool
}

// ReviewRequest represents a code review request
type ReviewRequest struct {
	Code        string            `json:"code"`
	Language    string            `json:"language"`
	FilePath    string            `json:"file_path"`
	Context     string            `json:"context"`
	Criteria    ReviewCriteria    `json:"criteria"`
	MaxTokens   int              `json:"max_tokens,omitempty"`
	Temperature float64          `json:"temperature,omitempty"`
}

// ReviewResponse represents the AI's review response
type ReviewResponse struct {
	Analysis     string    `json:"analysis"`
	Score        float64   `json:"score"`
	Issues       []Issue   `json:"issues"`
	Suggestions  []string  `json:"suggestions"`
	Complexity   Complexity `json:"complexity"`
	Confidence   float64   `json:"confidence"`
}

// Issue represents a code issue found by the AI
type Issue struct {
	Type        string `json:"type"`        // bug, performance, security, style
	Severity    string `json:"severity"`    // low, medium, high, critical
	Line        int    `json:"line"`
	Message     string `json:"message"`
	Suggestion  string `json:"suggestion"`
	Confidence  float64 `json:"confidence"`
}

// Complexity represents code complexity analysis
type Complexity struct {
	TimeComplexity   string `json:"time_complexity"`
	SpaceComplexity  string `json:"space_complexity"`
	CyclomaticComplexity int `json:"cyclomatic_complexity"`
	Maintainability  string `json:"maintainability"`
}

// ReviewCriteria defines what to review
type ReviewCriteria struct {
	AnalyzeProblem     bool `json:"analyze_problem"`
	AlgorithmAnalysis  bool `json:"algorithm_analysis"`
	BestApproaches     bool `json:"best_approaches"`
	ComplexityAnalysis bool `json:"complexity_analysis"`
	RiskAssessment     bool `json:"risk_assessment"`
	SecurityReview     bool `json:"security_review"`
	PerformanceReview  bool `json:"performance_review"`
}

// Manager manages multiple AI providers
type Manager struct {
	providers map[string]Provider
	defaultProvider string
}

// NewManager creates a new AI provider manager
func NewManager() *Manager {
	return &Manager{
		providers: make(map[string]Provider),
	}
}

// RegisterProvider registers an AI provider
func (m *Manager) RegisterProvider(name string, provider Provider) {
	m.providers[name] = provider
}

// SetDefaultProvider sets the default provider
func (m *Manager) SetDefaultProvider(name string) error {
	if _, exists := m.providers[name]; !exists {
		return fmt.Errorf("provider %s not registered", name)
	}
	m.defaultProvider = name
	return nil
}

// GetProvider returns a provider by name
func (m *Manager) GetProvider(name string) (Provider, error) {
	if name == "" {
		name = m.defaultProvider
	}
	
	provider, exists := m.providers[name]
	if !exists {
		return nil, fmt.Errorf("provider %s not found", name)
	}
	
	return provider, nil
}

// ReviewCode reviews code using the specified provider
func (m *Manager) ReviewCode(ctx context.Context, providerName string, request ReviewRequest) (*ReviewResponse, error) {
	provider, err := m.GetProvider(providerName)
	if err != nil {
		return nil, err
	}
	
	return provider.ReviewCode(ctx, request)
}

// GetAvailableProviders returns list of available providers
func (m *Manager) GetAvailableProviders() []string {
	var available []string
	for name, provider := range m.providers {
		if provider.IsAvailable() {
			available = append(available, name)
		}
	}
	return available
}
