"""Regression tests for Phase 1407 CDL-093 maintenance lottery prelock."""

from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PRELOCK_DOC = (
    REPO_ROOT / "docs/specs/ilc_cdl_093_maintenance_lottery_pool_prelock_1407_v0.1.md"
)
CDL_REGISTER = REPO_ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"


REQUIRED_TOKENS = [
    "cdl_093_deliberation_complete_phase_1407",
    "cdl_093_not_ratified_phase_1407",
    "cdl_093_candidate_prelock_constants_recorded_phase_1407",
    "cdl_093_prelock_committed_phase_1407",
    "cdl_093_scope_constants_locked_phase_1407",
]

REQUIRED_CONSTANTS = [
    "MAINTENANCE_LOTTERY_DRAW_MECHANISM",
    "MAINTENANCE_LOTTERY_SHADOW_DRAW_MECHANISM",
    "MAINTENANCE_LOTTERY_POOL_FUNDING_SOURCE",
    "MAINTENANCE_LOTTERY_POOL_FUNDING_FRACTION",
    "MAINTENANCE_POOL_FUNDING_FRACTION_PENDING_SIM",
    "MAINTENANCE_LOTTERY_NONZERO_FUNDING_REQUIRES_SIM",
    "MAINTENANCE_LOTTERY_TASK_ELIGIBILITY_MODE",
    "MAINTENANCE_LOTTERY_MIN_CONTRIBUTION_THRESHOLD",
    "MAINTENANCE_LOTTERY_ANTI_GAMING_CONTROLS",
    "MAINTENANCE_LOTTERY_ECU_DISTRIBUTION_PATH",
    "MAINTENANCE_LOTTERY_SETTLEMENT_BOUNDARY",
    "MAINTENANCE_LOTTERY_DIRECT_ILC_REWARD_ALLOWED",
    "MAINTENANCE_LOTTERY_ACTIVATION_DEFAULT",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _cdl_093_row(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("| CDL-093 |"):
            return line
    raise AssertionError("CDL-093 row not found")


def test_prelock_spec_present_with_required_tokens() -> None:
    text = _read(PRELOCK_DOC)

    for token in REQUIRED_TOKENS:
        assert token in text


def test_q1_through_q4_are_resolved_or_explicitly_carried_forward() -> None:
    text = _read(PRELOCK_DOC)

    assert "## 3. Q1 Resolution - Lottery Draw Mechanism" in text
    assert "## 4. Q2 Resolution - Pool Budget Source and Funding Fraction" in text
    assert "## 5. Q3 Resolution - Task Eligibility and Anti-Gaming Controls" in text
    assert "## 6. Q4 Resolution - ECU Distribution Path and Settlement Boundary" in text
    assert "production_vrf_or_later_ratified_randomness_required" in text
    assert "MAINTENANCE_POOL_FUNDING_FRACTION_PENDING_SIM" in text
    assert "review_lane_passed_maintenance_tasks_only" in text
    assert "cdl_047_treasury_quote_to_phase_1409_default_off_runtime_stub" in text


def test_all_scope_constants_are_locked() -> None:
    text = _read(PRELOCK_DOC)

    for constant in REQUIRED_CONSTANTS:
        assert f"`{constant}`" in text

    assert 'Decimal("0.00")' in text
    assert "false" in text
    assert "not_activated" in text


def test_historical_hardening_cdl_093_open_at_phase_1406_c2() -> None:
    result = subprocess.run(
        [
            "git",
            "show",
            "15992abe:docs/specs/ilc_constitutional_decision_log_v0.1.md",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    row = _cdl_093_row(result.stdout)

    assert "| open |" in row
    assert "opened_phase: 1406" in row
    assert "opening_token: cdl_093_maintenance_lottery_pool_opened_phase_1406" in row
    assert "ratification_status: not_ratified_pending_phase_1408" in row
    assert "ratification_token: cdl_093_ratified_phase_1408" not in row


def test_current_cdl_register_remains_open_and_unratified() -> None:
    row = _cdl_093_row(_read(CDL_REGISTER))

    assert "| open |" in row
    assert "ratification_status: not_ratified_pending_phase_1408" in row
    assert "ratified_phase: 1408" not in row
    assert "ratification_token: cdl_093_ratified_phase_1408" not in row


def test_prelock_does_not_activate_lottery_distribution() -> None:
    text = _read(PRELOCK_DOC)

    assert "CDL-093 remains open and unratified after Phase 1407" in text
    assert "MAINTENANCE_LOTTERY_ACTIVATION_DEFAULT` | `not_activated`" in text
    assert "MAINTENANCE_LOTTERY_LIVE_DRAWS_ALLOWED` | `false`" in text
    assert "MAINTENANCE_LOTTERY_ECU_SETTLEMENT_ALLOWED` | `false`" in text
