# Eliminate Hardcoded TASK_FIELDS — Design Spec
_Date: 2026-05-12_

## Goal

Remove the two known limitations from the schema-driven db_table_create work:

1. `db_list`, `db_purge`, and `db_update` validate field names against the hardcoded
   `TASK_FIELDS` list in `db_utils.py`. If a schema produces a table with different columns,
   those tools reject valid field names.
2. `create_db_schema.py` samples only the **first element** of each intermediate hierarchy
   level when collecting `promote` candidates. If different items at the same level have
   different scalar fields, some are silently missed.

---

## Limitation 1 — Schema-agnostic field validation and coercion

### Approach: SQLite introspection via `PRAGMA table_info`

Add a helper to `db_utils.py` that reads column metadata directly from the live database.
No new CLI args; no schema YAML required. The DB is already the source of truth.

### Changes to `db_utils.py`

**Add `get_table_columns(conn, table) -> dict[str, str]`**

```python
def get_table_columns(conn: sqlite3.Connection, table: str) -> dict[str, str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {row["name"]: row["type"] for row in rows}
```

Returns `{column_name: sql_type}` (e.g. `{"uuid": "TEXT", "time": "INTEGER", ...}`).

**Add `coerce_for_type(field, raw, sql_type) -> Any`**

Replaces the hardcoded `coerce_value()` for CLI-originated string values:

```
NA or None → None (SQL NULL)
sql_type == "INTEGER":
    accept plain integer strings ("0", "42") → int
    accept bool-like strings ("true", "yes", "1") → 1
                              ("false", "no", "0") → 0
    anything else → error, exit 1
sql_type == "REAL":
    float(raw) → error on failure, exit 1
sql_type == "TEXT" / "BLOB" / anything else:
    return raw as-is
```

Because SQLite stores booleans as INTEGER and does not distinguish them from plain integers,
all INTEGER columns accept both numeric and bool-like inputs. This is a deliberate trade-off:
we lose strict int-vs-bool enforcement but gain schema-agnostic coercion without needing a
schema YAML.

The existing `coerce_value()` stays in `db_utils.py` unchanged. It is still used by any
caller that passes already-typed values.

### Changes to `db_list.py`

- Import `get_table_columns`; drop `TASK_FIELDS`.
- After `get_connection()`, call `get_table_columns(conn, table)`.
- Validate filter field names against the returned column dict.

```python
conn = get_connection(db_path)
try:
    columns = get_table_columns(conn, table)
    bad = [f for f in filters if f not in columns]
    if bad:
        return {"status": "error", "message": f"unknown fields: {bad}"}
    ...
```

### Changes to `db_purge.py`

Identical pattern to `db_list.py`: open connection, get columns, validate filter keys.

### Changes to `db_update.py`

Two sites change:

**Pure function `db_update()`** — validate field names via introspection:

```python
conn = get_connection(db_path)
try:
    columns = get_table_columns(conn, table)
    bad = [f for f in updates if f not in columns or f in IMMUTABLE]
    if bad:
        return {"status": "error", "message": f"unknown or immutable fields: {bad}"}
    ...
```

**`main()`** — coerce CLI strings using PRAGMA types instead of `coerce_value()`:

```python
# open a temporary connection to get column types
conn_tmp = get_connection(args.db_path)
columns = get_table_columns(conn_tmp, args.table)
conn_tmp.close()

updates: dict[str, Any] = {}
for token in args.fields:
    field, _, raw_val = token.partition("=")
    sql_type = columns.get(field, "TEXT")
    updates[field] = coerce_for_type(field, raw_val, sql_type)
```

This opens two connections in the CLI path (one in `main()` for types, one inside
`db_update()` for the actual update). That is acceptable overhead for a CLI tool.

### `TASK_FIELDS` retention

`TASK_FIELDS` stays in `db_utils.py`. It is not removed because it may still be
referenced by other callers or future tools. The three scripts above simply stop
importing it.

---

## Limitation 2 — Union intermediate-level scalar fields

### Change to `create_db_schema.py`

In the `create_db_schema()` function, the loop that builds `hierarchy.levels` currently
samples only `arr[0]` for non-leaf levels. Replace that with a union across all items,
matching the leaf-level logic already in place.

**Before (lines ~119–122):**

```python
arr = cursor.get(key, [])
first = arr[0] if arr and isinstance(arr[0], dict) else {}
promote = _scalar_fields(first)
...
cursor = first
```

**After:**

```python
arr = cursor.get(key, [])
all_items = [item for item in arr if isinstance(item, dict)]
promote: dict[str, str] = {}
for item in all_items:
    promote.update(_scalar_fields(item))
cursor = all_items[0] if all_items else {}
```

Navigation to the next level still uses `all_items[0]` (DFS must follow one path).
Only `promote` collection changes — it now reflects the full union of scalar fields
seen across every item at that intermediate level.

---

## Impact on Tests

### `tests/test_db_table_create.py`

No changes required. `db_table_create.py` is unaffected.

### `tests/test_create_db_schema.py`

Add one new test:

| Test | What it checks |
|---|---|
| `test_unions_intermediate_fields` | If two items at the same intermediate level each have a unique scalar field, both appear in the level's `promote` dict |

### `tests/test_db_list.py` / `tests/test_db_purge.py` / `tests/test_db_update.py`

Existing behaviour tests are unaffected (same valid/invalid field semantics).

Add two new tests per script:

| Test | What it checks |
|---|---|
| `test_unknown_field_rejected` | Filter/update with a column that does not exist in the table → `status: error` |
| `test_valid_field_accepted` | Filter/update using a column present in the schema-generated table but absent from `TASK_FIELDS` (e.g. `shop_steward`, `location_steward`) → `status: ok` (proves `TASK_FIELDS` is no longer the gatekeeper; uses the existing `fresh_db` fixture, no extra setup needed) |

---

## Non-Goals

- Removing `TASK_FIELDS` from `db_utils.py` — left in place; not imported by the three scripts after this change.
- Making `coerce_value()` generic — it is kept as-is; `coerce_for_type()` is a new, parallel function.
- Extending `db_replicate`, `db_read`, `db_delete`, `task_id_to_uuid`, or `db_validate_task_table` — none use `TASK_FIELDS` for field validation.
