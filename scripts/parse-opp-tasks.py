#!/usr/bin/env python3
"""
parse_opp_tasks.py

Parses a volunteer-opportunity YAML file (e.g. metalshop-volunteer-opportunities.yaml)
and generates a Markdown file where each location has its own table with columns:
Task, Frequency, Purpose, Instructions, Last Date.
"""

import sys
from pathlib import Path

from signup_sheet_builder import load_yaml


def escape(value) -> str:
    """Escape pipe characters so the value is safe inside a Markdown table cell.

    Args:
        value: Any value; converted to str before escaping.

    Returns:
        String with literal '|' replaced by '\\|'.
    """
    return str(value).replace("|", "\\|")


def generate_markdown(data: dict) -> str:
    """Convert parsed opportunities YAML to a Markdown document with per-location tables.

    Each location gets a ### heading and a 5-column table: Task, Frequency,
    Purpose, Instructions, Last Date. Only handles the 'opportunities' root key.

    Args:
        data: Top-level dict parsed from YAML (must contain 'opportunities' key).

    Returns:
        Markdown string with shop header and per-location task tables.
    """
    lines = []
    lines.append("# Makersmiths Volunteer Opportunity Task List\n")

    shop = data.get("opportunities", {}).get("shop", {})
    shop_name = shop.get("name", "Unknown Shop")
    shop_address = shop.get("address", "")
    shop_steward = shop.get("steward", "")

    lines.append(f"**Shop:** {shop_name}  ")
    lines.append(f"**Address:** {shop_address}  ")
    lines.append(f"**Steward:** {shop_steward}\n")

    areas = shop.get("area", [])

    for area in areas:
        area_name = area.get("name", "Unknown Area")
        lines.append(f"## {area_name}\n")

        locations = area.get("location", [])

        for location in locations:
            loc_name = location.get("name", "Unknown Location")
            steward = location.get("steward", "???")
            work_tasks = location.get("work_tasks", [])

            lines.append(f"### {loc_name}\n")
            lines.append(f"**Steward:** {steward}  \n")

            lines.append("| Task | Frequency | Purpose | Instructions | Last Date |")
            lines.append("|------|-----------|---------|--------------|-----------|")

            if work_tasks:
                for task in work_tasks:
                    if isinstance(task, dict):
                        name = escape(task.get("task", "???"))
                        frequency = escape(task.get("frequency", "NA"))
                        purpose = escape(task.get("purpose", "NA"))
                        instructions = escape(task.get("instructions", "NA"))
                        last_date = escape(task.get("last_date", "NA"))
                    else:
                        name = escape(task)
                        frequency = purpose = instructions = last_date = "NA"

                    lines.append(
                        f"| {name} | {frequency} | {purpose} | {instructions} | {last_date} |"
                    )
            else:
                lines.append("| ??? | NA | NA | NA | NA |")

            lines.append("")

    return "\n".join(lines)


def main():
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
