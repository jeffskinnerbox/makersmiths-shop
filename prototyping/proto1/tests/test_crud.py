"""Tests for db_read, db_update, db_delete."""

import sqlite3
from db_read import db_read
from db_update import db_update
from db_delete import db_delete
from conftest import TABLE


def _first_uuid(db_path):
    conn = sqlite3.connect(db_path)
    uuid = conn.execute(f"SELECT uuid FROM {TABLE} LIMIT 1").fetchone()[0]
    conn.close()
    return uuid


def test_read_existing(fresh_db):
    uuid = _first_uuid(fresh_db)
    result = db_read(fresh_db, TABLE, uuid)
    assert result["status"] == "ok"
    assert result["record"]["uuid"] == uuid


def test_read_missing(fresh_db):
    result = db_read(fresh_db, TABLE, "00000000-0000-0000-0000-000000000000")
    assert result["status"] == "error"


def test_update_field(fresh_db):
    uuid = _first_uuid(fresh_db)
    result = db_update(fresh_db, TABLE, uuid, {"last_date": "2026-05-06"})
    assert result["status"] == "ok"
    assert result["record"]["last_date"] == "2026-05-06"


def test_update_na_sets_null(fresh_db):
    uuid = _first_uuid(fresh_db)
    db_update(fresh_db, TABLE, uuid, {"last_date": "2026-05-06"})
    result = db_update(fresh_db, TABLE, uuid, {"last_date": None})
    assert result["status"] == "ok"
    assert result["record"]["last_date"] is None


def test_update_immutable_uuid(fresh_db):
    uuid = _first_uuid(fresh_db)
    result = db_update(fresh_db, TABLE, uuid, {"uuid": "new-uuid"})
    assert result["status"] == "error"


def test_update_missing_record(fresh_db):
    result = db_update(fresh_db, TABLE, "00000000-0000-0000-0000-000000000000",
                       {"last_date": "2026-01-01"})
    assert result["status"] == "error"


def test_delete_existing(fresh_db):
    uuid = _first_uuid(fresh_db)
    result = db_delete(fresh_db, TABLE, uuid)
    assert result["status"] == "ok"
    assert result["deleted"]["uuid"] == uuid
    # Confirm it's gone.
    assert db_read(fresh_db, TABLE, uuid)["status"] == "error"


def test_delete_missing(fresh_db):
    result = db_delete(fresh_db, TABLE, "00000000-0000-0000-0000-000000000000")
    assert result["status"] == "error"


def test_update_unknown_field_rejected(fresh_db):
    uuid = _first_uuid(fresh_db)
    result = db_update(fresh_db, TABLE, uuid, {"nonexistent_column": "value"})
    assert result["status"] == "error"
    assert "nonexistent_column" in result["message"]


def test_update_schema_column_not_in_task_fields(fresh_db):
    # shop_steward is in the schema-generated table but absent from TASK_FIELDS.
    # Before this fix, db_update would reject it. After, it must return ok.
    uuid = _first_uuid(fresh_db)
    result = db_update(fresh_db, TABLE, uuid, {"shop_steward": "New Steward"})
    assert result["status"] == "ok"
    assert result["record"]["shop_steward"] == "New Steward"
