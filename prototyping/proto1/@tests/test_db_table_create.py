"""Tests for db_table_create."""

import sqlite3
from db_create import db_create
from db_table_create import db_table_create
from conftest import YAML_FILE


def test_loads_rows(tmp_path):
    db_path = str(tmp_path / "t.db")
    db_create(db_path)
    result = db_table_create(db_path, YAML_FILE)
    assert result["status"] == "ok"
    assert result["rows_loaded"] > 0


def test_table_name_from_yaml_stem(tmp_path):
    db_path = str(tmp_path / "t.db")
    db_create(db_path)
    result = db_table_create(db_path, YAML_FILE)
    assert result["table"] == "MSL_volunteer_opportunities"


def test_table_name_override(tmp_path):
    db_path = str(tmp_path / "t.db")
    db_create(db_path)
    result = db_table_create(db_path, YAML_FILE, table="my_tasks")
    assert result["table"] == "my_tasks"


def test_rows_have_uuid(tmp_path):
    db_path = str(tmp_path / "t.db")
    db_create(db_path)
    db_table_create(db_path, YAML_FILE)
    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT uuid FROM MSL_volunteer_opportunities LIMIT 1"
    ).fetchone()
    conn.close()
    assert row is not None and len(row[0]) == 36  # UUID format


def test_missing_yaml_file(tmp_path):
    db_path = str(tmp_path / "t.db")
    db_create(db_path)
    result = db_table_create(db_path, "/nonexistent/file.yaml")
    assert result["status"] == "error"
