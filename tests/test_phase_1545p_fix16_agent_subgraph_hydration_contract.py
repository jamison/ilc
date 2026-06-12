from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/specs/ilc_agent_subgraph_hydration_contract_1545p_fix16_v0.1.md"
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix16_g10_agent_subgraph_hydration_contract.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix16_agent_subgraph_hydration_contract_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING = ROOT / "docs/PLANNING_INDEX.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_fix16_tokens_and_public_path_boundaries_are_recorded() -> None:
    text = read(SPEC)

    for token in [
        "phase_1545p_fix16_agent_subgraph_hydration_contract_committed",
        "agent_subgraph_hydration_unfold_serialize_contract_recorded_phase_1545p_fix16",
        "permissioned_subgraph_slice_boundary_recorded_phase_1545p_fix16",
        "invitation_seed_connectivity_support_only_phase_1545p_fix16",
        "agent_hydration_governance_routing_rule_carried_forward_phase_1545p_fix16",
        "subgraph_hydration_not_public_serving_phase_1545p_fix16",
        "subgraph_hydration_not_live_zkp_phase_1545p_fix16",
        "graph_hydration_not_minting_phase_1545p_fix16",
        "public_path_remains_blocked_phase_1545p_fix16",
    ]:
        assert token in text

    for phrase in [
        "public sidecar serving;",
        "live ZKP routing;",
        "canonical graph mutation;",
        "ECU minting;",
        "public RC activation;",
    ]:
        assert phrase in text


def test_request_and_response_contract_fields_are_complete() -> None:
    text = read(SPEC)

    for field in [
        "`hydration_request_id`",
        "`requesting_agent_ref`",
        "`seed_ref`",
        "`invitation_edge_ref`",
        "`source_bundle_refs`",
        "`requested_slice_type`",
        "`root_node_ids`",
        "`authority_class_filter`",
        "`privacy_class_filter`",
        "`capability_refs`",
        "`max_nodes`",
        "`max_edges`",
        "`max_hops`",
        "`max_bytes`",
        "`projection_operator`",
        "`proximity_rule_id`",
        "`serialization_profile`",
    ]:
        assert field in text

    for field in [
        "`hydration_response_id`",
        "`source_citations`",
        "`slice_root_digest`",
        "`hydrated_nodes`",
        "`hydrated_edges`",
        "`folded_summaries`",
        "`projection_summary`",
        "`semantic_loss_annotations`",
        "`permission_decision`",
        "`privacy_redaction_summary`",
        "`refusal_tokens`",
        "`non_authorization_tokens`",
    ]:
        assert field in text


def test_permission_privacy_and_unfold_fold_contract_are_explicit() -> None:
    text = read(SPEC)

    for phrase in [
        "Private or membership-bound material requires opaque capability refs",
        "Responses must enforce node, edge, hop, byte, and privacy-class budgets",
        "Raw private path sets, raw membership lists, route history",
        "Type-definition rows remain support evidence while the type registry guard is active.",
        "`unfold_bundle_node`",
        "`unfold_type_definition_candidate`",
        "`unfold_sidecar_recipe`",
        "`fold_parallel_evidence_paths`",
        "`fold_private_proximity_witness`",
        "`fold_projection_summary`",
    ]:
        assert phrase in text


def test_governance_routing_and_fix_prompt_canon_are_hardened() -> None:
    text = read(SPEC)
    prompt = read(PROMPT)

    for phrase in [
        "Protocol architecture rule or required onboarding/distribution mechanism | ADR required.",
        "Constitutional authority, economics, activation, credit, reward eligibility, public serving, type-registry authority, or runtime guard clearance | CDL",
        "Later authorized Genesis successor-manifest phase required.",
    ]:
        assert phrase in text

    assert "proximity_witness_not_live_zkp_recorded_phase_1545p_fix11" in prompt
    assert "privacy_preserving_proximity_not_live_zkp_phase_1545p_fix11" not in prompt
    assert "ilc_confidential_coordination_sidecar_suite_forward_plan_v0.1.md" in prompt
    assert "ilc_agentic_p2p_delivery_sidecar_layering_spec_v0.1.md" not in prompt
    assert "ilc_private_communication_sidecar_receipts_capabilities_v0.1.md" not in prompt


def test_frontier_docs_record_fix16() -> None:
    walkthrough = read(WALKTHROUGH)
    status = read(STATUS)
    planning = read(PLANNING)

    assert "phase_1545p_fix16_agent_subgraph_hydration_contract_committed" in walkthrough
    assert "Phase 1545p-Fix16" in status
    assert "Phase 1545p-Fix16" in planning
    fix16_line = planning.split("Phase 1545p-Fix16", 1)[1].splitlines()[0]
    assert "⬅ CURRENT" in fix16_line or "Superseded as current frontier by Fix18" in fix16_line
