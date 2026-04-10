# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Shop Sergeant is a Slack-centric volunteer hour tracking system for Makersmiths makerspace members (required 2 hrs/month). It supports two parallel workflows:

1. **Digital (QR)**: Member scans QR on physical sheet → Slack prefills `task-done <task_id>` → bot logs to Google Sheets
2. **Physical (OCR)**: Admin photos completed paper sheet → posts to `#task-intake` → Claude vision extracts data → bot logs to Sheets with `source=OCR`
3. **Admin queries**: Natural language queries in `#shop-sergeant` → Claude agent reads Sheets and responds

Google Sheets is the authoritative data store.

## Current State

Phase 0 complete: sign-up sheet tools built and tested (`generate-signup-sheet-template.py`, `signup-sheet.py`). Ready for trial with stewards/members. No bot code yet. The 5-phase implementation plan is in `docs/implementation-plan.md`.

## Data Model

Hierarchical YAML structure: **Shop → Area → Location → Task** (with unique `task_id` like `MSL-METAL-001`)

Key data files:
- `input/MSL-volunteer-opportunities.yaml` — master task catalog (root key: `opportunities`, plural)
- `input/metalshop-volunteer-opportunities.yaml` — metalshop extended format; task_ids MSL-METAL-001…007 (root key: `opportunities`)

## Available Commands

```bash
# Validate YAML
yamllint input/MSL-volunteer-opportunities.yaml

# Convert YAML → Markdown
# parse-tasks.py: simple 3-col table (Task, Completion Date, Frequency); handles all root key formats
python3 scripts/parse-tasks.py input/MSL-volunteer-opportunities.yaml output/MSL-volunteer-opportunities.md
# parse-opp-tasks.py: extended 5-col table (task, frequency, purpose, instructions, last-date); opportunities format only
python3 scripts/parse-opp-tasks.py input/metalshop-volunteer-opportunities.yaml output/metalshop-task-list.md

# Convert Markdown → Word doc (input/custom-reference.docx controls styles)
pandoc -f gfm output/MSL-volunteer-opportunities.md -o output/MSL-volunteer-opportunities.docx \
    --reference-doc input/custom-reference.docx

# Convert YAML → Excel (for Google Sheets import)
python3 scripts/yaml-to-sheets.py
python3 scripts/yaml-to-sheets.py --yaml input/MSL-volunteer-opportunities.yaml --output output/google-sheet.xlsx

# Convert YAML → JSON
python3 scripts/yaml-to-json.py input/MSL-volunteer-opportunities.yaml | jq -C '.'

# Step 1: Generate Jinja2 template (run once; output is reusable)
python3 scripts/generate-signup-sheet-template.py --output output/signup-sheet-template.html.j2

# Step 2: Render HTML sign-up sheet from template + YAML
python3 scripts/signup-sheet.py \
    --template output/signup-sheet-template.html.j2 \
    --yaml input/metalshop-volunteer-opportunities.yaml \
    --output output/metalshop-signup-sheet.html

# Step 3: Convert HTML to PDF (Phase 0 — requires wkhtmltopdf)
wkhtmltopdf --orientation Landscape output/metalshop-signup-sheet.html output/metalshop-signup-sheet.pdf
# Convenience scripts (template + HTML + PDF, then open PDF): bash scripts/print-metalshop.sh  or  bash scripts/print-MSL.sh
# Post scripts (template + HTML only, then open HTML in Chrome): bash scripts/post-metalshop.sh  or  bash scripts/post-MSL.sh

# Clean up all generated output artifacts and .bak files (requires `trash` CLI, not rm)
bash scripts/clean-up.sh

# Optional flags for signup-sheet.py:
#   --location "Metalshop"      render a single location only
#   --qr-url "https://..."      override QR placeholder URL
#   --logo input/logo.png       override logo image path

# Run all tests
python3 -m pytest tests/ -v

# Run a single test (examples from each test module)
python3 -m pytest tests/test_signup_sheet_builder.py::test_extract_locations_opportunity_count -v
python3 -m pytest tests/test_signup_sheet_template.py::test_build_template_contains_jinja2_for_loop -v
```

## Tech Stack (Planned)

- **Python 3.11+** with Slack Bolt framework
- **Google Sheets API v4** — data persistence
- **Claude API** (`claude-sonnet-4-6`) — OCR and NL queries
- **`jinja2`** — HTML template rendering; **`qrcode[pil]`** — QR generation
- **`weasyprint`** — PDF rendering (Phase 1+)
- **APScheduler** — recurring reminders; **pytest** — testing

## Script Architecture (Phase 0)

`scripts/signup-sheet.py` (CLI, argparse only) imports from `scripts/signup_sheet_builder.py` (library, all logic). Tests import from the library directly via `sys.path.insert`.

`scripts/generate-signup-sheet-template.py` is self-contained — `build_template()` lives in the CLI file itself. Tests import it via `importlib.util.spec_from_file_location`.

`scripts/parse-opp-tasks.py` is also standalone (no library split) — parses `opportunities`-format YAML and emits per-location Markdown tables with task, frequency, purpose, instructions, and last-date columns.

Three YAML root keys, all handled by `detect_format()` in `signup_sheet_builder.py`:
- `opportunity` — single-area extended format
- `opportunities` — plural form of the same structure (both active input files use this)
- `tasks_list` — simpler master catalog format (supported in code and tests; no current input file uses it)

All formats use `work_tasks` for task lists (falling back to `task` key). Locations where all tasks are TBD or empty are silently skipped by `extract_locations()` (`skip_tbd=True` default).

`extract_locations()` also falls back to `loc.get("stward", ...)` when reading the steward field — this tolerates a known typo present in some legacy YAML data.

Logo and image assets live in `input/`. The default logo path is `input/makersmiths-logo.png`. A copy also lives in `logos_images/makersmiths-logo.png`; see `logos_images/README.md` for logo asset notes.

`_archive/` contains superseded scripts and YAML files from before the current architecture; ignore them when navigating the codebase.

`input/my-prompts.md` is a log of the original design prompts used to bootstrap this project — not input data for any script.

## Debugging

When encountering an error, consider writing a test case that reproduces it before fixing. This keeps the bug from regressing and grows the test suite.

## Key Docs

- `docs/specifications.md` — system spec (data flows, Sheets schema, sign-up sheet design)
- `docs/implementation-plan.md` — detailed 5-phase implementation plan with file map and code examples
- `requirements/feature-list.yaml` — feature tracker (template/placeholder, not yet populated)
- `requirements/use-case-list.yaml` — use case tracker
