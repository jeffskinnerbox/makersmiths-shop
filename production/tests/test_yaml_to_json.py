"""tests/test_yaml_to_json.py

Tests for scripts/yaml-to-json.py: convert_yaml_to_json().
"""
import importlib.util
import json
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "yaml_to_json",
    Path(__file__).parent.parent / "scripts" / "yaml-to-json.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
convert_yaml_to_json = _mod.convert_yaml_to_json


# ---------------------------------------------------------------------------
# stdout output
# ---------------------------------------------------------------------------

def test_convert_outputs_valid_json_to_stdout(tmp_path, capsys) -> None:
    f = tmp_path / "test.yaml"
    f.write_text("tasks_list:\n  shop:\n    name: Test\n")
    convert_yaml_to_json(str(f))
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["tasks_list"]["shop"]["name"] == "Test"


def test_convert_nested_structure_to_stdout(tmp_path, capsys) -> None:
    f = tmp_path / "test.yaml"
    f.write_text("a:\n  b: 1\n  c:\n    - x\n    - y\n")
    convert_yaml_to_json(str(f))
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["a"]["b"] == 1
    assert data["a"]["c"] == ["x", "y"]


def test_convert_respects_indent_argument(tmp_path, capsys) -> None:
    f = tmp_path / "test.yaml"
    f.write_text("key: value\n")
    convert_yaml_to_json(str(f), indent=4)
    captured = capsys.readouterr()
    # 4-space indent produces lines starting with 4 spaces
    assert "    " in captured.out


# ---------------------------------------------------------------------------
# file output
# ---------------------------------------------------------------------------

def test_convert_writes_to_output_file(tmp_path) -> None:
    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text("key: value\n")
    out_file = tmp_path / "out.json"
    convert_yaml_to_json(str(yaml_file), str(out_file))
    data = json.loads(out_file.read_text())
    assert data["key"] == "value"


def test_convert_file_output_is_valid_json(tmp_path) -> None:
    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text("a: 1\nb: true\nc: null\n")
    out_file = tmp_path / "out.json"
    convert_yaml_to_json(str(yaml_file), str(out_file))
    data = json.loads(out_file.read_text())
    assert data["a"] == 1
    assert data["b"] is True
    assert data["c"] is None


def test_convert_file_output_prints_path_to_stderr(tmp_path, capsys) -> None:
    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text("k: v\n")
    out_file = tmp_path / "out.json"
    convert_yaml_to_json(str(yaml_file), str(out_file))
    captured = capsys.readouterr()
    assert str(out_file) in captured.err


def test_convert_file_output_nothing_on_stdout(tmp_path, capsys) -> None:
    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text("k: v\n")
    out_file = tmp_path / "out.json"
    convert_yaml_to_json(str(yaml_file), str(out_file))
    captured = capsys.readouterr()
    assert captured.out == ""


# ---------------------------------------------------------------------------
# data fidelity
# ---------------------------------------------------------------------------

def test_convert_list_values_preserved(tmp_path, capsys) -> None:
    f = tmp_path / "test.yaml"
    f.write_text("items:\n  - one\n  - two\n  - three\n")
    convert_yaml_to_json(str(f))
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["items"] == ["one", "two", "three"]


def test_convert_empty_yaml_produces_null(tmp_path, capsys) -> None:
    f = tmp_path / "empty.yaml"
    f.write_text("")
    convert_yaml_to_json(str(f))
    captured = capsys.readouterr()
    assert json.loads(captured.out) is None
