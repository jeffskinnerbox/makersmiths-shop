# tests/test_signup_sheet_template.py
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "signup_sheet_template",
    Path(__file__).parent.parent / "scripts" / "generate-signup-sheet-template.py",
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


def test_build_template_contains_jinja2_for_loop() -> None:
    tmpl = build_template(**make_args())
    assert "{% for location in locations %}" in tmpl


def test_build_template_contains_task_loop() -> None:
    tmpl = build_template(**make_args())
    assert "{% for task in location.tasks %}" in tmpl


def test_build_template_title_embedded() -> None:
    tmpl = build_template(**make_args(title="Custom Title"))
    assert "Custom Title" in tmpl


def test_build_template_default_title() -> None:
    tmpl = build_template(**make_args())
    assert "Volunteer Opportunities" in tmpl


def test_build_template_font_sizes_in_css() -> None:
    tmpl = build_template(**make_args(title_font_size=16))
    assert "font-size: 16pt" in tmpl


def test_build_template_footer_text() -> None:
    tmpl = build_template(**make_args(footer="Contact: test@example.com"))
    assert "Contact: test@example.com" in tmpl


def test_build_template_default_footer() -> None:
    tmpl = build_template(**make_args())
    assert "Jeff Irland (xxx)" in tmpl


def test_build_template_landscape_page() -> None:
    tmpl = build_template(**make_args())
    assert "landscape" in tmpl


def test_build_template_qr_placeholder() -> None:
    tmpl = build_template(**make_args())
    assert "qr_b64" in tmpl


def test_build_template_logo_conditional() -> None:
    tmpl = build_template(**make_args())
    assert "logo_path" in tmpl
    assert "Makersmiths" in tmpl


# ---------------------------------------------------------------------------
# Additional font-size and template variable coverage
# ---------------------------------------------------------------------------

def test_build_template_location_font_size_in_css() -> None:
    tmpl = build_template(**make_args(location_font_size=14))
    assert "font-size: 14pt" in tmpl


def test_build_template_steward_font_size_in_css() -> None:
    tmpl = build_template(**make_args(steward_font_size=9))
    assert "font-size: 9pt" in tmpl


def test_build_template_footer_font_size_in_css() -> None:
    tmpl = build_template(**make_args(footer_font_size=7))
    assert "font-size: 7pt" in tmpl


def test_build_template_references_task_id() -> None:
    tmpl = build_template(**make_args())
    assert "task.task_id" in tmpl


def test_build_template_references_task_name() -> None:
    tmpl = build_template(**make_args())
    assert "task.name" in tmpl


def test_build_template_references_task_instructions() -> None:
    tmpl = build_template(**make_args())
    assert "task.instructions" in tmpl


def test_build_template_references_task_last_date() -> None:
    tmpl = build_template(**make_args())
    assert "task.last_date" in tmpl


def test_build_template_references_task_frequency() -> None:
    tmpl = build_template(**make_args())
    assert "task.frequency" in tmpl


def test_build_template_different_font_sizes_produce_different_output() -> None:
    tmpl_a = build_template(**make_args(title_font_size=20))
    tmpl_b = build_template(**make_args(title_font_size=30))
    assert tmpl_a != tmpl_b
