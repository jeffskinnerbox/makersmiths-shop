"""create_db_schema — generate a schema YAML from a hierarchical data YAML.

CLI usage:
    python create_db_schema.py --yaml_data <file> --root <dot.path> --leaf <key> [--output <file>]

Module usage:
    from create_db_schema import create_db_schema
    schema = create_db_schema("data.yaml", "opportunities.shop", "work_tasks")
"""

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from db_utils import print_yaml


def _navigate_root(data: dict[str, Any], root: str) -> dict[str, Any] | None:
    """Descend dot-separated path; return node dict or None if missing."""
    node: Any = data
    for segment in root.split("."):
        if not isinstance(node, dict) or segment not in node:
            return None
        node = node[segment]
    return node if isinstance(node, dict) else None


def _find_levels(node: dict[str, Any], leaf: str) -> list[str] | None:
    """DFS: return ordered list of array keys from node down to leaf, or None."""
    for key, val in node.items():
        if not isinstance(val, list) or not val:
            continue
        if key == leaf:
            return [key]
        if isinstance(val[0], dict):
            sub = _find_levels(val[0], leaf)
            if sub is not None:
                return [key] + sub
    return None


def _scalar_fields(node: dict[str, Any]) -> dict[str, str]:
    """Return {field_name: field_name} for every non-list, non-dict value in node."""
    return {k: k for k, v in node.items() if not isinstance(v, (list, dict))}


def _collect_all_leaves(node: dict[str, Any], level_keys: list[str]) -> list[dict[str, Any]]:
    """Walk the hierarchy and return every leaf record dict."""
    if not level_keys:
        return [node] if isinstance(node, dict) else []
    key = level_keys[0]
    array = node.get(key, [])
    if len(level_keys) == 1:
        return [item for item in array if isinstance(item, dict)]
    result: list[dict[str, Any]] = []
    for item in array:
        if isinstance(item, dict):
            result.extend(_collect_all_leaves(item, level_keys[1:]))
    return result


def _infer_sql_type(val: Any) -> tuple[str, str | None]:
    """Return (SQLite type string, coerce rule or None)."""
    if isinstance(val, bool):
        return "INTEGER", "bool"
    if isinstance(val, int):
        return "INTEGER", "int"
    if isinstance(val, float):
        return "REAL", None
    return "TEXT", None


def _infer_column(field: str, leaves: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a column spec by sampling the first non-None/non-NA value."""
    for record in leaves:
        val = record.get(field)
        if val is not None and val != "NA":
            sql_type, coerce = _infer_sql_type(val)
            col: dict[str, Any] = {"name": field, "type": sql_type}
            if coerce:
                col["coerce"] = coerce
            return col
    return {"name": field, "type": "TEXT"}


def create_db_schema(yaml_file: str, root: str, leaf: str) -> dict[str, Any]:
    yaml_path = Path(yaml_file)
    if not yaml_path.exists():
        return {"status": "error", "message": f"YAML file not found: {yaml_file}"}

    with open(yaml_path) as fh:
        data: dict[str, Any] = yaml.safe_load(fh)

    root_node = _navigate_root(data, root)
    if root_node is None:
        return {"status": "error", "message": f"root path not found: {root}"}

    level_keys = _find_levels(root_node, leaf)
    if level_keys is None:
        return {"status": "error", "message": f"leaf key not reachable: {leaf}"}

    all_leaves = _collect_all_leaves(root_node, level_keys)
    if not all_leaves:
        return {"status": "error", "message": "no leaf records found"}

    # Build hierarchy block
    root_promote = _scalar_fields(root_node)
    levels: list[dict[str, Any]] = []
    cursor: dict[str, Any] = root_node
    for i, key in enumerate(level_keys):
        is_leaf = i == len(level_keys) - 1
        entry: dict[str, Any] = {"key": key}
        if not is_leaf:
            arr = cursor.get(key, [])
            all_items = [item for item in arr if isinstance(item, dict)]
            promote: dict[str, str] = {}
            for item in all_items:
                promote.update(_scalar_fields(item))
            if promote:
                entry["promote"] = promote
            cursor = all_items[0] if all_items else {}
        else:
            entry["leaf"] = True
        levels.append(entry)

    # Build columns: uuid first, then leaf fields in discovery order
    seen: set[str] = set()
    ordered_fields: list[str] = []
    for record in all_leaves:
        for field in record.keys():
            if field not in seen:
                seen.add(field)
                ordered_fields.append(field)

    uuid_col: dict[str, Any] = {
        "name": "uuid",
        "type": "TEXT",
        "primary_key": True,
        "auto": "uuid4",
    }
    leaf_columns = [_infer_column(f, all_leaves) for f in ordered_fields]

    return {
        "hierarchy": {
            "root": root,
            "root_promote": root_promote,
            "levels": levels,
        },
        "columns": [uuid_col] + leaf_columns,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a schema YAML from a hierarchical data YAML."
    )
    parser.add_argument("--yaml_data", required=True, help="Path to the data YAML file")
    parser.add_argument("--root", required=True, help="Dot-separated path to root node")
    parser.add_argument("--leaf", required=True, help="Array key of the leaf (row source)")
    parser.add_argument("--output", default=None, help="Output schema YAML file (stdout if omitted)")
    args = parser.parse_args()

    result = create_db_schema(args.yaml_data, args.root, args.leaf)

    if "status" in result and result["status"] == "error":
        print_yaml(result)
        sys.exit(1)

    schema_yaml = yaml.dump(result, default_flow_style=False, allow_unicode=True, sort_keys=False)
    if args.output:
        Path(args.output).write_text(schema_yaml)
    else:
        print(schema_yaml, end="")


if __name__ == "__main__":
    main()
