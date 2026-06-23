from __future__ import annotations

from pathlib import Path

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import GenesisAtlasCandidateStore


REPO_ROOT = Path(__file__).resolve().parents[1]
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
REPORT_PATH = REPO_ROOT / "docs/specs/ilc_fix70_authority_lattice_audit_report_v0.1.md"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
BASELINE_CROSS_FAMILY = 3
BASELINE_AUTH_TOTAL = 69
EDGES_WITH_EVIDENCE = 134
BASELINE_GENESIS_GOVERNS_TARGETS: set[str] = {'adr:0013_external_payment_boundary', 'adr:0028_consensus_production_bridge', 'cdl:043_storage_economics_graph_pruning_active_graph_retention_constraints', 'cdl:014_path_level_marginal_contribution_method', 'cdl:025_terminal_issuance_model', 'adr:0026_protocol_vs_harness_product_boundary', 'cdl:076_truth_primitive_announcement_gossip_lightweight_truth_primitive_announcement', 'adr:0033_star_map_homoiconic_entity', 'cdl:058_validator_re_admission_bounded_cooldown_based_re_entry', 'adr:0002_ndjson_bundle_transport', 'cdl:041_shard_lifecycle_operations_creation_merge_split_partition_privacy', 'cdl:011_node_usefulness_formula_ratification_ew', 'cdl:048_activation_counsel_clearance', 'cdl:004_founder_operational_caps', 'cdl:069_pq_identity_epoch_endorsement', 'adr:0009_bundle_distribution', 'cdl:081_hyperedge_ecu_attribution', 'cdl:024', 'cdl:020', 'cdl:045_circuit_breaker', 'adr:0043_review_lane_t0_5_to_t1_promotion', 'cdl:049_bounded_existential_alignment', 'cdl:v4_minority_dissent_appeal_reopening_ratified_cdl_decisions', 'cdl:032', 'adr:0012_ecu_ilc_graph_coupling_anti_reflexivity', 'adr:0022_local_first_private_use_and_publication_bound_economics', 'cdl:026_cmax_cap', 'cdl:027_epoch_length', 'cdl:074_truth_primitive_runtime', 'cdl:007_rollback_resistance', 'cdl:052_epistemic_evaluation_contract', 'cdl:037_executable_node_descriptor_safety_agent_side_sandboxing', 'adr:0006_eve_canonical_capsule_integrity', 'cdl:033', 'cdl:061_gossip_http_envelope', 'adr:0003_star_map_ngram_route_index', 'cdl:091_jury_incentive', 'adr:0031_subgraph_homomorphism', 'cdl:v6_genesis_intervention', 'cdl:035_validation_lifecycle', 'cdl:038_private_to_public_promotion', 'cdl:072_bound_b_formula_amendment', 'cdl:022_genesis_state_bundle_specification_signing_ceremony', 'adr:0027_canonical_bootstrap_receipt_boundary', 'cdl:059_quality_signal_architecture', 'adr:0001_canonical_encoding_node_id_agent_interface', 'cdl:039_topology_shuffling_authorization', 'cdl:040_admission_control_identity_envelope', 'cdl:027_epoch_issuance_boundary', 'adr:0035_homoiconic_type_definition_system', 'cdl:v3_quorum_diversity', 'cdl:030_ecu_price_clamp_runtime', 'adr:0030_node_embedding', 'adr:0044_anti_capture_diversity_verification', 'cdl:028_fee_burn_split', 'cdl:053_werner_local_productive_credit_future_vehicle', 'cdl:009_fork_legitimacy', 'adr:0022_local_first_private_use_publication_bound_economics', 'cdl:086', 'adr:0001_canonical_encoding_and_mcp_mvp', 'cdl:015_implementation_order_lock_refactor_avoidance', 'adr:ADR_0029', 'cdl:031_dynamic_ranking_policy', 'cdl:047_treasury_governance', 'cdl:v2_sybil_resistance', 'cdl:013_governance_weight', 'adr:0005_star_map_observational_feeds', 'cdl:071_temporal_tier_reconciliation', 'adr:0034_d2d_sealed_sender', 'adr:0020_knowledge_node_first_design_principle', 'cdl:050_treasury_ecu_governor_lane', 'cdl:v5_schema_epoch_markers_cross_version_translation_centrality_comparability', 'cdl:056_validator_trust_tier_elevation', 'cdl:097_type_definition_node_authority', 'cdl:001_signer_lineage_trust_root', 'adr:0016', 'cdl:002_key_compromise_response', 'cdl:066_chosen_substrate_legitimacy', 'adr:0023_multi_layer_quality_signal_architecture', 'cdl:093_maintenance_lottery', 'cdl:092_capproof_content_addressing_capability_vector_signing_chain_bounded', 'cdl:089_blocking_authority', 'cdl:064_exact_numeric_representation', 'adr:0039_validator_endpoint_registry', 'cdl:088_public_claimability', 'cdl:087_canonical_fetch_distribution_policy', 'cdl:051_epoch_state_quorum', 'cdl:057_blocking_authority_activation', 'cdl:v7_agent_decomposition', 'adr:0036_operational_release_key_genesis_binding', 'cdl:005_issuance_cap_constitutional_wording', 'adr:0038_agent_birth_attestation', 'cdl:010_pseudonymity_accountability_balance', 'adr:0004_genesis_truth_primitives', 'adr:0028_settlement_substrate_graduation_governance_route', 'cdl:079_hb_002_p2p_bootstrap_distribution_bootstrap_bundle_signed', 'cdl:078_relay_incentive_constitutional_lock', 'cdl:019_multiplier_governance_surface', 'cdl:029_80_15_5_allocation_distribution', 'cdl:096_werner_global_tier_authority', 'cdl:048_mandatory_conversion', 'cdl:055_validator_staking_liveness_runtime', 'adr:0032_temporal_hypergraph', 'adr:0041_agent_init_and_ingestion_protocol', 'adr:0042_vrf_proof_verifier', 'cdl:008_layer_fixed_core_vs_loaded_layers', 'cdl:085_werner_phi_bound', 'cdl:067_settlement_substrate_governance', 'adr:0023_quality_signal', 'adr:0029_hypergraph_substrate', 'cdl:046_timed_out_validation_state_amendment_churn_orphan_recovery', 'adr:0025_transport_binding', 'cdl:003_founder_fade_out_mechanics', 'cdl:017_validator_admission_ejection', 'cdl:v1_temporal_decay', 'cdl:023_epoch_snapshot_contract', 'cdl:073_homoiconic_bootstrap_schema', 'adr:0010_communication_plane_separation_performance_boundaries', 'cdl:006', 'cdl:044_local_first_wallet_surface', 'adr:0007_constitutional_baseline_ratification_process', 'cdl:060_gossip_centrality_extension', 'cdl:075_truth_primitive_graph_persistence', 'adr:0022_local_first_private_publication_bound_economics', 'cdl:036_node_dissemination_runtime', 'adr:0011_native_p2p_transport_baseline_agent_communication', 'cdl:083_panel_quorum_refutation', 'cdl:034_node_schema_core_runtime', 'adr:0026_protocol_vs_harness_boundary', 'cdl:012_utility_flow_reward_linkage_uf', 'cdl:077_want_have_want_block_fetch', 'cdl:090_identity_bootstrap', 'adr:0031_subgraph_homomorphism_query_contract', 'cdl:063_ecu_directed_commission', 'adr:0019_graph_native_governance_compilation_boundary', 'adr:0040_jury_eligibility_assignment', 'cdl:095_jury_finality_petition_runtime', 'cdl:054_validator_reward_pool_routing', 'cdl:065_coupling_invariants_governance_lock', 'cdl:094_transport_principal_admission_wire', 'cdl:068_topology_shuffle_vrf_runtime', 'cdl:084_provenance_chain_attribution', 'adr:0008_node_usefulness_governance_weight_genesis_dilution', 'adr:0037_genesis_canonical_lineage_contract', 'cdl:042_agent_id_flat_namespace', 'adr:0014_identity_sybil_admission_control_envelope', 'cdl:082', 'adr:0030_node_embedding_substrate', 'cdl:080_star_map_n_gram_route_index'}


def _graph() -> tuple[list[dict], list[dict]]:
    store = GenesisAtlasCandidateStore(LMDB_ROOT)
    try:
        return store.iter_nodes(), store.iter_edges()
    finally:
        store.close()


def test_fix70_status_tokens_present() -> None:
    text = STATUS_PATH.read_text(encoding="utf-8")
    for token in (
        "fix70_authority_lattice_repair_phase_1545p",
        "adr_cdl_cross_links_added_phase_1545p_fix70",
        "cdl_lineage_edges_added_phase_1545p_fix70",
        "lifecycle_records_wired_phase_1545p_fix70",
        "fix70_complete",
    ):
        assert token in text


def test_cross_family_count_increased() -> None:
    _, edges = _graph()
    authority_prefixes = ("cdl:", "adr:")
    cross_family = [
        edge
        for edge in edges
        if edge["source"].startswith(authority_prefixes)
        and edge["target"].startswith(authority_prefixes)
        and (
            (edge["source"].startswith("cdl:") and edge["target"].startswith("adr:"))
            or (edge["source"].startswith("adr:") and edge["target"].startswith("cdl:"))
        )
    ]
    assert len(cross_family) > BASELINE_CROSS_FAMILY


def test_auth_total_count_increased() -> None:
    _, edges = _graph()
    authority_prefixes = ("cdl:", "adr:")
    auth_edges = [
        edge
        for edge in edges
        if edge["source"].startswith(authority_prefixes)
        and edge["target"].startswith(authority_prefixes)
    ]
    assert len(auth_edges) > BASELINE_AUTH_TOTAL


def test_genesis_root_governs_edges_preserved() -> None:
    _, edges = _graph()
    genesis_governs_targets_after = {
        edge["target"]
        for edge in edges
        if edge.get("edge_type") == "GOVERNS"
        and "genesis" in edge.get("source", "").lower()
        and (edge["target"].startswith("cdl:") or edge["target"].startswith("adr:"))
    }
    missing = BASELINE_GENESIS_GOVERNS_TARGETS - genesis_governs_targets_after
    assert not missing, f"Genesis GOVERNS edges dropped after Fix70: {missing}"


def test_all_added_edges_target_existing_nodes() -> None:
    nodes, edges = _graph()
    node_ids = {node["candidate_id"] for node in nodes}
    authority_prefixes = ("cdl:", "adr:")
    checked_edge_types = (
        "REFERENCES_AUTHORITY",
        "GOVERNS",
        "DERIVED_FROM",
        "SUPERSEDED_BY",
        "OPENED_FOR",
        "PRELOCK_FOR",
        "RATIFICATION_EVIDENCE_FOR",
        "SAME_AUTHORITY",
    )
    new_auth_edges = [
        edge
        for edge in edges
        if edge["source"].startswith(authority_prefixes)
        and edge.get("edge_type") in checked_edge_types
    ]
    missing = [edge for edge in new_auth_edges if edge["target"] not in node_ids]
    assert not missing, f"Authority edges pointing to missing nodes: {missing[:5]}"


def test_audit_report_records_evidence_and_stale_governs_queue() -> None:
    text = REPORT_PATH.read_text(encoding="utf-8")
    assert "## Stale Lifecycle GOVERNS Review Queue" in text
    assert "## ADR REFERENCES_AUTHORITY Edges Added" in text
    assert "docs/adr/ADR_0020_Knowledge_Node_First_Design_Principle.md" in text
    assert "CDL-V7" in text
    reported_edges = (
        text.count("| REFERENCES_AUTHORITY |")
        + text.count("| DERIVED_FROM |")
        + text.count("| PRELOCK_FOR |")
    )
    assert reported_edges >= EDGES_WITH_EVIDENCE
