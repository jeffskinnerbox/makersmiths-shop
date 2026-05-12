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
