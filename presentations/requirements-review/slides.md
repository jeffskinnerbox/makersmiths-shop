---
theme: default
addons:
  - excalidraw
title: "Shop Sergeant — Requirements Review"
titleTemplate: "%s — Slidev"
aspectRatio: 16/9
canvasWidth: 980
drawings:
  enabled: true
  persist: false
---

# Shop Sergeant

**System Requirements Review**

Makersmiths Leesburg · April 2026 · Jeff Irland

<!--
Opening: Thank you for coming. This review covers the requirements for Shop Sergeant —
the automated task-tracking system proposed to replace our paper-only volunteer process.
We'll walk through the problem, the solution architecture, and what we need to build.
-->

---
layout: two-cols-header
---

# Agenda

::left::

**1. Problem Statement**
Why the current process is broken

**2. System Overview**
4 pipelines · actors · tech stack

**3. Functional Requirements**
* Task Database Pipeline
* Task Sheet Pipeline
* Task Capture Pipeline
* Task Reporting Pipeline

::right::

**4. Design Details**
* Physical sign-up sheet format
* Slack bot capabilities
* Permission model

**5. Quality & Operations**
* Non-functional requirements
* Success criteria (KPIs)

**6. Current State & Next Steps**
* Phase 0 complete
* What we're testing next

---
layout: section
---

# The Problem

---

# Why We Need This

Current paper-only process has **5 critical gaps:**

<v-clicks>

* **Incomplete records** — Members rarely write their name and date after completing a task. No reliable record of who did what or when.

* **No cumulative history** — Sign-up sheets are discarded when replaced. No historical data for 501(c)(3) compliance.

* **No steward monitoring** — Stewards can't see which tasks are overdue or consistently missed. Problems surface only when something breaks.

* **No scheduling** — Periodic tasks (weekly, monthly) have no mechanism to track whether they were done on time.

* **No recognition** — Top contributors go unidentified because records don't exist. No way to thank members who go above and beyond.

</v-clicks>

<!--
Each problem drives specific requirements. The 2-tap goal comes from problem 1 (if it's hard, members won't do it).
The Google Sheets persistence comes from problem 2. Steward alerts come from problems 3 and 4.
-->

---
layout: section
---

# System Overview

---
layout: center
---

# Pipeline Overview

<Excalidraw filePath="./diagrams/pipeline-overview.excalidraw" />

<!--
4 pipelines form a closed loop.
Google Sheets is the single source of truth — if the bot goes down, no data is lost.
Slack is the primary UI for both members and administrators.
Each pipeline has distinct triggers, actors, and outputs.
Agentic Workers (the Slack bot) mediates all pipelines.
-->

---

# Actors

<div class="grid grid-cols-2 gap-8">
<div>

### Human Actors · Ellipse Shape

| Actor | Role Summary |
|-------|-------------|
| **Member** | Completes tasks; logs completions; queries own history |
| **Steward** | Manages tasks for their location; generates sheets |
| **Shop Steward** | Oversees entire shop; escalates issues |
| **Shop Sergeant** | Manages the process; monitors KPIs; full access |

</div>
<div>

### System Actors · Rectangle Shape

| Actor | Role Summary |
|-------|-------------|
| **Physical Sign-Up Sheet** | Shop-floor touchpoint — 8.5×11" landscape |
| **QR Code** | Encodes mobile web form URL; triggers digital logging |
| **Mobile Phone** | Member's personal device — no app required |
| **Mobile Web Form** | ≤ 2-tap completion UI, opened via QR scan |
| **Slack** | Primary interface — all notifications and commands |
| **Google Sheets** | **Single source of truth** for all data |
| **Claude AI Model** | OCR (vision API) + natural language query processing |
| **APScheduler** | Time-based automation — reminders, scheduled reports |
| **Agentic Workers** | Python Slack bot — mediates all 4 pipelines |

</div>
</div>

<!--
4 human actors, 9 system actors = 13 total.
Key distinction: human actors use ellipses in diagrams; system actors use rectangles.
Each has a unique color in the pipeline diagrams.
-->

---
layout: section
---

# Functional Requirements

---
layout: center
---

# Task Database Pipeline

<Excalidraw filePath="./diagrams/task-database-pipeline.excalidraw" />

<!--
Two input paths: Slack command (interactive) or YAML bulk-load (CLI).
Both go through Agentic Workers which validates Task IDs and rejects duplicates.
All changes written to the tasks sheet in Google Sheets.
Every modification triggers a #shop-alerts notification for auditability.
-->

---
layout: two-cols
---

# Task Database — Details

**Who can modify the task catalog?**
* **Steward** — own location only
* **Shop Steward** — all locations
* **Shop Sergeant** — all locations + system config

**Task ID format:** `SHOP-LOCATION-NNN`
e.g., `MSL-METAL-003` = Metalshop task #3

**Every task requires:** unique Task ID, name, frequency, location

**Validation rules:**
* Reject duplicate Task IDs
* Reject duplicate task names within same location

::right::

**Key Requirements**

| # | Requirement |
|---|-------------|
| DB-1 | Google Sheets = single source of truth |
| DB-2 | YAML bulk-load via CLI script |
| DB-3 | Add / update / delete via Slack in `#shop-admin` |
| DB-4 | Only Steward (own location), Shop Steward, Sergeant |
| DB-5 | Task ID + name + frequency + location required |
| DB-6 | Reject duplicate IDs and names within location |
| DB-7 | Every change notifies `#shop-alerts` |

---
layout: center
---

# Task Sheet Pipeline

<Excalidraw filePath="./diagrams/task-sheet-pipeline.excalidraw" />

<!--
Two triggers: on-demand Slack command or periodic APScheduler reminder.
Reads the task catalog from Google Sheets.
Renders PDF using Jinja2 + wkhtmltopdf with embedded QR code.
Notifies both #shop-bulletin (new sheet ready) and #shop-alerts (audit).
Physical sheet is printed and posted in the shop.
-->

---
layout: two-cols
---

# Physical Sign-Up Sheet Format

**Specification:**
* 8.5 × 11" landscape orientation
* One sheet per location
* Legible in black and white
* Makersmiths logo in header

**Required columns:**

| Column | Content |
|--------|---------|
| Task Name | Human-readable description |
| Frequency | Weekly, Monthly, Quarterly, etc. |
| Supervisor Required | Yes / No |
| Completion Date | Blank — member writes by hand |
| Member Name | Blank — member writes by hand |
| QR Code | Single code in page header (Method 3) |

::right::

**Task Display Rules**
* Tasks grouped by location
* TBD / empty tasks silently omitted
* Ordered by frequency (most frequent first)

**Key Requirements**

| # | Requirement |
|---|-------------|
| TS-1 | Generate for single location or all locations |
| TS-2 | Authorized roles only (Steward = own location) |
| TS-3 | Via Slack command or CLI |
| TS-4 | `#shop-bulletin` notified when sheet is ready |
| TS-5 | `#shop-alerts` notified each generation |
| TS-6 | Bot reminds stewards when task changes make a refresh advisable |

---
layout: center
---

# Task Capture Pipeline

<Excalidraw filePath="./diagrams/task-capture-pipeline.excalidraw" />

<!--
Two very different flows.
Path A (Method 3 — likely): Zero-install, zero-login. Member scans QR with phone camera,
browser opens mobile web form, selects task, taps Submit. 2 taps total.
Path B (Method 1 — fallback): Admin photos the completed paper sheet, posts to #shop-admin.
Claude vision API extracts names, task IDs, and dates. Records written with source=OCR.
Both paths converge on Agentic Workers → Google Sheets completions sheet.
-->

---
layout: two-cols
---

# Task Capture — Capture Methods

**Method 3 (Likely Selection) — QR → Mobile Web Form**

1. Member scans QR code on sign-up sheet with phone camera
2. Browser opens mobile web form automatically (no app, no login)
3. Member selects task + taps Submit **(≤ 2 taps total)**
4. Agentic Workers writes completion record to Google Sheets
5. Confirmation posted to `#shop-log`

**Method 1 (Fallback / Recovery) — OCR**

1. Steward or admin photos the completed paper sheet
2. Posts image to `#shop-admin`
3. Claude vision API extracts names, task IDs, dates
4. Records written to Sheets with `source=OCR`

::right::

**Key Requirements**

| # | Requirement |
|---|-------------|
| TC-1 | Record: name + Task ID + date + capture method |
| TC-2 | Written to Google Sheets immediately |
| TC-3 | Confirmation message in `#shop-log` |
| TC-4 | `#shop-alerts` notified on each capture event |
| TC-5 | **≤ 2 taps** from QR scan to confirmation (Method 3) |
| TC-6 | No account, no login, no app required |

**Phase 0 Trial Objective**

Test ease of use with actual stewards and members. Will users know how to scan? How error-prone is the flow? Do we need a different capture method?

---
layout: center
---

# Task Reporting Pipeline

<Excalidraw filePath="./diagrams/task-reporting-pipeline.excalidraw" />

<!--
Path A: Any actor sends a plain-English question to #shop-queries or #shop-admin.
Agentic Workers passes it to Claude AI for NL processing, queries Google Sheets, returns inline report.
Path B: APScheduler fires weekly/monthly jobs that auto-generate and post scheduled reports.
Output channels differ by report type and access level.
-->

---
layout: two-cols
---

# Task Reporting — Report Types

**On-Demand Reports (via Slack NL query)**

| Report | Description | Access |
|--------|-------------|--------|
| **Member** | Tasks completed; compliance status | Own: any member; Other: Steward+ |
| **Location** | Task status; overdue tasks | All Members (public) |
| **Shop** | Aggregate; top contributors | All Members (public) |
| **Compliance** | Who met 2hr/month requirement | Shop Steward + Sergeant only |

**Scheduled Reports (via APScheduler)**
* **Weekly** → `#shop-bulletin`: errors logged, availability across locations
* **Monthly** → `#shop-bulletin`: compliance summary
* **Monthly** → `#shop-bulletin`: top-contributor recognition post

::right::

**Slack Channel Structure**

| Channel | Access | Purpose |
|---------|--------|---------|
| `#shop-log` | All (read) | Completion confirmations |
| `#shop-bulletin` | All (read) | Announcements + scheduled reports |
| `#shop-queries` | All | NL queries — public data |
| `#shop-admin` 🔒 | Stewards+ | Admin commands; restricted reports |
| `#shop-alerts` 🔒 | Sgt only | Full audit trail + bot errors |

---
layout: section
---

# Design Details

---

# Permission Model

<div class="text-sm">

| Action | Member | Steward | Shop Steward | Shop Sergeant | Channel |
|--------|:------:|:-------:|:------------:|:-------------:|---------|
| Log task completion (QR / form) | ✅ | ✅ | ✅ | ✅ | `#shop-log` |
| Query own task history | ✅ | ✅ | ✅ | ✅ | `#shop-queries` |
| Query any member's task history | ❌ | ❌ | ✅ | ✅ | `#shop-admin` |
| Query open tasks / location status | ✅ | ✅ | ✅ | ✅ | `#shop-queries` |
| Add / update / delete a task | ❌ | ✅ own | ✅ | ✅ | `#shop-admin` |
| Generate / print sign-up sheet | ❌ | ✅ own | ✅ | ✅ | `#shop-admin` |
| Upload OCR photo for processing | ❌ | ✅ | ✅ | ✅ | `#shop-admin` |
| Request location or shop report | ✅ public | ✅ | ✅ | ✅ | `#shop-queries` |
| Trigger overdue reminder blast | ❌ | ❌ | ✅ | ✅ | `#shop-admin` |
| View bot errors / audit log | ❌ | ❌ | ✅ | ✅ | `#shop-alerts` |
| Suspend / restore — location scope | ❌ | ✅ | ✅ | ✅ | `#shop-admin` |
| Suspend / restore — shop scope | ❌ | ❌ | ❌ | ✅ | `#shop-admin` |

</div>

> **Note:** Steward permissions are scoped to their own location. Stewards CAN suspend/restore their location (for safety incidents) but CANNOT query other members' history.

<!--
Worth discussing: should Stewards be able to trigger overdue reminders for their own location?
Currently they cannot, which might frustrate a steward who sees a task overdue and wants to nudge members.
-->

---

# Agentic AI Capabilities (Claude API)

The bot uses `claude-sonnet-4-6` for two distinct capabilities:

<div class="grid grid-cols-2 gap-8">
<div>

**Natural Language Query Processing**

Members and stewards ask questions in plain English:

> "What tasks are still open in the metalshop?"

> "How many tasks has @alex done this month?"

> "Give me a status report on the laser cutter area"

Claude parses the intent, constructs the appropriate Google Sheets query, and formats the response.

</div>
<div>

**OCR Photo Processing (Vision API)**

Admin posts a photo of a completed sign-up sheet to `#shop-admin`:

1. Claude vision API processes the image
2. Extracts member names, Task IDs, completion dates
3. Handles illegible handwriting gracefully (writes `UNKNOWN` placeholder)
4. Records written to Sheets with `source=OCR`

**Note:** OCR accuracy depends on handwriting legibility and photo quality — real-world testing needed.

</div>
</div>

---
layout: section
---

# Quality & Operations

---
layout: two-cols
---

# Non-Functional Requirements

**Member Experience (Core Principle)**
* ≤ 2 taps from QR scan to confirmation
* No account, no login, no app required
* Paper fallback **always** available alongside digital

**Record Retention**
* Completion records retained **indefinitely**
* Export in CSV/Excel for 501(c)(3) compliance documentation
* Every record: member name + Task ID + date + capture method

**Availability & Resilience**
* Google Sheets is durable — bot outage causes zero data loss
* Physical sign-up sheet is the manual fallback
* OCR enables data recovery from completed paper sheets

::right::

**Access Control**
* Slack channel membership is the primary access control
* No separate authentication system needed
* Bot verifies actor role before executing restricted actions

**Multi-Shop Extensibility**
* Data model supports multiple shops from the start (MSL, MSP)
* All Task IDs shop-prefixed: `MSL-`, `MSP-`
* Initial release: MSL only
* Adding MSP must require **no architectural changes**

**Technology Stack**
* Python 3.11+ · Slack Bolt framework
* Google Sheets API v4 · Claude API (`claude-sonnet-4-6`)
* Jinja2 + wkhtmltopdf · `qrcode[pil]`
* APScheduler · pytest

---

# Success Criteria (KPIs)

<div class="grid grid-cols-2 gap-8">
<div>

**Member-Facing Metrics**

| ID | Metric | Target |
|----|--------|--------|
| **M1** | Member Compliance Rate | ≥ 50% monthly |
| **M2** | Task Completion Rate | ≥ 90% |
| **M3** | Data Completeness Rate | ≥ 95% |

*M1 formula:* unique members with ≥ 1 completion / total active members

*M2 formula:* tasks completed within their frequency window / total active tasks

*M3 formula:* records with all 3 required fields / total records

**⚠ Data Gap:** No member registry exists yet. Needed for M1 and O1 denominators. **Recommendation:** Add a `members` sheet to Google Sheets with `role` column.

</div>
<div>

**Operational Metrics**

| ID | Metric | Target |
|----|--------|--------|
| **O1** | Steward Adoption Rate | 100% within 60 days |
| **O2** | Sheet Refresh Latency | ≤ 24 hours |
| **O3** | Overdue Task Alert Rate | 100% |
| **O4** | Top Contributor Recognition | 100% monthly |

*O2 note:* Measurable portion = Slack cmd → PDF ready. Physical posting to wall is outside system boundary.

*O3 note:* Bot must log each overdue reminder to audit log with `task_id` + `alert_timestamp` — not currently stated as a requirement. Should be added to TR requirements.

</div>
</div>

---
layout: two-cols
---

# Out of Scope

**Not in this release:**

* Makersmiths Purcellville (MSP)
  * Architecture must accommodate, but no deployment planned
* Capture methods not selected
  * Once trial picks Method 3 or 1, others retired
* Email / SMS notifications
  * Slack only
* Native mobile app
  * Zero-install web form is sufficient
* Real-time dashboards
  * On-demand NL queries cover real-time needs

::right::

# Current State (Phase 0)

**Complete and passing tests:**
* `scripts/signup-sheet.py` — renders HTML sign-up sheet from YAML
* `scripts/signup-sheet2.py` — v2 with single header QR code
* `scripts/generate-signup-sheet-template.py` — Jinja2 template generator
* `scripts/yaml-to-sheets.py` — YAML → Excel for Google Sheets import
* All tests passing with pytest

**Phase 0 Prototyping Next:**

1. **Sign-up sheet format trial** (in progress) — test with stewards/members
2. **QR → mobile web form usability test** — will users know how to scan?
3. **Optional: OCR proof-of-concept** — photo a completed sheet → Claude vision → validate accuracy

---

# Open Questions

Before implementation begins, these deserve deliberate discussion:

<v-clicks>

* **Should Methods 1 and 2 be formally retired?** Phase 0 trial may confirm Method 3 works well — if so, remove methods 1+2 from scope to avoid design debt and ambiguity for developers.

* **Is the permission model too open or too tight?** Stewards can suspend their location (reasonable for emergencies) but can't trigger overdue reminders (may frustrate stewards who notice overdue tasks). Both edges worth discussing with actual stewards before implementation.

* **Should task duration be tracked?** The 2hr/month requirement is tracked by task COUNT not actual hours. Adding an estimated `time` field per task enables true compliance checking. Better to add now while the schema is still being designed.

* **APScheduler or Claude Routines for scheduling?** APScheduler runs in-process and is simple to test. Claude Routines are managed/cloud-scheduled — eliminates "missed job on restart" failures but adds per-run token cost and variable latency. A hybrid is possible.

* **Should the paper fallback have a planned sunset?** If Method 3 proves reliable and shop Wi-Fi is consistently available, the permanent paper fallback may add complexity (OCR, hand-entry columns) without sufficient benefit.

</v-clicks>

---
layout: center
---

# Questions?

**Jeff Irland**

📧 <jeff.irland@gmail.com> · 💬 Slack: jeff.irland

*Source: github.com/jeffskinnerbox/makersmiths-shop*

<!--
Thank you for attending. Happy to discuss any of the open questions or requirements
in more detail. The full requirements document is available on GitHub.
-->
