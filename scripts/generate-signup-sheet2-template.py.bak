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
