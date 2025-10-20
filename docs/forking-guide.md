# Using Slay Check with Your Own Fork

This guide explains how to fork the Slay Check repository and use your own fork in GitHub Actions workflows.

## Why Fork?

Forking Slay Check allows you to:
- **Customize the tool** for your specific needs
- **Add custom AI providers** or review criteria
- **Modify the review logic** to match your team's standards
- **Control updates** and version management
- **Contribute back** to the main project

## Fork Setup

### 1. Fork the Repository

1. Go to [Slay Check repository](https://github.com/slay-check/slay-check)
2. Click the "Fork" button
3. Choose your GitHub account as the destination
4. Wait for the fork to complete

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/slay-check.git
cd slay-check
```

### 3. Add Upstream Remote

```bash
git remote add upstream https://github.com/slay-check/slay-check.git
```

### 4. Set Up Development Environment

```bash
make dev-setup
```

## Using Your Fork in GitHub Actions

### Method 1: Direct Fork Usage

Create `.github/workflows/slay-check.yml` in your project:

```yaml
name: Slay Check - AI Code Review
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  slay-check:
    runs-on: ubuntu-latest
    if: github.event.pull_request.draft == false
    
    steps:
      - name: Checkout your repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      - name: Checkout Slay Check (your fork)
        uses: actions/checkout@v4
        with:
          repository: YOUR_USERNAME/slay-check
          path: slay-check
          token: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Set up Go
        uses: actions/setup-go@v4
        with:
          go-version: '1.21'
          
      - name: Build Slay Check from fork
        run: |
          cd slay-check
          go mod download
          go build -o ../slay-check ./cmd/github-action
          
      - name: Run Slay Check
        env:
          GITHUB_REPOSITORY: ${{ github.repository }}
          GITHUB_PR_NUMBER: ${{ github.event.pull_request.number }}
          SLAY_CHECK_AI_TOKEN: ${{ secrets.SLAY_CHECK_AI_TOKEN }}
          SLAY_CHECK_GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          ./slay-check
```

### Method 2: Using Personal Access Token

If you need more permissions, use a Personal Access Token:

```yaml
name: Slay Check - AI Code Review
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  slay-check:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout your repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      - name: Checkout Slay Check (your fork)
        uses: actions/checkout@v4
        with:
          repository: YOUR_USERNAME/slay-check
          path: slay-check
          token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
          
      - name: Set up Go
        uses: actions/setup-go@v4
        with:
          go-version: '1.21'
          
      - name: Build Slay Check from fork
        run: |
          cd slay-check
          go mod download
          go build -o ../slay-check ./cmd/github-action
          
      - name: Run Slay Check
        env:
          GITHUB_REPOSITORY: ${{ github.repository }}
          GITHUB_PR_NUMBER: ${{ github.event.pull_request.number }}
          SLAY_CHECK_AI_TOKEN: ${{ secrets.SLAY_CHECK_AI_TOKEN }}
          SLAY_CHECK_GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          ./slay-check
```

**Required Secret:** `PERSONAL_ACCESS_TOKEN` with `repo` scope.

### Method 3: Using Specific Branch/Tag

Use a specific branch or tag from your fork:

```yaml
- name: Checkout Slay Check (specific version)
  uses: actions/checkout@v4
  with:
    repository: YOUR_USERNAME/slay-check
    ref: v1.2.0  # or branch name like 'custom-features'
    path: slay-check
    token: ${{ secrets.GITHUB_TOKEN }}
```

## Customization Examples

### 1. Custom AI Provider

Add your own AI provider in `internal/ai/custom.go`:

```go
package ai

import (
    "context"
    "fmt"
)

type CustomProvider struct {
    apiKey string
    baseURL string
}

func NewCustomProvider(apiKey string) *CustomProvider {
    return &CustomProvider{
        apiKey: apiKey,
        baseURL: "https://api.custom-ai.com/v1",
    }
}

func (p *CustomProvider) ReviewCode(ctx context.Context, request ReviewRequest) (*ReviewResponse, error) {
    // Your custom implementation
    return &ReviewResponse{
        Analysis: "Custom AI analysis",
        Score: 8.5,
        Issues: []Issue{},
    }, nil
}

func (p *CustomProvider) GetName() string {
    return "custom"
}

func (p *CustomProvider) IsAvailable() bool {
    return p.apiKey != ""
}
```

### 2. Custom Review Criteria

Modify `internal/review/engine.go` to add custom criteria:

```go
// Add custom review logic
func (e *Engine) customReview(file PullRequestFile, pr *github.PullRequest) (*FileReview, error) {
    // Your custom review logic
    return &FileReview{
        Filename: file.Filename,
        Score: 9.0,
        Analysis: "Custom analysis based on your rules",
    }, nil
}
```

### 3. Custom Configuration

Add custom configuration options in `internal/config/config.go`:

```go
type Config struct {
    // ... existing fields ...
    CustomRules    []string `mapstructure:"custom_rules"`
    TeamStandards  bool     `mapstructure:"team_standards"`
    // ... more custom fields ...
}
```

## Updating Your Fork

### 1. Sync with Upstream

```bash
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

### 2. Create Feature Branches

```bash
git checkout -b feature/my-custom-feature
# Make your changes
git add .
git commit -m "Add custom feature"
git push origin feature/my-custom-feature
```

### 3. Create Pull Requests

Create PRs to the main repository to contribute your improvements back.

## Advanced Usage

### 1. Multiple Forks for Different Teams

Create separate forks for different teams:

```yaml
# Team A workflow
- name: Checkout Slay Check (Team A fork)
  uses: actions/checkout@v4
  with:
    repository: team-a/slay-check
    path: slay-check

# Team B workflow  
- name: Checkout Slay Check (Team B fork)
  uses: actions/checkout@v4
  with:
    repository: team-b/slay-check
    path: slay-check
```

### 2. Environment-Specific Forks

Use different forks for different environments:

```yaml
- name: Checkout Slay Check (environment-specific)
  uses: actions/checkout@v4
  with:
    repository: ${{ github.ref == 'refs/heads/main' && 'prod-team/slay-check' || 'dev-team/slay-check' }}
    path: slay-check
```

### 3. Conditional Fork Usage

Use different forks based on conditions:

```yaml
- name: Checkout Slay Check (conditional)
  uses: actions/checkout@v4
  with:
    repository: ${{ contains(github.event.pull_request.labels.*.name, 'security') && 'security-team/slay-check' || 'YOUR_USERNAME/slay-check' }}
    path: slay-check
```

## Troubleshooting

### Common Issues

#### 1. Permission Denied

**Error:** `Permission denied (publickey)`

**Solution:** Use Personal Access Token instead of SSH:
```yaml
token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
```

#### 2. Repository Not Found

**Error:** `Repository not found`

**Solution:** Check repository name and ensure it's public or you have access:
```yaml
repository: YOUR_USERNAME/slay-check  # Make sure this is correct
```

#### 3. Build Failures

**Error:** Build fails in GitHub Actions

**Solution:** Check Go version compatibility and dependencies:
```yaml
- name: Set up Go
  uses: actions/setup-go@v4
  with:
    go-version: '1.21'  # Match your fork's Go version
```

#### 4. Token Issues

**Error:** `Invalid token`

**Solution:** Ensure token has correct permissions:
- `repo` scope for private repositories
- `public_repo` scope for public repositories

## Best Practices

### 1. Keep Your Fork Updated

Regularly sync with upstream to get latest features and security updates.

### 2. Use Feature Branches

Don't modify main branch directly. Create feature branches for customizations.

### 3. Document Customizations

Document any customizations in your fork's README.

### 4. Contribute Back

Submit useful customizations back to the main project via pull requests.

### 5. Test Thoroughly

Test your fork thoroughly before using in production workflows.

## Security Considerations

### 1. Token Management

- Use minimal required permissions for tokens
- Rotate tokens regularly
- Never commit tokens to code

### 2. Code Review

- Review all customizations before merging
- Use security scanning tools
- Follow secure coding practices

### 3. Dependencies

- Keep dependencies updated
- Monitor for security vulnerabilities
- Use dependency scanning tools

## Support

- **Issues**: Create issues in your fork or the main repository
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check the main repository's documentation

Happy forking! 🚀
