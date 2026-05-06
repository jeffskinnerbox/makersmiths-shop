"""tests/test_parse_opp_tasks.py

Tests for scripts/parse-opp-tasks.py: escape() and generate_markdown().
This script only handles the 'opportunities' root key and produces 5-column tables.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "parse_opp_tasks",
    Path(__file__).parent.parent / "scripts" / "parse-opp-tasks.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
escape = _mod.escape
generate_markdown = _mod.generate_markdown


SAMPLE_YAML = {
    "opportunities": {
        "shop": {
            "name": "Makersmiths Leesburg",
            "address": "123 Main St",
            "steward": "Jeff Irland",
            "area": [
                {
                    "name": "Main Level",
                    "location": [
                        {
                            "name": "Metalshop",
                            "steward": "Brad Hess",
                            "work_tasks": [
                                {
                                    "task": "Clean grinder",
                                    "frequency": "Weekly",
                                    "purpose": "Safety",
                                    "instructions": "Use rag",
                                    "last_date": "2024-03-01",
                                },
                            ],
                        }
                    ],
                }
            ],
        }
    }
}


# ---------------------------------------------------------------------------
# escape()
# ---------------------------------------------------------------------------

def test_escape_pipe_character() -> None:
    assert escape("a|b") == "a\\|b"


def test_escape_multiple_pipes() -> None:
    assert escape("x|y|z") == "x\\|y\\|z"


def test_escape_no_pipe_unchanged() -> None:
    assert escape("hello") == "hello"


def test_escape_non_string_int() -> None:
    assert escape(99) == "99"


# ---------------------------------------------------------------------------
# generate_markdown() — structure
# ---------------------------------------------------------------------------

def test_generate_markdown_h1_heading() -> None:
    md = generate_markdown(SAMPLE_YAML)
    assert "# Makersmiths Volunteer Opportunity Task List" in md


def test_generate_markdown_shop_name() -> None:
    md = generate_markdown(SAMPLE_YAML)
    assert "Makersmiths Leesburg" in md


def test_generate_markdown_shop_address() -> None:
    md = generate_markdown(SAMPLE_YAML)
    assert "123 Main St" in md


def test_generate_markdown_shop_steward() -> None:
    md = generate_markdown(SAMPLE_YAML)
    assert "Jeff Irland" in md


def test_generate_markdown_area_h2_heading() -> None:
    md = generate_markdown(SAMPLE_YAML)
    assert "## Main Level" in md


def test_generate_markdown_location_h3_heading() -> None:
    md = generate_markdown(SAMPLE_YAML)
    assert "### Metalshop" in md


def test_generate_markdown_location_steward() -> None:
    md = generate_markdown(SAMPLE_YAML)
    assert "Brad Hess" in md


# ---------------------------------------------------------------------------
# generate_markdown() — 5-column table content
# ---------------------------------------------------------------------------

def test_generate_markdown_five_column_headers() -> None:
    md = generate_markdown(SAMPLE_YAML)
    assert "Task" in md
    assert "Frequency" in md
    assert "Purpose" in md
    assert "Instructions" in md
    assert "Last Date" in md


def test_generate_markdown_task_name() -> None:
    md = generate_markdown(SAMPLE_YAML)
    assert "Clean grinder" in md


def test_generate_markdown_frequency_value() -> None:
    md = generate_markdown(SAMPLE_YAML)
    assert "Weekly" in md


def test_generate_markdown_purpose_value() -> None:
    md = generate_markdown(SAMPLE_YAML)
    assert "Safety" in md


def test_generate_markdown_instructions_value() -> None:
    md = generate_markdown(SAMPLE_YAML)
    assert "Use rag" in md


def test_generate_markdown_last_date_value() -> None:
    md = generate_markdown(SAMPLE_YAML)
    assert "2024-03-01" in md


# ---------------------------------------------------------------------------
# generate_markdown() — edge cases
# ---------------------------------------------------------------------------

def test_generate_markdown_missing_optional_fields_default_na() -> None:
    data = {
        "opportunities": {
            "shop": {
                "name": "Test",
                "address": "",
                "steward": "",
                "area": [
                    {
                        "name": "Area",
                        "location": [
                            {
                                "name": "Loc",
                                "steward": "X",
                                "work_tasks": [{"task": "Minimal task"}],
                            }
                        ],
                    }
                ],
            }
        }
    }
    md = generate_markdown(data)
    assert "NA" in md


def test_generate_markdown_empty_tasks_shows_placeholder() -> None:
    data = {
        "opportunities": {
            "shop": {
                "name": "Test",
                "address": "",
                "steward": "",
                "area": [
                    {
                        "name": "Area",
                        "location": [{"name": "Loc", "steward": "X", "work_tasks": []}],
                    }
                ],
            }
        }
    }
    md = generate_markdown(data)
    assert "???" in md


def test_generate_markdown_plain_string_task() -> None:
    data = {
        "opportunities": {
            "shop": {
                "name": "Test",
                "address": "",
                "steward": "",
                "area": [
                    {
                        "name": "Area",
                        "location": [
                            {"name": "Loc", "steward": "X", "work_tasks": ["String task"]},
                        ],
                    }
                ],
            }
        }
    }
    md = generate_markdown(data)
    assert "String task" in md


def test_generate_markdown_plain_string_task_fills_na_columns() -> None:
    data = {
        "opportunities": {
            "shop": {
                "name": "Test",
                "address": "",
                "steward": "",
                "area": [
                    {
                        "name": "Area",
                        "location": [
                            {"name": "Loc", "steward": "X", "work_tasks": ["String task"]},
                        ],
                    }
                ],
            }
        }
    }
    md = generate_markdown(data)
    # Plain strings get NA for all other columns
    assert "NA" in md


def test_generate_markdown_pipe_in_value_escaped() -> None:
    data = {
        "opportunities": {
            "shop": {
                "name": "Test",
                "address": "",
                "steward": "",
                "area": [
                    {
                        "name": "Area",
                        "location": [
                            {
                                "name": "Loc",
                                "steward": "X",
                                "work_tasks": [
                                    {"task": "A|B task", "frequency": "Daily"}
                                ],
                            }
                        ],
                    }
                ],
            }
        }
    }
    md = generate_markdown(data)
    assert "A\\|B task" in md


def test_generate_markdown_multiple_locations() -> None:
    data = {
        "opportunities": {
            "shop": {
                "name": "Test",
                "address": "",
                "steward": "",
                "area": [
                    {
                        "name": "Area",
                        "location": [
                            {
                                "name": "Laser",
                                "steward": "X",
                                "work_tasks": [{"task": "Task L", "frequency": "Daily"}],
                            },
                            {
                                "name": "Wood",
                                "steward": "Y",
                                "work_tasks": [{"task": "Task W", "frequency": "Weekly"}],
                            },
                        ],
                    }
                ],
            }
        }
    }
    md = generate_markdown(data)
    assert "### Laser" in md
    assert "### Wood" in md
    assert "Task L" in md
    assert "Task W" in md
