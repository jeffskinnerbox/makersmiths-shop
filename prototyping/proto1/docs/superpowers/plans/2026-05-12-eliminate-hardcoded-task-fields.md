# Eliminate Hardcoded TASK_FIELDS Implementation Plan

> **Status: COMPLETE** — all 5 tasks implemented, reviewed, and merged to `main` on 2026-05-12. 57/57 tests passing.

**Goal:** Remove hardcoded `TASK_FIELDS` from `db_list`, `db_purge`, and `db_update` by reading valid column names directly from the live SQLite table via `PRAGMA table_info`, and fix `create_db_schema.py` to union scalar fields across all items at each intermediate hierarchy level instead of sampling only the first.

**Architecture:** Add two new utility functions to `db_utils.py` (`get_table_columns` for PRAGMA introspection, `coerce_for_type` for schema-agnostic type coercion); update three scripts to use them instead of `TASK_FIELDS`/`coerce_value`; fix a four-line sampling bug in `create_db_schema.py`.

**Tech Stack:** Python 3.11+, SQLite3, pytest, uv

---

## File Map

| File | Change |
|---|---|
| `scripts/db_utils.py` | Add `get_table_columns()` and `coerce_for_type()` |
| `scripts/db_list.py` | Remove `TASK_FIELDS` import; validate via `get_table_columns` |
| `scripts/db_purge.py` | Same as db_list |
| `scripts/db_update.py` | Remove `TASK_FIELDS`/`coerce_value` imports; use introspection + `coerce_for_type` |
| `scripts/create_db_schema.py` | Union all intermediate-level items for promote (4-line change) |
| `tests/test_db_utils.py` | **New file** — tests for the two new utility functions |
| `tests/test_bulk_ops.py` | Add 4 tests (2 for db_list, 2 for db_purge) |
| `tests/test_crud.py` | Add 2 tests for db_update |
| `tests/test_create_db_schema.py` | Add 1 test for intermediate union |

All test commands run from `prototyping/proto1/` with `uv run pytest`.

---

## Task 1: Add `get_table_columns` and `coerce_for_type` to `db_utils.py` ✅ `5d31761` + `1e90329`

**Files:**
- Create: `tests/test_db_utils.py`
- Modify: `scripts/db_utils.py`

- [x] **Step 1: Create `tests/test_db_utils.py` with failing tests**

```python
"""Tests for new db_utils helpers: get_table_columns, coerce_for_type."""

import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from db_utils import coerce_for_type, get_table_columns


def _make_conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        "CREATE TABLE t (id TEXT PRIMARY KEY, count INTEGER, score REAL, notes TEXT)"
    )
    return conn


def test_get_table_columns_returns_name_type_map():
    conn = _make_conn()
    cols = get_table_columns(conn, "t")
    conn.close()
    assert cols == {"id": "TEXT", "count": "INTEGER", "score": "REAL", "notes": "TEXT"}


def test_coerce_na_returns_none():
    assert coerce_for_type("x", "NA", "TEXT") is None


def test_coerce_integer_from_numeric_string():
    assert coerce_for_type("x", "42", "INTEGER") == 42


def test_coerce_integer_from_bool_true():
    assert coerce_for_type("x", "true", "INTEGER") == 1
    assert coerce_for_type("x", "yes", "INTEGER") == 1


def test_coerce_integer_from_bool_false():
    assert coerce_for_type("x", "false", "INTEGER") == 0
    assert coerce_for_type("x", "no", "INTEGER") == 0


def test_coerce_real_from_string():
    assert coerce_for_type("x", "3.14", "REAL") == pytest.approx(3.14)


def test_coerce_text_passthrough():
    assert coerce_for_type("x", "hello world", "TEXT") == "hello world"


def test_coerce_bad_integer_exits():
    with pytest.raises(SystemExit):
        coerce_for_type("x", "notanint", "INTEGER")


def test_coerce_bad_real_exits():
    with pytest.raises(SystemExit):
        coerce_for_type("x", "notafloat", "REAL")
```

- [x] **Step 2: Run to confirm all tests fail**

```bash
uv run pytest tests/test_db_utils.py -v
```

Expected: `ImportError` or `AttributeError` — `get_table_columns` and `coerce_for_type` don't exist yet.

- [x] **Step 3: Back up `db_utils.py` and add the two new functions**

```bash
cp -f scripts/db_utils.py scripts/db_utils.py.bak
```

Add at the end of `scripts/db_utils.py` (after `coerce_value`):

```python
def get_table_columns(conn: sqlite3.Connection, table: str) -> dict[str, str]:
    """Return {column_name: sql_type} for every column in table."""
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {row["name"]: row["type"] for row in rows}


def coerce_for_type(field: str, raw: str, sql_type: str) -> Any:
    """Coerce a CLI string value to the appropriate Python type given its SQLite column type."""
    if raw == NA or raw is None:
        return None
    upper = sql_type.upper()
    if upper == "INTEGER":
        if raw.lower() in ("true", "yes", "1"):
            return 1
        if raw.lower() in ("false", "no", "0"):
            return 0
        try:
            return int(raw)
        except ValueError:
            print(f"error: field '{field}' expects INTEGER, got '{raw}'", file=sys.stderr)
            sys.exit(1)
    if upper == "REAL":
        try:
            return float(raw)
        except ValueError:
            print(f"error: field '{field}' expects REAL, got '{raw}'", file=sys.stderr)
            sys.exit(1)
    return raw
```

- [x] **Step 4: Run tests to confirm they pass**

```bash
uv run pytest tests/test_db_utils.py -v
```

Expected: all 9 tests PASS.

- [x] **Step 5: Run full suite to confirm no regressions**

```bash
uv run pytest ./tests/ -v
```

Expected: all existing tests PASS.

- [x] **Step 6: Commit**

```bash
git add scripts/db_utils.py tests/test_db_utils.py
git commit -m "feat: add get_table_columns and coerce_for_type to db_utils"
```

---

## Task 2: Update `db_list.py` to use SQLite introspection ✅ `9c1169b`

**Files:**
- Modify: `tests/test_bulk_ops.py`
- Modify: `scripts/db_list.py`

- [x] **Step 1: Add failing tests to `tests/test_bulk_ops.py`**

Append to the end of `tests/test_bulk_ops.py`:

```python
def test_list_unknown_field_rejected(fresh_db):
    result = db_list(fresh_db, TABLE, {"nonexistent_column": "val"})
    assert result["status"] == "error"
    assert "nonexistent_column" in result["message"]


def test_list_schema_column_not_in_task_fields(fresh_db):
    # shop_steward is in the schema-generated table but absent from TASK_FIELDS.
    # Before this fix, db_list would reject it. After, it must return ok.
    result = db_list(fresh_db, TABLE, {"shop_steward": ".*"})
    assert result["status"] == "ok"
```

- [x] **Step 2: Run new tests to confirm they fail**

```bash
uv run pytest tests/test_bulk_ops.py::test_list_unknown_field_rejected tests/test_bulk_ops.py::test_list_schema_column_not_in_task_fields -v
```

Expected:
- `test_list_unknown_field_rejected` — PASS (coincidentally, existing code already rejects unknown fields; this stays passing)
- `test_list_schema_column_not_in_task_fields` — FAIL (`status: error` because `shop_steward` is not in `TASK_FIELDS`)

- [x] **Step 3: Back up `db_list.py` and rewrite it**

```bash
cp -f scripts/db_list.py scripts/db_list.py.bak
```

Replace `scripts/db_list.py` with:

```python
"""db_list — list records matching one or more field=regex filters.

At least one filter is required. Filters are AND-combined.
Regex matching is case-insensitive.

CLI usage:
    python db_list.py <db_path> <table> field=regex [field=regex ...]

Module usage:
    from db_list import db_list
    result = db_list("msl.db", "MSL_volunteer_opportunities",
                     {"frequency": "Weekly", "location": "Metal"})
"""

import argparse
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from db_utils import get_connection, get_table_columns, print_yaml, row_to_dict


def db_list(db_path: str, table: str, filters: dict[str, str]) -> dict[str, Any]:
    if not filters:
        return {"status": "error", "message": "at least one filter is required"}

    conn = get_connection(db_path)
    try:
        columns = get_table_columns(conn, table)
        bad = [f for f in filters if f not in columns]
        if bad:
            return {"status": "error", "message": f"unknown fields: {bad}"}

        where = " AND ".join(f"{f} REGEXP ?" for f in filters)
        params = list(filters.values())
        rows = conn.execute(
            f"SELECT * FROM {table} WHERE {where}", params
        ).fetchall()
    finally:
        conn.close()

    return {
        "status": "ok",
        "count": len(rows),
        "records": [row_to_dict(r) for r in rows],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="List records matching field=regex filters (AND-combined, case-insensitive)."
    )
    parser.add_argument("db_path", help="Path to the SQLite database")
    parser.add_argument("table", help="Table name")
    parser.add_argument("filters", nargs="+", metavar="field=regex",
                        help="One or more field=regex filters")
    args = parser.parse_args()

    filters: dict[str, str] = {}
    for token in args.filters:
        if "=" not in token:
            print(f"error: expected field=regex, got '{token}'", file=sys.stderr)
            sys.exit(1)
        field, _, pattern = token.partition("=")
        filters[field] = pattern

    result = db_list(args.db_path, args.table, filters)
    print_yaml(result)
    if result["status"] == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [x] **Step 4: Run new tests to confirm they pass**

```bash
uv run pytest tests/test_bulk_ops.py::test_list_unknown_field_rejected tests/test_bulk_ops.py::test_list_schema_column_not_in_task_fields -v
```

Expected: both PASS.

- [x] **Step 5: Run full suite to confirm no regressions**

```bash
uv run pytest ./tests/ -v
```

Expected: all tests PASS.

- [x] **Step 6: Commit**

```bash
git add scripts/db_list.py tests/test_bulk_ops.py
git commit -m "feat: db_list validates fields via PRAGMA table_info instead of TASK_FIELDS"
```

---

## Task 3: Update `db_purge.py` to use SQLite introspection ✅ `609946c`

**Files:**
- Modify: `tests/test_bulk_ops.py`
- Modify: `scripts/db_purge.py`

- [x] **Step 1: Add failing tests to `tests/test_bulk_ops.py`**

Append to the end of `tests/test_bulk_ops.py`:

```python
def test_purge_unknown_field_rejected(fresh_db):
    result = db_purge(fresh_db, TABLE, {"nonexistent_column": "val"})
    assert result["status"] == "error"
    assert "nonexistent_column" in result["message"]


def test_purge_schema_column_not_in_task_fields(fresh_db):
    # shop_steward is in the schema-generated table but absent from TASK_FIELDS.
    result = db_purge(fresh_db, TABLE, {"shop_steward": ".*"})
    assert result["status"] == "ok"
```

- [x] **Step 2: Run new tests to confirm expected failure**

```bash
uv run pytest tests/test_bulk_ops.py::test_purge_unknown_field_rejected tests/test_bulk_ops.py::test_purge_schema_column_not_in_task_fields -v
```

Expected:
- `test_purge_unknown_field_rejected` — PASS (existing code already rejects)
- `test_purge_schema_column_not_in_task_fields` — FAIL (`shop_steward` not in `TASK_FIELDS`)

- [x] **Step 3: Back up `db_purge.py` and rewrite it**

```bash
cp -f scripts/db_purge.py scripts/db_purge.py.bak
```

Replace `scripts/db_purge.py` with:

```python
"""db_purge — delete all records matching one or more field=regex filters.

At least one filter is required to prevent accidental full-table deletion.
Filters are AND-combined. Regex matching is case-insensitive.

CLI usage:
    python db_purge.py <db_path> <table> field=regex [field=regex ...]

Module usage:
    from db_purge import db_purge
    result = db_purge("msl.db", "MSL_volunteer_opportunities",
                      {"location": "Metalshop"})
"""

import argparse
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from db_utils import get_connection, get_table_columns, print_yaml, row_to_dict


def db_purge(db_path: str, table: str, filters: dict[str, str]) -> dict[str, Any]:
    if not filters:
        return {"status": "error", "message": "at least one filter is required"}

    conn = get_connection(db_path)
    try:
        columns = get_table_columns(conn, table)
        bad = [f for f in filters if f not in columns]
        if bad:
            return {"status": "error", "message": f"unknown fields: {bad}"}

        where = " AND ".join(f"{f} REGEXP ?" for f in filters)
        params = list(filters.values())
        rows = conn.execute(
            f"SELECT * FROM {table} WHERE {where}", params
        ).fetchall()
        deleted = [row_to_dict(r) for r in rows]
        conn.execute(f"DELETE FROM {table} WHERE {where}", params)
        conn.commit()
    finally:
        conn.close()

    return {"status": "ok", "deleted_count": len(deleted), "deleted": deleted}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Delete records matching field=regex filters (AND-combined, case-insensitive)."
    )
    parser.add_argument("db_path", help="Path to the SQLite database")
    parser.add_argument("table", help="Table name")
    parser.add_argument("filters", nargs="+", metavar="field=regex",
                        help="One or more field=regex filters")
    args = parser.parse_args()

    filters: dict[str, str] = {}
    for token in args.filters:
        if "=" not in token:
            print(f"error: expected field=regex, got '{token}'", file=sys.stderr)
            sys.exit(1)
        field, _, pattern = token.partition("=")
        filters[field] = pattern

    result = db_purge(args.db_path, args.table, filters)
    print_yaml(result)
    if result["status"] == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [x] **Step 4: Run new tests to confirm they pass**

```bash
uv run pytest tests/test_bulk_ops.py::test_purge_unknown_field_rejected tests/test_bulk_ops.py::test_purge_schema_column_not_in_task_fields -v
```

Expected: both PASS.

- [x] **Step 5: Run full suite to confirm no regressions**

```bash
uv run pytest ./tests/ -v
```

Expected: all tests PASS.

- [x] **Step 6: Commit**

```bash
git add scripts/db_purge.py tests/test_bulk_ops.py
git commit -m "feat: db_purge validates fields via PRAGMA table_info instead of TASK_FIELDS"
```

---

## Task 4: Update `db_update.py` to use SQLite introspection + `coerce_for_type` ✅ `b2b28e2`

**Files:**
- Modify: `tests/test_crud.py`
- Modify: `scripts/db_update.py`

- [x] **Step 1: Add failing tests to `tests/test_crud.py`**

Append to the end of `tests/test_crud.py`:

```python
def test_update_unknown_field_rejected(fresh_db):
    uuid = _first_uuid(fresh_db)
    result = db_update(fresh_db, TABLE, uuid, {"nonexistent_column": "value"})
    assert result["status"] == "error"
    assert "nonexistent_column" in result["message"]


def test_update_schema_column_not_in_task_fields(fresh_db):
    # shop_steward is in the schema-generated table but absent from TASK_FIELDS.
    # Before this fix, db_update would reject it. After, it must return ok.
    uuid = _first_uuid(fresh_db)
    result = db_update(fresh_db, TABLE, uuid, {"shop_steward": "New Steward"})
    assert result["status"] == "ok"
    assert result["record"]["shop_steward"] == "New Steward"
```

- [x] **Step 2: Run new tests to confirm expected failure**

```bash
uv run pytest tests/test_crud.py::test_update_unknown_field_rejected tests/test_crud.py::test_update_schema_column_not_in_task_fields -v
```

Expected:
- `test_update_unknown_field_rejected` — PASS (existing code already rejects)
- `test_update_schema_column_not_in_task_fields` — FAIL (`shop_steward` not in `TASK_FIELDS`)

- [x] **Step 3: Back up `db_update.py` and rewrite it**

```bash
cp -f scripts/db_update.py scripts/db_update.py.bak
```

Replace `scripts/db_update.py` with:

```python
"""db_update — modify one or more fields of a record by UUID.

Pass field=value pairs as positional arguments.
Use field=NA to set a field to NULL.

CLI usage:
    python db_update.py <db_path> <table> <uuid> field=value [field=value ...]

Module usage:
    from db_update import db_update
    result = db_update("msl.db", "MSL_volunteer_opportunities", "<uuid>",
                       {"last_date": "2026-05-06"})
"""

import argparse
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from db_utils import (
    coerce_for_type,
    get_connection,
    get_table_columns,
    print_yaml,
    row_to_dict,
)

IMMUTABLE = {"uuid"}


def db_update(
    db_path: str, table: str, uuid: str, updates: dict[str, Any]
) -> dict[str, Any]:
    if not updates:
        return {"status": "error", "message": "no fields provided to update"}

    conn = get_connection(db_path)
    try:
        columns = get_table_columns(conn, table)
        bad = [f for f in updates if f not in columns or f in IMMUTABLE]
        if bad:
            return {"status": "error", "message": f"unknown or immutable fields: {bad}"}

        exists = conn.execute(
            f"SELECT 1 FROM {table} WHERE uuid = ?", (uuid,)
        ).fetchone()
        if exists is None:
            return {"status": "error", "message": f"no record with uuid: {uuid}"}

        set_clause = ", ".join(f"{f} = ?" for f in updates)
        params = list(updates.values()) + [uuid]
        conn.execute(f"UPDATE {table} SET {set_clause} WHERE uuid = ?", params)
        conn.commit()
        row = conn.execute(f"SELECT * FROM {table} WHERE uuid = ?", (uuid,)).fetchone()
    finally:
        conn.close()

    return {"status": "ok", "record": row_to_dict(row)}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update fields of a record by UUID. Use field=value pairs."
    )
    parser.add_argument("db_path", help="Path to the SQLite database")
    parser.add_argument("table", help="Table name")
    parser.add_argument("uuid", help="UUID of the record to update")
    parser.add_argument("fields", nargs="+", metavar="field=value",
                        help="Fields to update (e.g. last_date=2026-05-06 or frequency=NA)")
    args = parser.parse_args()

    conn_tmp = get_connection(args.db_path)
    columns = get_table_columns(conn_tmp, args.table)
    conn_tmp.close()

    updates: dict[str, Any] = {}
    for token in args.fields:
        if "=" not in token:
            print(f"error: expected field=value, got '{token}'", file=sys.stderr)
            sys.exit(1)
        field, _, raw_val = token.partition("=")
        sql_type = columns.get(field, "TEXT")
        updates[field] = coerce_for_type(field, raw_val, sql_type)

    result = db_update(args.db_path, args.table, args.uuid, updates)
    print_yaml(result)
    if result["status"] == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [x] **Step 4: Run new tests to confirm they pass**

```bash
uv run pytest tests/test_crud.py::test_update_unknown_field_rejected tests/test_crud.py::test_update_schema_column_not_in_task_fields -v
```

Expected: both PASS.

- [x] **Step 5: Run full suite to confirm no regressions**

```bash
uv run pytest ./tests/ -v
```

Expected: all tests PASS.

- [x] **Step 6: Commit**

```bash
git add scripts/db_update.py tests/test_crud.py
git commit -m "feat: db_update validates fields and coerces types via PRAGMA table_info"
```

---

## Task 5: Fix `create_db_schema.py` intermediate-level field union ✅ `3d92b54`

**Files:**
- Modify: `tests/test_create_db_schema.py`
- Modify: `scripts/create_db_schema.py`

- [x] **Step 1: Add a failing test to `tests/test_create_db_schema.py`**

Add at the end of `tests/test_create_db_schema.py`:

```python
def test_unions_intermediate_fields(tmp_path):
    import yaml

    # Two sections: Alpha has only 'name'; Beta adds 'owner'.
    # Without the fix, 'owner' is missed because only arr[0] (Alpha) is sampled.
    data = {
        "root": {
            "sections": [
                {"name": "Alpha", "tasks": [{"task": "clean"}]},
                {"name": "Beta", "owner": "Bob", "tasks": [{"task": "fix"}]},
            ]
        }
    }
    yaml_path = tmp_path / "data.yaml"
    yaml_path.write_text(yaml.dump(data))

    from create_db_schema import create_db_schema
    result = create_db_schema(str(yaml_path), "root", "tasks")
    assert result.get("status") != "error", result.get("message")
    levels = {lv["key"]: lv for lv in result["hierarchy"]["levels"]}
    assert "name" in levels["sections"]["promote"]
    assert "owner" in levels["sections"]["promote"]
```

- [x] **Step 2: Run new test to confirm it fails**

```bash
uv run pytest tests/test_create_db_schema.py::test_unions_intermediate_fields -v
```

Expected: FAIL — `assert "owner" in levels["sections"]["promote"]` fails because only Alpha is sampled.

- [x] **Step 3: Back up `create_db_schema.py` and apply the fix**

```bash
cp -f scripts/create_db_schema.py scripts/create_db_schema.py.bak
```

In `scripts/create_db_schema.py`, locate the loop that builds `levels` (around line 113). Replace the block that reads:

```python
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
```

With:

```python
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
```

- [x] **Step 4: Run new test to confirm it passes**

```bash
uv run pytest tests/test_create_db_schema.py::test_unions_intermediate_fields -v
```

Expected: PASS.

- [x] **Step 5: Run full suite to confirm no regressions**

```bash
uv run pytest ./tests/ -v
```

Expected: all tests PASS.

- [x] **Step 6: Commit**

```bash
git add scripts/create_db_schema.py tests/test_create_db_schema.py
git commit -m "fix: union all intermediate-level items when collecting promote fields in create_db_schema"
```
