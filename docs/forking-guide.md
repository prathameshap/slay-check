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

1. Go to [Slay Check repository](https://github.com/prathameshap/slay-check)
2. Click the "Fork" button
3. Choose your GitHub account as the destination
4. Wait for the fork to complete

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/slay-check.git
cd slay-check
```

Ensure you're on `main` and add the upstream remote so you can sync with the canonical repo:

```bash
git checkout main
git remote add upstream https://github.com/prathameshap/slay-check.git
```

To update your fork with upstream changes: `git fetch upstream && git checkout main && git merge upstream/main` (or rebase), then push to your fork.

### 3. Set Up Development Environment

```bash
pip install -e .
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
        uses: actions/checkout@v5
        with:
          fetch-depth: 0
          
      - name: Checkout Slay Check (your fork)
        uses: actions/checkout@v5
        with:
          repository: YOUR_USERNAME/slay-check
          path: slay-check
          token: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
          
      - name: Install Slay Check from fork
        run: |
          cd slay-check
          pip install -e .
          
      - name: Run Slay Check
        env:
          GITHUB_REPOSITORY: ${{ github.repository }}
          GITHUB_PR_NUMBER: ${{ github.event.pull_request.number }}
          SLAY_CHECK_AI_TOKEN: ${{ secrets.SLAY_CHECK_AI_TOKEN }}
          SLAY_CHECK_GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python -m slay_check.github_action
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
        uses: actions/checkout@v5
        with:
          fetch-depth: 0
          
      - name: Checkout Slay Check (your fork)
        uses: actions/checkout@v5
        with:
          repository: YOUR_USERNAME/slay-check
          path: slay-check
          token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
          
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
          
      - name: Install Slay Check from fork
        run: |
          cd slay-check
          pip install -e .
          
      - name: Run Slay Check
        env:
          GITHUB_REPOSITORY: ${{ github.repository }}
          GITHUB_PR_NUMBER: ${{ github.event.pull_request.number }}
          SLAY_CHECK_AI_TOKEN: ${{ secrets.SLAY_CHECK_AI_TOKEN }}
          SLAY_CHECK_GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python -m slay_check.github_action
```

**Required Secret:** `PERSONAL_ACCESS_TOKEN` with `repo` scope.

### Method 3: Using Specific Branch/Tag

Use a specific branch or tag from your fork:

```yaml
- name: Checkout Slay Check (specific version)
  uses: actions/checkout@v5
  with:
    repository: YOUR_USERNAME/slay-check
    ref: v1.2.0  # or branch name like 'custom-features'
    path: slay-check
    token: ${{ secrets.GITHUB_TOKEN }}
```

## Customization Examples

### 1. Custom AI Provider

Add your own AI provider in `slay_check/ai/custom.py`:

```python
from typing import Dict, Any, Optional
from .base import AIProvider, ReviewRequest, ReviewResponse, Issue, IssueType, Severity, Complexity

class CustomProvider(AIProvider):
    """Custom AI provider for code review."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.custom-ai.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
    
    def get_name(self) -> str:
        return "custom"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def review_code(self, request: ReviewRequest) -> ReviewResponse:
        # Your custom implementation
        return ReviewResponse(
            analysis="Custom AI analysis",
            score=8.5,
            issues=[],
            suggestions=[],
            complexity=Complexity(),
            confidence=0.8
        )
```

### 2. Custom Review Criteria

Modify `slay_check/review.py` to add custom criteria:

```python
def custom_review(self, file_info: PullRequestFileInfo, pr_info: PullRequestInfo) -> FileReview:
    """Custom review logic."""
    # Your custom review logic
    return FileReview(
        filename=file_info.filename,
        language=self._detect_language(file_info.filename),
        score=9.0,
        issues=[],
        suggestions=[],
        complexity=None,
        analysis="Custom analysis based on your rules"
    )
```

### 3. Custom Configuration

Add custom configuration options in `slay_check/config.py`:

```python
class Config(BaseModel):
    # ... existing fields ...
    custom_rules: List[str] = []
    team_standards: bool = False
    # ... more custom fields ...
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
  uses: actions/checkout@v5
  with:
    repository: team-a/slay-check
    path: slay-check

# Team B workflow  
- name: Checkout Slay Check (Team B fork)
  uses: actions/checkout@v5
  with:
    repository: team-b/slay-check
    path: slay-check
```

### 2. Environment-Specific Forks

Use different forks for different environments:

```yaml
- name: Checkout Slay Check (environment-specific)
  uses: actions/checkout@v5
  with:
    repository: ${{ github.ref == 'refs/heads/main' && 'prod-team/slay-check' || 'dev-team/slay-check' }}
    path: slay-check
```

### 3. Conditional Fork Usage

Use different forks based on conditions:

```yaml
- name: Checkout Slay Check (conditional)
  uses: actions/checkout@v5
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

#### 3. Installation Failures

**Error:** Python installation fails

**Solution:** Check Python version compatibility and dependencies:
```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.11'  # Match your fork's Python version
    cache: 'pip'
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

Happy forking!