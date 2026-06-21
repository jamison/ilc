# Fix63b Direct Source Invariant Audit Batch 003 Report v0.1

Status: applied to unified LMDB
Phase: 1545p-Fix63b-batch003
Ledger: `docs/specs/ilc_fix63b_direct_source_invariant_audit_batch003_v0.1.json`

## Scope

This batch directly read source material for weak-evidence Fix63 invariant rows
21-30:

- `invariant:canon_export_exported_at_utc`
- `invariant:canon_export_preserves_overwrite_protection`
- `invariant:canon_export_rejects_invalid_exact_numeric_balance`
- `invariant:canon_key_registry_cli_outputs_json_error_contract`
- `invariant:canon_key_registry_prod_requires_nonempty_current_keys_and_signature`
- `invariant:canonical_commit_epoch_constructor_validator_decimal_finality_and_consensus_float_rejection`
- `invariant:causal_frontier_genesis_anchor_and_post_genesis_predecessor_quorum_refs`
- `invariant:ccss_cli_recipe_identity_placeholder_genesis_fail_closed_and_allow_reply_endpoint`
- `invariant:claim_composition_projection_schema_authority_source_allowed_reasons`
- `invariant:cluster_a_policy_hash_canonical_json_replay_determinism`

## Direct Reads

The batch read tests, runtime modules, phase walkthroughs, and supporting specs
for the ten invariants. The source line references are recorded per invariant in
the JSON ledger.

Primary files read:

- `tests/test_canon_export_cli.py`
- `ilc_core/cli/canon_export.py`
- `ilc_core/ledger/canon_export.py`
- `ilc_core/ledger/canon_export_format.py`
- `tests/test_canon_bundle_key_registry_cli.py`
- `ilc_core/cli/canon_bundle_key_registry.py`
- `docs/specs/canon_bundle_key_registry_v0.1.md`
- `tests/test_phase_1235_commit_epoch_canonical_mutation.py`
- `ilc_core/protocol/event_log.py`
- `tests/test_phase_1236_fix3_commit_epoch_causal_frontier_projection.py`
- `ilc_core/protocol/commit_epoch_emission_runtime.py`
- `tests/test_sidecar_ccss_cli_public_ux.py`
- `ilc_core/cli/ccss_cli.py`
- `ilc_core/ccss/runtime.py`
- `docs/specs/ilc_ccss_001_private_gated_shard_sidecar_contract_1324_v0.1.md`
- `docs/specs/ilc_ccss_002_capability_membership_grant_revocation_boundary_1325_v0.1.md`
- `docs/specs/ilc_ccss_003_sealed_sender_local_delivery_boundary_1326_v0.1.md`
- `docs/specs/ilc_ccss_004_gossip_jitter_cover_policy_tests_1327_v0.1.md`
- `tests/test_phase_1160_claim_composition_projection_build.py`
- `tools/build_genesis_claim_composition_projection.py`
- `docs/specs/ilc_genesis_claim_composition_projection_plan_1146_v0.1.md`
- `docs/phases/phase_1160_claim_composition_projection_build_walkthrough.md`
- `tests/test_ilc_cluster_a_replay_determinism.py`
- `ilc_core/protocol/ilc_cluster_a_ingest.py`
- `ilc_core/protocol/ilc_cluster_a_conformance.py`

## Findings

All ten entries are support-trace invariants with existing role-specific
authority references or classification edges. None require a new `GOVERNS`
edge.

The batch recommends 34 `EVIDENCES` edges from invariant nodes to the actual
source files read. These edges replace the prior weak `STATUS.md` proxy
evidence with source-level traceability.

## LMDB Plan

Applied the recommended edges through `AtlasLmdbSafeWriter` against:

```text
out/genesis_base_graph_v0.4_unified.lmdb
```

Safe-writer receipt summary:

- recommended evidence edges: `34`
- accepted evidence edges: `34`
- rejected evidence edges: `0`
- skipped evidence edges: `0`
- registered support nodes: `3`
- registered artifact edges: `4`
- final LMDB nodes: `16,355`
- final LMDB edges: `86,262`
- dangling edges: `0`
- edge-id debt: `0`

This report and the batch ledger were registered as support-only phase files in
the same LMDB.

## Non-Claims

This batch does not mutate signed Genesis artifacts, does not create authority
nodes, does not promote support invariants into genesis-core authority, does not
activate public RC, and does not authorize production economics, public serving,
or settlement.
