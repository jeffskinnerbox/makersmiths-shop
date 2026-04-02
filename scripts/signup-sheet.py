#!/usr/bin/env python3
"""
signup-sheet.py

CLI: Renders a Makersmiths volunteer sign-up sheet HTML from a Jinja2 template + YAML.

Usage:
    python3 scripts/signup-sheet.py \\
        --template output/signup-sheet-template.html.j2 \\
        --yaml input/metalshop-volunteer-opportunity.yaml \\
        --output output/metalshop-signup-sheet.html

Options:
    --location "Metalshop"     Generate a single location only
    --qr-url "https://..."     Override QR placeholder URL
    --logo input/logo.png      Path to logo image
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from signup_sheet import load_yaml, extract_locations, attach_qr_codes, render_sheet


def parse_args():
    p = argparse.ArgumentParser(
        description="Render a Makersmiths sign-up sheet HTML from template + YAML"
    )
    p.add_argument(
        "--template", default="output/signup-sheet-template.html.j2",
        help="Path to Jinja2 .html.j2 template"
    )
    p.add_argument(
        "--yaml", required=True,
        help="Path to YAML task file"
    )
    p.add_argument(
        "--output", default="output/signup-sheet.html",
        help="Output HTML file path"
    )
    p.add_argument(
        "--location", default=None,
        help="Filter to a single location name (default: all)"
    )
    p.add_argument(
        "--qr-url", default="https://makersmiths.org",
        help="URL to encode in QR codes"
    )
    p.add_argument(
        "--logo", default=None,
        help="Path to logo image file"
    )
    return p.parse_args()


def main():
    args = parse_args()

    if not Path(args.template).exists():
        print(f"ERROR: Template not found: {args.template}", file=sys.stderr)
        print("Run signup-sheet-template.py first.", file=sys.stderr)
        sys.exit(1)

    data = load_yaml(args.yaml)
    locations = extract_locations(data)

    if args.location:
        locations = [loc for loc in locations if loc["name"] == args.location]
        if not locations:
            print(f"ERROR: Location '{args.location}' not found in {args.yaml}", file=sys.stderr)
            sys.exit(1)

    if not locations:
        print("ERROR: No locations found in YAML.", file=sys.stderr)
        sys.exit(1)

    locations = attach_qr_codes(locations, args.qr_url)
    html = render_sheet(args.template, locations, logo_path=args.logo)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"Sign-up sheet written to {out}")
    print("Open in browser and use File > Print to save as PDF.")


if __name__ == "__main__":
    main()
