# ILC Genesis State Bundle Runtime Handoff 312 v0.1

Status: Phase-312 implementation handoff artifact  
Date: 2026-02-26  
Owner lane: G8 Constitution Cluster A

## 1. Implementation scope summary

Phase 312 implements the initial genesis state bundle runtime tranche in:
- `ilc_core/genesis/genesis_state_bundle_runtime.py`
- `ilc_core/genesis/__init__.py`

Shipped runtime surface:
- deterministic genesis bundle generator (`generate_genesis_bundle`),
- deterministic genesis bundle verifier (`verify_genesis_bundle`),
- canonical vector accessor (`canonical_genesis_vectors`),
- typed deterministic validation exception (`GenesisBundleValidationError`).

## 2. Dependency and version lock

Locked constants in this tranche:
- runtime version token: `genesis_state_bundle_312.v0.1`,
- schema dependency token: `d2_schema_baseline_310.v0.1`.

The schema dependency token is enforced in verifier validation and must remain explicit in downstream phases.

## 3. Determinism and ceremony rules

Determinism guarantees:
- canonical ordering for bundle fields, allocations, and signer sets,
- stable SHA-256 digest over canonical runtime core (`bundle_sha256`),
- deterministic checks payload ordering in verifier output.

Ceremony rule lock:
- required ceremony sequence is fixed to:
  1) `prepare_bundle`
  2) `announce_signers`
  3) `collect_attestations`
  4) `finalize_bundle`

## 4. Validation failure token catalog

Primary deterministic error tokens:
- `genesis_payload_not_object`
- `genesis_bundle_not_object`
- `genesis_bundle_id_missing`
- `genesis_bundle_epoch_zero_invalid`
- `genesis_bundle_network_missing`
- `genesis_bundle_allocations_not_list`
- `genesis_bundle_allocations_empty`
- `genesis_bundle_allocation_not_object`
- `genesis_bundle_allocation_account_missing`
- `genesis_bundle_allocation_units_invalid`
- `genesis_bundle_signers_not_list`
- `genesis_bundle_signers_empty`
- `genesis_bundle_signer_not_object`
- `genesis_bundle_signer_id_missing`
- `genesis_bundle_signature_missing`
- `genesis_bundle_duplicate_signer`
- `genesis_ceremony_not_list`
- `genesis_ceremony_empty`
- `genesis_ceremony_entry_not_object`
- `genesis_ceremony_step_missing`
- `genesis_ceremony_actor_missing`
- `genesis_ceremony_sequence_invalid`
- `genesis_bundle_record_not_object`
- `genesis_bundle_runtime_version_invalid`
- `genesis_bundle_schema_dependency_invalid`
- `genesis_bundle_digest_missing`
- `genesis_bundle_digest_mismatch`
- `genesis_bundle_not_canonical`

## 5. Canonical test vectors

Phase-312 baseline vectors are provided by `CANONICAL_GENESIS_VECTORS` in the runtime module and consumed directly by `tests/test_genesis_state_bundle_runtime_312.py`.

Current vectors:
- `genesis-mainnet-0`
- `genesis-testnet-0`

## 6. Compatibility notes for prior D2 lanes

Phase 312 does not alter query/verify/bundle/identity envelope contracts:
- query remains `299.v0.1`,
- verify remains `301.v0.1`,
- bundle remains `303.v0.1`,
- legacy identity remains flat `254.v0.1`.

These invariants are asserted in `test_runtime_integration_does_not_regress_query_verify_bundle_or_identity_envelopes`.

## 7. Test evidence summary

Executed for this phase:
- `tests/test_genesis_state_bundle_runtime_312.py`
- `tests/test_genesis_state_bundle_contract_and_cdl_022_evidence_prelock_311.py`
- `tests/test_d2_schema_baseline_contract_and_cdl_020_evidence_prelock_309.py`
- `tests/test_d2_schema_baseline_runtime_310.py`
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
- no CDL-022 ratification execution,
- no CDL-021 rust/wasm implementation,
- no CDL-024 wire transport implementation.

Carry-forward pointer:
- Phase 313 should lock epoch snapshot contract/evidence (CDL-023) using both schema (`d2_schema_baseline_310.v0.1`) and genesis runtime surfaces as dependencies.
