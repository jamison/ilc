from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    parse_decision_register_rows,
)


OPENING_PATH = Path("docs/specs/ilc_cdl_068_topology_shuffle_authorization_opening_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_736_cdl_068_opening.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_736_g8_cdl_068_topology_shuffle_authorization_opening_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PHASE_736_SUBJECT_TOKEN = "phase 736 cdl-068 topology shuffle authorization opening"
PHASE_736_BACKFILL_SUBJECT_TOKEN = "phase 736 walkthrough and status backfill"
EXACT_REQUIRED_MAIN_PATHS = {
    str(OPENING_PATH),
    str(DECISION_LOG_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    "## 1. Motivation and governing question",
    "## 2. Scope: what CDL-068 governs",
    "## 3. Scope: what CDL-068 does not govern (boundary with CDL-039 and CDL-017)",
    "## 4. Evidence checklist",
    "## 5. Prelock criteria",
    "## 6. Non-goals",
)
REQUIRED_TOKENS = (
    "cdl_068_opens_phase_736",
    "new_cdl_not_cdl_039_amendment",
    "topology_shuffle_authorization_separated_from_transport_contract",
    "cdl_068_evidence_checklist_requires_sim_topology_01_results",
    "cdl_068_not_ratified_in_window_733_738",
    "epoch_hash_v1_production_posture_cdl_068_scope",
    "vrf_upgrade_forward_obligation_in_cdl_068",
    "q3_settled_2026_04_19_new_cdl_not_cdl_039_amendment",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _commit_text(path: str, commit_ref: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{commit_ref}:{path}"],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout


def _resolve_commit_ref(subject_token: str, expected_paths: set[str]) -> str:
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
        if subject_token not in subject.lower():
            continue
        matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError(f"commit_not_present_in_local_history:{subject_token}")


def test_opening_document_contains_required_headings_in_order() -> None:
    text = _read(OPENING_PATH)
    positions = [text.index(heading) for heading in REQUIRED_HEADINGS]
    assert positions == sorted(positions)


def test_opening_document_contains_required_tokens() -> None:
    text = _read(OPENING_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_opening_document_states_exact_cdl_039_and_cdl_017_boundary() -> None:
    text = _read(OPENING_PATH)
    assert "CDL-039 governs how validators communicate" in text
    assert "CDL-068 governs which validators are assigned to communicate with each other" in text
    assert "A future reader of CDL-039 seeking topology shuffle authorization is in error - the correct reference is CDL-068." in text
    assert "CDL-017 remains the validator-admission lane." in text


def test_opening_document_records_full_pass_sim_outputs() -> None:
    text = _read(OPENING_PATH)
    assert "sim_topology_01_verdict=pass" in text
    assert "recommended_k_degree 4" in text
    assert "distinct_cluster_floor_recommendation 4" in text
    assert "max_cluster_share_ceiling_recommendation 33" in text
    assert "vrf_upgrade_threshold_validator_count 10" in text


def test_evidence_checklist_marks_phase_735_and_phase_734_complete_and_phase_737_future() -> None:
    text = _read(OPENING_PATH)
    assert "complete in Phase 735." in text
    assert "complete in Phase 734." in text
    assert "not complete yet at Phase 736." in text
    assert "Phase 737 must update `docs/research/ilc_validator_agent_design_evidence_v0.1.md`" in text


def test_opening_document_records_prelock_criteria_and_non_goals() -> None:
    text = _read(OPENING_PATH)
    assert "epoch-hash v1 remains acceptable for production v1 only with an explicit" in text
    assert "validator composition must use the explicit `validator_cluster_id` metric" in text
    assert "- ratify CDL-068," in text
    assert "- amend CDL-039," in text
    assert "- mutate `ilc_core/` or `ilc_consensus/`," in text


def test_phase_736_main_commit_touches_expected_paths_only_and_adds_only_cdl_068_row() -> None:
    commit_ref = _resolve_commit_ref(PHASE_736_SUBJECT_TOKEN, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS
    assert not any(
        path == "ilc_core" or path.startswith("ilc_core/")
        for path in _changed_paths_for_commit(commit_ref)
    )
    assert not any(
        path == "ilc_consensus" or path.startswith("ilc_consensus/")
        for path in _changed_paths_for_commit(commit_ref)
    )

    committed_rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), commit_ref))
    baseline_rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), f"{commit_ref}^"))
    assert "CDL-068" not in baseline_rows
    assert committed_rows["CDL-017"] == baseline_rows["CDL-017"]
    assert committed_rows["CDL-066"] == baseline_rows["CDL-066"]
    assert committed_rows["CDL-067"] == baseline_rows["CDL-067"]
    assert committed_rows["CDL-068"]["status"] == "open"
    assert "ratified_phase" not in committed_rows["CDL-068"]
    assert "ratified_date" not in committed_rows["CDL-068"]
    assert committed_rows["CDL-068"]["required_artifacts"].endswith(
        "docs/specs/ilc_cdl_068_topology_shuffle_authorization_opening_v0.1.md"
    )


def test_phase_736_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(
        PHASE_736_BACKFILL_SUBJECT_TOKEN,
        EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(
        path == "ilc_core" or path.startswith("ilc_core/")
        for path in changed_paths
    )
    assert not any(
        path == "ilc_consensus" or path.startswith("ilc_consensus/")
        for path in changed_paths
    )
