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
from db_utils import TASK_FIELDS, get_connection, print_yaml, row_to_dict


def db_list(db_path: str, table: str, filters: dict[str, str]) -> dict[str, Any]:
    if not filters:
        return {"status": "error", "message": "at least one filter is required"}

    bad = [f for f in filters if f not in TASK_FIELDS]
    if bad:
        return {"status": "error", "message": f"unknown fields: {bad}"}

    where = " AND ".join(f"{f} REGEXP ?" for f in filters)
    params = list(filters.values())

    conn = get_connection(db_path)
    try:
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
