# Fix63b Direct Source Invariant Audit Batch 005 Report v0.1

Status: applied to unified LMDB
Phase: 1545p-Fix63b-batch005
Ledger: `docs/specs/ilc_fix63b_direct_source_invariant_audit_batch005_v0.1.json`

## Scope

This batch directly read source material for weak-evidence Fix63 invariant rows
41-50:

- `invariant:genesis_accrual_theta_constants_hard_cap_taper_and_fail_closed_inputs`
- `invariant:genesis_attestation_ex_post_facto_no_history_rewrite_no_runtime_effect`
- `invariant:genesis_attestation_node_star_map_overrides_authority_traceability_and_crawler_safeguards`
- `invariant:genesis_authority_traceability_separate_from_derivation_reachability`
- `invariant:genesis_compile_checkpoint1_signed_star_map_authority_traceability_and_reachability_boundary`
- `invariant:genesis_compile_checkpoint_1_authority_traceability_pass_basis_reachability_gap_documented`
- `invariant:genesis_compile_checkpoint_1_source_coverage_partial_authority_trace_pass`
- `invariant:genesis_compile_checkpoint_2_authority_traceability_pass_legacy_basis_boundary`
- `invariant:genesis_compile_checkpoint_2_authority_traceability_pass_legacy_fail_expected`
- `invariant:genesis_compile_coverage_partial_result_and_edge_recipe_counts`

## Direct Reads

The batch read the concrete specs, prompts, tests, tools, checkpoint reports,
and walkthroughs that justify these invariants. Source line references are
recorded per invariant in the JSON ledger.

Primary files read:

- `tests/test_genesis_accrual_governor_phase_218.py`
- `tests/test_genesis_accrual_governor_gate_phase_218.py`
- `ilc_core/analysis/genesis_accrual_governor.py`
- `docs/specs/ilc_genesis_accrual_governor_contract_v0.1.md`
- `docs/specs/ilc_genesis_intent_attestation_and_init_authority_map_v0.1.md`
- `docs/antigravity_tasks/antigravity_prompt__phase_1142_atlas_tier1_curated_seed_patch.md`
- `tests/test_phase_1142_atlas_tier1_genesis_attestation.py`
- `docs/phases/phase_1142_atlas_tier1_genesis_attestation_walkthrough.md`
- `tests/test_genesis_node_candidate_crawl.py`
- `tools/crawl_genesis_node_candidates.py`
- `docs/antigravity_tasks/antigravity_prompt__phase_1143_genesis_compile_checkpoint_1.md`
- `tests/test_phase_1143_genesis_compile_checkpoint_1.py`
- `docs/sims/sim_spectral_02/genesis_compile_checkpoint_1_1143_v0.1.md`
- `docs/phases/phase_1143_genesis_compile_checkpoint_1_walkthrough.md`
- `tools/genesis_compile_coverage_diagnostic.py`
- `tests/test_genesis_compile_coverage_diagnostic.py`
- `docs/sims/sim_spectral_02/genesis_compile_coverage_diagnostic_v0.1.md`
- `docs/sims/sim_spectral_02/genesis_compile_coverage_diagnostic_v0.2_candidate.md`
- `tests/test_phase_1150_genesis_compile_checkpoint_2.py`
- `docs/sims/sim_spectral_02/genesis_compile_checkpoint_2_1150_v0.1.md`
- `docs/phases/phase_1150_genesis_compile_checkpoint_2_walkthrough.md`
- `tests/test_phase_1387f_graph_structure_analysis.py`
- `docs/phases/phase_1387f_graph_structure_analysis_walkthrough.md`

## Findings

All ten entries are support-trace invariants with existing role-specific
authority references, classification edges, or simulation/checkpoint scope.
None require a new `GOVERNS` edge.

The batch recommends 35 `EVIDENCES` edges from invariant nodes to actual source
files read. These edges replace weak proxy evidence with source-level
traceability.

## LMDB Application

Applied the recommended edges through `AtlasLmdbSafeWriter` against:

```text
out/genesis_base_graph_v0.4_unified.lmdb
```

Safe-writer summary:

- recommended evidence edges: `35`
- accepted evidence edges: `35`
- rejected evidence edges: `0`
- skipped evidence edges: `0`
- phase-file registration accepted nodes: `3`
- phase-file registration accepted edges: `4`
- parent phase support repair accepted nodes: `1`
- parent phase support repair accepted edges: `3`
- final LMDB nodes: `16,362`
- final LMDB edges: `86,345`
- dangling edges: `0`
- edge-id debt: `0`

The batch ledger and report were registered as support-only phase files in the
same LMDB. A parent support phase node
`phase:1545p_fix63b_direct_source_invariant_audit` was materialized so the
batch005 files can carry forward to the broader Fix63b audit without dangling
or rejected parent links.

## Non-Claims

This batch does not mutate signed Genesis artifacts, does not create authority
nodes, does not promote support invariants into genesis-core authority, does not
activate public RC, and does not authorize production economics, public serving,
or settlement.
