"""Tests for create_db_schema."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from conftest import YAML_FILE


def _schema(yaml_file=YAML_FILE, root="opportunities.shop", leaf="work_tasks"):
    from create_db_schema import create_db_schema
    return create_db_schema(yaml_file, root, leaf)


def test_generates_hierarchy():
    result = _schema()
    levels = result["hierarchy"]["levels"]
    assert [lv["key"] for lv in levels] == ["area", "location", "work_tasks"]


def test_generates_root_promote():
    result = _schema()
    rp = result["hierarchy"]["root_promote"]
    assert rp == {"name": "name", "address": "address", "steward": "steward"}


def test_generates_intermediate_promotes():
    result = _schema()
    levels = {lv["key"]: lv for lv in result["hierarchy"]["levels"]}
    assert "promote" in levels["area"]
    assert levels["area"]["promote"] == {"name": "name"}
    assert "promote" in levels["location"]
    assert levels["location"]["promote"] == {"name": "name", "steward": "steward"}


def test_infers_int_type():
    result = _schema()
    cols = {c["name"]: c for c in result["columns"]}
    assert cols["time"]["type"] == "INTEGER"
    assert cols["time"]["coerce"] == "int"


def test_infers_bool_type():
    result = _schema()
    cols = {c["name"]: c for c in result["columns"]}
    assert cols["supervision"]["type"] == "INTEGER"
    assert cols["supervision"]["coerce"] == "bool"


def test_unions_sparse_fields():
    # frequency/purpose/instructions appear on only some work_tasks records
    result = _schema()
    col_names = [c["name"] for c in result["columns"]]
    assert "frequency" in col_names
    assert "purpose" in col_names
    assert "instructions" in col_names


def test_uuid_column_prepended():
    result = _schema()
    first = result["columns"][0]
    assert first["name"] == "uuid"
    assert first.get("primary_key") is True
    assert first.get("auto") == "uuid4"


def test_bad_root():
    result = _schema(root="nonexistent.path")
    assert result["status"] == "error"
    assert "nonexistent.path" in result["message"]


def test_bad_leaf():
    result = _schema(leaf="nonexistent_leaf")
    assert result["status"] == "error"
    assert "nonexistent_leaf" in result["message"]
