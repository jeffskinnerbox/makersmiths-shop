"""Library module: Jinja2 HTML template builder for volunteer sign-up sheets."""

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
  .col-task {{ width: 48%; }}
  .col-last-done {{ width: 10%; text-align: center; }}
  .col-freq {{ width: 8%; text-align: center; }}
  .col-member-date {{ width: 8%; }}
  .col-qr {{ width: 85px; text-align: center; padding: 2px; }}
  .page {{ box-sizing: border-box; width: 100%; min-height: 7.5in; outline: 0.25in solid red; outline-offset: -0.25in; }}
</style>
</head>
<body>
{{% for location in locations %}}
<div class="page" style="page-break-after: always; padding: 0.3in;">
  <div style="display:flex; justify-content:space-between; border-bottom:2px solid #333; padding-bottom:4px; margin-bottom:6px;">
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
        <th class="col-qr">Log It (QR)</th>
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
        <td class="col-qr">
          {{% if task.qr_b64 %}}
            <img src="data:image/png;base64,{{{{ task.qr_b64 }}}}" width="75" height="75" alt="QR">
          {{% endif %}}
        </td>
      </tr>
      {{% endfor %}}
    </tbody>
  </table>
  <div class="footer" style="margin-top:6px; border-top:1px solid #ccc; padding-top:3px;">{footer}</div>
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
    """Return the rendered Jinja2 template string with CSS/layout values baked in."""
    return TEMPLATE_BODY.format(
        title=title,
        location_font_size=location_font_size,
        steward_font_size=steward_font_size,
        title_font_size=title_font_size,
        footer_font_size=footer_font_size,
        footer=footer,
    )
