# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Proto1 is a SQLite-backed volunteer task manager for Makersmiths Shop Sergeant. It provides CLI tools (in `scripts/`) that an AI agent will call to manage volunteer work task records. The tools are also importable as modules for composition.

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

# Type check
uv run mypy scripts/

# Create DB and load data
uv run python scripts/db_create.py msl.db
uv run python scripts/db_table_create.py msl.db MSL-volunteer-opportunities.yaml
```

## Architecture

**`scripts/db_utils.py`** — shared foundation imported by all other scripts. Defines `TASK_FIELDS`, `get_connection()` (registers Python `REGEXP` function into SQLite), `new_uuid()`, `row_to_dict()`, `print_yaml()`, and `coerce_value()`.

**Script pattern** — every script in `scripts/` exports a pure function (e.g. `db_read(db_path, table, uuid)`) plus a `main()` CLI wrapper. Tests import the pure functions directly via `sys.path.insert` pointing at `scripts/`.

**`tests/conftest.py`** — provides the `fresh_db` fixture (temp SQLite DB pre-loaded from `MSL-volunteer-opportunities.yaml`) and the `TABLE` constant used by all test modules.

**Data flow**: YAML file → `db_table_create` parses it → each task gets a generated UUID primary key → stored in SQLite. The `task_id` field (user-supplied) is not trusted for uniqueness; UUID is the canonical key.

**Output format**: all tools emit YAML to stdout. Errors go to stderr; scripts exit with code 1 on failure.

## Key Conventions

- `supervision` is stored as `0`/`1` in SQLite (boolean). CLI accepts `true/false/yes/no/0/1`.
- `time` field is stored as `INTEGER` (minutes). Coercion happens in `coerce_value()`.
- `NA` sentinel (string `"NA"`) maps to SQL `NULL`.
- `db_list` and `db_purge` accept `key=regex` filter pairs; filters are AND-combined, case-insensitive via the registered `REGEXP` function.
- `tests/` must NOT have an `__init__.py` — its presence prevents pytest from adding `tests/` to `sys.path`, breaking `from conftest import TABLE` in test files.
