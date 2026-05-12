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
