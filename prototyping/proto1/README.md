
# Proto1
This prototype, Proto1, will create a SQLite database populated with a single table contain all the MSL Volunteer Work (aka task).
Python tools will be created that can perform basic database operations on the table.
The intent is to provide these tools to a single AI agentic for managing the status of Volunteer Work tasks.

The database operation defined here are intended to be elementary operation,
and the AI agent will use them, in combination and with additional logic, for more elaborate database queries an operations.

The database created should be in this root directory but
all the tools created should be put in the `scripts` directory.
All test scripts should be put in the `tests` directory.

## Setup

```bash
uv sync              # create venv and install deps
uv sync --extra dev  # include pytest, mypy
```

Run tests:

```bash
uv run pytest ./tests/ -v
```

## Quick Start

```bash
# Generate schema from data YAML (one-time; hand-edit output to rename conflicting columns)
uv run python scripts/create_db_schema.py \
    --yaml_data MSL-volunteer-opportunities.yaml \
    --root opportunities.shop --leaf work_tasks \
    --output msl-schema.yaml

# Create the database and load MSL tasks
uv run python scripts/db_create.py msl.db
uv run python scripts/db_table_create.py \
    --db_path msl.db \
    --yaml_data MSL-volunteer-opportunities.yaml \
    --yaml_schema msl-schema.yaml

# Find a record's UUID
uv run python scripts/task_id_to_uuid.py msl.db MSL_volunteer_opportunities MSL-METAL-002

# Read / update / delete by UUID
uv run python scripts/db_read.py msl.db MSL_volunteer_opportunities <uuid>
uv run python scripts/db_update.py msl.db MSL_volunteer_opportunities <uuid> last_date=2026-05-06
uv run python scripts/db_delete.py msl.db MSL_volunteer_opportunities <uuid>

# List tasks matching regex filters (AND-combined, case-insensitive)
uv run python scripts/db_list.py msl.db MSL_volunteer_opportunities frequency=Weekly
uv run python scripts/db_list.py msl.db MSL_volunteer_opportunities location=Metalshop supervision=0

# Validate task_id uniqueness
uv run python scripts/db_validate_task_table.py msl.db MSL_volunteer_opportunities
```

**Note:** `supervision` is stored as `0` (false) or `1` (true) in SQLite.
Use `supervision=0` or `supervision=1` in list/purge filters.

## Database Operations Supported
* Atomic Operations on Records
  1. create - Creating a unique record id as it key, this operation inserts a single new row into a table,
     pre-populated with all required elements.
  1. read - Using a record id as it key, this operation retrieves a single record
  1. update - Using a record id as it key, this operation modifies one or more elements of a single records.
  1. delete - Using a record id as it key, this operation deletes a single record from the database.
* Multiple Record Operations
  1. list - Matching one or more record elements with regular expression, retrieve all records that match
  1. purge - Matching one or more record elements with regular expression, delete all records that match
  1. replicate - For a specified database table, make a new table with the same content.
* Supporting Information
  1. The output format of the Python CLI tools should be a YAML representation of the output.
  1. The records must have a unique ID over all time.  Uses a UUID as you main key to assure uniqueness.
     The user will provide a `task_id` as there unique id, but cannot be trusted to be unique.
  1. All tools created need to operate as CLI tools,
     but they must also be structure so there core purpose can be loaded as a module by other Python tools.
  1. All tools should should use Pythonic design principles, be well documented internally, and use type hints / static type checking.

## Load Source Data for Database Table
`MSL-volunteer-opportunities.yaml` is an example list of Makersmiths volunteer work tasks.
`msl-schema.yaml` is the hand-edited schema file that describes the SQLite table structure for that data.

The two-step process:
1. **`create_db_schema`** — reads any hierarchical data YAML and auto-generates a schema YAML capturing column names, SQLite types, coerce rules, and hierarchy traversal config. The raw output uses field names as column names by default; hand-edit it to rename conflicts (e.g. three nesting levels all have a field named `name`).
1. **`db_table_create`** — reads both the data YAML and the schema YAML. It traverses the data hierarchy using the schema's `root_promote` and `levels[].promote` config, flattening each leaf record into a row. Works for any hierarchical data file — not just the MSL format.

## Create Tools for Database Operations
1. Create Python tools to perform the following on the SQLite database record (CRUD):
   create (called `db_table_create`),
   read (called `db_read`),
   update (called `db_update`),
   and delete (called `db_delete`) on single SQLite database records.
1. Create Python tools to perform the following on multiple SQLite database records:
   list (called `db_list`), purge (called `db_purge`), replicate (called `db_replicate`).
1. For a user to easily find a records UUID,
   create a Python CLI tool (called `task_id_to_uuid`) that outputs the UUID for a record with a given `task_id`.
1. Create Python tool (called `db_validate_task_table`) to check `task_id` element for uniqueness over the whole table.
   Tool should return `true` or `false` and with a listing of those records that are not unique if `false`.

## Scripts Reference
All scripts in `scripts/` follow the same pattern: a pure function (e.g. `db_read()`) plus a `main()` CLI wrapper.
All output is YAML to `stdout`; errors go to `stderr` with exit code 1.

---

### `db_utils.py` — Shared foundation

Not a standalone script. Imported by every other script. Provides:

* `TASK_FIELDS` — canonical list of all task column names
* `get_connection(db_path)` — opens a SQLite connection with `row_factory` and a Python-backed `REGEXP` function registered
* `new_uuid()` — generates a UUID4 string
* `row_to_dict(row)` — converts a `sqlite3.Row` to a plain dict
* `print_yaml(data)` — serializes data to YAML and prints to stdout
* `coerce_value(field, raw)` — converts CLI string values to the right Python type (`time` → int, `supervision` → bool, `NA` → None)

---

### `create_db_schema.py` — Generate a schema YAML from a data YAML

Walks any hierarchical YAML file via DFS and emits a schema YAML capturing column definitions, SQLite types, coerce rules, and hierarchy traversal config.

```
python create_db_schema.py --yaml_data <file> --root <dot.path> --leaf <key> [--output <schema.yaml>]
```

* `--root` is a dot-separated path to the container node (e.g. `opportunities.shop`).
* `--leaf` is the array key where data records live (e.g. `work_tasks`).
* Infers SQLite type from first non-NA value: `bool` → `INTEGER + coerce: bool`, `int` → `INTEGER + coerce: int`, `float` → `REAL`, else `TEXT`.
* Collects leaf field union across **all** records (handles sparse YAML).
* Promotes all scalar fields from each intermediate level as column candidates.
* Output uses field names as column names by default — hand-edit to rename conflicts before use.
* `--output` omitted → emits to stdout.

---

### `db_create.py` — Create a new database

Creates an empty SQLite database file at the given path.

```
python db_create.py <db_path> [--overwrite]
```

* Fails if the file already exists unless `--overwrite` is passed.
* Outputs `status: ok` with the resolved path on success.

---

### `db_table_create.py` — Create table and load from YAML

Creates a SQLite table in an existing database and bulk-loads records using a schema YAML to drive both the table structure and the data traversal.

```
python db_table_create.py --db_path <db> --yaml_data <data.yaml> --yaml_schema <schema.yaml> [--table <name>]
```

* All arguments are named (no positional args).
* Table name defaults to the data YAML filename stem (non-alphanumeric characters replaced with `_`).
* Reads `hierarchy.root_promote` to seed per-row context from root-level scalars; reads each `levels[].promote` to carry intermediate-level scalars down to leaf rows.
* Works for any hierarchical YAML structure — not MSL-specific.
* Each row gets a generated UUID primary key; `NA` and `None` map to SQL `NULL`; coerce rules applied per schema column spec.
* Outputs row count loaded on success.

---

### `db_read.py` — Read one record by UUID

Fetches a single record by its UUID primary key.

```
python db_read.py <db_path> <table> <uuid>
```

* Returns `status: error` if the UUID doesn't exist.
* Outputs the full record as a YAML dict on success.

---

### `db_list.py` — List records by filter

Lists all records matching one or more `field=regex` filters (AND-combined, case-insensitive).

```
python db_list.py <db_path> <table> field=regex [field=regex ...]
```

* At least one filter is required.
* Filters use Python `re.search` semantics via the registered `REGEXP` SQLite function.
* Outputs a count and list of matching records.

---

### `db_update.py` — Update fields of a record

Modifies one or more fields of a record identified by UUID.

```
python db_update.py <db_path> <table> <uuid> field=value [field=value ...]
```

* `uuid` is immutable and cannot be updated.
* Use `field=NA` to set a field to NULL.
* `time` is coerced to int; `supervision` accepts `true/false/yes/no/0/1`.
* Returns the full updated record on success.

---

### `db_delete.py` — Delete one record by UUID

Deletes a single record identified by UUID.

```
python db_delete.py <db_path> <table> <uuid>
```

* Returns `status: error` if the UUID doesn't exist.
* Outputs the deleted record on success.

---

### `db_purge.py` — Bulk delete by filter

Deletes all records matching one or more `field=regex` filters (AND-combined, case-insensitive).

```
python db_purge.py <db_path> <table> field=regex [field=regex ...]
```

* At least one filter is required to prevent accidental full-table deletion.
* Outputs the count and list of deleted records.

---

### `db_replicate.py` — Copy a table

Copies a table (schema + all rows) to a new table name within the same database.

```
python db_replicate.py <db_path> <src_table> <dst_table>
```

* Fails if the source table doesn't exist or the destination table already exists.
* Outputs source/destination table names and row count copied.

---

### `db_validate_task_table.py` — Check task_id uniqueness

Checks whether all `task_id` values in a table are unique.

```
python db_validate_task_table.py <db_path> <table>
```

* Returns `unique: true` if no duplicates exist.
* Returns `unique: false` with a list of duplicate `task_id` values and their counts if duplicates are found.
* Always exits with code 0 (validation result, not an error condition).

---

### `task_id_to_uuid.py` — Resolve task_id to UUID(s)

Looks up the UUID(s) for a given `task_id`. Because `task_id` is not enforced unique, multiple matches are possible.

```
python task_id_to_uuid.py <db_path> <table> <task_id>
```

* Returns `status: error` if no match is found.
* Outputs a list of `{uuid, task_id, task}` dicts for all matches.

---

