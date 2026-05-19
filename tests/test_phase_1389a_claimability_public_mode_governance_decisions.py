"""Phase 1389a claimability public-mode governance decision checks."""

from pathlib import Path


REPO = Path(__file__).resolve().parents[1]

PROMPT = REPO / "docs/antigravity_tasks/antigravity_prompt__phase_1389a_g8_claimability_public_mode_governance_decisions.md"
DECISION = REPO / "docs/specs/ilc_claimability_public_mode_governance_decisions_1389a_v0.1.md"
WALKTHROUGH = REPO / "docs/phases/phase_1389a_claimability_public_mode_governance_decisions_walkthrough.md"
STATUS = REPO / "docs/phases/STATUS.md"
PLANNING = REPO / "docs/PLANNING_INDEX.md"
SEQUENCE_LOCK = REPO / "docs/specs/ilc_phase_1369_1390_sequence_lock_v0.1.md"
GROUPING = REPO / "docs/specs/ilc_window_1369_1390_candidate_phase_grouping_v0.1.md"
VERIFIER = REPO / "ilc_core/sidecars/claimability_receipt_verifier.py"

GOVERNANCE_TOKENS = {
    "claimability_public_mode_governance_decisions_phase_1389a",
    "cdl_088_is_public_claimability_api_authority_phase_1389a",
    "public_safe_disclosure_schema_final_cdl_088_scope_phase_1389a",
    "transport_principal_resolved_at_d2d_layer_adr_0039_cdl_078_phase_1389a",
    "claimability_runtime_registry_blockers_remain_phase_1389a",
}

GOVERNANCE_CLOSED_BLOCKERS = {
    "public_claimability_api_authority_missing_phase_1305",
    "public_safe_disclosure_schema_not_final_phase_1305",
    "transport_principal_public_path_not_activated_phase_1305",
}

RUNTIME_BLOCKERS = {
    "replay_nullifier_policy_not_activated_phase_1305",
    "duplicate_claim_registry_not_activated_phase_1305",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1389a_artifacts_exist() -> None:
    assert PROMPT.exists()
    assert DECISION.exists()
    assert WALKTHROUGH.exists()


def test_decision_records_all_required_governance_tokens() -> None:
    text = _text(DECISION)
    for token in GOVERNANCE_TOKENS:
        assert token in text


def test_decision_closes_only_governance_resolvable_blockers() -> None:
    text = _text(DECISION)
    for blocker in GOVERNANCE_CLOSED_BLOCKERS:
        assert blocker in text
    assert "Closed by this phase" in text


def test_runtime_blockers_remain_preserved_in_decision() -> None:
    text = _text(DECISION)
    for blocker in RUNTIME_BLOCKERS:
        assert blocker in text
    assert "Still open after this phase" in text
    assert "Phase 1389b remains SENSITIVE runtime work" in text


def test_phase_1389a_does_not_claim_runtime_activation() -> None:
    text = _text(DECISION)
    forbidden = {
        "claimability_verifier_public_mode_ready_phase_1389b",
        "public_claimability_gate_pass_phase_1389",
        "public claimability is activated",
        "_PUBLIC_MODE_BLOCKERS` to an empty tuple",
    }
    for phrase in forbidden:
        assert phrase not in text


def test_verifier_runtime_public_mode_blockers_are_unchanged() -> None:
    text = _text(VERIFIER)
    for blocker in GOVERNANCE_CLOSED_BLOCKERS | RUNTIME_BLOCKERS:
        assert blocker in text
    assert "_PUBLIC_MODE_BLOCKERS = (" in text
    assert "claimability_verifier_public_mode_ready_phase_1389b" not in text


def test_verifier_still_requires_canonical_blocker_list() -> None:
    text = _text(VERIFIER)
    assert "if public_mode_blockers != list(_PUBLIC_MODE_BLOCKERS):" in text
    assert "claimability_decision_public_mode_blockers_invalid_phase_1305" in text


def test_status_and_planning_record_phase_1389a_routing() -> None:
    status = _text(STATUS)
    planning = _text(PLANNING)
    for token in GOVERNANCE_TOKENS:
        assert token in status
        assert token in planning
    assert "Phase 1389b" in status
    assert "Phase 1389b" in planning


def test_sequence_docs_record_phase_1389a() -> None:
    sequence = _text(SEQUENCE_LOCK)
    grouping = _text(GROUPING)
    for token in GOVERNANCE_TOKENS:
        assert token in sequence
        assert token in grouping


def test_walkthrough_records_graph_delta_and_no_runtime_edit() -> None:
    text = _text(WALKTHROUGH)
    assert "graph_delta=load_bearing_artifact_added:docs/specs/ilc_claimability_public_mode_governance_decisions_1389a_v0.1.md -> public-claimability/governance-disposition" in text
    assert "No runtime files were edited" in text
    for token in GOVERNANCE_TOKENS:
        assert token in text
