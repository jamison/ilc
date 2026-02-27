# ILC Wire Transport Runtime Handoff 323 v0.1

Status: Phase-323 implementation handoff artifact  
Date: 2026-02-27  
Owner lane: G8 Constitution Cluster A

## 1. Implementation scope summary

Phase 323 implements the initial wire transport runtime tranche in:
- `ilc_core/network/wire_transport_runtime.py`
- `ilc_core/network/__init__.py`

Shipped runtime surface:
- deterministic wire transport envelope generator (`generate_wire_transport_envelope`),
- deterministic wire transport envelope verifier (`verify_wire_transport_envelope`),
- canonical vector accessor (`canonical_wire_transport_vectors`),
- typed deterministic validation exception (`WireTransportValidationError`).

## 2. Dependency/version lock section

Locked constants in this tranche:
- runtime version token: `wire_transport_runtime_323.v0.1`,
- schema dependency token: `d2_schema_baseline_310.v0.1`,
- genesis dependency token: `genesis_state_bundle_312.v0.1`,
- epoch dependency token: `epoch_snapshot_runtime_314.v0.1`.

Downstream phases may not silently substitute any dependency/version token.

## 3. Determinism and contract rules

Determinism guarantees:
- canonical ordering for headers and payload mappings,
- stable SHA-256 digest over canonical runtime core (`envelope_sha256`),
- deterministic checks payload ordering in verifier output.

Contract rule lock:
- runtime is provider-neutral and transport-agnostic,
- transport kind and delivery policy are validated through deterministic allowlists,
- no external network calls are required for generator/verifier operation.

## 4. Validation failure token catalog

Primary deterministic error tokens:
- `wire_transport_payload_record_not_object`
- `wire_transport_envelope_not_object`
- `wire_transport_message_id_missing`
- `wire_transport_schema_ref_missing`
- `wire_transport_content_type_missing`
- `wire_transport_headers_not_object`
- `wire_transport_header_key_invalid`
- `wire_transport_header_value_invalid`
- `wire_transport_payload_not_object`
- `wire_transport_transport_not_object`
- `wire_transport_kind_invalid`
- `wire_transport_delivery_mode_invalid`
- `wire_transport_qos_invalid`
- `wire_transport_retry_policy_not_object`
- `wire_transport_retry_max_invalid`
- `wire_transport_retry_backoff_invalid`
- `wire_transport_runtime_version_invalid`
- `wire_transport_schema_dependency_invalid`
- `wire_transport_genesis_dependency_invalid`
- `wire_transport_epoch_dependency_invalid`
- `wire_transport_digest_missing`
- `wire_transport_digest_mismatch`
- `wire_transport_not_canonical`

## 5. Canonical test vectors summary

Phase-323 baseline vectors are provided by `CANONICAL_WIRE_TRANSPORT_VECTORS` in the runtime module and consumed directly by `tests/test_wire_transport_runtime_323.py`.

Current vectors:
- `msg-claim-1` (quic / request_response / at_least_once)
- `msg-edge-1` (libp2p / pubsub / at_most_once)

## 6. Compatibility notes for prior runtime lanes

Compatibility lock preserved:
- schema baseline dependency remains `d2_schema_baseline_310.v0.1`,
- genesis runtime dependency remains `genesis_state_bundle_312.v0.1`,
- epoch runtime dependency remains `epoch_snapshot_runtime_314.v0.1`.

No regression scope in this lane:
- no mutation under `ilc_core/schema/`,
- no mutation under `ilc_core/genesis/`,
- no mutation under `ilc_core/epoch/`.

## 7. Test evidence summary

Executed for this phase:
- `tests/test_wire_transport_runtime_323.py`
- `tests/test_wire_transport_contract_and_cdl_024_evidence_prelock_322.py`
- `tests/test_d2_schema_baseline_runtime_310.py`
- `tests/test_genesis_state_bundle_runtime_312.py`
- `tests/test_epoch_snapshot_runtime_314.py`
- `tests/test_window_308_317_closure_gate_317.py`
- `tests/test_ratification_mutation_scope_261.py`
- `tools/check_window_308_317_closure_gate_phase_317.sh`
- `tools/run_mutation_canary_phase_297.py`

## 8. Non-goals and carry-forward pointer

Non-goals in this tranche:
- no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- no CDL-024 ratification execution,
- no CDL-021 rust/wasm implementation,
- no single-provider transport binding.

Carry-forward pointer:
- Phase 324 should open CDL-V1/V2/V3 entries and prelock evidence artifacts as sensitive constitutional mutation work,
- Phase 327 closure gate should include this handoff in cross-phase regression inputs.
