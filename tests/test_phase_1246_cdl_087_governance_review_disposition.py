from __future__ import annotations

from pathlib import Path


DISPOSITION = Path("docs/specs/ilc_cdl_087_governance_review_disposition_1246_v0.1.md")
CDL_REGISTER = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")


def _text() -> str:
    return DISPOSITION.read_text(encoding="utf-8")


def test_phase_1246_disposition_exists_and_is_review_only() -> None:
    text = _text()
    assert "REVIEW COMPLETE / RATIFICATION DEFERRED" in text
    assert "cdl_087_governance_review_complete_phase_1246" in text
    assert "cdl_087_ratification_deferred_pending_production_candidate_fetch_evidence" in text
    assert "Boundary:** review-only; no CDL mutation; no ratification" in text


def test_phase_1246_all_six_ratification_conditions_are_mapped() -> None:
    text = _text()
    for index in range(1, 7):
        assert f"### Condition {index}" in text
    assert "condition_1_sim_fetch_01_passed_for_governance_review" in text
    assert "condition_2_production_candidate_tier_classification_open" in text
    assert "condition_3_bootstrap_snapshot_format_open" in text
    assert "condition_4_production_candidate_observability_open" in text
    assert "condition_5_cdl_077_rate_limiter_preserved_pending_final_regression" in text
    assert "condition_6_fetch_incentive_projection_resolved_at_projection_level" in text


def test_phase_1246_sim_fetch_evidence_and_negative_control_are_recorded() -> None:
    text = _text()
    assert "scenario_count = 48" in text
    assert "pass = 38" in text
    assert "overall_robustness_verdict = pass" in text
    assert "stale_directory_one_hop_negative_control" in text
    assert "stale_directory_two_hop_rescue" in text
    assert "low_holder_adaptive_recovery" in text
    assert "Tier C remains advisory" in text


def test_phase_1246_remaining_blockers_are_explicit() -> None:
    text = _text()
    blockers = [
        "cdl_087_blocker_production_candidate_tier_classification_runtime",
        "cdl_087_blocker_bootstrap_snapshot_builder_and_verifier",
        "cdl_087_blocker_production_candidate_observability_collection_window",
        "cdl_087_blocker_final_cdl_077_rate_limiter_regression",
    ]
    for blocker in blockers:
        assert blocker in text


def test_phase_1246_sensitive_ratification_prompt_gate_is_explicit() -> None:
    text = _text()
    assert "GO CDL-087 ratification evidence phase" in text
    assert "Mutate the CDL register only if all six conditions pass" in text
    assert "CDL-087 ratification;" in text
    assert "CDL register mutation;" in text


def test_phase_1246_cdl_register_remains_open_for_cdl_087() -> None:
    text = CDL_REGISTER.read_text(encoding="utf-8")
    row = next(line for line in text.splitlines() if line.startswith("| CDL-087 |"))
    assert "| open |" in row
    assert " ratified |" not in row
    assert "evidence_document:" not in row
    assert "cdl_087_not_ratified_phase_1227" in row
