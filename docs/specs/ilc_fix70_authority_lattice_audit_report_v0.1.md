# Fix70 Authority Lattice Audit Report

## Summary

- ADR primary files direct-read: `43`.
- Baseline authority-to-authority edges: `69`.
- Baseline cross-family CDL/ADR edges: `3`.
- Baseline Genesis-root GOVERNS targets preserved: `149`.
- ADR `REFERENCES_AUTHORITY` edges added: `132`.
- CDL `GOVERNS` edges added: `0` (no reverse governance edge was added without explicit CDL-register governance language).
- CDL lineage edges added: `1`.
- Lifecycle edges added: `1`.
- Unresolved references recorded, not materialized: `10`.
- Post authority-to-authority edges: `203`.
- Post cross-family CDL/ADR edges: `78`.
- LMDB post counts: `16821` nodes / `89581` edges / dangling `0` / edge_id_debt `0`.

## Live CDL/ADR Node ID Map

### CDL Nodes

- `cdl:001`
- `cdl:001_signer_lineage_trust_root`
- `cdl:001_trust_root_runtime`
- `cdl:002`
- `cdl:002_key_compromise_response`
- `cdl:003_founder_fade_out_mechanics`
- `cdl:004_founder_operational_caps`
- `cdl:005_issuance_cap_constitutional_wording`
- `cdl:006`
- `cdl:007`
- `cdl:007_rollback_resistance`
- `cdl:008_layer_fixed_core_vs_loaded_layers`
- `cdl:009_fork_legitimacy`
- `cdl:010_pseudonymity_accountability_balance`
- `cdl:011_node_usefulness_formula_ratification_ew`
- `cdl:012_utility_flow_reward_linkage_uf`
- `cdl:013_governance_weight`
- `cdl:014_path_level_marginal_contribution_method`
- `cdl:015_implementation_order_lock_refactor_avoidance`
- `cdl:017_validator_admission_ejection`
- `cdl:019_multiplier_governance_surface`
- `cdl:020`
- `cdl:021`
- `cdl:022_genesis_state_bundle_specification_signing_ceremony`
- `cdl:023_epoch_snapshot_contract`
- `cdl:024`
- `cdl:025_terminal_issuance_model`
- `cdl:026_cmax_cap`
- `cdl:027_epoch_issuance_boundary`
- `cdl:027_epoch_length`
- `cdl:028`
- `cdl:028_fee_burn_split`
- `cdl:029_80_15_5_allocation_distribution`
- `cdl:029_allocation_split`
- `cdl:030_ecu_price_clamp_runtime`
- `cdl:031_dynamic_ranking_policy`
- `cdl:032`
- `cdl:033`
- `cdl:034_node_schema_core_runtime`
- `cdl:035_validation_lifecycle`
- `cdl:036_node_dissemination_runtime`
- `cdl:037_executable_node_descriptor_safety_agent_side_sandboxing`
- `cdl:038_private_to_public_promotion`
- `cdl:039_open_and_promotion_continuity`
- `cdl:039_topology_shuffling_authorization`
- `cdl:040_admission_control_identity_envelope`
- `cdl:041_shard_lifecycle_operations_creation_merge_split_partition_privacy`
- `cdl:042_agent_id_flat_namespace`
- `cdl:043_storage_economics_graph_pruning_active_graph_retention_constraints`
- `cdl:044_local_first_wallet_surface`
- `cdl:045_circuit_breaker`
- `cdl:046_timed_out_validation_state_amendment_churn_orphan_recovery`
- `cdl:047_treasury_governance`
- `cdl:047_treasury_reserve`
- `cdl:048_activation_counsel_clearance`
- `cdl:048_mandatory_conversion`
- `cdl:049_bounded_existential_alignment`
- `cdl:050_treasury_ecu_governor_lane`
- `cdl:051_epoch_state_quorum`
- `cdl:052_epistemic_evaluation_contract`
- `cdl:053_werner_local_productive_credit`
- `cdl:053_werner_local_productive_credit_future_vehicle`
- `cdl:054_validator_reward_pool_routing`
- `cdl:055_validator_staking_liveness`
- `cdl:055_validator_staking_liveness_runtime`
- `cdl:056_trust_tier_boundary`
- `cdl:056_validator_trust_tier_elevation`
- `cdl:057_blocking_authority_activation`
- `cdl:057_epoch_boundary_witness`
- `cdl:058_validator_re_admission_bounded_cooldown_based_re_entry`
- `cdl:059_quality_signal_architecture`
- `cdl:060`
- `cdl:060_gossip_centrality_extension`
- `cdl:060_gossip_hop_limit`
- `cdl:061`
- `cdl:061_gossip_http_envelope`
- `cdl:061_gossip_runtime_boundary`
- `cdl:062_sovereign_substrate_research_lane`
- `cdl:063_ecu_directed_commission`
- `cdl:064_exact_numeric_representation`
- `cdl:065_coupling_invariants_governance_lock`
- `cdl:066_chosen_substrate_legitimacy`
- `cdl:067_settlement_substrate_governance`
- `cdl:068_topology_shuffle_vrf`
- `cdl:068_topology_shuffle_vrf_runtime`
- `cdl:069_pq_identity_epoch_endorsement`
- `cdl:071_temporal_tier_reconciliation`
- `cdl:072_bound_b_formula_amendment`
- `cdl:073_homoiconic_bootstrap_schema`
- `cdl:074_truth_primitive_runtime`
- `cdl:075_truth_primitive_graph_persistence`
- `cdl:076_truth_primitive_announcement_gossip_lightweight_truth_primitive_announcement`
- `cdl:077`
- `cdl:077_want_have_want_block_fetch`
- `cdl:078_relay_incentive_constitutional_lock`
- `cdl:079_hb_002_p2p_bootstrap_distribution_bootstrap_bundle_signed`
- `cdl:080_star_map_n_gram_route_index`
- `cdl:081_hyperedge_attribution`
- `cdl:081_hyperedge_ecu_attribution`
- `cdl:082`
- `cdl:083_panel_quorum_refutation`
- `cdl:084_provenance_chain`
- `cdl:084_provenance_chain_attribution`
- `cdl:085`
- `cdl:085_opening_phase_1172`
- `cdl:085_prelock_historical_opening_and_prelock_state`
- `cdl:085_prelock_spec`
- `cdl:085_ratification_phase_1185`
- `cdl:085_werner_phi_bound`
- `cdl:086`
- `cdl:087`
- `cdl:087_canonical_fetch_distribution_policy`
- `cdl:088_public_claimability`
- `cdl:089_blocking_authority`
- `cdl:090_identity_bootstrap`
- `cdl:091_jury_incentive`
- `cdl:092_capproof_content_addressing_capability_vector_signing_chain_bounded`
- `cdl:093_maintenance_lottery`
- `cdl:094_transport_principal_admission_wire`
- `cdl:095_jury_finality_petition_runtime`
- `cdl:096_werner_flow_governor_lane`
- `cdl:096_werner_global_tier_authority`
- `cdl:097_type_definition_node_authority`
- `cdl:v1_temporal_decay`
- `cdl:v2_sybil_resistance`
- `cdl:v3_diversity_floor`
- `cdl:v3_quorum_diversity`
- `cdl:v4_minority_dissent_appeal_reopening_ratified_cdl_decisions`
- `cdl:v5_schema_epoch_markers_cross_version_translation_centrality_comparability`
- `cdl:v6_genesis_intervention`
- `cdl:v7_agent_decomposition`
- `cdl:v7_popperian_gate`

### ADR Nodes

- `adr:0001_canonical_encoding_and_mcp_mvp`
- `adr:0001_canonical_encoding_node_id_agent_interface`
- `adr:0002_ndjson_bundle_transport`
- `adr:0003_star_map_ngram_route_index`
- `adr:0004_genesis_truth_primitives`
- `adr:0005_star_map_observational_feeds`
- `adr:0006_eve_canonical_capsule_integrity`
- `adr:0007_constitutional_baseline_ratification_process`
- `adr:0008_node_usefulness_governance_weight_genesis_dilution`
- `adr:0009_bundle_distribution`
- `adr:0010_communication_plane_separation_performance_boundaries`
- `adr:0011_native_p2p_transport_baseline_agent_communication`
- `adr:0012_ecu_ilc_graph_coupling_anti_reflexivity`
- `adr:0013_external_payment_boundary`
- `adr:0014_identity_sybil_admission_control_envelope`
- `adr:0015_node_transfer_economics`
- `adr:0016`
- `adr:0018_sequestered_financial_shard`
- `adr:0019_graph_native_governance_compilation_boundary`
- `adr:0020_knowledge_node_first_design_principle`
- `adr:0021_epistemic_finality_claims`
- `adr:0022_local_first_private_publication_bound_economics`
- `adr:0022_local_first_private_use_and_publication_bound_economics`
- `adr:0022_local_first_private_use_publication_bound_economics`
- `adr:0023_multi_layer_quality_signal_architecture`
- `adr:0023_quality_signal`
- `adr:0024_agent_skills_infrastructure`
- `adr:0025_transport_binding`
- `adr:0026_protocol_vs_harness_boundary`
- `adr:0026_protocol_vs_harness_product_boundary`
- `adr:0027_canonical_bootstrap_receipt_boundary`
- `adr:0028_consensus_production_bridge`
- `adr:0028_option_b_graduation_posture`
- `adr:0028_settlement_substrate_graduation`
- `adr:0028_settlement_substrate_graduation_governance_route`
- `adr:0029_hypergraph_substrate`
- `adr:0030_node_embedding`
- `adr:0030_node_embedding_substrate`
- `adr:0031_subgraph_homomorphism`
- `adr:0031_subgraph_homomorphism_query_contract`
- `adr:0032_temporal_hypergraph`
- `adr:0033_star_map_homoiconic_entity`
- `adr:0034_d2d_sealed_sender`
- `adr:0035_homoiconic_type_definition_system`
- `adr:0036_operational_release_key_genesis_binding`
- `adr:0037_genesis_canonical_lineage_contract`
- `adr:0038_agent_birth_attestation`
- `adr:0039_validator_endpoint_registry`
- `adr:0040_jury_eligibility_assignment`
- `adr:0041_agent_init_and_ingestion_protocol`
- `adr:0042_vrf_proof_verifier`
- `adr:0043_review_lane_t0_5_to_t1_promotion`
- `adr:0044_anti_capture_diversity_verification`
- `adr:ADR_0029`

## Direct-Read ADR Files

| path | line_count | source_node |
| --- | --- | --- |
| docs/adr/ADR_0001_Canonical_Encoding_and_MCP_MVP.md | 154 | adr:0001_canonical_encoding_node_id_agent_interface |
| docs/adr/ADR_0002_NDJSON_Bundle_Transport.md | 135 | adr:0002_ndjson_bundle_transport |
| docs/adr/ADR_0003_Star_Map_Ngram_Route_Index.md | 93 | adr:0003_star_map_ngram_route_index |
| docs/adr/ADR_0004_Genesis_Primitive_Commit_Epoch.md | 58 | adr:0004_genesis_truth_primitives |
| docs/adr/ADR_0005_Star_Map_Observational_Feeds.md | 117 | adr:0005_star_map_observational_feeds |
| docs/adr/ADR_0006_EVE_Canonical_Capsule_Integrity.md | 105 | adr:0006_eve_canonical_capsule_integrity |
| docs/adr/ADR_0007_Constitutional_Baseline_and_Ratification_Process.md | 84 | adr:0007_constitutional_baseline_ratification_process |
| docs/adr/ADR_0008_Node_Usefulness_vs_Governance_Weight_and_Genesis_Dilution.md | 175 | adr:0008_node_usefulness_governance_weight_genesis_dilution |
| docs/adr/ADR_0009_Four_Layer_Protocol_Native_Bundle_Distribution.md | 180 | adr:0009_bundle_distribution |
| docs/adr/ADR_0010_Communication_Plane_Separation_and_Performance_Boundaries.md | 43 | adr:0010_communication_plane_separation_performance_boundaries |
| docs/adr/ADR_0011_Native_P2P_Transport_Baseline_for_Agent_Communication.md | 85 | adr:0011_native_p2p_transport_baseline_agent_communication |
| docs/adr/ADR_0012_ECU_ILC_Graph_Coupling_and_Anti_Reflexivity.md | 47 | adr:0012_ecu_ilc_graph_coupling_anti_reflexivity |
| docs/adr/ADR_0013_External_Payment_Boundary_and_Third_Party_Independence.md | 33 | adr:0013_external_payment_boundary |
| docs/adr/ADR_0014_Identity_Sybil_and_Admission_Control_Envelope.md | 38 | adr:0014_identity_sybil_admission_control_envelope |
| docs/adr/ADR_0015_Node_Transfer_Economics.md | 78 | adr:0015_node_transfer_economics |
| docs/adr/ADR_0016_Productive_ECU_Expansion_Bounty_Mechanism.md | 101 | adr:0016 |
| docs/adr/ADR_0017_Post_Issuance_Economic_Transition.md | 86 | MISSING |
| docs/adr/ADR_0018_Sequestered_Financial_Shard.md | 111 | adr:0018_sequestered_financial_shard |
| docs/adr/ADR_0019_Graph_Native_Governance_Compilation_Boundary.md | 106 | adr:0019_graph_native_governance_compilation_boundary |
| docs/adr/ADR_0020_Knowledge_Node_First_Design_Principle.md | 207 | adr:0020_knowledge_node_first_design_principle |
| docs/adr/ADR_0022_Local_First_Private_Use_and_Publication_Bound_Economics.md | 379 | adr:0022_local_first_private_publication_bound_economics |
| docs/adr/ADR_0023_Multi_Layer_Quality_Signal_Architecture.md | 276 | adr:0023_multi_layer_quality_signal_architecture |
| docs/adr/ADR_0024_Agent_Skills_Infrastructure.md | 215 | adr:0024_agent_skills_infrastructure |
| docs/adr/ADR_0025_D2d_HTTP_Gossip_Transport_Binding.md | 152 | adr:0025_transport_binding |
| docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md | 185 | adr:0026_protocol_vs_harness_product_boundary |
| docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md | 178 | adr:0027_canonical_bootstrap_receipt_boundary |
| docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md | 157 | adr:0028_settlement_substrate_graduation_governance_route |
| docs/adr/ADR_0029_Hypergraph_Substrate.md | 162 | adr:0029_hypergraph_substrate |
| docs/adr/ADR_0030_Node_Embedding_Substrate_and_Content_Typing.md | 131 | adr:0030_node_embedding_substrate |
| docs/adr/ADR_0031_Subgraph_Homomorphism_Query_Contract.md | 94 | adr:0031_subgraph_homomorphism_query_contract |
| docs/adr/ADR_0032_Temporal_Hypergraph_Epoch_Stamped_Incidence.md | 172 | adr:0032_temporal_hypergraph |
| docs/adr/ADR_0033_Star_Map_Homoiconic_Epistemiological_Entity.md | 257 | adr:0033_star_map_homoiconic_entity |
| docs/adr/ADR_0034_D2d_Sealed_Sender_Mechanism.md | 149 | adr:0034_d2d_sealed_sender |
| docs/adr/ADR_0035_Homoiconic_Type_Definition_System.md | 271 | adr:0035_homoiconic_type_definition_system |
| docs/adr/ADR_0036_Operational_Release_Key_Genesis_Binding.md | 144 | adr:0036_operational_release_key_genesis_binding |
| docs/adr/ADR_0037_Genesis_Canonical_Lineage_Contract.md | 290 | adr:0037_genesis_canonical_lineage_contract |
| docs/adr/ADR_0038_Agent_Birth_Attestation.md | 208 | adr:0038_agent_birth_attestation |
| docs/adr/ADR_0039_Validator_Endpoint_Registry.md | 255 | adr:0039_validator_endpoint_registry |
| docs/adr/ADR_0040_Jury_Eligibility_Assignment.md | 260 | adr:0040_jury_eligibility_assignment |
| docs/adr/ADR_0041_Agent_INIT_and_Ingestion_Protocol.md | 377 | adr:0041_agent_init_and_ingestion_protocol |
| docs/adr/ADR_0042_VRF_Proof_Verifier.md | 255 | adr:0042_vrf_proof_verifier |
| docs/adr/ADR_0043_Review_Lane_T0_5_To_T1_Promotion.md | 247 | adr:0043_review_lane_t0_5_to_t1_promotion |
| docs/adr/ADR_0044_Anti_Capture_Diversity_Verification.md | 208 | adr:0044_anti_capture_diversity_verification |

## ADR REFERENCES_AUTHORITY Edges Added

| source | edge_type | target | evidence_source_path | evidence_line | reference_label | evidence_text |
| --- | --- | --- | --- | --- | --- | --- |
| adr:0002_ndjson_bundle_transport | REFERENCES_AUTHORITY | adr:0003_star_map_ngram_route_index | docs/adr/ADR_0002_NDJSON_Bundle_Transport.md | 127 | ADR-0003 | **Concrete use-case:** Route index shards (ADR-0003) are transported as COSE-signed records in NDJSON bundles. |
| adr:0003_star_map_ngram_route_index | REFERENCES_AUTHORITY | adr:0001_canonical_encoding_node_id_agent_interface | docs/adr/ADR_0003_Star_Map_Ngram_Route_Index.md | 46 | ADR-0001 | - DAG-CBOR with string-only keys (per ADR-0001) |
| adr:0003_star_map_ngram_route_index | REFERENCES_AUTHORITY | adr:0002_ndjson_bundle_transport | docs/adr/ADR_0003_Star_Map_Ngram_Route_Index.md | 93 | ADR-0002 | - [ADR-0002: NDJSON Bundle Transport](ADR_0002_NDJSON_Bundle_Transport.md) |
| adr:0005_star_map_observational_feeds | REFERENCES_AUTHORITY | adr:0002_ndjson_bundle_transport | docs/adr/ADR_0005_Star_Map_Observational_Feeds.md | 116 | ADR-0002 | - [ADR-0002: NDJSON Bundle Transport](ADR_0002_NDJSON_Bundle_Transport.md) |
| adr:0006_eve_canonical_capsule_integrity | REFERENCES_AUTHORITY | adr:0001_canonical_encoding_node_id_agent_interface | docs/adr/ADR_0006_EVE_Canonical_Capsule_Integrity.md | 104 | ADR-0001 | - [ADR-0001: Canonical Encoding and MCP MVP](ADR_0001_Canonical_Encoding_and_MCP_MVP.md) |
| adr:0008_node_usefulness_governance_weight_genesis_dilution | REFERENCES_AUTHORITY | cdl:013_governance_weight | docs/adr/ADR_0008_Node_Usefulness_vs_Governance_Weight_and_Genesis_Dilution.md | 37 | CDL-013 | under the ratified `CDL-013` global-normalization posture. |
| adr:0009_bundle_distribution | REFERENCES_AUTHORITY | cdl:022_genesis_state_bundle_specification_signing_ceremony | docs/adr/ADR_0009_Four_Layer_Protocol_Native_Bundle_Distribution.md | 90 | CDL-022 | - Layer 1 Genesis state bundle requires a formal signing ceremony (CDL-022) |
| adr:0009_bundle_distribution | REFERENCES_AUTHORITY | cdl:019_multiplier_governance_surface | docs/adr/ADR_0009_Four_Layer_Protocol_Native_Bundle_Distribution.md | 119 | CDL-019 | \| CDL-019 \| Multiplier-governance surface unification \| **Phase 230 — IMMEDIATE** \| |
| adr:0009_bundle_distribution | REFERENCES_AUTHORITY | cdl:020 | docs/adr/ADR_0009_Four_Layer_Protocol_Native_Bundle_Distribution.md | 120 | CDL-020 | \| CDL-020 \| Protocol-native bundle schema and complete type system \| When D2 phase complete \| |
| adr:0009_bundle_distribution | REFERENCES_AUTHORITY | cdl:021 | docs/adr/ADR_0009_Four_Layer_Protocol_Native_Bundle_Distribution.md | 121 | CDL-021 | \| CDL-021 \| Rust kernel port and WASM distribution \| When Phase B trigger criteria met \| |
| adr:0009_bundle_distribution | REFERENCES_AUTHORITY | cdl:023_epoch_snapshot_contract | docs/adr/ADR_0009_Four_Layer_Protocol_Native_Bundle_Distribution.md | 123 | CDL-023 | \| CDL-023 \| Epoch snapshot mechanism and fast-bootstrap protocol \| When D2c phase complete \| |
| adr:0009_bundle_distribution | REFERENCES_AUTHORITY | cdl:024 | docs/adr/ADR_0009_Four_Layer_Protocol_Native_Bundle_Distribution.md | 124 | CDL-024 | \| CDL-024 \| Wire protocol specification and transport bindings \| When D2d phase complete \| |
| adr:0009_bundle_distribution | REFERENCES_AUTHORITY | adr:0001_canonical_encoding_node_id_agent_interface | docs/adr/ADR_0009_Four_Layer_Protocol_Native_Bundle_Distribution.md | 139 | ADR-0001 | \| ADR-0001 (Canonical Encoding and MCP MVP) \| ADR-0009 extends ADR-0001's DAG-CBOR + CIDv1 + COSE Sign1 encoding stack to the full distribution surface \| |
| adr:0009_bundle_distribution | REFERENCES_AUTHORITY | adr:0002_ndjson_bundle_transport | docs/adr/ADR_0009_Four_Layer_Protocol_Native_Bundle_Distribution.md | 140 | ADR-0002 | \| ADR-0002 (NDJSON Bundle Transport) \| NDJSON remains for logs only; this ADR governs the protocol-native bundle format, which is distinct \| |
| adr:0009_bundle_distribution | REFERENCES_AUTHORITY | adr:0004_genesis_truth_primitives | docs/adr/ADR_0009_Four_Layer_Protocol_Native_Bundle_Distribution.md | 141 | ADR-0004 | \| ADR-0004 (Genesis Truth Primitives) \| The seven truth primitives are defined in the Layer 0 bundle; star.map remains L2 routing \| |
| adr:0009_bundle_distribution | REFERENCES_AUTHORITY | adr:0007_constitutional_baseline_ratification_process | docs/adr/ADR_0009_Four_Layer_Protocol_Native_Bundle_Distribution.md | 142 | ADR-0007 | \| ADR-0007 (Constitutional Baseline) \| CDL-019 through CDL-024 are routed through the constitutional decision-log process per ADR-0007 \| |
| adr:0009_bundle_distribution | REFERENCES_AUTHORITY | adr:0008_node_usefulness_governance_weight_genesis_dilution | docs/adr/ADR_0009_Four_Layer_Protocol_Native_Bundle_Distribution.md | 143 | ADR-0008 | \| ADR-0008 (Node Usefulness vs Governance Weight) \| Layer 0 scoring parameters block encodes the ECU weights and governance configuration governed by ADR-0008 \| |
| adr:0011_native_p2p_transport_baseline_agent_communication | REFERENCES_AUTHORITY | cdl:024 | docs/adr/ADR_0011_Native_P2P_Transport_Baseline_for_Agent_Communication.md | 5 | CDL-024 | **Accepted:** 2026-03-31 (post-Phase 547 architectural review; consistent with CDL-024 allowed transport kinds and ADR-0025) |
| adr:0011_native_p2p_transport_baseline_agent_communication | REFERENCES_AUTHORITY | adr:0025_transport_binding | docs/adr/ADR_0011_Native_P2P_Transport_Baseline_for_Agent_Communication.md | 5 | ADR-0025 | **Accepted:** 2026-03-31 (post-Phase 547 architectural review; consistent with CDL-024 allowed transport kinds and ADR-0025) |
| adr:0015_node_transfer_economics | REFERENCES_AUTHORITY | cdl:034_node_schema_core_runtime | docs/adr/ADR_0015_Node_Transfer_Economics.md | 7 | CDL-034 | **Dependencies:** CDL-034 (three-envelope node schema), CDL-035 (validation lifecycle), CDL-V1 (temporal decay), CDL-V7 (Popperian gate), CDL-029 (allocation split) |
| adr:0015_node_transfer_economics | REFERENCES_AUTHORITY | cdl:035_validation_lifecycle | docs/adr/ADR_0015_Node_Transfer_Economics.md | 7 | CDL-035 | **Dependencies:** CDL-034 (three-envelope node schema), CDL-035 (validation lifecycle), CDL-V1 (temporal decay), CDL-V7 (Popperian gate), CDL-029 (allocation split) |
| adr:0015_node_transfer_economics | REFERENCES_AUTHORITY | cdl:v1_temporal_decay | docs/adr/ADR_0015_Node_Transfer_Economics.md | 7 | CDL-V1 | **Dependencies:** CDL-034 (three-envelope node schema), CDL-035 (validation lifecycle), CDL-V1 (temporal decay), CDL-V7 (Popperian gate), CDL-029 (allocation split) |
| adr:0015_node_transfer_economics | REFERENCES_AUTHORITY | cdl:v7_agent_decomposition | docs/adr/ADR_0015_Node_Transfer_Economics.md | 7 | CDL-V7 | **Dependencies:** CDL-034 (three-envelope node schema), CDL-035 (validation lifecycle), CDL-V1 (temporal decay), CDL-V7 (Popperian gate), CDL-029 (allocation split) |
| adr:0015_node_transfer_economics | REFERENCES_AUTHORITY | cdl:029_80_15_5_allocation_distribution | docs/adr/ADR_0015_Node_Transfer_Economics.md | 7 | CDL-029 | **Dependencies:** CDL-034 (three-envelope node schema), CDL-035 (validation lifecycle), CDL-V1 (temporal decay), CDL-V7 (Popperian gate), CDL-029 (allocation split) |
| adr:0015_node_transfer_economics | REFERENCES_AUTHORITY | cdl:013_governance_weight | docs/adr/ADR_0015_Node_Transfer_Economics.md | 42 | CDL-013 | - Consistent with CDL-013 (governance-weight decay) and ADM-003 Phase 354 (L-tiers = epistemic tiers) |
| adr:0016 | REFERENCES_AUTHORITY | cdl:025_terminal_issuance_model | docs/adr/ADR_0016_Productive_ECU_Expansion_Bounty_Mechanism.md | 9 | CDL-025 | **Dependencies:** CDL-025 (terminal issuance model), CDL-029 (allocation split), CDL-V3 (quorum diversity), CDL-V7 (Popperian gate), CDL-035 (validation lifecycle) |
| adr:0016 | REFERENCES_AUTHORITY | cdl:029_80_15_5_allocation_distribution | docs/adr/ADR_0016_Productive_ECU_Expansion_Bounty_Mechanism.md | 9 | CDL-029 | **Dependencies:** CDL-025 (terminal issuance model), CDL-029 (allocation split), CDL-V3 (quorum diversity), CDL-V7 (Popperian gate), CDL-035 (validation lifecycle) |
| adr:0016 | REFERENCES_AUTHORITY | cdl:v3_quorum_diversity | docs/adr/ADR_0016_Productive_ECU_Expansion_Bounty_Mechanism.md | 9 | CDL-V3 | **Dependencies:** CDL-025 (terminal issuance model), CDL-029 (allocation split), CDL-V3 (quorum diversity), CDL-V7 (Popperian gate), CDL-035 (validation lifecycle) |
| adr:0016 | REFERENCES_AUTHORITY | cdl:v7_agent_decomposition | docs/adr/ADR_0016_Productive_ECU_Expansion_Bounty_Mechanism.md | 9 | CDL-V7 | **Dependencies:** CDL-025 (terminal issuance model), CDL-029 (allocation split), CDL-V3 (quorum diversity), CDL-V7 (Popperian gate), CDL-035 (validation lifecycle) |
| adr:0016 | REFERENCES_AUTHORITY | cdl:035_validation_lifecycle | docs/adr/ADR_0016_Productive_ECU_Expansion_Bounty_Mechanism.md | 9 | CDL-035 | **Dependencies:** CDL-025 (terminal issuance model), CDL-029 (allocation split), CDL-V3 (quorum diversity), CDL-V7 (Popperian gate), CDL-035 (validation lifecycle) |
| adr:0018_sequestered_financial_shard | REFERENCES_AUTHORITY | cdl:051_epoch_state_quorum | docs/adr/ADR_0018_Sequestered_Financial_Shard.md | 56 | CDL-051 | ## Relationship to CDL-051 and Epoch-State Runtime |
| adr:0018_sequestered_financial_shard | REFERENCES_AUTHORITY | cdl:050_treasury_ecu_governor_lane | docs/adr/ADR_0018_Sequestered_Financial_Shard.md | 78 | CDL-050 | - Gives CDL-050 and Treasury risk modeling a bounded L1/L2 interface. |
| adr:0019_graph_native_governance_compilation_boundary | REFERENCES_AUTHORITY | adr:0007_constitutional_baseline_ratification_process | docs/adr/ADR_0019_Graph_Native_Governance_Compilation_Boundary.md | 7 | ADR-0007 | **Dependencies:** ADR-0007, ADR-0009, ADR-0011, ADM-003 v0.2, Window 434-440 handoff |
| adr:0019_graph_native_governance_compilation_boundary | REFERENCES_AUTHORITY | adr:0009_bundle_distribution | docs/adr/ADR_0019_Graph_Native_Governance_Compilation_Boundary.md | 7 | ADR-0009 | **Dependencies:** ADR-0007, ADR-0009, ADR-0011, ADM-003 v0.2, Window 434-440 handoff |
| adr:0019_graph_native_governance_compilation_boundary | REFERENCES_AUTHORITY | adr:0011_native_p2p_transport_baseline_agent_communication | docs/adr/ADR_0019_Graph_Native_Governance_Compilation_Boundary.md | 7 | ADR-0011 | **Dependencies:** ADR-0007, ADR-0009, ADR-0011, ADM-003 v0.2, Window 434-440 handoff |
| adr:0020_knowledge_node_first_design_principle | REFERENCES_AUTHORITY | cdl:v7_agent_decomposition | docs/adr/ADR_0020_Knowledge_Node_First_Design_Principle.md | 7 | CDL-V7 | **Dependencies:** ADR-0019, ADM-003 v0.2, CDL-V7 |
| adr:0020_knowledge_node_first_design_principle | REFERENCES_AUTHORITY | adr:0019_graph_native_governance_compilation_boundary | docs/adr/ADR_0020_Knowledge_Node_First_Design_Principle.md | 7 | ADR-0019 | **Dependencies:** ADR-0019, ADM-003 v0.2, CDL-V7 |
| adr:0020_knowledge_node_first_design_principle | REFERENCES_AUTHORITY | cdl:001_signer_lineage_trust_root | docs/adr/ADR_0020_Knowledge_Node_First_Design_Principle.md | 101 | CDL-001 | Not all information can be placed on the graph. The genesis layer (CDL-001 signer lineage, |
| adr:0020_knowledge_node_first_design_principle | REFERENCES_AUTHORITY | cdl:050_treasury_ecu_governor_lane | docs/adr/ADR_0020_Knowledge_Node_First_Design_Principle.md | 155 | CDL-050 | 2. **Documentation migration inventory:** After Window 450+ CDL-050 resolution, a |
| adr:0020_knowledge_node_first_design_principle | REFERENCES_AUTHORITY | adr:0021_epistemic_finality_claims | docs/adr/ADR_0020_Knowledge_Node_First_Design_Principle.md | 163 | ADR-0021 | mechanisms rather than as a new bespoke finality protocol. See planned ADR-0021. |
| adr:0022_local_first_private_publication_bound_economics | REFERENCES_AUTHORITY | adr:0019_graph_native_governance_compilation_boundary | docs/adr/ADR_0022_Local_First_Private_Use_and_Publication_Bound_Economics.md | 8 | ADR-0019 | **Dependencies:** ADR-0019, ADR-0020, node schema visibility model, OpenClaw / CLI-first |
| adr:0022_local_first_private_publication_bound_economics | REFERENCES_AUTHORITY | adr:0020_knowledge_node_first_design_principle | docs/adr/ADR_0022_Local_First_Private_Use_and_Publication_Bound_Economics.md | 8 | ADR-0020 | **Dependencies:** ADR-0019, ADR-0020, node schema visibility model, OpenClaw / CLI-first |
| adr:0023_multi_layer_quality_signal_architecture | REFERENCES_AUTHORITY | cdl:v7_agent_decomposition | docs/adr/ADR_0023_Multi_Layer_Quality_Signal_Architecture.md | 23 | CDL-V7 | (Register 1): the CDL-V7 Popperian basic-statement gate, CDL-049 admissible claim forms, and |
| adr:0023_multi_layer_quality_signal_architecture | REFERENCES_AUTHORITY | cdl:049_bounded_existential_alignment | docs/adr/ADR_0023_Multi_Layer_Quality_Signal_Architecture.md | 23 | CDL-049 | (Register 1): the CDL-V7 Popperian basic-statement gate, CDL-049 admissible claim forms, and |
| adr:0023_multi_layer_quality_signal_architecture | REFERENCES_AUTHORITY | cdl:036_node_dissemination_runtime | docs/adr/ADR_0023_Multi_Layer_Quality_Signal_Architecture.md | 34 | CDL-036 | - `epistemic_type` field in the CDL-036 authored payload labels the register |
| adr:0023_multi_layer_quality_signal_architecture | REFERENCES_AUTHORITY | cdl:v3_quorum_diversity | docs/adr/ADR_0023_Multi_Layer_Quality_Signal_Architecture.md | 66 | CDL-V3 | - CDL-V3 cluster diversity floor applies; model-type diversity reduces preference correlation |
| adr:0023_multi_layer_quality_signal_architecture | REFERENCES_AUTHORITY | cdl:039_topology_shuffling_authorization | docs/adr/ADR_0023_Multi_Layer_Quality_Signal_Architecture.md | 86 | CDL-039 | - Gossip: piggybacked on d2d gossip protocol; CDL-039 compliant (no topology information) |
| adr:0023_multi_layer_quality_signal_architecture | REFERENCES_AUTHORITY | cdl:v4_minority_dissent_appeal_reopening_ratified_cdl_decisions | docs/adr/ADR_0023_Multi_Layer_Quality_Signal_Architecture.md | 208 | CDL-V4 | — requires CDL-V4 reopening process |
| adr:0023_multi_layer_quality_signal_architecture | REFERENCES_AUTHORITY | cdl:053_werner_local_productive_credit_future_vehicle | docs/adr/ADR_0023_Multi_Layer_Quality_Signal_Architecture.md | 218 | CDL-053 | - CDL-053 scope (Werner credit architecture): this ADR is independent of CDL-053 |
| adr:0023_multi_layer_quality_signal_architecture | REFERENCES_AUTHORITY | cdl:030_ecu_price_clamp_runtime | docs/adr/ADR_0023_Multi_Layer_Quality_Signal_Architecture.md | 219 | CDL-030 | - B_e budget and P_e clamp (CDL-030): passive attribution is bounded within existing budget |
| adr:0023_multi_layer_quality_signal_architecture | REFERENCES_AUTHORITY | adr:0016 | docs/adr/ADR_0023_Multi_Layer_Quality_Signal_Architecture.md | 244 | ADR-0016 | - ILC CDL-036, CDL-V3, CDL-V7, CDL-049, ADM-001 v0.2, d2d/gossip.py, ADR-0016 |
| adr:0023_multi_layer_quality_signal_architecture | REFERENCES_AUTHORITY | cdl:060_gossip_centrality_extension | docs/adr/ADR_0023_Multi_Layer_Quality_Signal_Architecture.md | 255 | CDL-060 | - `recommended_u_floor = 0.05` (CDL-060 ratified lane; `U_FLOOR` in |
| adr:0023_multi_layer_quality_signal_architecture | REFERENCES_AUTHORITY | cdl:061_gossip_http_envelope | docs/adr/ADR_0023_Multi_Layer_Quality_Signal_Architecture.md | 274 | CDL-061 | - CDL-061 (Phase 557) does not alter `U_FLOOR`. |
| adr:0024_agent_skills_infrastructure | REFERENCES_AUTHORITY | cdl:034_node_schema_core_runtime | docs/adr/ADR_0024_Agent_Skills_Infrastructure.md | 9 | CDL-034 | **Dependencies:** agentskills.io open standard (December 2025), CDL-034 (authored envelope |
| adr:0024_agent_skills_infrastructure | REFERENCES_AUTHORITY | cdl:052_epistemic_evaluation_contract | docs/adr/ADR_0024_Agent_Skills_Infrastructure.md | 10 | CDL-052 | schema), CDL-052 (epistemic runtime), CDL-V7 (Popperian gate for skill versioning claims) |
| adr:0024_agent_skills_infrastructure | REFERENCES_AUTHORITY | cdl:v7_agent_decomposition | docs/adr/ADR_0024_Agent_Skills_Infrastructure.md | 10 | CDL-V7 | schema), CDL-052 (epistemic runtime), CDL-V7 (Popperian gate for skill versioning claims) |
| adr:0024_agent_skills_infrastructure | REFERENCES_AUTHORITY | cdl:053_werner_local_productive_credit_future_vehicle | docs/adr/ADR_0024_Agent_Skills_Infrastructure.md | 149 | CDL-053 | - The above is adjacent to CDL-053 (Werner credit) and the long-tail research track |
| adr:0025_transport_binding | REFERENCES_AUTHORITY | adr:0011_native_p2p_transport_baseline_agent_communication | docs/adr/ADR_0025_D2d_HTTP_Gossip_Transport_Binding.md | 5 | ADR-0011 | **Accepted:** 2026-03-31 (post-Phase 547 architectural review; Codex review confirmed architecture sound; ADR-0011 confirmed as the accepted baseline during the same review) |
| adr:0025_transport_binding | REFERENCES_AUTHORITY | cdl:024 | docs/adr/ADR_0025_D2d_HTTP_Gossip_Transport_Binding.md | 7 | CDL-024 | **Supersedes:** Nothing (extends CDL-024 and ADR-0011 for the gossip sub-layer) |
| adr:0025_transport_binding | REFERENCES_AUTHORITY | cdl:039_topology_shuffling_authorization | docs/adr/ADR_0025_D2d_HTTP_Gossip_Transport_Binding.md | 8 | CDL-039 | **See also:** ADR-0011 (Native P2P Transport Baseline), CDL-024 (wire transport), CDL-039 (topology privacy), CDL-060 (gossip centrality extension), `docs/research/ilc_http_gossip_transport_x402_context_v0.1.md` |
| adr:0025_transport_binding | REFERENCES_AUTHORITY | cdl:060_gossip_centrality_extension | docs/adr/ADR_0025_D2d_HTTP_Gossip_Transport_Binding.md | 8 | CDL-060 | **See also:** ADR-0011 (Native P2P Transport Baseline), CDL-024 (wire transport), CDL-039 (topology privacy), CDL-060 (gossip centrality extension), `docs/research/ilc_http_gossip_transport_x402_context_v0.1.md` |
| adr:0025_transport_binding | REFERENCES_AUTHORITY | cdl:036_node_dissemination_runtime | docs/adr/ADR_0025_D2d_HTTP_Gossip_Transport_Binding.md | 129 | CDL-036 | - This ADR does not govern the content dissemination layer (CDL-036 pull-fetch remains unchanged) |
| adr:0025_transport_binding | REFERENCES_AUTHORITY | cdl:061_gossip_http_envelope | docs/adr/ADR_0025_D2d_HTTP_Gossip_Transport_Binding.md | 140 | CDL-061 | 3. **CDL-061 governance lane**: Phase 557 opened CDL-061, Phase 561 ratified it, and the decision log now records the gossip HTTP envelope contract as ratified canon. |
| adr:0025_transport_binding | REFERENCES_AUTHORITY | cdl:047_treasury_governance | docs/adr/ADR_0025_D2d_HTTP_Gossip_Transport_Binding.md | 152 | CDL-047 | 6. **Window 595+ planning**: Treat inbound x402 task submission as a separate treasury-governed lane requiring stablecoin-to-ECU conversion rules under CDL-047. Do not merge it into the gossip transport stack. |
| adr:0026_protocol_vs_harness_product_boundary | REFERENCES_AUTHORITY | adr:0022_local_first_private_publication_bound_economics | docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md | 30 | ADR-0022 | - weaken local/private architectural guarantees in ADR-0022, |
| adr:0027_canonical_bootstrap_receipt_boundary | REFERENCES_AUTHORITY | adr:0026_protocol_vs_harness_product_boundary | docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md | 165 | ADR-0026 | - or replace the protocol-vs-harness boundary in ADR-0026. |
| adr:0028_settlement_substrate_graduation_governance_route | REFERENCES_AUTHORITY | cdl:062_sovereign_substrate_research_lane | docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md | 38 | CDL-062 | - with no decision-log mutation and no opening of `CDL-062` in Window 607-612. |
| adr:0029_hypergraph_substrate | REFERENCES_AUTHORITY | cdl:v1_temporal_decay | docs/adr/ADR_0029_Hypergraph_Substrate.md | 54 | CDL-V1 | weight is dynamic — callers must apply temporal decay (CDL-V1) before use. |
| adr:0029_hypergraph_substrate | REFERENCES_AUTHORITY | cdl:v3_quorum_diversity | docs/adr/ADR_0029_Hypergraph_Substrate.md | 130 | CDL-V3 | - **Panel hyperedge quorum rules**: what constitutes a valid `panel` hyperedge — minimum degree, agent diversity requirements? — likely extends CDL-V3 diversity floor |
| adr:0029_hypergraph_substrate | REFERENCES_AUTHORITY | adr:0030_node_embedding_substrate | docs/adr/ADR_0029_Hypergraph_Substrate.md | 157 | ADR-0030 | - ADR-0030: Node Embedding Substrate (embeddings are the query interface over this substrate) |
| adr:0029_hypergraph_substrate | REFERENCES_AUTHORITY | adr:0031_subgraph_homomorphism_query_contract | docs/adr/ADR_0029_Hypergraph_Substrate.md | 158 | ADR-0031 | - ADR-0031: Subgraph Homomorphism Query Contract (HyperEdgeRecord extends gRPC response) |
| adr:0030_node_embedding_substrate | REFERENCES_AUTHORITY | adr:0029_hypergraph_substrate | docs/adr/ADR_0030_Node_Embedding_Substrate_and_Content_Typing.md | 43 | ADR-0029 | - `"hyperedge_entity"` — a star-expanded hyperedge node (see ADR-0029 §2.3) |
| adr:0030_node_embedding_substrate | REFERENCES_AUTHORITY | cdl:097_type_definition_node_authority | docs/adr/ADR_0030_Node_Embedding_Substrate_and_Content_Typing.md | 45 | CDL-097 | - `"type_definition"` — a CDL-097 governed definition-node content category |
| adr:0030_node_embedding_substrate | REFERENCES_AUTHORITY | adr:0031_subgraph_homomorphism_query_contract | docs/adr/ADR_0030_Node_Embedding_Substrate_and_Content_Typing.md | 129 | ADR-0031 | - ADR-0031: Subgraph Homomorphism Query Contract (node responses in gRPC SHOULD include content_type; embedding is omitted from wire format by default for bandwidth reasons) |
| adr:0031_subgraph_homomorphism_query_contract | REFERENCES_AUTHORITY | adr:0029_hypergraph_substrate | docs/adr/ADR_0031_Subgraph_Homomorphism_Query_Contract.md | 48 | ADR-0029 | When HyperEdge types are activated (per ADR-0029), the response schema extends to: |
| adr:0031_subgraph_homomorphism_query_contract | REFERENCES_AUTHORITY | adr:0030_node_embedding_substrate | docs/adr/ADR_0031_Subgraph_Homomorphism_Query_Contract.md | 92 | ADR-0030 | - ADR-0030: Node Embedding Substrate (embedding fields on node responses follow the same forward-reservation pattern) |
| adr:0032_temporal_hypergraph | REFERENCES_AUTHORITY | adr:0029_hypergraph_substrate | docs/adr/ADR_0032_Temporal_Hypergraph_Epoch_Stamped_Incidence.md | 5 | ADR-0029 | **Lane:** H-004 (amendment to ADR-0029) |
| adr:0032_temporal_hypergraph | REFERENCES_AUTHORITY | adr:0030_node_embedding_substrate | docs/adr/ADR_0032_Temporal_Hypergraph_Epoch_Stamped_Incidence.md | 158 | ADR-0030 | \| ADR-0030 \| No conflict. Content-type node embedding is orthogonal to spectral analysis. \| |
| adr:0032_temporal_hypergraph | REFERENCES_AUTHORITY | adr:0031_subgraph_homomorphism_query_contract | docs/adr/ADR_0032_Temporal_Hypergraph_Epoch_Stamped_Incidence.md | 159 | ADR-0031 | \| ADR-0031 \| No conflict. Subgraph query contract is a different analytical surface. \| |
| adr:0033_star_map_homoiconic_entity | REFERENCES_AUTHORITY | adr:0003_star_map_ngram_route_index | docs/adr/ADR_0033_Star_Map_Homoiconic_Epistemiological_Entity.md | 15 | ADR-0003 | - ADR-0003 defines the signed, versioned n-gram route index as a low-cost |
| adr:0033_star_map_homoiconic_entity | REFERENCES_AUTHORITY | adr:0005_star_map_observational_feeds | docs/adr/ADR_0033_Star_Map_Homoiconic_Epistemiological_Entity.md | 17 | ADR-0005 | - ADR-0005 defines observational star-map feeds as append-only event surfaces. |
| adr:0033_star_map_homoiconic_entity | REFERENCES_AUTHORITY | adr:0029_hypergraph_substrate | docs/adr/ADR_0033_Star_Map_Homoiconic_Epistemiological_Entity.md | 19 | ADR-0029 | ILC also now has the accepted hypergraph substrate in ADR-0029, including the |
| adr:0033_star_map_homoiconic_entity | REFERENCES_AUTHORITY | adr:0030_node_embedding_substrate | docs/adr/ADR_0033_Star_Map_Homoiconic_Epistemiological_Entity.md | 62 | ADR-0030 | This ADR also does **not** amend ADR-0030's accepted semantic |
| adr:0034_d2d_sealed_sender | REFERENCES_AUTHORITY | cdl:060_gossip_centrality_extension | docs/adr/ADR_0034_D2d_Sealed_Sender_Mechanism.md | 61 | CDL-060 | ## 3. CDL-060 Compatibility Surface |
| adr:0034_d2d_sealed_sender | REFERENCES_AUTHORITY | cdl:061_gossip_http_envelope | docs/adr/ADR_0034_D2d_Sealed_Sender_Mechanism.md | 83 | CDL-061 | ## 4. CDL-061 Compatibility Surface |
| adr:0035_homoiconic_type_definition_system | REFERENCES_AUTHORITY | cdl:097_type_definition_node_authority | docs/adr/ADR_0035_Homoiconic_Type_Definition_System.md | 3 | CDL-097 | **Status:** Accepted — CDL-097 ratified Phase 1528p; implementation authority in place; runtime scaffold is Phase 1529p work; no production activation authorized. |
| adr:0035_homoiconic_type_definition_system | REFERENCES_AUTHORITY | adr:0030_node_embedding_substrate | docs/adr/ADR_0035_Homoiconic_Type_Definition_System.md | 102 | ADR-0030 | ### 3.2 Relationship to ADR-0030 |
| adr:0035_homoiconic_type_definition_system | REFERENCES_AUTHORITY | adr:0004_genesis_truth_primitives | docs/adr/ADR_0035_Homoiconic_Type_Definition_System.md | 171 | ADR-0004 | primitives established in ADR-0004: |
| adr:0035_homoiconic_type_definition_system | REFERENCES_AUTHORITY | adr:0019_graph_native_governance_compilation_boundary | docs/adr/ADR_0035_Homoiconic_Type_Definition_System.md | 221 | ADR-0019 | \| ADR-0019 \| Graph-native governance boundary. ADR-0035 brings type definitions inside that boundary \| |
| adr:0035_homoiconic_type_definition_system | REFERENCES_AUTHORITY | adr:0021_epistemic_finality_claims | docs/adr/ADR_0035_Homoiconic_Type_Definition_System.md | 222 | ADR-0021 | \| ADR-0021 \| Epistemic finality claims. Type-level claims are constitutional; they use the CDL process, not the normal Popperian evaluation path \| |
| adr:0035_homoiconic_type_definition_system | REFERENCES_AUTHORITY | adr:0029_hypergraph_substrate | docs/adr/ADR_0035_Homoiconic_Type_Definition_System.md | 223 | ADR-0029 | \| ADR-0029 \| Established hypergraph substrate and star expansion. ADR-0035 governs the type of hyperedge, not just its structure \| |
| adr:0035_homoiconic_type_definition_system | REFERENCES_AUTHORITY | adr:0033_star_map_homoiconic_entity | docs/adr/ADR_0035_Homoiconic_Type_Definition_System.md | 225 | ADR-0033 | \| ADR-0033 \| Star-map navigation results as first-class nodes. ADR-0035 may eventually govern the `star_map` NodeType as a definition node once CDL is opened \| |
| adr:0037_genesis_canonical_lineage_contract | REFERENCES_AUTHORITY | cdl:085_werner_phi_bound | docs/adr/ADR_0037_Genesis_Canonical_Lineage_Contract.md | 13 | CDL-085 | Window 1156-1165 closed with CDL-085 still SIM-gated and with the unsigned Genesis |
| adr:0037_genesis_canonical_lineage_contract | REFERENCES_AUTHORITY | adr:0036_operational_release_key_genesis_binding | docs/adr/ADR_0037_Genesis_Canonical_Lineage_Contract.md | 18 | ADR-0036 | The contract is separate from ADR-0036. ADR-0036 covers a delegated operational release |
| adr:0037_genesis_canonical_lineage_contract | REFERENCES_AUTHORITY | cdl:v7_agent_decomposition | docs/adr/ADR_0037_Genesis_Canonical_Lineage_Contract.md | 194 | CDL-V7 | CDL-V7 (`cdl_v7_popperian_gate_runtime_398.v0.1`) is the existing single-claim |
| adr:0038_agent_birth_attestation | REFERENCES_AUTHORITY | cdl:042_agent_id_flat_namespace | docs/adr/ADR_0038_Agent_Birth_Attestation.md | 7 | CDL-042 | **Dependencies:** ADR-0037, CDL-042, CDL-069, Phase 587 public identity boundary |
| adr:0038_agent_birth_attestation | REFERENCES_AUTHORITY | cdl:069_pq_identity_epoch_endorsement | docs/adr/ADR_0038_Agent_Birth_Attestation.md | 7 | CDL-069 | **Dependencies:** ADR-0037, CDL-042, CDL-069, Phase 587 public identity boundary |
| adr:0038_agent_birth_attestation | REFERENCES_AUTHORITY | adr:0037_genesis_canonical_lineage_contract | docs/adr/ADR_0038_Agent_Birth_Attestation.md | 7 | ADR-0037 | **Dependencies:** ADR-0037, CDL-042, CDL-069, Phase 587 public identity boundary |
| adr:0038_agent_birth_attestation | REFERENCES_AUTHORITY | cdl:090_identity_bootstrap | docs/adr/ADR_0038_Agent_Birth_Attestation.md | 40 | CDL-090 | before CDL-090 opens the non-custodial identity bootstrap lane. |
| adr:0039_validator_endpoint_registry | REFERENCES_AUTHORITY | cdl:017_validator_admission_ejection | docs/adr/ADR_0039_Validator_Endpoint_Registry.md | 7 | CDL-017 | **Dependencies:** CDL-017, CDL-068, CDL-078, ADR-0038, CDL-090, Phase 1360 Fix2a, Phase 1386a |
| adr:0039_validator_endpoint_registry | REFERENCES_AUTHORITY | cdl:068_topology_shuffle_vrf_runtime | docs/adr/ADR_0039_Validator_Endpoint_Registry.md | 7 | CDL-068 | **Dependencies:** CDL-017, CDL-068, CDL-078, ADR-0038, CDL-090, Phase 1360 Fix2a, Phase 1386a |
| adr:0039_validator_endpoint_registry | REFERENCES_AUTHORITY | cdl:078_relay_incentive_constitutional_lock | docs/adr/ADR_0039_Validator_Endpoint_Registry.md | 7 | CDL-078 | **Dependencies:** CDL-017, CDL-068, CDL-078, ADR-0038, CDL-090, Phase 1360 Fix2a, Phase 1386a |
| adr:0039_validator_endpoint_registry | REFERENCES_AUTHORITY | cdl:090_identity_bootstrap | docs/adr/ADR_0039_Validator_Endpoint_Registry.md | 7 | CDL-090 | **Dependencies:** CDL-017, CDL-068, CDL-078, ADR-0038, CDL-090, Phase 1360 Fix2a, Phase 1386a |
| adr:0039_validator_endpoint_registry | REFERENCES_AUTHORITY | adr:0038_agent_birth_attestation | docs/adr/ADR_0039_Validator_Endpoint_Registry.md | 7 | ADR-0038 | **Dependencies:** CDL-017, CDL-068, CDL-078, ADR-0038, CDL-090, Phase 1360 Fix2a, Phase 1386a |
| adr:0039_validator_endpoint_registry | REFERENCES_AUTHORITY | cdl:088_public_claimability | docs/adr/ADR_0039_Validator_Endpoint_Registry.md | 82 | CDL-088 | the endpoint-claim identity authority. CDL-088 governs public claimability authority |
| adr:0040_jury_eligibility_assignment | REFERENCES_AUTHORITY | cdl:052_epistemic_evaluation_contract | docs/adr/ADR_0040_Jury_Eligibility_Assignment.md | 7 | CDL-052 | **Dependencies:** ADM-003, ADR-0038, CDL-052, CDL-059, CDL-068, CDL-090, CDL-V3, CDL-V7, Phase 1391 / J-001 |
| adr:0040_jury_eligibility_assignment | REFERENCES_AUTHORITY | cdl:059_quality_signal_architecture | docs/adr/ADR_0040_Jury_Eligibility_Assignment.md | 7 | CDL-059 | **Dependencies:** ADM-003, ADR-0038, CDL-052, CDL-059, CDL-068, CDL-090, CDL-V3, CDL-V7, Phase 1391 / J-001 |
| adr:0040_jury_eligibility_assignment | REFERENCES_AUTHORITY | cdl:068_topology_shuffle_vrf_runtime | docs/adr/ADR_0040_Jury_Eligibility_Assignment.md | 7 | CDL-068 | **Dependencies:** ADM-003, ADR-0038, CDL-052, CDL-059, CDL-068, CDL-090, CDL-V3, CDL-V7, Phase 1391 / J-001 |
| adr:0040_jury_eligibility_assignment | REFERENCES_AUTHORITY | cdl:090_identity_bootstrap | docs/adr/ADR_0040_Jury_Eligibility_Assignment.md | 7 | CDL-090 | **Dependencies:** ADM-003, ADR-0038, CDL-052, CDL-059, CDL-068, CDL-090, CDL-V3, CDL-V7, Phase 1391 / J-001 |
| adr:0040_jury_eligibility_assignment | REFERENCES_AUTHORITY | cdl:v3_quorum_diversity | docs/adr/ADR_0040_Jury_Eligibility_Assignment.md | 7 | CDL-V3 | **Dependencies:** ADM-003, ADR-0038, CDL-052, CDL-059, CDL-068, CDL-090, CDL-V3, CDL-V7, Phase 1391 / J-001 |
| adr:0040_jury_eligibility_assignment | REFERENCES_AUTHORITY | cdl:v7_agent_decomposition | docs/adr/ADR_0040_Jury_Eligibility_Assignment.md | 7 | CDL-V7 | **Dependencies:** ADM-003, ADR-0038, CDL-052, CDL-059, CDL-068, CDL-090, CDL-V3, CDL-V7, Phase 1391 / J-001 |
| adr:0040_jury_eligibility_assignment | REFERENCES_AUTHORITY | adr:0038_agent_birth_attestation | docs/adr/ADR_0040_Jury_Eligibility_Assignment.md | 7 | ADR-0038 | **Dependencies:** ADM-003, ADR-0038, CDL-052, CDL-059, CDL-068, CDL-090, CDL-V3, CDL-V7, Phase 1391 / J-001 |
| adr:0041_agent_init_and_ingestion_protocol | REFERENCES_AUTHORITY | cdl:042_agent_id_flat_namespace | docs/adr/ADR_0041_Agent_INIT_and_Ingestion_Protocol.md | 7 | CDL-042 | **Dependencies:** CDL-042, CDL-069, CDL-078, ADR-0035, ADR-0040, ADR-0038, |
| adr:0041_agent_init_and_ingestion_protocol | REFERENCES_AUTHORITY | cdl:069_pq_identity_epoch_endorsement | docs/adr/ADR_0041_Agent_INIT_and_Ingestion_Protocol.md | 7 | CDL-069 | **Dependencies:** CDL-042, CDL-069, CDL-078, ADR-0035, ADR-0040, ADR-0038, |
| adr:0041_agent_init_and_ingestion_protocol | REFERENCES_AUTHORITY | cdl:078_relay_incentive_constitutional_lock | docs/adr/ADR_0041_Agent_INIT_and_Ingestion_Protocol.md | 7 | CDL-078 | **Dependencies:** CDL-042, CDL-069, CDL-078, ADR-0035, ADR-0040, ADR-0038, |
| adr:0041_agent_init_and_ingestion_protocol | REFERENCES_AUTHORITY | adr:0035_homoiconic_type_definition_system | docs/adr/ADR_0041_Agent_INIT_and_Ingestion_Protocol.md | 7 | ADR-0035 | **Dependencies:** CDL-042, CDL-069, CDL-078, ADR-0035, ADR-0040, ADR-0038, |
| adr:0041_agent_init_and_ingestion_protocol | REFERENCES_AUTHORITY | adr:0040_jury_eligibility_assignment | docs/adr/ADR_0041_Agent_INIT_and_Ingestion_Protocol.md | 7 | ADR-0040 | **Dependencies:** CDL-042, CDL-069, CDL-078, ADR-0035, ADR-0040, ADR-0038, |
| adr:0041_agent_init_and_ingestion_protocol | REFERENCES_AUTHORITY | adr:0038_agent_birth_attestation | docs/adr/ADR_0041_Agent_INIT_and_Ingestion_Protocol.md | 7 | ADR-0038 | **Dependencies:** CDL-042, CDL-069, CDL-078, ADR-0035, ADR-0040, ADR-0038, |
| adr:0042_vrf_proof_verifier | REFERENCES_AUTHORITY | cdl:068_topology_shuffle_vrf_runtime | docs/adr/ADR_0042_VRF_Proof_Verifier.md | 7 | CDL-068 | **Dependencies:** ADR-0040, ADR-0038, CDL-068, Phase 1396/J-006, Phase 1398/J-008, Phase 1409 |
| adr:0042_vrf_proof_verifier | REFERENCES_AUTHORITY | adr:0040_jury_eligibility_assignment | docs/adr/ADR_0042_VRF_Proof_Verifier.md | 7 | ADR-0040 | **Dependencies:** ADR-0040, ADR-0038, CDL-068, Phase 1396/J-006, Phase 1398/J-008, Phase 1409 |
| adr:0042_vrf_proof_verifier | REFERENCES_AUTHORITY | adr:0038_agent_birth_attestation | docs/adr/ADR_0042_VRF_Proof_Verifier.md | 7 | ADR-0038 | **Dependencies:** ADR-0040, ADR-0038, CDL-068, Phase 1396/J-006, Phase 1398/J-008, Phase 1409 |
| adr:0042_vrf_proof_verifier | REFERENCES_AUTHORITY | adr:0041_agent_init_and_ingestion_protocol | docs/adr/ADR_0042_VRF_Proof_Verifier.md | 35 | ADR-0041 | \| ADR-0042 is the next ADR number \| `docs/adr/` directory listing \| confirmed: ADR-0040 and ADR-0041 are present; no ADR-0042 existed before this phase \| |
| adr:0042_vrf_proof_verifier | REFERENCES_AUTHORITY | cdl:090_identity_bootstrap | docs/adr/ADR_0042_VRF_Proof_Verifier.md | 111 | CDL-090 | "identity_lineage_ref": "<ADR-0038/CDL-090-compatible identity lineage ref>", |
| adr:0043_review_lane_t0_5_to_t1_promotion | REFERENCES_AUTHORITY | cdl:091_jury_incentive | docs/adr/ADR_0043_Review_Lane_T0_5_To_T1_Promotion.md | 7 | CDL-091 | **Dependencies:** ADR-0041, ADR-0040, CDL-091, Phase 1387a, Phase 1397/J-007, Phase 1398/J-008, Phase 1412, Phase 1413 |
| adr:0043_review_lane_t0_5_to_t1_promotion | REFERENCES_AUTHORITY | adr:0041_agent_init_and_ingestion_protocol | docs/adr/ADR_0043_Review_Lane_T0_5_To_T1_Promotion.md | 7 | ADR-0041 | **Dependencies:** ADR-0041, ADR-0040, CDL-091, Phase 1387a, Phase 1397/J-007, Phase 1398/J-008, Phase 1412, Phase 1413 |
| adr:0043_review_lane_t0_5_to_t1_promotion | REFERENCES_AUTHORITY | adr:0040_jury_eligibility_assignment | docs/adr/ADR_0043_Review_Lane_T0_5_To_T1_Promotion.md | 7 | ADR-0040 | **Dependencies:** ADR-0041, ADR-0040, CDL-091, Phase 1387a, Phase 1397/J-007, Phase 1398/J-008, Phase 1412, Phase 1413 |
| adr:0043_review_lane_t0_5_to_t1_promotion | REFERENCES_AUTHORITY | adr:0042_vrf_proof_verifier | docs/adr/ADR_0043_Review_Lane_T0_5_To_T1_Promotion.md | 43 | ADR-0042 | \| ADR-0043 is the next ADR number \| `docs/adr/` directory listing \| confirmed: ADR-0042 is present and no ADR-0043 existed before this phase \| |
| adr:0044_anti_capture_diversity_verification | REFERENCES_AUTHORITY | cdl:v3_quorum_diversity | docs/adr/ADR_0044_Anti_Capture_Diversity_Verification.md | 7 | CDL-V3 | **Dependencies:** ADR-0040, ADR-0042, ADR-0043, CDL-V3, Phase 397, Phase 1412, Phase 1413, Phase 1417, Phase 1398/J-008 |
| adr:0044_anti_capture_diversity_verification | REFERENCES_AUTHORITY | adr:0040_jury_eligibility_assignment | docs/adr/ADR_0044_Anti_Capture_Diversity_Verification.md | 7 | ADR-0040 | **Dependencies:** ADR-0040, ADR-0042, ADR-0043, CDL-V3, Phase 397, Phase 1412, Phase 1413, Phase 1417, Phase 1398/J-008 |
| adr:0044_anti_capture_diversity_verification | REFERENCES_AUTHORITY | adr:0042_vrf_proof_verifier | docs/adr/ADR_0044_Anti_Capture_Diversity_Verification.md | 7 | ADR-0042 | **Dependencies:** ADR-0040, ADR-0042, ADR-0043, CDL-V3, Phase 397, Phase 1412, Phase 1413, Phase 1417, Phase 1398/J-008 |
| adr:0044_anti_capture_diversity_verification | REFERENCES_AUTHORITY | adr:0043_review_lane_t0_5_to_t1_promotion | docs/adr/ADR_0044_Anti_Capture_Diversity_Verification.md | 7 | ADR-0043 | **Dependencies:** ADR-0040, ADR-0042, ADR-0043, CDL-V3, Phase 397, Phase 1412, Phase 1413, Phase 1417, Phase 1398/J-008 |
| adr:0044_anti_capture_diversity_verification | REFERENCES_AUTHORITY | cdl:068_topology_shuffle_vrf_runtime | docs/adr/ADR_0044_Anti_Capture_Diversity_Verification.md | 114 | CDL-068 | CDL-068 validator topology thresholds remain separate. |

## CDL to ADR GOVERNS Edges Added

No `cdl:* --GOVERNS--> adr:*` edges were added in Fix70. The CDL register contains many ADR dependency references, but this pass requires explicit governance/authorization/constraining language for reverse `GOVERNS` edges and does not infer governance from subject overlap or dependency columns.

## CDL Lineage Edges Added

| source | edge_type | target | evidence_source_path | evidence_line | reference_label | evidence_text |
| --- | --- | --- | --- | --- | --- | --- |
| cdl:069_pq_identity_epoch_endorsement | DERIVED_FROM | cdl:042_agent_id_flat_namespace | docs/specs/ilc_constitutional_decision_log_v0.1.md | 101 | CDL-069 amends CDL-042 | \| CDL-069 \| CDL-042 / ADR-0001 / Phase-838 / NIST FIPS 204 / Row-5 / CDL-066 / CDL-017 \| Post-quantum agent identity root (ML-DSA-65) and epoch endorsement protocol — amends CDL-042 identity derivation, establishes endorsed ephemeral session key protocol across protocol, agency, economic, cryptographic, governance, and privacy ambits \| ratified \| retain BLS12-381 for identity root with planned PQ migration later, adopt ML-DSA-65 as identity root from Genesis with BLS retained for consensus only, adopt hybrid dual-key with deferred migration ceremony \| adopt ML-DSA-65 as mandatory identity root from Genesis forward with BLS retained exclusively for consensus aggregation and ephemeral hot signing; epoch endorsement packet binds identity root to per-epoch ephemeral key \| docs/specs/ilc_cdl_069_pq_identity_and_epoch_endorsement_protocol_opening_838_v0.1.md \| opened_phase: 838 \| opened_date: 2026-04-25 \| ratified_phase: 838j \| ratified_date: 2026-04-26 \| evidence_document: docs/specs/ilc_cdl_069_pq_identity_and_epoch_endorsement_protocol_ratification_evidence_838j_v0.1.md \| |

## Lifecycle Record Edges Added

| source | edge_type | target | evidence_source_path | evidence_line | reference_label | evidence_text |
| --- | --- | --- | --- | --- | --- | --- |
| cdl:085_prelock_historical_opening_and_prelock_state | PRELOCK_FOR | cdl:085_werner_phi_bound | live_lmdb_node_record | None | CDL-085 historical opening/prelock lifecycle node | cdl:085_prelock_historical_opening_and_prelock_state |

## Stale Lifecycle GOVERNS Review Queue

- `cdl:011_node_usefulness_formula_ratification_ew`

## Unresolvable Targets

| source | source_file | source_adr | reference | reason | line | line_text |
| --- | --- | --- | --- | --- | --- | --- |
| adr:0016 | docs/adr/ADR_0016_Productive_ECU_Expansion_Bounty_Mechanism.md |  | ADR-0017 | target_node_missing | 82 | - Under the corrected ECU-side Treasury governance model (see ADR-0017 correction and `docs/research/ilc_opus_treasury_jubilee_and_graph_dependency_analysis_v0.1.md`), the ADR-0016 push/pull bounty mechanism is the Treasury's **primary expansionary lever** — not a supplementary feature. Protocol-issued bounties (stimulus) and peer-funded bounties (demand-side pull) are the main tool for ECU credit expansion during downturns, replacing the ILC-side reserve manipulation model previously described in ADR-0017. |
|  | docs/adr/ADR_0017_Post_Issuance_Economic_Transition.md | 0017 | ADR-0017 | source_adr_node_missing | 1 | # ADR-0017: Post-Issuance Economic Transition and Late-Economy Design |
|  | docs/adr/ADR_0017_Post_Issuance_Economic_Transition.md | 0017 | CDL-025 | source_adr_node_missing | 7 | **Dependencies:** CDL-025 (terminal issuance model B — fee-funded tail), CDL-026 (C_max lock), CDL-027 (halving H=48), CDL-028 (fee-burn split), CDL-030 (P_e clamp 0.75-1.30) |
|  | docs/adr/ADR_0017_Post_Issuance_Economic_Transition.md | 0017 | CDL-026 | source_adr_node_missing | 7 | **Dependencies:** CDL-025 (terminal issuance model B — fee-funded tail), CDL-026 (C_max lock), CDL-027 (halving H=48), CDL-028 (fee-burn split), CDL-030 (P_e clamp 0.75-1.30) |
|  | docs/adr/ADR_0017_Post_Issuance_Economic_Transition.md | 0017 | CDL-027 | source_adr_node_missing | 7 | **Dependencies:** CDL-025 (terminal issuance model B — fee-funded tail), CDL-026 (C_max lock), CDL-027 (halving H=48), CDL-028 (fee-burn split), CDL-030 (P_e clamp 0.75-1.30) |
|  | docs/adr/ADR_0017_Post_Issuance_Economic_Transition.md | 0017 | CDL-028 | source_adr_node_missing | 7 | **Dependencies:** CDL-025 (terminal issuance model B — fee-funded tail), CDL-026 (C_max lock), CDL-027 (halving H=48), CDL-028 (fee-burn split), CDL-030 (P_e clamp 0.75-1.30) |
|  | docs/adr/ADR_0017_Post_Issuance_Economic_Transition.md | 0017 | CDL-030 | source_adr_node_missing | 7 | **Dependencies:** CDL-025 (terminal issuance model B — fee-funded tail), CDL-026 (C_max lock), CDL-027 (halving H=48), CDL-028 (fee-burn split), CDL-030 (P_e clamp 0.75-1.30) |
|  | docs/adr/ADR_0017_Post_Issuance_Economic_Transition.md | 0017 | CDL-029 | source_adr_node_missing | 29 | The treasury (funded by 5% genesis allocation per CDL-029, ongoing fee revenue, transfer tax revenue per ADR-0015, and node reversion revenue) should be designed to govern ECU-side credit conditions as a counter-cyclical economic stabilizer in the late economy. |
|  | docs/adr/ADR_0017_Post_Issuance_Economic_Transition.md | 0017 | ADR-0015 | source_adr_node_missing | 29 | The treasury (funded by 5% genesis allocation per CDL-029, ongoing fee revenue, transfer tax revenue per ADR-0015, and node reversion revenue) should be designed to govern ECU-side credit conditions as a counter-cyclical economic stabilizer in the late economy. |
|  | docs/adr/ADR_0017_Post_Issuance_Economic_Transition.md | 0017 | ADR-0016 | source_adr_node_missing | 35 | - **Stimulus (ECU expansion):** Protocol bounties and peer-funded bounties (ADR-0016 push/pull mechanism) to expand productive ECU creation during downturns. This is the Treasury's primary expansionary lever. |

## Safe Writer Receipts

```json
{
  "dry_run": {
    "accepted_edge_count": 134,
    "accepted_edges": [
      {
        "edge_id": "edge:9723593c8617a507",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0002_ndjson_bundle_transport",
        "target": "adr:0003_star_map_ngram_route_index"
      },
      {
        "edge_id": "edge:d5046a98ada7611c",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0003_star_map_ngram_route_index",
        "target": "adr:0001_canonical_encoding_node_id_agent_interface"
      },
      {
        "edge_id": "edge:020a50c74283e98c",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0003_star_map_ngram_route_index",
        "target": "adr:0002_ndjson_bundle_transport"
      },
      {
        "edge_id": "edge:0e232b28c6c8c49a",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0005_star_map_observational_feeds",
        "target": "adr:0002_ndjson_bundle_transport"
      },
      {
        "edge_id": "edge:47444a9e0caca346",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0006_eve_canonical_capsule_integrity",
        "target": "adr:0001_canonical_encoding_node_id_agent_interface"
      },
      {
        "edge_id": "edge:c74763cb443fbe73",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0008_node_usefulness_governance_weight_genesis_dilution",
        "target": "cdl:013_governance_weight"
      },
      {
        "edge_id": "edge:71884405eab26f8e",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0009_bundle_distribution",
        "target": "cdl:022_genesis_state_bundle_specification_signing_ceremony"
      },
      {
        "edge_id": "edge:5bc9a0180b501204",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0009_bundle_distribution",
        "target": "cdl:019_multiplier_governance_surface"
      },
      {
        "edge_id": "edge:3911bf72690367a4",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0009_bundle_distribution",
        "target": "cdl:020"
      },
      {
        "edge_id": "edge:fb66c67cfe98991b",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0009_bundle_distribution",
        "target": "cdl:021"
      },
      {
        "edge_id": "edge:7dd242fb2b562264",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0009_bundle_distribution",
        "target": "cdl:023_epoch_snapshot_contract"
      },
      {
        "edge_id": "edge:3d3cb9e441180092",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0009_bundle_distribution",
        "target": "cdl:024"
      },
      {
        "edge_id": "edge:7570da8f9234c11d",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0009_bundle_distribution",
        "target": "adr:0001_canonical_encoding_node_id_agent_interface"
      },
      {
        "edge_id": "edge:d426eef838a45cdd",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0009_bundle_distribution",
        "target": "adr:0002_ndjson_bundle_transport"
      },
      {
        "edge_id": "edge:591d6cbbce782cc9",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0009_bundle_distribution",
        "target": "adr:0004_genesis_truth_primitives"
      },
      {
        "edge_id": "edge:dc8f7c6a196f45be",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0009_bundle_distribution",
        "target": "adr:0007_constitutional_baseline_ratification_process"
      },
      {
        "edge_id": "edge:e49aced2901f44b6",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0009_bundle_distribution",
        "target": "adr:0008_node_usefulness_governance_weight_genesis_dilution"
      },
      {
        "edge_id": "edge:5917d2b99684c9f7",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0011_native_p2p_transport_baseline_agent_communication",
        "target": "cdl:024"
      },
      {
        "edge_id": "edge:813ab79a48f548d2",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0011_native_p2p_transport_baseline_agent_communication",
        "target": "adr:0025_transport_binding"
      },
      {
        "edge_id": "edge:c1430918a994d455",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0015_node_transfer_economics",
        "target": "cdl:034_node_schema_core_runtime"
      },
      {
        "edge_id": "edge:4358ea2d45e6166e",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0015_node_transfer_economics",
        "target": "cdl:035_validation_lifecycle"
      },
      {
        "edge_id": "edge:5846656991b8e09f",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0015_node_transfer_economics",
        "target": "cdl:v1_temporal_decay"
      },
      {
        "edge_id": "edge:159a588f149518f5",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0015_node_transfer_economics",
        "target": "cdl:v7_agent_decomposition"
      },
      {
        "edge_id": "edge:c77a116c246e4afc",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0015_node_transfer_economics",
        "target": "cdl:029_80_15_5_allocation_distribution"
      },
      {
        "edge_id": "edge:14f162d543b9776f",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0015_node_transfer_economics",
        "target": "cdl:013_governance_weight"
      },
      {
        "edge_id": "edge:3b8fbe47fabf960e",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0016",
        "target": "cdl:025_terminal_issuance_model"
      },
      {
        "edge_id": "edge:a5aa12daaf69d371",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0016",
        "target": "cdl:029_80_15_5_allocation_distribution"
      },
      {
        "edge_id": "edge:80f2a43016a0c28a",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0016",
        "target": "cdl:v3_quorum_diversity"
      },
      {
        "edge_id": "edge:fd772199726f0dd4",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0016",
        "target": "cdl:v7_agent_decomposition"
      },
      {
        "edge_id": "edge:35edd623d13f51ef",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0016",
        "target": "cdl:035_validation_lifecycle"
      },
      {
        "edge_id": "edge:202affbd969d3998",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0018_sequestered_financial_shard",
        "target": "cdl:051_epoch_state_quorum"
      },
      {
        "edge_id": "edge:99e99a5cc4e54da9",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0018_sequestered_financial_shard",
        "target": "cdl:050_treasury_ecu_governor_lane"
      },
      {
        "edge_id": "edge:a435af16bb72d554",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0019_graph_native_governance_compilation_boundary",
        "target": "adr:0007_constitutional_baseline_ratification_process"
      },
      {
        "edge_id": "edge:e302d9de80ccb2b0",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0019_graph_native_governance_compilation_boundary",
        "target": "adr:0009_bundle_distribution"
      },
      {
        "edge_id": "edge:b9922c6117157c14",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0019_graph_native_governance_compilation_boundary",
        "target": "adr:0011_native_p2p_transport_baseline_agent_communication"
      },
      {
        "edge_id": "edge:46fea8bb5eb9c1d4",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0020_knowledge_node_first_design_principle",
        "target": "cdl:v7_agent_decomposition"
      },
      {
        "edge_id": "edge:aa7a70843d73d5ff",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0020_knowledge_node_first_design_principle",
        "target": "adr:0019_graph_native_governance_compilation_boundary"
      },
      {
        "edge_id": "edge:0cbf5961615ab77d",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0020_knowledge_node_first_design_principle",
        "target": "cdl:001_signer_lineage_trust_root"
      },
      {
        "edge_id": "edge:d1be0e5ab9adbf0c",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0020_knowledge_node_first_design_principle",
        "target": "cdl:050_treasury_ecu_governor_lane"
      },
      {
        "edge_id": "edge:e87f2c5b69c7f6a5",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0020_knowledge_node_first_design_principle",
        "target": "adr:0021_epistemic_finality_claims"
      },
      {
        "edge_id": "edge:6a444c185ebc260a",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0022_local_first_private_publication_bound_economics",
        "target": "adr:0019_graph_native_governance_compilation_boundary"
      },
      {
        "edge_id": "edge:d84a31b1716cdbc4",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0022_local_first_private_publication_bound_economics",
        "target": "adr:0020_knowledge_node_first_design_principle"
      },
      {
        "edge_id": "edge:3e13bc975744ce23",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0023_multi_layer_quality_signal_architecture",
        "target": "cdl:v7_agent_decomposition"
      },
      {
        "edge_id": "edge:e1f6c1df2a89b72a",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0023_multi_layer_quality_signal_architecture",
        "target": "cdl:049_bounded_existential_alignment"
      },
      {
        "edge_id": "edge:e9da80c15c0c9967",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0023_multi_layer_quality_signal_architecture",
        "target": "cdl:036_node_dissemination_runtime"
      },
      {
        "edge_id": "edge:0a0c47fa4480bed6",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0023_multi_layer_quality_signal_architecture",
        "target": "cdl:v3_quorum_diversity"
      },
      {
        "edge_id": "edge:1b463aaa0b64503b",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0023_multi_layer_quality_signal_architecture",
        "target": "cdl:039_topology_shuffling_authorization"
      },
      {
        "edge_id": "edge:8216f3d12bcb419b",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0023_multi_layer_quality_signal_architecture",
        "target": "cdl:v4_minority_dissent_appeal_reopening_ratified_cdl_decisions"
      },
      {
        "edge_id": "edge:449c3fdc4a2c408a",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0023_multi_layer_quality_signal_architecture",
        "target": "cdl:053_werner_local_productive_credit_future_vehicle"
      },
      {
        "edge_id": "edge:b1a000fbdc8b524a",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0023_multi_layer_quality_signal_architecture",
        "target": "cdl:030_ecu_price_clamp_runtime"
      },
      {
        "edge_id": "edge:948801adf8bb4587",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0023_multi_layer_quality_signal_architecture",
        "target": "adr:0016"
      },
      {
        "edge_id": "edge:fe4c8a4931f37c61",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0023_multi_layer_quality_signal_architecture",
        "target": "cdl:060_gossip_centrality_extension"
      },
      {
        "edge_id": "edge:3a1826337c95e6c0",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0023_multi_layer_quality_signal_architecture",
        "target": "cdl:061_gossip_http_envelope"
      },
      {
        "edge_id": "edge:2736e1d3c98bd4bd",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0024_agent_skills_infrastructure",
        "target": "cdl:034_node_schema_core_runtime"
      },
      {
        "edge_id": "edge:9b071058db3135c0",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0024_agent_skills_infrastructure",
        "target": "cdl:052_epistemic_evaluation_contract"
      },
      {
        "edge_id": "edge:e106a8cbd77c65cd",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0024_agent_skills_infrastructure",
        "target": "cdl:v7_agent_decomposition"
      },
      {
        "edge_id": "edge:9a4e40eedb2ed5cf",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0024_agent_skills_infrastructure",
        "target": "cdl:053_werner_local_productive_credit_future_vehicle"
      },
      {
        "edge_id": "edge:48ff53f16107bb7a",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0025_transport_binding",
        "target": "adr:0011_native_p2p_transport_baseline_agent_communication"
      },
      {
        "edge_id": "edge:cd7a5983e0cbb4fa",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0025_transport_binding",
        "target": "cdl:024"
      },
      {
        "edge_id": "edge:766058a2870c12db",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0025_transport_binding",
        "target": "cdl:039_topology_shuffling_authorization"
      },
      {
        "edge_id": "edge:0450dc997a73def8",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0025_transport_binding",
        "target": "cdl:060_gossip_centrality_extension"
      },
      {
        "edge_id": "edge:63fe938f7bd1c731",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0025_transport_binding",
        "target": "cdl:036_node_dissemination_runtime"
      },
      {
        "edge_id": "edge:f9dedfc8d9252a4d",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0025_transport_binding",
        "target": "cdl:061_gossip_http_envelope"
      },
      {
        "edge_id": "edge:b5248c6255c4a0f8",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0025_transport_binding",
        "target": "cdl:047_treasury_governance"
      },
      {
        "edge_id": "edge:bb5a8d9ef650ab20",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0026_protocol_vs_harness_product_boundary",
        "target": "adr:0022_local_first_private_publication_bound_economics"
      },
      {
        "edge_id": "edge:18945707129ed8a5",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0027_canonical_bootstrap_receipt_boundary",
        "target": "adr:0026_protocol_vs_harness_product_boundary"
      },
      {
        "edge_id": "edge:3bffa9452e840c93",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0028_settlement_substrate_graduation_governance_route",
        "target": "cdl:062_sovereign_substrate_research_lane"
      },
      {
        "edge_id": "edge:49252cf5de8a19a2",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0029_hypergraph_substrate",
        "target": "cdl:v1_temporal_decay"
      },
      {
        "edge_id": "edge:8bb1669b043c4ebe",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0029_hypergraph_substrate",
        "target": "cdl:v3_quorum_diversity"
      },
      {
        "edge_id": "edge:ce7cb80e3cedd287",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0029_hypergraph_substrate",
        "target": "adr:0030_node_embedding_substrate"
      },
      {
        "edge_id": "edge:60e0d33368d41295",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0029_hypergraph_substrate",
        "target": "adr:0031_subgraph_homomorphism_query_contract"
      },
      {
        "edge_id": "edge:67ff74a359930696",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0030_node_embedding_substrate",
        "target": "adr:0029_hypergraph_substrate"
      },
      {
        "edge_id": "edge:5b1f488c55f890c5",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0030_node_embedding_substrate",
        "target": "cdl:097_type_definition_node_authority"
      },
      {
        "edge_id": "edge:532bfe2c8decf8bc",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0030_node_embedding_substrate",
        "target": "adr:0031_subgraph_homomorphism_query_contract"
      },
      {
        "edge_id": "edge:27b33c40b5fa916b",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0031_subgraph_homomorphism_query_contract",
        "target": "adr:0029_hypergraph_substrate"
      },
      {
        "edge_id": "edge:4efaa0c5363ad400",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0031_subgraph_homomorphism_query_contract",
        "target": "adr:0030_node_embedding_substrate"
      },
      {
        "edge_id": "edge:d55df829ce407821",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0032_temporal_hypergraph",
        "target": "adr:0029_hypergraph_substrate"
      },
      {
        "edge_id": "edge:98f9e6acfe4f65a7",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0032_temporal_hypergraph",
        "target": "adr:0030_node_embedding_substrate"
      },
      {
        "edge_id": "edge:fb85121656bf9504",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0032_temporal_hypergraph",
        "target": "adr:0031_subgraph_homomorphism_query_contract"
      },
      {
        "edge_id": "edge:bbaf5dd5b31fc8c8",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0033_star_map_homoiconic_entity",
        "target": "adr:0003_star_map_ngram_route_index"
      },
      {
        "edge_id": "edge:4231946a057cc67c",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0033_star_map_homoiconic_entity",
        "target": "adr:0005_star_map_observational_feeds"
      },
      {
        "edge_id": "edge:7f8adcf797c8dee4",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0033_star_map_homoiconic_entity",
        "target": "adr:0029_hypergraph_substrate"
      },
      {
        "edge_id": "edge:b7312e1bd59813a4",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0033_star_map_homoiconic_entity",
        "target": "adr:0030_node_embedding_substrate"
      },
      {
        "edge_id": "edge:f2b900b67d6e3f73",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0034_d2d_sealed_sender",
        "target": "cdl:060_gossip_centrality_extension"
      },
      {
        "edge_id": "edge:cdd2c84ce4d73ea6",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0034_d2d_sealed_sender",
        "target": "cdl:061_gossip_http_envelope"
      },
      {
        "edge_id": "edge:eea2c1220bd5ff4f",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0035_homoiconic_type_definition_system",
        "target": "cdl:097_type_definition_node_authority"
      },
      {
        "edge_id": "edge:e0636ce9edfc5aa3",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0035_homoiconic_type_definition_system",
        "target": "adr:0030_node_embedding_substrate"
      },
      {
        "edge_id": "edge:3f61131186e09f75",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0035_homoiconic_type_definition_system",
        "target": "adr:0004_genesis_truth_primitives"
      },
      {
        "edge_id": "edge:35dfdcd92c4c5421",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0035_homoiconic_type_definition_system",
        "target": "adr:0019_graph_native_governance_compilation_boundary"
      },
      {
        "edge_id": "edge:c741ca789e28ec6e",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0035_homoiconic_type_definition_system",
        "target": "adr:0021_epistemic_finality_claims"
      },
      {
        "edge_id": "edge:ebe83c4d0ae123aa",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0035_homoiconic_type_definition_system",
        "target": "adr:0029_hypergraph_substrate"
      },
      {
        "edge_id": "edge:cec016db2e413a98",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0035_homoiconic_type_definition_system",
        "target": "adr:0033_star_map_homoiconic_entity"
      },
      {
        "edge_id": "edge:a6be5b3e365fcb73",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0037_genesis_canonical_lineage_contract",
        "target": "cdl:085_werner_phi_bound"
      },
      {
        "edge_id": "edge:86ddeffd30a65d67",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0037_genesis_canonical_lineage_contract",
        "target": "adr:0036_operational_release_key_genesis_binding"
      },
      {
        "edge_id": "edge:8f13bec7a12082a2",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0037_genesis_canonical_lineage_contract",
        "target": "cdl:v7_agent_decomposition"
      },
      {
        "edge_id": "edge:19f767719e8f8862",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0038_agent_birth_attestation",
        "target": "cdl:042_agent_id_flat_namespace"
      },
      {
        "edge_id": "edge:ec24f68407be0e99",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0038_agent_birth_attestation",
        "target": "cdl:069_pq_identity_epoch_endorsement"
      },
      {
        "edge_id": "edge:05ebfab1181f0c90",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0038_agent_birth_attestation",
        "target": "adr:0037_genesis_canonical_lineage_contract"
      },
      {
        "edge_id": "edge:a0b825d6f226f5ea",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0038_agent_birth_attestation",
        "target": "cdl:090_identity_bootstrap"
      },
      {
        "edge_id": "edge:389948f84b74b854",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0039_validator_endpoint_registry",
        "target": "cdl:017_validator_admission_ejection"
      },
      {
        "edge_id": "edge:7788244636f7b689",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0039_validator_endpoint_registry",
        "target": "cdl:068_topology_shuffle_vrf_runtime"
      },
      {
        "edge_id": "edge:1bc9a58f52a8b797",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0039_validator_endpoint_registry",
        "target": "cdl:078_relay_incentive_constitutional_lock"
      },
      {
        "edge_id": "edge:35948acb86c4c9fe",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0039_validator_endpoint_registry",
        "target": "cdl:090_identity_bootstrap"
      },
      {
        "edge_id": "edge:d766f09c9da7cf33",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0039_validator_endpoint_registry",
        "target": "adr:0038_agent_birth_attestation"
      },
      {
        "edge_id": "edge:af1dcf2c04a36523",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0039_validator_endpoint_registry",
        "target": "cdl:088_public_claimability"
      },
      {
        "edge_id": "edge:91fd0b77195ee092",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0040_jury_eligibility_assignment",
        "target": "cdl:052_epistemic_evaluation_contract"
      },
      {
        "edge_id": "edge:9f963e13dae0451f",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0040_jury_eligibility_assignment",
        "target": "cdl:059_quality_signal_architecture"
      },
      {
        "edge_id": "edge:f377e9fc0ff9b752",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0040_jury_eligibility_assignment",
        "target": "cdl:068_topology_shuffle_vrf_runtime"
      },
      {
        "edge_id": "edge:4a17a4204803f817",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0040_jury_eligibility_assignment",
        "target": "cdl:090_identity_bootstrap"
      },
      {
        "edge_id": "edge:7ba90a6e1f0b07f2",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0040_jury_eligibility_assignment",
        "target": "cdl:v3_quorum_diversity"
      },
      {
        "edge_id": "edge:511449277fb5541d",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0040_jury_eligibility_assignment",
        "target": "cdl:v7_agent_decomposition"
      },
      {
        "edge_id": "edge:1d5991a75a2eb274",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0040_jury_eligibility_assignment",
        "target": "adr:0038_agent_birth_attestation"
      },
      {
        "edge_id": "edge:d53241714bed8c4d",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0041_agent_init_and_ingestion_protocol",
        "target": "cdl:042_agent_id_flat_namespace"
      },
      {
        "edge_id": "edge:81f57973cb4a3045",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0041_agent_init_and_ingestion_protocol",
        "target": "cdl:069_pq_identity_epoch_endorsement"
      },
      {
        "edge_id": "edge:75a8c1d86a300eba",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0041_agent_init_and_ingestion_protocol",
        "target": "cdl:078_relay_incentive_constitutional_lock"
      },
      {
        "edge_id": "edge:b96041497ef3c440",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0041_agent_init_and_ingestion_protocol",
        "target": "adr:0035_homoiconic_type_definition_system"
      },
      {
        "edge_id": "edge:b7579c7474d7b0dd",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0041_agent_init_and_ingestion_protocol",
        "target": "adr:0040_jury_eligibility_assignment"
      },
      {
        "edge_id": "edge:3ba41dfa913f29ae",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0041_agent_init_and_ingestion_protocol",
        "target": "adr:0038_agent_birth_attestation"
      },
      {
        "edge_id": "edge:7fc5195c4efa876c",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0042_vrf_proof_verifier",
        "target": "cdl:068_topology_shuffle_vrf_runtime"
      },
      {
        "edge_id": "edge:7e73e5a8fcd6813b",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0042_vrf_proof_verifier",
        "target": "adr:0040_jury_eligibility_assignment"
      },
      {
        "edge_id": "edge:9403a2fdab67d001",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0042_vrf_proof_verifier",
        "target": "adr:0038_agent_birth_attestation"
      },
      {
        "edge_id": "edge:034021c9a6345974",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0042_vrf_proof_verifier",
        "target": "adr:0041_agent_init_and_ingestion_protocol"
      },
      {
        "edge_id": "edge:607ff8cad8284355",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0042_vrf_proof_verifier",
        "target": "cdl:090_identity_bootstrap"
      },
      {
        "edge_id": "edge:d344901fbd89f003",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0043_review_lane_t0_5_to_t1_promotion",
        "target": "cdl:091_jury_incentive"
      },
      {
        "edge_id": "edge:816c5d4ae9437775",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0043_review_lane_t0_5_to_t1_promotion",
        "target": "adr:0041_agent_init_and_ingestion_protocol"
      },
      {
        "edge_id": "edge:9aede2816e063416",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0043_review_lane_t0_5_to_t1_promotion",
        "target": "adr:0040_jury_eligibility_assignment"
      },
      {
        "edge_id": "edge:5a060daad46ef03b",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0043_review_lane_t0_5_to_t1_promotion",
        "target": "adr:0042_vrf_proof_verifier"
      },
      {
        "edge_id": "edge:4e9a85a8050c6a76",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0044_anti_capture_diversity_verification",
        "target": "cdl:v3_quorum_diversity"
      },
      {
        "edge_id": "edge:4279178f4faf16fe",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0044_anti_capture_diversity_verification",
        "target": "adr:0040_jury_eligibility_assignment"
      },
      {
        "edge_id": "edge:847097aaab0fe193",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0044_anti_capture_diversity_verification",
        "target": "adr:0042_vrf_proof_verifier"
      },
      {
        "edge_id": "edge:e90b8aa169be48eb",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0044_anti_capture_diversity_verification",
        "target": "adr:0043_review_lane_t0_5_to_t1_promotion"
      },
      {
        "edge_id": "edge:0294854359b8f438",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0044_anti_capture_diversity_verification",
        "target": "cdl:068_topology_shuffle_vrf_runtime"
      },
      {
        "edge_id": "edge:2ee2b111cbcc7ecc",
        "edge_type": "DERIVED_FROM",
        "source": "cdl:069_pq_identity_epoch_endorsement",
        "target": "cdl:042_agent_id_flat_namespace"
      },
      {
        "edge_id": "edge:980f2e9982c5f880",
        "edge_type": "PRELOCK_FOR",
        "source": "cdl:085_prelock_historical_opening_and_prelock_state",
        "target": "cdl:085_werner_phi_bound"
      }
    ],
    "accepted_node_count": 0,
    "accepted_nodes": [],
    "dry_run": true,
    "metadata": {},
    "mutated": false,
    "phase": "1545p-Fix70",
    "pre_counts": {
      "edges": 89447,
      "nodes": 16821
    },
    "projected_counts": {
      "edges": 89581,
      "nodes": 16821
    },
    "projected_dangling_edge_count": 0,
    "projected_dangling_edges": [],
    "rejected_edge_count": 0,
    "rejected_edges": [],
    "skipped_edge_count": 0,
    "skipped_edges": [],
    "skipped_node_count": 0,
    "skipped_nodes": [],
    "status": "PASS",
    "version": "genesis_atlas_lmdb_writer_1545p_fix59b.v0.1"
  },
  "live": {
    "accepted_edge_count": 134,
    "accepted_edges": [
      {
        "edge_id": "edge:9723593c8617a507",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0002_ndjson_bundle_transport",
        "target": "adr:0003_star_map_ngram_route_index"
      },
      {
        "edge_id": "edge:d5046a98ada7611c",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0003_star_map_ngram_route_index",
        "target": "adr:0001_canonical_encoding_node_id_agent_interface"
      },
      {
        "edge_id": "edge:020a50c74283e98c",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0003_star_map_ngram_route_index",
        "target": "adr:0002_ndjson_bundle_transport"
      },
      {
        "edge_id": "edge:0e232b28c6c8c49a",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0005_star_map_observational_feeds",
        "target": "adr:0002_ndjson_bundle_transport"
      },
      {
        "edge_id": "edge:47444a9e0caca346",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0006_eve_canonical_capsule_integrity",
        "target": "adr:0001_canonical_encoding_node_id_agent_interface"
      },
      {
        "edge_id": "edge:c74763cb443fbe73",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0008_node_usefulness_governance_weight_genesis_dilution",
        "target": "cdl:013_governance_weight"
      },
      {
        "edge_id": "edge:71884405eab26f8e",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0009_bundle_distribution",
        "target": "cdl:022_genesis_state_bundle_specification_signing_ceremony"
      },
      {
        "edge_id": "edge:5bc9a0180b501204",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0009_bundle_distribution",
        "target": "cdl:019_multiplier_governance_surface"
      },
      {
        "edge_id": "edge:3911bf72690367a4",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0009_bundle_distribution",
        "target": "cdl:020"
      },
      {
        "edge_id": "edge:fb66c67cfe98991b",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0009_bundle_distribution",
        "target": "cdl:021"
      },
      {
        "edge_id": "edge:7dd242fb2b562264",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0009_bundle_distribution",
        "target": "cdl:023_epoch_snapshot_contract"
      },
      {
        "edge_id": "edge:3d3cb9e441180092",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0009_bundle_distribution",
        "target": "cdl:024"
      },
      {
        "edge_id": "edge:7570da8f9234c11d",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0009_bundle_distribution",
        "target": "adr:0001_canonical_encoding_node_id_agent_interface"
      },
      {
        "edge_id": "edge:d426eef838a45cdd",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0009_bundle_distribution",
        "target": "adr:0002_ndjson_bundle_transport"
      },
      {
        "edge_id": "edge:591d6cbbce782cc9",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0009_bundle_distribution",
        "target": "adr:0004_genesis_truth_primitives"
      },
      {
        "edge_id": "edge:dc8f7c6a196f45be",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0009_bundle_distribution",
        "target": "adr:0007_constitutional_baseline_ratification_process"
      },
      {
        "edge_id": "edge:e49aced2901f44b6",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0009_bundle_distribution",
        "target": "adr:0008_node_usefulness_governance_weight_genesis_dilution"
      },
      {
        "edge_id": "edge:5917d2b99684c9f7",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0011_native_p2p_transport_baseline_agent_communication",
        "target": "cdl:024"
      },
      {
        "edge_id": "edge:813ab79a48f548d2",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0011_native_p2p_transport_baseline_agent_communication",
        "target": "adr:0025_transport_binding"
      },
      {
        "edge_id": "edge:c1430918a994d455",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0015_node_transfer_economics",
        "target": "cdl:034_node_schema_core_runtime"
      },
      {
        "edge_id": "edge:4358ea2d45e6166e",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0015_node_transfer_economics",
        "target": "cdl:035_validation_lifecycle"
      },
      {
        "edge_id": "edge:5846656991b8e09f",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0015_node_transfer_economics",
        "target": "cdl:v1_temporal_decay"
      },
      {
        "edge_id": "edge:159a588f149518f5",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0015_node_transfer_economics",
        "target": "cdl:v7_agent_decomposition"
      },
      {
        "edge_id": "edge:c77a116c246e4afc",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0015_node_transfer_economics",
        "target": "cdl:029_80_15_5_allocation_distribution"
      },
      {
        "edge_id": "edge:14f162d543b9776f",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0015_node_transfer_economics",
        "target": "cdl:013_governance_weight"
      },
      {
        "edge_id": "edge:3b8fbe47fabf960e",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0016",
        "target": "cdl:025_terminal_issuance_model"
      },
      {
        "edge_id": "edge:a5aa12daaf69d371",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0016",
        "target": "cdl:029_80_15_5_allocation_distribution"
      },
      {
        "edge_id": "edge:80f2a43016a0c28a",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0016",
        "target": "cdl:v3_quorum_diversity"
      },
      {
        "edge_id": "edge:fd772199726f0dd4",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0016",
        "target": "cdl:v7_agent_decomposition"
      },
      {
        "edge_id": "edge:35edd623d13f51ef",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0016",
        "target": "cdl:035_validation_lifecycle"
      },
      {
        "edge_id": "edge:202affbd969d3998",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0018_sequestered_financial_shard",
        "target": "cdl:051_epoch_state_quorum"
      },
      {
        "edge_id": "edge:99e99a5cc4e54da9",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0018_sequestered_financial_shard",
        "target": "cdl:050_treasury_ecu_governor_lane"
      },
      {
        "edge_id": "edge:a435af16bb72d554",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0019_graph_native_governance_compilation_boundary",
        "target": "adr:0007_constitutional_baseline_ratification_process"
      },
      {
        "edge_id": "edge:e302d9de80ccb2b0",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0019_graph_native_governance_compilation_boundary",
        "target": "adr:0009_bundle_distribution"
      },
      {
        "edge_id": "edge:b9922c6117157c14",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0019_graph_native_governance_compilation_boundary",
        "target": "adr:0011_native_p2p_transport_baseline_agent_communication"
      },
      {
        "edge_id": "edge:46fea8bb5eb9c1d4",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0020_knowledge_node_first_design_principle",
        "target": "cdl:v7_agent_decomposition"
      },
      {
        "edge_id": "edge:aa7a70843d73d5ff",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0020_knowledge_node_first_design_principle",
        "target": "adr:0019_graph_native_governance_compilation_boundary"
      },
      {
        "edge_id": "edge:0cbf5961615ab77d",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0020_knowledge_node_first_design_principle",
        "target": "cdl:001_signer_lineage_trust_root"
      },
      {
        "edge_id": "edge:d1be0e5ab9adbf0c",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0020_knowledge_node_first_design_principle",
        "target": "cdl:050_treasury_ecu_governor_lane"
      },
      {
        "edge_id": "edge:e87f2c5b69c7f6a5",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0020_knowledge_node_first_design_principle",
        "target": "adr:0021_epistemic_finality_claims"
      },
      {
        "edge_id": "edge:6a444c185ebc260a",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0022_local_first_private_publication_bound_economics",
        "target": "adr:0019_graph_native_governance_compilation_boundary"
      },
      {
        "edge_id": "edge:d84a31b1716cdbc4",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0022_local_first_private_publication_bound_economics",
        "target": "adr:0020_knowledge_node_first_design_principle"
      },
      {
        "edge_id": "edge:3e13bc975744ce23",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0023_multi_layer_quality_signal_architecture",
        "target": "cdl:v7_agent_decomposition"
      },
      {
        "edge_id": "edge:e1f6c1df2a89b72a",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0023_multi_layer_quality_signal_architecture",
        "target": "cdl:049_bounded_existential_alignment"
      },
      {
        "edge_id": "edge:e9da80c15c0c9967",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0023_multi_layer_quality_signal_architecture",
        "target": "cdl:036_node_dissemination_runtime"
      },
      {
        "edge_id": "edge:0a0c47fa4480bed6",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0023_multi_layer_quality_signal_architecture",
        "target": "cdl:v3_quorum_diversity"
      },
      {
        "edge_id": "edge:1b463aaa0b64503b",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0023_multi_layer_quality_signal_architecture",
        "target": "cdl:039_topology_shuffling_authorization"
      },
      {
        "edge_id": "edge:8216f3d12bcb419b",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0023_multi_layer_quality_signal_architecture",
        "target": "cdl:v4_minority_dissent_appeal_reopening_ratified_cdl_decisions"
      },
      {
        "edge_id": "edge:449c3fdc4a2c408a",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0023_multi_layer_quality_signal_architecture",
        "target": "cdl:053_werner_local_productive_credit_future_vehicle"
      },
      {
        "edge_id": "edge:b1a000fbdc8b524a",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0023_multi_layer_quality_signal_architecture",
        "target": "cdl:030_ecu_price_clamp_runtime"
      },
      {
        "edge_id": "edge:948801adf8bb4587",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0023_multi_layer_quality_signal_architecture",
        "target": "adr:0016"
      },
      {
        "edge_id": "edge:fe4c8a4931f37c61",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0023_multi_layer_quality_signal_architecture",
        "target": "cdl:060_gossip_centrality_extension"
      },
      {
        "edge_id": "edge:3a1826337c95e6c0",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0023_multi_layer_quality_signal_architecture",
        "target": "cdl:061_gossip_http_envelope"
      },
      {
        "edge_id": "edge:2736e1d3c98bd4bd",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0024_agent_skills_infrastructure",
        "target": "cdl:034_node_schema_core_runtime"
      },
      {
        "edge_id": "edge:9b071058db3135c0",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0024_agent_skills_infrastructure",
        "target": "cdl:052_epistemic_evaluation_contract"
      },
      {
        "edge_id": "edge:e106a8cbd77c65cd",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0024_agent_skills_infrastructure",
        "target": "cdl:v7_agent_decomposition"
      },
      {
        "edge_id": "edge:9a4e40eedb2ed5cf",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0024_agent_skills_infrastructure",
        "target": "cdl:053_werner_local_productive_credit_future_vehicle"
      },
      {
        "edge_id": "edge:48ff53f16107bb7a",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0025_transport_binding",
        "target": "adr:0011_native_p2p_transport_baseline_agent_communication"
      },
      {
        "edge_id": "edge:cd7a5983e0cbb4fa",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0025_transport_binding",
        "target": "cdl:024"
      },
      {
        "edge_id": "edge:766058a2870c12db",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0025_transport_binding",
        "target": "cdl:039_topology_shuffling_authorization"
      },
      {
        "edge_id": "edge:0450dc997a73def8",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0025_transport_binding",
        "target": "cdl:060_gossip_centrality_extension"
      },
      {
        "edge_id": "edge:63fe938f7bd1c731",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0025_transport_binding",
        "target": "cdl:036_node_dissemination_runtime"
      },
      {
        "edge_id": "edge:f9dedfc8d9252a4d",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0025_transport_binding",
        "target": "cdl:061_gossip_http_envelope"
      },
      {
        "edge_id": "edge:b5248c6255c4a0f8",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0025_transport_binding",
        "target": "cdl:047_treasury_governance"
      },
      {
        "edge_id": "edge:bb5a8d9ef650ab20",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0026_protocol_vs_harness_product_boundary",
        "target": "adr:0022_local_first_private_publication_bound_economics"
      },
      {
        "edge_id": "edge:18945707129ed8a5",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0027_canonical_bootstrap_receipt_boundary",
        "target": "adr:0026_protocol_vs_harness_product_boundary"
      },
      {
        "edge_id": "edge:3bffa9452e840c93",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0028_settlement_substrate_graduation_governance_route",
        "target": "cdl:062_sovereign_substrate_research_lane"
      },
      {
        "edge_id": "edge:49252cf5de8a19a2",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0029_hypergraph_substrate",
        "target": "cdl:v1_temporal_decay"
      },
      {
        "edge_id": "edge:8bb1669b043c4ebe",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0029_hypergraph_substrate",
        "target": "cdl:v3_quorum_diversity"
      },
      {
        "edge_id": "edge:ce7cb80e3cedd287",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0029_hypergraph_substrate",
        "target": "adr:0030_node_embedding_substrate"
      },
      {
        "edge_id": "edge:60e0d33368d41295",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0029_hypergraph_substrate",
        "target": "adr:0031_subgraph_homomorphism_query_contract"
      },
      {
        "edge_id": "edge:67ff74a359930696",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0030_node_embedding_substrate",
        "target": "adr:0029_hypergraph_substrate"
      },
      {
        "edge_id": "edge:5b1f488c55f890c5",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0030_node_embedding_substrate",
        "target": "cdl:097_type_definition_node_authority"
      },
      {
        "edge_id": "edge:532bfe2c8decf8bc",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0030_node_embedding_substrate",
        "target": "adr:0031_subgraph_homomorphism_query_contract"
      },
      {
        "edge_id": "edge:27b33c40b5fa916b",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0031_subgraph_homomorphism_query_contract",
        "target": "adr:0029_hypergraph_substrate"
      },
      {
        "edge_id": "edge:4efaa0c5363ad400",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0031_subgraph_homomorphism_query_contract",
        "target": "adr:0030_node_embedding_substrate"
      },
      {
        "edge_id": "edge:d55df829ce407821",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0032_temporal_hypergraph",
        "target": "adr:0029_hypergraph_substrate"
      },
      {
        "edge_id": "edge:98f9e6acfe4f65a7",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0032_temporal_hypergraph",
        "target": "adr:0030_node_embedding_substrate"
      },
      {
        "edge_id": "edge:fb85121656bf9504",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0032_temporal_hypergraph",
        "target": "adr:0031_subgraph_homomorphism_query_contract"
      },
      {
        "edge_id": "edge:bbaf5dd5b31fc8c8",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0033_star_map_homoiconic_entity",
        "target": "adr:0003_star_map_ngram_route_index"
      },
      {
        "edge_id": "edge:4231946a057cc67c",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0033_star_map_homoiconic_entity",
        "target": "adr:0005_star_map_observational_feeds"
      },
      {
        "edge_id": "edge:7f8adcf797c8dee4",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0033_star_map_homoiconic_entity",
        "target": "adr:0029_hypergraph_substrate"
      },
      {
        "edge_id": "edge:b7312e1bd59813a4",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0033_star_map_homoiconic_entity",
        "target": "adr:0030_node_embedding_substrate"
      },
      {
        "edge_id": "edge:f2b900b67d6e3f73",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0034_d2d_sealed_sender",
        "target": "cdl:060_gossip_centrality_extension"
      },
      {
        "edge_id": "edge:cdd2c84ce4d73ea6",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0034_d2d_sealed_sender",
        "target": "cdl:061_gossip_http_envelope"
      },
      {
        "edge_id": "edge:eea2c1220bd5ff4f",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0035_homoiconic_type_definition_system",
        "target": "cdl:097_type_definition_node_authority"
      },
      {
        "edge_id": "edge:e0636ce9edfc5aa3",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0035_homoiconic_type_definition_system",
        "target": "adr:0030_node_embedding_substrate"
      },
      {
        "edge_id": "edge:3f61131186e09f75",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0035_homoiconic_type_definition_system",
        "target": "adr:0004_genesis_truth_primitives"
      },
      {
        "edge_id": "edge:35dfdcd92c4c5421",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0035_homoiconic_type_definition_system",
        "target": "adr:0019_graph_native_governance_compilation_boundary"
      },
      {
        "edge_id": "edge:c741ca789e28ec6e",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0035_homoiconic_type_definition_system",
        "target": "adr:0021_epistemic_finality_claims"
      },
      {
        "edge_id": "edge:ebe83c4d0ae123aa",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0035_homoiconic_type_definition_system",
        "target": "adr:0029_hypergraph_substrate"
      },
      {
        "edge_id": "edge:cec016db2e413a98",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0035_homoiconic_type_definition_system",
        "target": "adr:0033_star_map_homoiconic_entity"
      },
      {
        "edge_id": "edge:a6be5b3e365fcb73",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0037_genesis_canonical_lineage_contract",
        "target": "cdl:085_werner_phi_bound"
      },
      {
        "edge_id": "edge:86ddeffd30a65d67",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0037_genesis_canonical_lineage_contract",
        "target": "adr:0036_operational_release_key_genesis_binding"
      },
      {
        "edge_id": "edge:8f13bec7a12082a2",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0037_genesis_canonical_lineage_contract",
        "target": "cdl:v7_agent_decomposition"
      },
      {
        "edge_id": "edge:19f767719e8f8862",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0038_agent_birth_attestation",
        "target": "cdl:042_agent_id_flat_namespace"
      },
      {
        "edge_id": "edge:ec24f68407be0e99",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0038_agent_birth_attestation",
        "target": "cdl:069_pq_identity_epoch_endorsement"
      },
      {
        "edge_id": "edge:05ebfab1181f0c90",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0038_agent_birth_attestation",
        "target": "adr:0037_genesis_canonical_lineage_contract"
      },
      {
        "edge_id": "edge:a0b825d6f226f5ea",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0038_agent_birth_attestation",
        "target": "cdl:090_identity_bootstrap"
      },
      {
        "edge_id": "edge:389948f84b74b854",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0039_validator_endpoint_registry",
        "target": "cdl:017_validator_admission_ejection"
      },
      {
        "edge_id": "edge:7788244636f7b689",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0039_validator_endpoint_registry",
        "target": "cdl:068_topology_shuffle_vrf_runtime"
      },
      {
        "edge_id": "edge:1bc9a58f52a8b797",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0039_validator_endpoint_registry",
        "target": "cdl:078_relay_incentive_constitutional_lock"
      },
      {
        "edge_id": "edge:35948acb86c4c9fe",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0039_validator_endpoint_registry",
        "target": "cdl:090_identity_bootstrap"
      },
      {
        "edge_id": "edge:d766f09c9da7cf33",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0039_validator_endpoint_registry",
        "target": "adr:0038_agent_birth_attestation"
      },
      {
        "edge_id": "edge:af1dcf2c04a36523",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0039_validator_endpoint_registry",
        "target": "cdl:088_public_claimability"
      },
      {
        "edge_id": "edge:91fd0b77195ee092",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0040_jury_eligibility_assignment",
        "target": "cdl:052_epistemic_evaluation_contract"
      },
      {
        "edge_id": "edge:9f963e13dae0451f",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0040_jury_eligibility_assignment",
        "target": "cdl:059_quality_signal_architecture"
      },
      {
        "edge_id": "edge:f377e9fc0ff9b752",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0040_jury_eligibility_assignment",
        "target": "cdl:068_topology_shuffle_vrf_runtime"
      },
      {
        "edge_id": "edge:4a17a4204803f817",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0040_jury_eligibility_assignment",
        "target": "cdl:090_identity_bootstrap"
      },
      {
        "edge_id": "edge:7ba90a6e1f0b07f2",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0040_jury_eligibility_assignment",
        "target": "cdl:v3_quorum_diversity"
      },
      {
        "edge_id": "edge:511449277fb5541d",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0040_jury_eligibility_assignment",
        "target": "cdl:v7_agent_decomposition"
      },
      {
        "edge_id": "edge:1d5991a75a2eb274",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0040_jury_eligibility_assignment",
        "target": "adr:0038_agent_birth_attestation"
      },
      {
        "edge_id": "edge:d53241714bed8c4d",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0041_agent_init_and_ingestion_protocol",
        "target": "cdl:042_agent_id_flat_namespace"
      },
      {
        "edge_id": "edge:81f57973cb4a3045",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0041_agent_init_and_ingestion_protocol",
        "target": "cdl:069_pq_identity_epoch_endorsement"
      },
      {
        "edge_id": "edge:75a8c1d86a300eba",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0041_agent_init_and_ingestion_protocol",
        "target": "cdl:078_relay_incentive_constitutional_lock"
      },
      {
        "edge_id": "edge:b96041497ef3c440",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0041_agent_init_and_ingestion_protocol",
        "target": "adr:0035_homoiconic_type_definition_system"
      },
      {
        "edge_id": "edge:b7579c7474d7b0dd",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0041_agent_init_and_ingestion_protocol",
        "target": "adr:0040_jury_eligibility_assignment"
      },
      {
        "edge_id": "edge:3ba41dfa913f29ae",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0041_agent_init_and_ingestion_protocol",
        "target": "adr:0038_agent_birth_attestation"
      },
      {
        "edge_id": "edge:7fc5195c4efa876c",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0042_vrf_proof_verifier",
        "target": "cdl:068_topology_shuffle_vrf_runtime"
      },
      {
        "edge_id": "edge:7e73e5a8fcd6813b",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0042_vrf_proof_verifier",
        "target": "adr:0040_jury_eligibility_assignment"
      },
      {
        "edge_id": "edge:9403a2fdab67d001",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0042_vrf_proof_verifier",
        "target": "adr:0038_agent_birth_attestation"
      },
      {
        "edge_id": "edge:034021c9a6345974",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0042_vrf_proof_verifier",
        "target": "adr:0041_agent_init_and_ingestion_protocol"
      },
      {
        "edge_id": "edge:607ff8cad8284355",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0042_vrf_proof_verifier",
        "target": "cdl:090_identity_bootstrap"
      },
      {
        "edge_id": "edge:d344901fbd89f003",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0043_review_lane_t0_5_to_t1_promotion",
        "target": "cdl:091_jury_incentive"
      },
      {
        "edge_id": "edge:816c5d4ae9437775",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0043_review_lane_t0_5_to_t1_promotion",
        "target": "adr:0041_agent_init_and_ingestion_protocol"
      },
      {
        "edge_id": "edge:9aede2816e063416",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0043_review_lane_t0_5_to_t1_promotion",
        "target": "adr:0040_jury_eligibility_assignment"
      },
      {
        "edge_id": "edge:5a060daad46ef03b",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0043_review_lane_t0_5_to_t1_promotion",
        "target": "adr:0042_vrf_proof_verifier"
      },
      {
        "edge_id": "edge:4e9a85a8050c6a76",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0044_anti_capture_diversity_verification",
        "target": "cdl:v3_quorum_diversity"
      },
      {
        "edge_id": "edge:4279178f4faf16fe",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0044_anti_capture_diversity_verification",
        "target": "adr:0040_jury_eligibility_assignment"
      },
      {
        "edge_id": "edge:847097aaab0fe193",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0044_anti_capture_diversity_verification",
        "target": "adr:0042_vrf_proof_verifier"
      },
      {
        "edge_id": "edge:e90b8aa169be48eb",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0044_anti_capture_diversity_verification",
        "target": "adr:0043_review_lane_t0_5_to_t1_promotion"
      },
      {
        "edge_id": "edge:0294854359b8f438",
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "adr:0044_anti_capture_diversity_verification",
        "target": "cdl:068_topology_shuffle_vrf_runtime"
      },
      {
        "edge_id": "edge:2ee2b111cbcc7ecc",
        "edge_type": "DERIVED_FROM",
        "source": "cdl:069_pq_identity_epoch_endorsement",
        "target": "cdl:042_agent_id_flat_namespace"
      },
      {
        "edge_id": "edge:980f2e9982c5f880",
        "edge_type": "PRELOCK_FOR",
        "source": "cdl:085_prelock_historical_opening_and_prelock_state",
        "target": "cdl:085_werner_phi_bound"
      }
    ],
    "accepted_node_count": 0,
    "accepted_nodes": [],
    "dry_run": false,
    "metadata": {},
    "mutated": true,
    "phase": "1545p-Fix70",
    "post_invariants": {
      "no_dangling_edges": true,
      "payload_edge_count_matches_rows": true,
      "payload_node_count_matches_rows": true,
      "source_path_index_matches_rows": true,
      "tier_group_index_matches_rows": true,
      "tier_index_matches_rows": true
    },
    "post_lmdb_counts": {
      "edges": 89581,
      "nodes": 16821,
      "payload_edges": 89581,
      "payload_nodes": 16821
    },
    "pre_counts": {
      "edges": 89447,
      "nodes": 16821
    },
    "projected_counts": {
      "edges": 89581,
      "nodes": 16821
    },
    "projected_dangling_edge_count": 0,
    "projected_dangling_edges": [],
    "rejected_edge_count": 0,
    "rejected_edges": [],
    "skipped_edge_count": 0,
    "skipped_edges": [],
    "skipped_node_count": 0,
    "skipped_nodes": [],
    "status": "PASS",
    "version": "genesis_atlas_lmdb_writer_1545p_fix59b.v0.1"
  }
}
```
