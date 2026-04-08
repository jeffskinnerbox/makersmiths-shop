"""tests/test_signup_sheet_builder.py"""

import sys
import base64
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from signup_sheet_builder import (  # noqa: E402
    detect_format,
    extract_locations,
    load_yaml,
    make_qr_b64,
    attach_qr_codes,
    render_sheet,
)


OPPORTUNITY_YAML = {
    "opportunity": {
        "shop": {
            "name": "Makersmiths Leesburg (MSL)",
            "steward": "John Carter",
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
                                    "task_id": "MSL-METAL-001",
                                    "frequency": "Weekly",
                                },
                                {
                                    "task": "Vacuum floor",
                                    "task_id": "MSL-METAL-002",
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

TASKS_LIST_YAML = {
    "tasks_list": {
        "shop": {
            "name": "Makersmiths Leesburg (MSL)",
            "area": [
                {
                    "name": "Main Level",
                    "location": [
                        {
                            "name": "3D Printing",
                            "steward": "Bryan Daniels",
                            "work_tasks": [
                                {
                                    "task": "Dust machines",
                                    "task_id": "MSL-3DP-001",
                                    "frequency": "Weekly",
                                },
                            ],
                        }
                    ],
                }
            ],
        }
    }
}


def test_detect_format_opportunity():
    assert detect_format(OPPORTUNITY_YAML) == "opportunity"


def test_detect_format_tasks_list():
    assert detect_format(TASKS_LIST_YAML) == "tasks_list"


def test_detect_format_unknown_raises():
    with pytest.raises(ValueError, match="Unknown YAML format"):
        detect_format({"other_key": {}})


def test_extract_locations_opportunity_count():
    locs = extract_locations(OPPORTUNITY_YAML)
    assert len(locs) == 1


def test_extract_locations_opportunity_name():
    locs = extract_locations(OPPORTUNITY_YAML)
    assert locs[0]["name"] == "Metalshop"


def test_extract_locations_opportunity_steward():
    locs = extract_locations(OPPORTUNITY_YAML)
    assert locs[0]["steward"] == "Brad Hess"


def test_extract_locations_opportunity_task_count():
    locs = extract_locations(OPPORTUNITY_YAML)
    assert len(locs[0]["tasks"]) == 2


def test_extract_locations_opportunity_task_fields():
    locs = extract_locations(OPPORTUNITY_YAML)
    task = locs[0]["tasks"][0]
    assert task["name"] == "Wipe machines"
    assert task["task_id"] == "MSL-METAL-001"
    assert task["frequency"] == "Weekly"


def test_extract_locations_tasks_list_format():
    locs = extract_locations(TASKS_LIST_YAML)
    assert locs[0]["name"] == "3D Printing"
    assert locs[0]["tasks"][0]["task_id"] == "MSL-3DP-001"


def test_extract_locations_missing_task_id_defaults_na():
    data = {
        "opportunity": {
            "shop": {
                "area": [
                    {
                        "location": [
                            {
                                "name": "X",
                                "steward": "Y",
                                "work_tasks": [
                                    {"task": "No ID task", "frequency": "Weekly"}
                                ],
                            }
                        ]
                    }
                ]
            }
        }
    }
    locs = extract_locations(data)
    assert locs[0]["tasks"][0]["task_id"] == "NA"


def test_make_qr_b64_returns_string():
    result = make_qr_b64("https://makersmiths.org")
    assert isinstance(result, str)
    assert len(result) > 100


def test_make_qr_b64_is_valid_base64():
    result = make_qr_b64("https://makersmiths.org")
    decoded = base64.b64decode(result)
    assert decoded[:4] == b"\x89PNG"


def test_attach_qr_codes_adds_qr_b64():
    locs = extract_locations(OPPORTUNITY_YAML)
    locs = attach_qr_codes(locs, "https://makersmiths.org")
    for loc in locs:
        for task in loc["tasks"]:
            assert "qr_b64" in task
            assert len(task["qr_b64"]) > 100


def test_attach_qr_codes_all_tasks_same_url():
    locs = extract_locations(OPPORTUNITY_YAML)
    locs = attach_qr_codes(locs, "https://makersmiths.org")
    qr_values = [task["qr_b64"] for loc in locs for task in loc["tasks"]]
    assert len(set(qr_values)) == 1


# ---------------------------------------------------------------------------
# TBD filtering
# ---------------------------------------------------------------------------

TBD_YAML = {
    "tasks_list": {
        "shop": {
            "name": "MSL",
            "area": [
                {
                    "name": "Main Level",
                    "location": [
                        {
                            "name": "Real Location",
                            "steward": "Alice",
                            "work_tasks": [
                                {"task": "Clean tables", "frequency": "Weekly"},
                            ],
                        },
                        {
                            "name": "TBD Location",
                            "steward": "Bob",
                            "work_tasks": [{"task": "TBD"}],
                        },
                        {
                            "name": "Empty Location",
                            "steward": "Carol",
                            "work_tasks": None,
                        },
                    ],
                }
            ],
        }
    }
}


def test_extract_locations_skips_tbd_by_default():
    locs = extract_locations(TBD_YAML)
    names = [loc["name"] for loc in locs]
    assert "Real Location" in names
    assert "TBD Location" not in names
    assert "Empty Location" not in names


def test_extract_locations_includes_tbd_when_disabled():
    locs = extract_locations(TBD_YAML, skip_tbd=False)
    names = [loc["name"] for loc in locs]
    assert "TBD Location" in names
    assert "Empty Location" in names


def test_extract_locations_tbd_tasks_excluded_within_location():
    """Mixed location: real tasks kept, TBD tasks dropped."""
    data = {
        "tasks_list": {
            "shop": {
                "area": [
                    {
                        "location": [
                            {
                                "name": "Mixed",
                                "steward": "X",
                                "work_tasks": [
                                    {"task": "Real task", "frequency": "Weekly"},
                                    {"task": "TBD"},
                                ],
                            }
                        ]
                    }
                ]
            }
        }
    }
    locs = extract_locations(data)
    assert len(locs) == 1
    assert len(locs[0]["tasks"]) == 1
    assert locs[0]["tasks"][0]["name"] == "Real task"


# ---------------------------------------------------------------------------
# detect_format — opportunities plural key
# ---------------------------------------------------------------------------


def test_detect_format_opportunities():
    data = {"opportunities": {"shop": {}}}
    assert detect_format(data) == "opportunities"


# ---------------------------------------------------------------------------
# load_yaml
# ---------------------------------------------------------------------------


def test_load_yaml_from_path(tmp_path):
    f = tmp_path / "test.yaml"
    f.write_text("tasks_list:\n  shop:\n    name: Test\n")
    data = load_yaml(str(f))
    assert data["tasks_list"]["shop"]["name"] == "Test"


def test_load_yaml_from_file_object(tmp_path):
    f = tmp_path / "test.yaml"
    f.write_text("tasks_list:\n  shop:\n    name: Test\n")
    with open(f) as fh:
        data = load_yaml(fh)
    assert data["tasks_list"]["shop"]["name"] == "Test"


# ---------------------------------------------------------------------------
# render_sheet
# ---------------------------------------------------------------------------


def test_render_sheet_returns_html(tmp_path):
    tmpl = tmp_path / "sheet.html.j2"
    tmpl.write_text(
        "<html>{% for location in locations %}<p>{{ location.name }}</p>{% endfor %}</html>"
    )
    locs = [{"name": "Metalshop", "steward": "Brad", "tasks": []}]
    html = render_sheet(str(tmpl), locs, logo_path=None)
    assert "<p>Metalshop</p>" in html


def test_render_sheet_no_logo_skips_uri(tmp_path):
    tmpl = tmp_path / "sheet.html.j2"
    tmpl.write_text("{% if logo_path %}HAS_LOGO{% endif %}RENDERED")
    html = render_sheet(str(tmpl), [], logo_path=None)
    assert "HAS_LOGO" not in html
    assert "RENDERED" in html


def test_render_sheet_with_logo_embeds_data_uri(tmp_path):
    tmpl = tmp_path / "sheet.html.j2"
    tmpl.write_text("{{ logo_path }}")
    # minimal 1×1 PNG
    png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk"
        "+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )
    logo = tmp_path / "logo.png"
    logo.write_bytes(png)
    html = render_sheet(str(tmpl), [], logo_path=str(logo))
    assert html.startswith("data:image/png;base64,")
