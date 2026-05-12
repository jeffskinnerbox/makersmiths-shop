# Schema-Driven DB Table Creation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the hardcoded SQLite schema in `db_table_create.py` with a schema-driven approach; add `create_db_schema.py` to auto-generate the schema YAML from any hierarchical data YAML.

**Architecture:** `create_db_schema.py` walks a data YAML via DFS to discover hierarchy levels and field types, emitting a portable schema YAML. The rewritten `db_table_create.py` reads that schema to build `CREATE TABLE` SQL and flatten rows from any arbitrarily-structured data YAML — hierarchy traversal is fully data-driven via `root_promote` + `levels[].promote`.

**Tech Stack:** Python 3.11+, PyYAML, SQLite3, pytest, uv

---

## File Map

| Action | Path | Responsibility |
|---|---|---|
| Create | `scripts/create_db_schema.py` | DFS hierarchy discovery, type inference, schema YAML generation |
| Rewrite | `scripts/db_table_create.py` | Schema-driven CREATE TABLE + generic hierarchy traversal |
| Create | `msl-schema.yaml` | Hand-edited schema for MSL data; used by conftest fixture |
| Modify | `tests/conftest.py` | Add `SCHEMA_FILE` constant; pass it to `fresh_db` fixture |
| Modify | `tests/test_db_table_create.py` | Update all calls to new API; add 2 error tests |
| Create | `tests/test_create_db_schema.py` | 9 tests for hierarchy, type inference, error cases |

---

## Task 1: Write `tests/test_create_db_schema.py` (all tests fail)

**Files:**
- Create: `tests/test_create_db_schema.py`

- [ ] **Step 1: Write all 9 tests**

```python
"""Tests for create_db_schema."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from conftest import YAML_FILE


def _schema(yaml_file=YAML_FILE, root="opportunities.shop", leaf="work_tasks"):
    from create_db_schema import create_db_schema
    return create_db_schema(yaml_file, root, leaf)


def test_generates_hierarchy():
    result = _schema()
    levels = result["hierarchy"]["levels"]
    assert [lv["key"] for lv in levels] == ["area", "location", "work_tasks"]


def test_generates_root_promote():
    result = _schema()
    rp = result["hierarchy"]["root_promote"]
    assert rp == {"name": "name", "address": "address", "steward": "steward"}


def test_generates_intermediate_promotes():
    result = _schema()
    levels = {lv["key"]: lv for lv in result["hierarchy"]["levels"]}
    assert levels["area"].get("promote") == {"name": "name"}
    assert levels["location"].get("promote") == {"name": "name", "steward": "steward"}


def test_infers_int_type():
    result = _schema()
    cols = {c["name"]: c for c in result["columns"]}
    assert cols["time"]["type"] == "INTEGER"
    assert cols["time"]["coerce"] == "int"


def test_infers_bool_type():
    result = _schema()
    cols = {c["name"]: c for c in result["columns"]}
    assert cols["supervision"]["type"] == "INTEGER"
    assert cols["supervision"]["coerce"] == "bool"


def test_unions_sparse_fields():
    # frequency/purpose/instructions appear on only some work_tasks records
    result = _schema()
    col_names = [c["name"] for c in result["columns"]]
    assert "frequency" in col_names
    assert "purpose" in col_names
    assert "instructions" in col_names


def test_uuid_column_prepended():
    result = _schema()
    first = result["columns"][0]
    assert first["name"] == "uuid"
    assert first.get("primary_key") is True
    assert first.get("auto") == "uuid4"


def test_bad_root():
    result = _schema(root="nonexistent.path")
    assert result["status"] == "error"


def test_bad_leaf():
    result = _schema(leaf="nonexistent_leaf")
    assert result["status"] == "error"
```

- [ ] **Step 2: Confirm all tests fail (import error is expected)**

```bash
uv run pytest tests/test_create_db_schema.py -v
```

Expected: `ERROR collecting tests/test_create_db_schema.py` — `ModuleNotFoundError: No module named 'create_db_schema'`

---

## Task 2: Implement `create_db_schema.py` — hierarchy discovery

**Files:**
- Create: `scripts/create_db_schema.py`

- [ ] **Step 1: Create the script with hierarchy helpers**

```python
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
            first = arr[0] if arr and isinstance(arr[0], dict) else {}
            promote = _scalar_fields(first)
            if promote:
                entry["promote"] = promote
            cursor = first
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
```

- [ ] **Step 2: Run all create_db_schema tests**

```bash
uv run pytest tests/test_create_db_schema.py -v
```

Expected: all 9 tests PASS.

- [ ] **Step 3: Commit**

```bash
git add scripts/create_db_schema.py tests/test_create_db_schema.py
git commit -m "feat: add create_db_schema tool with hierarchy discovery and type inference"
```

---

## Task 3: Generate and check in `msl-schema.yaml`

**Files:**
- Create: `msl-schema.yaml` (proto1 root)

- [ ] **Step 1: Run the tool to see the raw generated output**

```bash
uv run python scripts/create_db_schema.py \
    --yaml_data MSL-volunteer-opportunities.yaml \
    --root opportunities.shop \
    --leaf work_tasks
```

The raw output will have conflicting column names (`name` appears three times from shop, area, and location levels; `steward` appears twice). This is expected — the tool uses field names as column names by default.

- [ ] **Step 2: Write the hand-edited `msl-schema.yaml` to disk**

Write the following content to `msl-schema.yaml` in the proto1 root. This renames conflicting columns so each column name is unique and descriptive:

```yaml
hierarchy:
  root: opportunities.shop
  root_promote:
    shop: name
    shop_address: address
    shop_steward: steward
  levels:
  - key: area
    promote:
      area: name
  - key: location
    promote:
      location: name
      location_steward: steward
  - key: work_tasks
    leaf: true
columns:
- name: uuid
  type: TEXT
  primary_key: true
  auto: uuid4
- name: task_id
  type: TEXT
- name: task
  type: TEXT
- name: time
  type: INTEGER
  coerce: int
- name: frequency
  type: TEXT
- name: purpose
  type: TEXT
- name: instructions
  type: TEXT
- name: supervision
  type: INTEGER
  coerce: bool
- name: last_date
  type: TEXT
- name: location
  type: TEXT
- name: location_steward
  type: TEXT
- name: area
  type: TEXT
- name: shop
  type: TEXT
- name: shop_address
  type: TEXT
- name: shop_steward
  type: TEXT
```

- [ ] **Step 3: Commit**

```bash
git add msl-schema.yaml
git commit -m "feat: add hand-edited msl-schema.yaml for MSL volunteer opportunities data"
```

---

## Task 4: Write updated `tests/test_db_table_create.py` (tests fail until Task 5)

**Files:**
- Modify: `tests/test_db_table_create.py`

All 5 existing tests are updated to pass `SCHEMA_FILE` as the third argument to `db_table_create`. Two new error tests are added.

- [ ] **Step 1: Back up and rewrite the test file**

```bash
cp -f tests/test_db_table_create.py tests/test_db_table_create.py.bak
```

Write the following to `tests/test_db_table_create.py`:

```python
"""Tests for db_table_create."""

import sqlite3
from db_create import db_create
from db_table_create import db_table_create
from conftest import SCHEMA_FILE, YAML_FILE


def test_loads_rows(tmp_path):
    db_path = str(tmp_path / "t.db")
    db_create(db_path)
    result = db_table_create(db_path, YAML_FILE, SCHEMA_FILE)
    assert result["status"] == "ok"
    assert result["rows_loaded"] > 0


def test_table_name_from_yaml_stem(tmp_path):
    db_path = str(tmp_path / "t.db")
    db_create(db_path)
    result = db_table_create(db_path, YAML_FILE, SCHEMA_FILE)
    assert result["table"] == "MSL_volunteer_opportunities"


def test_table_name_override(tmp_path):
    db_path = str(tmp_path / "t.db")
    db_create(db_path)
    result = db_table_create(db_path, YAML_FILE, SCHEMA_FILE, table="my_tasks")
    assert result["table"] == "my_tasks"


def test_rows_have_uuid(tmp_path):
    db_path = str(tmp_path / "t.db")
    db_create(db_path)
    db_table_create(db_path, YAML_FILE, SCHEMA_FILE)
    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT uuid FROM MSL_volunteer_opportunities LIMIT 1"
    ).fetchone()
    conn.close()
    assert row is not None and len(row[0]) == 36  # UUID4 format


def test_missing_yaml_file(tmp_path):
    db_path = str(tmp_path / "t.db")
    db_create(db_path)
    result = db_table_create(db_path, "/nonexistent/file.yaml", SCHEMA_FILE)
    assert result["status"] == "error"


def test_missing_schema_file(tmp_path):
    db_path = str(tmp_path / "t.db")
    db_create(db_path)
    result = db_table_create(db_path, YAML_FILE, "/nonexistent/schema.yaml")
    assert result["status"] == "error"


def test_bad_hierarchy(tmp_path):
    import yaml
    schema_path = str(tmp_path / "bad_schema.yaml")
    bad_schema = {
        "hierarchy": {"root": "no.such.path", "levels": [{"key": "items", "leaf": True}]},
        "columns": [{"name": "uuid", "type": "TEXT", "primary_key": True, "auto": "uuid4"}],
    }
    with open(schema_path, "w") as fh:
        yaml.dump(bad_schema, fh)
    db_path = str(tmp_path / "t.db")
    db_create(db_path)
    result = db_table_create(db_path, YAML_FILE, schema_path)
    assert result["status"] == "error"
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
uv run pytest tests/test_db_table_create.py -v
```

Expected: all 7 tests FAIL — `db_table_create` still uses old 2-argument signature and won't accept `SCHEMA_FILE`.

---

## Task 5: Rewrite `scripts/db_table_create.py`

**Files:**
- Modify: `scripts/db_table_create.py`

- [ ] **Step 1: Back up the existing file**

```bash
cp -f scripts/db_table_create.py scripts/db_table_create.py.bak
```

- [ ] **Step 2: Rewrite the script**

```python
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
    """Apply int or bool coerce rule; exit 1 on failure."""
    if rule == "int":
        try:
            return int(val)
        except (ValueError, TypeError):
            print(f"error: field '{name}' must be int, got {val!r}", file=sys.stderr)
            sys.exit(1)
    if rule == "bool":
        if isinstance(val, bool):
            return int(val)
        s = str(val).lower()
        if s in ("true", "1", "yes"):
            return 1
        if s in ("false", "0", "no"):
            return 0
        print(f"error: field '{name}' must be bool, got {val!r}", file=sys.stderr)
        sys.exit(1)
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
    built_rows = [_build_row(r, columns, coerce_map, auto_map) for r in merged_rows]

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
```

- [ ] **Step 3: Run db_table_create tests to verify they pass**

```bash
uv run pytest tests/test_db_table_create.py -v
```

Expected: all 7 tests PASS.

- [ ] **Step 4: Commit**

```bash
git add scripts/db_table_create.py tests/test_db_table_create.py
git commit -m "feat: rewrite db_table_create to be schema-driven; add schema error tests"
```

---

## Task 6: Update `tests/conftest.py`

**Files:**
- Modify: `tests/conftest.py`

- [ ] **Step 1: Back up and update conftest**

```bash
cp -f tests/conftest.py tests/conftest.py.bak
```

Write the following to `tests/conftest.py`:

```python
"""Shared fixtures for all test modules."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

YAML_FILE = str(Path(__file__).parent.parent / "MSL-volunteer-opportunities.yaml")
SCHEMA_FILE = str(Path(__file__).parent.parent / "msl-schema.yaml")


@pytest.fixture
def fresh_db(tmp_path):
    """Create a temporary DB pre-loaded with the MSL YAML data."""
    from db_create import db_create
    from db_table_create import db_table_create

    db_path = str(tmp_path / "test.db")
    db_create(db_path)
    db_table_create(db_path, YAML_FILE, SCHEMA_FILE)
    return db_path


TABLE = "MSL_volunteer_opportunities"
```

- [ ] **Step 2: Run the full test suite**

```bash
uv run pytest ./tests/ -v
```

Expected: all tests PASS (30 original + 9 new create_db_schema + 2 new db_table_create = 41 total).

- [ ] **Step 3: Commit**

```bash
git add tests/conftest.py
git commit -m "feat: add SCHEMA_FILE to conftest; wire fresh_db fixture to schema-driven loader"
```

---

## Task 7: End-to-end manual validation

- [ ] **Step 1: Rebuild msl.db using the new tools**

```bash
uv run python scripts/db_create.py msl.db --overwrite
uv run python scripts/db_table_create.py \
    --db_path msl.db \
    --yaml_data MSL-volunteer-opportunities.yaml \
    --yaml_schema msl-schema.yaml
```

Expected output (YAML) — `rows_loaded` is the actual task count from the YAML (≥ 60 for the current MSL file):
```yaml
status: ok
table: MSL_volunteer_opportunities
rows_loaded: 63
db_path: /home/jeff/src/projects/makersmiths/shop-sergeant/prototyping/proto1/msl.db
```

- [ ] **Step 2: Spot-check schema columns are all present**

```bash
uv run python -c "
import sqlite3
conn = sqlite3.connect('msl.db')
cols = [r[1] for r in conn.execute(\"PRAGMA table_info(MSL_volunteer_opportunities)\")]
print(cols)
conn.close()
"
```

Expected columns: `['uuid', 'task_id', 'task', 'time', 'frequency', 'purpose', 'instructions', 'supervision', 'last_date', 'location', 'location_steward', 'area', 'shop', 'shop_address', 'shop_steward']`

- [ ] **Step 3: Spot-check a row has correct promoted values**

```bash
uv run python scripts/db_list.py msl.db MSL_volunteer_opportunities location=Metalshop
```

Expected: records with `shop: Makersmiths Leesburg (MSL)`, `area: Main Level`, `location: Metalshop`.

- [ ] **Step 4: Run the full test suite one final time**

```bash
uv run pytest ./tests/ -v
```

Expected: all tests PASS, 0 failures.

- [ ] **Step 5: Commit msl.db if it changed**

```bash
git add msl.db
git commit -m "rebuild msl.db with schema-driven loader"
```
