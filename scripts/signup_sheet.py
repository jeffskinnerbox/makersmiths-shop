#!/usr/bin/env python3
"""
signup_sheet.py

Core library for Makersmiths sign-up sheet generation.
Provides YAML parsing, QR code generation, and HTML rendering functions.
Imported by signup-sheet.py (CLI) and tests.
"""

import base64
import io
from pathlib import Path

import qrcode
import yaml
from jinja2 import Environment, FileSystemLoader


def load_yaml(source) -> dict:
    """Load YAML from a file path (str/Path) or an open file object (e.g. sys.stdin)."""
    if hasattr(source, "read"):
        return yaml.safe_load(source)
    with open(source, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def detect_format(data: dict) -> str:
    """Return the root key used to access shop data."""
    for key in ("opportunity", "opportunities", "tasks_list"):
        if key in data:
            return key
    raise ValueError(
        f"Unknown YAML format: root key must be 'opportunity', 'opportunities', or 'tasks_list', "
        f"got: {list(data.keys())}"
    )


def _is_real_task(t) -> bool:
    """Return True if t is a real task (not a TBD placeholder)."""
    if isinstance(t, dict):
        return t.get("task", "").strip().upper() != "TBD" and t.get("task", "").strip() != ""
    return str(t).strip().upper() != "TBD" and str(t).strip() != ""


def extract_locations(data: dict, skip_tbd: bool = True) -> list:
    """
    Return list of location dicts from YAML data.
    Each dict: {'name': str, 'steward': str, 'tasks': [{'name', 'task_id', 'frequency'}]}

    When skip_tbd=True (default), locations with no real tasks (empty or all-TBD) are omitted.
    """
    fmt = detect_format(data)
    shop = data[fmt]["shop"]

    locations = []
    for area in shop.get("area", []):
        for loc in area.get("location", []):
            raw_tasks = loc.get("work_tasks", loc.get("task", [])) or []

            # Skip locations with no real task data
            if skip_tbd and not any(_is_real_task(t) for t in raw_tasks):
                continue

            tasks = []
            for t in raw_tasks:
                if not _is_real_task(t):
                    continue
                if isinstance(t, dict):
                    instructions = t.get("instructions", "")
                    tasks.append({
                        "name": t.get("task", "???"),
                        "task_id": t.get("task_id") or "NA",
                        "frequency": t.get("frequency", "NA"),
                        "last_date": t.get("last_date") or "NA",
                        "instructions": "" if (not instructions or str(instructions).strip().upper() == "NA") else str(instructions).strip(),
                    })
                else:
                    tasks.append({"name": str(t), "task_id": "NA", "frequency": "NA", "last_date": "NA", "instructions": ""})

            locations.append({
                "name": loc.get("name", "???"),
                "steward": loc.get("steward", loc.get("stward", "???")),
                "tasks": tasks,
            })
    return locations


def make_qr_b64(url: str) -> str:
    """Generate QR code for url, return as base64-encoded PNG string."""
    img = qrcode.make(url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def attach_qr_codes(locations: list, qr_url: str) -> list:
    """Add qr_b64 field to every task. All tasks share the same placeholder URL."""
    qr_b64 = make_qr_b64(qr_url)
    for loc in locations:
        for task in loc["tasks"]:
            task["qr_b64"] = qr_b64
    return locations


def _logo_data_uri(logo_path: str) -> str | None:
    """Return a base64 data URI for the logo image, or None if not found."""
    p = Path(logo_path)
    if not p.exists():
        return None
    suffix = p.suffix.lower().lstrip(".")
    mime = "jpeg" if suffix in ("jpg", "jpeg") else suffix
    data = base64.b64encode(p.read_bytes()).decode("utf-8")
    return f"data:image/{mime};base64,{data}"


def render_sheet(template_path: str, locations: list, logo_path: str | None) -> str:
    """Render the Jinja2 template with location/task data."""
    tmpl_file = Path(template_path)
    env = Environment(
        loader=FileSystemLoader(str(tmpl_file.parent)),
        autoescape=False,
    )
    template = env.get_template(tmpl_file.name)
    logo_uri = _logo_data_uri(logo_path) if logo_path else None
    return template.render(locations=locations, logo_path=logo_uri)
