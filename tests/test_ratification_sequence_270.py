from __future__ import annotations

from pathlib import Path


SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_270_279_sequence_lock_v0.1.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_sequence_lock_artifact_exists() -> None:
    assert SEQUENCE_LOCK_PATH.exists()


def test_sequence_lock_contains_required_sections() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    required = [
        "## 1. Purpose and sequence scope",
        "## 2. Entry state from Phase 269 handoff",
        "## 3. Locked phase table (270-279)",
        "## 4. Per-phase sensitivity classification",
        "## 5. CDL dependency map and ratification ordering",
        "## 6. Mandatory entry/exit gates per phase lane",
        "## 7. Non-goals and out-of-scope boundaries",
        "## 8. Forward pointer",
    ]
    for heading in required:
        assert heading in text


def test_phase_table_covers_270_through_279() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    for phase in range(270, 280):
        assert f"| {phase} |" in text


def test_sensitivity_table_marks_required_sensitive_phases() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    for phase in [272, 273, 274, 276, 277, 279]:
        assert f"| {phase} | sensitive |" in text


def test_cdl_031_is_explicitly_out_of_scope() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    assert "CDL-031" in text
    assert "deferred to Phase 280+" in text


def test_phase_269_verification_gate_reference_present() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    assert "tools/check_cdl_ratification_verification_gate_phase_269.sh" in text


def test_no_cdl_mutation_instructions_in_phase_270_lock() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    assert "open -> ratified" not in text
    assert "ratified_phase:" not in text
