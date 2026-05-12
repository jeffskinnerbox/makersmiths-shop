# Schema-Driven DB Table Creation — Design Spec
_Date: 2026-05-12_

## Goal

Replace the hardcoded SQLite schema in `db_table_create.py` with a schema-driven approach. A new tool (`create_db_schema.py`) reads any hierarchical YAML data file and generates a portable schema YAML that captures column definitions, type coercion rules, and hierarchy traversal instructions. The updated `db_table_create.py` consumes both the data YAML and schema YAML, making it work for any arbitrarily-structured data file.

---

## Schema YAML Format

The schema file is the contract between the data YAML and the SQLite table. It has two top-level keys: `hierarchy` and `columns`.

### `hierarchy`

```yaml
hierarchy:
  root: opportunities.shop       # dot-path to the container node in the data YAML
  root_promote:                  # scalars from the root container node itself
    shop: name
    shop_address: address
    shop_steward: steward
  levels:
    - key: area                  # array key to iterate at this level
      promote:                   # scalars from each item of THIS level's array
        area: name
    - key: location
      promote:
        location: name
        location_steward: steward
    - key: work_tasks            # leaf level — rows sourced here; no promote needed
      leaf: true
```

- `root` is a dot-separated path navigated by splitting on `.` and traversing the YAML dict.
- `root_promote` captures scalar fields from the root container node (not from any array). Maps `column_name: field_name`.
- Each entry in `levels` names one array key to iterate. `promote` on a level captures scalars from **each item of that level's own array** — not from the parent. Maps `column_name: field_name`.
- Promoted values accumulate into a context dict that is carried into every descendant row.
- The level marked `leaf: true` is where actual data records live. Its items are merged with the accumulated context to form rows. No `promote` is needed on the leaf level; all item fields are included automatically (filtered to schema columns).
- Only one level may be `leaf: true`; it must be last.

### `columns`

```yaml
columns:
  - name: uuid
    type: TEXT
    primary_key: true
    auto: uuid4          # value is generated, not sourced from data
  - name: task_id
    type: TEXT
  - name: time
    type: INTEGER
    coerce: int
  - name: supervision
    type: INTEGER
    coerce: bool
  - name: frequency
    type: TEXT
  - name: purpose
    type: TEXT
  - name: instructions
    type: TEXT
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

| Field | Required | Values |
|---|---|---|
| `name` | yes | column name in SQLite |
| `type` | yes | `TEXT`, `INTEGER`, `REAL`, `BLOB` |
| `primary_key` | no | `true` |
| `auto` | no | `uuid4` — generates value, ignores data source |
| `coerce` | no | `int`, `bool` — applied after NA/None check |

Coerce semantics (match existing `coerce_value()` behaviour):
- `int`: `int(raw)` — exits with error if conversion fails
- `bool`: `true/yes/1` → `1`, `false/no/0` → `0`, else error
- `NA` string or Python `None` → SQL `NULL` regardless of coerce rule

---

## `create_db_schema.py`

### CLI

```bash
uv run python scripts/create_db_schema.py \
    --yaml_data <yaml_file> \
    --root <dot.path> \
    --leaf <key> \
    [--output <schema.yaml>]
# --output omitted → emit YAML to stdout
```

### Pure function

```python
def create_db_schema(yaml_file: str, root: str, leaf: str) -> dict[str, Any]
```

Returns the schema dict (same structure as the YAML above). `main()` serialises it to `--output` or stdout.

### Algorithm

1. Load YAML; navigate to `root` by splitting on `.` and descending the dict. Error if any segment is missing.
2. DFS from the root node to find the ordered chain of array keys that leads to the first occurrence of `leaf`. This chain becomes `hierarchy.levels`.
3. Collect `root_promote`: all scalar-valued fields (str, int, float, bool) directly on the root container node (i.e. keys whose value is not a list or dict). Column name equals field name by default.
4. For each intermediate level, sample **the first element** of the array and collect all scalar-valued fields as `promote` candidates for that level. Column name equals field name by default.
5. For the leaf level, take the **union of all field keys** across every leaf record in the entire file (handles sparse YAML where optional fields only appear on some records).
6. Infer SQLite type per field from the first non-None/non-NA value seen:
   - Python `bool` → `INTEGER`, `coerce: bool`
   - Python `int` → `INTEGER`, `coerce: int`
   - Python `float` → `REAL`
   - anything else → `TEXT`
7. Prepend a `uuid` column (`type: TEXT, primary_key: true, auto: uuid4`) to `columns`.
8. Return the complete schema dict.

### Errors

| Condition | Behaviour |
|---|---|
| YAML file not found | `status: error` + exit 1 |
| `root` path not found in YAML | `status: error` + exit 1 |
| `leaf` key not reachable from `root` | `status: error` + exit 1 |
| No leaf records found | `status: error` + exit 1 |

---

## Updated `db_table_create.py`

### CLI (breaking change — positional args replaced with named args)

```bash
uv run python scripts/db_table_create.py \
    --db_path <db_path> \
    --yaml_data <yaml_file> \
    --yaml_schema <schema_yaml> \
    [--table <name>]
```

`--table` still overrides the default table name (YAML filename stem, sanitised).

### Pure function

```python
def db_table_create(
    db_path: str,
    yaml_file: str,
    schema_file: str,
    table: str | None = None,
) -> dict[str, Any]
```

### Algorithm

1. Load and validate schema YAML (must have `hierarchy` and `columns` keys).
2. Build `CREATE TABLE` SQL from `columns`: respect `primary_key`, `type`. Use `CREATE TABLE IF NOT EXISTS`.
3. Build a coerce map `{column_name: coerce_rule}` and an auto map `{column_name: generator}` from `columns`.
4. Traverse the data YAML using `hierarchy`:
   - Navigate to `root` node; seed context dict from `root_promote` scalars.
   - Recurse through `levels` in order; at each non-leaf level, iterate the array; for each item, extend a copy of the context with that item's `promote` fields, then descend to the next level.
   - At the leaf level, for each record: merge the accumulated context with all fields from the leaf record item.
5. For each merged row dict:
   - For columns with `auto: uuid4`, generate a fresh UUID (ignore any data value).
   - Map Python `None` and string `"NA"` to SQL `NULL`.
   - Apply `coerce` rules to non-NULL values.
   - Emit only the columns listed in the schema (ignore extra data fields).
6. `executemany` INSERT; commit.
7. Return `{status: ok, table, rows_loaded, db_path}`.

### Errors

| Condition | Behaviour |
|---|---|
| DB file not found | `status: error` + exit 1 |
| Schema file not found | `status: error` + exit 1 |
| Schema missing `hierarchy` or `columns` | `status: error` + exit 1 |
| YAML data file not found | `status: error` + exit 1 |
| `root` not found in data | `status: error` + exit 1 |
| Coerce failure (bad int/bool value) | `status: error` + exit 1 |

---

## Impact on Existing Code

### `db_utils.py`
No changes. `TASK_FIELDS` and `coerce_value()` remain for `db_update`, `db_list`, `db_purge`.

### `tests/conftest.py`
`fresh_db` fixture calls `db_table_create(db_path, YAML_FILE)` today. Must be updated to:

```python
db_table_create(db_path, YAML_FILE, SCHEMA_FILE)
```

`SCHEMA_FILE` points to a pre-generated `msl-schema.yaml` checked into the repo root of proto1.

### `tests/test_db_table_create.py`
All direct calls to `db_table_create(...)` gain the `schema_file` argument. Existing behaviour tests (row count, UUID presence, table name override, missing YAML) are retained; two new tests added:
- `test_missing_schema_file` — schema path does not exist → `status: error`
- `test_bad_hierarchy` — schema root not found in data → `status: error`

### New `tests/test_create_db_schema.py`

| Test | What it checks |
|---|---|
| `test_generates_hierarchy` | levels list matches expected keys |
| `test_infers_int_type` | `time` → `INTEGER + coerce: int` |
| `test_infers_bool_type` | `supervision` → `INTEGER + coerce: bool` |
| `test_unions_sparse_fields` | field present in only some records still appears in schema |
| `test_uuid_column_prepended` | first column is `uuid` with `primary_key: true` |
| `test_bad_root` | error on missing root path |
| `test_bad_leaf` | error on unreachable leaf key |

---

## Workflow (end-to-end)

```bash
# 1. Generate schema from existing data file (one-time or after data structure changes)
uv run python scripts/create_db_schema.py \
    --yaml_data MSL-volunteer-opportunities.yaml \
    --root opportunities.shop \
    --leaf work_tasks \
    --output msl-schema.yaml

# 2. Review / edit msl-schema.yaml (remove unwanted promoted columns, adjust types)

# 3. Create DB and load data
uv run python scripts/db_create.py msl.db
uv run python scripts/db_table_create.py \
    --db_path msl.db \
    --yaml_data MSL-volunteer-opportunities.yaml \
    --yaml_schema msl-schema.yaml

# 4. Run tests
uv run pytest ./tests/ -v
```

---

## Known Limitations

- `db_list`, `db_purge`, `db_update` still validate against the hardcoded `TASK_FIELDS` list in `db_utils.py`. If a schema produces a table with different columns, those tools will reject valid field names. Extending those tools to be schema-aware is out of scope for this change.
- `create_db_schema.py` samples only the **first element** of intermediate levels for promote candidates. If different items at the same level have different scalar fields, some may be missed. The leaf union logic does not apply to intermediate levels.
