from pathlib import Path

import pytest

from ilc_core.epistemic import (
    PRODUCTION_JURY_ACTIVATION_NOT_AUTHORIZED as PACKAGE_PRODUCTION_FLAG,
)
from ilc_core.epistemic.jury_activation_gate import (
    JURY_ACTIVATION_GATE_VERSION_1427,
    PRODUCTION_JURY_ACTIVATION_NOT_AUTHORIZED,
    GateConditionStatus,
    evaluate_jury_activation_gate,
)


ROOT = Path(__file__).resolve().parents[1]
GATE_MODULE = ROOT / "ilc_core/epistemic/jury_activation_gate.py"
PHASE_REPORT = ROOT / "docs/specs/ilc_production_jury_activation_gate_pass_1427_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1427_j008_gate_rerun_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1399_1428_sequence_lock_v0.1.md"
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1427_g8_j008_gate_rerun.md"

PHASE_1427_TOKENS = (
    "production_jury_activation_gate_pass_phase_1427",
    "j008_gate_rerun_phase_1427",
    "production_jury_activation_authorized_phase_1427",
    "all_10_conditions_met_phase_1427",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_evaluate_jury_activation_gate_passes_after_phase_1427() -> None:
    report = evaluate_jury_activation_gate()
    assert report.verdict == "PASS"
    assert report.blocking_not_met == []
    assert report.production_activated is True
    assert report.runtime_version == JURY_ACTIVATION_GATE_VERSION_1427


def test_production_authorization_guard_is_false_after_phase_1427() -> None:
    assert PRODUCTION_JURY_ACTIVATION_NOT_AUTHORIZED is False
    assert PACKAGE_PRODUCTION_FLAG is False


def test_all_10_conditions_are_met() -> None:
    report = evaluate_jury_activation_gate()
    assert len(report.conditions) == 10
    assert all(condition.status == GateConditionStatus.MET for condition in report.conditions)


@pytest.mark.parametrize("token", PHASE_1427_TOKENS)
def test_phase_1427_tokens_present_in_module_phase_tokens(token: str) -> None:
    report = evaluate_jury_activation_gate()
    assert token in report.phase_tokens
    assert token in _read(GATE_MODULE)


def test_historical_tokens_still_preserved() -> None:
    report = evaluate_jury_activation_gate()
    for token in (
        "production_jury_activation_gate_defined_phase_j008",
        "production_jury_activation_not_authorized_phase_j008",
        "j008_gate_verdict_incomplete",
        "j008_gate_verdict_still_incomplete_pending_production_go_phase_1425",
    ):
        assert token in report.phase_tokens


def test_phase_1427_report_walkthrough_and_status_backfills() -> None:
    combined = "\n".join(
        _read(path) for path in (PHASE_REPORT, WALKTHROUGH, STATUS, PLANNING_INDEX, SEQUENCE_LOCK)
    )
    for token in PHASE_1427_TOKENS:
        assert token in combined
    assert 'verdict="PASS"' in combined
    assert "PRODUCTION_JURY_ACTIVATION_NOT_AUTHORIZED=False" in combined
    assert "Phase 1428" in combined


def test_phase_1427_non_authorization_boundary_recorded() -> None:
    text = _read(PHASE_REPORT)
    for phrase in (
        "does not authorize public RC publication",
        "source publication",
        "public repository push",
        "public package upload",
        "release signing",
        "activation-certificate signing",
        "epoch 0-to-1 transition",
        "CDL mutation",
        "Genesis signing",
    ):
        assert phrase in text


def test_phase_1427_prompt_uses_real_phase_1398_test_path() -> None:
    text = _read(PROMPT)
    assert "tests/test_phase_1398_j008_production_jury_activation_gate.py" in text
    assert "tests/test_phase_1398_j008_jury_activation_gate.py" not in text
