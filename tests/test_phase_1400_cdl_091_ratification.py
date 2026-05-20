"""Regression tests for Phase 1400 CDL-091 ratification."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CDL_LOG = REPO_ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
EVIDENCE_DOC = REPO_ROOT / "docs/specs/ilc_cdl_091_jury_incentive_economics_ratification_evidence_1400_v0.1.md"
PRELOCK_DOC = REPO_ROOT / "docs/specs/ilc_cdl_091_jury_incentive_economics_prelock_1399_v0.1.md"
JURY_INCENTIVE_RUNTIME = REPO_ROOT / "ilc_core/epistemic/jury_incentive_runtime.py"
PHASE_1399_C1 = "06993864"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _cdl_091_row(text: str | None = None) -> str:
    if text is None:
        text = _text(CDL_LOG)
    rows = [line for line in text.splitlines() if line.startswith("| CDL-091 |")]
    assert len(rows) == 1, f"expected exactly one CDL-091 row, found {len(rows)}"
    return rows[0]


def test_evidence_doc_present_with_required_tokens() -> None:
    assert EVIDENCE_DOC.exists()
    text = _text(EVIDENCE_DOC)

    for token in [
        "cdl_091_ratified_phase_1400",
        "cdl_091_jury_incentive_economics_ratification_evidence_committed",
        "cdl_091_historical_hardening_phase_1399_ref_asserted",
        "reviewer_payment_not_activated_phase_1400",
    ]:
        assert token in text


def test_all_phase_1399_scope_constants_are_enumerated() -> None:
    text = _text(EVIDENCE_DOC)

    for constant in [
        "PRIMARY_REVIEW_FUNDING_SOURCE",
        "SECONDARY_CONTESTED_FUNDING_SOURCE",
        "BASE_REVIEW_FEE_ECU",
        "PANEL_PAYMENT_MODEL",
        "REGULAR_PANEL_SIZE",
        "OUTSIDER_SEATS",
        "MAX_COMPENSATED_REVIEWERS",
        "REVIEWER_QUORUM_K",
        "ACCURACY_BONUS_MAX_MULTIPLIER",
        "ACCURACY_BONUS_VESTING_EPOCHS",
        "APPEAL_SURVIVAL_WEIGHT",
        "REFUTATION_SURVIVAL_WEIGHT",
        "INDEPENDENT_REVIEWER_CONSENSUS_WEIGHT",
        "LONG_RUN_GRAPH_SURVIVAL_WEIGHT",
        "APPROVAL_BIAS_MIN_REVIEWS",
        "APPROVAL_BIAS_Z_THRESHOLD",
        "OUTLIER_BONUS_ATTENUATION",
        "APPROVAL_ONLY_PAYMENT_REJECTED",
        "REVIEWER_PAYMENT_NOT_ACTIVATED",
    ]:
        assert constant in text
        assert constant in _text(PRELOCK_DOC)


def test_historical_hardening_phase_1399_c1_shows_cdl_091_open() -> None:
    result = subprocess.run(
        ["git", "show", f"{PHASE_1399_C1}:docs/specs/ilc_constitutional_decision_log_v0.1.md"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    row = _cdl_091_row(result.stdout)

    assert "| open |" in row
    assert "opened_phase: 1399" in row
    assert "opening_token: cdl_091_jury_incentive_economics_opened_phase_1399" in row
    assert "ratification_token: cdl_091_ratified_phase_1400" not in row


def test_cdl_091_register_row_ratified_after_phase_1400_c2() -> None:
    row = _cdl_091_row()

    assert "| ratified |" in row
    assert "ratified_phase: 1400" in row
    assert "ratified_date: 2026-05-20" in row
    assert "ratification_token: cdl_091_ratified_phase_1400" in row
    assert (
        "evidence_document: docs/specs/ilc_cdl_091_jury_incentive_economics_ratification_evidence_1400_v0.1.md"
        in row
    )


def test_reviewer_payment_remains_not_activated() -> None:
    row = _cdl_091_row()
    evidence = _text(EVIDENCE_DOC)

    assert "reviewer_payment_status: not_activated" in row
    assert "runtime_activation_status: not_authorized" in row
    assert "reviewer_payment_not_activated_phase_1400" in evidence
    assert not JURY_INCENTIVE_RUNTIME.exists()
    assert "activate reviewer payment" in evidence
    assert "does not" in evidence
