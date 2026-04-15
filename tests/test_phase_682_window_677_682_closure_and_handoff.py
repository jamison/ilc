from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest


THREAT_MODEL_PATH = Path("docs/specs/ilc_privacy_public_legitimacy_threat_model_678_v0.1.md")
OBSERVABILITY_PATH = Path("docs/specs/ilc_public_legitimacy_observability_budget_679_v0.1.md")
MATRIX_PATH = Path("docs/specs/ilc_row_5_mechanism_family_matrix_680_v0.1.md")
SIM_PATH = Path("docs/specs/ilc_row_5_correlation_unlinkability_simulation_packet_681_v0.1.md")
DECISION_PATH = Path("docs/specs/ilc_row_5_prework_narrowing_decision_682_v0.1.md")
HANDOFF_PATH = Path("docs/specs/ilc_window_677_682_handoff_682_v0.1.md")
CHECKLIST_PATH = Path("docs/specs/ilc_option_b_graduation_checklist_state_682_v0.1.json")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v4.3.md")
GUIDE_PATH = Path("docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
MEMPALACE_MANIFEST_PATH = Path("docs/tools/mempalace/ilc_mempalace_current_frontier_manifest_v0.1.json")
GROUPING_PATH = Path("docs/specs/ilc_window_677_682_candidate_phase_grouping_v0.1.md")
FRAME_PATH = Path(
    "docs/research/ilc_window_677_682_privacy_public_legitimacy_conversation_frame_2026_04_15_v0.1.md"
)
INVENTORY_PATH = Path("docs/research/ilc_row_5_canon_inventory_and_issue_register_677_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_682_window_677_682_closure_and_handoff.py")
PHASE_682_SUBJECT_TOKENS = ("row 5", "privacy window")
EXACT_REQUIRED_MAIN_PATHS = {
    str(THREAT_MODEL_PATH),
    str(OBSERVABILITY_PATH),
    str(MATRIX_PATH),
    str(SIM_PATH),
    str(DECISION_PATH),
    str(HANDOFF_PATH),
    str(CHECKLIST_PATH),
    str(CAPSULE_PATH),
    str(GUIDE_PATH),
    str(STATUS_PATH),
    str(GROUPING_PATH),
    str(FRAME_PATH),
    str(INVENTORY_PATH),
    str(TEST_PATH),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(_read(path))


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _subject_matches(subject: str, tokens: tuple[str, ...]) -> bool:
    lowered = subject.lower()
    return all(token in lowered for token in tokens)


def _find_commit_ref(*, subject_tokens: tuple[str, ...]) -> str | None:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if _subject_matches(subject, subject_tokens):
            return commit_hash
    return None


def _resolve_commit_ref(*, subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if _subject_matches(subject, subject_tokens):
            matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError(f"commit_not_present_in_local_history:{subject_tokens}")


def _require_commit_or_skip(subject_tokens: tuple[str, ...]) -> None:
    if _find_commit_ref(subject_tokens=subject_tokens) is None:
        pytest.skip(f"commit_not_yet_present:{subject_tokens}")


def test_threat_model_and_observability_budget_contain_required_tokens() -> None:
    threat_text = _read(THREAT_MODEL_PATH)
    observability_text = _read(OBSERVABILITY_PATH)
    threat_required = (
        "phase_678_threat_model_scopes_row_5_to_correlation_minimization_and_unlinkability",
        "public_submission_privacy_not_private_work_privacy",
        "receipt_exists_but_contributor_linkage_is_target_of_protection",
        "hosted_query_surface_aggregation_is_primary_public_scale_surveillance_vector",
        "operator_path_metadata_and_timing_correlation_are_realistic_secondary_surfaces",
        "namespace_receipt_timing_and_query_pattern_leakage_must_be_modeled_together",
    )
    observability_required = (
        "observability_budget_caps_privacy_mechanism_design_space",
        "machine_legible_receipts_nonnegotiable",
        "receipt_lineage_nonnegotiable",
        "challengeability_nonnegotiable",
        "bounded_human_auditability_nonnegotiable",
        "default_specialized_tooling_requirement_is_inadmissible",
        "receipt_visibility_yes_contributor_linkability_no",
    )
    for token in threat_required:
        assert token in threat_text
    for token in observability_required:
        assert token in observability_text


def test_mechanism_matrix_and_simulation_packet_contain_required_tokens() -> None:
    matrix_text = _read(MATRIX_PATH)
    sim_text = _read(SIM_PATH)
    matrix_required = (
        "three_bucket_mechanism_family_matrix_complete",
        "near_term_tractable_families_preserve_receipt_lineage_and_auditability",
        "later_stage_tractable_families_include_nullifier_and_heavier_zk_variants",
        "presumptively_inadmissible_families_break_queryability_challengeability_or_operator_independence",
        "phase_680_rejection_list_is_more_important_than_premature_family_selection",
    )
    sim_required = (
        "materially_harder_defined_by_degradation_metric_not_narrative_only",
        "phase_681_scopes_to_phase_680_survivor_set",
        "ordinary_observer_recall_below_0_45_is_minimum_materially_harder_threshold",
        "operator_path_recall_below_0_60_is_stretch_target_not_closure_minimum",
        "scenario_level_recall_bands_not_calibrated_outputs",
        "survivor_set_reduces_public_observer_correlation_materially_but_not_perfectly",
        "hosted_query_and_operator_path_surfaces_remain_primary_residual_leakage",
    )
    for token in matrix_required:
        assert token in matrix_text
    for token in sim_required:
        assert token in sim_text


def test_decision_and_handoff_advance_row_5_to_partial_only() -> None:
    decision_text = _read(DECISION_PATH)
    handoff_text = _read(HANDOFF_PATH)
    decision_required = (
        "row_5_advances_to_partial_in_682_not_closed",
        "window_677_682_meets_minimum_acceptable_result_not_best_case_only",
        "remaining_gap_substrate_specific_mechanism_and_live_proof_not_yet_complete",
        "later_cdl_vehicle_plausible_but_not_opened_here",
    )
    handoff_required = (
        "window_677_682_handoff_682_closed",
        "window_677_682_row_5_lane_status_pass",
        "row_5_partial_after_682",
        "cdl_062_still_unopened_after_682",
        "option_d_posture_active_after_682",
        "rows_6_through_9_not_reopened_after_682",
        "window_683_686_legal_positioning_and_opening_readiness_is_next_planned_lane",
        "Disposition: required",
    )
    for token in decision_required:
        assert token in decision_text
    for token in handoff_required:
        assert token in handoff_text


def test_checklist_state_682_advances_row_5_and_preserves_other_rows() -> None:
    data = _read_json(CHECKLIST_PATH)
    rows = {entry["row"]: entry for entry in data["rows"]}
    assert data["option_b_selected"] is False
    assert data["option_d_active"] is True
    assert data["window"] == "677-682"
    assert len(data["rows"]) == 9
    assert rows[
        "1. public init/admission flow tied to canonical receipts"
    ]["status"] == "runtime_closed"
    assert rows[
        "2. machine-legible public receipt issuance and query/runtime contract"
    ]["status"] == "runtime_closed"
    assert rows[
        "3. user and agent visible ECU to ILC lifecycle contract"
    ]["status"] == "runtime_closed"
    assert rows[
        "4. public wallet surface contract sufficient for a first participant-touch economic loop"
    ]["status"] == "runtime_closed"
    assert rows[
        "5. privacy-preserving public legitimacy mechanism at the settlement layer"
    ]["status"] == "partial"
    assert rows[
        "6. coupling invariants that keep protocol truth and graph legitimacy upstream of settlement backend choice"
    ]["status"] == "closed"
    assert rows[
        "7. censorship-resistance requirement for public legitimacy surfaces"
    ]["status"] == "closed"
    assert rows[
        "8. independence from external constitutional centers as a future-substrate selection criterion"
    ]["status"] == "closed"
    assert rows[
        "9. transport and discovery operational maturity threshold for public participant use"
    ]["status"] == "closed"


def test_capsule_v4_3_and_transition_guide_reflect_row_5_partial_and_next_lane() -> None:
    capsule_text = _read(CAPSULE_PATH)
    guide_text = _read(GUIDE_PATH)
    capsule_required = (
        "Capsule v4.3 supersedes v4.2.",
        "Window 677-682 is now closed as the row-5 privacy-preserving public",
        "- row 5 is now `partial`",
        "The next planned lane is Window 683-686 for legal positioning and opening",
    )
    guide_required = (
        "Windows `659-664`, `665-670`, `671-676`, and `677-682` have since completed.",
        "- row `5`: `partial`",
        "- next constitutional target: legal positioning and opening readiness",
        "row `5` advanced from `not_started` to `partial`",
    )
    for token in capsule_required:
        assert token in capsule_text
    for token in guide_required:
        assert token in guide_text


def test_prelock_planning_artifacts_are_marked_historical_after_window_close() -> None:
    grouping = _read(GROUPING_PATH)
    frame = _read(FRAME_PATH)
    inventory = _read(INVENTORY_PATH)
    assert "Historical note, 2026-04-15:" in grouping
    assert "superseded for current-frontier closure status" in grouping
    assert "Historical note, 2026-04-15:" in frame
    assert "superseded for current-frontier closure status" in frame
    assert "Historical note, 2026-04-15:" in inventory
    assert "the lane is now closed as a row-5" in inventory


def test_status_log_records_677_through_682_completion() -> None:
    text = _read(STATUS_PATH)
    required = (
        "## Phase 677",
        "## Phase 678",
        "## Phase 679",
        "## Phase 680",
        "## Phase 681",
        "## Phase 682",
        "Window 677-682 closure and row-5 partial-state handoff",
        "Window 683-686 — legal positioning and opening readiness.",
    )
    for token in required:
        assert token in text
    assert "current 677-682 closure bundle commit" not in text


def test_mempalace_manifest_reflects_682_frontier() -> None:
    data = _read_json(MEMPALACE_MANIFEST_PATH)
    tier_a = set(data["tiers"]["tier_a_canonical"]["include"])
    tier_b = set(data["tiers"]["tier_b_planning"]["include"])
    assert "docs/specs/ilc_antigravity_context_capsule_v4.3.md" in tier_a
    assert "docs/specs/ilc_window_677_682_handoff_682_v0.1.md" in tier_a
    assert "docs/specs/ilc_option_b_graduation_checklist_state_682_v0.1.json" in tier_a
    assert "docs/specs/ilc_row_5_prework_narrowing_decision_682_v0.1.md" in tier_a
    assert "docs/specs/ilc_antigravity_context_capsule_v4.2.md" not in tier_a
    assert "docs/specs/ilc_option_b_graduation_checklist_state_676_v0.1.json" not in tier_a
    assert "docs/specs/ilc_phase_677_682_sequence_lock_v0.1.md" in tier_b
    assert "docs/specs/ilc_window_677_682_candidate_phase_grouping_v0.1.md" in tier_b
    assert "docs/research/ilc_row_5_canon_inventory_and_issue_register_677_v0.1.md" in tier_b
    assert "docs/research/ilc_window_677_682_privacy_public_legitimacy_conversation_frame_2026_04_15_v0.1.md" in tier_b


def test_live_decision_log_still_has_no_cdl_062_row() -> None:
    text = _read(DECISION_LOG_PATH)
    assert "| CDL-062 |" not in text


def test_phase_682_main_commit_path_set_obeys_phase_scope() -> None:
    _require_commit_or_skip(PHASE_682_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_682_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert not any(path.startswith("ilc_core/") for path in changed_paths)
