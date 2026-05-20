"""Regression tests for Phase 1406 CDL-093 maintenance lottery pool opening."""

from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OPENING_DOC = (
    REPO_ROOT / "docs/specs/ilc_cdl_093_maintenance_lottery_pool_opening_1406_v0.1.md"
)
CDL_REGISTER = REPO_ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
GATE_SOURCE = REPO_ROOT / "ilc_core/epistemic/jury_activation_gate.py"


REQUIRED_TOKENS = [
    "cdl_093_maintenance_lottery_pool_opened_phase_1406",
    "cdl_093_not_ratified_phase_1406",
    "cdl_093_deliberation_questions_recorded_phase_1406",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _cdl_093_row(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("| CDL-093 |"):
            return line
    raise AssertionError("CDL-093 row not found")


def test_opening_spec_present_with_required_tokens() -> None:
    text = _read(OPENING_DOC)

    for token in REQUIRED_TOKENS:
        assert token in text


def test_deliberation_questions_q1_through_q4_recorded() -> None:
    text = _read(OPENING_DOC)

    assert "### Q1 — Lottery draw mechanism" in text
    assert "### Q2 — Pool budget source and funding fraction" in text
    assert "### Q3 — Task eligibility criteria and anti-gaming controls" in text
    assert "### Q4 — ECU distribution path and settlement boundary" in text
    assert "pool budget source" in text
    assert "task eligibility" in text
    assert "lottery mechanics" in text
    assert "ECU distribution path" in text
    assert "anti-gaming controls" in text


def test_historical_hardening_cdl_093_absent_at_phase_1404() -> None:
    result = subprocess.run(
        [
            "git",
            "show",
            "608096a3:docs/specs/ilc_constitutional_decision_log_v0.1.md",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    assert "| CDL-093 |" not in result.stdout


def test_current_cdl_register_opens_cdl_093_after_phase_1406_c2() -> None:
    row = _cdl_093_row(_read(CDL_REGISTER))

    assert "| open |" in row
    assert "opened_phase: 1406" in row
    assert "opening_token: cdl_093_maintenance_lottery_pool_opened_phase_1406" in row
    assert "historical_non_ratification_token: cdl_093_not_ratified_phase_1406" in row
    assert "ratification_status: not_ratified_pending_phase_1408" in row
    assert "distribution_status: not_activated" in row


def test_opening_preserves_non_activation_boundaries() -> None:
    text = _read(OPENING_DOC)
    row = _cdl_093_row(_read(CDL_REGISTER))

    assert "CDL-093 is not ratified after Phase 1406" in text
    assert "activate maintenance lottery distribution" in text
    assert "runtime_activation_status: not_authorized" in row
    assert "live_draw_status: not_activated" in row
    assert "ecu_distribution_status: not_activated" in row


def test_j008_maintenance_lottery_gate_not_flipped_by_opening() -> None:
    text = _read(GATE_SOURCE)

    assert 'condition_id="MAINTENANCE_LOTTERY_CDL_RATIFIED"' in text
    assert "status=GateConditionStatus.NOT_MET" in text
    assert "maintenance_lottery_cdl_not_opened_phase_j008" in text
