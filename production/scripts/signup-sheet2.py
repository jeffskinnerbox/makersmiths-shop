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
