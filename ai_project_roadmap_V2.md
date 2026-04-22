# Shop Sergeant: Documentation & Prototyping Roadmap V2

## Context

Shop Sergeant is an AI-enabled volunteer hour tracking system for Makersmiths makerspace,
built on **Claude API** (`claude-sonnet-4-6`), **Slack Bolt** (Python 3.11+),
**Google Sheets API v4**, and a **mobile web form** (no app install).
Requirements are documented in `docs/requirements.md`.

Four pipelines define the system: **Task Database**, **Task Sheet**, **Task Capture**,
and **Task Reporting**. This roadmap is restructured around those pipelines as the
primary implementation axis — Phases 3–6 each deliver one pipeline end-to-end.

---

## Approach: Parallel Track → Pipeline-by-Pipeline Build

Phases 0–2 run the parallel architecture + prototyping approach from Roadmap V1.
From Phase 3 onward, each pipeline is a self-contained phase with its own specification,
implementation, and exit criteria — sequenced by dependency.

```
Phase 0: Requirements + Trials
    │
    ├──[Track 1]──► Architecture Skeleton
    │                      │
    ├──[Track 2]──► Prototype Findings ──┘
    │
    ├──► Phase 2: Architecture Convergence
    │              │
    │         [key decisions locked]
    │              │
    ├──► Phase 3: Task Database Pipeline  (foundation for all)
    │              │
    ├──► Phase 4: Task Sheet Pipeline     (depends on Phase 3)
    │              │
    ├──► Phase 5: Task Capture Pipeline   (depends on Phases 3–4)
    │              │
    └──► Phase 6: Task Reporting Pipeline (depends on all)
```

---

## Phase 0: Requirements Lock + Current Trials
*Pre-condition — partially complete*

### Complete

- `scripts/signup-sheet.py`, `signup-sheet2.py` — HTML/PDF sign-up sheet generation
- `scripts/generate-signup-sheet-template.py`, `generate-signup-sheet2-template.py` — Jinja2 template generation
- `scripts/yaml-to-sheets.py` — YAML → Excel for Google Sheets import
- `scripts/parse-tasks.py`, `parse-opp-tasks.py` — YAML → Markdown review tools
- Automated tests: all passing (`pytest tests/ -v`)

### Remaining Trials

| Trial | Objective | Outcome Needed |
|---|---|---|
| **Sign-up sheet UX** | Deploy printed sheets with stewards and members; assess readability, task clarity | Confirm sheet format works on the shop floor |
| **QR → mobile form** | Prototype scanning QR code → mobile web form; validate ≤2-tap flow (TC-5), no-login UX (TC-6) | Validate or flag Method 3 before building it |
| **OCR proof-of-concept** *(optional)* | Photograph completed sheet → `claude-sonnet-4-6` vision API; assess extraction accuracy under real shop conditions | Decide whether Method 1 (OCR) is a viable fallback |

### Exit Criteria

- Requirements approved by all stakeholders
- Capture method selected from §5.3 (Method 1 OCR / Method 2 per-task QR / Method 3 single-sheet QR; likely Method 3)
- Key architectural unknowns identified and assigned to prototype sprints (Phase 1)

---

## Phase 1: Parallel Launch (2–3 weeks)

### Track 1 — Architecture Document (structural sections)

Write sections that are requirements-derivable and platform-independent:

| Section | Content | Source |
|---|---|---|
| System context & pipeline boundaries | 4 pipelines (Task Database, Task Sheet, Task Capture, Task Reporting); what each does and does not do | §4.1, §5.1–5.4 |
| Actors | 9 system actors (Physical Sign-Up Sheet, QR Code, Mobile Phone, Mobile Web Form, Slack, Google Sheets, Claude AI Model, APScheduler, Agentic Workers) + 4 human actors (Member, Steward, Shop Steward, Shop Sergeant) | §2.2–2.3 |
| Slack channel structure | 5 channels: `#shop-log`, `#shop-bulletin`, `#shop-queries`, `#shop-admin` 🔒, `#shop-alerts` 🔒; who reads and writes each | §7.2 |
| Permission model design | Role matrix (Member / Steward / Shop Steward / Shop Sergeant) for all 13 bot actions (§7.1); Slack channel membership as primary access control | §7.3, §8.4 |
| Google Sheets data structure | `tasks` sheet, `completions` sheet, `members` sheet (required for M1/O1 KPIs — currently a gap in §9); shop-prefixed Task IDs (`MSL-LOCATION-NNN`) | §9 M1/O1, DB-1, DB-5 |
| Deployment topology | Python bot process hosting Slack Bolt and APScheduler; no mobile app; mobile web form served from bot process or co-located service | §4.2, §8.1 |
| Security model | Slack channel membership = access control; service account credentials for Google Sheets API v4; no additional auth system required | §8.4 |
| Multi-shop extensibility | All IDs shop-prefixed (`MSL-`, `MSP-`); initial deploy for MSL only; adding MSP must not require architectural changes | §8.5 |

**Leave open** (defer to prototype findings): Claude prompt patterns, Sheets schema
field-level detail, mobile form design specifics, notification fan-out pattern.

### Track 2 — Prototype Sprints (1 week each, throwaway code)

| Sprint | Target | Specific Questions to Answer |
|---|---|---|
| **P1 — Claude API** | Natural language + OCR | How accurately does `claude-sonnet-4-6` parse `#shop-queries` NL questions (e.g., "What tasks are overdue in the metalshop?")? What prompt structure reliably extracts names, Task IDs, and dates from sign-up sheet photos (Method 1)? Stateless (re-send context each call) vs. stateful (maintain session) — which is practical for multi-turn Slack conversations? What is p95 latency under realistic query load? |
| **P2 — Slack Bolt** | Command handling + channel routing | Do Slack Bolt event handlers reliably parse `#shop-admin` command patterns (`sheet metalshop`, `add task "Inspect welding gear" weekly`, `delete MSL-METAL-002`)? Can the bot enforce channel-specific behavior (e.g., refuse compliance report in `#shop-queries`)? How do Slack interactive components (buttons, modals) work for mobile form confirmation flows? |
| **P3 — Google Sheets** | Read/write + auth | Can the bot write a completion record to the `completions` sheet within TC-2 (immediately on submission)? What are real API rate limits (100 req/100s per user) under concurrent task logging? Does service account auth hold up reliably for all 4 pipelines? What retry strategy handles write timeouts (e.g., `BOT_ERROR Google Sheets write timeout — retry succeeded after 2s`)? |
| **P4 — Mobile Web Form** | QR → form → POST | Can a single-page mobile web form (no app, no login) achieve ≤2 taps from QR scan to completion confirmation (TC-5, TC-6)? What is the minimum viable form design? Does POST to bot endpoint work reliably on mobile networks in the shop? Is a PWA (service worker + offline support) warranted, or is a plain web page sufficient? |

---

## Phase 2: Architecture Convergence (1 week)

### Key Decisions

| Decision | Context | Informed By |
|---|---|---|
| **Capture method: final selection** | Method 3 (single-sheet QR → mobile web form) is the likely choice (§5.3). Confirm, or formally retire Method 1 (OCR) and Method 2 (per-task QR). If OCR is kept as a fallback, scope it explicitly. | Phase 0 trial + P1/P4 findings |
| **Claude integration pattern** | Stateless (re-send Sheets context with each API call) vs. stateful (maintain session state across Slack events). Affects Agentic Workers design and Sheets read frequency. | P1 findings |
| **Sheets write strategy** | Real-time per-event write (simplest, highest API load) vs. write queue with batch commits (more complex, lower API load). Must satisfy TC-2 (immediate write on submission). | P3 findings |
| **Members sheet timing** | Add `members` sheet (name, Slack handle, role, join_date, status) now in Phase 3, or defer until compliance reporting becomes a live need. Required for M1 and O1 KPIs (§9). | Architecture team |
| **Mobile form hosting** | Same Python process as the Slack bot, or a separate lightweight service (Flask/FastAPI)? Affects deployment complexity and Phase 5 scope. | P4 findings |
| **Notification fan-out pattern** | When one Slack event (e.g., OCR photo posted to `#shop-admin`) triggers writes to Google Sheets + posts to `#shop-log` + `#shop-alerts`, what is the sequencing and error isolation model? | P2 + P3 findings |

### Deliverables

- Architecture Document finalized (all sections complete)
- Decision record written for each item above
- Internal architecture review and sign-off

---

## Phase 3: Task Database Pipeline

*Establishes the Google Sheets foundation that all subsequent pipelines depend on.*

**Requirements: DB-1 through DB-7 (§5.1)**

### Specification

| Artifact | Contents |
|---|---|
| **Google Sheets schema** | `tasks` sheet: `task_id` (MSL-LOCATION-NNN), `name`, `location`, `area`, `shop`, `frequency` (Daily/Weekly/Bi-Weekly/Monthly/Quarterly), `time` (minutes), `supervisor_required` (bool), `instructions`, `last_date`. `completions` sheet: `member_name`, `task_id`, `completion_date`, `source` (QR/OCR/form). `members` sheet: `name`, `slack_handle`, `role` (member/steward/shop_steward/shop_sergeant), `join_date`, `status` (active/inactive). |
| **Slack command formats** | `add task <location> "<name>" <frequency> [supervised]` → creates task with next available Task ID and notifies `#shop-alerts`. `update <task_id> <field> <value>` → modifies a single field. `delete <task_id> [reason]` → removes task and logs reason. |
| **Validation rules** | Reject duplicate Task IDs (DB-6). Reject duplicate task names within same location, case-insensitive (DB-6). Reject modifications by unauthorized roles (DB-4). |
| **`#shop-alerts` notification schema** | Every CRUD event: `[timestamp] TASK_CREATED\|UPDATED\|DELETED <task_id> by @<user>` (DB-7) |

### Implementation

1. Google Sheets service account auth setup; provision `tasks`, `completions`, `members` sheets
2. YAML bulk-load integration: `yaml-to-sheets.py` → `tasks` sheet (DB-2)
3. Slack Bolt skeleton: event subscriptions for `#shop-admin`, channel-aware permission checks
4. `add`, `update`, `delete` command handlers writing to `tasks` sheet via Sheets API v4 (DB-3)
5. Role enforcement: Steward commands scoped to own location; Shop Steward/Shop Sergeant unrestricted (DB-4)
6. Validation: reject duplicate Task IDs and duplicate names within location before writing (DB-6)
7. `#shop-alerts` notification on every CRUD event (DB-7)

### Exit Criteria

- `tasks`, `completions`, `members` sheets provisioned and populated with MSL test data
- YAML bulk-load verified end-to-end against live Sheets
- All 3 Slack commands (`add`, `update`, `delete`) working with correct permission enforcement
- `#shop-alerts` notification firing on every CRUD event
- Unit tests passing for all DB-1 through DB-7 requirements

---

## Phase 4: Task Sheet Pipeline

*Integrates the existing CLI sign-up sheet scripts into the Slack bot.*

**Requirements: TS-1 through TS-6 (§5.2)**

**Depends on:** Phase 3 (task catalog must be live in Google Sheets)

### Specification

| Artifact | Contents |
|---|---|
| **Slack command format** | `sheet <location>` — generate PDF for one location (TS-1, TS-3). `sheet all` — generate PDFs for all locations. Restricted to Steward (own location), Shop Steward, Shop Sergeant (TS-2). |
| **PDF generation handoff** | Bot reads task list from `tasks` sheet; calls existing `scripts/signup-sheet.py` (or `signup-sheet2.py`) via subprocess or direct import, replacing the YAML file input. |
| **Notification schema** | `#shop-bulletin`: "Metalshop sign-up sheet ready — N tasks — [Download PDF →]" (TS-4). `#shop-alerts`: `SHEET_GENERATED <location> by @<user> (N tasks)` (TS-5). |
| **Refresh reminder logic** | APScheduler job: when `tasks` sheet changes (CRUD event) without a corresponding `SHEET_GENERATED` event for that location within a configurable window, post reminder to `#shop-admin` (TS-6). |

### Implementation

1. Wire `sheet <location>` and `sheet all` commands in Slack Bolt with permission check
2. Sheets → script bridge: query `tasks` sheet by location, pass data to existing sheet-generation scripts
3. Post generated PDF to `#shop-bulletin` with download link (TS-4)
4. Log `SHEET_GENERATED` event to `#shop-alerts` on every generation (TS-5)
5. APScheduler: track `last_sheet_generated` timestamp per location; trigger refresh reminder when task catalog has been modified after the last sheet generation (TS-6)

### Exit Criteria

- `sheet metalshop` generates correct PDF from live Sheets data
- `sheet all` generates one sheet per location without errors
- `#shop-bulletin` and `#shop-alerts` notifications firing correctly
- Refresh reminder posts to `#shop-admin` when tasks are modified after the last sheet generation
- Unauthorized users receive a rejection message

---

## Phase 5: Task Capture Pipeline

*The core member-facing flow. Method 3 (single-sheet QR → mobile web form) is the likely selection.*

**Requirements: TC-1 through TC-6 (§5.3)**

**Depends on:** Phase 3 (task catalog), Phase 4 (QR codes on sign-up sheets)

### Specification

| Artifact | Contents |
|---|---|
| **Mobile web form** | Single-page, mobile-optimized. Loaded by scanning QR code on sign-up sheet. Shows location name and task list. Member enters name, selects task, taps Submit. No login or account required (TC-6). Target: ≤2 taps from scan to confirmation (TC-5). |
| **POST endpoint contract** | `POST /capture` body: `{"member_name": str, "task_id": str, "location": str, "completion_date": str (YYYY-MM-DD), "source": "form"}`. Response: `{"status": "ok", "message": "Logged!"}` or HTTP error with message. |
| **Completions write spec** | Write to `completions` sheet immediately on POST (TC-2). Fields: `member_name`, `task_id`, `completion_date`, `source`. Also update `last_date` in `tasks` sheet for the completed task. |
| **`#shop-log` confirmation schema** | `✅ Task logged\nMember: @<name>\nTask: <task_id> — <task_name>\nDate: <date>\nMethod: QR form` (TC-3) |
| **OCR fallback spec** *(if Method 1 retained)* | Admin posts photo to `#shop-admin`. Bot sends image to `claude-sonnet-4-6` vision API with extraction prompt. Writes records with `source=OCR`. Partial or illegible fields stored as `UNKNOWN` placeholder (not dropped) to maintain M3 data completeness rate (§9 M3). |

### Implementation

1. Mobile web form: fetch task list from `tasks` sheet by location; render task selector; POST on submit
2. POST handler: validate fields (TC-1), write to `completions` sheet immediately (TC-2), update `last_date` in `tasks` sheet
3. `#shop-log` confirmation message (TC-3) and `#shop-alerts` notification (TC-4)
4. QR code generation per location, encoding `GET /form?location=<location_id>` URL (Method 3)
5. OCR handler *(if Method 1 selected)*: `#shop-admin` photo upload → Claude vision API → extraction prompt → Sheets write with `source=OCR`; partial records stored with `UNKNOWN` placeholders

### Exit Criteria

- QR scan → form load → task select → Submit → `completions` sheet write completes in ≤2 taps (TC-5)
- No login or account required at any step (TC-6)
- `completions` sheet updated immediately on submit, not batched (TC-2)
- `#shop-log` confirmation and `#shop-alerts` notification firing on every capture event (TC-3, TC-4)
- Every completion record includes all TC-1 fields: member_name, task_id, completion_date, source
- OCR flow *(if implemented)*: extracts ≥90% of fields under real shop conditions; partial records stored with `UNKNOWN` placeholder, not discarded

---

## Phase 6: Task Reporting Pipeline

*Natural language queries and automated scheduled reports, powered by Claude and APScheduler.*

**Requirements: TR-1 through TR-7 (§5.4)**

**Depends on:** All previous phases (needs live task data, completion records, and member registry)

### Specification

| Artifact | Contents |
|---|---|
| **Claude NL query prompt** | System prompt for `claude-sonnet-4-6`: role as Shop Sergeant bot, available data sources (tasks/completions/members sheets), query patterns (open tasks, member history, location status, compliance). Tool/function call definitions for Sheets reads. |
| **Report type specs** | **Member report**: tasks completed by member in current month, compliance status (≥2 hrs). **Location report**: task completion status, overdue tasks, days since last completion. **Shop report**: aggregate compliance %, top contributors by task count, overdue task count by location. **Compliance report** *(restricted to Shop Steward+)*: which members have/have not met 2hr/month requirement (§7.3). |
| **APScheduler job schedule** | Weekly (e.g., Mondays): error/availability report → `#shop-bulletin` (TR-7). Monthly (1st of month): compliance summary → `#shop-bulletin` (TR-5). Monthly (1st): top-contributors report → `#shop-bulletin` (TR-6). Daily: overdue task check — compare `last_date + frequency_window` to today for every active task. |
| **KPI data contracts** | M1 (compliance rate): `completions` distinct members / `members` active count. M2 (task completion rate): `tasks` frequency windows vs. `completions` last_date. M3 (data completeness): null-check on required `completions` fields. O1 (steward adoption): distinct steward users in audit log. O3 (overdue alert rate): APScheduler must log each alert event with `task_id` to `#shop-alerts` for numerator tracking. |
| **Suspend/restore spec** | `suspend <location\|area\|shop> [all\|<action>]` → bot rejects affected actions and posts notice to `#shop-alerts`. `restore <location\|area\|shop>` → re-enables. Steward: own location only. Shop Steward: any location/area. Shop Sergeant: shop-wide (§7.1). |

### Implementation

1. `#shop-queries` NL handler: Slack message event → Claude API with system prompt and Sheets data → formatted response inline in channel (TR-1, TR-3)
2. Report generators: `member_report()`, `location_report()`, `shop_report()`, `compliance_report()` — each queries Sheets and returns a formatted Slack message
3. Permission enforcement: compliance report rejected for Member and Steward roles (§7.3)
4. `#shop-alerts` notification on every report generation event (TR-4)
5. APScheduler integration: weekly error/availability post to `#shop-bulletin` (TR-7); monthly compliance summary (TR-5) and top-contributors (TR-6) posts
6. Overdue alert job: daily Sheets query → compare `last_date + frequency_window` to today → post overdue list to `#shop-bulletin`; log each alert with `task_id` to `#shop-alerts` for O3 KPI
7. Suspend/restore command handlers with scope enforcement (location / area / shop)
8. KPI query functions for M1–M3 and O1–O4 callable on-demand via `#shop-admin`

### Exit Criteria

- NL query in `#shop-queries` returns correct, formatted data from Sheets (TR-1)
- All 4 report types (Member, Location, Shop, Compliance) generating correct output (TR-2, TR-3)
- Compliance report rejected when requested by Member or Steward role
- `#shop-alerts` notified on every report generation (TR-4)
- Scheduled posts firing on correct cadence: weekly (TR-7), monthly summary (TR-5), monthly top-contributors (TR-6)
- Overdue alert job detects all overdue tasks and logs each alert event with `task_id` to audit log (O3)
- Suspend/restore enforcing correct role scoping at location, area, and shop levels
- KPI functions return correct values for M1, M2, M3, O1, O2, O3, O4 from test data

---

## Unresolved Questions

1. Is Method 3 confirmed as the sole capture method, or is OCR (Method 1) kept as a fallback? If kept, is it admin-initiated only (manual photo upload to `#shop-admin`) or does it also trigger automatically?
2. Is the `members` sheet added in Phase 3, or deferred until compliance reporting (Phase 6) becomes an active need?
3. Should per-task `time` estimates (integer minutes; default 15) be added to the `tasks` schema in Phase 3, while the data model is still being designed, to enable hour-based compliance calculation?
4. Is the mobile web form served from the same Python process as the Slack bot, or a separate lightweight service?
5. Does the Phase 0 QR trial indicate whether a PWA (service worker, offline support, home-screen shortcut) is warranted over a plain mobile web page?
