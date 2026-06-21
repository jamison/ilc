# Fix63b Direct Source Invariant Audit Batch 007 Report v0.1

Status: applied to unified LMDB
Phase: 1545p-Fix63b-batch007
Ledger: `docs/specs/ilc_fix63b_direct_source_invariant_audit_batch007_v0.1.json`

## Scope

This batch directly read source material for weak-evidence Fix63 invariant rows
61-70:

- `invariant:genesis_star_map_authority_trace_depth_max_2_hub_spoke`
- `invariant:genesis_star_map_edge_recipe_completeness_77_of_77`
- `invariant:genesis_star_map_gap_analysis_review_categories_and_hypergraph_shape`
- `invariant:gossip_receive_accepts_canonical_node_ids_and_rejects_legacy_or_mismatched_ids`
- `invariant:governance_weight_decay_genesis_baseline_vote_share_precision_and_input_guards`
- `invariant:graph_edge_iterators_and_public_edges_surface_removed`
- `invariant:hardware_archetype_strategy_applies_to_agent_mining`
- `invariant:hash_id_canonical_fingerprint_alias_migration_contract`
- `invariant:idea_descent_genesis_candidate_refutation_and_trace_integrity`
- `invariant:idea_descent_genesis_candidate_refutation_trace_contract`

## Direct Reads

The batch read concrete tests, runtime modules, evaluator code, objective specs,
walkthroughs, and SIM reports. Source line references are recorded per
invariant in the JSON ledger.

Primary files read:

- `tests/test_phase_1387f_graph_structure_analysis.py`
- `tests/test_phase_1387g_epistemic_leverage.py`
- `tests/test_phase_1387h_edge_recipe_canonicalization.py`
- `docs/phases/phase_1387h_edge_recipe_canonicalization_walkthrough.md`
- `docs/phases/phase_1387i_graphopt_synthesis_walkthrough.md`
- `docs/sims/sim_spectral_02/genesis_graphopt_01_synthesis_report_v0.1.md`
- `docs/sims/sim_spectral_02/genesis_core_star_map_gap_analysis_v0.1.md`
- `ilc_core/server.py`
- `tests/test_node_id_runtime_bridge_phase_1003.py`
- `docs/phases/phase_1013_g8_constitution_cluster_a_nodeid_strict_canonical_cutover_runtime_and_contracts_walkthrough.md`
- `ilc_core/analysis/governance_weight.py`
- `tests/test_governance_weight_phase_207.py`
- `ilc_core/protocol/governance_weighted_decision.py`
- `docs/phases/phase_1357_reputation_py_h11_float_kill_walkthrough.md`
- `ilc_core/graph/__init__.py`
- `tests/test_graph_edges.py`
- `docs/phases/phase_0977_g8_constitution_cluster_a_track1_full_edge_removal_direct_append_compatibility_sunset_and_public_edge_list_surface_removal_slice4_walkthrough.md`
- `ilc_core/hardware.py`
- `ilc_core/agent.py`
- `tests/test_hardware_archetypes.py`
- `tests/test_agent_auto_strategy.py`
- `ilc_core/types.py`
- `ilc_core/encoding/cidv1.py`
- `tests/test_node_id_dual_contract_phase_1002.py`
- `tests/test_node_id_migration_utility_phase_1004.py`
- `tools/idea_descent_runner.py`
- `tests/test_idea_descent_genesis_star_map_loop.py`
- `tools/evaluators/genesis_star_map_evaluator.py`
- `docs/specs/ilc_idea_descent_genesis_star_map_objective_v0.1.md`
- `docs/phases/phase_1545p_fix3_idea_descent_genesis_rework_walkthrough.md`
- `docs/specs/ilc_genesis_star_map_candidate_methodology_preservation_1545p_fix6_v0.1.md`
- `tests/test_phase_1545p_fix6_genesis_v03_methodology_preservation.py`

## Findings

All ten entries are support-trace invariants with direct source evidence. None
require a new `GOVERNS` edge in this batch. Runtime-backed rows such as strict
canonical gossip, governance weight, graph edge iterator removal, hardware
archetype strategy, and canonical NodeID migration are evidenced by their
runtime modules and focused tests. SIM/evaluator rows remain support-only
because the read sources explicitly describe diagnostic or local-only support
surfaces.

The batch recommends 37 `EVIDENCES` edges from invariant nodes to actual source
files read. These edges replace weak proxy evidence with source-level
traceability.

## LMDB Application

Applied the recommended edges through `AtlasLmdbSafeWriter` against:

```text
out/genesis_base_graph_v0.4_unified.lmdb
```

Safe-writer summary:

- recommended evidence edges: `37`
- accepted evidence edges: `36`
- skipped duplicate evidence edges: `1`
- rejected evidence edges: `0`
- phase-file registration accepted nodes: `3`
- phase-file registration accepted edges: `6`
- final LMDB nodes: `16,368`
- final LMDB edges: `86,427`
- dangling edges: `0`
- edge-id debt: `0`

The skipped edge was an already-present semantic duplicate for
`invariant:idea_descent_genesis_candidate_refutation_and_trace_integrity`
evidencing `tests/test_idea_descent_genesis_star_map_loop.py`.

The batch ledger and report were registered as support-only phase files in the
same LMDB and carry forward to
`phase:1545p_fix63b_direct_source_invariant_audit`.

## Non-Claims

This batch does not mutate signed Genesis artifacts, does not create authority
nodes, does not promote support invariants into genesis-core authority, does not
activate public RC, and does not authorize production economics, public serving,
or settlement.
