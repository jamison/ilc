# ILC D2e-03 Prototype Contract 263 v0.1

Status: Phase-263 contract artifact
Date: 2026-02-22
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

Lock implementation boundaries for the D2e-03 prototype lane before runtime code changes.

This contract defines what Phase 264 must implement and what remains deferred.

## 2. Locked command surface constraints (Phase-253 anchor)

Phase 264 must implement only the commands locked in `docs/specs/ilc_cli_command_surface_lock_253_v0.1.md`.

Primitive commands (7):
- `assert`
- `validate`
- `contradict`
- `refute`
- `revise`
- `link`
- `epoch`

Operational commands (8):
- `query`
- `verify`
- `balance`
- `identity`
- `bundle`
- `shard`
- `capproof`
- `config`

No command additions, renames, or aliases are permitted in Phase 264.

## 3. Output schema conformance constraints (Phase-254 anchor)

Phase 264 runtime outputs must conform to `docs/specs/ilc_cli_output_schemas_254_v0.1.md`.

Required output behavior:
- deterministic JSON output on `stdout`,
- structured JSON error payloads on `stderr`,
- exit-code contract preserved (`0`, `1`, `2`, `3`),
- schema version tagging compatible with Phase-254 contract.

## 4. Data model and persistence boundary (JSON-first local graph)

Phase 264 prototype persistence model:
- local JSON-backed graph state,
- D2 minimal schema baseline from `docs/specs/ilc_d2_minimal_schema_specification_255_v0.1.md` (Node, Edge, Epoch Record),
- deterministic serialization path for prototype artifacts.

No networked state service or transport abstraction work is required in Phase 264.

## 5. Explicit DAG-CBOR deferral statement

DAG-CBOR byte-level encoding and full CID pipeline hardening are deferred beyond Phase 264.

Phase 264 does not require runtime DAG-CBOR encoding implementation to satisfy contract closure.

## 6. Acceptance checklist for Phase 264

- [ ] locked command names are implemented with no extra commands,
- [ ] command output responses conform to Phase-254 schema contract,
- [ ] exit-code semantics match locked values,
- [ ] prototype uses local JSON-backed graph persistence,
- [ ] D2 minimal schema constraints are covered by tests,
- [ ] DAG-CBOR deferral is preserved with no in-scope runtime encoder,
- [ ] no CDL mutation occurs during implementation lane.

## 7. Non-goals

Phase 264 implementation is not required to:
- deliver D2e-04 identity subsystem features,
- implement D2e-07 bundle subsystem features,
- implement transport bindings,
- alter constitutional decision-log state.

## 8. Canonical anchors

- `docs/specs/ilc_cli_command_surface_lock_253_v0.1.md`
- `docs/specs/ilc_cli_output_schemas_254_v0.1.md`
- `docs/specs/ilc_d2_minimal_schema_specification_255_v0.1.md`
- `docs/specs/ilc_d2e_03_readiness_assessment_257_v0.1.md`
- `docs/specs/ilc_phase_260_269_sequence_lock_v0.1.md`
