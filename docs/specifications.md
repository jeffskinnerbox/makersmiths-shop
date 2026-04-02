# Shop Sergeant — Slack-Centric Hybrid System Specification

**Date:** 2026-04-01
**Status:** Draft

---

## 1. Context & Problem

Makersmiths members are required to volunteer 2 hours/month for makerspace upkeep. Tasks are posted on physical sign-up sheets around two locations (Leesburg MSL, Purcellville MSP). Members sign and date completed tasks. Periodically, admin staff manually transcribe sheet data into a Google Sheets log, which serves as the source of truth for volunteer tracking and reporting.

**Goals:**
- Minimize friction for members — effort should go into doing the task, not bookkeeping
- Support both physical signing (pen on paper) and digital logging (phone/Slack)
- Keep Google Sheets as the authoritative data store
- Give admin staff a low-effort, automated workflow for data collection and reporting

---

## 2. System Overview

A **Slack-Centric Hybrid** approach with two parallel data flows feeding one Google Sheet:

- **Digital flow:** QR code on sheet → member scans → Slack opens with task pre-filled → member taps Send → bot logs instantly to Sheets
- **OCR flow:** Member signs physical sheet → admin photographs sheet → posts to Slack → Claude OCRs the image → admin confirms → Sheets updated

All admin workflow (queries, reports, reminders, sheet generation) is handled via a Claude-powered Slack bot.

---

## 3. Sign-Up Sheet Design

### Format
Each 8.5×11 sheet covers one location (e.g., Metal Shop, Leesburg). Columns:

| Task Name | Frequency | Member (sign) | Date | Log It (QR) |
|-----------|-----------|---------------|------|-------------|
| Clean welding tables | Weekly | _(sign here)_ | _(date)_ | [QR image] |

- Physical columns remain unchanged — members can sign with pen as before
- New **Log It** column adds a per-task QR code for digital logging

### QR Code Encoding
Each QR encodes a Slack deep link with the stable task ID:

```
slack://channel?team=<TEAM_ID>&id=<TASK_LOG_CHANNEL_ID>&message=task-done%20MSL-METAL-001
```

On scan, Slack opens with `#task-log` pre-filled. Member taps Send. Total: 2 taps.

### Task IDs
Each task in `tasks-list.yaml` gets a stable ID field (e.g., `MSL-METAL-001`). Format: `<SHOP>-<AREA_CODE>-<SEQ>`.

### Generation Pipeline

**Phase 0 (trial — HTML output):**
1. `signup-sheet-template.py` generates a reusable Jinja2 `.html.j2` template
2. `signup-sheet.py` parses YAML, generates per-task QR codes (inline base64 PNG), renders HTML
3. Admin opens HTML in browser → File > Print → save as PDF or print directly
- QR codes encode `https://makersmiths.org` as placeholder until Slack bot is live

**Phase 1 (automated — PDF output):**
1. `generate-sheets.py` encodes live Slack deep links in QR codes
2. Output is PDF (via `weasyprint`) for direct posting or bot-triggered generation

---

## 4. Slack Channels

| Channel | Purpose | Access |
|---------|---------|--------|
| `#task-log` | Member completions via QR scan | All members |
| `#task-intake` | Admin posts sheet photos for OCR | Admin only |
| `#shop-sergeant` | Admin queries, reports, commands | Admin only |
| `#announcements` | Scheduled bot reminders | Bot posts only |

---

## 5. Slack Bot Behaviors

### Member: Digital Completion (QR flow)
1. Member scans QR → Slack opens with draft: `task-done MSL-METAL-001`
2. Member taps Send in `#task-log`
3. Bot resolves task ID → fetches task name + location from task catalog
4. Bot appends row to Google Sheets (`source = QR`)
5. Bot replies in thread: `✅ Jeff Smith completed Clean welding tables (Metal Shop, Leesburg) — Apr 1 2026. Thanks!`

### Admin: OCR Collection (physical fallback)
1. Admin photographs completed sign-up sheet
2. Admin posts photo to `#task-intake`
3. Bot sends image to Claude vision API with sheet context (location, task list)
4. Claude returns structured JSON: `[{task_id, member_name, date, confidence}]`
5. Bot formats results as a threaded Slack message with action buttons:
   - Rows with high confidence: listed for bulk confirm
   - Rows with low confidence: flagged individually with `[✅ Confirm] [✏️ Edit] [❌ Discard]`
6. Admin confirms → bot appends rows to Sheets (`source = OCR` or `OCR-flagged`)

### Admin: Natural Language Queries (`#shop-sergeant`)
Bot passes message + Google Sheets data to Claude agent. Examples:
- "Who hasn't logged hours for March?" → queries log, cross-references member roster, lists gaps
- "Generate monthly report" → summarizes completions by member and area, posts to channel
- "Which tasks are overdue?" → compares last completion dates vs frequency
- "Generate sign-up sheet for Wood Shop" → triggers PDF generation with fresh QR codes
- "Send reminders to members with no March hours" → DMs listed members

### Scheduled Reminders
Bot posts to `#announcements` on configurable schedule:
- **15th of each month:** "Halfway through [Month] — have you logged your volunteer hours?"
- **End of month (3 days before):** "Only 3 days left to log [Month] hours!"

---

## 6. Google Sheets Data Model

### Sheet: `task-log` (append-only)

| Column | Type | Notes |
|--------|------|-------|
| `timestamp` | datetime | When row was appended |
| `member_name` | string | From Slack display name (QR) or OCR |
| `slack_id` | string | Slack user ID — empty for OCR-only entries |
| `task_id` | string | Stable ID from YAML (e.g., `MSL-METAL-001`) |
| `task_name` | string | Human-readable task name |
| `location` | string | Shop/area name |
| `shop` | string | `MSL` or `MSP` |
| `completion_date` | date | Date task was done (not necessarily today) |
| `source` | enum | `QR`, `OCR`, `OCR-flagged`, `Manual` |
| `notes` | string | Admin notes, OCR confidence flags |

Rows are never edited or deleted. Corrections are new rows with `source = Manual`.

### Sheet: `members`

| Column | Type | Notes |
|--------|------|-------|
| `member_name` | string | Full display name |
| `slack_id` | string | For linking OCR entries to Slack identity |
| `active` | boolean | Filter inactive members from reports |

Admin-managed manually (populated by admin team from existing membership records). Used by Claude to identify members with zero logged hours.

### Sheet: `task-catalog`

| Column | Type | Notes |
|--------|------|-------|
| `task_id` | string | Stable ID |
| `task_name` | string | |
| `location` | string | |
| `shop` | string | |
| `frequency` | string | Weekly, Bi-Weekly, Monthly, etc. |
| `last_generated` | date | Last time a sheet was printed with this task |

Synced from YAML when sheets are generated. Allows Claude to resolve task IDs without re-reading YAML at runtime.

---

## 7. Technology Stack

| Component | Technology |
|-----------|-----------|
| Bot framework | Slack Bolt for Python |
| AI / OCR / agent | Claude API (`claude-sonnet-4-6`), vision + tool use |
| Data store | Google Sheets API v4 |
| QR generation | Python `qrcode` library |
| Sheet template | Python `jinja2` |
| HTML rendering | Browser print-to-PDF (Phase 0); Python `weasyprint` (Phase 1+) |
| Hosting | Makersmiths on-premise server (Linux) |
| Config / secrets | Environment variables or `.env` file |
| Task data | Existing `tasks-list.yaml` + `parse-tasks.py` pipeline |

---

## 8. Phased Implementation

### Phase 0 — Sign-Up Sheet Tools (Trial) ✅
- Add `task_id` fields to `metalshop-volunteer-opportunity.yaml`
- Create `signup-sheet-template.py` (Jinja2 template generator)
- Create `signup-sheet.py` (YAML + template → HTML sign-up sheet)
- QR codes encode `https://makersmiths.org` as placeholder
- Trial: post sheets at MSL Metalshop, collect steward/member feedback

**Test:** Generate metalshop sheet, print, post, review with steward.

### Phase 1 — Foundation
- Add stable `task_id` fields to `tasks-list.yaml` (all locations)
- Create `generate-sheets.py`: encodes live Slack deep links in QR codes, renders PDFs via `weasyprint`
- Set up Google Sheets with `task-log`, `members`, `task-catalog` sheets
- Verify QR → Slack deep link flow manually

**Test:** Generate a sheet for Metal Shop, scan a QR, confirm Slack opens with correct pre-fill.

### Phase 2 — Slack Bot (Digital Flow)
- Create Slack app, configure Bolt bot, deploy to server
- Implement `task-done <task_id>` message handler
- Resolve task ID from `task-catalog`, append row to `task-log`
- Reply with confirmation message in thread

**Test:** Post `task-done MSL-METAL-001` in `#task-log`, verify Google Sheet row appended.

### Phase 3 — OCR Flow
- Implement image upload handler in `#task-intake`
- Call Claude vision API with sheet image + context prompt
- Parse structured JSON response
- Format Slack confirmation UI with action buttons
- Handle confirm/edit/discard actions → append to Sheets

**Test:** Post photo of a filled-out test sheet, confirm Claude parses correctly, confirm Sheets updated after admin approval.

### Phase 4 — Admin Agent
- Implement natural language handler in `#shop-sergeant`
- Claude agent with Google Sheets read access
- Built-in intents: monthly report, overdue tasks, zero-hours members, sheet generation
- Scheduled reminder posts

**Test:** Ask "Who hasn't logged hours this month?" and verify response matches Sheets data.

- Monthly reports are posted to `#shop-sergeant` in Slack **and** emailed to leadership. Claude generates the summary; bot handles both delivery channels.

---

## 9. Unresolved Questions

1. **Slack deep links on Android vs iOS** — deep link format may differ; needs testing on both platforms before Phase 1 sign-off.
2. **OCR prompt tuning** — Claude's accuracy on handwritten names depends on sheet layout; may need iteration with real sheet samples (images exist in `signup_sheets/`).
3. **Multi-completion per task** — can a task appear on multiple sheets (different months)? How does the system distinguish a March completion from an April one for the same task?
