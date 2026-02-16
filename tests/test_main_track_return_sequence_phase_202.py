from pathlib import Path


SEQUENCE_SPEC = Path("docs/specs/ilc_main_track_return_sequence_202_211_v0.1.md")
TODO_PATH = Path("TODO.txt")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_202_sequence_spec_exists_and_has_locked_window() -> None:
    text = _read(SEQUENCE_SPEC)
    assert "ILC Main-Track Return Sequence 202-211 v0.1" in text
    assert "## 4. Locked Phase Window (202-211)" in text

    expected_rows = (
        "| 202 | `spec` |",
        "| 203 | `integration` |",
        "| 204 | `integration` |",
        "| 205 | `integration` |",
        "| 206 | `test` |",
        "| 207 | `integration` |",
        "| 208 | `integration` |",
        "| 209 | `integration` |",
        "| 210 | `integration` |",
        "| 211 | `closure` |",
    )
    for row in expected_rows:
        assert row in text


def test_phase_202_entry_gate_is_explicit_before_phase_203() -> None:
    text = _read(SEQUENCE_SPEC)
    assert "## 3. Entry Gate Before Phase 203" in text
    assert "validate_phase_prompt.py" in text
    assert "tests/test_main_track_return_sequence_phase_202.py -q" in text
    assert "tests/test_no_ellipses_in_walkthroughs.py -q" in text


def test_phase_202_todo_references_new_sequence_spec() -> None:
    todo_text = _read(TODO_PATH)
    assert "docs/specs/ilc_main_track_return_sequence_202_211_v0.1.md" in todo_text
    assert "[TODO – Main-Track Return Sequence (202-211 Lock)]" in todo_text
