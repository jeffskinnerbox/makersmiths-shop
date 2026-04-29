---
theme: apple-basic
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

Makersmiths Leesburg (MSL) · April 30, 2026 · Jeff Irland

<!--
Opening: Thank you for coming. This review covers the requirements for Shop Sergeant —
the automated task-tracking system proposed to replace our paper-only volunteer process.
We'll walk through the problem, the solution architecture, and what we need to build.
Your critical review and recommendations are the goal here — not just sign-off.
-->

---

# Why We Need This

Makersmiths' current paper-only work task volunteering process has several weaknesses.
A new automated process, called Shop Sergeant, is proposed to remove much of the friction in the current process,
make work task activity more visible, and gather the data for our non-profit status.
The process uses Slack as its primary communication/control medium,
but can also be trigger via a few clicks on a mobile phone web form.

**Current paper-only process has 5 critical gaps:**
<div class="text-sm">

| **Gap** | **Problem** | **Impact** |
|---|---|---|
| **Incomplete records** | Members rarely write their name and date after completing a task | No reliable record of who did what — compliance data simply doesn't exist |
| **No cumulative history** | Sign-up sheets are discarded when replaced | No historical data to support Makersmiths' 501(c)(3) volunteer-labor documentation |
| **No steward monitoring** | Stewards have no way to see overdue or ignored tasks | Problems surface only when equipment breaks or a safety issue arises — never proactively |
| **No scheduling** | Periodic tasks have no mechanism to track whether they were done on time | Maintenance gets forgotten; equipment degrades; safety risks accumulate |
| **No recognition** | Top contributors can't be identified because records don't exist | Highly engaged members receive no recognition; motivation and community goodwill suffer |

</div>

---
layout: two-cols
---

# Actors — Human

<div class="text-sm">

_Ellipse shape in all diagrams_

| **Actor** | **Role Summary** |
|---|---|
| **Member** | Completes tasks; logs completions via QR or Slack; queries own history |
| **Steward** | Manages tasks for their location; generates sign-up sheets; monitors status |
| **Shop Steward** | Oversees entire shop; coordinates stewards; escalates issues |
| **Shop Sergeant** | Manages the process; monitors KPIs; full system access |

</div>

::right::

# Actors — System

<div class="text-sm">

_Rectangle shape in all diagrams_

| **Actor** | **Role Summary** |
|---|---|
| **Physical Sign-Up Sheet** | Shop-floor touchpoint — 8.5×11" landscape, posted per location |
| **QR Code** | Encodes mobile web form URL; triggers digital logging |
| **Mobile Phone** | Member's own device — no app install required |
| **Mobile Web Form** | ≤ 3-tap completion UI opened via QR scan |
| **Slack** | Primary interface — all notifications and commands |
| **Google Sheets** | **Single source of truth** for all data |
| **Claude AI Model** | Natural language query + Slack Update task processing |
| **APScheduler** | Time-based automation — reminders and scheduled reports |
| **Agentic Workers** | Python Slack bot — mediates all 4 pipelines |

</div>

---

# Technology Stack

<div class="text-sm">

| **Component** | **Technology** | **Role** |
|---|---|---|
| **Bot framework** | Python 3.11+ · Slack Bolt | Listens to Slack events; dispatches commands to the appropriate pipeline |
| **AI agent** | Claude API (`claude-sonnet-4-6`) | Natural language query handling; Slack Update task completion processing |
| **Data store** | Google Sheets API v4 | Authoritative storage for all tasks and completion records |
| **Sheet generation** | Jinja2 + wkhtmltopdf | Renders HTML sign-up sheet templates to PDF for printing |
| **QR codes** | `qrcode[pil]` Python library | Generates QR codes embedded in sign-up sheets |
| **Scheduling** | APScheduler | Sends recurring reminders; monitors overdue periodic tasks |
| **Testing** | pytest | Unit and integration tests for all pipeline components |

</div>

---
layout: two-cols
---

# Agentic AI Capabilities

<div class="text-sm">

The bot uses `claude-sonnet-4-6` for two capabilities:

**Natural Language Query Processing**

Members and stewards ask questions in plain English:

> "What tasks are still open in the metalshop?"

> "How many tasks has @alex done this month?"

Claude parses the intent, constructs the Google Sheets query, and formats the response inline in Slack.

</div>

::right::

<div class="text-sm">

**Slack Update Task Processing**

Member posts in `#shop-queries`:

> "I just finished cleaning the metalshop floor"

Claude identifies the most likely task, presents it for member confirmation, then writes the structured record.

**What Claude does NOT do:**
* Modify data without member confirmation
* Execute admin commands from `#shop-queries`
* Access data outside Google Sheets

</div>

---
layout: center
class: dark-gray
---

<img src="./assets/pipeline-overview.png" class="max-h-full max-w-full object-contain" />


---
layout: two-cols
---

# Task Database Pipeline Details

<div class="text-sm">

**Who can modify the task catalog?**
* **Steward** — own location only
* **Shop Steward** — all locations
* **Shop Sergeant** — all locations + system config

**Task ID format:** `SHOP-LOCATION-NNN`
e.g., `MSL-METAL-003` = Metalshop task #3

**Every task requires:**
unique Task ID · name · frequency · location

**Validation rules:**
* Reject duplicate Task IDs
* Reject duplicate task names within same location

</div>

::right::

<div class="text-sm">

**Key Requirements**

| # | Requirement |
|---|---|
| DB-1 | Google Sheets = single source of truth |
| DB-2 | YAML bulk-load via CLI script |
| DB-3 | Add / update / delete via Slack in `#shop-admin` |
| DB-4 | Only Steward (own location), Shop Steward, Sergeant |
| DB-5 | Task ID + name + frequency + location required |
| DB-6 | Reject duplicate IDs and names within location |
| DB-7 | Every change notifies `#shop-alerts` |

</div>

---
layout: center
class: dark-gray
---

<img src="./assets/task-database-pipeline.png" class="max-h-full max-w-full object-contain" />

---
layout: center
class: dark-gray
---

<img src="./assets/task-sheet-pipeline.png" class="max-h-full max-w-full object-contain" />


---
layout: two-cols
---

# Physical Sign-Up Sheet Format

<div class="text-sm">

**Specification:**
* 8.5 × 11 inches, landscape orientation
* One sheet per location · Legible in black and white
* Makersmiths logo in header

**Required columns:**

| Column | Content |
|---|---|
| Task Name | Human-readable description |
| Frequency | Weekly, Monthly, Quarterly, etc. |
| Supervisor Required | Yes / No |
| Completion Date | Blank — member writes by hand |
| Member Name | Blank — member writes by hand |

**QR Code:** Single code in page header (one per location)

</div>

::right::

<div class="text-sm">

**Task Display Rules**
* Tasks grouped by location
* TBD / empty tasks silently omitted
* Ordered by frequency (most frequent first)

**Key Requirements**

| # | Requirement |
|---|---|
| TS-1 | Generate for single location or all locations |
| TS-2 | Authorized roles only (Steward = own location) |
| TS-3 | Via Slack command or CLI |
| TS-4 | `#shop-bulletin` notified when sheet is ready |
| TS-5 | `#shop-alerts` notified each generation |
| TS-6 | Bot reminds stewards when task changes make a refresh advisable |

</div>

---
layout: center
class: dark-gray
---

<img src="./assets/task-capture-pipeline.png" class="max-h-full max-w-full object-contain" />

---
layout: two-cols
---

# Task Capture Pipeline Details

# Method 1: QR

<div class="text-sm">

**Single-Sheet QR Flow**

1. Member scans QR code on sign-up sheet with phone camera
2. Browser opens mobile web form automatically (no app, no login)
3. Member selects task + taps Submit **(≤ 3 taps total)**
4. Agentic Workers writes completion record to Google Sheets
5. Confirmation posted to `#shop-log`

**Record written includes:**
* Member name · Task ID · Completion date · Source: `QR-form`

</div>

::right::

# Method 2: Slack

<div class="text-sm">

**Slack Update Flow**

1. Member posts in `#shop-queries` — free-form text or `task-done <task_id>`
2. Bot identifies task via NL processing (Claude AI) or task list selection
3. Bot confirms task identity with member before writing
4. Agentic Workers writes completion record to Google Sheets
5. Confirmation posted to `#shop-log`

**Record written includes:**
* Member name · Task ID · Completion date · Source: `Slack`

> Method 2 assumes the member has an existing Slack account.

</div>

---

# Task Capture — Requirements

<div class="text-sm">

| # | Requirement |
|---|---|
| TC-1 | Every completion record must include: Member name, Task ID, completion date, and capture method (`QR-form` or `Slack`) |
| TC-2 | Completion records must be written to Google Sheets immediately upon submission |
| TC-3 | A confirmation message must appear in `#shop-log` for every logged completion |
| TC-4 | `#shop-alerts` must be notified whenever a capture event is processed |
| TC-5 | The Method 1 (QR) capture flow must require ≤ 3 taps on a mobile device from QR scan to confirmation |
| TC-6 | Method 1 (QR) must not require Members to create an account or install an app |
| TC-7 | The bot must accept task completions in `#shop-queries` via free-form NL text or the `task-done <task_id>` command |
| TC-8 | When no Task ID is provided, the bot must identify the task via NL processing or present a task list for selection |
| TC-9 | The bot must confirm the identified task with the member before writing the completion record |

</div>

---
layout: center
class: dark-gray
---

<img src="./assets/task-reporting-pipeline.png" class="max-h-full max-w-full object-contain" />


---
layout: two-cols
---

# Task Reporting Pipeline Detail

<div class="text-sm">

**On-Demand Reports (NL query in Slack)**

| Report | Description | Access |
|---|---|---|
| **Member** | Tasks completed; compliance status | Own: any member · Other: Steward+ |
| **Location** | Task status; overdue tasks | All Members (public) |
| **Shop** | Aggregate; top contributors | All Members (public) |
| **Compliance** | Who met 2hr/month requirement | Shop Steward + Sergeant only |

**Scheduled Reports (APScheduler)**
* **Weekly** → `#shop-bulletin`: errors logged, location availability
* **Monthly** → `#shop-bulletin`: compliance summary
* **Monthly** → `#shop-bulletin`: top-contributor recognition post

</div>

::right::

# Slack Channel Structure

<div class="text-sm">

| Channel | Access | Purpose |
|---|---|---|
| `#shop-log` | All (read) | Task completion confirmations |
| `#shop-bulletin` | All (read) | Announcements + scheduled reports |
| `#shop-queries` | All | NL queries — public data |
| `#shop-admin` 🔒 | Stewards+ | Admin commands; restricted reports |
| `#shop-alerts` 🔒 | Sgt only | Full audit trail + bot errors |

</div>

---

# Permission Model

<div class="text-xs">

| Action | Member | Steward | Shop Steward | Shop Sergeant | Channel |
|---|:---:|:---:|:---:|:---:|---|
| Log task completion (QR or Slack) | ✅ | ✅ | ✅ | ✅ | web form / `#shop-queries` |
| Query own task history | ✅ | ✅ | ✅ | ✅ | `#shop-queries` |
| Query any Member's task history | ❌ | ❌ | ✅ | ✅ | `#shop-admin` |
| Query open tasks / location status | ✅ | ✅ | ✅ | ✅ | `#shop-queries` |
| Add / update / delete a task | ❌ | ✅ own | ✅ | ✅ | `#shop-admin` |
| Generate / print sign-up sheet | ❌ | ✅ own | ✅ | ✅ | `#shop-admin` |
| Request location or shop report | ✅ public | ✅ | ✅ | ✅ | `#shop-queries` / `#shop-admin` |
| Trigger overdue reminder blast | ❌ | ❌ | ✅ | ✅ | `#shop-admin` |
| View bot errors / audit log | ❌ | ❌ | ✅ | ✅ | `#shop-alerts` |
| Suspend / restore — location scope | ❌ | ✅ | ✅ | ✅ | `#shop-admin` |
| Suspend / restore — shop scope | ❌ | ❌ | ❌ | ✅ | `#shop-admin` |

</div>

<div class="text-xs mt-2">

> Steward permissions are scoped to their own location. Stewards CAN suspend/restore their location but CANNOT query other members' history or trigger reminder blasts.

</div>

---
layout: two-cols
---

# Non-Functional Requirements

<div class="text-sm">

**Member Experience (Core Principle)**
* ≤ 3 taps from QR scan to confirmation (Method 1)
* No account, no login, no app required for Method 1
* Paper fallback **always** available alongside digital

**Record Retention**
* Completion records retained **indefinitely** in Google Sheets
* Every record: member name + Task ID + date + capture method
* Exportable in CSV / Excel for 501(c)(3) compliance documentation

**Availability & Resilience**
* Google Sheets is durable — bot outage = zero data loss
* Physical sign-up sheet is the permanent manual fallback
* Two independent capture paths reduce single-point-of-failure risk

</div>

::right::

<div class="text-sm">

**Access Control**
* Slack channel membership is the primary access control mechanism
* No separate authentication system required
* Bot verifies actor role before executing restricted actions

**Multi-Shop Extensibility**
* Data model supports multiple shops from day one (MSL, MSP)
* All Task IDs are shop-prefixed (`MSL-`, `MSP-`) to prevent collisions
* Initial release: MSL only — adding MSP requires **no architectural changes**

**Technology Stack**
* Python 3.11+ · Slack Bolt · Google Sheets API v4
* Claude API (`claude-sonnet-4-6`) · Jinja2 + wkhtmltopdf
* `qrcode[pil]` · APScheduler · pytest

</div>

---

# Success Criteria — Member-Facing KPIs

<div class="text-sm">

| ID | Metric | Definition | Target |
|---|---|---|---|
| **M1** | Member Compliance Rate | % of active Members who log ≥ 1 completion in a given month | ≥ 50% monthly |
| **M2** | Task Completion Rate | % of posted tasks completed within their scheduled period | ≥ 90% |
| **M3** | Data Completeness Rate | % of completion records with all 3 required fields (name + Task ID + date) | ≥ 95% |

**Data gaps identified:**

* **M1 — denominator gap:** No member registry exists. **Recommendation:** Add a `members` sheet to Google Sheets with a `role` column — provides the denominator for M1 and enables the compliance report.
* **M2 and M3** — Fully computable from existing `tasks` and `completions` sheets. No gaps.

</div>

---

# Success Criteria — Operational KPIs

<div class="text-sm">

| ID | Metric | Definition | Target |
|---|---|---|---|
| **O1** | Steward Adoption Rate | % of Stewards who issued ≥ 1 bot command in the period | 100% within 60 days of launch |
| **O2** | Sheet Refresh Latency | Time from Slack command to PDF available for download | ≤ 24 hours |
| **O3** | Overdue Task Alert Rate | % of overdue tasks for which an APScheduler reminder was sent | 100% |
| **O4** | Top Contributor Recognition | Monthly top-contributor report posted to `#shop-bulletin` on time | 100% monthly |

**Data gaps identified:**

* **O1 — denominator gap:** Same as M1: no steward registry. Fixed by the `members` sheet with a `role` column.
* **O2 — scope:** Physical posting to wall is not observable. O2 is redefined as "Slack command → PDF ready."
* **O3 — log requirement:** Bot must log each overdue-reminder event with `task_id` + `alert_timestamp`. **Must be added to TR requirements.**

</div>

---

# Out of Scope

<div class="text-sm">

| Item | Notes |
|---|---|
| **Makersmiths Purcellville (MSP)** | Future release. Architecture must accommodate MSP without structural changes, but no MSP deployment is planned. |
| **Capture methods not selected** | Once Phase 0 trial picks a method, the other is documented for reference only. |
| **Email / SMS notifications** | Slack is the sole notification channel. No alternatives planned. |
| **Native mobile app** | Mobile experience delivered via mobile-optimized web form (Method 1) or Slack (Method 2). No app install required. |
| **Real-time dashboards** | Reports delivered on-demand via Slack or on a scheduled basis. NL queries cover real-time needs. |

</div>

---
layout: two-cols
---

# Current State — Phase 0

<div class="text-sm">

**Complete and passing tests:**

* `scripts/signup-sheet.py` — renders HTML sign-up sheet from YAML task file
* `scripts/signup-sheet2.py` — v2 with single header QR code (likely selection)
* `scripts/generate-signup-sheet-template.py` / `...-template2.py` — Jinja2 template generators
* `scripts/yaml-to-sheets.py` — YAML → Excel for Google Sheets import
* All tests passing with `pytest`

**Phase 0 Prototype trials pending:**

1. **Sign-up sheet format trial** — test v1 vs v2 with real stewards/members on the shop floor
2. **QR → mobile web form usability** — will members know how to scan?
3. **Slack Update usability** — can members describe tasks clearly enough for Claude to identify them?

</div>

::right::

# Next Steps

<div class="text-sm">

**After Phase 0 trial:**

1. **Select capture method(s)** — commit to Method 1 (QR), Method 2 (Slack), or both
2. **Add member registry** (`members` sheet) — unblocks M1 and O1 KPIs
3. **Write specs** (`docs/specifications.md`) — data flows, API contracts, Sheets schema
4. **Phase 1** — Google Sheets integration + YAML bulk-load
5. **Phase 2** — Slack bot framework + task CRUD commands
6. **Phase 3** — Task capture (QR web form + Slack Update)
7. **Phase 4** — Reporting pipeline + APScheduler
8. **Soft launch** — Limited steward pilot at MSL

</div>

---

# Open Questions

<div class="text-sm">

Before implementation begins, these deserve deliberate discussion:

* **Permission model edges** — Stewards can suspend their location (reasonable for emergencies) but can't trigger overdue reminders for their own location. Both edges worth discussing with actual stewards before the permission model is coded.

* **Track task duration?** — The 2hr/month requirement tracks task _count_, not actual _hours_. Adding an estimated `time` field per task enables true compliance checking. Better to add to the schema now than retrofit later.

* **Paper fallback sunset?** — If Method 1 proves reliable and shop Wi-Fi is consistently available, the permanent paper fallback adds complexity without sufficient benefit. Should it have a planned deprecation trigger?

* **APScheduler or Claude Routines?** — APScheduler runs in-process; jobs are silently skipped on bot restart. Claude Routines are managed cloud-scheduled — no persistent process needed, but adds per-run token cost. A hybrid is possible.

* **Keep both capture methods post-trial?** — If Phase 0 confirms Method 1 works reliably, retiring Method 2 removes design scope and developer ambiguity. The trial data should drive this decision.

</div>

---
layout: center
---

# Sign-Up Sheet — Example Output

<img src="./assets/metalshop-signup-sheet2.png" class="max-h-96 object-contain mx-auto" />

<div class="text-sm text-center mt-2">

_Metalshop sign-up sheet (v2) — single QR code in header · 8.5×11" landscape · black-and-white printable_

</div>

---
layout: center
---

# Questions & Discussion

**Jeff Irland**

📧 <jeff.irland@gmail.com> · 💬 Slack: jeff.irland

_Source: github.com/jeffskinnerbox/makersmiths-shop_

_Full requirements: `docs/requirements.md` · Next doc: `docs/specifications.md`

