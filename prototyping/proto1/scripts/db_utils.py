"""Shared utilities: DB connections, YAML output, UUID generation."""

import sqlite3
import sys
import uuid
from pathlib import Path
from typing import Any

import yaml


# Fields every task row carries; sparse YAML rows are filled with NA.
TASK_FIELDS: list[str] = [
    "uuid",
    "task_id",
    "task",
    "time",
    "frequency",
    "purpose",
    "instructions",
    "supervision",
    "last_date",
    "location",
    "area",
    "shop",
]

NA = "NA"


def get_connection(db_path: str) -> sqlite3.Connection:
    """Return a SQLite connection with row_factory set."""
    path = Path(db_path)
    if not path.exists():
        print(f"error: database not found: {db_path}", file=sys.stderr)
        sys.exit(1)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    # Enable regex support via Python's re module.
    conn.create_function("REGEXP", 2, _regexp)
    return conn


def _regexp(pattern: str, value: Any) -> bool:
    import re
    if value is None:
        return False
    try:
        return bool(re.search(pattern, str(value), re.IGNORECASE))
    except re.error:
        return False


def new_uuid() -> str:
    return str(uuid.uuid4())


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(zip(row.keys(), tuple(row)))


def to_yaml(data: Any) -> str:
    return yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)


def print_yaml(data: Any) -> None:
    print(to_yaml(data), end="")


def coerce_value(field: str, raw: str) -> Any:
    """Convert a CLI string value to the appropriate Python type for the field."""
    if raw == NA:
        return None
    if field == "time":
        try:
            return int(raw)
        except ValueError:
            print(f"error: 'time' must be an integer, got '{raw}'", file=sys.stderr)
            sys.exit(1)
    if field == "supervision":
        if raw.lower() in ("true", "1", "yes"):
            return True
        if raw.lower() in ("false", "0", "no"):
            return False
        print(f"error: 'supervision' must be true/false, got '{raw}'", file=sys.stderr)
        sys.exit(1)
    return raw
