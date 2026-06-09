# SPDX-License-Identifier: AGPL-3.0-only

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

AUDIT_PATH = (
    REPO_ROOT
    / "docs/specs/ilc_public_repo_disclosure_vs_provisional_coverage_audit_1545p_fix5_v0.1.md"
)
CHECKLIST_PATH = (
    REPO_ROOT / "docs/specs/ilc_phase_1448a_prepublication_review_checklist_v0.1.md"
)
CONTINUATION_PATH = (
    REPO_ROOT / "docs/specs/ilc_soft_rc_private_continuation_plan_1448x_to_1500_v0.1.md"
)


def test_phase_1545p_fix5_audit_records_required_tokens() -> None:
    text = AUDIT_PATH.read_text()

    for token in (
        "repo_disclosure_vs_five_provisional_coverage_audit_phase_1545p_fix5",
        "public_export_surface_rehearsal_passed_phase_1545p_fix5",
        "five_filing_topic_coverage_no_unrouted_material_gap_found_phase_1545p_fix5",
        "human_risk_authorization_relying_on_fedex_delivery_pending_uspto_receipts_phase_1545p_fix5",
        "phase_1448a_e1_resolved_by_human_risk_authorization_phase_1545p_fix5",
        "public_path_may_resume_after_final_publication_gate_phase_1545p_fix5",
        "formal_uspto_receipts_still_pending_phase_1545p_fix5",
    ):
        assert token in text


def test_phase_1545p_fix5_coverage_matrix_includes_all_five_filings() -> None:
    text = AUDIT_PATH.read_text()

    for label in (
        "Filing 1 covers",
        "Filing 2 covers",
        "Filing 3 covers",
        "Filing 4 covers",
        "Filing 5 covers",
    ):
        assert label in text
    assert "No material public-RC disclosure family was found" in text
    assert "No public repository publication by this record" in text
    assert "No USPTO filing receipt" in text
    assert "application-number" in text


def test_phase_1545p_fix5_checklist_marks_e1_resolved_by_risk_authorization() -> None:
    text = CHECKLIST_PATH.read_text()

    assert "Phase 1545p-Fix5 human risk authorization resolves E1" in text
    assert "RESOLVED FOR PROJECT-GOVERNANCE PURPOSES" in text
    assert "formal USPTO filing receipts/application numbers" in text
    assert "remain pending" in text
    assert "Phase 1448b still requires its own exact GO" in text


def test_phase_1545p_fix5_continuation_plan_keeps_publication_gate_separate() -> None:
    text = CONTINUATION_PATH.read_text()

    assert "public_path_may_resume_after_final_publication_gate_phase_1545p_fix5" in text
    assert "This document still does not itself disclose publicly or execute publication." in text
    assert "final publication gate" in text
    assert "exact human GO" in text
