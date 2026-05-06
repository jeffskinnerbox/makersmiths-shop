#!/usr/bin/env python3
"""
signup-sheet.py

CLI: Renders a Makersmiths volunteer sign-up sheet HTML from a Jinja2 template + YAML.

Usage:
    # stdin → stdout (pipeline-friendly)
    cat input/metalshop-volunteer-opportunity.yaml | python3 scripts/signup-sheet.py

    # file → file
    python3 scripts/signup-sheet.py \\
        --input input/metalshop-volunteer-opportunity.yaml \\
        --output output/metalshop-signup-sheet.html

Options:
    --template output/...      Jinja2 template path
    --location "Metalshop"     Generate a single location only
    --qr-url "https://..."     Override QR placeholder URL
    --logo input/logo.png      Path to logo image
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from signup_sheet_builder import load_yaml, extract_locations, attach_qr_codes, render_sheet

DEFAULT_QR_URL = "https://makersmiths.org"
DEFAULT_LOGO = "input/makersmiths-logo.png"


def parse_args() -> argparse.Namespace:
    """Parse and return CLI arguments for the sign-up sheet renderer."""
    p = argparse.ArgumentParser(
        description="Render a Makersmiths sign-up sheet HTML from template + YAML"
    )
    p.add_argument(
        "-t", "--template", default="output/signup-sheet-template.html.j2",
        help="Path to Jinja2 .html.j2 template"
    )
    p.add_argument(
        "-i", "--input", "--yaml", default=None, dest="input",
        help="Path to YAML task file (default: stdin)"
    )
    p.add_argument(
        "-o", "--output", default=None,
        help="Output HTML file path (default: stdout)"
    )
    p.add_argument(
        "-l", "--location", default=None,
        help="Filter to a single location name (default: all)"
    )
    p.add_argument(
        "-q", "--qr-url", default=DEFAULT_QR_URL,
        help="URL to encode in QR codes"
    )
    p.add_argument(
        "-a", "--logo", default=DEFAULT_LOGO,
        help=f"Path to logo image file (default: {DEFAULT_LOGO})"
    )
    return p.parse_args()


def main() -> None:
    """Load YAML, filter locations, attach QR codes, render HTML, and write output."""
    args = parse_args()

    if not Path(args.template).exists():
        print(f"ERROR: Template not found: {args.template}", file=sys.stderr)
        print("Run generate-signup-sheet-template.py first.", file=sys.stderr)
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

    locations = attach_qr_codes(locations, args.qr_url)
    html = render_sheet(args.template, locations, logo_path=args.logo)

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
