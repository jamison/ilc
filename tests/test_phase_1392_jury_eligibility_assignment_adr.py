from pathlib import Path


REPO = Path(__file__).resolve().parents[1]

ADR = REPO / "docs/adr/ADR_0040_Jury_Eligibility_Assignment.md"
ADR_README = REPO / "docs/adr/README.md"
WALKTHROUGH = REPO / "docs/phases/phase_1392_jury_eligibility_assignment_adr_walkthrough.md"
J_PLAN = REPO / "docs/specs/ilc_jury_epoch_work_canonicalization_phase_plan_v0.1.md"

REQUIRED_TOKENS = {
    "jury_eligibility_assignment_adr_accepted_phase_j002",
    "randomized_jury_assignment_opt_in_boundary_defined",
    "non_opt_in_agents_not_forced_into_jury_service",
}

SOURCE_PATHS = {
    "docs/specs/ilc_jury_epoch_work_canon_map_v0.1.md",
    "docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md",
    "docs/specs/ilc_cdl_068_topology_shuffle_authorization_ratification_evidence_743_v0.1.md",
    "ilc_core/validator/topology_shuffle_runtime.py",
    "docs/specs/ilc_cdl_v3_quorum_diversity_ratification_evidence_332_v0.1.md",
    "docs/specs/ilc_cdl_v3_diversity_floor_runtime_handoff_397_v0.1.md",
    "ilc_core/consensus/diversity_floor_runtime.py",
    "docs/phases/phase_0588_g8_public_quorum_eligibility_genesis_lineage_authority_boundary_lock_walkthrough.md",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_adr_0040_exists_and_is_accepted():
    assert ADR.exists()
    text = read(ADR)
    assert "# ADR-0040: Jury Eligibility and Assignment" in text
    assert "**Status:** Accepted" in text
    assert "**Phase:** 1392 / J-002" in text


def test_required_tokens_present_in_adr():
    text = read(ADR)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_source_paths_exist_and_are_cited():
    text = read(ADR)
    for rel_path in SOURCE_PATHS:
        assert (REPO / rel_path).exists(), rel_path
        assert rel_path in text


def test_opt_in_boundary_is_explicit_and_non_coercive():
    text = read(ADR)
    assert "graph_connection_alone_does_not_create_jury_service_obligation" in text
    assert "Graph connection, agent birth, validator identity, or ordinary graph participation alone does not create" in text
    assert "condition for receiving lane-specific benefits" in text
    assert "Mandatory jury service for all graph-connected agents" in text


def test_non_opt_in_agents_are_not_penalized():
    text = read(ADR)
    assert "non_opt_in_agents_are_not_penalized_for_review_non_response" in text
    assert "Non-opt-in agents are not penalized for failing to review" in text
    assert "Punishing non-opt-in agents for not reviewing" in text


def test_deterministic_assignment_shape_is_defined_without_prng():
    text = read(ADR)
    assert "epoch_hash_shadow_assignment_allowed" in text
    assert "domain_separator" in text
    assert "review_epoch" in text
    assert "review_lane" in text
    assert "claim_or_task_id" in text
    assert "eligible_agent_id" in text
    assert "outsider_candidate_flag" in text
    assert "It must not use predictable process-local PRNG such as Python" in text


def test_vrf_boundary_is_not_overclaimed():
    text = read(ADR)
    assert "vrf_required_for_production_high_value_assignment" in text
    assert "vrf_proof_verifier_not_implemented" in text
    assert "does not claim that a VRF proof verifier exists" in text
    assert "must not market deterministic epoch-hash shadow assignment as production privacy" in text


def test_diversity_and_outsider_seat_requirements_are_preserved():
    text = read(ADR)
    assert "panel_size=8" in text
    assert "regular_reviewers=7" in text
    assert "outsider_seat=true" in text
    assert "reviewer_quorum=k=5 of m=7" in text
    assert "independence_k=3" in text
    assert "same_operator_domain_not_independent" in text


def test_availability_commitment_shape_contains_required_fields():
    text = read(ADR)
    for field in [
        '"agent_id"',
        '"availability_epoch_range"',
        '"capability_claims"',
        '"cluster_id"',
        '"identity_lineage_ref"',
        '"max_concurrent_reviews"',
        '"non_response_policy_ref"',
        '"review_lane"',
        '"signature_ref"',
    ]:
        assert field in text


def test_non_authorizations_are_explicit():
    text = read(ADR)
    for phrase in [
        "no runtime implementation",
        "no production VRF implementation",
        "no reviewer-payment logic",
        "no public ingestion activation",
        "no public graph canonicalization",
        "no production jury activation",
        "no CDL mutation",
    ]:
        assert phrase in text


def test_adr_readme_indexes_adr_0040():
    text = read(ADR_README)
    assert "ADR_0040_Jury_Eligibility_Assignment.md" in text
    assert "Jury Eligibility and Assignment" in text


def test_j_plan_marks_j002_complete_after_execution():
    text = read(J_PLAN)
    assert "J-002 / 1392 now complete" in text
    assert "ADR_0040_Jury_Eligibility_Assignment.md" in text


def test_walkthrough_exists_and_contains_graph_delta():
    assert WALKTHROUGH.exists()
    text = read(WALKTHROUGH)
    for token in REQUIRED_TOKENS:
        assert token in text
    assert "graph_delta=load_bearing_artifact_added:docs/adr/ADR_0040_Jury_Eligibility_Assignment.md -> jury_epoch_work_canon" in text
    assert "No runtime implementation, CDL mutation, public ingestion activation, reviewer payment activation, production jury activation, or public RC claim occurred" in text
