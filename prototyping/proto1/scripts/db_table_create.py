"""db_table_create — create a SQLite table from a data YAML using a schema YAML.

CLI usage:
    python db_table_create.py --db_path <db> --yaml_data <data.yaml> --yaml_schema <schema.yaml> [--table <name>]

Module usage:
    from db_table_create import db_table_create
    result = db_table_create("msl.db", "data.yaml", "msl-schema.yaml")
"""

import argparse
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from db_utils import new_uuid, print_yaml


def _navigate(data: Any, dot_path: str) -> Any:
    """Descend a dot-separated path; return None if any segment is missing."""
    node = data
    for segment in dot_path.split("."):
        if not isinstance(node, dict) or segment not in node:
            return None
        node = node[segment]
    return node


def _flatten_rows(data: dict[str, Any], hierarchy: dict[str, Any]) -> list[dict[str, Any]]:
    """Walk the data YAML using the hierarchy spec and return flat row dicts."""
    root_node = _navigate(data, hierarchy["root"])
    if root_node is None:
        return []

    # Seed context from root-level scalars
    context: dict[str, Any] = {
        col: root_node.get(field)
        for col, field in hierarchy.get("root_promote", {}).items()
    }

    rows: list[dict[str, Any]] = []
    levels: list[dict[str, Any]] = hierarchy["levels"]

    def recurse(node: dict[str, Any], level_idx: int, ctx: dict[str, Any]) -> None:
        level = levels[level_idx]
        for item in node.get(level["key"], []):
            if not isinstance(item, dict):
                continue
            child_ctx = dict(ctx)
            if level.get("leaf"):
                merged = dict(child_ctx)
                merged.update(item)
                rows.append(merged)
            else:
                for col, field in level.get("promote", {}).items():
                    child_ctx[col] = item.get(field)
                recurse(item, level_idx + 1, child_ctx)

    recurse(root_node, 0, context)
    return rows


def _apply_coerce(name: str, val: Any, rule: str) -> Any:
    """Apply int or bool coerce rule; raises ValueError on failure."""
    if rule == "int":
        try:
            return int(val)
        except (ValueError, TypeError):
            raise ValueError(f"field '{name}' must be int, got {val!r}")
    if rule == "bool":
        if isinstance(val, bool):
            return int(val)
        s = str(val).lower()
        if s in ("true", "1", "yes"):
            return 1
        if s in ("false", "0", "no"):
            return 0
        raise ValueError(f"field '{name}' must be bool, got {val!r}")
    return val


def _build_row(
    merged: dict[str, Any],
    columns: list[dict[str, Any]],
    coerce_map: dict[str, str],
    auto_map: dict[str, Any],
) -> dict[str, Any]:
    """Project merged dict onto schema columns, applying coerce and auto rules."""
    row: dict[str, Any] = {}
    for col in columns:
        name = col["name"]
        if name in auto_map:
            row[name] = auto_map[name]()
        else:
            raw = merged.get(name)
            if raw is None or raw == "NA":
                row[name] = None
            elif name in coerce_map:
                row[name] = _apply_coerce(name, raw, coerce_map[name])
            else:
                row[name] = raw
    return row


def db_table_create(
    db_path: str,
    yaml_file: str,
    schema_file: str,
    table: str | None = None,
) -> dict[str, Any]:
    schema_path = Path(schema_file)
    if not schema_path.exists():
        return {"status": "error", "message": f"schema file not found: {schema_file}"}

    yaml_path = Path(yaml_file)
    if not yaml_path.exists():
        return {"status": "error", "message": f"YAML file not found: {yaml_file}"}

    db = Path(db_path)
    if not db.exists():
        return {"status": "error", "message": f"database not found: {db_path}"}

    with open(schema_path) as fh:
        schema: dict[str, Any] = yaml.safe_load(fh)

    if "hierarchy" not in schema or "columns" not in schema:
        return {"status": "error", "message": "schema missing 'hierarchy' or 'columns'"}

    with open(yaml_path) as fh:
        data: dict[str, Any] = yaml.safe_load(fh)

    hierarchy = schema["hierarchy"]
    if _navigate(data, hierarchy["root"]) is None:
        return {"status": "error", "message": f"root not found in data: {hierarchy['root']}"}

    columns: list[dict[str, Any]] = schema["columns"]
    table_name = table or re.sub(r"[^a-zA-Z0-9_]", "_", yaml_path.stem)

    col_defs = [
        f"{c['name']} {c['type']}" + (" PRIMARY KEY" if c.get("primary_key") else "")
        for c in columns
    ]
    create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(col_defs)})"
    insert_sql = (
        f"INSERT INTO {table_name} "
        f"({', '.join(c['name'] for c in columns)}) "
        f"VALUES ({', '.join(':' + c['name'] for c in columns)})"
    )

    coerce_map = {c["name"]: c["coerce"] for c in columns if "coerce" in c}
    auto_map: dict[str, Any] = {
        c["name"]: new_uuid for c in columns if c.get("auto") == "uuid4"
    }

    merged_rows = _flatten_rows(data, hierarchy)
    try:
        built_rows = [_build_row(r, columns, coerce_map, auto_map) for r in merged_rows]
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}

    conn = sqlite3.connect(str(db))
    try:
        conn.execute(create_sql)
        conn.executemany(insert_sql, built_rows)
        conn.commit()
    finally:
        conn.close()

    return {
        "status": "ok",
        "table": table_name,
        "rows_loaded": len(built_rows),
        "db_path": str(db.resolve()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a SQLite table from a data YAML using a schema YAML."
    )
    parser.add_argument("--db_path", required=True, help="Path to the SQLite database")
    parser.add_argument("--yaml_data", required=True, help="Path to the data YAML file")
    parser.add_argument("--yaml_schema", required=True, help="Path to the schema YAML file")
    parser.add_argument("--table", default=None, help="Table name override (default: YAML stem)")
    args = parser.parse_args()
    result = db_table_create(args.db_path, args.yaml_data, args.yaml_schema, table=args.table)
    print_yaml(result)
    if result["status"] == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
