"""Tests for db_create."""

from pathlib import Path
from db_create import db_create


def test_creates_db_file(tmp_path):
    db_path = str(tmp_path / "new.db")
    result = db_create(db_path)
    assert result["status"] == "ok"
    assert Path(db_path).exists()


def test_error_if_already_exists(tmp_path):
    db_path = str(tmp_path / "existing.db")
    db_create(db_path)
    result = db_create(db_path)
    assert result["status"] == "error"


def test_overwrite_flag(tmp_path):
    db_path = str(tmp_path / "existing.db")
    db_create(db_path)
    result = db_create(db_path, overwrite=True)
    assert result["status"] == "ok"
