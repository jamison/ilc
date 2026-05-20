"""Regression tests for Phase 1399 CDL-091 opening and prelock."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CDL_LOG = REPO_ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PRELOCK_SPEC = REPO_ROOT / "docs/specs/ilc_cdl_091_jury_incentive_economics_prelock_1399_v0.1.md"

# Phase 1399 C1 commit — CDL-091 register opening (ILC_CDL_MUTATION_AUTHORIZED=1)
# Historical hardening: CDL-091 must appear as `status: open` at this exact commit.
PHASE_1399_C1_COMMIT = "06993864"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _cdl_091_row_at_commit(commit: str) -> str:
    """Read CDL register at a historical commit and return the CDL-091 row."""
    result = subprocess.run(
        ["git", "show", f"{commit}:{CDL_LOG.relative_to(REPO_ROOT)}"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    rows = [line for line in result.stdout.splitlines() if line.startswith("| CDL-091 |")]
    assert len(rows) == 1, (
        f"expected exactly one CDL-091 row at {commit}, found {len(rows)}"
    )
    return rows[0]


def test_cdl_091_register_row_opened_by_phase_1399() -> None:
    # Historical hardening: assert CDL-091 state at Phase 1399 C1 commit.
    row = _cdl_091_row_at_commit(PHASE_1399_C1_COMMIT)

    assert "| open |" in row, f"CDL-091 not open at Phase 1399 C1 commit {PHASE_1399_C1_COMMIT}"
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
    # Historical hardening: check CDL register state at Phase 1399 C1 commit.
    row = _cdl_091_row_at_commit(PHASE_1399_C1_COMMIT)
    text = _text(PRELOCK_SPEC)

    assert "reviewer_payment_status: not_activated" in row
    assert "`REVIEWER_PAYMENT_NOT_ACTIVATED` | `true`" in text
    assert "activate reviewer payments" in text
    assert "does not" in text


def test_phase_1399_does_not_ratify_cdl_091() -> None:
    # Historical hardening: at Phase 1399 C1 commit CDL-091 must be open, not ratified.
    row = _cdl_091_row_at_commit(PHASE_1399_C1_COMMIT)

    assert "| ratified |" not in row, (
        f"CDL-091 must not be ratified at Phase 1399 C1 commit {PHASE_1399_C1_COMMIT}"
    )
    assert "ratification_token: cdl_091_ratified_phase_1400" not in row
