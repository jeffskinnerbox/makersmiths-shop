---
name: readme-writer
description: Create or update README.md for GitHub repos. Auto-detects whether README exists, analyzes codebase, asks only for what can't be inferred (purpose, audience, live URLs). Fixed section order with content that adapts to project type (CLI, library, web app, service). Use when user asks to create, generate, write, or update a README.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
license: MIT
metadata:
  source: I used Claude Code's /skill-generator skill and my /grill-me skill
---

# README Writer

Creates or updates `README.md` for GitHub repositories. Analyzes the codebase to infer structure, tech stack, and commands — then asks targeted questions only for what code can't reveal.

Complements `project-doc-writer`, which handles CONTRIBUTING.md, ARCHITECTURE.md, and other project docs. This skill owns README exclusively.

## When to Use

- "Create a README"
- "Generate a README for this repo"
- "Write a README.md"
- "Update the README"
- "My README is stale / missing sections"

## Mode Detection

Before anything else, check if `README.md` already exists:

- **No README** → Create mode: generate from scratch
- **README exists** → Update mode: read current file, identify missing/stale sections, preserve what's good

## Step 1: Analyze the Codebase

Run these checks silently before asking the user anything:

### Project identity
- `package.json` / `pyproject.toml` / `Cargo.toml` / `go.mod` — name, description, version, scripts
- `git remote -v` — GitHub remote URL (extract org/repo for links)
- `git log --oneline -10` — recent activity, infer project maturity

### Project type detection
Classify as one of: **CLI tool**, **Python/JS library**, **web app**, **backend service**, **data pipeline**, **other**

Detection signals:

| Type | Signals |
|---|---|
| CLI tool | `argparse`, `click`, `commander`, `bin` field in package.json, shebang scripts |
| Library | No `main` entry point, exports only, no web server setup |
| Web app | React/Vue/Next/Django/Flask with templates, frontend assets |
| Backend service | REST routes, GraphQL, webhooks, no frontend |
| Data pipeline | ETL scripts, YAML configs, scheduled jobs, no web layer |

### Conditional section signals

| Section | Include when |
|---|---|
| Badges | `.github/workflows/` exists OR `LICENSE` file found |
| Features | Project has >3 meaningful capabilities |
| Configuration | `.env.example` OR `config/` directory OR `settings.py` OR config flags in README/YAML |
| API docs | Route definitions found (`@app.route`, `router.get`, `app.use`) |
| Development setup | Active git repo with contributors or non-trivial build process |
| Testing | `tests/` or `test/` directory, or test files found |
| Contributing | GitHub remote detected |
| Changelog | `CHANGELOG.md` or `CHANGELOG.rst` exists |

## Step 2: Ask Targeted Questions

Ask only for what the codebase can't provide. Ask all needed questions at once (don't spread across multiple turns):

**Always ask:**
- "What does this project do?" (if package description is missing or too terse)
- "Who is the target audience?" (developers, end users, internal team, etc.)

**Ask only if applicable:**
- Live URL or demo link (if web app detected but no URL found)
- Logo or screenshot path (if web app or UI project)
- Whether the project is open source (affects Contributing section tone)

## Step 3: Write the README
Fetch this style guide before generating the `README.md` file:
[GitHub Docs: Basic writing and formatting syntax](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)

### Fixed section order

Always use this order. Omit conditional sections if their signal isn't present.

```
1. Title + description        [REQUIRED]
2. Badges                     [conditional: CI config or LICENSE found]
3. Features                   [conditional: >3 meaningful capabilities]
4. Quick Start                [REQUIRED]
5. Usage                      [REQUIRED]
6. Configuration              [conditional: .env.example or config files]
7. API Reference              [conditional: route definitions found]
8. Development                [conditional: non-trivial build or active contributors]
9. Testing                    [conditional: test directory found]
10. Contributing              [conditional: GitHub remote detected]
11. License                   [REQUIRED]
12. Changelog                 [conditional: CHANGELOG.md exists]
```

### Content adapts by project type

**Title + description**
- One-sentence description. No marketing fluff. What it does, not why it's great.

**Badges** (standard set only)

```markdown
![CI](https://github.com/ORG/REPO/actions/workflows/WORKFLOW.yml/badge.svg)
![License](https://img.shields.io/github/license/ORG/REPO)
```

Derive `ORG/REPO` from `git remote -v`. Use actual workflow filename from `.github/workflows/`.

**Quick Start** — adapts by type:
- *CLI*: install command + one working example invocation
- *Library*: `pip install` / `npm install` + minimal usage snippet
- *Web app*: clone → install deps → env setup → run dev server
- *Service*: clone → configure → start (Docker preferred if Dockerfile present)

**Usage** — adapts by type:
- *CLI*: show `--help` output block + 2-3 real command examples
- *Library*: code snippet showing the primary API (import → call → result)
- *Web app*: screenshot placeholder OR feature walkthrough with headings
- *Service*: primary endpoints table OR sequence diagram description

**Configuration** (when included):
- Table of all env vars: `Variable | Default | Description`
- Source from `.env.example` if present

**API Reference** (when included):
- Table of endpoints: `Method | Path | Description`
- Source from route definitions; don't fabricate

**Contributing** (when included):

```markdown
1. Fork the repo
2. Create a branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Push and open a Pull Request

See [GitHub Issues](https://github.com/ORG/REPO/issues) for open tasks.
```

**License**
- If `LICENSE` file exists: `This project is licensed under the [LICENSE NAME] — see [LICENSE](LICENSE) for details.`
- If no LICENSE file: `License not specified.` (don't invent one)

## Step 4: Write the File

**Create mode:** Write `README.md` at repo root.

**Update mode:**
1. Backup first: `cp README.md README.md.bak`
2. Identify which sections exist and which are missing or stale
3. Add missing sections in the correct position
4. Update stale sections (e.g., wrong commands, outdated dependency versions)
5. Preserve sections that look intentional and current

## Validation Before Writing

- [ ] All commands in Quick Start verified against actual scripts/Makefile/package.json
- [ ] Badge URLs use real ORG/REPO from `git remote`
- [ ] No placeholder text left in final output (`YOUR_ORG`, `example.com`, etc.)
- [ ] Section order matches fixed order above
- [ ] Conditional sections only included when their signal is present
- [ ] Update mode: backup created before any edits

## What Not to Do

- Don't include a Table of Contents for short READMEs (<6 sections)
- Don't add Acknowledgments, Roadmap, or Support sections unless user asks
- Don't invent API endpoints, env vars, or commands — only document what exists
- Don't use `project-doc-writer` for README; this skill owns it
- Don't add badges that link to external services not already configured in the repo
