"""scripts/markdown_writer.py

Shared markdown generation logic for parse-tasks.py and parse-opp-tasks.py.
Both scripts produce per-location task tables but differ in title, column
definitions, and shop-level metadata. This library handles the common loop.
"""
from dataclasses import dataclass
from typing import Callable


def escape(value) -> str:
    """Escape pipe characters so the value is safe inside a Markdown table cell.

    Args:
        value: Any value; converted to str before escaping.

    Returns:
        String with literal '|' replaced by '\\|'.
    """
    return str(value).replace("|", "\\|")


@dataclass
class ColumnDef:
    """Defines one column in a per-location task table.

    Attributes:
        header: Column header text (e.g. 'Task Name').
        extractor: Called with a task dict; returns the raw cell value.
    """
    header: str
    extractor: Callable[[dict], str]


def generate_markdown(
    title: str,
    shop: dict,
    columns: list,
    extra_meta: list = None,
) -> str:
    """Generate a Markdown document with per-location task tables.

    Args:
        title: Document H1 heading (without leading '#').
        shop: Shop dict containing 'name', 'address', 'area' keys.
        columns: Ordered list of ColumnDef instances defining the table.
        extra_meta: Optional extra '**Key:** value' lines appended after the
            address line (e.g. ['**Steward:** Alice  ']).

    Returns:
        Markdown string with shop header followed by area/location sections.
    """
    if extra_meta is None:
        extra_meta = []

    lines = [f"# {title}\n"]

    shop_name = shop.get("name", "Unknown Shop")
    shop_address = shop.get("address", "")
    lines.append(f"**Shop:** {shop_name}  ")
    lines.append(f"**Address:** {shop_address}  ")
    lines.extend(extra_meta)
    lines.append("")

    header_row = "| " + " | ".join(col.header for col in columns) + " |"
    separator = "|" + "|".join("-" * (len(col.header) + 2) for col in columns) + "|"
    empty_row = "| ??? |" + " NA |" * (len(columns) - 1)

    for area in shop.get("area", []):
        area_name = area.get("name", "Unknown Area")
        lines.append(f"## {area_name}\n")

        for location in area.get("location", []):
            loc_name = location.get("name", "Unknown Location")
            steward = location.get("steward", "???")
            tasks = location.get("work_tasks", location.get("task", []))

            lines.append(f"### {loc_name}\n")
            lines.append(f"**Steward:** {steward}  \n")
            lines.append(header_row)
            lines.append(separator)

            if tasks:
                for task in tasks:
                    # Normalise plain string tasks to a dict so extractors work uniformly.
                    task_dict = task if isinstance(task, dict) else {"task": str(task)}
                    cells = [escape(col.extractor(task_dict)) for col in columns]
                    lines.append("| " + " | ".join(cells) + " |")
            else:
                lines.append(empty_row)

            lines.append("")

    return "\n".join(lines)
