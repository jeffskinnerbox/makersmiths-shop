# tests/test_signup_sheet_template.py
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from signup_sheet_template import build_template  # noqa: E402


def make_args(**overrides):
    defaults = dict(
        title="Volunteer Opportunities",
        location_font_size=12,
        steward_font_size=10,
        title_font_size=14,
        footer_font_size=8,
        footer="Questions concerning the design & use of this form should be sent to Jeff Irland (xxx)",
        output="output/signup-sheet-template.html.j2",
    )
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def test_build_template_contains_jinja2_for_loop():
    tmpl = build_template(make_args())
    assert "{% for location in locations %}" in tmpl


def test_build_template_contains_task_loop():
    tmpl = build_template(make_args())
    assert "{% for task in location.tasks %}" in tmpl


def test_build_template_title_embedded():
    tmpl = build_template(make_args(title="Custom Title"))
    assert "Custom Title" in tmpl


def test_build_template_default_title():
    tmpl = build_template(make_args())
    assert "Volunteer Opportunities" in tmpl


def test_build_template_font_sizes_in_css():
    tmpl = build_template(make_args(title_font_size=16))
    assert "font-size: 16pt" in tmpl


def test_build_template_footer_text():
    tmpl = build_template(make_args(footer="Contact: test@example.com"))
    assert "Contact: test@example.com" in tmpl


def test_build_template_default_footer():
    tmpl = build_template(make_args())
    assert "Jeff Irland (xxx)" in tmpl


def test_build_template_landscape_page():
    tmpl = build_template(make_args())
    assert "landscape" in tmpl


def test_build_template_qr_placeholder():
    tmpl = build_template(make_args())
    assert "qr_b64" in tmpl


def test_build_template_logo_conditional():
    tmpl = build_template(make_args())
    assert "logo_path" in tmpl
    assert "Makersmiths" in tmpl
