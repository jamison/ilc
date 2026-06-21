# Fix63b Direct Source Invariant Audit Batch 004 Report v0.1

Status: applied to unified LMDB
Phase: 1545p-Fix63b-batch004
Ledger: `docs/specs/ilc_fix63b_direct_source_invariant_audit_batch004_v0.1.json`

## Scope

This batch directly read source material for weak-evidence Fix63 invariant rows
31-40:

- `invariant:curated_seed_authority_source_generated_out_artifacts_reproducible`
- `invariant:data_center_ballast_ilc_utilization_not_worse_than_baseline`
- `invariant:domain_exception_hierarchy_and_backward_compatible_imports_stable`
- `invariant:ecu_aware_decimal_staking_strategy`
- `invariant:edge_path_lineage_only_link_path_semantic_relations`
- `invariant:edge_recipe_canonicalization_scope_distinguishes_attestation_provenance`
- `invariant:freshness_gate_genesis_exemption_monotonic_floor_fail_closed_and_diversity_interaction`
- `invariant:gap14_adapter_extraction_structural_store_interfaces_primitive_registry_and_lmdb_adapter`
- `invariant:genesis_32_node_composability_audit_projection_class_and_authority_source_contract`
- `invariant:genesis_accrual_governor_phase_218_gate_cli_contract`

## Direct Reads

The batch read the concrete tests, runtime modules, phase walkthroughs, and
support specs for the ten invariants. Source line references are recorded per
invariant in the JSON ledger.

Primary files read:

- `tests/test_phase_1136a_genesis_morphogenic_hypergraph_atlas.py`
- `docs/phases/phase_1136a_genesis_morphogenic_hypergraph_atlas_walkthrough.md`
- `tests/test_phase_1149_atlas_tier2_patch.py`
- `docs/phases/phase_1149_atlas_tier2_curated_seed_patch_walkthrough.md`
- `tests/test_data_center_ballast.py`
- `tests/test_data_center_controller.py`
- `simulations/data_center_ballast.py`
- `ilc_core/exceptions.py`
- `tests/test_domain_exception_hierarchy_guardrail.py`
- `docs/phases/phase_0989_g8_constitution_cluster_a_domain_exception_hierarchy_foundation_walkthrough.md`
- `tests/test_agent_strategy.py`
- `tests/test_agent_auto_strategy.py`
- `ilc_core/agent.py`
- `tests/test_edge_link_boundary_phase_1007.py`
- `docs/phases/phase_0065f_walkthrough.md`
- `tests/test_phase_1387h_edge_recipe_canonicalization.py`
- `docs/phases/phase_1387h_edge_recipe_canonicalization_walkthrough.md`
- `tests/test_freshness_gate_phase_217.py`
- `ilc_core/analysis/freshness_gate.py`
- `tests/test_phase_598_freshness_gate_provenance_and_genesis_exemption_closure.py`
- `docs/specs/ilc_freshness_gate_provenance_and_genesis_exemption_closure_598_v0.1.md`
- `tests/test_phase_1250_gap14_adapter_extraction.py`
- `docs/phases/phase_1250_gap14_adapter_extraction_walkthrough.md`
- `ilc_core/storage/truth_primitive_graph_lmdb_adapter.py`
- `ilc_core/epistemic/truth_primitive_graph_store.py`
- `ilc_core/protocol/primitive_type_registry.py`
- `ilc_core/protocol/harness_interfaces.py`
- `tests/test_phase_1151_composability_audit.py`
- `tests/test_phase_1160_claim_composition_projection_build.py`
- `tools/build_genesis_claim_composition_projection.py`
- `docs/specs/ilc_genesis_claim_composition_projection_plan_1146_v0.1.md`
- `docs/phases/phase_1160_claim_composition_projection_build_walkthrough.md`
- `tests/test_genesis_accrual_governor_phase_218.py`
- `tests/test_genesis_accrual_governor_gate_phase_218.py`
- `ilc_core/analysis/genesis_accrual_governor.py`
- `docs/specs/ilc_genesis_accrual_governor_contract_v0.1.md`
- `docs/phases/phase_0218_g8_constitution_cluster_a_ra12_genesis_accrual_governor_simulation_and_cap_trajectory_checks_walkthrough.md`

## Findings

All ten entries are support-trace invariants with existing role-specific
authority references or classification edges. None require a new `GOVERNS`
edge.

The batch recommends 37 `EVIDENCES` edges from invariant nodes to the actual
source files read. These edges replace the prior weak `STATUS.md` proxy
evidence with source-level traceability.

## LMDB Plan

Applied the recommended edges through `AtlasLmdbSafeWriter` against:

```text
out/genesis_base_graph_v0.4_unified.lmdb
```

Safe-writer summary:

- recommended evidence edges: `37`
- accepted evidence edges: `37`
- rejected evidence edges: `0`
- skipped evidence edges: `0`
- final LMDB nodes: `16,358`
- final LMDB edges: `86,303`
- dangling edges: `0`
- edge-id debt: `0`

This report and the batch ledger were registered as support-only phase files in
the same LMDB.

## Non-Claims

This batch does not mutate signed Genesis artifacts, does not create authority
nodes, does not promote support invariants into genesis-core authority, does not
activate public RC, and does not authorize production economics, public serving,
or settlement.
