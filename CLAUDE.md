# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Shop Sergeant is a Slack-centric volunteer hour tracking system for Makersmiths makerspace members (required 2 hrs/month). It supports two parallel workflows:

1. **Digital (QR)**: Member scans QR on physical sheet → Slack prefills `task-done <task_id>` → bot logs to Google Sheets
2. **Physical (OCR)**: Admin photos completed paper sheet → posts to `#task-intake` → Claude vision extracts data → bot logs to Sheets with `source=OCR`
3. **Admin queries**: Natural language queries in `#shop-sergeant` → Claude agent reads Sheets and responds

Google Sheets is the authoritative data store.

## Current State

Phase 0 complete: sign-up sheet tools built and tested (`signup-sheet-template.py`, `signup-sheet.py`). Ready for trial with stewards/members. No bot code yet. The 5-phase implementation plan is in `docs/implementation-plan.md`.

## Data Model

Hierarchical YAML structure: **Shop → Area → Location → Task** (with unique `task_id` like `MSL-METAL-001`)

Key data files:
- `input/tasks-list.yaml` — master task catalog (task_id fields still needed for most locations)
- `input/metalshop-volunteer-opportunity.yaml` — metalshop extended format; task_ids added (MSL-METAL-001…007)

## Available Commands

```bash
# Validate YAML
yamllint input/tasks-list.yaml

# Convert YAML → Markdown
python3 scripts/parse-tasks.py input/tasks-list.yaml output/tasks-list.md
python3 scripts/parse-opp-tasks.py input/metalshop-volunteer-opportunity.yaml output/metalshop-task-list.md

# Convert Markdown → Word doc
pandoc -f gfm output/tasks-list.md -o output/tasks-list.docx

# Convert YAML → JSON
python3 scripts/yaml-to-json.py input/tasks-list.yaml | jq -C '.'

# Generate sign-up sheet template (Jinja2)
python3 scripts/signup-sheet-template.py --output output/signup-sheet-template.html.j2

# Generate sign-up sheet HTML (metalshop example)
python3 scripts/signup-sheet.py \
    --template output/signup-sheet-template.html.j2 \
    --yaml input/metalshop-volunteer-opportunity.yaml \
    --output output/metalshop-signup-sheet.html

# Run tests
python3 -m pytest tests/ -v
```

## Tech Stack (Planned)

- **Python 3.11+** with Slack Bolt framework
- **Google Sheets API v4** — data persistence
- **Claude API** (`claude-sonnet-4-6`) — OCR and NL queries
- **`jinja2`** — HTML template rendering; **`qrcode[pil]`** — QR generation
- **`weasyprint`** — PDF rendering (Phase 1+)
- **APScheduler** — recurring reminders; **pytest** — testing

## Key Docs

- `docs/specifications.md` — system spec (data flows, Sheets schema, sign-up sheet design)
- `docs/implementation-plan.md` — detailed 5-phase implementation plan with file map and code examples
- `requirements/feature-list.yaml` — feature tracker
