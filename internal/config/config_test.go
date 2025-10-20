package config

import (
	"os"
	"testing"
)

func TestDefaultConfig(t *testing.T) {
	cfg := DefaultConfig()
	
	if cfg.AIProvider != "openai" {
		t.Errorf("Expected AIProvider to be 'openai', got '%s'", cfg.AIProvider)
	}
	
	if !cfg.ReviewCriteria.AnalyzeProblem {
		t.Error("Expected AnalyzeProblem to be true")
	}
	
	if cfg.MaxFileSize != 10000 {
		t.Errorf("Expected MaxFileSize to be 10000, got %d", cfg.MaxFileSize)
	}
	
	if cfg.MaxFilesPerPR != 50 {
		t.Errorf("Expected MaxFilesPerPR to be 50, got %d", cfg.MaxFilesPerPR)
	}
}

func TestConfigValidation(t *testing.T) {
	tests := []struct {
		name    string
		config  *Config
		wantErr bool
	}{
		{
			name: "valid config",
			config: &Config{
				AIProvider:  "openai",
				AIToken:     "test-token",
				GitHubToken: "github-token",
			},
			wantErr: false,
		},
		{
			name: "missing AI provider",
			config: &Config{
				AIToken:     "test-token",
				GitHubToken: "github-token",
			},
			wantErr: true,
		},
		{
			name: "missing AI token",
			config: &Config{
				AIProvider:  "openai",
				GitHubToken: "github-token",
			},
			wantErr: true,
		},
		{
			name: "missing GitHub token",
			config: &Config{
				AIProvider: "openai",
				AIToken:    "test-token",
			},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.config.Validate()
			if (err != nil) != tt.wantErr {
				t.Errorf("Validate() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func TestLoadConfig(t *testing.T) {
	// Set up test environment variables
	os.Setenv("SLAY_CHECK_AI_PROVIDER", "anthropic")
	os.Setenv("SLAY_CHECK_AI_TOKEN", "test-token")
	os.Setenv("SLAY_CHECK_GITHUB_TOKEN", "github-token")
	defer func() {
		os.Unsetenv("SLAY_CHECK_AI_PROVIDER")
		os.Unsetenv("SLAY_CHECK_AI_TOKEN")
		os.Unsetenv("SLAY_CHECK_GITHUB_TOKEN")
	}()

	cfg, err := Load()
	if err != nil {
		t.Fatalf("Load() error = %v", err)
	}

	if cfg.AIProvider != "anthropic" {
		t.Errorf("Expected AIProvider to be 'anthropic', got '%s'", cfg.AIProvider)
	}

	if cfg.AIToken != "test-token" {
		t.Errorf("Expected AIToken to be 'test-token', got '%s'", cfg.AIToken)
	}

	if cfg.GitHubToken != "github-token" {
		t.Errorf("Expected GitHubToken to be 'github-token', got '%s'", cfg.GitHubToken)
	}
}
