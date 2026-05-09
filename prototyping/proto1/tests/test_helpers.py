"""Tests for task_id_to_uuid and db_validate_task_table."""

import sqlite3
from task_id_to_uuid import task_id_to_uuid
from db_validate_task_table import db_validate_task_table
from conftest import TABLE


def _known_task_id(db_path):
    conn = sqlite3.connect(db_path)
    tid = conn.execute(f"SELECT task_id FROM {TABLE} WHERE task_id IS NOT NULL LIMIT 1").fetchone()[0]
    conn.close()
    return tid


def test_found(fresh_db):
    task_id = _known_task_id(fresh_db)
    result = task_id_to_uuid(fresh_db, TABLE, task_id)
    assert result["status"] == "ok"
    assert result["count"] >= 1
    assert result["matches"][0]["task_id"] == task_id


def test_not_found(fresh_db):
    result = task_id_to_uuid(fresh_db, TABLE, "DOES-NOT-EXIST-999")
    assert result["status"] == "error"


def test_validate_all_unique(fresh_db):
    result = db_validate_task_table(fresh_db, TABLE)
    assert result["status"] == "ok"
    assert result["unique"] is True


def test_validate_detects_duplicate(fresh_db):
    # Insert a row with an existing task_id to force a duplicate.
    conn = sqlite3.connect(fresh_db)
    import uuid as _uuid
    task_id = conn.execute(
        f"SELECT task_id FROM {TABLE} WHERE task_id IS NOT NULL LIMIT 1"
    ).fetchone()[0]
    conn.execute(
        f"INSERT INTO {TABLE} (uuid, task_id, task) VALUES (?, ?, ?)",
        (str(_uuid.uuid4()), task_id, "Duplicate task for test"),
    )
    conn.commit()
    conn.close()

    result = db_validate_task_table(fresh_db, TABLE)
    assert result["status"] == "ok"
    assert result["unique"] is False
    dup_ids = [d["task_id"] for d in result["duplicates"]]
    assert task_id in dup_ids
