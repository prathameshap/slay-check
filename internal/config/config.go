package config

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/spf13/viper"
)

// Config represents the application configuration
type Config struct {
	AIProvider     string            `mapstructure:"ai_provider"`
	AIToken        string            `mapstructure:"ai_token"`
	GitHubToken    string            `mapstructure:"github_token"`
	ReviewCriteria ReviewCriteria    `mapstructure:"review_criteria"`
	ExcludePatterns []string         `mapstructure:"exclude_patterns"`
	MaxFileSize    int               `mapstructure:"max_file_size"`
	MaxFilesPerPR  int               `mapstructure:"max_files_per_pr"`
	Verbose        bool              `mapstructure:"verbose"`
	DryRun         bool              `mapstructure:"dry_run"`
}

// ReviewCriteria defines what aspects to review
type ReviewCriteria struct {
	AnalyzeProblem     bool `mapstructure:"analyze_problem"`
	AlgorithmAnalysis  bool `mapstructure:"algorithm_analysis"`
	BestApproaches     bool `mapstructure:"best_approaches"`
	ComplexityAnalysis bool `mapstructure:"complexity_analysis"`
	RiskAssessment     bool `mapstructure:"risk_assessment"`
	SecurityReview     bool `mapstructure:"security_review"`
	PerformanceReview  bool `mapstructure:"performance_review"`
}

// DefaultConfig returns default configuration values
func DefaultConfig() *Config {
	return &Config{
		AIProvider: "openai",
		ReviewCriteria: ReviewCriteria{
			AnalyzeProblem:     true,
			AlgorithmAnalysis:  true,
			BestApproaches:     true,
			ComplexityAnalysis: true,
			RiskAssessment:     true,
			SecurityReview:     true,
			PerformanceReview:  true,
		},
		ExcludePatterns: []string{"*.md", "*.txt", "vendor/*", "node_modules/*"},
		MaxFileSize:     10000,
		MaxFilesPerPR:   50,
		Verbose:         false,
		DryRun:          false,
	}
}

// Load loads configuration from various sources
func Load() (*Config, error) {
	// Set default values
	cfg := DefaultConfig()

	// Set up viper
	viper.SetConfigName("slay-check")
	viper.SetConfigType("yaml")
	viper.AddConfigPath(".")
	viper.AddConfigPath("$HOME/.slay-check")
	viper.AddConfigPath("/etc/slay-check")

	// Environment variables
	viper.SetEnvPrefix("SLAY_CHECK")
	viper.AutomaticEnv()

	// Bind environment variables
	viper.BindEnv("ai_provider", "SLAY_CHECK_AI_PROVIDER")
	viper.BindEnv("ai_token", "SLAY_CHECK_AI_TOKEN")
	viper.BindEnv("github_token", "SLAY_CHECK_GITHUB_TOKEN")
	viper.BindEnv("verbose", "SLAY_CHECK_VERBOSE")
	viper.BindEnv("dry_run", "SLAY_CHECK_DRY_RUN")

	// Read config file
	if err := viper.ReadInConfig(); err != nil {
		if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
			return nil, fmt.Errorf("error reading config file: %w", err)
		}
		// Config file not found, use defaults
	}

	// Unmarshal into struct
	if err := viper.Unmarshal(cfg); err != nil {
		return nil, fmt.Errorf("error unmarshaling config: %w", err)
	}

	// Validate configuration
	if err := cfg.Validate(); err != nil {
		return nil, fmt.Errorf("configuration validation failed: %w", err)
	}

	return cfg, nil
}

// Validate checks if the configuration is valid
func (c *Config) Validate() error {
	if c.AIProvider == "" {
		return fmt.Errorf("ai_provider is required")
	}

	if c.AIToken == "" {
		return fmt.Errorf("ai_token is required")
	}

	if c.GitHubToken == "" {
		return fmt.Errorf("github_token is required")
	}

	return nil
}

// Save saves the configuration to a file
func (c *Config) Save(path string) error {
	// Ensure directory exists
	dir := filepath.Dir(path)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return fmt.Errorf("failed to create config directory: %w", err)
	}

	// Set viper values
	viper.Set("ai_provider", c.AIProvider)
	viper.Set("review_criteria", c.ReviewCriteria)
	viper.Set("exclude_patterns", c.ExcludePatterns)
	viper.Set("max_file_size", c.MaxFileSize)
	viper.Set("max_files_per_pr", c.MaxFilesPerPR)
	viper.Set("verbose", c.Verbose)
	viper.Set("dry_run", c.DryRun)

	// Write config file
	return viper.WriteConfigAs(path)
}
