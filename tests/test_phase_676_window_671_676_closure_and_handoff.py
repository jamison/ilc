from __future__ import annotations

import json
from pathlib import Path


THREAT_MODEL_PATH = Path("docs/specs/ilc_censorship_resistance_threat_model_672_v0.1.md")
EXCLUSION_MATRIX_PATH = Path(
    "docs/specs/ilc_external_constitutional_center_and_exclusion_matrix_673_v0.1.md"
)
EXIT_THRESHOLD_PATH = Path("docs/specs/ilc_exitability_and_replayability_threshold_674_v0.1.md")
CRITERIA_LOCK_PATH = Path("docs/specs/ilc_rows_7_8_selection_criteria_lock_675_v0.1.md")
DECISION_PATH = Path("docs/specs/ilc_rows_7_8_ratification_or_threshold_decision_675_v0.1.md")
HANDOFF_PATH = Path("docs/specs/ilc_window_671_676_handoff_676_v0.1.md")
CHECKLIST_PATH = Path("docs/specs/ilc_option_b_graduation_checklist_state_676_v0.1.json")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v4.2.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict:
    return json.loads(_read(path))


def test_threat_model_exists_and_contains_required_tokens() -> None:
    text = _read(THREAT_MODEL_PATH)
    required = (
        "broad_censorship_model_means_practical_exclusion_counts",
        "public_legitimacy_surfaces_include_admission_namespace_quorum_settlement_reputation_and_receipt_lineage",
        "censorship_includes_denial_throttling_routing_namespace_custody_and_sequencing_surfaces",
        "dashboard_provider_shell_and_hosted_api_chokepoints_are_in_scope",
        "one_operator_one_dashboard_one_provider_shell_not_acceptable_as_ordinary_public_legitimacy_posture",
    )
    for token in required:
        assert token in text


def test_exclusion_matrix_exists_and_contains_required_tokens() -> None:
    text = _read(EXCLUSION_MATRIX_PATH)
    required = (
        "external_constitutional_center_means_outside_system_with_de_facto_or_formal_legitimacy_veto",
        "outside_veto_authority_is_presumptively_disqualifying",
        "substrate_families_classified_as_admissible_risky_or_presumptively_inadmissible",
        "genesis_bootstrap_exception_not_equal_to_third_party_sovereign_dependency",
    )
    for token in required:
        assert token in text


def test_exitability_threshold_exists_and_contains_required_tokens() -> None:
    text = _read(EXIT_THRESHOLD_PATH)
    required = (
        "strong_exitability_requires_export_verify_replay_and_migrate_without_operator_consent",
        "row_7_future_substrate_proof_obligations_are_hard_gate",
        "read_only_observation_is_insufficient_for_row_7",
        "state_export_without_replayability_is_insufficient_for_row_7",
        "privileged_original_operator_consent_may_not_be_required_for_exit",
    )
    for token in required:
        assert token in text


def test_criteria_lock_and_decision_artifacts_exist_and_close_rows_7_and_8() -> None:
    lock_text = _read(CRITERIA_LOCK_PATH)
    decision_text = _read(DECISION_PATH)
    lock_required = (
        "rows_7_8_selection_criteria_locked_without_opening_cdl_062",
        "row_7_closed_as_criteria_lock_with_future_proof_obligations",
        "row_8_closed_as_independence_and_exclusion_criteria_lock",
        "future_substrate_must_satisfy_row_7_proof_obligations_before_row_7_compliance_claim",
        "external_constitutional_center_exclusion_is_now_hard_gate_for_later_substrate_work",
    )
    decision_required = (
        "row_7_closed_in_675_if_and_only_if_criteria_and_proof_obligations_locked",
        "row_8_closed_in_675_if_and_only_if_exclusion_matrix_and_independence_definition_locked",
        "cdl_062_remains_unopened_after_675",
        "option_d_remains_active_after_675",
        "row_7_is_not_runtime_proven_here",
        "row_8_is_not_substrate_selection_here",
    )
    for token in lock_required:
        assert token in lock_text
    for token in decision_required:
        assert token in decision_text


def test_handoff_records_window_close_and_next_lane() -> None:
    text = _read(HANDOFF_PATH)
    required = (
        "window_671_676_handoff_676_closed",
        "window_671_676_rows_7_8_lane_status_pass",
        "rows_7_8_closed_after_676_as_criteria_first_locks",
        "row_5_remains_open_after_676",
        "cdl_062_still_unopened_after_676",
        "option_d_posture_active_after_676",
        "window_677_682_privacy_prework_is_next_planned_lane",
        "Disposition: required",
    )
    for token in required:
        assert token in text


def test_checklist_state_676_closes_rows_7_and_8_and_keeps_row_5_open() -> None:
    data = _read_json(CHECKLIST_PATH)
    rows = {entry["row"]: entry for entry in data["rows"]}
    assert data["window"] == "671-676"
    assert rows[
        "5. privacy-preserving public legitimacy mechanism at the settlement layer"
    ]["status"] == "not_started"
    assert rows[
        "7. censorship-resistance requirement for public legitimacy surfaces"
    ]["status"] == "closed"
    assert rows[
        "8. independence from external constitutional centers as a future-substrate selection criterion"
    ]["status"] == "closed"
    assert rows[
        "9. transport and discovery operational maturity threshold for public participant use"
    ]["status"] == "closed"


def test_capsule_v4_2_reflects_closed_rows_7_and_8_and_next_lane() -> None:
    text = _read(CAPSULE_PATH)
    required = (
        "Capsule v4.2 supersedes v4.1.",
        "Window 671-676 is now closed as the rows-7-and-8 censorship-resistance and",
        "- rows 7-8 are now `closed`",
        "The next planned lane is Window 677-682 for privacy-preserving public",
        "Window 671-676 closed rows 7 and 8, did not open `CDL-062`, did not close row",
    )
    for token in required:
        assert token in text
