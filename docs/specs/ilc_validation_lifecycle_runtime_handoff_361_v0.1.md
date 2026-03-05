# ILC Validation Lifecycle Runtime Handoff 361 v0.1

Status: runtime handoff artifact
Date: 2026-03-05
Phase: 361

## 1. Implementation scope

Phase 361 implements the CDL-035 validation lifecycle runtime tranche for deterministic transition validation, gate-verdict by-reference attachment, and quarantine handling.

Implemented runtime module:
- `ilc_core/node/validation_lifecycle_runtime_361.py`

## 2. Dependency and version locks

Locked constants:
- `VALIDATION_LIFECYCLE_RUNTIME_VERSION = "validation_lifecycle_runtime_361.v0.1"`
- `CDL_035_DEPENDENCY = "cdl_035_ratified_350.v0.1"`
- `NODE_SCHEMA_CORE_DEPENDENCY = "node_schema_core_runtime_360.v0.1"`

## 3. Lifecycle state machine and transition matrix

Allowed lifecycle states:
- `proposed`, `under_review`, `corroborated`, `quarantined`, `refuted`, `finalized`

Allowed edges:
- `proposed -> under_review | quarantined`
- `under_review -> corroborated | refuted | quarantined`
- `corroborated -> finalized | refuted | quarantined`
- `quarantined -> under_review | refuted`
- `refuted -> under_review`

Forbidden edges are rejected with deterministic transition-failure tokens.

## 4. Gate-verdict by-reference attachment contract

Gate verdict references are carried only in protocol interpretation envelope fields.

The authored payload remains immutable and does not gain lifecycle metadata fields or gate-verdict payload copies.

## 5. Quarantine handling contract

`quarantined` is a first-class lifecycle state with explicit transition rules.

Transitions into quarantine require gate verdict references, and recovery exits are restricted to approved edges.

## 6. Validation failure token catalog

Representative deterministic tokens:
- `validation_lifecycle_transition_forbidden`
- `validation_lifecycle_gate_verdict_ref_required`
- `validation_lifecycle_from_state_invalid`
- `validation_lifecycle_to_state_invalid`
- `validation_lifecycle_record_digest_mismatch`

## 7. Carry-forward constraints for phase 362

Phase 362 must retain authored payload immutability and continue attaching gate verdict references by reference.

Phase 362 must not widen transition edges or quarantine entry/exit semantics without constitutional authorization.

## 8. Non-goals

This tranche does not:
- implement CDL-036 transport runtime,
- mutate decision-log state,
- mutate authored payload in-place,
- introduce non-deterministic lifecycle evaluation.
