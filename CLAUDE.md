# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Shop Sergeant is a volunteer hour tracking system for [Makersmiths](https://makersmiths.org) makerspace members (2 hrs/month required). Members find and sign up for tasks via physical sign-up sheets; the system manages the task catalog, sign-up sheet generation, completion capture, and reporting through Slack.

The system is Slack-centric: members interact via `#shop-bulletin`, `#shop-admin`, and `#shop-queries` channels. Google Sheets is the authoritative data store.

## Repo Structure

```
shop-sergeant/
├── production/          # Active code — sign-up sheet pipeline (Phase 0 complete)
│   ├── CLAUDE.md        # Detailed guidance for production work (read this when working in production/)
│   ├── scripts/         # Python CLI tools and shared libraries
│   ├── tests/           # pytest suite (conftest.py manages sys.path)
│   ├── input/           # YAML task catalogs, logo, reference docs
│   ├── output/          # Generated HTML/PDF/XLSX (tracked in git)
│   ├── templates/       # Feature/use-case tracker YAML templates
│   └── docs/            # Requirements, roadmap, engineering method docs
├── prototyping/
│   └── proto1/          # SQLite CRUD tools — AI-callable scripts for task DB
│       └── CLAUDE.md    # Detailed guidance for proto1 (read when working there)
├── presentations/       # Single Slidev project; multiple deck .md files + shared assets
└── logos_images/        # Logo assets
```

**Sub-level CLAUDE.md files are the authoritative guidance for their subtrees.** Always read the relevant one before working in `production/` or `prototyping/proto1/`.

## Quick Commands

```bash
# Run all production tests (from production/)
cd production && python3 -m pytest tests/ -v

# Run a single production test
cd production && python3 -m pytest tests/test_signup_sheet_builder.py::test_extract_locations_opportunity_count -v

# Run all proto1 tests (from prototyping/proto1/, requires uv)
cd prototyping/proto1 && uv run pytest ./tests/ -v

# Presentations — live dev server (from presentations/)
cd presentations && pnpm dev
```

## Implementation Phases

- **Phase 0** (complete): YAML → HTML/PDF sign-up sheet generation; trial with stewards/members
- **Phase 1–4** (planned): Slack bot, Google Sheets integration, QR/OCR task capture, NL reporting

## Key Data Concepts

YAML task catalog uses a 4-level hierarchy: **Shop → Area → Location → Task**. Each task has a unique `task_id` (e.g. `MSL-METAL-001`). Three root-key formats exist (`opportunity`, `opportunities`, `tasks_list`); all are normalized by `detect_format()` in `production/scripts/signup_sheet_builder.py`.

## Presentations

`presentations/` is a single Slidev project. Multiple deck source files live there (e.g. `requirements-review-april-30-2026.md`, `member-meeting-may-6-2026.md`); `slides.md` is the active entry point. Diagrams are `.excalidraw` files under `presentations/diagrams/`, exported to `presentations/assets/`.

```bash
cd presentations
pnpm dev        # live-reload dev server
pnpm build      # build static site → dist/
pnpm export     # export to PDF (requires playwright-chromium)
```

See `production/CLAUDE.md` §Presentations for full details on utilities and setup scripts.

## Tech Stack

- **Python 3.11+** — all production scripts; `uv` for dependency management in proto1
- **Jinja2 + qrcode[pil]** — sign-up sheet rendering (Phase 0)
- **Slack Bolt, Google Sheets API v4, Claude API (`claude-sonnet-4-6`)** — planned Phase 1+
- **pytest** — test runner for both `production/tests/` and `prototyping/proto1/tests/`
- **Slidev + Excalidraw** — presentation toolchain
