from pathlib import Path

from ilc_core.epistemic.jury_activation_gate import evaluate_jury_activation_gate
from ilc_core.epistemic.jury_assignment_runtime import (
    PRODUCTION_ASSIGNMENT_NOT_ACTIVATED,
    _TOKEN_PRODUCTION_ASSIGNMENT_ACTIVATED,
    _TOKEN_WINDOW_1429_FIRST_PHASE,
)


ROOT = Path(__file__).resolve().parents[1]
JURY_ASSIGNMENT_RUNTIME = ROOT / "ilc_core/epistemic/jury_assignment_runtime.py"
WALKTHROUGH = ROOT / "docs/phases/phase_1429_production_assignment_activation_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1429_1458_sequence_lock_v0.1.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_production_assignment_flag_is_flipped_after_phase_1429() -> None:
    assert PRODUCTION_ASSIGNMENT_NOT_ACTIVATED is False


def test_j008_gate_still_passes_after_assignment_activation() -> None:
    report = evaluate_jury_activation_gate()

    assert report.verdict == "PASS"
    assert report.gate_authorized is True
    assert report.production_activated is False
    assert report.execution_surfaces_activated is False
    assert report.blocking_not_met == []


def test_phase_1429_tokens_are_present_in_runtime_source() -> None:
    source = _read(JURY_ASSIGNMENT_RUNTIME)

    assert _TOKEN_PRODUCTION_ASSIGNMENT_ACTIVATED == "production_assignment_activated_phase_1429"
    assert _TOKEN_WINDOW_1429_FIRST_PHASE == "window_1429_1458_first_phase"
    assert _TOKEN_PRODUCTION_ASSIGNMENT_ACTIVATED in source
    assert _TOKEN_WINDOW_1429_FIRST_PHASE in source


def test_phase_1429_backfills_record_non_public_rc_activation() -> None:
    combined = "\n".join(_read(path) for path in (WALKTHROUGH, STATUS, SEQUENCE_LOCK))

    assert "production_assignment_activated_phase_1429" in combined
    assert "production_assignment_not_activated_flag_flipped_phase_1429" in combined
    assert "j008_gate_still_pass_after_activation_phase_1429" in combined
    assert "window_1429_1458_first_phase" in combined
    assert "public_rc_not_activated_phase_1429" in combined
    assert "Phase 1430" in combined
