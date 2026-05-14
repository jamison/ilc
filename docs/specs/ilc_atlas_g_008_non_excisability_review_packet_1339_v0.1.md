# ATLAS-G-008 Non-Excisability Review Packet Phase 1339 v0.1

Status: `atlas_g_008_non_excisability_packet_classified_phase_1339`

Input candidate: `out/genesis_core_star_map_v0.2_candidate.json`

Diagnostic: `out/genesis_compile_coverage_diagnostic_v0.2_candidate.json`

## Review Verdict

Every Genesis core node in the regenerated v0.2 candidate is traceable,
non-redundant, and non-excisable for the unsigned v0.2 signing boundary.

The diagnostic confirms all `49` core nodes are authority-traceable from the
Genesis authority root. The remaining `32` basis-unreachable nodes are not
untraceable artifacts; they are structural reachability gaps in the current
low-level transition-basis compiler model. They are explicitly deferred as
compiler-coverage debt and do not block candidate signing after Phase 1339.

## Non-Excisability Classes

| Class | Nodes | Reason non-excisable |
|---|---:|---|
| Truth primitives and axioms | 10 | Required low-level Genesis basis and transition basis |
| Genesis authority identity, key, ceremony, and assertion artifacts | 5 | Required signing and authority lineage |
| Bootstrap and state artifacts | 4 | Required install/load and bootstrap lineage |
| ADR authority artifacts | 15 | Required accepted ADR governance spine and morphogenic substrate lineage |
| CDL artifacts | 8 | Required ratified constitutional policy and economic settlement lineage |
| Policy constants and rules | 7 | Required economic, authority-sunset, and attribution policy locks |

## Added or Reclassified Before Signing

| Candidate ID | Status | Evidence |
|---|---|---|
| `adr:0037_genesis_canonical_lineage_contract` | Added, pending v0.2 signing | `docs/adr/ADR_0037_Genesis_Canonical_Lineage_Contract.md` |
| `cdl:v1_temporal_decay` | Added, pending v0.2 signing | `docs/specs/ilc_cdl_v1_temporal_decay_ratification_evidence_330_v0.1.md` |
| `cdl:v2_sybil_resistance` | Added, pending v0.2 signing | `docs/specs/ilc_cdl_v2_sybil_resistance_ratification_evidence_331_v0.1.md` |
| `cdl:v3_quorum_diversity` | Added, pending v0.2 signing | `docs/specs/ilc_cdl_v3_quorum_diversity_ratification_evidence_332_v0.1.md` |
| `cdl:v7_agent_decomposition` | Added, pending v0.2 signing | `docs/specs/ilc_cdl_v7_agent_decomposition_criteria_ratification_evidence_335_v0.1.md` |
| `cdl:085_werner_phi_bound` | Added, pending v0.2 signing | `docs/specs/ilc_cdl_085_ratification_evidence_1185_v0.1.md` |
| `policy:reuse_attribution_rate_0_20` | Added, pending v0.2 signing | `ilc_core/types.py` |
| `policy:edge_mint_phi_bound_0_60` | Added, pending v0.2 signing | `ilc_core/types.py` |

## Basis-Unreachable Nodes Explicitly Deferred

These nodes remain basis-unreachable in the diagnostic, but each is
authority-traceable and non-excisable. The deferral is limited to compiler
reachability expressiveness, not node legitimacy.

| Candidate ID | Disposition |
|---|---|
| `adr:0008_node_usefulness_governance_weight_genesis_dilution` | `explicitly-defer-with-authority` |
| `adr:0012_ecu_ilc_graph_coupling_anti_reflexivity` | `explicitly-defer-with-authority` |
| `adr:0019_graph_native_governance_compilation_boundary` | `explicitly-defer-with-authority` |
| `adr:0020_knowledge_node_first_design_principle` | `explicitly-defer-with-authority` |
| `adr:0022_local_first_private_publication_bound_economics` | `explicitly-defer-with-authority` |
| `adr:0023_multi_layer_quality_signal_architecture` | `explicitly-defer-with-authority` |
| `adr:0026_protocol_vs_harness_product_boundary` | `explicitly-defer-with-authority` |
| `adr:0028_settlement_substrate_graduation_governance_route` | `explicitly-defer-with-authority` |
| `adr:0029_hypergraph_substrate` | `explicitly-defer-with-authority` |
| `adr:0030_node_embedding_substrate` | `explicitly-defer-with-authority` |
| `adr:0031_subgraph_homomorphism_query_contract` | `explicitly-defer-with-authority` |
| `adr:0032_temporal_hypergraph` | `explicitly-defer-with-authority` |
| `adr:0035_homoiconic_type_definition_system` | `explicitly-defer-with-authority` |
| `adr:0037_genesis_canonical_lineage_contract` | `explicitly-defer-with-authority` |
| `artifact:genesis_agent1_pubkey_record_838a` | `explicitly-defer-with-authority` |
| `artifact:genesis_intent_attestation_init_authority_map` | `explicitly-defer-with-authority` |
| `cdl:081_hyperedge_ecu_attribution` | `explicitly-defer-with-authority` |
| `cdl:083_panel_quorum_refutation` | `explicitly-defer-with-authority` |
| `cdl:084_provenance_chain_attribution` | `explicitly-defer-with-authority` |
| `cdl:085_werner_phi_bound` | `explicitly-defer-with-authority` |
| `cdl:v1_temporal_decay` | `explicitly-defer-with-authority` |
| `cdl:v2_sybil_resistance` | `explicitly-defer-with-authority` |
| `cdl:v3_quorum_diversity` | `explicitly-defer-with-authority` |
| `cdl:v7_agent_decomposition` | `explicitly-defer-with-authority` |
| `ceremony:genesis_agent1_keygen_838a` | `explicitly-defer-with-authority` |
| `policy:edge_mint_phi_bound_0_60` | `explicitly-defer-with-authority` |
| `policy:genesis_accrual_governor` | `explicitly-defer-with-authority` |
| `policy:genesis_authority_sunset` | `explicitly-defer-with-authority` |
| `policy:genesis_theta_hard_0_05` | `explicitly-defer-with-authority` |
| `policy:genesis_theta_soft_exp_minus_3` | `explicitly-defer-with-authority` |
| `policy:provenance_decay_alpha_0_45` | `explicitly-defer-with-authority` |
| `policy:reuse_attribution_rate_0_20` | `explicitly-defer-with-authority` |

## Non-Claims

This review packet is unsigned evidence only. It does not sign Genesis v0.2,
mutate CDL state, publish a public RC, activate claimability, or activate any
wallet, ECU, ILC, or value path.
