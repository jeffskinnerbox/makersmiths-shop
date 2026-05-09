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
├── presentations/       # Slidev decks (members-meeting/, requirements-review/)
└── logos_images/        # Logo assets
```

**Sub-level CLAUDE.md files are the authoritative guidance for their subtrees.** Always read the relevant one before working in `production/` or `prototyping/proto1/`.

## Implementation Phases

- **Phase 0** (complete): YAML → HTML/PDF sign-up sheet generation; trial with stewards/members
- **Phase 1–4** (planned): Slack bot, Google Sheets integration, QR/OCR task capture, NL reporting

Full plan will live in `production/docs/implementation-plan.md` (not yet created).

## Key Data Concepts

YAML task catalog uses a 4-level hierarchy: **Shop → Area → Location → Task**. Each task has a unique `task_id` (e.g. `MSL-METAL-001`). Three root-key formats exist (`opportunity`, `opportunities`, `tasks_list`); all are normalized by `detect_format()` in `production/scripts/signup_sheet_builder.py`.

## Presentations

Slide decks under `presentations/` are self-contained Slidev projects. Run all `pnpm` commands from inside the deck's subdirectory. See `production/CLAUDE.md` §Presentations for commands.

## Tech Stack

- **Python 3.11+** — all production scripts; `uv` for dependency management in proto1
- **Jinja2 + qrcode[pil]** — sign-up sheet rendering (Phase 0)
- **Slack Bolt, Google Sheets API v4, Claude API (`claude-sonnet-4-6`)** — planned Phase 1+
- **pytest** — test runner for both `production/tests/` and `prototyping/proto1/tests/`
- **Slidev + Excalidraw** — presentation toolchain
