from pathlib import Path


SEQUENCE_SPEC = Path("docs/specs/ilc_main_track_return_sequence_213_221_v0.1.md")
MASTER_PLAN = Path("docs/ILC_Master_Development_Plan_v0.4.md")
TODO_PATH = Path("TODO.txt")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_213_sequence_spec_exists_and_has_locked_window() -> None:
    text = _read(SEQUENCE_SPEC)
    assert "ILC Main-Track Return Sequence 213-221 v0.1" in text
    assert "## 4. Locked Phase Window (213-221)" in text

    expected_rows = (
        "| 213 | `spec` |",
        "| 214 | `integration` |",
        "| 215 | `ratification` |",
        "| 216 | `integration` |",
        "| 217 | `integration` |",
        "| 218 | `integration` |",
        "| 219 | `integration` |",
        "| 220 | `integration` |",
        "| 221 | `closure` |",
    )
    for row in expected_rows:
        assert row in text


def test_phase_213_entry_gate_is_explicit_before_phase_214() -> None:
    text = _read(SEQUENCE_SPEC)
    assert "## 3. Entry Gate Before Phase 214" in text
    assert "validate_phase_prompt.py" in text
    assert "tests/test_main_track_return_sequence_phase_213.py -q" in text
    assert "tests/test_no_ellipses_in_walkthroughs.py -q" in text


def test_phase_213_master_plan_and_todo_reference_sequence_spec() -> None:
    pointer = "docs/specs/ilc_main_track_return_sequence_213_221_v0.1.md"
    master_plan_text = _read(MASTER_PLAN)
    todo_text = _read(TODO_PATH)

    assert pointer in master_plan_text
    assert pointer in todo_text
    assert "[TODO – Main-Track Return Sequence (213-221 Lock)]" in todo_text
