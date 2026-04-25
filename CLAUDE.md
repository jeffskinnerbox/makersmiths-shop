# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Shop Sergeant is a Slack-centric volunteer hour tracking system for Makersmiths makerspace members (required 2 hrs/month). It is organized around four pipelines:

- **Task Database**: Maintains the master task catalog in Google Sheets; add/update/delete via Slack (`#shop-admin`) or YAML bulk-load
- **Task Sheet**: Generates printable sign-up sheets from the task catalog; posts to `#shop-bulletin` when ready
- **Task Capture**: Records completions via single-sheet QR → mobile web form (Method 3, likely), or OCR photo posted to `#shop-admin`
- **Task Reporting**: Natural language queries in `#shop-queries`; scheduled reports to `#shop-bulletin`; compliance reports restricted to Shop Steward+

Google Sheets is the authoritative data store.

## Current State

Phase 0 complete: sign-up sheet tools built and tested (`generate-signup-sheet-template.py`, `signup-sheet.py`, `signup-sheet2.py`). Ready for trial with stewards/members. No bot code yet. The 5-phase implementation plan is in `docs/implementation-plan.md`.

Two sign-up sheet variants exist:
- **v1** (`signup-sheet.py`) — one QR code per task row, 3 sign-off columns
- **v2** (`signup-sheet2.py`) — single QR code in page header, 4 sign-off columns, no per-task QR

## Data Model

Hierarchical YAML structure: **Shop → Area → Location → Task** (with unique `task_id` like `MSL-METAL-001`)

Key data files:
- `input/MSL-volunteer-opportunities.yaml` — master task catalog (root key: `opportunities`, plural)
- `input/metalshop-volunteer-opportunities.yaml` — metalshop extended format; task_ids MSL-METAL-001…007 (root key: `opportunities`)

## Available Commands

```bash
# Validate YAML
yamllint input/MSL-volunteer-opportunities.yaml

# Step 1: Generate Jinja2 template (run once; output is reusable)
python3 scripts/generate-signup-sheet-template.py --output output/signup-sheet-template.html.j2

# Step 2: Render HTML sign-up sheet from template + YAML
python3 scripts/signup-sheet.py \
    --template output/signup-sheet-template.html.j2 \
    --yaml input/metalshop-volunteer-opportunities.yaml \
    --output output/metalshop-signup-sheet.html
#   --location "Metalshop"      render a single location only
#   --qr-url "https://..."      override QR placeholder URL
#   --logo input/logo.png       override logo image path

# v2 sign-up sheet: single QR in header (run once for template, then render)
python3 scripts/generate-signup-sheet2-template.py --output output/signup-sheet2-template.html.j2
python3 scripts/signup-sheet2.py \
    --template output/signup-sheet2-template.html.j2 \
    --yaml input/metalshop-volunteer-opportunities.yaml \
    --output output/metalshop-signup-sheet2.html

# Step 3: Convert HTML to PDF (Phase 0 — requires wkhtmltopdf)
wkhtmltopdf --orientation Landscape output/metalshop-signup-sheet.html output/metalshop-signup-sheet.pdf
# Convenience scripts (template + HTML + PDF, then open PDF): bash scripts/print-metalshop.sh  or  bash scripts/print-MSL.sh
# Post scripts (template + HTML only, then open HTML in Chrome): bash scripts/post-metalshop.sh  or  bash scripts/post-MSL.sh

# Generate presentation slides as Excalidraw files → output/slides/slide-NN.excalidraw
python3 scripts/generate_slides.py

# Convert requirements.md → requirements.pdf
bash scripts/requirements-to-pdf.sh

# Convert YAML → Excel (for Google Sheets import)
python3 scripts/yaml-to-sheets.py --yaml input/MSL-volunteer-opportunities.yaml --output output/google-sheet.xlsx

# Clean up all generated output artifacts and .bak files (requires `trash` CLI, not rm)
bash scripts/clean-up.sh

# Run all tests
python3 -m pytest tests/ -v

# Run a single test (examples from each test module)
python3 -m pytest tests/test_signup_sheet_builder.py::test_extract_locations_opportunity_count -v
python3 -m pytest tests/test_signup_sheet_template.py::test_build_template_contains_jinja2_for_loop -v
python3 -m pytest tests/test_yaml_to_sheets.py::test_extract_rows_returns_correct_count -v
python3 -m pytest tests/test_parse_tasks.py::test_escape_pipe_character -v
python3 -m pytest tests/test_parse_opp_tasks.py -v
python3 -m pytest tests/test_yaml_to_json.py::test_convert_outputs_valid_json_to_stdout -v
python3 -m pytest tests/test_yaml_to_sheets.py::test_extract_rows_returns_correct_count -v
```

### Debugging / utility scripts (not production, no further development planned)

```bash
# Convert YAML → Markdown (3-col table)
python3 scripts/parse-tasks.py input/MSL-volunteer-opportunities.yaml output/MSL-volunteer-opportunities.md
# Convert YAML → Markdown (5-col extended table; opportunities format only)
python3 scripts/parse-opp-tasks.py input/metalshop-volunteer-opportunities.yaml output/metalshop-task-list.md
# Convert Markdown → Word doc (input/custom-reference.docx controls styles)
pandoc -f gfm output/MSL-volunteer-opportunities.md -o output/MSL-volunteer-opportunities.docx \
    --reference-doc input/custom-reference.docx
# Convert YAML → JSON
python3 scripts/yaml-to-json.py input/MSL-volunteer-opportunities.yaml | jq -C '.'
# Note: scripts/pdf-margins.css is used by requirements-to-pdf.sh only; not a standalone tool
```

## Presentations (Slidev + Excalidraw)

Slide decks live under `presentations/` — each subdirectory is a self-contained Slidev project with its own `package.json`. Currently:

- `presentations/members-meeting/` — members meeting overview
- `presentations/requirements-review/` — requirements walkthrough

All three `pnpm` commands must be run from inside the presentation subdirectory:

```bash
cd presentations/members-meeting   # or requirements-review
pnpm dev        # live-reload dev server (opens browser)
pnpm build      # build static site → dist/
pnpm export     # export to PDF (requires playwright-chromium)
```

Diagrams are authored as `.excalidraw` files in the `diagrams/` subdirectory of each deck and referenced directly by `slidev-addon-excalidraw`. Assets (PNG/SVG exports) live in `assets/`. Slides source is `slides.md` in each subdirectory.

### Presentation utilities (`presentations/scripts/`)

```bash
# One-time machine setup (Node >= 18, pnpm, Slidev CLI, Playwright/Chromium)
bash presentations/scripts/setup.sh

# Bootstrap a new deck (creates subdirectory, package.json, slides.md scaffold, runs pnpm install)
bash presentations/scripts/new-deck.sh <deck-name>

# Export all .excalidraw files in a deck's diagrams/ → assets/ as SVG (default) or PNG
python3 presentations/scripts/export-diagrams.py --input presentations/<deck>/diagrams/ --output presentations/<deck>/assets/
# Requires: pip install playwright && python3 -m playwright install chromium (first run)
```

New decks created with `new-deck.sh` are ready to use (`pnpm install` is run automatically). Existing decks cloned without `node_modules` need `pnpm install` before `pnpm dev`.

## Tech Stack (Planned)

- **Python 3.11+** with Slack Bolt framework
- **Google Sheets API v4** — data persistence
- **Claude API** (`claude-sonnet-4-6`) — OCR and NL queries
- **`jinja2`** — HTML template rendering; **`qrcode[pil]`** — QR generation
- **APScheduler** — recurring reminders; **pytest** — testing

## Script Architecture (Phase 0)

`scripts/signup-sheet.py` (CLI, argparse only) imports from `scripts/signup_sheet_builder.py` (library, all logic). Tests import from the library directly via `sys.path.insert`.

Key public API of `signup_sheet_builder.py`:

| Function | Purpose |
|---|---|
| `load_yaml(source)` | Load YAML from file path or stdin |
| `detect_format(data)` | Return root key (`opportunity`/`opportunities`/`tasks_list`) |
| `extract_locations(data)` | Parse shop→area→location→task hierarchy |
| `attach_qr_codes(locations, url)` | Generate QR codes and attach to tasks (v1) |
| `make_qr_b64(url)` | Return base64-encoded QR PNG (used by v2) |
| `_logo_data_uri(path)` | Return base64 data URI for logo image |
| `render_sheet(template, locations, meta)` | Render Jinja2 HTML with location/task data |

`scripts/generate-signup-sheet-template.py` (v1) and `scripts/generate-signup-sheet2-template.py` (v2) are both self-contained — `build_template()` lives in each CLI file. Tests import them via `importlib.util.spec_from_file_location`.

`scripts/signup-sheet2.py` imports `load_yaml`, `extract_locations`, `make_qr_b64`, `_logo_data_uri` from `signup_sheet_builder.py`. Its `render_sheet2()` takes `template_path`, `locations`, `logo_path`, and `qr_b64` (top-level, not per-task).

`scripts/parse-tasks.py` imports `load_yaml` from `signup_sheet_builder.py` and delegates table rendering to `markdown_writer.py`.

`scripts/parse-opp-tasks.py` also uses `markdown_writer.py` for rendering — no longer standalone. Parses `opportunities`-format YAML; emits per-location tables with task, frequency, purpose, instructions, and last-date columns.

`scripts/markdown_writer.py` — shared library for both parse scripts. Provides `ColumnDef` dataclass and `generate_markdown(title, shop, columns, extra_meta)` which handles the area/location/task loop.

`scripts/yaml-to-sheets.py` exposes testable functions: `load_yaml`, `detect_shop`, `extract_rows`, `validate`, `backup_existing`, `write_xlsx`, and the `COLUMNS` list. `validate()` checks for blank/duplicate `task_id` and duplicate task names within the same location (case-insensitive); exits on failure.

`tests/conftest.py` inserts `scripts/` into `sys.path` once for all tests — individual test files no longer need to do this themselves. Tests for scripts with hyphens (e.g. `parse-opp-tasks.py`, `yaml-to-json.py`) use `importlib.util.spec_from_file_location` since the filenames are not valid Python module identifiers.

Three YAML root keys, all handled by `detect_format()` in `signup_sheet_builder.py`:
- `opportunity` — single-area extended format
- `opportunities` — plural form of the same structure (both active input files use this)
- `tasks_list` — simpler master catalog format (supported in code and tests; no current input file uses it)

All formats use `work_tasks` for task lists (falling back to `task` key). Locations where all tasks are TBD or empty are silently skipped by `extract_locations()` (`skip_tbd=True` default).

Logo and image assets live in `input/`. The default logo path is `input/makersmiths-logo.png`. A copy also lives in `logos_images/makersmiths-logo.png`; see `logos_images/README.md` for logo asset notes.

`docs/my-prompts.md` is a log of the original design prompts used to bootstrap this project — not input data for any script.

Generated files in `output/` are tracked in git (`.gitignore` entries for `output/*` are commented out). Run `bash scripts/clean-up.sh` to remove them before regenerating.

## Diagrams

All diagrams created for this project must include both human actors and system actors as defined in `docs/requirements.md` §2.2 and §2.3:

- **Human actors:** Member, Steward, Shop Steward, Shop Sergeant
- **System actors:** Physical Sign-Up Sheet, QR Code, Mobile Phone, Mobile Web Form, Slack, Google Sheets, Claude AI Model, APScheduler, Agentic Workers

## Debugging

When encountering an error, consider writing a test case that reproduces it before fixing. This keeps the bug from regressing and grows the test suite.

## Key Docs

The documentation development follows this dependency chain:

```
                           use-cases.md ---------------------------------> test-cases.py
                                ^
                                |         +-----------> prototyping.md
                                |         |
my-understanding.md ---> requirements.md -+-> specifications.md ---> architecture.md ---> implementation-plan.md
```

`docs/my-engineering-method.md` explains the engineering method behind this chain and is the canonical reference for how these docs relate.

- `docs/my-understanding.md` — original vision doc (current process, actors, shortcomings, future goals)
- `docs/my-engineering-method.md` — engineering method overview; describes the doc lineage above
- `docs/requirements.md` — system requirements (pipelines, permissions, KPIs; all stakeholders)
- `docs/specifications.md` — system spec (data flows, Sheets schema, sign-up sheet design) **[not yet created]**
- `docs/implementation-plan.md` — detailed 5-phase implementation plan with file map and code examples **[not yet created]**
- `templates/feature-list.yaml` — feature tracker template (placeholder, not yet populated)
- `templates/use-case-list.yaml` — use case tracker template
- `ai_project_roadmap.md` / `ai_project_roadmap_V2.md` — AI-assisted roadmap docs (+ `.excalidraw` diagrams)
- `input/Leesburg Site-wide Cleaning and Maintenance Tasks.xlsx` — original source data from stewards
- `presentations/members-meeting/` — Slidev deck for members meeting (Excalidraw-integrated)
- `presentations/requirements-review/` — Slidev deck for requirements walkthrough
