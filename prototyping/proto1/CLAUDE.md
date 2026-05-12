# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Proto1 is a SQLite-backed volunteer task manager for Makersmiths Shop Sergeant. It provides CLI tools (in `scripts/`) that an AI agent calls to manage volunteer work task records. Tools are also importable as modules for composition.

## Commands

```bash
# Install deps (use --extra dev for pytest/mypy)
uv sync --extra dev

# Run all tests
uv run pytest ./tests/ -v

# Run a single test file
uv run pytest tests/test_crud.py -v

# Run a single test by name
uv run pytest tests/test_crud.py::test_read_existing -v

# Type check (strict mode)
uv run mypy scripts/

# Generate schema from a data YAML (one-time; hand-edit output before use)
uv run python scripts/create_db_schema.py \
    --yaml_data MSL-volunteer-opportunities.yaml \
    --root opportunities.shop --leaf work_tasks \
    --output msl-schema.yaml

# Create DB and load data (requires schema file)
uv run python scripts/db_create.py msl.db
uv run python scripts/db_table_create.py \
    --db_path msl.db \
    --yaml_data MSL-volunteer-opportunities.yaml \
    --yaml_schema msl-schema.yaml
```

## Architecture

**`scripts/db_utils.py`** — shared foundation imported by all other scripts. Defines `TASK_FIELDS`, `get_connection()` (registers Python `REGEXP` function into SQLite), `new_uuid()`, `row_to_dict()`, `print_yaml()`, `coerce_value()`, `get_table_columns()`, and `coerce_for_type()`.

- `get_table_columns(conn, table) -> dict[str, str]` — reads `PRAGMA table_info(table)`, returns `{column_name: sql_type}`. Used by `db_list`, `db_purge`, and `db_update` to validate field names against the live DB schema instead of the hardcoded `TASK_FIELDS` list.
- `coerce_for_type(field, raw, sql_type) -> Any` — schema-agnostic CLI coercion: `NA`/`None` → `NULL`; `INTEGER` accepts bool-like (`true/yes/1` → 1, `false/no/0` → 0) or numeric strings; `REAL` → float; `TEXT` passthrough. Used by `db_update`'s `main()`.
- `TASK_FIELDS` and `coerce_value()` remain for backward compatibility but are no longer imported by `db_list`, `db_purge`, or `db_update`.

**Script pattern** — every script exports a pure function (e.g. `db_read(db_path, table, uuid)`) plus a `main()` CLI wrapper. Tests import the pure functions directly; `conftest.py` does `sys.path.insert` to `scripts/` so no install is needed.

**`tests/conftest.py`** — provides the `fresh_db` fixture (temp SQLite DB pre-loaded from `MSL-volunteer-opportunities.yaml` + `msl-schema.yaml`), `YAML_FILE`, `SCHEMA_FILE`, and `TABLE` constants used by all test modules.

**Data flow**: schema YAML defines columns, types, coerce rules, and hierarchy traversal config. `create_db_schema.py` generates the schema from any hierarchical data YAML via DFS — it unions scalar fields across **all items** at each intermediate level (not just the first), so promote candidates are never missed. `db_table_create.py` reads both the schema and data YAMLs: it seeds a context dict from `root_promote` scalars, recurses through `levels[].promote` fields at each intermediate level, then merges context + leaf record at the leaf level. Each row gets a generated UUID primary key. The `task_id` field (user-supplied) is not trusted for uniqueness; UUID is the canonical key.

**`msl-schema.yaml`** — hand-edited schema for `MSL-volunteer-opportunities.yaml`. The raw output of `create_db_schema.py` has duplicate column names (shop/area/location all have a `name` field); this file renames them to `shop`, `area`, `location`, `location_steward`, `shop_address`, `shop_steward`. Used by `conftest.py` as `SCHEMA_FILE`.

**Output format**: all tools emit YAML to stdout. Errors go to stderr; scripts exit with code 1 on failure.

## Script Inventory

| Script | Purpose |
|---|---|
| `create_db_schema.py` | Generate schema YAML from hierarchical data YAML (`--yaml_data`, `--root`, `--leaf`, `--output`) |
| `db_create.py` | Create empty SQLite DB (`--overwrite` flag available) |
| `db_table_create.py` | Create table and bulk-load from data + schema YAMLs (`--db_path`, `--yaml_data`, `--yaml_schema`, `--table`) |
| `db_read.py` | Fetch one record by UUID |
| `db_update.py` | Modify fields of a record by UUID |
| `db_delete.py` | Delete one record by UUID |
| `db_list.py` | List records matching `field=regex` filters (AND-combined) |
| `db_purge.py` | Bulk-delete records matching `field=regex` filters |
| `db_replicate.py` | Copy a table (schema + rows) to a new table name |
| `task_id_to_uuid.py` | Resolve a `task_id` → UUID(s); needed because task_id isn't enforced unique |
| `db_validate_task_table.py` | Check task_id uniqueness; returns `unique: true/false` with duplicate list |

## Key Conventions

- `db_table_create.py` now uses **named CLI args** (`--db_path`, `--yaml_data`, `--yaml_schema`, `--table`); positional args were removed.
- `create_db_schema.py` promotes **all scalar fields** at each hierarchy level using field name as column name by default. The generated schema must be hand-edited to rename conflicting column names before use (e.g. three levels all have a field named `name`).
- Table name defaults to YAML filename stem with non-alphanumeric characters replaced by `_` (e.g. `MSL-volunteer-opportunities.yaml` → `MSL_volunteer_opportunities`).
- `supervision` is stored as `0`/`1` in SQLite. CLI accepts `true/false/yes/no/0/1`; use `supervision=0` or `supervision=1` in list/purge filters.
- `time` field is stored as `INTEGER` (minutes). Coercion for CLI inputs happens in `coerce_for_type()`; `coerce_value()` is retained for other callers.
- `NA` sentinel (string `"NA"`) maps to SQL `NULL`.
- `db_list`, `db_purge`, and `db_update` validate field names against the live SQLite schema via `PRAGMA table_info` — they work with any schema-generated table, not just the MSL-specific `TASK_FIELDS` list.
- `db_list` and `db_purge` require at least one filter (prevents accidental full-table operations); filters use `re.search` semantics via the registered `REGEXP` function.
- `tests/` must NOT have an `__init__.py` — its presence prevents pytest from adding `tests/` to `sys.path`, breaking `from conftest import TABLE`.
- mypy runs in `strict` mode (`pyproject.toml`).

## Typical AI Agent Workflow

```bash
# 0. (One-time) Generate schema from data YAML, hand-edit, then load DB
uv run python scripts/create_db_schema.py \
    --yaml_data MSL-volunteer-opportunities.yaml \
    --root opportunities.shop --leaf work_tasks \
    --output msl-schema.yaml
# edit msl-schema.yaml to rename conflicting column names
uv run python scripts/db_create.py msl.db
uv run python scripts/db_table_create.py \
    --db_path msl.db \
    --yaml_data MSL-volunteer-opportunities.yaml \
    --yaml_schema msl-schema.yaml

# 1. Resolve a human-readable task_id to its UUID
uv run python scripts/task_id_to_uuid.py msl.db MSL_volunteer_opportunities MSL-METAL-002

# 2. Read / update / delete by that UUID
uv run python scripts/db_read.py msl.db MSL_volunteer_opportunities <uuid>
uv run python scripts/db_update.py msl.db MSL_volunteer_opportunities <uuid> last_date=2026-05-06
uv run python scripts/db_delete.py msl.db MSL_volunteer_opportunities <uuid>

# 3. Bulk queries
uv run python scripts/db_list.py msl.db MSL_volunteer_opportunities frequency=Weekly location=Metal
uv run python scripts/db_purge.py msl.db MSL_volunteer_opportunities location=^Obsolete$

# 4. Backup before destructive ops
uv run python scripts/db_replicate.py msl.db MSL_volunteer_opportunities tasks_backup
```
