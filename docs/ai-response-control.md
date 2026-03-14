# AI Response Control Guide

## Choosing What Gets Reviewed

Use **presets** or **focus** to control which aspects of the code are reviewed (see [README Configuration](https://github.com/prathameshap/slay-check#configuration)):

```yaml
# One word: full (default), standard, minimal, security, performance
review_preset: security
# Or only these: review_focus: [security, performance, complexity]
```

**Environment variables:** `SLAY_CHECK_REVIEW_PRESET=security`, `SLAY_CHECK_REVIEW_FOCUS=security,performance` (comma-separated).

**Defaults:** If you omit both, all criteria are enabled (full review).

---

## Token Limits & AI Strictness Configuration

### 1. **Token Limits** (`max_tokens`)

Control how long AI responses are:

```yaml
# slay-check.yaml
max_tokens: 2000  # Shorter responses
```

**Token Guidelines:**
- `500-1000`: Very short (quick reviews)
- `1000-2000`: Short (standard reviews) 
- `2000-4000`: Medium (detailed reviews) - **Default**
- `4000-8000`: Long (comprehensive analysis)

### 2. **AI Strictness** (`temperature`)

Control how strict/creative the AI is:

```yaml
# slay-check.yaml
temperature: 0.1  # Very strict
```

**Temperature Guidelines:**
- `0.0-0.2`: Very strict, deterministic
- `0.2-0.4`: Strict, reliable - **Default: 0.3**
- `0.4-0.6`: Moderate, flexible
- `0.6-0.8`: Lenient, creative
- `0.8-1.0`: Very lenient, unpredictable

### 3. **Review Strictness** (Score Thresholds)

Control how strict the review scoring is:

```yaml
# slay-check.yaml
min_score_threshold: 8.0    # Very strict (default: 6.0)
critical_issues_limit: 1    # Very strict (default: 3)
```

**Strictness Levels:**
- **Very Strict**: `min_score_threshold: 8.0`, `critical_issues_limit: 1`
- **Strict**: `min_score_threshold: 7.0`, `critical_issues_limit: 2`
- **Moderate**: `min_score_threshold: 6.0`, `critical_issues_limit: 3` (default)
- **Lenient**: `min_score_threshold: 5.0`, `critical_issues_limit: 5`

### 4. **Environment-Specific Settings**

Different strictness per environment:

#### **Development** (Fast & Cheap):
```yaml
max_tokens: 2000
temperature: 0.2
min_score_threshold: 5.0
critical_issues_limit: 10
```

#### **Production** (Balanced):
```yaml
max_tokens: 4000
temperature: 0.3
min_score_threshold: 7.0
critical_issues_limit: 2
```

#### **Security** (Very Strict):
```yaml
max_tokens: 3000
temperature: 0.1
min_score_threshold: 8.0
critical_issues_limit: 1
```

#### **Performance** (Strict):
```yaml
max_tokens: 3500
temperature: 0.2
min_score_threshold: 8.0
critical_issues_limit: 1
```

### 5. **Environment Variables**

Override settings via environment:

```bash
# What to review (preset or focus)
export SLAY_CHECK_REVIEW_PRESET="security"
export SLAY_CHECK_REVIEW_FOCUS="security,performance"   # comma-separated

# Token limits
export SLAY_CHECK_MAX_TOKENS="2000"

# AI strictness
export SLAY_CHECK_TEMPERATURE="0.1"

# Review strictness
export SLAY_CHECK_MIN_SCORE_THRESHOLD="8.0"
export SLAY_CHECK_CRITICAL_ISSUES_LIMIT="1"
```

### 6. **GitHub Actions Configuration**

Set in repository variables:

```yaml
env:
  SLAY_CHECK_MAX_TOKENS: "2000"
  SLAY_CHECK_TEMPERATURE: "0.1"
  SLAY_CHECK_MIN_SCORE_THRESHOLD: "8.0"
  SLAY_CHECK_CRITICAL_ISSUES_LIMIT: "1"
```

### 7. **Quick Examples**

#### **Very Strict & Short Responses:**
```yaml
max_tokens: 1000
temperature: 0.1
min_score_threshold: 8.0
critical_issues_limit: 1
```

#### **Lenient & Detailed Responses:**
```yaml
max_tokens: 6000
temperature: 0.5
min_score_threshold: 5.0
critical_issues_limit: 5
```

#### **Balanced (Default):**
```yaml
max_tokens: 4000
temperature: 0.3
min_score_threshold: 6.0
critical_issues_limit: 3
```

### 8. **Testing Different Settings**

```bash
# Test with strict settings
export SLAY_CHECK_MAX_TOKENS="1000"
export SLAY_CHECK_TEMPERATURE="0.1"
slay-check review --local --dry-run

# Test with lenient settings  
export SLAY_CHECK_MAX_TOKENS="6000"
export SLAY_CHECK_TEMPERATURE="0.5"
slay-check review --local --dry-run
```
