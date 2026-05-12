"""Tests for db_list, db_purge, db_replicate."""

import sqlite3
from db_list import db_list
from db_purge import db_purge
from db_replicate import db_replicate
from conftest import TABLE


def test_list_requires_filter(fresh_db):
    result = db_list(fresh_db, TABLE, {})
    assert result["status"] == "error"


def test_list_single_filter(fresh_db):
    result = db_list(fresh_db, TABLE, {"location": "Metalshop"})
    assert result["status"] == "ok"
    assert result["count"] > 0
    for rec in result["records"]:
        assert rec["location"] == "Metalshop"


def test_list_multiple_filters(fresh_db):
    result = db_list(fresh_db, TABLE, {"location": "Metalshop", "frequency": "Weekly"})
    assert result["status"] == "ok"
    for rec in result["records"]:
        assert rec["location"] == "Metalshop"


def test_list_regex_case_insensitive(fresh_db):
    result = db_list(fresh_db, TABLE, {"location": "metalshop"})
    assert result["status"] == "ok"
    assert result["count"] > 0


def test_list_unknown_field(fresh_db):
    result = db_list(fresh_db, TABLE, {"nonexistent": "val"})
    assert result["status"] == "error"


def test_purge_requires_filter(fresh_db):
    result = db_purge(fresh_db, TABLE, {})
    assert result["status"] == "error"


def test_purge_deletes_matches(fresh_db):
    before = db_list(fresh_db, TABLE, {"location": "Metalshop"})["count"]
    result = db_purge(fresh_db, TABLE, {"location": "Metalshop"})
    assert result["status"] == "ok"
    assert result["deleted_count"] == before
    after = db_list(fresh_db, TABLE, {"location": "Metalshop"})["count"]
    assert after == 0


def test_replicate_copies_all_rows(fresh_db):
    src_count = sqlite3.connect(fresh_db).execute(
        f"SELECT count(*) FROM {TABLE}"
    ).fetchone()[0]
    result = db_replicate(fresh_db, TABLE, "backup_table")
    assert result["status"] == "ok"
    assert result["rows_copied"] == src_count


def test_replicate_error_if_dst_exists(fresh_db):
    db_replicate(fresh_db, TABLE, "backup_table")
    result = db_replicate(fresh_db, TABLE, "backup_table")
    assert result["status"] == "error"


def test_replicate_error_if_src_missing(fresh_db):
    result = db_replicate(fresh_db, "nonexistent_table", "backup_table")
    assert result["status"] == "error"


def test_list_unknown_field_rejected(fresh_db):
    result = db_list(fresh_db, TABLE, {"nonexistent_column": "val"})
    assert result["status"] == "error"
    assert "nonexistent_column" in result["message"]


def test_list_schema_column_not_in_task_fields(fresh_db):
    # shop_steward is in the schema-generated table but absent from TASK_FIELDS.
    # Before this fix, db_list would reject it. After, it must return ok.
    result = db_list(fresh_db, TABLE, {"shop_steward": ".*"})
    assert result["status"] == "ok"


def test_purge_unknown_field_rejected(fresh_db):
    result = db_purge(fresh_db, TABLE, {"nonexistent_column": "val"})
    assert result["status"] == "error"
    assert "nonexistent_column" in result["message"]


def test_purge_schema_column_not_in_task_fields(fresh_db):
    # shop_steward is in the schema-generated table but absent from TASK_FIELDS.
    result = db_purge(fresh_db, TABLE, {"shop_steward": ".*"})
    assert result["status"] == "ok"
