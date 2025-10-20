# Slay Check - Fork Usage Examples

This document provides practical examples of using Slay Check forks in GitHub Actions workflows.

## Basic Fork Usage

### Simple Fork Workflow

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
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      - name: Checkout Slay Check fork
        uses: actions/checkout@v4
        with:
          repository: YOUR_USERNAME/slay-check
          path: slay-check
          token: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
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

## Advanced Fork Usage

### 1. Using Personal Access Token

```yaml
name: Slay Check - AI Code Review (PAT)
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  slay-check:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      - name: Checkout Slay Check fork
        uses: actions/checkout@v4
        with:
          repository: YOUR_USERNAME/slay-check
          path: slay-check
          token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
          
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
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

### 2. Using Specific Branch

```yaml
name: Slay Check - AI Code Review (Branch)
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  slay-check:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      - name: Checkout Slay Check fork (specific branch)
        uses: actions/checkout@v4
        with:
          repository: YOUR_USERNAME/slay-check
          ref: feature/custom-review-logic
          path: slay-check
          token: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
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

### 3. Using Specific Tag/Release

```yaml
name: Slay Check - AI Code Review (Tag)
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  slay-check:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      - name: Checkout Slay Check fork (specific tag)
        uses: actions/checkout@v4
        with:
          repository: YOUR_USERNAME/slay-check
          ref: v1.2.0-custom
          path: slay-check
          token: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
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

## Conditional Fork Usage

### 1. Environment-Based Forks

```yaml
name: Slay Check - AI Code Review (Environment)
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  slay-check:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      - name: Checkout Slay Check fork (environment-based)
        uses: actions/checkout@v4
        with:
          repository: ${{ github.ref == 'refs/heads/main' && 'prod-team/slay-check' || 'dev-team/slay-check' }}
          path: slay-check
          token: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
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

### 2. Label-Based Forks

```yaml
name: Slay Check - AI Code Review (Label-based)
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  slay-check:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      - name: Checkout Slay Check fork (label-based)
        uses: actions/checkout@v4
        with:
          repository: ${{ contains(github.event.pull_request.labels.*.name, 'security') && 'security-team/slay-check' || 'YOUR_USERNAME/slay-check' }}
          path: slay-check
          token: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
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

### 3. File Path-Based Forks

```yaml
name: Slay Check - AI Code Review (Path-based)
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  slay-check:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      - name: Checkout Slay Check fork (path-based)
        uses: actions/checkout@v4
        with:
          repository: ${{ contains(github.event.pull_request.head.ref, 'frontend') && 'frontend-team/slay-check' || 'backend-team/slay-check' }}
          path: slay-check
          token: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
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

## Multi-Fork Usage

### 1. Multiple Review Jobs

```yaml
name: Slay Check - Multi-Fork Review
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  security-review:
    runs-on: ubuntu-latest
    if: contains(github.event.pull_request.labels.*.name, 'security')
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      - name: Checkout Security Slay Check fork
        uses: actions/checkout@v4
        with:
          repository: security-team/slay-check
          path: slay-check
          token: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install Slay Check from fork
        run: |
          cd slay-check
          pip install -e .
          
      - name: Run Security Slay Check
        env:
          GITHUB_REPOSITORY: ${{ github.repository }}
          GITHUB_PR_NUMBER: ${{ github.event.pull_request.number }}
          SLAY_CHECK_AI_TOKEN: ${{ secrets.SLAY_CHECK_AI_TOKEN }}
          SLAY_CHECK_GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SLAY_CHECK_AI_PROVIDER: anthropic  # Use Claude for security
        run: |
          python -m slay_check.github_action

  performance-review:
    runs-on: ubuntu-latest
    if: contains(github.event.pull_request.labels.*.name, 'performance')
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      - name: Checkout Performance Slay Check fork
        uses: actions/checkout@v4
        with:
          repository: performance-team/slay-check
          path: slay-check
          token: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install Slay Check from fork
        run: |
          cd slay-check
          pip install -e .
          
      - name: Run Performance Slay Check
        env:
          GITHUB_REPOSITORY: ${{ github.repository }}
          GITHUB_PR_NUMBER: ${{ github.event.pull_request.number }}
          SLAY_CHECK_AI_TOKEN: ${{ secrets.SLAY_CHECK_AI_TOKEN }}
          SLAY_CHECK_GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SLAY_CHECK_AI_PROVIDER: openai  # Use GPT-4 for performance
        run: |
          python -m slay_check.github_action

  general-review:
    runs-on: ubuntu-latest
    if: ${{ !contains(github.event.pull_request.labels.*.name, 'security') && !contains(github.event.pull_request.labels.*.name, 'performance') }}
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      - name: Checkout General Slay Check fork
        uses: actions/checkout@v4
        with:
          repository: YOUR_USERNAME/slay-check
          path: slay-check
          token: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install Slay Check from fork
        run: |
          cd slay-check
          pip install -e .
          
      - name: Run General Slay Check
        env:
          GITHUB_REPOSITORY: ${{ github.repository }}
          GITHUB_PR_NUMBER: ${{ github.event.pull_request.number }}
          SLAY_CHECK_AI_TOKEN: ${{ secrets.SLAY_CHECK_AI_TOKEN }}
          SLAY_CHECK_GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python -m slay_check.github_action
```

## Error Handling and Fallbacks

### 1. Fallback to Main Repository

```yaml
name: Slay Check - AI Code Review (Fallback)
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  slay-check:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      - name: Checkout Slay Check fork (with fallback)
        id: checkout-fork
        uses: actions/checkout@v4
        with:
          repository: YOUR_USERNAME/slay-check
          path: slay-check
          token: ${{ secrets.GITHUB_TOKEN }}
        continue-on-error: true
        
      - name: Checkout main Slay Check (fallback)
        if: steps.checkout-fork.outcome == 'failure'
        uses: actions/checkout@v4
        with:
          repository: slay-check/slay-check
          path: slay-check
          token: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install Slay Check
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

## Configuration Examples

### 1. Custom Configuration File

```yaml
name: Slay Check - AI Code Review (Custom Config)
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  slay-check:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      - name: Checkout Slay Check fork
        uses: actions/checkout@v4
        with:
          repository: YOUR_USERNAME/slay-check
          path: slay-check
          token: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Copy custom configuration
        run: |
          cp slay-check-custom.yaml slay-check/slay-check.yaml
          
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

### 2. Environment-Specific Configuration

```yaml
name: Slay Check - AI Code Review (Env Config)
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  slay-check:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      - name: Checkout Slay Check fork
        uses: actions/checkout@v4
        with:
          repository: YOUR_USERNAME/slay-check
          path: slay-check
          token: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
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
          SLAY_CHECK_AI_PROVIDER: ${{ github.ref == 'refs/heads/main' && 'openai' || 'anthropic' }}
          SLAY_CHECK_VERBOSE: ${{ github.ref == 'refs/heads/main' && 'false' || 'true' }}
          SLAY_CHECK_DRY_RUN: ${{ github.ref == 'refs/heads/main' && 'false' || 'true' }}
        run: |
          python -m slay_check.github_action
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Repository Access Issues

**Problem:** `Repository not found` or `Permission denied`

**Solutions:**
- Ensure the fork repository exists and is accessible
- Use Personal Access Token with correct permissions
- Check repository name spelling
- Verify token has `repo` scope for private repositories

#### 2. Installation Failures

**Problem:** Python installation fails

**Solutions:**
- Check Python version compatibility (3.11+)
- Ensure all dependencies are available
- Verify the fork has the correct structure
- Check for syntax errors in custom code

#### 3. Configuration Issues

**Problem:** Configuration not loading correctly

**Solutions:**
- Verify configuration file format
- Check environment variable names
- Ensure configuration file is in correct location
- Validate YAML syntax

#### 4. Token Issues

**Problem:** Invalid or expired tokens

**Solutions:**
- Regenerate Personal Access Token
- Check token permissions
- Verify token is correctly set in repository secrets
- Ensure token hasn't expired

## Best Practices

1. **Use specific branches/tags** for stable deployments
2. **Test forks thoroughly** before using in production
3. **Keep forks updated** with upstream changes
4. **Document customizations** in fork README
5. **Use minimal required permissions** for tokens
6. **Monitor fork performance** and optimize as needed
7. **Contribute useful changes** back to main repository

## Security Considerations

1. **Token Management**
   - Use minimal required permissions
   - Rotate tokens regularly
   - Never commit tokens to code
   - Use repository secrets for sensitive data

2. **Code Review**
   - Review all customizations
   - Use security scanning tools
   - Follow secure coding practices
   - Validate external dependencies

3. **Access Control**
   - Limit fork access to trusted users
   - Use branch protection rules
   - Implement code review requirements
   - Monitor access logs

Happy forking! 🚀