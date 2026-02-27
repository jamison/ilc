# ILC Wire Transport Contract and CDL-024 Evidence Prelock 322 v0.1

Status: Phase-322 contract/evidence artifact  
Date: 2026-02-27  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

Define the wire-transport contract boundary and lock pre-ratification evidence requirements for CDL-024 before any runtime implementation tranche.

This phase is contract/evidence only. It does not implement runtime behavior in `ilc_core/` and does not mutate constitutional decision-log rows.

## 2. CDL-024 state and option inventory

Source of truth: `docs/specs/ilc_constitutional_decision_log_v0.1.md`.  
Values below are derived from the parsed CDL-024 row in the decision log at phase execution time.

Current CDL-024 row state:
- `status: open`
- `current_candidate: transport-agnostic + reference bindings (proposed)`

Option inventory:
- `single transport binding`
- `transport-agnostic + reference bindings`
- `framework-specific bindings`

Phase-322 lock:
- no ratification selection is executed in this phase,
- option inventory is preserved for the future ratification lane,
- this lane only defines admissibility boundaries and evidence requirements.

## 3. Wire transport command/data contract baseline

Baseline contract surface for wire transport work:
- wire transport contracts must define deterministic message envelope fields, schema versioning rules, and transport metadata boundaries,
- wire transport contracts must define deterministic error envelope structure and retry semantics,
- wire transport contracts must define deterministic conformance outcomes for canonical message fixtures,
- wire transport contracts must remain provider-neutral and transport-agnostic in this phase.

Minimum contract elements for downstream runtime lane:
- canonical transport envelope namespace and versioning rules,
- required section taxonomy (message envelope, headers, payload framing, error contract, conformance assertions),
- deterministic normalization rules for transport envelope serialization,
- compatibility commitments to current runtime surfaces (schema/genesis/epoch tokens).

## 4. Dependency and transport-agnostic boundary lock

Hard compatibility lock:
- Phase 322 and Phase 323 must preserve compatibility with:
  - `d2_schema_baseline_310.v0.1`,
  - `genesis_state_bundle_312.v0.1`,
  - `epoch_snapshot_runtime_314.v0.1`.

Transport boundary lock:
- this lane remains transport-agnostic and provider-neutral,
- this lane does not bind implementation to a single transport/provider,
- this lane does not include rust/wasm implementation coupling (`CDL-021` remains out of scope).

## 5. Determinism and conformance validation rules

Determinism rules:
- transport schema/spec text and envelope examples must be stable under repeat generation,
- normative examples must be machine-verifiable by tests,
- envelope ordering and digest semantics must be deterministic.

Validation rules:
- conformance checks must provide deterministic failure tokens for invalid transport message fixtures,
- invalid header/payload/error envelope states must produce deterministic rejection tokens,
- validation semantics must avoid dependency on non-local third-party services.

## 6. Evidence prelock requirements for CDL-024

Before any CDL-024 ratification lane may open, the following evidence package must exist:
1. D2d message schema set with canonical envelope definitions,
2. transport requirement and compatibility matrix,
3. deterministic conformance test vectors (valid and invalid transport fixtures),
4. error-envelope contract and retry-boundary semantics,
5. explicit deferral boundaries to CDL-021 rust/wasm implementation work.

Phase-322 output is admissibility-focused:
- it defines required evidence classes,
- it does not claim ratification closure,
- it does not change `current_candidate` text.

## 7. Phase-323 runtime entry criteria lock

Phase 323 may begin only when all of the following are true:
- `python3 -m pytest tests/test_phase_318_sequence_lock.py -q` passes,
- `python3 -m pytest tests/test_cdl_023_ratification_321.py -q` passes,
- `python3 -m pytest tests/test_wire_transport_contract_and_cdl_024_evidence_prelock_322.py -q` passes,
- `python3 -m pytest tests/test_d2_schema_baseline_runtime_310.py -q` passes,
- `python3 -m pytest tests/test_genesis_state_bundle_runtime_312.py -q` passes,
- `python3 -m pytest tests/test_epoch_snapshot_runtime_314.py -q` passes,
- `python3 -m pytest tests/test_window_308_317_closure_gate_317.py -q` passes,
- `bash tools/check_window_308_317_closure_gate_phase_317.sh` exits `0`,
- parsed decision-log check confirms `CDL-024` remains `status: open`,
- runtime scope is limited to wire transport implementation tranche,
- no implicit ratification language is introduced in runtime outputs.

## 8. Non-goals and canonical anchors

Non-goals in Phase 322:
- no `ilc_core/` runtime implementation,
- no constitutional decision-log mutation,
- no CDL-024 ratification execution,
- no CDL-021 rust/wasm runtime implementation.

Boundary statement:
- no decision-log mutation in this phase,
- no runtime changes under `ilc_core/` in this phase.

Canonical anchors:
- `docs/specs/ilc_phase_318_327_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_023_epoch_snapshot_ratification_evidence_321_v0.1.md`
- `docs/specs/ilc_d2_schema_baseline_runtime_handoff_310_v0.1.md`
- `docs/specs/ilc_genesis_state_bundle_runtime_handoff_312_v0.1.md`
- `docs/specs/ilc_epoch_snapshot_runtime_handoff_314_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_distribution_architecture_roadmap_v0.3.md`
- `docs/specs/ilc_antigravity_context_capsule_v0.6.md`
