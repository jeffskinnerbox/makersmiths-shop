"""task_id_to_uuid — look up the UUID(s) for a given task_id.

Because task_ids are not guaranteed unique, this may return multiple records.

CLI usage:
    python task_id_to_uuid.py <db_path> <table> <task_id>

Module usage:
    from task_id_to_uuid import task_id_to_uuid
    result = task_id_to_uuid("msl.db", "MSL_volunteer_opportunities", "MSL-METAL-002")
"""

import argparse
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from db_utils import get_connection, print_yaml


def task_id_to_uuid(db_path: str, table: str, task_id: str) -> dict[str, Any]:
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            f"SELECT uuid, task_id, task FROM {table} WHERE task_id = ?", (task_id,)
        ).fetchall()
    finally:
        conn.close()

    if not rows:
        return {"status": "error", "message": f"no record with task_id: {task_id}"}

    matches = [{"uuid": r["uuid"], "task_id": r["task_id"], "task": r["task"]} for r in rows]
    return {"status": "ok", "count": len(matches), "matches": matches}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Find the UUID(s) for a given task_id."
    )
    parser.add_argument("db_path", help="Path to the SQLite database")
    parser.add_argument("table", help="Table name")
    parser.add_argument("task_id", help="task_id to look up")
    args = parser.parse_args()
    result = task_id_to_uuid(args.db_path, args.table, args.task_id)
    print_yaml(result)
    if result["status"] == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
