#!/usr/bin/env python3
"""parse_opp_tasks.py

Parses a volunteer-opportunity YAML file (e.g. metalshop-volunteer-opportunities.yaml)
and generates a Markdown file where each location has its own 5-column table:
Task, Frequency, Purpose, Instructions, Last Date.
"""

import sys
from pathlib import Path

from signup_sheet_builder import load_yaml
from markdown_writer import ColumnDef, escape
from markdown_writer import generate_markdown as _generate_markdown_doc

_TITLE = "Makersmiths Volunteer Opportunity Task List"

_COLUMNS = [
    ColumnDef("Task", lambda t: t.get("task", "???")),
    ColumnDef("Frequency", lambda t: t.get("frequency", "NA")),
    ColumnDef("Purpose", lambda t: t.get("purpose", "NA")),
    ColumnDef("Instructions", lambda t: t.get("instructions", "NA")),
    ColumnDef("Last Date", lambda t: t.get("last_date", "NA")),
]


def generate_markdown(data: dict) -> str:
    """Convert parsed opportunities YAML to a Markdown document with per-location tables.

    Only handles the 'opportunities' root key. Delegates table rendering to
    markdown_writer with a shop-level steward metadata line.

    Args:
        data: Top-level dict parsed from YAML (must contain 'opportunities' key).

    Returns:
        Markdown string with shop header and per-location task tables.
    """
    shop = data.get("opportunities", {}).get("shop", {})
    shop_steward = shop.get("steward", "")
    extra_meta = [f"**Steward:** {shop_steward}"]
    return _generate_markdown_doc(_TITLE, shop, _COLUMNS, extra_meta=extra_meta)


def main() -> None:
    """Load YAML from argv[1] (or default), generate Markdown, write to argv[2] (or default)."""
    input_file = (
        sys.argv[1] if len(sys.argv) > 1 else "metalshop-volunteer-opportunities.yaml"
    )
    output_file = sys.argv[2] if len(sys.argv) > 2 else "metalshop-task-list.md"

    print(f"Parsing: {input_file}")
    data = load_yaml(input_file)

    print("Generating markdown...")
    markdown = generate_markdown(data)

    Path(output_file).write_text(markdown)
    print(f"Markdown written to: {output_file}")


if __name__ == "__main__":
    main()
