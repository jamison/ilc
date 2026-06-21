# Fix63b Direct Source Invariant Audit Batch 008 Report v0.1

Status: applied to unified LMDB
Phase: 1545p-Fix63b-batch008
Ledger: `docs/specs/ilc_fix63b_direct_source_invariant_audit_batch008_v0.1.json`

## Scope

This batch directly read source material for weak-evidence Fix63 invariant rows
71-80:

- `invariant:idea_descent_genesis_rework_local_rehearsal_no_graph_write_no_signing`
- `invariant:idea_descent_rehearsal_sidecar_local_only_canonical_hash_determinism_no_activation_no_writes`
- `invariant:ilc_core_code_health_thresholds_not_regressed`
- `invariant:ilc_node_v0_ndjson_roundtrip_and_csv_export`
- `invariant:j006_shadow_only_no_public_activation_no_random_no_float`
- `invariant:j007_shadow_ingestion_no_production_ingestion_no_live_ecu_distribution_no_random_no_float`
- `invariant:ledger_phase3_no_loose_any_and_has_bundle_replay_audit_typed_markers`
- `invariant:ledger_signature_migration_dual_verify_cutoff_and_security_contract`
- `invariant:legacy_kernel_genesis_graph_boot_and_derivative_link`
- `invariant:lineage_lifecycle_event_schema_transition_pair_coverage`

## Direct Reads

The batch read concrete runtime modules, tests, specifications, and walkthroughs.
Source line references are recorded per invariant in the JSON ledger.

Primary files read:

- `ilc_core/sidecars/idea_descent_rehearsal.py`
- `tests/test_phase_1546p_idea_descent_rehearsal_sidecar.py`
- `docs/specs/ilc_idea_descent_phase_prompt_objective_v0.1.md`
- `tests/test_code_health.py`
- `ilc_core/node/node_v0.py`
- `tests/test_ilc_node_v0.py`
- `docs/phases/phase_0066f_g1_ilc_node_v0_walkthrough.md`
- `ilc_core/protocol/event_export.py`
- `ilc_core/epistemic/jury_assignment_runtime.py`
- `tests/test_phase_1396_j006_jury_assignment_runtime.py`
- `docs/phases/phase_1396_j006_jury_assignment_runtime_walkthrough.md`
- `ilc_core/epistemic/ingestion_shadow_harness.py`
- `tests/test_phase_1397_j007_shadow_public_ingestion_harness.py`
- `docs/phases/phase_1397_j007_shadow_public_ingestion_harness_walkthrough.md`
- `tests/test_ledger_typed_contract_guardrails_phase3.py`
- `docs/phases/phase_0985_g8_constitution_cluster_a_typed_return_contract_rollout_ledger_canon_export_and_bundle_helper_report_surfaces_phase3_walkthrough.md`
- `tests/test_ledger_signature_migration_contract_282.py`
- `docs/specs/ilc_ledger_signature_migration_contract_282_v0.1.md`
- `docs/phases/phase_0282_g8_constitution_cluster_a_ledger_signature_migration_contract_lock_walkthrough.md`
- `tests/test_kernel.py`
- `ilc_core/graph/__init__.py`
- `docs/phases/phase_0974_g8_constitution_cluster_a_track1_full_edge_removal_production_edge_constructor_eviction_slice1_walkthrough.md`
- `tests/test_lineage_event_schema_phase_240.py`
- `docs/specs/ilc_lineage_lifecycle_event_schema_v0.1.md`
- `docs/phases/phase_0240_g8_constitution_cluster_a_security_runtime_sequence_lock_and_lineage_event_schema_walkthrough.md`
- `docs/specs/ilc_lineage_lifecycle_event_schema_v0.2.md`
- `tests/test_signing_provider_interface_262.py`
- `docs/phases/phase_0262_g8_constitution_cluster_a_signing_provider_interface_and_wallet_agnostic_doc_amendments_walkthrough.md`

## Findings

All ten entries are support-trace invariants with direct source evidence. None
requires a new `GOVERNS` edge in this batch.

Three entries also have explicit authority/policy references from the direct
read:

- J006 references ADR-0040 jury eligibility assignment.
- J007 references ADR-0041 agent INIT and ingestion protocol.
- The lineage lifecycle transition invariant references CDL-001 signer lineage
  trust root.

Two idea-descent local-only invariants are classified by the existing local-only
idea-descent policy node.

## Recommended Edges

The batch recommends 35 new edges:

- `EVIDENCES`: 30
- `CLASSIFIED_BY`: 2
- `REFERENCES_AUTHORITY`: 3

These replace weak proxy evidence with source-level traceability while
preserving the support-only boundary for local rehearsal, shadow harness,
contract-lock, and compatibility surfaces.

## LMDB Application

Applied through `AtlasLmdbSafeWriter` against:

```text
out/genesis_base_graph_v0.4_unified.lmdb
```

Safe-writer summary:

- recommended semantic edges: `35`
- accepted semantic edges: `35`
- skipped duplicate semantic edges: `0`
- rejected semantic edges: `0`
- phase-file registration accepted nodes: `3`
- phase-file registration accepted edges: `6`
- registration refresh accepted nodes: `1`
- registration refresh accepted edges: `2`
- final LMDB nodes: `16,372`
- final LMDB edges: `86,470`
- dangling edges: `0`
- edge-id debt: `0`

The batch ledger and report were registered as support-only phase files in the
same LMDB and carry forward to
`phase:1545p_fix63b_direct_source_invariant_audit`.

The registration refresh used the same corrected file contents after the
ledger-summary repair. It added only the support phase node
`phase:1545p_fix63b_batch008_refresh` and two refresh `CARRIES_FORWARD` edges;
duplicate classification and carry-forward edges to the root Fix63b phase were
skipped by the safe writer.

## Non-Claims

This batch does not mutate signed Genesis artifacts, does not create authority
nodes, does not promote support invariants into genesis-core authority, does not
activate public RC, and does not authorize production economics, public serving,
or settlement.
