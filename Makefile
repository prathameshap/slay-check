# Makefile for Slay Check

.PHONY: build test clean install lint fmt vet help

# Variables
BINARY_NAME=slay-check
CLI_BINARY=cmd/slay-check/slay-check
GITHUB_ACTION_BINARY=cmd/github-action/slay-check
VERSION=$(shell git describe --tags --always --dirty)
BUILD_TIME=$(shell date -u '+%Y-%m-%d_%H:%M:%S')
LDFLAGS=-ldflags "-X main.version=$(VERSION) -X main.buildTime=$(BUILD_TIME)"

# Default target
all: build

# Build all binaries
build: build-cli build-github-action

# Build CLI binary
build-cli:
	@echo "Building CLI binary..."
	go build $(LDFLAGS) -o $(CLI_BINARY) ./cmd/slay-check

# Build GitHub Action binary
build-github-action:
	@echo "Building GitHub Action binary..."
	go build $(LDFLAGS) -o $(GITHUB_ACTION_BINARY) ./cmd/github-action

# Run tests
test:
	@echo "Running tests..."
	go test -v ./...

# Run tests with coverage
test-coverage:
	@echo "Running tests with coverage..."
	go test -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out -o coverage.html
	@echo "Coverage report generated: coverage.html"

# Run integration tests
test-integration:
	@echo "Running integration tests..."
	go test -tags=integration -v ./...

# Run all tests (unit + integration)
test-all: test test-integration

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -f $(CLI_BINARY)
	rm -f $(GITHUB_ACTION_BINARY)
	rm -f coverage.out coverage.html
	go clean

# Install CLI tool
install:
	@echo "Installing CLI tool..."
	go install $(LDFLAGS) ./cmd/slay-check

# Run linter
lint:
	@echo "Running linter..."
	golangci-lint run

# Format code
fmt:
	@echo "Formatting code..."
	go fmt ./...

# Run go vet
vet:
	@echo "Running go vet..."
	go vet ./...

# Run all code quality checks
check: fmt vet lint test

# Run benchmarks
bench:
	@echo "Running benchmarks..."
	go test -bench=. ./...

# Generate mocks
generate:
	@echo "Generating mocks..."
	go generate ./...

# Download dependencies
deps:
	@echo "Downloading dependencies..."
	go mod download
	go mod tidy

# Update dependencies
deps-update:
	@echo "Updating dependencies..."
	go get -u ./...
	go mod tidy

# Run security scan
security:
	@echo "Running security scan..."
	gosec ./...

# Build for multiple platforms
build-all:
	@echo "Building for multiple platforms..."
	GOOS=linux GOARCH=amd64 go build $(LDFLAGS) -o bin/$(BINARY_NAME)-linux-amd64 ./cmd/slay-check
	GOOS=darwin GOARCH=amd64 go build $(LDFLAGS) -o bin/$(BINARY_NAME)-darwin-amd64 ./cmd/slay-check
	GOOS=darwin GOARCH=arm64 go build $(LDFLAGS) -o bin/$(BINARY_NAME)-darwin-arm64 ./cmd/slay-check
	GOOS=windows GOARCH=amd64 go build $(LDFLAGS) -o bin/$(BINARY_NAME)-windows-amd64.exe ./cmd/slay-check

# Create release packages
release: build-all
	@echo "Creating release packages..."
	mkdir -p release
	tar -czf release/$(BINARY_NAME)-linux-amd64.tar.gz -C bin $(BINARY_NAME)-linux-amd64
	tar -czf release/$(BINARY_NAME)-darwin-amd64.tar.gz -C bin $(BINARY_NAME)-darwin-amd64
	tar -czf release/$(BINARY_NAME)-darwin-arm64.tar.gz -C bin $(BINARY_NAME)-darwin-arm64
	zip -j release/$(BINARY_NAME)-windows-amd64.zip bin/$(BINARY_NAME)-windows-amd64.exe

# Run Docker build
docker-build:
	@echo "Building Docker image..."
	docker build -t slay-check:$(VERSION) .
	docker build -t slay-check:latest .

# Run Docker tests
docker-test:
	@echo "Running Docker tests..."
	docker run --rm slay-check:latest version

# Development setup
dev-setup:
	@echo "Setting up development environment..."
	go mod download
	go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
	go install github.com/securecodewarrior/gosec/v2/cmd/gosec@latest
	@echo "Development environment ready!"

# Run local development server
dev:
	@echo "Starting development server..."
	go run ./cmd/slay-check

# Show help
help:
	@echo "Available targets:"
	@echo "  build          - Build all binaries"
	@echo "  build-cli      - Build CLI binary"
	@echo "  build-github-action - Build GitHub Action binary"
	@echo "  test           - Run unit tests"
	@echo "  test-coverage  - Run tests with coverage report"
	@echo "  test-integration - Run integration tests"
	@echo "  test-all       - Run all tests"
	@echo "  clean          - Clean build artifacts"
	@echo "  install        - Install CLI tool"
	@echo "  lint           - Run linter"
	@echo "  fmt            - Format code"
	@echo "  vet            - Run go vet"
	@echo "  check          - Run all code quality checks"
	@echo "  bench          - Run benchmarks"
	@echo "  generate       - Generate mocks"
	@echo "  deps           - Download dependencies"
	@echo "  deps-update    - Update dependencies"
	@echo "  security       - Run security scan"
	@echo "  build-all      - Build for multiple platforms"
	@echo "  release        - Create release packages"
	@echo "  docker-build   - Build Docker image"
	@echo "  docker-test    - Run Docker tests"
	@echo "  dev-setup      - Set up development environment"
	@echo "  dev            - Run development server"
	@echo "  help           - Show this help"
