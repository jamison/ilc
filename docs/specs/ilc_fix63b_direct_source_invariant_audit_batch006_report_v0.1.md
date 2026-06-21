# Fix63b Direct Source Invariant Audit Batch 006 Report v0.1

Status: applied to unified LMDB
Phase: 1545p-Fix63b-batch006
Ledger: `docs/specs/ilc_fix63b_direct_source_invariant_audit_batch006_v0.1.json`

## Scope

This batch directly read source material for weak-evidence Fix63 invariant rows
51-60:

- `invariant:genesis_compile_coverage_partial_with_structural_gaps_authority_traceability_31_32_recipes_complete`
- `invariant:genesis_epistemic_work_task_json_alias_and_task_queue_bridge`
- `invariant:genesis_graph_zero_keystone_nodes_hub_spoke_resilience`
- `invariant:genesis_node_candidate_crawl_review_queue_rejection_and_promotion_trace_contract`
- `invariant:genesis_node_candidate_crawl_star_map_and_review_ledger_consistency`
- `invariant:genesis_optimization_harness_rejects_activation_claims_invalid_edges_missing_recipes`
- `invariant:genesis_readiness_audit_reverification_gate_cli_contract`
- `invariant:genesis_readiness_remediation_closure_gate_cli_contract`
- `invariant:genesis_root_envelope_binds_m1_m2_m3_manifest_hashes`
- `invariant:genesis_signing_private_key_never_committed_or_agent_handled`

## Direct Reads

The batch read concrete tests, runtime modules, shell gates, specs, reports,
walkthroughs, and tool implementations. Source line references are recorded per
invariant in the JSON ledger.

Primary files read:

- `docs/sims/sim_spectral_02/genesis_compile_coverage_diagnostic_v0.1.md`
- `tools/genesis_compile_coverage_diagnostic.py`
- `tests/test_genesis_compile_coverage_diagnostic.py`
- `tests/test_genesis_work_task_model.py`
- `ilc_core/genesis/work_task.py`
- `ilc_core/work/task_queue.py`
- `epistemic_work_task_schema_v1.json`
- `tests/test_phase_1387g_epistemic_leverage.py`
- `docs/phases/phase_1387i_graphopt_synthesis_walkthrough.md`
- `docs/sims/sim_spectral_02/genesis_graphopt_01_synthesis_report_v0.1.md`
- `tests/test_genesis_node_candidate_crawl.py`
- `tools/crawl_genesis_node_candidates.py`
- `docs/sims/sim_spectral_02/genesis_node_candidate_inventory_v0.1.md`
- `docs/sims/sim_spectral_02/genesis_node_candidate_decision_log_v0.1.md`
- `tests/test_phase_1545p_fix9_genesis_optimization_harness.py`
- `tools/evaluators/genesis_optimization_harness.py`
- `docs/specs/ilc_genesis_optimization_autoresearch_harness_1545p_fix9_v0.1.md`
- `docs/phases/phase_1545p_fix9_genesis_optimization_autoresearch_harness_walkthrough.md`
- `tests/test_genesis_readiness_audit_reverification_gate_phase_1012.py`
- `tools/check_genesis_readiness_audit_reverification_1012.sh`
- `docs/specs/ilc_genesis_readiness_audit_reverification_post_1011_v0.1.md`
- `docs/phases/phase_1012_g8_constitution_cluster_a_genesis_readiness_audit_reverification_gate_and_closure_report_walkthrough.md`
- `tests/test_genesis_readiness_remediation_closure_gate_phase_1009.py`
- `tools/check_genesis_readiness_remediation_closure_996_1008.sh`
- `docs/specs/ilc_genesis_readiness_remediation_996_1008_handoff_v0.1.md`
- `docs/specs/ilc_genesis_readiness_audit_reconciliation_v0.1.md`
- `tools/build_genesis_signing_root_envelope.py`
- `tests/test_phase_1142s_genesis_signing_ceremony.py`
- `ilc_core/rc/signing_ceremony_status.py`
- `docs/phases/phase_1142s_genesis_node_attestation_signing_ceremony_walkthrough.md`

## Findings

All ten entries are support-trace invariants with existing role-specific
authority references, classification edges, or gate/report scope. None require a
new `GOVERNS` edge.

The batch recommends 34 `EVIDENCES` edges from invariant nodes to actual source
files read. These edges replace weak proxy evidence with source-level
traceability.

## LMDB Application

Applied the recommended edges through `AtlasLmdbSafeWriter` against:

```text
out/genesis_base_graph_v0.4_unified.lmdb
```

Safe-writer summary:

- recommended evidence edges: `34`
- accepted evidence edges: `34`
- rejected evidence edges: `0`
- skipped evidence edges: `0`
- phase-file registration accepted nodes: `3`
- phase-file registration accepted edges: `6`
- final LMDB nodes: `16,365`
- final LMDB edges: `86,385`
- dangling edges: `0`
- edge-id debt: `0`

The batch ledger and report were registered as support-only phase files in the
same LMDB and carry forward to
`phase:1545p_fix63b_direct_source_invariant_audit`.

## Non-Claims

This batch does not mutate signed Genesis artifacts, does not create authority
nodes, does not promote support invariants into genesis-core authority, does not
activate public RC, and does not authorize production economics, public serving,
or settlement.
