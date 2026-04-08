# Shop Sergeant Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Slack-centric hybrid volunteer task management system for Makersmiths that supports physical sign-up sheets (pen/paper) and digital logging (QR→Slack), with Claude-powered OCR and admin workflows feeding Google Sheets as the source of truth.

**Architecture:** Sign-up sheets are generated as PDFs with per-task QR codes that open Slack with a pre-filled message. A Slack bot handles three channels: `#task-log` (member completions), `#task-intake` (admin OCR uploads), and `#shop-sergeant` (admin natural language queries). All data flows into a Google Sheet (`task-log`, `members`, `task-catalog`).

**Tech Stack:** Python 3.11+, `jinja2`, `qrcode[pil]`, Slack Bolt for Python (Socket Mode), Claude API (`claude-sonnet-4-6`), Google Sheets API v4, `weasyprint` (Phase 1+), `APScheduler`, `pytest`

---

## File Map

```
shop-sergeant/
├── input/
│   ├── MSL-volunteer-opportunities.yaml                        # MODIFIED (Phase 0+1): add task_id to each task
│   ├── metalshop-volunteer-opportunities.yaml  # MODIFIED (Phase 0): task_id fields added ✅
│   └── makersmiths-logo.png                   # NEW: drop logo here for header
├── scripts/
│   ├── parse-tasks.py                         # existing, updated to handle all root keys
│   ├── signup-sheet-template.py               # NEW (Phase 0): template gen (CLI + build_template()) ✅
│   ├── signup_sheet.py                        # NEW (Phase 0): sheet renderer library ✅
│   ├── signup-sheet.py                        # NEW (Phase 0): CLI for sheet gen ✅
│   ├── generate-sheets.py                     # NEW (Phase 1): YAML → PDF with live QR codes
│   └── sync-catalog.py                        # NEW (Phase 1): sync task-catalog sheet from YAML
├── bot/
│   ├── __init__.py              # NEW (Phase 2): empty
│   ├── app.py                   # NEW (Phase 2): Slack Bolt entry point
│   ├── config.py                # NEW (Phase 2): env var loading
│   ├── sheets.py                # NEW (Phase 2): Google Sheets client
│   ├── claude_client.py         # NEW (Phase 3): Claude API (OCR + agent)
│   ├── scheduler.py             # NEW (Phase 4): APScheduler reminders
│   └── handlers/
│       ├── __init__.py          # NEW (Phase 2): empty
│       ├── task_done.py         # NEW (Phase 2): "task-done <id>" handler
│       ├── ocr.py               # NEW (Phase 3): image upload → OCR handler
│       └── admin.py             # NEW (Phase 4): natural language query handler
├── tests/
│   ├── test_signup_sheet_template.py   # NEW (Phase 0) ✅
│   ├── test_signup_sheet.py            # NEW (Phase 0) ✅
│   ├── conftest.py                     # NEW (Phase 1): shared fixtures
│   ├── test_sheets.py                  # NEW (Phase 1): Sheets client unit tests
│   ├── test_task_done.py               # NEW (Phase 2): task-done handler tests
│   ├── test_ocr.py                     # NEW (Phase 3): OCR handler tests
│   └── test_admin.py                   # NEW (Phase 4): admin query handler tests
├── output/                      # generated files land here (gitignored except .gitkeep) ✅
├── requirements.txt             # NEW (Phase 1)
├── .env.example                 # NEW (Phase 1)
└── output/sheets/               # NEW (Phase 1): generated PDFs
```

---

## Phase 0 — Sign-Up Sheet Tools (Trial) ✅

**Goal:** Create printable sign-up sheets from YAML data and validate the form design
with stewards and members before any automation is built. QR codes use a placeholder
URL (`https://makersmiths.org`) until the Slack bot exists.

**Deliverables (all complete):**
- `scripts/signup-sheet-template.py` — generates a reusable Jinja2 HTML template
- `scripts/signup-sheet.py` — renders template + YAML → HTML sign-up sheet
- `input/metalshop-volunteer-opportunities.yaml` — task_id fields added (MSL-METAL-001…007)
- 33 tests passing

**Usage:**

```bash
# Generate the default Jinja2 template
python3 scripts/signup-sheet-template.py --output output/signup-sheet-template.html.j2

# Generate the metalshop sign-up sheet
python3 scripts/signup-sheet.py \
    --template output/signup-sheet-template.html.j2 \
    --yaml input/metalshop-volunteer-opportunities.yaml \
    --output output/metalshop-signup-sheet.html

# Open in browser → File > Print to save as PDF
```

**Trial Process:**
1. Generate the metalshop sign-up sheet and review with area steward (Brad Hess)
2. Print and post in place of existing sign-up sheets at MSL
3. Walk members through how the QR column will eventually work
4. Collect feedback on: layout, task names, frequency labels, QR column placement
5. Update YAML and/or template based on feedback before moving to Phase 1

---

## Phase 1 — Foundation (QR Sheets + Google Sheets Setup)

### Task 1: Add task_id to MSL-volunteer-opportunities.yaml

**Files:**
- Modify: `MSL-volunteer-opportunities.yaml`

- [x] **Step 1: Open MSL-volunteer-opportunities.yaml and add `task_id` to every task under `work_tasks`**

  Format: `<SHOP_CODE>-<AREA_CODE>-<SEQ>` where SHOP_CODE = `MSL` or `MSP`, AREA_CODE is a short 3-4 letter code for the location (e.g., `3DP`, `METAL`, `WOOD`, `LASER`), SEQ is a zero-padded 3-digit number.

  Example diff for the 3D Printing location:

  ```yaml
  - name: 3D Printing
    steward: Bryan Daniels, Scott Silvers
    work_tasks:
      - task: Dust & Wipe Down Machines
        task_id: MSL-3D-PRINT-001
        frequency: Weekly
      - task: Clean-Off & Organize Tabletops
        task_id: MSL-3D-PRINT-002
        frequency: Weekly
      - task: Remove Anything That is Not 3D Printing and Put Away
        task_id: MSL-3D-PRINT-003
        frequency: Weekly
      - task: Vaccum Floor & Clean-Up Filament Srapes
        task_id: MSL-3D-PRINT-004
        frequency: Weekly
      - task: Clean Resin Wash Station
        task_id: MSL-3D-PRINT-005
        frequency: Weekly
      - task: ReSpool Red PLA
        task_id: MSL-3D-PRINT-006
        frequency: Monthly
  ```

  Apply this pattern to every location in the file. Keep seq numbers unique within a location.

- [x] **Step 2: Validate YAML syntax**

  ```bash
  yamllint input/MSL-volunteer-opportunities.yaml
  ```

  Expected: no errors.

- [x] **Step 3: Spot-check IDs are unique across the file**

  ```bash
  python3 -c "
  import yaml
  with open('input/MSL-volunteer-opportunities.yaml') as f:
      data = yaml.safe_load(f)
  ids = []
  shop = data['opportunities']['shop']
  for area in shop.get('area', []):
      for loc in area.get('location', []):
          for task in loc.get('work_tasks', []):
              tid = task.get('task_id')
              if tid:
                  ids.append(tid)
  dupes = [x for x in ids if ids.count(x) > 1]
  print(f'Total IDs: {len(ids)}, Duplicates: {set(dupes)}')
  "
  ```

  Expected: `Duplicates: set()`

- [x] **Step 4: Commit**

  ```bash
  git add input/MSL-volunteer-opportunities.yaml
  git commit -m "feat: add stable task_id to all tasks in MSL-volunteer-opportunities.yaml"
  ```

---

### Task 2: Create project structure and requirements

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `bot/__init__.py`
- Create: `bot/handlers/__init__.py`

- [ ] **Step 1: Write requirements.txt**

  ```
  # Slack
  slack-bolt>=1.18.0
  slack-sdk>=3.27.0

  # Claude
  anthropic>=0.28.0

  # Google Sheets
  google-api-python-client>=2.120.0
  google-auth>=2.29.0

  # QR + PDF
  qrcode[pil]>=7.4.2
  weasyprint>=62.1
  Pillow>=10.3.0

  # Scheduler
  APScheduler>=3.10.4

  # YAML
  pyyaml>=6.0.1

  # HTTP (for downloading Slack images)
  requests>=2.31.0

  # Testing
  pytest>=8.1.0
  pytest-mock>=3.14.0
  ```

- [ ] **Step 2: Write .env.example**

  ```bash
  SLACK_BOT_TOKEN=xoxb-your-bot-token
  SLACK_APP_TOKEN=xapp-your-app-token
  ANTHROPIC_API_KEY=sk-ant-your-key
  GOOGLE_CREDENTIALS_FILE=/path/to/service-account.json
  GOOGLE_SPREADSHEET_ID=your-spreadsheet-id
  TASK_LOG_CHANNEL=C0000000001
  TASK_INTAKE_CHANNEL=C0000000002
  SHOP_SERGEANT_CHANNEL=C0000000003
  ANNOUNCEMENTS_CHANNEL=C0000000004
  SLACK_TEAM_ID=T0000000001
  ```

- [ ] **Step 3: Create empty `__init__.py` files**

  ```bash
  mkdir -p bot/handlers tests
  touch bot/__init__.py bot/handlers/__init__.py tests/__init__.py
  ```

- [ ] **Step 4: Install dependencies**

  ```bash
  pip install -r requirements.txt
  ```

  Expected: all packages install without error.

- [ ] **Step 5: Commit**

  ```bash
  git add requirements.txt .env.example bot/__init__.py bot/handlers/__init__.py tests/__init__.py
  git commit -m "chore: add requirements and project skeleton"
  ```

---

### Task 3: Write config.py

**Files:**
- Create: `bot/config.py`

- [ ] **Step 1: Write the failing test**

  ```python
  # tests/test_config.py
  import os
  import pytest
  from bot.config import load_config

  def test_load_config_raises_on_missing_vars(monkeypatch):
      for key in ["SLACK_BOT_TOKEN", "SLACK_APP_TOKEN", "ANTHROPIC_API_KEY",
                  "GOOGLE_CREDENTIALS_FILE", "GOOGLE_SPREADSHEET_ID",
                  "TASK_LOG_CHANNEL", "TASK_INTAKE_CHANNEL",
                  "SHOP_SERGEANT_CHANNEL", "ANNOUNCEMENTS_CHANNEL", "SLACK_TEAM_ID"]:
          monkeypatch.delenv(key, raising=False)
      with pytest.raises(EnvironmentError, match="Missing required env vars"):
          load_config()

  def test_load_config_returns_config(monkeypatch):
      monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
      monkeypatch.setenv("SLACK_APP_TOKEN", "xapp-test")
      monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
      monkeypatch.setenv("GOOGLE_CREDENTIALS_FILE", "/tmp/creds.json")
      monkeypatch.setenv("GOOGLE_SPREADSHEET_ID", "sheet-123")
      monkeypatch.setenv("TASK_LOG_CHANNEL", "C001")
      monkeypatch.setenv("TASK_INTAKE_CHANNEL", "C002")
      monkeypatch.setenv("SHOP_SERGEANT_CHANNEL", "C003")
      monkeypatch.setenv("ANNOUNCEMENTS_CHANNEL", "C004")
      monkeypatch.setenv("SLACK_TEAM_ID", "T001")
      config = load_config()
      assert config.slack_bot_token == "xoxb-test"
      assert config.slack_team_id == "T001"
  ```

- [ ] **Step 2: Run test to verify it fails**

  ```bash
  pytest tests/test_config.py -v
  ```

  Expected: FAIL with `ImportError` or `ModuleNotFoundError`.

- [ ] **Step 3: Write bot/config.py**

  ```python
  import os
  from dataclasses import dataclass

  @dataclass
  class Config:
      slack_bot_token: str
      slack_app_token: str
      anthropic_api_key: str
      google_credentials_file: str
      google_spreadsheet_id: str
      task_log_channel: str
      task_intake_channel: str
      shop_sergeant_channel: str
      announcements_channel: str
      slack_team_id: str

  def load_config() -> Config:
      required = [
          "SLACK_BOT_TOKEN", "SLACK_APP_TOKEN", "ANTHROPIC_API_KEY",
          "GOOGLE_CREDENTIALS_FILE", "GOOGLE_SPREADSHEET_ID",
          "TASK_LOG_CHANNEL", "TASK_INTAKE_CHANNEL",
          "SHOP_SERGEANT_CHANNEL", "ANNOUNCEMENTS_CHANNEL", "SLACK_TEAM_ID",
      ]
      missing = [k for k in required if not os.getenv(k)]
      if missing:
          raise EnvironmentError(f"Missing required env vars: {', '.join(missing)}")
      return Config(
          slack_bot_token=os.environ["SLACK_BOT_TOKEN"],
          slack_app_token=os.environ["SLACK_APP_TOKEN"],
          anthropic_api_key=os.environ["ANTHROPIC_API_KEY"],
          google_credentials_file=os.environ["GOOGLE_CREDENTIALS_FILE"],
          google_spreadsheet_id=os.environ["GOOGLE_SPREADSHEET_ID"],
          task_log_channel=os.environ["TASK_LOG_CHANNEL"],
          task_intake_channel=os.environ["TASK_INTAKE_CHANNEL"],
          shop_sergeant_channel=os.environ["SHOP_SERGEANT_CHANNEL"],
          announcements_channel=os.environ["ANNOUNCEMENTS_CHANNEL"],
          slack_team_id=os.environ["SLACK_TEAM_ID"],
      )
  ```

- [ ] **Step 4: Run test to verify it passes**

  ```bash
  pytest tests/test_config.py -v
  ```

  Expected: 2 PASSED.

- [ ] **Step 5: Commit**

  ```bash
  git add bot/config.py tests/test_config.py
  git commit -m "feat: add config loader with env var validation"
  ```

---

### Task 4: Write sheets.py

**Files:**
- Create: `bot/sheets.py`
- Create: `tests/test_sheets.py`

- [ ] **Step 1: Write the failing tests**

  ```python
  # tests/test_sheets.py
  import pytest
  from unittest.mock import MagicMock, patch
  from bot.sheets import SheetsClient

  @pytest.fixture
  def mock_service():
      with patch("bot.sheets.build") as mock_build:
          mock_svc = MagicMock()
          mock_build.return_value = mock_svc
          with patch("bot.sheets.Credentials.from_service_account_file"):
              yield mock_svc

  @pytest.fixture
  def client(mock_service):
      return SheetsClient("/fake/creds.json", "sheet-id-123")

  def test_get_task_returns_matching_row(client, mock_service):
      mock_service.spreadsheets().values().get().execute.return_value = {
          "values": [
              ["task_id", "task_name", "location", "shop", "frequency", "last_generated"],
              ["MSL-METAL-001", "Clean welding tables", "Metal Shop", "MSL", "Weekly", "2026-04-01"],
              ["MSL-METAL-002", "Check grinder wheels", "Metal Shop", "MSL", "Weekly", "2026-04-01"],
          ]
      }
      result = client.get_task("MSL-METAL-001")
      assert result["task_name"] == "Clean welding tables"
      assert result["shop"] == "MSL"

  def test_get_task_returns_none_for_unknown_id(client, mock_service):
      mock_service.spreadsheets().values().get().execute.return_value = {
          "values": [
              ["task_id", "task_name", "location", "shop", "frequency", "last_generated"],
          ]
      }
      result = client.get_task("MSL-UNKNOWN-999")
      assert result is None

  def test_append_completion_calls_api(client, mock_service):
      mock_service.spreadsheets().values().append().execute.return_value = {}
      client.append_completion(
          member_name="Jeff Smith",
          slack_id="U123",
          task_id="MSL-METAL-001",
          task_name="Clean welding tables",
          location="Metal Shop",
          shop="MSL",
          completion_date="2026-04-01",
          source="QR",
      )
      mock_service.spreadsheets().values().append.assert_called_once()
      call_kwargs = mock_service.spreadsheets().values().append.call_args
      row = call_kwargs.kwargs["body"]["values"][0]
      assert row[1] == "Jeff Smith"
      assert row[3] == "MSL-METAL-001"
      assert row[8] == "QR"

  def test_get_active_members_filters_inactive(client, mock_service):
      mock_service.spreadsheets().values().get().execute.return_value = {
          "values": [
              ["member_name", "slack_id", "active"],
              ["Jeff Smith", "U001", "Y"],
              ["Old Member", "U002", "N"],
              ["Amy Jones", "U003", "Y"],
          ]
      }
      members = client.get_active_members()
      assert len(members) == 2
      assert all(m["active"] == "Y" for m in members)
  ```

- [ ] **Step 2: Run tests to verify they fail**

  ```bash
  pytest tests/test_sheets.py -v
  ```

  Expected: FAIL with `ImportError`.

- [ ] **Step 3: Write bot/sheets.py**

  ```python
  from datetime import datetime
  from typing import Optional
  from google.oauth2.service_account import Credentials
  from googleapiclient.discovery import build

  SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

  class SheetsClient:
      def __init__(self, credentials_file: str, spreadsheet_id: str):
          creds = Credentials.from_service_account_file(credentials_file, scopes=SCOPES)
          self._service = build("sheets", "v4", credentials=creds)
          self._spreadsheet_id = spreadsheet_id

      def _get_rows(self, range_: str) -> list[dict]:
          result = self._service.spreadsheets().values().get(
              spreadsheetId=self._spreadsheet_id, range=range_
          ).execute()
          rows = result.get("values", [])
          if not rows:
              return []
          header = rows[0]
          return [dict(zip(header, row)) for row in rows[1:]]

      def get_task(self, task_id: str) -> Optional[dict]:
          for row in self._get_rows("task-catalog!A:F"):
              if row.get("task_id") == task_id:
                  return row
          return None

      def get_full_task_catalog(self) -> list[dict]:
          return self._get_rows("task-catalog!A:F")

      def get_all_completions(self) -> list[dict]:
          return self._get_rows("task-log!A:J")

      def get_active_members(self) -> list[dict]:
          members = self._get_rows("members!A:C")
          return [m for m in members if m.get("active", "").upper() in ("Y", "YES", "TRUE")]

      def append_completion(self, member_name: str, slack_id: str, task_id: str,
                            task_name: str, location: str, shop: str,
                            completion_date: str, source: str, notes: str = "") -> None:
          timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
          row = [timestamp, member_name, slack_id, task_id, task_name,
                 location, shop, completion_date, source, notes]
          self._service.spreadsheets().values().append(
              spreadsheetId=self._spreadsheet_id,
              range="task-log!A:J",
              valueInputOption="USER_ENTERED",
              body={"values": [row]},
          ).execute()
  ```

- [ ] **Step 4: Run tests to verify they pass**

  ```bash
  pytest tests/test_sheets.py -v
  ```

  Expected: 4 PASSED.

- [ ] **Step 5: Commit**

  ```bash
  git add bot/sheets.py tests/test_sheets.py
  git commit -m "feat: add Google Sheets client with task lookup and completion logging"
  ```

---

### Task 5: Write generate-sheets.py (QR PDF generation)

**Files:**
- Create: `scripts/generate-sheets.py`
- Modify: `.gitignore` (add `output/`)

- [ ] **Step 1: Add output/ to .gitignore**

  ```bash
  echo "output/" >> .gitignore
  ```

- [ ] **Step 2: Write scripts/generate-sheets.py**

  ```python
  #!/usr/bin/env python3
  """
  generate-sheets.py

  Generates sign-up sheet PDFs from MSL-volunteer-opportunities.yaml.
  Each location gets its own PDF page with task rows and per-task QR codes.

  Usage:
      python3 scripts/generate-sheets.py MSL-volunteer-opportunities.yaml output/sheets \
          --team-id T0000000001 --channel-id C0000000001
  """

  import argparse
  import base64
  import sys
  import yaml
  import qrcode
  from io import BytesIO
  from pathlib import Path
  from datetime import date
  from weasyprint import HTML


  def make_qr_data_url(task_id: str, team_id: str, channel_id: str) -> str:
      msg = f"task-done%20{task_id}"
      link = f"slack://channel?team={team_id}&id={channel_id}&message={msg}"
      qr = qrcode.make(link)
      buf = BytesIO()
      qr.save(buf, format="PNG")
      b64 = base64.b64encode(buf.getvalue()).decode()
      return f"data:image/png;base64,{b64}"


  def render_location_html(shop_name: str, location_name: str, steward: str,
                            tasks: list, team_id: str, channel_id: str) -> str:
      rows = ""
      for t in tasks:
          task_id = t.get("task_id", "")
          task_name = t.get("task", task_id)
          frequency = t.get("frequency", "")
          if task_id:
              qr_url = make_qr_data_url(task_id, team_id, channel_id)
              qr_cell = f'<img src="{qr_url}" width="55" height="55">'
          else:
              qr_cell = "<em>no ID</em>"
          rows += f"""
          <tr>
            <td>{task_name}</td>
            <td class="freq">{frequency}</td>
            <td class="sign"></td>
            <td class="sign"></td>
            <td class="qr">{qr_cell}</td>
          </tr>"""

      return f"""<!DOCTYPE html>
  <html>
  <head><meta charset="utf-8">
  <style>
    body {{ font-family: Arial, sans-serif; font-size: 10.5pt; margin: 18px 24px; }}
    h1 {{ font-size: 13pt; margin-bottom: 2px; }}
    h2 {{ font-size: 11pt; margin-top: 4px; color: #333; }}
    p {{ margin: 4px 0 10px; font-size: 9.5pt; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border: 1px solid #aaa; padding: 5px 7px; vertical-align: middle; }}
    th {{ background: #e8e8e8; text-align: left; font-size: 10pt; }}
    .freq {{ width: 70px; text-align: center; }}
    .sign {{ width: 150px; }}
    .qr {{ width: 65px; text-align: center; padding: 3px; }}
    .footer {{ font-size: 8.5pt; color: #888; margin-top: 6px; }}
  </style>
  </head>
  <body>
    <h1>{shop_name}</h1>
    <h2>{location_name}</h2>
    <p><strong>Steward:</strong> {steward} &nbsp;&nbsp;
       <strong>Generated:</strong> {date.today().isoformat()}</p>
    <p><em>Sign and date when you complete a task.
       Or scan the QR code — Slack opens, tap Send to log digitally.</em></p>
    <table>
      <thead>
        <tr>
          <th>Task</th><th>Freq</th>
          <th>Member (sign)</th><th>Date</th><th>Log It</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
    <p class="footer">
      Scan QR → Slack opens with task pre-filled → tap Send. Done in 2 taps.
    </p>
  </body>
  </html>"""


  def generate_sheets(yaml_path: str, output_dir: str, team_id: str, channel_id: str) -> None:
      with open(yaml_path) as f:
          data = yaml.safe_load(f)

      shop = data["tasks_list"]["shop"]
      shop_name = shop["name"]
      out = Path(output_dir)
      out.mkdir(parents=True, exist_ok=True)

      for area in shop.get("area", []):
          for location in area.get("location", []):
              loc_name = location.get("name", "unknown")
              steward = location.get("steward", "")
              tasks = location.get("work_tasks", [])
              if not tasks:
                  continue

              html = render_location_html(shop_name, loc_name, steward,
                                          tasks, team_id, channel_id)
              safe = loc_name.lower().replace(" ", "-").replace("/", "-")
              pdf_path = out / f"{safe}.pdf"
              HTML(string=html).write_pdf(str(pdf_path))
              print(f"  Generated: {pdf_path}")


  def main():
      parser = argparse.ArgumentParser(description="Generate sign-up sheet PDFs with QR codes")
      parser.add_argument("yaml_file", help="Path to MSL-volunteer-opportunities.yaml")
      parser.add_argument("output_dir", help="Directory to write PDFs into")
      parser.add_argument("--team-id", required=True, help="Slack workspace team ID (T...)")
      parser.add_argument("--channel-id", required=True, help="Slack #task-log channel ID (C...)")
      args = parser.parse_args()

      print(f"Generating sheets from {args.yaml_file} → {args.output_dir}/")
      generate_sheets(args.yaml_file, args.output_dir, args.team_id, args.channel_id)
      print("Done.")


  if __name__ == "__main__":
      main()
  ```

- [ ] **Step 3: Run the generator against real data (smoke test)**

  ```bash
  cd /home/jeff/src/projects/makersmiths/shop-sergeant
  python3 scripts/generate-sheets.py MSL-volunteer-opportunities.yaml output/sheets \
      --team-id TXXXXXXXX --channel-id CXXXXXXXX
  ```

  Expected: PDF files appear in `output/sheets/`. Open one PDF — verify table with QR images in the last column.

- [ ] **Step 4: Verify QR codes decode correctly**

  Open the PDF, screenshot a QR code, decode it with a phone camera or online QR decoder.
  Expected: decoded URL matches `slack://channel?team=TXXXXXXXX&id=CXXXXXXXX&message=task-done%20MSL-XXXX-XXX`

- [ ] **Step 5: Commit**

  ```bash
  git add scripts/generate-sheets.py .gitignore
  git commit -m "feat: add QR-code PDF sign-up sheet generator"
  ```

---

### Task 6: Write sync-catalog.py and set up Google Sheets

**Files:**
- Create: `scripts/sync-catalog.py`

- [ ] **Step 1: Manually create the Google Spreadsheet**

  1. Go to [sheets.google.com](https://sheets.google.com) and create a new spreadsheet named `ShopSergeant`.
  2. Rename the default sheet to `task-log`.
  3. Add sheets named `members` and `task-catalog` (click `+` at the bottom).
  4. In `task-log`, add header row in row 1: `timestamp | member_name | slack_id | task_id | task_name | location | shop | completion_date | source | notes`
  5. In `members`, add header row: `member_name | slack_id | active`
  6. In `task-catalog`, add header row: `task_id | task_name | location | shop | frequency | last_generated`
  7. Copy the spreadsheet ID from the URL (`https://docs.google.com/spreadsheets/d/<ID>/edit`).

- [ ] **Step 2: Create a Google Service Account**

  1. In [Google Cloud Console](https://console.cloud.google.com), create a project (or reuse one).
  2. Enable the **Google Sheets API**.
  3. Create a Service Account. Download the JSON key file. Store at a safe path (e.g., `/etc/shop-sergeant/google-creds.json`).
  4. Share the spreadsheet with the service account email (give it Editor access).

- [ ] **Step 3: Write scripts/sync-catalog.py**

  ```python
  #!/usr/bin/env python3
  """
  sync-catalog.py

  Syncs task-catalog Google Sheet from MSL-volunteer-opportunities.yaml.
  Clears the sheet (except header) and rewrites all task rows.

  Usage:
      python3 scripts/sync-catalog.py MSL-volunteer-opportunities.yaml \
          --credentials /path/to/creds.json \
          --spreadsheet-id YOUR_SHEET_ID
  """

  import argparse
  import yaml
  from datetime import date
  from google.oauth2.service_account import Credentials
  from googleapiclient.discovery import build

  SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
  HEADER = ["task_id", "task_name", "location", "shop", "frequency", "last_generated"]


  def sync(yaml_path: str, credentials_file: str, spreadsheet_id: str) -> None:
      creds = Credentials.from_service_account_file(credentials_file, scopes=SCOPES)
      service = build("sheets", "v4", credentials=creds)
      sheets = service.spreadsheets()

      with open(yaml_path) as f:
          data = yaml.safe_load(f)

      shop = data["tasks_list"]["shop"]
      shop_code = "MSL" if "Leesburg" in shop.get("name", "") else "MSP"
      today = date.today().isoformat()

      rows = [HEADER]
      for area in shop.get("area", []):
          for location in area.get("location", []):
              loc_name = location.get("name", "")
              for task in location.get("work_tasks", []):
                  task_id = task.get("task_id", "")
                  if not task_id:
                      continue
                  rows.append([
                      task_id,
                      task.get("task", ""),
                      loc_name,
                      shop_code,
                      task.get("frequency", ""),
                      today,
                  ])

      # Clear existing data (keep header by clearing A2:F)
      sheets.values().clear(
          spreadsheetId=spreadsheet_id, range="task-catalog!A2:F"
      ).execute()

      # Write all rows (including header at A1)
      sheets.values().update(
          spreadsheetId=spreadsheet_id,
          range="task-catalog!A1",
          valueInputOption="USER_ENTERED",
          body={"values": rows},
      ).execute()

      print(f"Synced {len(rows) - 1} tasks to task-catalog sheet.")


  def main():
      parser = argparse.ArgumentParser()
      parser.add_argument("yaml_file")
      parser.add_argument("--credentials", required=True)
      parser.add_argument("--spreadsheet-id", required=True)
      args = parser.parse_args()
      sync(args.yaml_file, args.credentials, args.spreadsheet_id)


  if __name__ == "__main__":
      main()
  ```

- [ ] **Step 4: Run sync-catalog.py**

  ```bash
  python3 scripts/sync-catalog.py MSL-volunteer-opportunities.yaml \
      --credentials /path/to/creds.json \
      --spreadsheet-id YOUR_SHEET_ID
  ```

  Expected: `Synced N tasks to task-catalog sheet.` Open the Google Sheet and confirm rows appear in `task-catalog`.

- [ ] **Step 5: Commit**

  ```bash
  git add scripts/sync-catalog.py
  git commit -m "feat: add sync-catalog script to populate task-catalog sheet from YAML"
  ```

---

## Phase 2 — Slack Bot (Digital QR Flow)

### Task 7: Create Slack App

This is configuration work, no code.

- [ ] **Step 1: Create Slack app at api.slack.com**

  1. Go to [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → **From scratch**.
  2. Name: `ShopSergeant`. Workspace: select Makersmiths workspace.

- [ ] **Step 2: Configure bot scopes**

  Under **OAuth & Permissions** → **Bot Token Scopes**, add:
  - `chat:write` — post messages
  - `channels:history` — read messages in channels bot is in
  - `im:write` — send DMs
  - `users:read` — look up user display names
  - `files:read` — download uploaded images

- [ ] **Step 3: Enable Socket Mode**

  Under **Socket Mode** → toggle **Enable Socket Mode** on.
  Generate an App-Level Token with scope `connections:write`. This is `SLACK_APP_TOKEN`.

- [ ] **Step 4: Enable Events**

  Under **Event Subscriptions** → toggle on. Subscribe to:
  - `message.channels` — for `#task-log`, `#task-intake`, `#shop-sergeant`
  - `message.files` — for image uploads in `#task-intake`

- [ ] **Step 5: Install app to workspace**

  Under **Install App** → Install to Workspace. Copy the **Bot User OAuth Token** — this is `SLACK_BOT_TOKEN`.

- [ ] **Step 6: Get channel and team IDs**

  In Slack, right-click each channel (`#task-log`, `#task-intake`, `#shop-sergeant`, `#announcements`) → **View channel details** → copy the channel ID (starts with `C`).
  For the team ID: in Slack → **Your workspace name** → **Settings** → workspace URL has the ID, or use the API. It starts with `T`.

- [ ] **Step 7: Create .env from .env.example and fill in real values**

  ```bash
  cp .env.example .env
  # Edit .env with actual tokens, IDs, and credential path
  ```

- [ ] **Step 8: Invite the bot to the required channels**

  In each of `#task-log`, `#task-intake`, `#shop-sergeant` — type `/invite @ShopSergeant`.

---

### Task 8: Write app.py

**Files:**
- Create: `bot/app.py`

- [ ] **Step 1: Write bot/app.py**

  ```python
  import os
  from dotenv import load_dotenv
  from slack_bolt import App
  from slack_bolt.adapter.socket_mode import SocketModeHandler
  from bot.config import load_config
  from bot.sheets import SheetsClient
  from bot.claude_client import ClaudeClient
  from bot.scheduler import start_scheduler
  from bot.handlers import task_done, ocr, admin


  def create_app():
      load_dotenv()
      config = load_config()
      app = App(token=config.slack_bot_token)
      sheets = SheetsClient(config.google_credentials_file, config.google_spreadsheet_id)
      claude = ClaudeClient(config.anthropic_api_key)

      task_done.register(app, sheets, config)
      ocr.register(app, sheets, claude, config)
      admin.register(app, sheets, claude, config)

      start_scheduler(app.client, config.announcements_channel)
      return app, config


  if __name__ == "__main__":
      app, config = create_app()
      handler = SocketModeHandler(app, config.slack_app_token)
      print("ShopSergeant bot is running...")
      handler.start()
  ```

  Also add `python-dotenv` to requirements.txt:

  ```
  python-dotenv>=1.0.1
  ```

- [ ] **Step 2: Commit**

  ```bash
  git add bot/app.py requirements.txt
  git commit -m "feat: add Slack Bolt app entry point"
  ```

---

### Task 9: Write handlers/task_done.py

**Files:**
- Create: `bot/handlers/task_done.py`
- Create: `tests/test_task_done.py`

- [ ] **Step 1: Write the failing tests**

  ```python
  # tests/test_task_done.py
  import pytest
  from unittest.mock import MagicMock, patch
  from bot.handlers.task_done import handle_task_done_message


  @pytest.fixture
  def sheets():
      mock = MagicMock()
      mock.get_task.return_value = {
          "task_id": "MSL-METAL-001",
          "task_name": "Clean welding tables",
          "location": "Metal Shop",
          "shop": "MSL",
      }
      return mock


  @pytest.fixture
  def slack_client():
      client = MagicMock()
      client.users_info.return_value = {"user": {"real_name": "Jeff Smith"}}
      return client


  def test_valid_task_id_logs_completion_and_replies(sheets, slack_client):
      say = MagicMock()
      message = {"text": "task-done MSL-METAL-001", "user": "U001", "ts": "123.456"}
      handle_task_done_message(message, say, slack_client, sheets)
      sheets.append_completion.assert_called_once()
      call_kwargs = sheets.append_completion.call_args.kwargs
      assert call_kwargs["task_id"] == "MSL-METAL-001"
      assert call_kwargs["member_name"] == "Jeff Smith"
      assert call_kwargs["source"] == "QR"
      say.assert_called_once()
      assert "Clean welding tables" in say.call_args.args[0]


  def test_unknown_task_id_replies_with_error(sheets, slack_client):
      sheets.get_task.return_value = None
      say = MagicMock()
      message = {"text": "task-done MSL-UNKNOWN-999", "user": "U001", "ts": "123.456"}
      handle_task_done_message(message, say, slack_client, sheets)
      sheets.append_completion.assert_not_called()
      say.assert_called_once()
      assert "Unknown task ID" in say.call_args.args[0]


  def test_non_task_message_is_ignored(sheets, slack_client):
      say = MagicMock()
      message = {"text": "hello everyone!", "user": "U001", "ts": "123.456"}
      handle_task_done_message(message, say, slack_client, sheets)
      sheets.get_task.assert_not_called()
      say.assert_not_called()
  ```

- [ ] **Step 2: Run tests to verify they fail**

  ```bash
  pytest tests/test_task_done.py -v
  ```

  Expected: FAIL with `ImportError`.

- [ ] **Step 3: Write bot/handlers/task_done.py**

  ```python
  import re
  from datetime import date
  from slack_bolt import App
  from bot.sheets import SheetsClient
  from bot.config import Config

  TASK_DONE_RE = re.compile(r"^task-done\s+([A-Z]+-[A-Z0-9]+-\d+)$", re.IGNORECASE)


  def handle_task_done_message(message: dict, say, client, sheets: SheetsClient) -> None:
      text = (message.get("text") or "").strip()
      match = TASK_DONE_RE.match(text)
      if not match:
          return

      task_id = match.group(1).upper()
      task = sheets.get_task(task_id)
      if not task:
          say(f"❌ Unknown task ID `{task_id}`. Check the QR code on the sign-up sheet.",
              thread_ts=message["ts"])
          return

      user_id = message["user"]
      user_info = client.users_info(user=user_id)
      member_name = user_info["user"]["real_name"]
      today = date.today().isoformat()

      sheets.append_completion(
          member_name=member_name,
          slack_id=user_id,
          task_id=task_id,
          task_name=task["task_name"],
          location=task["location"],
          shop=task["shop"],
          completion_date=today,
          source="QR",
      )
      say(
          f"✅ *{member_name}* completed _{task['task_name']}_ "
          f"({task['location']}, {task['shop']}) — {today}. Thanks for contributing!",
          thread_ts=message["ts"],
      )


  def register(app: App, sheets: SheetsClient, config: Config) -> None:
      @app.message(TASK_DONE_RE)
      def on_task_done(message, say, client):
          handle_task_done_message(message, say, client, sheets)
  ```

- [ ] **Step 4: Run tests to verify they pass**

  ```bash
  pytest tests/test_task_done.py -v
  ```

  Expected: 3 PASSED.

- [ ] **Step 5: Smoke test with running bot**

  ```bash
  python3 -m bot.app
  ```

  In `#task-log`, type: `task-done MSL-METAL-001`
  Expected: bot replies in thread with confirmation. Open Google Sheet — new row in `task-log`.

- [ ] **Step 6: Commit**

  ```bash
  git add bot/handlers/task_done.py tests/test_task_done.py
  git commit -m "feat: add task-done Slack handler with Sheets logging"
  ```

---

## Phase 3 — OCR Flow

### Task 10: Write claude_client.py (OCR)

**Files:**
- Create: `bot/claude_client.py`
- Create: `tests/test_ocr_parsing.py`

- [ ] **Step 1: Write the failing tests**

  ```python
  # tests/test_ocr_parsing.py
  import pytest
  import json
  from unittest.mock import MagicMock, patch
  from bot.claude_client import ClaudeClient


  @pytest.fixture
  def claude():
      with patch("bot.claude_client.anthropic.Anthropic"):
          client = ClaudeClient("fake-key")
          return client


  def test_ocr_sheet_returns_parsed_completions(claude):
      mock_response = MagicMock()
      mock_response.content = [MagicMock(
          text=json.dumps([
              {"task_id": "MSL-METAL-001", "member_name": "Jeff Smith",
               "date": "2026-03-28", "confidence": 0.95},
              {"task_id": "MSL-METAL-002", "member_name": "Amy Jones",
               "date": "2026-03-30", "confidence": 0.88},
          ])
      )]
      claude._client.messages.create.return_value = mock_response

      task_list = [
          {"task_id": "MSL-METAL-001", "task_name": "Clean welding tables", "location": "Metal Shop"},
          {"task_id": "MSL-METAL-002", "task_name": "Check grinder wheels", "location": "Metal Shop"},
      ]
      result = claude.ocr_sheet(b"fake-image-bytes", task_list)
      assert len(result) == 2
      assert result[0]["task_id"] == "MSL-METAL-001"
      assert result[0]["confidence"] == 0.95


  def test_ocr_sheet_sends_image_as_base64(claude):
      mock_response = MagicMock()
      mock_response.content = [MagicMock(text="[]")]
      claude._client.messages.create.return_value = mock_response

      claude.ocr_sheet(b"\x89PNG\r\n", [])
      call_kwargs = claude._client.messages.create.call_args.kwargs
      content = call_kwargs["messages"][0]["content"]
      image_block = content[0]
      assert image_block["type"] == "image"
      assert image_block["source"]["type"] == "base64"
  ```

- [ ] **Step 2: Run tests to verify they fail**

  ```bash
  pytest tests/test_ocr_parsing.py -v
  ```

  Expected: FAIL with `ImportError`.

- [ ] **Step 3: Write bot/claude_client.py**

  ```python
  import anthropic
  import base64
  import json


  class ClaudeClient:
      def __init__(self, api_key: str):
          self._client = anthropic.Anthropic(api_key=api_key)

      def ocr_sheet(self, image_bytes: bytes, task_list: list[dict]) -> list[dict]:
          """Parse a sign-up sheet photo. Returns [{task_id, member_name, date, confidence}]."""
          task_context = "\n".join(
              f"- {t['task_id']}: {t['task_name']} ({t.get('location', '')})"
              for t in task_list
          )
          image_b64 = base64.standard_b64encode(image_bytes).decode()

          response = self._client.messages.create(
              model="claude-sonnet-4-6",
              max_tokens=1024,
              messages=[{
                  "role": "user",
                  "content": [
                      {
                          "type": "image",
                          "source": {
                              "type": "base64",
                              "media_type": "image/jpeg",
                              "data": image_b64,
                          },
                      },
                      {
                          "type": "text",
                          "text": (
                              "This is a Makersmiths volunteer sign-up sheet.\n"
                              f"Known tasks on this sheet:\n{task_context}\n\n"
                              "Extract every row where a member name AND a date are both filled in.\n"
                              "Return a JSON array ONLY, no other text:\n"
                              '[{"task_id":"MSL-METAL-001","member_name":"Jeff Smith",'
                              '"date":"2026-03-28","confidence":0.95}]\n\n'
                              "Rules:\n"
                              "- Match member names to the known task list by row position.\n"
                              "- Use YYYY-MM-DD for dates. Infer year from context if absent.\n"
                              "- Set confidence 0.0–1.0. Use < 0.7 for unclear handwriting.\n"
                              "- If task_id is ambiguous, use the closest match by row order."
                          ),
                      },
                  ],
              }],
          )
          return json.loads(response.content[0].text)

      def answer_admin_query(self, question: str,
                             completions: list[dict], members: list[dict]) -> str:
          """Answer a natural language admin question about volunteer task data."""
          completions_json = json.dumps(completions[-500:], indent=2)
          members_json = json.dumps(members, indent=2)

          response = self._client.messages.create(
              model="claude-sonnet-4-6",
              max_tokens=2048,
              messages=[{
                  "role": "user",
                  "content": (
                      "You are ShopSergeant, a Slack bot for Makersmiths makerspace.\n"
                      "Your job is to help admins track volunteer task completion.\n\n"
                      f"Task completion log (up to 500 recent entries):\n{completions_json}\n\n"
                      f"Active members:\n{members_json}\n\n"
                      f"Admin question: {question}\n\n"
                      "Answer concisely using Slack markdown (*bold*, _italic_, bullet lists). "
                      "If you suggest an action (e.g. sending reminders), phrase it as an offer."
                  ),
              }],
          )
          return response.content[0].text
  ```

- [ ] **Step 4: Run tests to verify they pass**

  ```bash
  pytest tests/test_ocr_parsing.py -v
  ```

  Expected: 2 PASSED.

- [ ] **Step 5: Commit**

  ```bash
  git add bot/claude_client.py tests/test_ocr_parsing.py
  git commit -m "feat: add Claude client for OCR and admin query"
  ```

---

### Task 11: Write handlers/ocr.py

**Files:**
- Create: `bot/handlers/ocr.py`
- Create: `tests/test_ocr.py`

- [ ] **Step 1: Write the failing tests**

  ```python
  # tests/test_ocr.py
  import pytest
  from unittest.mock import MagicMock, patch
  from bot.handlers import ocr as ocr_handler


  @pytest.fixture
  def sheets():
      mock = MagicMock()
      mock.get_full_task_catalog.return_value = [
          {"task_id": "MSL-METAL-001", "task_name": "Clean welding tables",
           "location": "Metal Shop", "shop": "MSL"},
      ]
      mock.get_task.return_value = {
          "task_id": "MSL-METAL-001", "task_name": "Clean welding tables",
          "location": "Metal Shop", "shop": "MSL",
      }
      return mock


  @pytest.fixture
  def claude():
      mock = MagicMock()
      mock.ocr_sheet.return_value = [
          {"task_id": "MSL-METAL-001", "member_name": "Jeff Smith",
           "date": "2026-03-28", "confidence": 0.95},
      ]
      return mock


  def test_confirm_all_appends_to_sheets(sheets, claude):
      pending = {"ts-001": [
          {"task_id": "MSL-METAL-001", "member_name": "Jeff Smith",
           "date": "2026-03-28", "confidence": 0.95}
      ]}
      say = MagicMock()
      body = {"actions": [{"value": "ts-001"}]}
      ocr_handler.confirm_all_completions(body, say, sheets, pending)
      sheets.append_completion.assert_called_once()
      assert pending == {}
      say.assert_called_once()
      assert "Logged 1" in say.call_args.args[0]


  def test_discard_all_clears_pending(sheets, claude):
      pending = {"ts-001": [{"task_id": "MSL-METAL-001", "member_name": "Jeff"}]}
      say = MagicMock()
      body = {"actions": [{"value": "ts-001"}]}
      ocr_handler.discard_all_completions(body, say, pending)
      assert pending == {}
      say.assert_called_once()


  def test_low_confidence_uses_ocr_flagged_source(sheets, claude):
      pending = {"ts-002": [
          {"task_id": "MSL-METAL-001", "member_name": "Mikl?",
           "date": "2026-03-29", "confidence": 0.55}
      ]}
      say = MagicMock()
      body = {"actions": [{"value": "ts-002"}]}
      ocr_handler.confirm_all_completions(body, say, sheets, pending)
      call_kwargs = sheets.append_completion.call_args.kwargs
      assert call_kwargs["source"] == "OCR-flagged"
  ```

- [ ] **Step 2: Run tests to verify they fail**

  ```bash
  pytest tests/test_ocr.py -v
  ```

  Expected: FAIL with `ImportError`.

- [ ] **Step 3: Write bot/handlers/ocr.py**

  ```python
  import requests
  from slack_bolt import App
  from bot.sheets import SheetsClient
  from bot.claude_client import ClaudeClient
  from bot.config import Config

  # In-memory store of unconfirmed OCR results: {event_ts: [parsed_rows]}
  _pending: dict[str, list[dict]] = {}


  def confirm_all_completions(body: dict, say, sheets: SheetsClient,
                               pending: dict = None) -> None:
      if pending is None:
          pending = _pending
      thread_ts = body["actions"][0]["value"]
      rows = pending.pop(thread_ts, [])
      if not rows:
          say("Nothing to confirm.", thread_ts=thread_ts)
          return
      for r in rows:
          task = sheets.get_task(r["task_id"])
          if not task:
              continue
          source = "OCR" if r["confidence"] >= 0.7 else "OCR-flagged"
          sheets.append_completion(
              member_name=r["member_name"],
              slack_id="",
              task_id=r["task_id"],
              task_name=task["task_name"],
              location=task["location"],
              shop=task["shop"],
              completion_date=r["date"],
              source=source,
              notes=f"confidence={r['confidence']:.2f}",
          )
      say(f"✅ Logged {len(rows)} completion(s) to Google Sheets.", thread_ts=thread_ts)


  def discard_all_completions(body: dict, say, pending: dict = None) -> None:
      if pending is None:
          pending = _pending
      thread_ts = body["actions"][0]["value"]
      pending.pop(thread_ts, None)
      say("Discarded.", thread_ts=thread_ts)


  def register(app: App, sheets: SheetsClient, claude: ClaudeClient, config: Config) -> None:
      @app.event("message")
      def handle_image_upload(event, client, say):
          if event.get("channel") != config.task_intake_channel:
              return
          files = event.get("files", [])
          if not files:
              return
          file_info = files[0]
          url = file_info.get("url_private_download")
          if not url:
              return

          resp = requests.get(url, headers={"Authorization": f"Bearer {config.slack_bot_token}"})
          resp.raise_for_status()

          task_list = sheets.get_full_task_catalog()
          parsed = claude.ocr_sheet(resp.content, task_list)
          _pending[event["ts"]] = parsed

          high = [r for r in parsed if r["confidence"] >= 0.7]
          low = [r for r in parsed if r["confidence"] < 0.7]

          lines = [f"Parsed *{len(parsed)}* completion(s) from sheet:\n"]
          for r in high:
              lines.append(f"• `{r['task_id']}` — *{r['member_name']}* — {r['date']}")
          for r in low:
              lines.append(
                  f"• ⚠️ `{r['task_id']}` — _{r['member_name']}?_ — {r['date']} "
                  f"(low confidence: {r['confidence']:.0%})"
              )
          lines.append("")

          say(
              text="\n".join(lines),
              thread_ts=event["ts"],
              blocks=[
                  {"type": "section",
                   "text": {"type": "mrkdwn", "text": "\n".join(lines)}},
                  {"type": "actions",
                   "block_id": f"ocr_{event['ts']}",
                   "elements": [
                       {"type": "button",
                        "text": {"type": "plain_text", "text": "✅ Confirm All"},
                        "style": "primary",
                        "action_id": "ocr_confirm_all",
                        "value": event["ts"]},
                       {"type": "button",
                        "text": {"type": "plain_text", "text": "❌ Discard All"},
                        "style": "danger",
                        "action_id": "ocr_discard_all",
                        "value": event["ts"]},
                   ]},
              ],
          )

      @app.action("ocr_confirm_all")
      def on_confirm(ack, body, say):
          ack()
          confirm_all_completions(body, say, sheets)

      @app.action("ocr_discard_all")
      def on_discard(ack, body, say):
          ack()
          discard_all_completions(body, say)
  ```

- [ ] **Step 4: Run tests to verify they pass**

  ```bash
  pytest tests/test_ocr.py -v
  ```

  Expected: 3 PASSED.

- [ ] **Step 5: Smoke test OCR flow with the bot running**

  ```bash
  python3 -m bot.app
  ```

  Post a photo of a test sign-up sheet (use one from `signup_sheets/`) to `#task-intake`.
  Expected: bot replies in thread with parsed completions and action buttons. Click **✅ Confirm All**. Open Google Sheet — rows appear in `task-log` with `source=OCR`.

- [ ] **Step 6: Commit**

  ```bash
  git add bot/handlers/ocr.py tests/test_ocr.py
  git commit -m "feat: add OCR image handler with Claude vision and admin confirm flow"
  ```

---

## Phase 4 — Admin Agent + Reminders

### Task 12: Write handlers/admin.py

**Files:**
- Create: `bot/handlers/admin.py`
- Create: `tests/test_admin.py`

- [ ] **Step 1: Write the failing tests**

  ```python
  # tests/test_admin.py
  import pytest
  from unittest.mock import MagicMock
  from bot.handlers.admin import handle_admin_message


  @pytest.fixture
  def sheets():
      mock = MagicMock()
      mock.get_all_completions.return_value = [
          {"member_name": "Jeff Smith", "task_name": "Clean tables",
           "completion_date": "2026-04-01", "source": "QR"},
      ]
      mock.get_active_members.return_value = [
          {"member_name": "Jeff Smith", "slack_id": "U001", "active": "Y"},
          {"member_name": "Amy Jones", "slack_id": "U002", "active": "Y"},
      ]
      return mock


  @pytest.fixture
  def claude():
      mock = MagicMock()
      mock.answer_admin_query.return_value = "Here are the members with no hours logged: Amy Jones"
      return mock


  def test_admin_message_calls_claude_and_replies(sheets, claude):
      say = MagicMock()
      message = {
          "text": "Who hasn't logged hours this month?",
          "user": "U001",
          "ts": "123.456",
          "channel": "C003",
          "bot_id": None,
      }
      handle_admin_message(message, say, sheets, claude, shop_sergeant_channel="C003")
      claude.answer_admin_query.assert_called_once()
      question = claude.answer_admin_query.call_args.args[0]
      assert "hasn't logged" in question
      say.assert_called_once()
      assert "Amy Jones" in say.call_args.args[0]


  def test_bot_messages_are_ignored(sheets, claude):
      say = MagicMock()
      message = {
          "text": "I am the bot speaking",
          "bot_id": "B001",
          "ts": "123.456",
          "channel": "C003",
      }
      handle_admin_message(message, say, sheets, claude, shop_sergeant_channel="C003")
      claude.answer_admin_query.assert_not_called()


  def test_wrong_channel_is_ignored(sheets, claude):
      say = MagicMock()
      message = {
          "text": "some message",
          "user": "U001",
          "ts": "123.456",
          "channel": "C999",
          "bot_id": None,
      }
      handle_admin_message(message, say, sheets, claude, shop_sergeant_channel="C003")
      claude.answer_admin_query.assert_not_called()
  ```

- [ ] **Step 2: Run tests to verify they fail**

  ```bash
  pytest tests/test_admin.py -v
  ```

  Expected: FAIL with `ImportError`.

- [ ] **Step 3: Write bot/handlers/admin.py**

  ```python
  from slack_bolt import App
  from bot.sheets import SheetsClient
  from bot.claude_client import ClaudeClient
  from bot.config import Config


  def handle_admin_message(message: dict, say, sheets: SheetsClient,
                            claude: ClaudeClient, shop_sergeant_channel: str) -> None:
      if message.get("channel") != shop_sergeant_channel:
          return
      if message.get("bot_id"):
          return
      question = (message.get("text") or "").strip()
      if not question:
          return

      completions = sheets.get_all_completions()
      members = sheets.get_active_members()
      answer = claude.answer_admin_query(question, completions, members)
      say(answer, thread_ts=message["ts"])


  def register(app: App, sheets: SheetsClient, claude: ClaudeClient, config: Config) -> None:
      @app.message()
      def on_admin_message(message, say):
          handle_admin_message(message, say, sheets, claude, config.shop_sergeant_channel)
  ```

- [ ] **Step 4: Run tests to verify they pass**

  ```bash
  pytest tests/test_admin.py -v
  ```

  Expected: 3 PASSED.

- [ ] **Step 5: Commit**

  ```bash
  git add bot/handlers/admin.py tests/test_admin.py
  git commit -m "feat: add natural language admin query handler"
  ```

---

### Task 13: Write scheduler.py (reminders)

**Files:**
- Create: `bot/scheduler.py`

- [ ] **Step 1: Write bot/scheduler.py**

  ```python
  from datetime import datetime
  from apscheduler.schedulers.background import BackgroundScheduler
  from slack_sdk import WebClient


  def start_scheduler(client: WebClient, announcements_channel: str) -> BackgroundScheduler:
      scheduler = BackgroundScheduler()

      def mid_month_reminder() -> None:
          month = datetime.now().strftime("%B")
          client.chat_postMessage(
              channel=announcements_channel,
              text=(
                  f"📋 Halfway through *{month}* — have you logged your volunteer hours? "
                  f"Every member needs 2 hours/month. Sign a task sheet or scan a QR code "
                  f"and tap Send in #task-log."
              ),
          )

      def end_of_month_reminder() -> None:
          month = datetime.now().strftime("%B")
          client.chat_postMessage(
              channel=announcements_channel,
              text=(
                  f"⏰ Only 3 days left to log your *{month}* volunteer hours! "
                  f"Check the sign-up sheets posted around the shop."
              ),
          )

      # 15th of each month at 9:00 AM
      scheduler.add_job(mid_month_reminder, "cron", day=15, hour=9, minute=0,
                        id="mid_month_reminder")
      # 28th of each month at 9:00 AM (~3 days before month end for all months)
      scheduler.add_job(end_of_month_reminder, "cron", day=28, hour=9, minute=0,
                        id="end_of_month_reminder")

      scheduler.start()
      return scheduler
  ```

- [ ] **Step 2: Verify reminders fire manually (spot test)**

  Temporarily change `day=15` to `day="*"` and `minute=0` to `minute="*"` so it fires every minute. Run the bot for 2 minutes and confirm the message appears in `#announcements`. Then revert.

- [ ] **Step 3: Commit**

  ```bash
  git add bot/scheduler.py
  git commit -m "feat: add monthly reminder scheduler (15th and 28th)"
  ```

---

### Task 14: Add email report delivery

**Files:**
- Modify: `bot/config.py` (add email fields)
- Create: `bot/email_client.py`
- Modify: `bot/handlers/admin.py` (trigger email on report requests)

- [ ] **Step 1: Write the failing test**

  ```python
  # tests/test_email_client.py
  import pytest
  from unittest.mock import patch, MagicMock
  from bot.email_client import EmailClient

  def test_send_report_calls_smtp(monkeypatch):
      with patch("bot.email_client.smtplib.SMTP_SSL") as mock_smtp_cls:
          mock_smtp = MagicMock()
          mock_smtp_cls.return_value.__enter__.return_value = mock_smtp
          client = EmailClient(
              smtp_host="smtp.gmail.com",
              smtp_port=465,
              username="bot@example.com",
              password="secret",
              leadership_emails=["leader@makersmiths.org"],
          )
          client.send_report(subject="April Report", body="3 members logged hours.")
          mock_smtp.login.assert_called_once_with("bot@example.com", "secret")
          mock_smtp.sendmail.assert_called_once()
          args = mock_smtp.sendmail.call_args.args
          assert args[0] == "bot@example.com"
          assert "leader@makersmiths.org" in args[1]
  ```

- [ ] **Step 2: Run test to verify it fails**

  ```bash
  pytest tests/test_email_client.py -v
  ```

  Expected: FAIL with `ImportError`.

- [ ] **Step 3: Write bot/email_client.py**

  ```python
  import smtplib
  from email.mime.text import MIMEText
  from email.mime.multipart import MIMEMultipart


  class EmailClient:
      def __init__(self, smtp_host: str, smtp_port: int, username: str,
                   password: str, leadership_emails: list[str]):
          self._host = smtp_host
          self._port = smtp_port
          self._username = username
          self._password = password
          self._to = leadership_emails

      def send_report(self, subject: str, body: str) -> None:
          msg = MIMEMultipart("alternative")
          msg["Subject"] = subject
          msg["From"] = self._username
          msg["To"] = ", ".join(self._to)
          msg.attach(MIMEText(body, "plain"))
          with smtplib.SMTP_SSL(self._host, self._port) as smtp:
              smtp.login(self._username, self._password)
              smtp.sendmail(self._username, self._to, msg.as_string())
  ```

- [ ] **Step 4: Add email fields to Config and load_config**

  In `bot/config.py`, add to the `Config` dataclass:

  ```python
  smtp_host: str
  smtp_port: int
  smtp_username: str
  smtp_password: str
  leadership_emails: list[str]  # comma-separated in env var
  ```

  In `load_config`, add to the `required` list:

  ```python
  "SMTP_HOST", "SMTP_PORT", "SMTP_USERNAME", "SMTP_PASSWORD", "LEADERSHIP_EMAILS"
  ```

  And in the `Config(...)` constructor call:

  ```python
  smtp_host=os.environ["SMTP_HOST"],
  smtp_port=int(os.environ["SMTP_PORT"]),
  smtp_username=os.environ["SMTP_USERNAME"],
  smtp_password=os.environ["SMTP_PASSWORD"],
  leadership_emails=os.environ["LEADERSHIP_EMAILS"].split(","),
  ```

  Add to `.env.example`:

  ```bash
  SMTP_HOST=smtp.gmail.com
  SMTP_PORT=465
  SMTP_USERNAME=shopsgt@makersmiths.org
  SMTP_PASSWORD=your-app-password
  LEADERSHIP_EMAILS=leader1@makersmiths.org,leader2@makersmiths.org
  ```

- [ ] **Step 5: Extend handlers/admin.py to email reports**

  In `bot/app.py`, instantiate `EmailClient` and pass to `admin.register`:

  ```python
  from bot.email_client import EmailClient
  # inside create_app():
  email = EmailClient(
      smtp_host=config.smtp_host,
      smtp_port=config.smtp_port,
      username=config.smtp_username,
      password=config.smtp_password,
      leadership_emails=config.leadership_emails,
  )
  admin.register(app, sheets, claude, email, config)
  ```

  Update `handle_admin_message` signature and add email trigger for report requests:

  ```python
  import re
  from bot.email_client import EmailClient

  REPORT_RE = re.compile(r"\b(generate|create|send|monthly)\b.*\breport\b", re.IGNORECASE)

  def handle_admin_message(message: dict, say, sheets: SheetsClient,
                            claude: ClaudeClient, email: EmailClient,
                            shop_sergeant_channel: str) -> None:
      if message.get("channel") != shop_sergeant_channel:
          return
      if message.get("bot_id"):
          return
      question = (message.get("text") or "").strip()
      if not question:
          return

      completions = sheets.get_all_completions()
      members = sheets.get_active_members()
      answer = claude.answer_admin_query(question, completions, members)
      say(answer, thread_ts=message["ts"])

      if REPORT_RE.search(question):
          from datetime import datetime
          month = datetime.now().strftime("%B %Y")
          email.send_report(
              subject=f"Makersmiths Volunteer Hours — {month}",
              body=answer,
          )
          say("📧 Report also emailed to leadership.", thread_ts=message["ts"])
  ```

  Update `register` to accept `email`:

  ```python
  def register(app: App, sheets: SheetsClient, claude: ClaudeClient,
               email: EmailClient, config: Config) -> None:
      @app.message()
      def on_admin_message(message, say):
          handle_admin_message(message, say, sheets, claude, email, config.shop_sergeant_channel)
  ```

- [ ] **Step 6: Update test_admin.py to pass email mock**

  Add `email = MagicMock()` fixture and pass it to `handle_admin_message` in all existing tests. Add one new test:

  ```python
  def test_report_request_triggers_email(sheets, claude):
      email = MagicMock()
      say = MagicMock()
      message = {
          "text": "Generate monthly report",
          "user": "U001", "ts": "123.456",
          "channel": "C003", "bot_id": None,
      }
      handle_admin_message(message, say, sheets, claude, email, shop_sergeant_channel="C003")
      email.send_report.assert_called_once()
      assert say.call_count == 2  # answer + "emailed to leadership" notice
  ```

- [ ] **Step 7: Run tests to verify they pass**

  ```bash
  pytest tests/test_email_client.py tests/test_admin.py -v
  ```

  Expected: all PASSED.

- [ ] **Step 8: Commit**

  ```bash
  git add bot/email_client.py bot/config.py bot/handlers/admin.py bot/app.py \
          tests/test_email_client.py tests/test_admin.py .env.example
  git commit -m "feat: add email report delivery to leadership on monthly report requests"
  ```

---

### Task 15: Full test suite and integration smoke test

- [ ] **Step 1: Run all unit tests**

  ```bash
  cd /home/jeff/src/projects/makersmiths/shop-sergeant
  pytest tests/ -v
  ```

  Expected: all tests PASS (test_config, test_sheets, test_task_done, test_ocr_parsing, test_ocr, test_admin, test_email_client).

- [ ] **Step 2: Start bot and run end-to-end integration test**

  ```bash
  python3 -m bot.app
  ```

  Run through the full member digital flow:
  1. Generate a test PDF: `python3 scripts/generate-sheets.py MSL-volunteer-opportunities.yaml output/sheets --team-id <T_ID> --channel-id <C_ID>`
  2. Open the PDF, scan a QR code with a phone
  3. Confirm Slack opens with `task-done MSL-XXXX-XXX` pre-filled
  4. Tap Send — confirm bot replies ✅ with correct task name
  5. Open Google Sheet — confirm new row in `task-log` with `source=QR`

  Run through admin OCR flow:
  1. Post a photo from `signup_sheets/` to `#task-intake`
  2. Confirm bot parses and presents action buttons
  3. Click **✅ Confirm All**
  4. Open Google Sheet — confirm rows appear with `source=OCR`

  Run through admin query:
  1. In `#shop-sergeant`, type: `Who has logged hours this month?`
  2. Confirm bot replies with a sensible summary

- [ ] **Step 3: Final commit**

  ```bash
  git add .
  git commit -m "feat: complete shop-sergeant v1 — QR sheets, Slack bot, OCR flow, admin agent"
  ```

---

## Deployment

- [ ] Copy `.env` to server. Set ownership: `chmod 600 .env`.
- [ ] Copy `google-creds.json` to server at path specified in `GOOGLE_CREDENTIALS_FILE`.
- [ ] Install dependencies on server: `pip install -r requirements.txt`.
- [ ] Run as a systemd service:

  ```ini
  # /etc/systemd/system/shop-sergeant.service
  [Unit]
  Description=ShopSergeant Slack Bot
  After=network.target

  [Service]
  User=shop-sergeant
  WorkingDirectory=/opt/shop-sergeant
  EnvironmentFile=/opt/shop-sergeant/.env
  ExecStart=/usr/bin/python3 -m bot.app
  Restart=always
  RestartSec=10

  [Install]
  WantedBy=multi-user.target
  ```

  ```bash
  sudo systemctl enable shop-sergeant
  sudo systemctl start shop-sergeant
  sudo systemctl status shop-sergeant
  ```

---

## Open Questions (from spec)

1. **Slack deep link format on Android vs iOS** — test QR scan on both platforms in Phase 1 before printing sheets at scale.
2. **OCR prompt tuning** — after Phase 3 smoke test, review parsed results against `signup_sheets/` sample images and refine the Claude prompt in `claude_client.ocr_sheet` if accuracy is low.
3. **Multi-completion per task across months** — the append-only log handles this correctly (multiple rows with the same `task_id` are fine). The open question is whether reports should count them separately or deduplicate by month. Decide before Phase 4 report logic.
