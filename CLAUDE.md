# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Shop Sergeant is a Slack-centric volunteer hour tracking system for Makersmiths makerspace members (required 2 hrs/month). It supports two parallel workflows:

1. **Digital (QR)**: Member scans QR on physical sheet → Slack prefills `task-done <task_id>` → bot logs to Google Sheets
2. **Physical (OCR)**: Admin photos completed paper sheet → posts to `#task-intake` → Claude vision extracts data → bot logs to Sheets with `source=OCR`
3. **Admin queries**: Natural language queries in `#shop-sergeant` → Claude agent reads Sheets and responds

Google Sheets is the authoritative data store.

## Current State

Early implementation phase. Data model and specs are complete; no bot code exists yet. The 4-phase implementation plan is in `docs/2026-04-01-shop-sergeant.md`.

## Data Model

Hierarchical YAML structure: **Shop → Area → Location → Task** (with unique `task_id` like `MSL-METAL-001`)

Key data files:
- `tasks-list.yaml` — master task catalog (some tasks still need `task_id` fields added)
- `metalshop-volunteer-opportunity.yaml` — metalshop extended format with sub-tasks

## Available Commands

```bash
# Validate YAML
yamllint tasks-list.yaml

# Convert YAML → Markdown
python3 scripts/parse-tasks.py tasks-list.yaml tasks-list.md
python3 scripts/parse-opp-tasks.py metalshop-volunteer-opportunity.yaml metalshop-task-list.md

# Convert Markdown → Word doc
pandoc -f gfm tasks-list.md -o tasks-list.docx

# Convert YAML → JSON
python3 scripts/yaml-to-json.py tasks-list.yaml | jq -C '.'
```

## Tech Stack (Planned)

- **Python 3.11+** with Slack Bolt framework
- **Google Sheets API v4** — data persistence
- **Claude API** (`claude-sonnet-4-6`) — OCR and NL queries
- **`qrcode`** — QR generation; **`weasyprint`** — PDF rendering
- **APScheduler** — recurring reminders; **pytest** — testing

## Key Docs

- `docs/specifications.md` — system spec (data flows, Sheets schema, sign-up sheet design)
- `docs/2026-04-01-shop-sergeant.md` — detailed 4-phase implementation plan with file map and code examples
- `requirements/feature-list.yaml` — feature tracker
