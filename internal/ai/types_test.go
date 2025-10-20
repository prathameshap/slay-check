package ai

import (
	"context"
	"testing"
)

func TestManager(t *testing.T) {
	manager := NewManager()
	
	// Test registering provider
	provider := &MockProvider{name: "test"}
	manager.RegisterProvider("test", provider)
	
	// Test getting provider
	got, err := manager.GetProvider("test")
	if err != nil {
		t.Errorf("GetProvider() error = %v", err)
	}
	
	if got.GetName() != "test" {
		t.Errorf("Expected provider name 'test', got '%s'", got.GetName())
	}
	
	// Test getting non-existent provider
	_, err = manager.GetProvider("nonexistent")
	if err == nil {
		t.Error("Expected error for non-existent provider")
	}
	
	// Test setting default provider
	err = manager.SetDefaultProvider("test")
	if err != nil {
		t.Errorf("SetDefaultProvider() error = %v", err)
	}
	
	// Test getting default provider
	got, err = manager.GetProvider("")
	if err != nil {
		t.Errorf("GetProvider() with empty name error = %v", err)
	}
	
	if got.GetName() != "test" {
		t.Errorf("Expected default provider name 'test', got '%s'", got.GetName())
	}
}

func TestManagerReviewCode(t *testing.T) {
	manager := NewManager()
	
	provider := &MockProvider{
		name: "test",
		response: &ReviewResponse{
			Analysis: "Test analysis",
			Score:    8.5,
			Issues:   []Issue{},
		},
	}
	
	manager.RegisterProvider("test", provider)
	manager.SetDefaultProvider("test")
	
	request := ReviewRequest{
		Code:     "test code",
		Language: "go",
		FilePath: "test.go",
		Criteria: ReviewCriteria{
			AnalyzeProblem: true,
		},
	}
	
	response, err := manager.ReviewCode(context.Background(), "test", request)
	if err != nil {
		t.Errorf("ReviewCode() error = %v", err)
	}
	
	if response.Analysis != "Test analysis" {
		t.Errorf("Expected analysis 'Test analysis', got '%s'", response.Analysis)
	}
	
	if response.Score != 8.5 {
		t.Errorf("Expected score 8.5, got %f", response.Score)
	}
}

func TestGetAvailableProviders(t *testing.T) {
	manager := NewManager()
	
	// Add available provider
	availableProvider := &MockProvider{name: "available", available: true}
	manager.RegisterProvider("available", availableProvider)
	
	// Add unavailable provider
	unavailableProvider := &MockProvider{name: "unavailable", available: false}
	manager.RegisterProvider("unavailable", unavailableProvider)
	
	available := manager.GetAvailableProviders()
	
	if len(available) != 1 {
		t.Errorf("Expected 1 available provider, got %d", len(available))
	}
	
	if available[0] != "available" {
		t.Errorf("Expected available provider 'available', got '%s'", available[0])
	}
}

// MockProvider is a mock implementation of the Provider interface
type MockProvider struct {
	name     string
	response *ReviewResponse
	available bool
}

func (m *MockProvider) ReviewCode(ctx context.Context, request ReviewRequest) (*ReviewResponse, error) {
	return m.response, nil
}

func (m *MockProvider) GetName() string {
	return m.name
}

func (m *MockProvider) IsAvailable() bool {
	return m.available
}
