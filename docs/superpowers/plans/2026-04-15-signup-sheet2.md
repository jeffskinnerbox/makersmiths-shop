# signup-sheet2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create an alternative volunteer sign-up sheet with a single page-level QR code in a 4-zone header and 4 sign-off columns instead of per-task QR codes.

**Architecture:** Two new scripts mirror the v1 pair: `generate-signup-sheet2-template.py` bakes CSS/text into a Jinja2 template file, and `signup-sheet2.py` renders HTML from that template + YAML. A single QR code is generated once and passed as a top-level template variable `qr_b64`. No changes to `signup_sheet_builder.py`.

**Tech Stack:** Python 3.11+, Jinja2, qrcode[pil], PyYAML (all already installed)

---

## File Map

| Action | Path | Responsibility |
|---|---|---|
| Create | `scripts/generate-signup-sheet2-template.py` | Generates `output/signup-sheet2-template.html.j2` |
| Create | `scripts/signup-sheet2.py` | Renders HTML from template + YAML; single QR |
| Generated | `output/signup-sheet2-template.html.j2` | Jinja2 template produced by generator |
| Generated | `output/metalshop-signup-sheet2.html` | Final rendered output for visual review |

No files modified. No test files (Phase 0 pattern — visual review only).

---

## Task 1: Write `generate-signup-sheet2-template.py`

**Files:**
- Create: `scripts/generate-signup-sheet2-template.py`

- [ ] **Step 1: Create `scripts/generate-signup-sheet2-template.py`**

```python
#!/usr/bin/env python3
"""Generate a Jinja2 HTML template for volunteer sign-up sheets (v2 — single QR header)."""

import argparse
import sys
from pathlib import Path

DEFAULT_LOCATION_FONT_SIZE = 12
DEFAULT_STEWARD_FONT_SIZE = 10
DEFAULT_TITLE_FONT_SIZE = 30
DEFAULT_FOOTER_FONT_SIZE = 8
DEFAULT_TITLE = "Volunteer Opportunities"
DEFAULT_FOOTER = (
    "Questions concerning the design & use of this form should be sent to Jeff Irland (xxx)"
)

TEMPLATE_BODY = r"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title></title>
<style>
  @page {{ size: 11in 8.5in landscape; margin: 0.5in; }}
  body {{ font-family: Arial, sans-serif; margin: 0; }}
  .location {{ font-size: {location_font_size}pt; font-weight: bold; }}
  .steward {{ font-size: {steward_font_size}pt; font-weight: bold; }}
  .title {{ font-size: {title_font_size}pt; font-weight: bold; color: red; }}
  .footer {{ font-size: {footer_font_size}pt; font-weight: bold; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th, td {{ border: 1px solid #888; padding: 1px 6px; line-height: 1.2; }}
  th {{ background-color: #ddd; }}
  .col-task {{ width: 46%; }}
  .col-last-done {{ width: 10%; text-align: center; }}
  .col-freq {{ width: 8%; text-align: center; }}
  .col-member-date {{ width: 9%; }}
  .page {{ box-sizing: border-box; width: 100%; min-height: 7.5in; outline: 0.25in solid red; outline-offset: -0.25in; }}
</style>
</head>
<body>
{{% for location in locations %}}
<div class="page" style="page-break-after: always; padding: 0.3in;">
  <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #333; padding-bottom:4px; margin-bottom:6px;">
    <div style="flex:0 0 90px; text-align:center;">
      {{% if qr_b64 %}}
        <img src="data:image/png;base64,{{{{ qr_b64 }}}}" width="80" height="80" alt="QR">
      {{% endif %}}
    </div>
    <div>
      <div class="location">Location: {{{{ location.name }}}}</div>
      <div class="steward">Steward: {{{{ location.steward }}}}</div>
    </div>
    <div style="text-align:center;">
      <div class="title">{title}</div>
    </div>
    <div style="text-align:right;">
      {{% if logo_path %}}
        <img src="{{{{ logo_path }}}}" alt="Makersmiths" style="height:55px;">
      {{% else %}}
        <strong style="font-size:14pt;">Makersmiths</strong>
      {{% endif %}}
    </div>
  </div>
  <table>
    <thead>
      <tr>
        <th class="col-task">Task Name</th>
        <th class="col-last-done">Last Done</th>
        <th class="col-freq">Frequency</th>
        <th class="col-member-date">Member Name / Date</th>
        <th class="col-member-date">Member Name / Date</th>
        <th class="col-member-date">Member Name / Date</th>
        <th class="col-member-date">Member Name / Date</th>
      </tr>
    </thead>
    <tbody>
      {{% for task in location.tasks %}}
      <tr>
        <td class="col-task" style="position:relative;"><span style="color:red; font-weight:bold;">{{{{ task.name }}}}</span>{{% if task.instructions %}}<br><span style="font-size:8pt; font-weight:normal;">{{{{ task.instructions }}}}</span>{{% endif %}}{{% if task.task_id %}}<div style="position:absolute; bottom:1px; left:6px; font-size:8pt; font-weight:normal;">{{{{ task.task_id }}}}</div>{{% endif %}}</td>
        <td class="col-last-done">{{{{ task.last_date }}}}</td>
        <td class="col-freq">{{{{ task.frequency }}}}</td>
        <td class="col-member-date">&nbsp;</td>
        <td class="col-member-date">&nbsp;</td>
        <td class="col-member-date">&nbsp;</td>
        <td class="col-member-date">&nbsp;</td>
      </tr>
      {{% endfor %}}
    </tbody>
  </table>
  <div class="footer" style="margin-top:6px; border-top:1px solid #ccc; padding-top:3px; text-align:center;">{footer}</div>
</div>
{{% endfor %}}
</body>
</html>
"""


def build_template(
    title: str,
    footer: str,
    location_font_size: int,
    steward_font_size: int,
    title_font_size: int,
    footer_font_size: int,
) -> str:
    """Return the Jinja2 template string with CSS values and static text baked in."""
    return TEMPLATE_BODY.format(
        title=title,
        location_font_size=location_font_size,
        steward_font_size=steward_font_size,
        title_font_size=title_font_size,
        footer_font_size=footer_font_size,
        footer=footer,
    )


def main() -> None:
    """Parse CLI args, build the Jinja2 template, and write it to a file or stdout."""
    parser = argparse.ArgumentParser(
        description="Generate a Jinja2 HTML template for volunteer sign-up sheets (v2)."
    )
    parser.add_argument("-o", "--output", default=None, help="Output file path (default: stdout)")
    parser.add_argument("-t", "--title", default=DEFAULT_TITLE, help=f"Sheet title (default: {DEFAULT_TITLE})")
    parser.add_argument("-f", "--footer", default=DEFAULT_FOOTER, help="Footer text")
    parser.add_argument("-l", "--location-font-size", type=int, default=DEFAULT_LOCATION_FONT_SIZE, dest="location_font_size", help="Location header font size in pt (default: 12)")
    parser.add_argument("-s", "--steward-font-size", type=int, default=DEFAULT_STEWARD_FONT_SIZE, dest="steward_font_size", help="Steward line font size in pt (default: 10)")
    parser.add_argument("-a", "--title-font-size", type=int, default=DEFAULT_TITLE_FONT_SIZE, dest="title_font_size", help="Title font size in pt (default: 30)")
    parser.add_argument("-b", "--footer-font-size", type=int, default=DEFAULT_FOOTER_FONT_SIZE, dest="footer_font_size", help="Footer font size in pt (default: 8)")
    args = parser.parse_args()

    content = build_template(
        title=args.title,
        footer=args.footer,
        location_font_size=args.location_font_size,
        steward_font_size=args.steward_font_size,
        title_font_size=args.title_font_size,
        footer_font_size=args.footer_font_size,
    )

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        print(f"Template written to {out_path}", file=sys.stderr)
    else:
        sys.stdout.write(content)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
git add scripts/generate-signup-sheet2-template.py
git commit -m "feat: add generate-signup-sheet2-template.py (single QR header)"
```

---

## Task 2: Run the generator to produce the template file

**Files:**
- Generated: `output/signup-sheet2-template.html.j2`

- [ ] **Step 1: Run the generator**

```bash
python3 scripts/generate-signup-sheet2-template.py \
    --output output/signup-sheet2-template.html.j2
```

Expected stderr: `Template written to output/signup-sheet2-template.html.j2`

- [ ] **Step 2: Verify the template contains the expected Jinja2 markers**

```bash
grep -c "qr_b64" output/signup-sheet2-template.html.j2
```

Expected: `2` (one in the `{% if qr_b64 %}` check, one in the `<img>` src)

```bash
grep -c "col-member-date" output/signup-sheet2-template.html.j2
```

Expected: `9` (1 CSS rule + 4 `<th>` elements + 4 `<td>` elements)

```bash
grep "col-qr" output/signup-sheet2-template.html.j2
```

Expected: no output (the QR column is gone from the table)

- [ ] **Step 3: Commit the generated template**

```bash
git add output/signup-sheet2-template.html.j2
git commit -m "feat: generate signup-sheet2 Jinja2 template"
```

---

## Task 3: Write `signup-sheet2.py`

**Files:**
- Create: `scripts/signup-sheet2.py`

- [ ] **Step 1: Create `scripts/signup-sheet2.py`**

```python
#!/usr/bin/env python3
"""
signup-sheet2.py

CLI: Renders a Makersmiths volunteer sign-up sheet HTML (v2 — single QR in header).

Differences from signup-sheet.py:
  - One QR code per page (in header, top-left zone) instead of one per task row.
  - Table has 4 sign-off columns instead of 3; no QR column.
  - Template variable `qr_b64` is top-level (not per-task).

Usage:
    # Generate the template first (run once):
    python3 scripts/generate-signup-sheet2-template.py \
        --output output/signup-sheet2-template.html.j2

    # Render:
    python3 scripts/signup-sheet2.py \
        --template output/signup-sheet2-template.html.j2 \
        --yaml input/metalshop-volunteer-opportunities.yaml \
        --output output/metalshop-signup-sheet2.html
"""

import argparse
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

sys.path.insert(0, str(Path(__file__).parent))
from signup_sheet_builder import load_yaml, extract_locations, make_qr_b64, _logo_data_uri

DEFAULT_QR_URL = "https://makersmiths.org"
DEFAULT_LOGO = "input/makersmiths-logo.png"
DEFAULT_TEMPLATE = "output/signup-sheet2-template.html.j2"


def parse_args() -> argparse.Namespace:
    """Parse and return CLI arguments for the sign-up sheet v2 renderer."""
    p = argparse.ArgumentParser(
        description="Render a Makersmiths sign-up sheet HTML (v2 — single QR in header)"
    )
    p.add_argument("-t", "--template", default=DEFAULT_TEMPLATE, help="Path to Jinja2 .html.j2 template")
    p.add_argument("-i", "--input", "--yaml", default=None, dest="input", help="Path to YAML task file (default: stdin)")
    p.add_argument("-o", "--output", default=None, help="Output HTML file path (default: stdout)")
    p.add_argument("-l", "--location", default=None, help="Filter to a single location name (default: all)")
    p.add_argument("-q", "--qr-url", default=DEFAULT_QR_URL, help="URL to encode in the single page QR code")
    p.add_argument("-a", "--logo", default=DEFAULT_LOGO, help=f"Path to logo image file (default: {DEFAULT_LOGO})")
    return p.parse_args()


def render_sheet2(template_path: str, locations: list, logo_path: str | None, qr_b64: str | None) -> str:
    """Render the v2 Jinja2 template with location data and a single QR code."""
    tmpl_file = Path(template_path)
    env = Environment(loader=FileSystemLoader(str(tmpl_file.parent)), autoescape=False)
    template = env.get_template(tmpl_file.name)
    logo_uri = _logo_data_uri(logo_path) if logo_path else None
    return template.render(locations=locations, logo_path=logo_uri, qr_b64=qr_b64)


def main() -> None:
    """Load YAML, filter locations, generate one QR, render HTML, and write output."""
    args = parse_args()

    if not Path(args.template).exists():
        print(f"ERROR: Template not found: {args.template}", file=sys.stderr)
        print("Run generate-signup-sheet2-template.py first.", file=sys.stderr)
        sys.exit(1)

    source = args.input if args.input else sys.stdin
    data = load_yaml(source)
    locations = extract_locations(data)

    if args.location:
        locations = [loc for loc in locations if loc["name"] == args.location]
        if not locations:
            print(f"ERROR: Location '{args.location}' not found.", file=sys.stderr)
            sys.exit(1)

    if not locations:
        print("ERROR: No locations found in YAML.", file=sys.stderr)
        sys.exit(1)

    qr_b64 = make_qr_b64(args.qr_url)
    html = render_sheet2(args.template, locations, logo_path=args.logo, qr_b64=qr_b64)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        print(f"Sign-up sheet written to {out}", file=sys.stderr)
        print("Open in browser and use File > Print to save as PDF.", file=sys.stderr)
    else:
        sys.stdout.write(html)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
git add scripts/signup-sheet2.py
git commit -m "feat: add signup-sheet2.py renderer (single QR in header)"
```

---

## Task 4: Render and visually verify the output

**Files:**
- Generated: `output/metalshop-signup-sheet2.html`

- [ ] **Step 1: Render against the metalshop YAML**

```bash
python3 scripts/signup-sheet2.py \
    --template output/signup-sheet2-template.html.j2 \
    --yaml input/metalshop-volunteer-opportunities.yaml \
    --output output/metalshop-signup-sheet2.html
```

Expected stderr:
```
Sign-up sheet written to output/metalshop-signup-sheet2.html
Open in browser and use File > Print to save as PDF.
```

- [ ] **Step 2: Open in browser and verify visually**

```bash
xdg-open output/metalshop-signup-sheet2.html
```

Check:
- Header has 4 zones left-to-right: QR image (~80px) | Location + Steward | "Volunteer Opportunities" title | Makersmiths logo
- Table has 4 "Member Name / Date" sign-off columns (no QR column)
- Each task row shows task name, last-done date, frequency, 4 blank sign-off cells
- Red page-border outline visible (0.25in inset)
- Footer text at bottom of each page

- [ ] **Step 3: Commit the rendered output**

```bash
git add output/metalshop-signup-sheet2.html
git commit -m "feat: add rendered metalshop signup-sheet2 HTML for review"
```
