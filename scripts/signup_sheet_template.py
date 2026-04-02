"""Library module: Jinja2 HTML template builder for volunteer sign-up sheets."""

TEMPLATE_BODY = r"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8">
<style>
  @page {{ size: 11in 8.5in landscape; margin: 0.5in; }}
  body {{ font-family: Arial, sans-serif; }}
  .location {{ font-size: {location_font_size}pt; font-weight: bold; }}
  .steward {{ font-size: {steward_font_size}pt; font-weight: bold; }}
  .title {{ font-size: {title_font_size}pt; font-weight: bold; color: red; }}
  .footer {{ font-size: {footer_font_size}pt; font-weight: bold; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th, td {{ border: 1px solid #888; padding: 4px 6px; }}
  th {{ background-color: #ddd; }}
  .col-task {{ width: 38%; }}
  .col-freq {{ width: 10%; }}
  .col-member {{ width: 30%; }}
  .col-date {{ width: 12%; }}
  .col-qr {{ width: 60px; text-align: center; }}
</style>
</head>
<body>
{{% for location in locations %}}
<div class="page" style="page-break-after: always;">
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
        <th class="col-freq">Frequency</th>
        <th class="col-member">Member (sign)</th>
        <th class="col-date">Date</th>
        <th class="col-qr">Log It (QR)</th>
      </tr>
    </thead>
    <tbody>
      {{% for task in location.tasks %}}
      <tr>
        <td class="col-task">{{{{ task.name }}}}</td>
        <td class="col-freq">{{{{ task.frequency }}}}</td>
        <td class="col-member">&nbsp;</td>
        <td class="col-date">&nbsp;</td>
        <td class="col-qr">
          {{% if task.qr_b64 %}}
            <img src="data:image/png;base64,{{{{ task.qr_b64 }}}}" width="50" height="50" alt="QR">
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


def build_template(args) -> str:
    """Return the rendered Jinja2 template string with CSS/layout values baked in."""
    return TEMPLATE_BODY.format(
        title=args.title,
        location_font_size=args.location_font_size,
        steward_font_size=args.steward_font_size,
        title_font_size=args.title_font_size,
        footer_font_size=args.footer_font_size,
        footer=args.footer,
    )
