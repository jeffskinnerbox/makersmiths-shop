#!/usr/bin/env python3
"""parse_tasks.py

Parses a MSL-volunteer-opportunities.yaml file and generates a Markdown file
where each location has its own 3-column table: Task Name, Completion Date,
Frequency.
"""

import sys
from pathlib import Path

from signup_sheet_builder import load_yaml
from markdown_writer import ColumnDef, escape
from markdown_writer import generate_markdown as _generate_markdown_doc

_TITLE = "Makersmiths Task List"

_COLUMNS = [
    ColumnDef("Task Name", lambda t: t.get("task", t.get("name", "???"))),
    ColumnDef("Completion Date", lambda t: t.get("completion_date", "NA")),
    ColumnDef("Frequency", lambda t: t.get("frequency", "NA")),
]


def generate_markdown(data: dict) -> str:
    """Convert parsed YAML data to a Markdown document with per-location tables.

    Handles all supported root-key formats (opportunity, opportunities,
    tasks_list) and delegates table rendering to markdown_writer.

    Args:
        data: Top-level dict parsed from YAML.

    Returns:
        Markdown string with shop header and per-location task tables.
    """
    root = (
        data.get("tasks_list")
        or data.get("opportunities")
        or data.get("opportunity")
        or {}
    )
    shop = root.get("shop", {})
    return _generate_markdown_doc(_TITLE, shop, _COLUMNS)


def main() -> None:
    """Load YAML from argv[1] (or default), generate Markdown, write to argv[2] (or default)."""
    input_file = sys.argv[1] if len(sys.argv) > 1 else "input/MSL-volunteer-opportunities.yaml"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "output/MSL-task-list.md"

    print(f"Parsing: {input_file}")
    data = load_yaml(input_file)

    print("Generating markdown...")
    markdown = generate_markdown(data)

    Path(output_file).write_text(markdown)
    print(f"Markdown written to: {output_file}")


if __name__ == "__main__":
    main()
