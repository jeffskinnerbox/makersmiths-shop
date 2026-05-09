"""db_delete — delete a single record by UUID.

CLI usage:
    python db_delete.py <db_path> <table> <uuid>

Module usage:
    from db_delete import db_delete
    result = db_delete("msl.db", "MSL_volunteer_opportunities", "<uuid>")
"""

import argparse
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from db_utils import get_connection, print_yaml, row_to_dict


def db_delete(db_path: str, table: str, uuid: str) -> dict[str, Any]:
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            f"SELECT * FROM {table} WHERE uuid = ?", (uuid,)
        ).fetchone()
        if row is None:
            return {"status": "error", "message": f"no record with uuid: {uuid}"}
        deleted = row_to_dict(row)
        conn.execute(f"DELETE FROM {table} WHERE uuid = ?", (uuid,))
        conn.commit()
    finally:
        conn.close()

    return {"status": "ok", "deleted": deleted}


def main() -> None:
    parser = argparse.ArgumentParser(description="Delete a single record by UUID.")
    parser.add_argument("db_path", help="Path to the SQLite database")
    parser.add_argument("table", help="Table name")
    parser.add_argument("uuid", help="UUID of the record to delete")
    args = parser.parse_args()
    result = db_delete(args.db_path, args.table, args.uuid)
    print_yaml(result)
    if result["status"] == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
