"""tests/test_signup_sheet.py"""
import sys
import base64
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from signup_sheet import (  # noqa: E402
    detect_format,
    extract_locations,
    make_qr_b64,
    attach_qr_codes,
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
                                {"task": "Wipe machines", "task_id": "MSL-METAL-001", "frequency": "Weekly"},
                                {"task": "Vacuum floor", "task_id": "MSL-METAL-002", "frequency": "Daily"},
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
                                {"task": "Dust machines", "task_id": "MSL-3DP-001", "frequency": "Weekly"},
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


def test_extract_locations_missing_task_id_defaults_empty():
    data = {
        "opportunity": {
            "shop": {
                "area": [{"location": [{"name": "X", "steward": "Y", "work_tasks": [
                    {"task": "No ID task", "frequency": "Weekly"}
                ]}]}]
            }
        }
    }
    locs = extract_locations(data)
    assert locs[0]["tasks"][0]["task_id"] == ""


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
