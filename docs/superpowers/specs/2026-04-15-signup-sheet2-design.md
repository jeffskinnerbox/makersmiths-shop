---
title: signup-sheet2 — Single QR Header Layout
date: 2026-04-15
status: approved
---

# signup-sheet2 Design

Alternative volunteer sign-up sheet format. Replaces per-task QR codes with a single QR code in the page header, and adds a 4th "Member Name / Date" sign-off column using the freed space.

## What Changes vs. signup-sheet (v1)

| | signup-sheet (v1) | signup-sheet2 (v2) |
|---|---|---|
| QR code | One per task row (same URL, 85px column) | One per page, top-left header zone |
| Sign-off columns | 3 × "Member Name / Date" | 4 × "Member Name / Date" |
| Task name col width | 48% | 46% |
| `col-qr` table column | Yes | Removed |

## Header Layout

4-zone flex row, left-to-right:

```
[ QR ~90px ] [ Location / Steward ] [ Title (center) ] [ Logo ]
```

- QR image: 80×80px, embedded as base64 PNG data URI
- Location/Steward: same font sizes as v1 (12pt bold / 10pt bold)
- Title: same (30pt bold red)
- Logo: same (55px tall, base64 data URI)

## Table Columns

| Column | Width | Notes |
|---|---|---|
| Task Name | 46% | Includes task_id (bottom-left) and instructions (8pt) |
| Last Done | 10% | Centered |
| Frequency | 8% | Centered |
| Member Name / Date × 4 | 9% each | Blank sign-off cells |

Total: 46 + 10 + 8 + 36 = 100%

## Scripts

### `scripts/generate-signup-sheet2-template.py`

- Same structure as `generate-signup-sheet-template.py`
- CLI args: `--output`, `--title`, `--footer`, `--location-font-size`, `--steward-font-size`, `--title-font-size`, `--footer-font-size`
- Produces `output/signup-sheet2-template.html.j2`

### `scripts/signup-sheet2.py`

- Same CLI args as `signup-sheet.py` (`--template`, `--input`, `--output`, `--location`, `--qr-url`, `--logo`)
- Imports `load_yaml`, `extract_locations`, `make_qr_b64`, `_logo_data_uri` from `signup_sheet_builder`
- Generates **one** QR code via `make_qr_b64(qr_url)` — not per-task
- Renders template directly (inline Jinja2 env+render) passing `locations`, `logo_path`, and `qr_b64` as top-level variables
- No changes to `signup_sheet_builder.py`

## Template Variables

The `.html.j2` template receives:

| Variable | Type | Source |
|---|---|---|
| `locations` | list[dict] | `extract_locations()` — same structure as v1 |
| `logo_path` | str \| None | Base64 data URI from `_logo_data_uri()` |
| `qr_b64` | str | Base64 PNG from `make_qr_b64()` — single value, top-level |

Tasks no longer carry a `qr_b64` field. The template reads `qr_b64` once in the header, not per-row.

## Out of Scope

- No changes to `signup_sheet_builder.py`
- No new tests (follows Phase 0 pattern — visual output reviewed manually)
- No convenience shell scripts (`print-*.sh`, `post-*.sh`) for now
