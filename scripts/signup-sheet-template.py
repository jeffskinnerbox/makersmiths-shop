#!/usr/bin/env python3
"""CLI entry point: generate a Jinja2 HTML template for volunteer sign-up sheets."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from signup_sheet_template import build_template  # noqa: E402


def main():
    parser = argparse.ArgumentParser(
        description="Generate a Jinja2 HTML template for volunteer sign-up sheets."
    )
    parser.add_argument(
        "--output",
        default="output/signup-sheet-template.html.j2",
        help="Output file path (default: output/signup-sheet-template.html.j2)",
    )
    parser.add_argument(
        "--title",
        default="Volunteer Opportunities",
        help="Sheet title (default: Volunteer Opportunities)",
    )
    parser.add_argument(
        "--location-font-size",
        type=int,
        default=12,
        dest="location_font_size",
        help="Location header font size in pt (default: 12)",
    )
    parser.add_argument(
        "--steward-font-size",
        type=int,
        default=10,
        dest="steward_font_size",
        help="Steward line font size in pt (default: 10)",
    )
    parser.add_argument(
        "--title-font-size",
        type=int,
        default=20,
        dest="title_font_size",
        help="Title font size in pt (default: 14)",
    )
    parser.add_argument(
        "--footer-font-size",
        type=int,
        default=8,
        dest="footer_font_size",
        help="Footer font size in pt (default: 8)",
    )
    parser.add_argument(
        "--footer",
        default="Questions concerning the design & use of this form should be sent to Jeff Irland (xxx)",
        help="Footer text",
    )

    args = parser.parse_args()
    content = build_template(
        title=args.title,
        footer=args.footer,
        location_font_size=args.location_font_size,
        steward_font_size=args.steward_font_size,
        title_font_size=args.title_font_size,
        footer_font_size=args.footer_font_size,
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    print(f"Template written to {out_path}")


if __name__ == "__main__":
    main()
