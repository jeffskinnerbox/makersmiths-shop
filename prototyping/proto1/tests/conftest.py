"""Shared fixtures for all test modules."""

import sys
from pathlib import Path

import pytest

# Make scripts importable.
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

YAML_FILE = str(Path(__file__).parent.parent / "MSL-volunteer-opportunities.yaml")


@pytest.fixture
def fresh_db(tmp_path):
    """Create a temporary DB pre-loaded with the MSL YAML data."""
    from db_create import db_create
    from db_table_create import db_table_create

    db_path = str(tmp_path / "test.db")
    db_create(db_path)
    db_table_create(db_path, YAML_FILE)
    return db_path


TABLE = "MSL_volunteer_opportunities"
