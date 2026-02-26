# ILC Genesis State Bundle Contract and CDL-022 Evidence Prelock 311 v0.1

Status: Phase-311 contract/evidence artifact  
Date: 2026-02-26  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

Define the genesis state bundle contract boundary and lock pre-ratification evidence requirements for CDL-022 before any runtime implementation tranche.

This phase is contract/evidence only. It does not implement runtime behavior in `ilc_core/` and does not mutate constitutional decision-log rows.

## 2. CDL-022 state and option inventory

Source of truth: `docs/specs/ilc_constitutional_decision_log_v0.1.md`.  
Values below are derived from the parsed CDL-022 row in the decision log at phase execution time.

Current CDL-022 row state:
- `status: open`
- `current_candidate: genesis bundle + ceremony (proposed)`

Option inventory:
- `genesis bundle only`
- `genesis bundle + ceremony`
- `ad hoc bootstrapping`

Phase-311 lock:
- no ratification selection is executed in this phase,
- option inventory is preserved for the future ratification lane,
- this lane only defines admissibility boundaries and evidence requirements.

## 3. Genesis state bundle command/data contract baseline

Baseline contract surface for genesis state bundle work:
- genesis bundle artifacts must define deterministic object layout, mandatory headers, and canonical serialization requirements,
- ceremony artifacts must define deterministic sequencing for signing and attestation steps,
- genesis bundle contract must remain transport-agnostic in this phase (no CDL-024 implementation coupling),
- generator/verifier contracts must emit deterministic pass/fail outcomes for canonical test vectors.

Minimum contract elements for downstream runtime lane:
- canonical genesis bundle namespace and versioning rules,
- required section taxonomy (genesis metadata, signer set, signature attestations, integrity references),
- deterministic normalization rules for emitted bundle artifacts,
- backward-compatibility statement against D2 schema baseline dependency.

## 4. D2 schema dependency lock (`d2_schema_baseline_310.v0.1`)

Hard dependency lock:
- Phase 311 and Phase 312 depend on schema baseline version token `d2_schema_baseline_310.v0.1`,
- downstream runtime behavior may not silently substitute another schema baseline token,
- any future baseline token change requires an explicit lane and explicit governance tracking.

Verifier regression carry-forward token set from Phase 310:
- `d2_schema_catalog_not_object`
- `d2_schema_invalid_catalog_version`
- `d2_schema_catalog_digest_missing`
- `d2_schema_catalog_digest_mismatch`
- `d2_schema_catalog_not_canonical`

## 5. Determinism and validation rules

Determinism rules:
- bundle schema text and ceremony examples must be stable under repeat generation,
- normative examples must be machine-verifiable by tests,
- output ordering and canonical digest semantics must be deterministic.

Validation rules:
- generator/verifier contracts must provide deterministic failure tokens for invalid input,
- invalid ceremony sequence states must produce deterministic rejection tokens,
- validation semantics must avoid dependency on non-local third-party services.

## 6. Evidence prelock requirements for CDL-022

Before any CDL-022 ratification lane may open, the following evidence package must exist:
1. genesis state bundle schema/spec artifact set,
2. generator/verifier tooling contract with deterministic validation semantics,
3. canonical test vectors for both valid and invalid bundle/ceremony states,
4. ceremony checklist with deterministic step ordering and attestation requirements,
5. explicit deferral boundaries to CDL-021 (rust/wasm) and CDL-024 (wire transport).

Phase-311 output is admissibility-focused:
- it defines required evidence classes,
- it does not claim ratification closure,
- it does not change `current_candidate` text.

## 7. Phase-312 runtime entry criteria lock

Phase 312 may begin only when all of the following are true:
- `python3 -m pytest tests/test_phase_308_sequence_lock.py -q` passes,
- `python3 -m pytest tests/test_d2_schema_baseline_contract_and_cdl_020_evidence_prelock_309.py -q` passes,
- `python3 -m pytest tests/test_d2_schema_baseline_runtime_310.py -q` passes,
- `python3 -m pytest tests/test_genesis_state_bundle_contract_and_cdl_022_evidence_prelock_311.py -q` passes,
- `python3 -m pytest tests/test_window_298_307_closure_gate_307.py -q` passes,
- `bash tools/check_window_298_307_closure_gate_phase_307.sh` exits `0`,
- parsed decision-log check confirms `CDL-022` remains `status: open`,
- runtime scope is limited to genesis state bundle implementation tranche,
- no implicit ratification language is introduced in runtime outputs.

## 8. Non-goals and canonical anchors

Non-goals in Phase 311:
- no `ilc_core/` runtime implementation,
- no constitutional decision-log mutation,
- no CDL-022 ratification execution,
- no CDL-024 wire transport implementation details.

Boundary statement:
- no decision-log mutation in this phase,
- no runtime changes under `ilc_core/` in this phase.

Canonical anchors:
- `docs/specs/ilc_phase_308_317_sequence_lock_v0.1.md`
- `docs/specs/ilc_d2_schema_baseline_runtime_handoff_310_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_distribution_architecture_roadmap_v0.3.md`
- `docs/specs/ilc_antigravity_context_capsule_v0.6.md`
