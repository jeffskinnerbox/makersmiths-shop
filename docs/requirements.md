# Shop Sergeant — System Requirements

**Project:** Shop Sergeant
**Organization:** Makersmiths Makerspace
**Scope:** Makersmiths Leesburg (MSL) — initial release
**Status:** Phase 0 complete; Phases 1–4 planned
**Audience:** All stakeholders — members, stewards, shop stewards, shop sergeant, and developers

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Glossary](#2-glossary)
3. [Problem Statement](#3-problem-statement)
4. [System Overview](#4-system-overview)
5. [Functional Requirements](#5-functional-requirements)
6. [Physical Sign-Up Sheet Requirements](#6-physical-sign-up-sheet-requirements)
7. [Agentic AI and Slack Bot Requirements](#7-agentic-ai-and-slack-bot-requirements)
8. [Non-Functional Requirements](#8-non-functional-requirements)
9. [Success Criteria (KPIs)](#9-success-criteria-kpis)
10. [Out of Scope](#10-out-of-scope)

---

## 1. Introduction

### 1.1 Purpose and Scope

This document defines the requirements for **Shop Sergeant**, an automated volunteer task tracking system for the Makersmiths makerspace. It is written for all stakeholders — members and stewards who will use the system, and developers who will build it.

This document is the starting point for the design process. It is followed by:
- `docs/specifications.md` — detailed system design, data flows, API contracts, and database schema
- `docs/implementation-plan.md` — phased development plan with file maps and code structure

**Scope:** This initial release targets **Makersmiths Leesburg (MSL)** only. Extension to Makersmiths Purcellville (MSP) is a future milestone and is explicitly out of scope here. The system architecture must, however, support multi-shop expansion without structural changes.

### 1.2 Project Background

All Makersmiths members are required to volunteer **2 hours per month** to help maintain, operate, and improve the makerspace. Today, this requirement is tracked entirely on paper: handwritten sign-up sheets are posted around the shop, members write their name and date when they complete a task, and the sheets are periodically replaced.

This paper-only process has significant gaps — completion records are often missing or illegible, there is no cumulative history, stewards have no visibility into whether their area's tasks are getting done, and members who regularly contribute go unrecognized.

**Shop Sergeant** replaces the manual bookkeeping with an automated system centered on **Slack** and **Google Sheets**, while keeping the physical sign-up sheet as the primary touchpoint for members on the shop floor.

---

## 2. Glossary

### 2.1 Physical Spaces

| Term | Definition | MSL Example |
|---|---|---|
| **Shop** | A physical location where Makersmiths operates. Each shop is independently managed. | Makersmiths Leesburg (MSL) |
| **Area** | A major subdivision of a shop — typically a floor, wing, or building section. | Main Floor, Exterior |
| **Location** | A specific craft or functional space within an area. Locations are the unit at which tasks and sign-up sheets are organized. | Metalshop, Laser Cutter, Wood Shop, Bathrooms |

### 2.2 Actors

| Actor | Who They Are | Key Responsibilities | System Access |
|---|---|---|---|
| **Member** | Any active Makersmiths member | Complete volunteer tasks; log completions | Log own tasks; query own history; view open tasks and public reports |
| **Steward** | A member responsible for a specific location | Define tasks for their location; monitor task completion; train members | All member actions + task add/update/delete (own location); generate sign-up sheets (own location); upload OCR photos |
| **Shop Steward** | A member who oversees the entire shop | Monitor all areas; coordinate stewards; escalate issues | All steward actions + shop-wide access; trigger reminder blasts |
| **Shop Sergeant** | A member who manages the task volunteering process itself | Ensure the process runs smoothly; monitor KPIs; maintain the system | All shop steward actions + bot error log; audit trail; full system configuration |

### 2.3 System Terms

| Term | Definition |
|---|---|
| **Task** | A discrete unit of volunteer work. Each task has a name, frequency, purpose, and instructions. |
| **Task ID** | A unique identifier for a task, formatted as `SHOP-LOCATION-NNN` (e.g., `MSL-METAL-003`). Used in all system references. |
| **Sign-Up Sheet** | A printed 8.5×11" landscape sheet listing tasks for a single location. Members write their name and date, or scan a QR code, to record completions. |
| **QR Code** | A scannable code printed on the sign-up sheet. Scanning it opens a mobile form where the member records a task completion. |
| **Pipeline** | One of four end-to-end workflows in the system: Task Database, Task Sheet, Task Capture, and Task Reporting. |
| **Source of Truth** | **Google Sheets** — all task definitions, completion records, and history live here. All other system components read from and write to Google Sheets. |
| **Capture Method** | The mechanism by which a member records a completed task. Three methods are under consideration; one will be selected for implementation. |
| **OCR** | Optical Character Recognition — the process of extracting text from a photo of a completed sign-up sheet using the Claude vision API. |

---

## 3. Problem Statement

The current paper-only task volunteering process has five significant weaknesses:

### 3.1 Incomplete Completion Records

**Problem:** After completing a task, members frequently do not write their name, the date, or even confirm the task as done on the sign-up sheet.

**Impact:** There is little to no reliable record of who did what or when. The data needed for compliance, recognition, and process improvement simply does not exist.

**Requirement:** The system must make recording a completion so fast and easy (target: ≤ 2 taps on a mobile device) that members do it consistently.

### 3.2 No Cumulative Record-Keeping

**Problem:** When sign-up sheets are replaced, all prior completion data is discarded. No historical record is maintained.

**Impact:** Makersmiths holds 501(c)(3) tax-exempt status, which may require documentation of volunteer labor. Without cumulative records, the organization cannot demonstrate member contributions over time.

**Requirement:** All completion records must be stored permanently in Google Sheets. Records must include member name, task ID, date, and capture method used.

### 3.3 Stewards Have No Monitoring Tools

**Problem:** Stewards are responsible for their location's tasks but have no way to see which tasks are overdue, which are being completed regularly, or which are being ignored.

**Impact:** Problems in a location are only discovered when something breaks or a safety issue arises — not proactively.

**Requirement:** Stewards must be able to query task status for their location at any time via Slack. The system must automatically alert stewards when tasks are overdue.

### 3.4 Periodic Tasks Have No Scheduling

**Problem:** Some tasks must be performed on a regular schedule (weekly, monthly, quarterly) but there is no mechanism to track whether they have been done on time.

**Impact:** Periodic maintenance gets forgotten. Equipment degrades. Safety risks accumulate.

**Requirement:** Tasks must have an associated frequency. The system must track last-completion dates and generate alerts when periodic tasks are overdue.

### 3.5 Top Contributors Go Unrecognized

**Problem:** Members who consistently go above and beyond their 2-hour requirement are not identified or thanked, because no records exist.

**Impact:** Highly engaged members receive no recognition. This reduces motivation and community goodwill.

**Requirement:** The system must generate periodic reports identifying top contributors so the shop sergeant and stewards can recognize them.

---

## 4. System Overview

### 4.1 Architecture Summary

Shop Sergeant is built around four pipelines, each handling a distinct part of the volunteer task workflow:

| Pipeline | What It Does |
|---|---|
| **Task Database** | Maintains the master list of all tasks in Google Sheets; supports add, update, and delete |
| **Task Sheet** | Generates printable sign-up sheets from the task database and posts them around the shop |
| **Task Capture** | Records task completions from members via QR code scan or OCR photo scan |
| **Task Reporting** | Generates reports on task completion, member participation, and location health |

**Google Sheets** is the system's single source of truth. All pipelines read from and write to it. **Slack** is the primary user interface for both members and administrators. Physical sign-up sheets serve as the member-facing touchpoint on the shop floor.

> *[Excalidraw diagram: end-to-end pipeline overview — four pipelines flowing through Google Sheets, with Slack as the interface layer and sign-up sheets as the physical touchpoint]*

### 4.2 Technology Stack

| Component | Technology | Role |
|---|---|---|
| Bot framework | Python 3.11+ with Slack Bolt | Listens to Slack events; dispatches commands to the appropriate pipeline |
| AI agent | Claude API (`claude-sonnet-4-6`) | Natural language query handling; OCR photo processing via vision API |
| Data store | Google Sheets API v4 | Authoritative storage for all tasks and completion records |
| Sheet generation | Jinja2 + wkhtmltopdf | Renders HTML sign-up sheet templates to PDF for printing |
| QR codes | `qrcode[pil]` Python library | Generates QR codes embedded in sign-up sheets |
| Scheduling | APScheduler | Sends recurring reminders; monitors overdue periodic tasks |
| Testing | pytest | Unit and integration tests for all pipeline components |

### 4.3 Current State (Phase 0 — Complete)

Phase 0 implemented the **Task Sheet Pipeline** tooling:

- `scripts/signup-sheet.py` — CLI tool that renders a sign-up sheet HTML from a YAML task file
- `scripts/generate-signup-sheet-template.py` — generates the reusable Jinja2 HTML template
- `scripts/yaml-to-sheets.py` — converts YAML task definitions to Excel for Google Sheets import
- `scripts/parse-tasks.py` and `parse-opp-tasks.py` — YAML to Markdown converters for review

All Phase 0 scripts have passing automated tests. The system is ready for trial with stewards and members. No Slack bot or Google Sheets integration exists yet.

---

## 5. Functional Requirements

### 5.1 Task Database Pipeline

**Purpose:** Maintain the authoritative catalog of all volunteer tasks in Google Sheets.

> *[Excalidraw diagram: YAML input → Python scripts → Google Sheets; Slack commands → bot → Google Sheets; change events → #shop-alerts]*

**Inputs:** YAML task definition files; Slack commands in `#shop-admin`

**Outputs:** Updated Google Sheets task catalog; Slack notifications in `#shop-alerts`

**Requirements:**

| # | Requirement |
|---|---|
| DB-1 | Google Sheets is the single source of truth for all task definitions and completion records |
| DB-2 | Task definitions may be bulk-loaded from YAML files using provided scripts |
| DB-3 | Individual tasks may be added, updated, or deleted via Slack commands in `#shop-admin` |
| DB-4 | Only stewards (for their own location), shop stewards, and the shop sergeant may modify tasks |
| DB-5 | Every task must have a unique Task ID (`SHOP-LOCATION-NNN`), a name, a frequency, and a location |
| DB-6 | The system must reject duplicate Task IDs and duplicate task names within the same location |
| DB-7 | Every modification to the task catalog must trigger a notification in `#shop-alerts` |

### 5.2 Task Sheet Pipeline

**Purpose:** Generate printable sign-up sheets from the task database and notify stewards when new sheets are needed.

> *[Excalidraw diagram: Google Sheets → YAML export → Jinja2 template → HTML → PDF → print; #shop-admin command triggers generation; #shop-bulletin notified]*

**Inputs:** Task YAML files (exported from Sheets); Slack commands in `#shop-admin`; optional logo and custom reference doc

**Outputs:** PDF sign-up sheets ready for printing; Slack notifications in `#shop-bulletin` and `#shop-alerts`

**Requirements:**

| # | Requirement |
|---|---|
| TS-1 | The system must generate a sign-up sheet for any single location or all locations in a shop |
| TS-2 | Only stewards (own location), shop stewards, and the shop sergeant may generate sign-up sheets |
| TS-3 | Sheets must be generated via Slack command in `#shop-admin` or via CLI script |
| TS-4 | `#shop-bulletin` must be notified when new sheets are ready for printing |
| TS-5 | `#shop-alerts` must be notified each time a sheet is generated |
| TS-6 | The Slack bot must periodically remind stewards and the shop steward when task changes make a sheet refresh advisable |

### 5.3 Task Capture Pipeline

**Purpose:** Record task completions from members via mobile device, with minimum friction.

> *[Excalidraw diagram: member scans QR on sign-up sheet → mobile form or Slack prefill → bot writes to Google Sheets → confirmation in #volunteer-log]*

**Inputs:** QR code scan from member's mobile device; OCR photo posted by admin to `#shop-admin`

**Outputs:** Completion record written to Google Sheets; confirmation message in `#volunteer-log`; notification in `#shop-alerts`

Three capture methods are under consideration. One will be selected for implementation based on a trial with stewards and members.

| Method | Description | Status |
|---|---|---|
| **Method 1 — OCR** | Admin photographs a completed sign-up sheet and posts it to `#shop-admin`. Claude vision extracts member names, task IDs, and dates. Bot writes records to Google Sheets with `source=OCR`. | Alternative |
| **Method 2 — Per-Task QR** | Each task row has its own QR code. Scanning it pre-fills a Slack message `task-done <task_id>`. Sending the message logs the completion. | Alternative |
| **Method 3 — Single-Sheet QR** | A single QR code appears on each sign-up sheet. Scanning opens a mobile web form where the member selects their name, the task completed, and confirms. The form posts to the bot, which logs to Sheets. | **Likely selection** |

**Requirements (all methods):**

| # | Requirement |
|---|---|
| TC-1 | Every completion record must include: member name, Task ID, completion date, and capture method (`QR`, `OCR`, or `form`) |
| TC-2 | Completion records must be written to Google Sheets immediately upon submission |
| TC-3 | A confirmation message must appear in `#volunteer-log` for every logged completion |
| TC-4 | `#shop-alerts` must be notified whenever a capture event is processed |
| TC-5 | The capture flow must require ≤ 2 taps on a mobile device from QR scan to confirmation (Method 3) |
| TC-6 | The system must not require members to create an account or log in to record a completion |

### 5.4 Task Reporting Pipeline

**Purpose:** Generate reports on task completion, member participation, and location health, accessible via Slack.

> *[Excalidraw diagram: member or admin sends NL query in Slack → Claude agent reads Google Sheets → formatted report response in Slack]*

**Inputs:** Natural language queries in `#shop-queries` or `#shop-admin`; scheduled report triggers

**Outputs:** Inline Slack report responses; `#shop-alerts` notification on report generation

**Report types:**

| Report | Description | Access |
|---|---|---|
| **Member report** | Tasks completed by a specific member; compliance status | Member (own only), stewards+ (any member) |
| **Location report** | Task completion status for a specific location; overdue tasks | All members (public data) |
| **Shop report** | Aggregate compliance, overdue tasks, top contributors across all locations | All members (public data) |
| **Compliance report** | Which members have/have not met the 2hr/month requirement | Shop steward and shop sergeant only |

**Requirements:**

| # | Requirement |
|---|---|
| TR-1 | Members may request reports via natural language in `#shop-queries` (public data only) |
| TR-2 | Stewards and above may request any report type via `#shop-admin` |
| TR-3 | The bot must respond to report requests inline in Slack |
| TR-4 | `#shop-alerts` must be notified when any report is generated |
| TR-5 | A monthly summary report must be automatically posted to `#shop-bulletin` |
| TR-6 | A monthly top-contributors report must be automatically posted to `#shop-bulletin` |

---

## 6. Physical Sign-Up Sheet Requirements

The sign-up sheet is the primary member-facing touchpoint. Most members will interact with the system only through this physical sheet.

### 6.1 Format

| Property | Requirement |
|---|---|
| Paper size | 8.5×11 inches, landscape orientation |
| One sheet per location | Each location (e.g., Metalshop, Laser Cutter) gets its own sheet |
| Print compatibility | Must be legible when printed in black and white |
| Logo | Makersmiths logo in the sheet header |
| Header info | Location name, steward name, date generated |

### 6.2 Columns

Each task row on the sign-up sheet must include:

| Column | Content |
|---|---|
| Task Name | Human-readable task description |
| Frequency | How often the task should be done (e.g., Weekly, Monthly) |
| Supervisor Required | Y/N — whether a steward must be present |
| Completion Date | Blank — member writes the date by hand (fallback if QR not used) |
| Member Name | Blank — member writes their name by hand (fallback if QR not used) |
| QR Code | Scannable code for digital task logging |

### 6.3 Task Display Rules

- Tasks are grouped by location
- Tasks that are TBD or have no defined work are silently omitted from the sheet
- Task rows are ordered by frequency (most frequent first) within a location

### 6.4 QR Code Placement

The QR code placement depends on the capture method selected:

- **Method 2 (per-task QR):** One QR code per task row, in the rightmost column
- **Method 3 (single-sheet QR, likely):** One QR code in the sheet header or footer, covering the entire location

---

## 7. Agentic AI and Slack Bot Requirements

Shop Sergeant uses a **custom Slack bot** built with the Slack Bolt framework (Python) and the Claude API. This is distinct from Anthropic's "Claude in Slack" product — the custom bot can read from and write to Google Sheets, execute task management commands, and send structured notifications.

The Claude AI model powers two capabilities: **natural language query handling** (members and stewards ask questions in plain English) and **OCR processing** (extracting completion data from photos of sign-up sheets via the Claude vision API).

### 7.1 Slack Channel Structure

| Channel | Access | Who Posts | Purpose |
|---|---|---|---|
| `#volunteer-log` | All members (read), Bot (write) | Bot only | Task completion confirmations; one message per logged completion |
| `#shop-bulletin` | All members (read), Bot (write) | Bot only | Announcements: new sign-up sheets available, overdue reminders, monthly summaries, top contributors |
| `#shop-queries` | All members | Members + Bot | Natural language queries about tasks, member history, location status, and public reports |
| `#shop-admin` 🔒 | Stewards, shop steward, shop sergeant | Admins + Bot | Task add/update/delete, sign-up sheet generation, OCR photo uploads, restricted report requests, compliance queries |
| `#shop-alerts` 🔒 | Shop sergeant | Bot only | Bot errors, audit trail, system event log — every significant system action generates an entry here |

### 7.2 Permission Model

The following table defines what each actor may ask the bot to do, and where:

| Action | Member | Steward | Shop Steward | Shop Sergeant | Channel |
|---|---|---|---|---|---|
| Log task completion (QR/form) | x | ✅ | ✅ | ✅ | `#volunteer-log` |
| Query own task history | x | ✅ | ✅ | ✅ | `#shop-queries` |
| Query any member's task history |   |   | x | x | `#shop-admin` |
| Query open tasks / location status | x | ✅ | ✅ | ✅ | `#shop-queries` |
| Add / update / delete a task |   | x (own location) | x | x | `#shop-admin` |
| Generate / print sign-up sheet |   | x (own location) | x | x | `#shop-admin` |
| Upload OCR photo for processing | ❌ | ✅ | ✅ | ✅ | `#shop-admin` |
| Request location or shop report | x (public data) | x | x | x | `#shop-queries` / `#shop-admin` |
| Trigger overdue reminder blast |   | ❌ | x | x | `#shop-admin` |
| View bot errors / audit log |   | ❌ | x | x | `#shop-alerts` |

> **Note:** Steward permissions are scoped to their own location. A Metalshop steward cannot modify Laser Cutter tasks.

### 7.3 Agent Capabilities

The Claude-powered bot agent must be able to:

| Capability | Description |
|---|---|
| **Natural language query** | Parse plain-English questions from `#shop-queries` and respond with data from Google Sheets. Example: "What tasks are still open in the metalshop?" |
| **Task completion logging** | Accept completion events from QR/form submissions and write structured records to Google Sheets |
| **OCR processing** | Accept a photo of a completed sign-up sheet posted to `#shop-admin`, extract member names, task IDs, and dates using the Claude vision API, and write records to Google Sheets with `source=OCR` |
| **Task management** | Execute add, update, and delete operations on Google Sheets in response to Slack commands from authorized users |
| **Report generation** | Query Google Sheets and return formatted reports inline in Slack — member, location, shop, and compliance report types |
| **Scheduled reminders** | Use APScheduler to send periodic reminders to `#shop-bulletin`: overdue task alerts, monthly compliance summaries, top-contributor recognition |
| **Notification routing** | Route system event notifications to the correct channel (`#volunteer-log`, `#shop-bulletin`, or `#shop-alerts`) based on event type |

### 7.4 Example Interactions

The following examples illustrate how actors will interact with the Slack bot.

---

**Example 1: Member logs a completed task (Method 3 — single-sheet QR)**

> Member scans QR code on the Metalshop sign-up sheet. A mobile web form opens showing the Metalshop task list. Member taps "Clean and sweep metalshop floor" and taps "Submit."

Bot posts to `#volunteer-log`:

```
✅ Task logged
Member:  @alex_johnson
Task:    MSL-METAL-003 — Clean and sweep metalshop floor
Date:    2026-04-13
Method:  QR form
```

---

**Example 2: Member queries own task history**

In `#shop-queries`:
> **@alex_johnson:** How many tasks have I done this month?

> **@shop-sergeant-bot:** You've completed 3 tasks in April 2026:
> - Apr 2 — MSL-METAL-003 Clean and sweep metalshop floor
> - Apr 7 — MSL-LASER-002 Clean laser cutter bed and optics
> - Apr 11 — MSL-METAL-005 Check and top off cutting fluids
>
> You've met your 2-hour volunteer requirement for April.

---

**Example 3: Steward adds a task**

In `#shop-admin`:
> **@sarah_steward:** Add a new task to the metalshop — "Inspect welding equipment for damage", weekly, supervision required

> **@shop-sergeant-bot:** Task created:
> - ID: MSL-METAL-008
> - Name: Inspect welding equipment for damage
> - Location: Metalshop
> - Frequency: Weekly
> - Supervisor required: Yes
>
> Google Sheets updated. Generate a new sign-up sheet when ready: `sheet metalshop`

---

**Example 4: Shop sergeant requests monthly compliance report**

In `#shop-admin`:
> **@jeff_sergeant:** Give me the April compliance report

> **@shop-sergeant-bot:** **April 2026 — Member Compliance Report**
>
> 38 of 47 active members (81%) met the 2-hour volunteer requirement.
>
> | Status | Count |
> |---|---|
> | Compliant (≥ 2 hrs) | 38 |
> | Non-compliant (< 2 hrs) | 7 |
> | No activity recorded | 2 |
>
> Top contributors this month: @alex_johnson (5 tasks), @maria_w (4 tasks), @dave_m (4 tasks)
> Full report: [View in Google Sheets →]

---

**Example 5: Bot-initiated overdue task reminder**

Bot posts to `#shop-bulletin` (automated, weekly):

```
⚠️  Overdue Task Reminder — Metalshop

The following tasks are past due:

• MSL-METAL-001 — Inspect and clean bandsaw (Weekly — last done 18 days ago)
• MSL-METAL-006 — Replace worn grinding wheels (Monthly — last done 47 days ago)

Metalshop steward: @sarah_steward
Sign up to help: [Metalshop Sign-Up Sheet QR →]
```

---

## 8. Non-Functional Requirements

### 8.1 Frictionless Member Experience

The system's core design principle is **minimum friction for members**. Members must be able to record a task completion as easily and quickly as possible — the goal is to remove every barrier between finishing a task and logging it.

- Task logging via mobile must require **≤ 2 taps** from QR scan to confirmation
- Members must not be required to create an account, log in, or remember a password
- The fallback (writing on the paper sheet) must always remain available alongside the digital method

### 8.2 Record Retention and Compliance

- All task completion records must be retained **indefinitely** in Google Sheets
- Records must include: member name, Task ID, completion date, and capture method
- Data must be exportable from Google Sheets in standard formats (CSV, Excel) for compliance reporting
- These records may be required to support Makersmiths' **501(c)(3) tax-exempt status**

### 8.3 Availability and Resilience

- The Slack bot is the primary interface, but **Google Sheets is the durable store** — if the bot is temporarily unavailable, no data is lost
- The physical sign-up sheet provides a manual fallback for task logging at all times
- OCR processing allows admin to recover data from paper sheets even if real-time digital capture fails

### 8.4 Access Control

- Slack channel membership is the primary access control mechanism — `#shop-admin` and `#shop-alerts` are restricted channels
- No separate authentication system is required
- The bot must verify actor role before executing restricted actions (task CRUD, compliance reports, etc.)

### 8.5 Multi-Shop Extensibility

- The data model must support multiple shops from the start (MSL, MSP)
- All task IDs are shop-prefixed (`MSL-`, `MSP-`) to prevent collisions
- The initial release deploys for MSL only, but adding MSP must not require architectural changes

---

## 9. Success Criteria (KPIs)

The shop sergeant is responsible for monitoring the following KPIs to assess system health and process effectiveness.

### Member-Facing Metrics

| ID | Metric | Definition | Target |
|---|---|---|---|
| **M1** | Member Compliance Rate | % of active members who log ≥ 2 volunteer hours in a given month | ≥ 80% monthly |
| **M2** | Task Completion Rate | % of posted work tasks completed within their scheduled period | ≥ 90% |
| **M3** | Data Completeness Rate | % of completed tasks with a full record in Google Sheets (name + date + Task ID) | ≥ 95% |
| **M4** | Capture Friction Score | Average number of taps required for a member to log a completed task via mobile | ≤ 2 taps |

### Operational Metrics

| ID | Metric | Definition | Target |
|---|---|---|---|
| **O1** | Steward Adoption Rate | % of stewards actively using the system to manage tasks | 100% within 60 days of launch |
| **O2** | Sheet Refresh Latency | Time between a steward requesting a new sign-up sheet and it being physically posted | ≤ 24 hours |
| **O3** | Overdue Task Alert Rate | % of overdue tasks that triggered an automated reminder before going unnoticed | 100% |
| **O4** | Top Contributor Recognition | Monthly top-contributor report generated and posted to `#shop-bulletin` on time | 100% monthly |

---

## 10. Out of Scope

The following are explicitly **not** part of this initial release:

| Item | Notes |
|---|---|
| **Makersmiths Purcellville (MSP)** | Future release. The system architecture must accommodate MSP without structural changes, but no MSP deployment is planned in Phases 1–4. |
| **Capture methods not selected** | Once a capture method is chosen from the three options in §5.3, the remaining methods are documented for reference only and will not be implemented. |
| **Member billing or dues tracking** | Shop Sergeant tracks volunteer hours only. Membership dues and billing are managed separately. |
| **Non-Slack notification channels** | Email and SMS notifications are not in scope. Slack is the sole notification channel. |
| **Mobile app** | No native iOS or Android app. The mobile experience is delivered through Slack and a mobile-optimized web form (Method 3). |
| **Real-time dashboards** | Reports are delivered on-demand via Slack or on a scheduled basis. No live dashboard is planned. |

---

*This document is maintained by the shop sergeant. For questions, open a thread in `#shop-admin` or contact the shop sergeant directly.*

