# README & How-to-Use — Ease of Use Rating

This document rates the README and usage documentation for **ease of use** from a new user’s perspective.

---

## Overall scores (1–10)

| Audience | Score | Notes |
|----------|--------|--------|
| **First-time: “Run in GitHub Actions”** | **7.5 / 10** | Quick Start is copy-paste ready and secrets are clear; workflow is a bit long and install step may surprise (token in URL). |
| **First-time: “Run locally / CLI”** | **6.5 / 10** | README has the right commands; some linked docs still use `YOUR_USERNAME` or wrong context (e.g. Actions syntax in “local” section). |
| **Power user / custom provider** | **8 / 10** | Presets, focus, Custom HTTP, Perplexity, Cursor, defaults table — strong. |
| **Discoverability (“Where do I start?”)** | **5.5 / 10** | Single long README; no clear “30-second path” vs “full config” split; many doc links without a “start here” map. |

**Overall ease-of-use rating: 6.5 / 10** — Good content and coverage, but the path from “I just want it to work” to “done” could be shorter and clearer; a few doc bugs hurt local users.

---

## What works well

### README

- **Quick Start structure**: Numbered steps (add workflow → add secrets → optional config), with a full workflow users can copy.
- **Secrets callout**: “Add repository secrets” and table of workflow file vs secret make setup predictable.
- **Configuration**: Presets (`full` / `standard` / `minimal` / `security` / `performance`) and `review_focus` are easy to understand; defaults table is helpful.
- **Where the comment goes**: Explicit note that Slay Check posts **one comment** (issue comment vs review) and how to switch — reduces confusion.
- **Provider table**: AI providers and example models are scannable.
- **Local Development**: Install + `export` + `slay-check review --repo ... --pr ...` is clear; VS Code/Cursor env tip is useful.
- **Development / Testing**: Commands for pytest, coverage, black, isort, flake8, and manual run with `--dry-run` are practical.

### docs/github-action.md

- **Basic Setup**: Minimal workflow + required secrets + optional variables are well separated.
- **Custom HTTP / Perplexity / Cursor**: Request/response JSON and provider-specific notes are detailed and usable.

### docs/setup-guide.md

- **Step-by-step flow**: Prerequisites → API key → Secrets → Workflow → Config → Test is logical.
- **Troubleshooting**: Token, repo not found, permissions, “no files to review” — covers common failures.

### docs/local-development.md

- **Usage**: `--local`, `--pr`, `--base`/`--head`, `--verbose` are documented with examples.
- **Config examples**: Dev vs prod vs security presets help people copy-paste and adapt.
- **IDE / pre-commit**: Short notes for VS Code and pre-commit hook add real-world use cases.

---

## What hurts ease of use

### 1. README length and “first path”

- README is long (300+ lines). New users may not see a single “do this first” path.
- **Suggestion**: Add a short **TL;DR** at the top, e.g. “Copy the workflow below → add `SLAY_CHECK_AI_TOKEN` secret → push a PR. Done.” Then keep the rest as “Configuration” / “Advanced”.

### 2. Install step in Quick Start

- `pip install git+https://x-access-token:${{ secrets.GITHUB_TOKEN }}@github.com/...` is correct for installing from the same private repo in Actions but can look odd (“why is GITHUB_TOKEN in the URL?”).
- **Suggestion**: One short line before the workflow: “This installs Slay Check from this repo; the token lets the job read the repo.”

### 3. Broken or misleading “local” instructions

- **docs/setup-guide.md** “Local Development” section uses:
  - `pip install git+https://x-access-token:${{ secrets.GITHUB_TOKEN }}@github.com/...` — that’s Actions syntax; it doesn’t work in a local terminal.
- **Suggestion**: For local install use a normal URL, e.g. `pip install git+https://github.com/prathameshap/slay-check.git`, and move any token-based install to an “Installing from a private fork in Actions” section.

### 4. YOUR_USERNAME in non-fork docs

- **docs/setup-guide.md** “Basic Setup” still has `pip install git+https://github.com/YOUR_USERNAME/slay-check.git` and “Fork Setup” uses `repository: YOUR_USERNAME/slay-check` (that one is correct for forks).
- **docs/local-development.md** uses `YOUR_USERNAME` in install and clone for the main “how to run locally” flow.
- **Suggestion**: Any instruction that means “use the official repo” should use `prathameshap/slay-check`; keep `YOUR_USERNAME` only in forking docs and fork workflow examples.

### 5. Too many doc links without a map

- Documentation lists 10+ links (Setup, GitHub Action, Local, Forking, AI Response Control, REPO_ISSUES, Rust, Licensing, etc.) with no “start here” or “by role” guidance.
- **Suggestion**: Add a short “Docs by goal” block, e.g. “Run in Actions → github-action.md”; “Run locally → local-development.md”; “Customize review → Configuration below”; “Fork / contribute → CONTRIBUTING.md”.

### 6. License block length

- The license section is important but long (version condition, enterprises vs individuals, “no monetary gain”). It can distract users who only want to run the tool.
- **Suggestion**: Keep a one-line summary at the top (“Dual license for v1.0.0: AGPL for enterprises, GPL for individuals”) and link to **Licensing** for full text.

---

## Summary table

| Criterion | Rating | Comment |
|-----------|--------|--------|
| Can I run it in Actions in &lt;5 min? | 7/10 | Yes with copy-paste; install step could be briefly explained. |
| Can I run it locally without reading everything? | 6/10 | README is enough; linked local docs have wrong URLs/syntax in places. |
| Is configuration understandable? | 8/10 | Presets and focus are easy; full YAML is there for power users. |
| Is it obvious where to read next? | 5/10 | Many links; no clear “start here” or “by goal” map. |
| Are copy-paste examples correct? | 6.5/10 | README and github-action.md are correct; setup-guide and local-development have fixable bugs. |
| Troubleshooting / “what went wrong”? | 7/10 | Setup-guide and local-development troubleshooting sections help; README could add one “Common issues” line with a link. |

---

## Recommended quick wins

1. **README**: Add a 2–3 line TL;DR at the top (“Quickest start: copy workflow → add `SLAY_CHECK_AI_TOKEN` → open a PR”).
2. **README**: Add a one-sentence explanation for the install step (token used so the job can clone this repo).
3. **docs/setup-guide.md**: In “Local Development”, replace the `pip install` that uses `${{ secrets.GITHUB_TOKEN }}` with a normal public install (e.g. `pip install git+https://github.com/prathameshap/slay-check.git`).
4. **docs/setup-guide.md** and **docs/local-development.md**: Use `prathameshap/slay-check` (not `YOUR_USERNAME`) wherever the intent is “use the official Slay Check repo”.
5. **README**: Add a short “Docs by goal” list (Run in Actions → X; Run locally → Y; Customize → Z; Contribute → CONTRIBUTING).

After these changes, a reasonable target would be **~7.5 / 10** overall ease of use, with a clearer “minimal path” and fewer doc bugs for local and first-time users.
