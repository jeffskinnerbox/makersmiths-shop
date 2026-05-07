"""db_table_create — create a SQLite table from a YAML file and load all task records.

The table name defaults to the YAML filename stem (without extension).
Each task row gets a generated UUID as its primary key.

CLI usage:
    python db_table_create.py <db_path> <yaml_file> [--table <name>]

Module usage:
    from db_table_create import db_table_create
    result = db_table_create("msl.db", "MSL-volunteer-opportunities.yaml")
"""

import argparse
import sqlite3
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from db_utils import NA, TASK_FIELDS, new_uuid, print_yaml

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS {table} (
    uuid          TEXT PRIMARY KEY,
    task_id       TEXT,
    task          TEXT,
    time          INTEGER,
    frequency     TEXT,
    purpose       TEXT,
    instructions  TEXT,
    supervision   INTEGER,
    last_date     TEXT,
    location      TEXT,
    area          TEXT,
    shop          TEXT
)
"""

INSERT_SQL = """
INSERT INTO {table}
    (uuid, task_id, task, time, frequency, purpose, instructions,
     supervision, last_date, location, area, shop)
VALUES
    (:uuid, :task_id, :task, :time, :frequency, :purpose, :instructions,
     :supervision, :last_date, :location, :area, :shop)
"""


def _supervision_bool(val: Any) -> int | None:
    """Store supervision as 1/0/NULL so SQLite can handle it."""
    if val is None or val == NA:
        return None
    if isinstance(val, bool):
        return int(val)
    if isinstance(val, str):
        return 1 if val.lower() in ("true", "1", "yes") else 0
    return int(val)


def _na_or(val: Any) -> Any:
    """Return None for NA/missing values so SQLite stores NULL."""
    if val is None or val == NA:
        return None
    return val


def _flatten_tasks(data: dict) -> list[dict[str, Any]]:
    """Walk the nested shop→area→location→work_tasks hierarchy and yield flat rows."""
    rows: list[dict[str, Any]] = []
    shop_node = data.get("opportunities", {}).get("shop", {})
    shop_name: str = shop_node.get("name", NA)

    for area_node in shop_node.get("area", []):
        area_name: str = area_node.get("name", NA)
        for loc_node in area_node.get("location", []):
            loc_name: str = loc_node.get("name", NA)
            for task in loc_node.get("work_tasks", []):
                rows.append(
                    {
                        "uuid": new_uuid(),
                        "task_id": _na_or(task.get("task_id")),
                        "task": _na_or(task.get("task")),
                        "time": _na_or(task.get("time")),
                        "frequency": _na_or(task.get("frequency")),
                        "purpose": _na_or(task.get("purpose")),
                        "instructions": _na_or(task.get("instructions")),
                        "supervision": _supervision_bool(task.get("supervision")),
                        "last_date": _na_or(task.get("last_date")),
                        "location": loc_name,
                        "area": area_name,
                        "shop": shop_name,
                    }
                )
    return rows


def db_table_create(
    db_path: str,
    yaml_file: str,
    table: str | None = None,
) -> dict[str, Any]:
    yaml_path = Path(yaml_file)
    if not yaml_path.exists():
        return {"status": "error", "message": f"YAML file not found: {yaml_file}"}

    db = Path(db_path)
    if not db.exists():
        return {"status": "error", "message": f"database not found: {db_path}"}

    table_name = table or yaml_path.stem
    # Sanitize table name: keep only alphanumeric and underscores.
    safe_table = "".join(c if c.isalnum() or c == "_" else "_" for c in table_name)

    with open(yaml_path) as fh:
        data = yaml.safe_load(fh)

    rows = _flatten_tasks(data)

    conn = sqlite3.connect(str(db))
    try:
        conn.execute(CREATE_SQL.format(table=safe_table))
        conn.executemany(INSERT_SQL.format(table=safe_table), rows)
        conn.commit()
    finally:
        conn.close()

    return {
        "status": "ok",
        "table": safe_table,
        "rows_loaded": len(rows),
        "db_path": str(db.resolve()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a SQLite table from a YAML file and load all task records."
    )
    parser.add_argument("db_path", help="Path to the SQLite database")
    parser.add_argument("yaml_file", help="Path to the volunteer opportunities YAML file")
    parser.add_argument(
        "--table",
        default=None,
        help="Table name override (default: YAML filename stem)",
    )
    args = parser.parse_args()
    result = db_table_create(args.db_path, args.yaml_file, table=args.table)
    print_yaml(result)
    if result["status"] == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
