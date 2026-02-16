from pathlib import Path


SEQUENCE_SPEC = Path("docs/specs/ilc_main_track_return_sequence_post_glossary_v0.1.md")
MASTER_PLAN = Path("docs/ILC_Master_Development_Plan_v0.4.md")
TODO_PATH = Path("TODO.txt")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_192_sequence_spec_exists_and_has_locked_window() -> None:
    text = _read(SEQUENCE_SPEC)
    assert "ILC Main-Track Return Sequence Post-Glossary v0.1" in text
    assert "## 4. Locked Phase Window (192-201)" in text

    expected_rows = (
        "| 192 | `spec` |",
        "| 193 | `integration` |",
        "| 194 | `integration` |",
        "| 195 | `test` |",
        "| 196 | `integration` |",
        "| 197 | `integration` |",
        "| 198 | `integration` |",
        "| 199 | `test` |",
        "| 200 | `integration` |",
        "| 201 | `closure` |",
    )
    for row in expected_rows:
        assert row in text


def test_phase_192_entry_gate_is_explicit_before_phase_193() -> None:
    text = _read(SEQUENCE_SPEC)
    assert "## 3. Entry Gate Before Phase 193" in text
    assert "validate_phase_prompt.py" in text
    assert "tests/test_main_track_return_sequence_phase_192.py -q" in text
    assert "tests/test_no_ellipses_in_walkthroughs.py -q" in text


def test_phase_192_master_plan_and_todo_reference_sequence_spec() -> None:
    master_plan_text = _read(MASTER_PLAN)
    todo_text = _read(TODO_PATH)

    pointer = "docs/specs/ilc_main_track_return_sequence_post_glossary_v0.1.md"
    assert pointer in master_plan_text
    assert pointer in todo_text
    assert "[TODO – Main-Track Return Sequence (Post-Glossary Lock)]" in todo_text
