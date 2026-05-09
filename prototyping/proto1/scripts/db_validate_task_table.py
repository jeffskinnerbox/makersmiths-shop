"""db_validate_task_table — check task_id uniqueness across the entire table.

Returns true if all task_ids are unique, false with a list of duplicates otherwise.

CLI usage:
    python db_validate_task_table.py <db_path> <table>

Module usage:
    from db_validate_task_table import db_validate_task_table
    result = db_validate_task_table("msl.db", "MSL_volunteer_opportunities")
"""

import argparse
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from db_utils import get_connection, print_yaml


def db_validate_task_table(db_path: str, table: str) -> dict[str, Any]:
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            f"""
            SELECT task_id, count(*) AS cnt
            FROM {table}
            GROUP BY task_id
            HAVING cnt > 1
            ORDER BY task_id
            """
        ).fetchall()
    finally:
        conn.close()

    if not rows:
        return {"status": "ok", "unique": True}

    duplicates = [{"task_id": r["task_id"], "count": r["cnt"]} for r in rows]
    return {"status": "ok", "unique": False, "duplicates": duplicates}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check task_id uniqueness across the table."
    )
    parser.add_argument("db_path", help="Path to the SQLite database")
    parser.add_argument("table", help="Table name")
    args = parser.parse_args()
    result = db_validate_task_table(args.db_path, args.table)
    print_yaml(result)


if __name__ == "__main__":
    main()
