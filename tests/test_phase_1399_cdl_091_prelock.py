"""Regression tests for Phase 1399 CDL-091 opening and prelock."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CDL_LOG = REPO_ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PRELOCK_SPEC = REPO_ROOT / "docs/specs/ilc_cdl_091_jury_incentive_economics_prelock_1399_v0.1.md"
PHASE_1400_EVIDENCE = REPO_ROOT / "docs/specs/ilc_cdl_091_jury_incentive_economics_ratification_evidence_1400_v0.1.md"
JURY_INCENTIVE_RUNTIME = REPO_ROOT / "ilc_core/epistemic/jury_incentive_runtime.py"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _cdl_091_row() -> str:
    text = _text(CDL_LOG)
    rows = [line for line in text.splitlines() if line.startswith("| CDL-091 |")]
    assert len(rows) == 1, f"expected exactly one CDL-091 row, found {len(rows)}"
    return rows[0]


def test_cdl_091_register_row_opened_by_phase_1399() -> None:
    row = _cdl_091_row()

    assert "| open |" in row
    assert "opened_phase: 1399" in row
    assert "opened_date: 2026-05-20" in row
    assert "opening_token: cdl_091_jury_incentive_economics_opened_phase_1399" in row
    assert "predecessor_opening_token: jury_incentive_economics_cdl_opened_phase_j004" in row
    assert "ratification_status: not_ratified_pending_phase_1400" in row
    assert "reviewer_payment_status: not_activated" in row


def test_prelock_spec_present_with_required_tokens() -> None:
    assert PRELOCK_SPEC.exists()
    text = _text(PRELOCK_SPEC)

    for token in [
        "cdl_091_prelock_committed_phase_1399",
        "cdl_091_not_ratified_phase_1399",
        "cdl_091_scope_constants_locked_phase_1399",
    ]:
        assert token in text


def test_prelock_records_funding_source_decisions() -> None:
    text = _text(PRELOCK_SPEC)

    assert "PRIMARY_REVIEW_FUNDING_SOURCE" in text
    assert "fixed_pooled_review_budget" in text
    assert "SECONDARY_CONTESTED_FUNDING_SOURCE" in text
    assert "petition_bond_for_contested_or_escalated_cases" in text
    assert "J-004 left funding source unresolved" in text


def test_prelock_uses_decimal_strings_for_economic_constants() -> None:
    text = _text(PRELOCK_SPEC)

    assert 'BASE_REVIEW_FEE_ECU` | `Decimal("0.05")' in text
    assert 'ACCURACY_BONUS_MAX_MULTIPLIER` | `Decimal("1.00")' in text
    assert 'APPROVAL_BIAS_Z_THRESHOLD` | `Decimal("2.50")' in text
    assert "No Python float value is authorized." in text


def test_reviewer_payment_remains_inactive() -> None:
    row = _cdl_091_row()
    text = _text(PRELOCK_SPEC)

    assert "reviewer_payment_status: not_activated" in row
    assert "`REVIEWER_PAYMENT_NOT_ACTIVATED` | `true`" in text
    assert "activate reviewer payments" in text
    assert "does not" in text


def test_phase_1399_does_not_ratify_cdl_091() -> None:
    row = _cdl_091_row()

    assert "| ratified |" not in row
    assert "ratification_token: cdl_091_ratified_phase_1400" not in row
    assert not PHASE_1400_EVIDENCE.exists()
    assert not JURY_INCENTIVE_RUNTIME.exists()
