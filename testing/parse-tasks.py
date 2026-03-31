#!/usr/bin/env python3
"""
parse_tasks.py

Parses a tasks-list.yaml file and generates a Markdown file where each
location has its own table with columns: Task Name, Completion Date, Frequency.
"""

import yaml
import sys
from pathlib import Path


def parse_yaml(filepath: str) -> dict:
    with open(filepath, "r") as f:
        return yaml.safe_load(f)


def generate_markdown(data: dict) -> str:
    lines = []
    lines.append("# Makersmiths Task List\n")

    shop = data.get("tasks_list", {}).get("shop", {})
    shop_name = shop.get("name", "Unknown Shop")
    shop_address = shop.get("address", "")

    lines.append(f"**Shop:** {shop_name}  ")
    lines.append(f"**Address:** {shop_address}\n")

    areas = shop.get("area", [])

    for area in areas:
        area_name = area.get("name", "Unknown Area")
        lines.append(f"## {area_name}\n")

        locations = area.get("location", [])

        for location in locations:
            loc_name = location.get("name", "Unknown Location")
            steward = location.get("steward", location.get("stward", "???"))  # handle typo in yaml
            tasks = location.get("task", [])

            lines.append(f"### {loc_name}\n")
            lines.append(f"**Steward:** {steward}  \n")

            # Table header
            lines.append("| Task Name | Completion Date | Frequency |")
            lines.append("|-----------|----------------|-----------|")

            if tasks:
                for task in tasks:
                    if isinstance(task, dict):
                        task_name = task.get("name", "???")
                        completion_date = task.get("completion_date", "NA")
                        frequency = task.get("frequency", "NA")
                    else:
                        task_name = str(task)
                        completion_date = "NA"
                        frequency = "NA"

                    # Escape any pipe characters in values
                    task_name = str(task_name).replace("|", "\\|")
                    completion_date = str(completion_date).replace("|", "\\|")
                    frequency = str(frequency).replace("|", "\\|")

                    lines.append(f"| {task_name} | {completion_date} | {frequency} |")
            else:
                lines.append("| ??? | NA | NA |")

            lines.append("")  # blank line after each table

    return "\n".join(lines)


def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/uploads/tasks-list.yaml"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "/mnt/user-data/outputs/tasks-list.md"

    print(f"Parsing: {input_file}")
    data = parse_yaml(input_file)

    print("Generating markdown...")
    markdown = generate_markdown(data)

    Path(output_file).write_text(markdown)
    print(f"Markdown written to: {output_file}")


if __name__ == "__main__":
    main()
