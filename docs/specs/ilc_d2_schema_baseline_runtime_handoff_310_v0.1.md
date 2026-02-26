# ILC D2 Schema Baseline Runtime Handoff 310 v0.1

Status: Phase-310 implementation handoff artifact  
Date: 2026-02-26  
Owner lane: G8 Constitution Cluster A

## 1. Implementation scope summary

Phase 310 implements the initial D2 schema baseline runtime tranche in:
- `ilc_core/schema/d2_schema_baseline_runtime.py`
- `ilc_core/schema/__init__.py`

Shipped runtime surface:
- deterministic schema catalog generator (`generate_schema_catalog`),
- deterministic catalog verifier (`verify_schema_catalog`),
- canonical vector accessor (`canonical_schema_vectors`),
- typed deterministic validation exception (`D2SchemaValidationError`).

## 2. Determinism contract

Determinism guarantees in this tranche:
- canonical ordering for entries and fields,
- stable SHA-256 digest over canonical JSON (`catalog_sha256`),
- deterministic checks payload ordering in verifier output.

Repeat runs over identical inputs produce byte-equivalent catalogs and equivalent verification payloads.

## 3. Validation failure token catalog

Primary deterministic error tokens:
- `d2_schema_entries_empty`
- `d2_schema_missing_schema_id`
- `d2_schema_fields_not_list`
- `d2_schema_fields_empty`
- `d2_schema_missing_field_name`
- `d2_schema_invalid_field_type`
- `d2_schema_invalid_required_flag`
- `d2_schema_duplicate_field`
- `d2_schema_duplicate_schema_id`
- `d2_schema_catalog_not_object`
- `d2_schema_invalid_catalog_version`
- `d2_schema_catalog_entries_not_list`
- `d2_schema_catalog_digest_missing`
- `d2_schema_catalog_digest_mismatch`
- `d2_schema_catalog_not_canonical`

## 4. Canonical test vectors

Phase-310 baseline vectors are provided by `CANONICAL_SCHEMA_VECTORS` in the runtime module and consumed directly by `tests/test_d2_schema_baseline_runtime_310.py`.

Current vectors:
- `d2.claim.v1`
- `d2.edge.v1`

## 5. Compatibility notes for prior D2 lanes

Phase 310 does not alter query/verify/bundle/identity envelope contracts:
- query remains `299.v0.1`,
- verify remains `301.v0.1`,
- bundle remains `303.v0.1`,
- legacy identity remains flat `254.v0.1`.

These invariants are asserted in `test_runtime_integration_does_not_regress_query_verify_bundle_or_identity_envelopes`.

## 6. Test evidence summary

Executed for this phase:
- `tests/test_d2_schema_baseline_runtime_310.py`
- `tests/test_d2_schema_baseline_contract_and_cdl_020_evidence_prelock_309.py`
- `tests/test_d2e_05_query_subsystem_contract_299.py`
- `tests/test_d2e_06_verify_subsystem_contract_301.py`
- `tests/test_d2e_07_bundle_subsystem_contract_303.py`
- `tests/test_d2e_05_query_subsystem_300.py`
- `tests/test_d2e_06_verify_subsystem_302.py`
- `tests/test_d2e_07_bundle_subsystem_304.py`
- `tests/test_d2e_composed_preflight_306.py`
- `tests/test_window_298_307_closure_gate_307.py`

## 7. Non-goals and carry-forward pointer

Non-goals in this tranche:
- no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- no CDL-020 ratification execution,
- no CDL-021 rust/wasm implementation,
- no CDL-024 wire transport implementation.

Carry-forward pointer:
- Phase 311 should lock genesis state bundle contract/evidence using this schema runtime baseline as a prerequisite runtime surface.
- Phase 311 must reference the locked schema baseline version token `d2_schema_baseline_310.v0.1` as a hard dependency.
