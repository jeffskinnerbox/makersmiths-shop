"""db_replicate — copy a table to a new table with the same schema and data.

CLI usage:
    python db_replicate.py <db_path> <src_table> <dst_table>

Module usage:
    from db_replicate import db_replicate
    result = db_replicate("msl.db", "MSL_volunteer_opportunities", "tasks_backup")
"""

import argparse
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from db_utils import get_connection, print_yaml


def db_replicate(db_path: str, src_table: str, dst_table: str) -> dict[str, Any]:
    conn = get_connection(db_path)
    try:
        src_exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (src_table,)
        ).fetchone()
        if src_exists is None:
            return {"status": "error", "message": f"source table not found: {src_table}"}

        dst_exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (dst_table,)
        ).fetchone()
        if dst_exists is not None:
            return {"status": "error", "message": f"destination table already exists: {dst_table}"}

        # Recreate schema then copy rows.
        conn.execute(f"CREATE TABLE {dst_table} AS SELECT * FROM {src_table}")
        conn.commit()

        count = conn.execute(f"SELECT count(*) FROM {dst_table}").fetchone()[0]
    finally:
        conn.close()

    return {
        "status": "ok",
        "src_table": src_table,
        "dst_table": dst_table,
        "rows_copied": count,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Copy a table to a new table with the same schema and data."
    )
    parser.add_argument("db_path", help="Path to the SQLite database")
    parser.add_argument("src_table", help="Source table name")
    parser.add_argument("dst_table", help="Destination table name")
    args = parser.parse_args()
    result = db_replicate(args.db_path, args.src_table, args.dst_table)
    print_yaml(result)
    if result["status"] == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
