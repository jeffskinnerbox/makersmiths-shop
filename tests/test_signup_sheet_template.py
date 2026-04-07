# tests/test_signup_sheet_template.py
import importlib.util
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "signup_sheet_template",
    Path(__file__).parent.parent / "scripts" / "signup-sheet-template.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
build_template = _mod.build_template


def make_args(**overrides):
    defaults = dict(
        title="Volunteer Opportunities",
        location_font_size=12,
        steward_font_size=10,
        title_font_size=14,
        footer_font_size=8,
        footer="Questions concerning the design & use of this form should be sent to Jeff Irland (xxx)",
    )
    defaults.update(overrides)
    return defaults


def test_build_template_contains_jinja2_for_loop():
    tmpl = build_template(**make_args())
    assert "{% for location in locations %}" in tmpl


def test_build_template_contains_task_loop():
    tmpl = build_template(**make_args())
    assert "{% for task in location.tasks %}" in tmpl


def test_build_template_title_embedded():
    tmpl = build_template(**make_args(title="Custom Title"))
    assert "Custom Title" in tmpl


def test_build_template_default_title():
    tmpl = build_template(**make_args())
    assert "Volunteer Opportunities" in tmpl


def test_build_template_font_sizes_in_css():
    tmpl = build_template(**make_args(title_font_size=16))
    assert "font-size: 16pt" in tmpl


def test_build_template_footer_text():
    tmpl = build_template(**make_args(footer="Contact: test@example.com"))
    assert "Contact: test@example.com" in tmpl


def test_build_template_default_footer():
    tmpl = build_template(**make_args())
    assert "Jeff Irland (xxx)" in tmpl


def test_build_template_landscape_page():
    tmpl = build_template(**make_args())
    assert "landscape" in tmpl


def test_build_template_qr_placeholder():
    tmpl = build_template(**make_args())
    assert "qr_b64" in tmpl


def test_build_template_logo_conditional():
    tmpl = build_template(**make_args())
    assert "logo_path" in tmpl
    assert "Makersmiths" in tmpl
