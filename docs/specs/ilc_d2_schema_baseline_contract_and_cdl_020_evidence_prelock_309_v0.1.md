# ILC D2 Schema Baseline Contract and CDL-020 Evidence Prelock 309 v0.1

Status: Phase-309 contract/evidence artifact  
Date: 2026-02-26  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

Define the D2 schema baseline contract and lock pre-ratification evidence boundaries for CDL-020 before any runtime implementation tranche.

This phase is contract/evidence only. It does not implement `ilc_core/` runtime behavior and does not mutate constitutional decision-log rows.

## 2. CDL-020 state and option inventory

Source of truth: `docs/specs/ilc_constitutional_decision_log_v0.1.md`.
Values below are derived from the parsed CDL-020 row in the decision log at phase execution time.

Current CDL-020 row state:
- `status: open`
- `current_candidate: full schema catalog (proposed)`

Option inventory:
- `full schema catalog`
- `minimal schema catalog`
- `phased schema catalog`

Phase-309 lock:
- no ratification selection is executed in this phase,
- option inventory is preserved for later ratification lane,
- this lane only defines evidence and contract requirements needed to make a future ratification admissible.

## 3. D2 schema baseline command/data contract

Baseline contract surface for D2 schema work:
- schema catalog artifacts must define canonical type identifiers, field requirements, and deterministic serialization expectations,
- bundle schema artifacts must align with existing D2 command envelope boundaries (`299.v0.1`, `301.v0.1`, `303.v0.1`, legacy identity `254.v0.1`),
- schema contract must remain transport-agnostic at this stage (no CDL-024 implementation coupling),
- schema baseline must provide a deterministic mapping from declared types to validation outcomes for generator/verifier tooling.

Minimum contract elements to carry into runtime lane:
- canonical schema namespace and versioning rules,
- deterministic ordering/normalization rules for schema emission,
- required/optional field taxonomy,
- backward-compatibility statement for D2 pre-existing envelope lanes.

## 4. Determinism and validation rules

Determinism rules:
- schema text and serialization examples must be stable under repeat generation,
- normative examples must be machine-verifiable by tests,
- ambiguous free-form schema definitions are out of contract.

Validation rules:
- generator/verifier tooling contract must validate schema shape deterministically,
- invalid schema inputs must produce explicit and deterministic failure tokens,
- validation semantics must be phrased to avoid dependency on non-local third-party services.

## 5. Evidence prelock requirements for CDL-020

Before any CDL-020 ratification lane may open, the following evidence package must exist:
1. D2 schema artifact set (type catalog + bundle schema baseline),
2. generator/verifier tooling contract with deterministic validation semantics,
3. initial test vectors proving deterministic pass/fail behavior,
4. explicit boundaries to CDL-021 (rust/wasm) and CDL-024 (wire transport) deferrals.

Phase-309 prelock output is admissibility-focused:
- it defines required evidence classes,
- it does not claim ratification closure,
- it does not change `current_candidate` text.

## 6. Phase-310 runtime entry criteria lock

Phase 310 may begin only when all of the following are true:
- this contract artifact is present and tested,
- CDL-020 remains `status: open` with unchanged row text,
- runtime scope is limited to D2 schema baseline implementation tranche,
- no implicit ratification language is introduced in runtime outputs.

## 7. Non-goals and canonical anchors

Non-goals in Phase 309:
- no `ilc_core/` runtime implementation,
- no constitutional decision-log mutation,
- no CDL-020 ratification execution,
- no CDL-024 wire transport implementation details.

Boundary statement:
- no decision-log mutation in this phase,
- no runtime changes under `ilc_core/` in this phase.

Canonical anchors:
- `docs/specs/ilc_phase_308_317_sequence_lock_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_distribution_architecture_roadmap_v0.3.md`
- `docs/specs/ilc_antigravity_context_capsule_v0.6.md`
