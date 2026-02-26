# ILC Epoch Snapshot Contract and CDL-023 Evidence Prelock 313 v0.1

Status: Phase-313 contract/evidence artifact  
Date: 2026-02-26  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

Define the epoch snapshot contract boundary and lock pre-ratification evidence requirements for CDL-023 before any runtime implementation tranche.

This phase is contract/evidence only. It does not implement runtime behavior in `ilc_core/` and does not mutate constitutional decision-log rows.

## 2. CDL-023 state and option inventory

Source of truth: `docs/specs/ilc_constitutional_decision_log_v0.1.md`.  
Values below are derived from the parsed CDL-023 row in the decision log at phase execution time.

Current CDL-023 row state:
- `status: open`
- `current_candidate: hybrid model (proposed)`

Option inventory:
- `periodic snapshots`
- `triggered snapshots`
- `hybrid model`

Phase-313 lock:
- no ratification selection is executed in this phase,
- option inventory is preserved for the future ratification lane,
- this lane only defines admissibility boundaries and evidence requirements.

## 3. Epoch snapshot command/data contract baseline

Baseline contract surface for epoch snapshot work:
- epoch snapshot artifacts must define deterministic snapshot object layout, mandatory headers, and canonical serialization requirements,
- fast-bootstrap artifacts must define deterministic replay and integrity verification boundaries,
- epoch snapshot contract remains transport-agnostic in this phase (no CDL-024 implementation coupling),
- snapshot generator/verifier contracts must emit deterministic pass/fail outcomes for canonical test vectors.

Minimum contract elements for downstream runtime lane:
- canonical snapshot namespace and versioning rules,
- required section taxonomy (snapshot metadata, retained epochs, checkpoint references, integrity attestations),
- deterministic normalization rules for emitted snapshot artifacts,
- retention and bootstrap-policy contract hooks with deterministic validation semantics.

## 4. Dependency locks (`d2_schema_baseline_310.v0.1`, `genesis_state_bundle_312.v0.1`)

Hard dependency locks:
- Phase 313 and Phase 314 depend on schema baseline version token `d2_schema_baseline_310.v0.1`,
- Phase 313 and Phase 314 depend on genesis runtime version token `genesis_state_bundle_312.v0.1`,
- downstream runtime behavior may not silently substitute either dependency token,
- any future dependency token change requires an explicit lane and explicit governance tracking.

## 5. Determinism and validation rules

Determinism rules:
- snapshot schema/spec text and bootstrap examples must be stable under repeat generation,
- normative examples must be machine-verifiable by tests,
- output ordering and canonical digest semantics must be deterministic.

Validation rules:
- generator/verifier contracts must provide deterministic failure tokens for invalid snapshot input,
- invalid retention/bootstrap states must produce deterministic rejection tokens,
- validation semantics must avoid dependency on non-local third-party services.

## 6. Evidence prelock requirements for CDL-023

Before any CDL-023 ratification lane may open, the following evidence package must exist:
1. epoch snapshot schema/spec artifact set,
2. snapshot generator/verifier tooling contract with deterministic validation semantics,
3. canonical test vectors for valid and invalid snapshot/bootstrap states,
4. retention-policy contract with deterministic admissibility checks,
5. explicit deferral boundaries to CDL-021 (rust/wasm) and CDL-024 (wire transport runtime).

Phase-313 output is admissibility-focused:
- it defines required evidence classes,
- it does not claim ratification closure,
- it does not change `current_candidate` text.

## 7. Phase-314 runtime entry criteria lock

Phase 314 may begin only when all of the following are true:
- `python3 -m pytest tests/test_phase_308_sequence_lock.py -q` passes,
- `python3 -m pytest tests/test_d2_schema_baseline_contract_and_cdl_020_evidence_prelock_309.py -q` passes,
- `python3 -m pytest tests/test_genesis_state_bundle_contract_and_cdl_022_evidence_prelock_311.py -q` passes,
- `python3 -m pytest tests/test_d2_schema_baseline_runtime_310.py -q` passes,
- `python3 -m pytest tests/test_genesis_state_bundle_runtime_312.py -q` passes,
- `python3 -m pytest tests/test_epoch_snapshot_contract_and_cdl_023_evidence_prelock_313.py -q` passes,
- `python3 -m pytest tests/test_window_298_307_closure_gate_307.py -q` passes,
- `bash tools/check_window_298_307_closure_gate_phase_307.sh` exits `0`,
- parsed decision-log check confirms `CDL-023` remains `status: open`,
- dependency checks confirm `d2_schema_baseline_310.v0.1` and `genesis_state_bundle_312.v0.1`,
- runtime scope is limited to epoch snapshot implementation tranche,
- no implicit ratification language is introduced in runtime outputs.

## 8. Non-goals and canonical anchors

Non-goals in Phase 313:
- no `ilc_core/` runtime implementation,
- no constitutional decision-log mutation,
- no CDL-023 ratification execution,
- no CDL-024 wire transport implementation details.

Boundary statement:
- no decision-log mutation in this phase,
- no runtime changes under `ilc_core/` in this phase.

Canonical anchors:
- `docs/specs/ilc_phase_308_317_sequence_lock_v0.1.md`
- `docs/specs/ilc_d2_schema_baseline_runtime_handoff_310_v0.1.md`
- `docs/specs/ilc_genesis_state_bundle_runtime_handoff_312_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_distribution_architecture_roadmap_v0.3.md`
- `docs/specs/ilc_antigravity_context_capsule_v0.6.md`
