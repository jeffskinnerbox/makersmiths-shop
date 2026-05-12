"""Tests for new db_utils helpers: get_table_columns, coerce_for_type."""

import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from db_utils import coerce_for_type, get_table_columns


def _make_conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        "CREATE TABLE t (id TEXT PRIMARY KEY, count INTEGER, score REAL, notes TEXT)"
    )
    return conn


def test_get_table_columns_returns_name_type_map():
    conn = _make_conn()
    cols = get_table_columns(conn, "t")
    conn.close()
    assert cols == {"id": "TEXT", "count": "INTEGER", "score": "REAL", "notes": "TEXT"}


def test_coerce_na_returns_none():
    assert coerce_for_type("x", "NA", "TEXT") is None


def test_coerce_integer_from_numeric_string():
    assert coerce_for_type("x", "42", "INTEGER") == 42


def test_coerce_integer_from_bool_true():
    assert coerce_for_type("x", "true", "INTEGER") == 1
    assert coerce_for_type("x", "yes", "INTEGER") == 1


def test_coerce_integer_from_bool_false():
    assert coerce_for_type("x", "false", "INTEGER") == 0
    assert coerce_for_type("x", "no", "INTEGER") == 0


def test_coerce_real_from_string():
    assert coerce_for_type("x", "3.14", "REAL") == pytest.approx(3.14)


def test_coerce_text_passthrough():
    assert coerce_for_type("x", "hello world", "TEXT") == "hello world"


def test_coerce_bad_integer_exits():
    with pytest.raises(SystemExit):
        coerce_for_type("x", "notanint", "INTEGER")


def test_coerce_bad_real_exits():
    with pytest.raises(SystemExit):
        coerce_for_type("x", "notafloat", "REAL")
