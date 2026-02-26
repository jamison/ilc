# ILC Epoch Snapshot Runtime Handoff 314 v0.1

Status: Phase-314 implementation handoff artifact  
Date: 2026-02-26  
Owner lane: G8 Constitution Cluster A

## 1. Implementation scope summary

Phase 314 implements the initial epoch snapshot runtime tranche in:
- `ilc_core/epoch/epoch_snapshot_runtime.py`
- `ilc_core/epoch/__init__.py`

Shipped runtime surface:
- deterministic epoch snapshot generator (`generate_epoch_snapshot`),
- deterministic epoch snapshot verifier (`verify_epoch_snapshot`),
- canonical vector accessor (`canonical_epoch_snapshot_vectors`),
- typed deterministic validation exception (`EpochSnapshotValidationError`).

## 2. Dependency and version lock

Locked constants in this tranche:
- runtime version token: `epoch_snapshot_runtime_314.v0.1`,
- schema dependency token: `d2_schema_baseline_310.v0.1`,
- genesis dependency token: `genesis_state_bundle_312.v0.1`.

Downstream phases may not silently substitute any dependency/version token.

## 3. Determinism and contract rules

Determinism guarantees:
- canonical ordering for checkpoint refs, retained epochs, and required artifact lists,
- stable SHA-256 digest over canonical runtime core (`snapshot_sha256`),
- deterministic checks payload ordering in verifier output.

Contract rule lock:
- bootstrap target epoch must equal snapshot epoch,
- retention window must align with bootstrap start epoch and keep-last count,
- runtime validation is local and deterministic (no third-party dependency).

## 4. Validation failure token catalog

Primary deterministic error tokens:
- `epoch_snapshot_payload_not_object`
- `epoch_snapshot_not_object`
- `epoch_snapshot_id_missing`
- `epoch_snapshot_network_missing`
- `epoch_snapshot_epoch_invalid`
- `epoch_snapshot_retained_epochs_not_list`
- `epoch_snapshot_retained_epochs_empty`
- `epoch_snapshot_retained_epoch_invalid`
- `epoch_snapshot_target_epoch_not_retained`
- `epoch_snapshot_checkpoint_refs_not_list`
- `epoch_snapshot_checkpoint_refs_empty`
- `epoch_snapshot_checkpoint_ref_not_object`
- `epoch_snapshot_checkpoint_kind_missing`
- `epoch_snapshot_checkpoint_ref_missing`
- `epoch_snapshot_checkpoint_ref_duplicate`
- `epoch_snapshot_bootstrap_not_object`
- `epoch_snapshot_bootstrap_start_epoch_invalid`
- `epoch_snapshot_bootstrap_target_epoch_invalid`
- `epoch_snapshot_bootstrap_epoch_range_invalid`
- `epoch_snapshot_bootstrap_target_epoch_mismatch`
- `epoch_snapshot_bootstrap_required_artifacts_not_list`
- `epoch_snapshot_bootstrap_required_artifacts_empty`
- `epoch_snapshot_bootstrap_required_artifact_invalid`
- `epoch_snapshot_retention_not_object`
- `epoch_snapshot_retention_keep_last_invalid`
- `epoch_snapshot_retention_minimum_epoch_invalid`
- `epoch_snapshot_retention_window_invalid`
- `epoch_snapshot_retention_bootstrap_mismatch`
- `epoch_snapshot_record_not_object`
- `epoch_snapshot_runtime_version_invalid`
- `epoch_snapshot_schema_dependency_invalid`
- `epoch_snapshot_genesis_dependency_invalid`
- `epoch_snapshot_digest_missing`
- `epoch_snapshot_digest_mismatch`
- `epoch_snapshot_not_canonical`

## 5. Canonical test vectors

Phase-314 baseline vectors are provided by `CANONICAL_EPOCH_SNAPSHOT_VECTORS` in the runtime module and consumed directly by `tests/test_epoch_snapshot_runtime_314.py`.

Current vectors:
- `snapshot-mainnet-100`
- `snapshot-testnet-42`

## 6. Compatibility notes for prior D2 lanes

Phase 314 does not alter query/verify/bundle/identity envelope contracts:
- query remains `299.v0.1`,
- verify remains `301.v0.1`,
- bundle remains `303.v0.1`,
- legacy identity remains flat `254.v0.1`.

These invariants are asserted in `test_runtime_integration_does_not_regress_query_verify_bundle_or_identity_envelopes`.

## 7. Test evidence summary

Executed for this phase:
- `tests/test_epoch_snapshot_runtime_314.py`
- `tests/test_epoch_snapshot_contract_and_cdl_023_evidence_prelock_313.py`
- `tests/test_d2_schema_baseline_contract_and_cdl_020_evidence_prelock_309.py`
- `tests/test_genesis_state_bundle_contract_and_cdl_022_evidence_prelock_311.py`
- `tests/test_d2_schema_baseline_runtime_310.py`
- `tests/test_genesis_state_bundle_runtime_312.py`
- `tests/test_phase_308_sequence_lock.py`
- `tests/test_d2e_05_query_subsystem_contract_299.py`
- `tests/test_d2e_06_verify_subsystem_contract_301.py`
- `tests/test_d2e_07_bundle_subsystem_contract_303.py`
- `tests/test_d2e_05_query_subsystem_300.py`
- `tests/test_d2e_06_verify_subsystem_302.py`
- `tests/test_d2e_07_bundle_subsystem_304.py`
- `tests/test_d2e_composed_preflight_306.py`
- `tests/test_window_298_307_closure_gate_307.py`

## 8. Non-goals and carry-forward pointer

Non-goals in this tranche:
- no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- no CDL-023 ratification execution,
- no CDL-021 rust/wasm implementation,
- no CDL-024 wire transport implementation.

Carry-forward pointer:
- Phase 315 should publish monitoring baseline updates covering D2 schema + genesis + epoch runtime surfaces,
- Phase 316 should consume this handoff to execute composed preflight across all three runtime lanes.
