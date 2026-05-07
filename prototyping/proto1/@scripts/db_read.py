"""db_read — retrieve a single record by UUID.

CLI usage:
    python db_read.py <db_path> <table> <uuid>

Module usage:
    from db_read import db_read
    result = db_read("msl.db", "MSL_volunteer_opportunities", "<uuid>")
"""

import argparse
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from db_utils import get_connection, print_yaml, row_to_dict


def db_read(db_path: str, table: str, uuid: str) -> dict[str, Any]:
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            f"SELECT * FROM {table} WHERE uuid = ?", (uuid,)
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return {"status": "error", "message": f"no record with uuid: {uuid}"}
    return {"status": "ok", "record": row_to_dict(row)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Read a single record by UUID.")
    parser.add_argument("db_path", help="Path to the SQLite database")
    parser.add_argument("table", help="Table name")
    parser.add_argument("uuid", help="UUID of the record to read")
    args = parser.parse_args()
    result = db_read(args.db_path, args.table, args.uuid)
    print_yaml(result)
    if result["status"] == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
