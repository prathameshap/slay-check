# Repository issues and technical debt

This document lists known issues, gaps, and technical debt in the Slay Check codebase (as of the last update). Use it for prioritization and contribution ideas.

---

## High priority

### 1. Local review not implemented
- **Where:** `slay_check/cli.py` → `review_local_changes()`
- **What:** CLI advertises `review --local` but the function only prints "Local review not yet implemented".
- **Impact:** Users following the README quick start for local development get a dead end.
- **Fix options:** Implement using `git diff` → parse patch → reuse existing AI review pipeline; or document as "planned" and remove from quick start.

### 2. Config.load() does not deep-merge nested config
- **Where:** `slay_check/config.py` → `Config.load()`
- **What:** YAML is loaded into a flat merge with env. If a user's YAML has only top-level keys (e.g. `ai_provider`, `ai_model`) and no `review_criteria`, Pydantic gets a dict for `review_criteria` from defaults, but if the file has partial nested data it can overwrite entire sections and break validation.
- **Impact:** Partial config files can cause confusing validation errors or wrong defaults.
- **Fix:** Merge config with a full default dict (e.g. `Config().model_dump()`) so nested defaults are preserved when the file omits them.

### 3. GitHub token required even for local-only usage
- **Where:** `slay_check/config.py` → `validate()`
- **What:** `validate()` requires both `ai_token` and `github_token`. For `review --local` (once implemented), GitHub token is not needed.
- **Impact:** Users cannot run local-only flows without a dummy GitHub token.
- **Fix:** Validate GitHub token only when performing PR review or posting comments (e.g. when not in local-only mode).

---

## Medium priority

### 4. No CI workflow running tests on this repo
- **Where:** `.github/workflows/`
- **What:** Workflows only run the Slay Check action (or install from git); none run `pytest` / lint on push/PR for the slay-check repo itself.
- **Impact:** Regressions can be merged without automated checks.
- **Fix:** Added `.github/workflows/ci.yml` to run black, isort, flake8, and pytest (with dummy tokens). Ensure branch names match your default branch (main/master).

### 5. Duplicate prompt logic across AI providers
- **Where:** `slay_check/ai/openai.py`, `anthropic.py`, `google.py`
- **What:** `_build_prompt()` is largely copy-pasted (~80 lines each). JSON schema and criteria text are repeated.
- **Impact:** Changes to prompt or schema must be edited in three places; risk of drift.
- **Fix:** Extract shared prompt builder (and optional JSON schema) into `slay_check/ai/base.py` or a small `prompts.py` module; providers call shared builder.

### 6. Broad exception handling and generic re-raises
- **Where:** `github_client.py`, `review.py`, AI providers
- **What:** `except Exception as e: raise Exception(f"...{str(e)}")` loses exception type and stack trace.
- **Impact:** Harder debugging; tools that rely on exception type don’t work well.
- **Fix:** Re-raise with `raise ... from e` or define specific exceptions (e.g. `SlayCheckConfigError`, `SlayCheckGitHubError`) and wrap only at boundaries.

### 7. Inconsistent logging vs print
- **Where:** `review.py`, `github_client.py`, `github_action.py`, `ai/openai.py`
- **What:** Mix of `print()` and (in CLI) `rich.console`. No structured logging.
- **Impact:** In Actions, all output is plain stdout; hard to filter or increase verbosity selectively.
- **Fix:** Use `logging` with a single configuration; CLI and Action set level/format as needed; replace `print()` with `logger.info()` etc.

---

## Low priority

### 8. Unused import in github_client.py
- **Where:** `slay_check/github_client.py` — `from github import Github, PullRequest`
- **What:** `PullRequest` is not used in the file.
- **Fix:** Remove unused import.

### 9. Severity comparison as string
- **Where:** `slay_check/github_action.py` — `issue.severity == "critical"`
- **What:** Works because `Severity` is a `str` Enum, but comparing to enum is clearer and type-safe.
- **Fix:** Use `issue.severity == Severity.CRITICAL` and import `Severity` from `ai.base`.

### 10. Config load path order not documented
- **Where:** `slay_check/config.py` → `Config.load()`
- **What:** Order of `default_paths` (e.g. `slay-check.yaml` vs `~/.slay-check/config.yaml`) determines which file wins when multiple exist. Not documented.
- **Fix:** Document in docstring and in docs/setup-guide.md.

### 11. .gitignore ignores all slay-check.yaml
- **Where:** `.gitignore` — `slay-check.yaml`
- **What:** Prevents committing any repo-level config. Some projects may want to commit a non-secret example or defaults.
- **Fix:** Consider ignoring only files with secrets (e.g. `config/local.yaml`) or document that contributors should not commit tokens and use env for secrets.

---

## Documentation / community

### 12. YOUR_USERNAME placeholder inconsistency
- **Where:** `pyproject.toml` (fixed to prathameshap), various docs and forking workflows
- **What:** Some files had `YOUR_USERNAME` for the canonical repo; forking docs correctly use it as placeholder for fork author.
- **Fix:** Canonical repo URLs point to `prathameshap/slay-check`; forking templates keep `YOUR_USERNAME` where users are expected to substitute their fork.

### 13. CONTRIBUTING.md references pytest for github_action
- **Where:** CONTRIBUTING.md — "Test GitHub Action: python -m slay_check.github_action --help"
- **What:** `github_action` has no `--help` (no argparse); it reads env and exits with error if vars missing.
- **Fix:** Update to e.g. "Test GitHub Action entrypoint: set GITHUB_REPOSITORY, GITHUB_PR_NUMBER and run python -m slay_check.github_action (use dry-run in dev)."

---

## Test coverage gaps

### 14. No integration test for ReviewEngine
- **Where:** `tests/`
- **What:** No test that runs `ReviewEngine.review_pull_request()` with mocked GitHub client and mocked AI provider.
- **Impact:** Wiring and aggregation logic (scores, comments, thresholds) not covered by tests.
- **Fix:** Add test that mocks `GitHubClient.get_pull_request` and `AIProvider.review_code`, asserts on `ReviewResult` shape and `post_review_comments` input.

### 15. Config.load() with missing file not covered
- **Where:** `slay_check/config.py`
- **What:** Behavior when no config file exists (only env) is only implicitly tested.
- **Fix:** Add test: no config file, only env vars set, assert `Config.load()` returns config from env.

---

## Summary table

| #  | Area           | Priority | Effort (rough) |
|----|----------------|----------|----------------|
| 1  | Local review   | High     | Medium         |
| 2  | Config merge   | High     | Small          |
| 3  | GitHub token   | High     | Small          |
| 4  | CI workflow    | Medium   | Done (ci.yml)  |
| 5  | Prompt dedup   | Medium   | Medium         |
| 6  | Exceptions     | Medium   | Medium         |
| 7  | Logging        | Medium   | Small          |
| 8  | Unused import  | Low      | Trivial        |
| 9  | Severity enum  | Low      | Trivial        |
| 10 | Config docs    | Low      | Trivial        |
| 11 | .gitignore     | Low      | Trivial        |
| 12 | YOUR_USERNAME  | Low      | Done           |
| 13 | CONTRIBUTING   | Low      | Trivial        |
| 14 | ReviewEngine   | Low      | Small          |
| 15 | Config.load    | Low      | Trivial        |
