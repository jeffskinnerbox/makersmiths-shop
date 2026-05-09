"""db_create — create an empty SQLite database file.

CLI usage:
    python db_create.py <db_path>

Module usage:
    from db_create import db_create
    db_create("my.db")
"""

import argparse
import sqlite3
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from db_utils import print_yaml


def db_create(db_path: str, overwrite: bool = False) -> dict:
    path = Path(db_path)
    if path.exists() and not overwrite:
        return {"status": "error", "message": f"database already exists: {db_path}"}
    conn = sqlite3.connect(str(path))
    conn.close()
    return {"status": "ok", "db_path": str(path.resolve())}


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an empty SQLite database.")
    parser.add_argument("db_path", help="Path for the new SQLite database file")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite if exists")
    args = parser.parse_args()
    result = db_create(args.db_path, overwrite=args.overwrite)
    print_yaml(result)
    if result["status"] == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
