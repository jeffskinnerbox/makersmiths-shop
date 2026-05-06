"""tests/test_parse_tasks.py

Tests for scripts/parse-tasks.py: escape() and generate_markdown().
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "parse_tasks",
    Path(__file__).parent.parent / "scripts" / "parse-tasks.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
escape = _mod.escape
generate_markdown = _mod.generate_markdown


SAMPLE_YAML = {
    "tasks_list": {
        "shop": {
            "name": "Makersmiths Leesburg",
            "address": "123 Main St",
            "area": [
                {
                    "name": "Main Level",
                    "location": [
                        {
                            "name": "Metalshop",
                            "steward": "Brad Hess",
                            "work_tasks": [
                                {
                                    "task": "Wipe machines",
                                    "completion_date": "2024-01-01",
                                    "frequency": "Weekly",
                                },
                                {
                                    "task": "Sweep floor",
                                    "completion_date": "NA",
                                    "frequency": "Daily",
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
    assert escape("a|b|c") == "a\\|b\\|c"


def test_escape_no_pipe_unchanged() -> None:
    assert escape("hello") == "hello"


def test_escape_int_converted_to_string() -> None:
    assert escape(42) == "42"


def test_escape_none_converted_to_string() -> None:
    assert escape(None) == "None"


# ---------------------------------------------------------------------------
# generate_markdown() — structure
# ---------------------------------------------------------------------------

def test_generate_markdown_h1_heading() -> None:
    md = generate_markdown(SAMPLE_YAML)
    assert md.startswith("# Makersmiths Task List")


def test_generate_markdown_contains_shop_name() -> None:
    md = generate_markdown(SAMPLE_YAML)
    assert "Makersmiths Leesburg" in md


def test_generate_markdown_contains_shop_address() -> None:
    md = generate_markdown(SAMPLE_YAML)
    assert "123 Main St" in md


def test_generate_markdown_area_h2_heading() -> None:
    md = generate_markdown(SAMPLE_YAML)
    assert "## Main Level" in md


def test_generate_markdown_location_h3_heading() -> None:
    md = generate_markdown(SAMPLE_YAML)
    assert "### Metalshop" in md


def test_generate_markdown_steward_line() -> None:
    md = generate_markdown(SAMPLE_YAML)
    assert "Brad Hess" in md


# ---------------------------------------------------------------------------
# generate_markdown() — table content
# ---------------------------------------------------------------------------

def test_generate_markdown_table_headers() -> None:
    md = generate_markdown(SAMPLE_YAML)
    assert "Task Name" in md
    assert "Completion Date" in md
    assert "Frequency" in md


def test_generate_markdown_task_name_present() -> None:
    md = generate_markdown(SAMPLE_YAML)
    assert "Wipe machines" in md


def test_generate_markdown_completion_date_present() -> None:
    md = generate_markdown(SAMPLE_YAML)
    assert "2024-01-01" in md


def test_generate_markdown_frequency_present() -> None:
    md = generate_markdown(SAMPLE_YAML)
    assert "Weekly" in md


def test_generate_markdown_multiple_tasks() -> None:
    md = generate_markdown(SAMPLE_YAML)
    assert "Sweep floor" in md
    assert "Daily" in md


# ---------------------------------------------------------------------------
# generate_markdown() — edge cases
# ---------------------------------------------------------------------------

def test_generate_markdown_empty_tasks_shows_placeholder() -> None:
    data = {
        "tasks_list": {
            "shop": {
                "name": "Test",
                "address": "",
                "area": [
                    {
                        "name": "Area",
                        "location": [
                            {"name": "Loc", "steward": "X", "work_tasks": []},
                        ],
                    }
                ],
            }
        }
    }
    md = generate_markdown(data)
    assert "???" in md


def test_generate_markdown_plain_string_task() -> None:
    data = {
        "tasks_list": {
            "shop": {
                "name": "Test",
                "address": "",
                "area": [
                    {
                        "name": "Area",
                        "location": [
                            {"name": "Loc", "steward": "X", "work_tasks": ["Just a string task"]},
                        ],
                    }
                ],
            }
        }
    }
    md = generate_markdown(data)
    assert "Just a string task" in md


def test_generate_markdown_pipe_in_task_name_escaped() -> None:
    data = {
        "tasks_list": {
            "shop": {
                "name": "Test",
                "address": "",
                "area": [
                    {
                        "name": "Area",
                        "location": [
                            {
                                "name": "Loc",
                                "steward": "X",
                                "work_tasks": [{"task": "Check A|B valve", "frequency": "Weekly"}],
                            }
                        ],
                    }
                ],
            }
        }
    }
    md = generate_markdown(data)
    assert "Check A\\|B valve" in md


def test_generate_markdown_opportunities_format() -> None:
    data = {
        "opportunities": {
            "shop": {
                "name": "Opp Shop",
                "address": "456 Elm",
                "area": [
                    {
                        "name": "Upper",
                        "location": [
                            {
                                "name": "Laser",
                                "steward": "Jane",
                                "work_tasks": [{"task": "Clean lens", "frequency": "Monthly"}],
                            }
                        ],
                    }
                ],
            }
        }
    }
    md = generate_markdown(data)
    assert "Opp Shop" in md
    assert "Clean lens" in md


def test_generate_markdown_multiple_locations() -> None:
    data = {
        "tasks_list": {
            "shop": {
                "name": "Test",
                "address": "",
                "area": [
                    {
                        "name": "Area",
                        "location": [
                            {
                                "name": "Loc A",
                                "steward": "X",
                                "work_tasks": [{"task": "Task A", "frequency": "Daily"}],
                            },
                            {
                                "name": "Loc B",
                                "steward": "Y",
                                "work_tasks": [{"task": "Task B", "frequency": "Weekly"}],
                            },
                        ],
                    }
                ],
            }
        }
    }
    md = generate_markdown(data)
    assert "### Loc A" in md
    assert "### Loc B" in md
    assert "Task A" in md
    assert "Task B" in md


def test_generate_markdown_multiple_areas() -> None:
    data = {
        "tasks_list": {
            "shop": {
                "name": "Test",
                "address": "",
                "area": [
                    {
                        "name": "Upper Level",
                        "location": [
                            {"name": "Laser", "steward": "X", "work_tasks": []},
                        ],
                    },
                    {
                        "name": "Lower Level",
                        "location": [
                            {"name": "Wood", "steward": "Y", "work_tasks": []},
                        ],
                    },
                ],
            }
        }
    }
    md = generate_markdown(data)
    assert "## Upper Level" in md
    assert "## Lower Level" in md


def test_generate_markdown_unknown_steward_key_shows_default() -> None:
    """'stward' is not a recognised key; steward should default to '???'."""
    data = {
        "tasks_list": {
            "shop": {
                "name": "Test",
                "address": "",
                "area": [
                    {
                        "name": "Area",
                        "location": [
                            {
                                "name": "Loc",
                                "stward": "Wrong Key Person",  # misspelled — not read
                                "work_tasks": [{"task": "T", "frequency": "Daily"}],
                            }
                        ],
                    }
                ],
            }
        }
    }
    md = generate_markdown(data)
    assert "Wrong Key Person" not in md
    assert "???" in md
