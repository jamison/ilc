# ILC Node Schema Core Runtime Handoff 360 v0.1

Status: runtime handoff artifact
Date: 2026-03-05
Phase: 360

## 1. Implementation scope

Phase 360 implements the CDL-034 node schema core runtime tranche for envelope boundaries, reserved-field enforcement, and primitive taxonomy validation.

Implemented runtime module:
- `ilc_core/node/node_schema_core_runtime_360.py`

## 2. Dependency and version locks

Locked constants:
- `NODE_SCHEMA_CORE_RUNTIME_VERSION = "node_schema_core_runtime_360.v0.1"`
- `CDL_034_DEPENDENCY = "cdl_034_ratified_349.v0.1"`
- `SCHEMA_BASELINE_DEPENDENCY = "d2_schema_baseline_310.v0.1"`

## 3. Envelope-boundary runtime semantics

Runtime output preserves the ratified three-envelope model:
- authored payload envelope stores submitter-authored claim material,
- protocol interpretation envelope stores protocol-derived fields,
- transport envelope stores dissemination metadata by reference.

`gate_routing` remains protocol-derived and is rejected if supplied as authored input.

`confidence` and `uncertainty_note` remain authored metadata in authored payload envelope.

## 4. Reserved-field collision enforcement

Reserved fields are enforced against extension surfaces (`meta`, `user_tags`).

If a reserved field is shadowed by authored extension keys, runtime validation fails with deterministic tokenized errors.

## 5. Validation failure token catalog

Representative deterministic tokens:
- `node_schema_gate_routing_submitter_forbidden`
- `node_schema_refutation_not_default_primitive`
- `node_schema_reserved_field_shadow`
- `node_schema_primitive_type_invalid`
- `node_schema_record_digest_mismatch`

## 6. Deterministic vector and digest behavior

Canonical vectors produce deterministic record outputs and stable digest values.

Generator and verifier semantics are canonicalized through sorted serialization and digest checks.

## 7. Carry-forward constraints for phase 361

Phase 361 must treat validation lifecycle state and gate-verdict references as protocol interpretation envelope attachments by reference.

Phase 361 must not mutate authored payload state in-place while applying lifecycle transitions.

## 8. Non-goals

This tranche does not:
- implement validation lifecycle transitions,
- implement transport-layer fetch/dissemination runtime,
- mutate decision-log state,
- allow `refutation` as a default primitive_type.
- refutation is not a default primitive_type.
