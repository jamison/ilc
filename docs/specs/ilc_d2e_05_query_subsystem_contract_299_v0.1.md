# ILC D2e-05 Query Subsystem Contract 299 v0.1

Status: Phase-299 contract artifact  
Date: 2026-02-24  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

Lock the D2e-05 query subsystem command contract and JSON schema boundaries before runtime implementation.

This is a contract-only lane.
This phase does not implement query runtime behavior.

## 2. Query command surface contract

Base command:
- `ilc query`

Contracted subcommands for Phase-300 implementation:
- `ilc query node --node-id <id>`
- `ilc query epoch --epoch <n>`
- `ilc query claim --claim-id <id>`

Command-surface compatibility requirements:
- `--help` must print usage and exit `0`.
- unknown arguments must exit `2`.
- command errors must use structured stderr contract defined in section 4.

## 3. Request/response JSON schema contract

Envelope contract (JSON-first):
- success envelope:
  - `{"ok": true, "data": <object>, "meta": <object>}`
- error envelope:
  - `{"ok": false, "error": {"code": <string>, "message": <string>}, "meta": <object>}`

Minimum `meta` fields:
- `command`: invoked command token,
- `schema_version`: contract schema tag,
- `generated_at`: ISO-8601 UTC timestamp.

Schema boundary:
- response `data` shape must be command-specific and versioned,
- no undocumented top-level fields may appear without schema-version bump.

## 4. Error-code and exit-code contract

Exit code contract:
- `0`: success,
- `2`: argument/usage failure,
- `1`: runtime/processing failure.

Error code tokens (minimum set):
- `query_invalid_input`,
- `query_not_found`,
- `query_backend_unavailable`,
- `query_internal_error`.

## 5. Determinism and ordering contract

Determinism requirements:
- identical request input over identical backing state must yield byte-equivalent JSON after stable serialization,
- map/object keys in emitted JSON must be sorted lexicographically,
- list ordering must be stable and explicitly documented per subcommand,
- no non-deterministic fields in `data` payloads.

Timestamp boundary:
- `meta.generated_at` is operational metadata and may vary,
- deterministic comparison mode for tests must ignore `meta.generated_at` or normalize it.

## 6. Phase-300 handoff entry criteria

Phase 300 may begin only when:
1. this Phase-299 contract artifact exists and contract tests pass,
2. command surface and error/exit code semantics are unchanged from this contract,
3. implementation scope is restricted to D2e-05 runtime behavior in `ilc_core/` without decision-log mutation.

## 7. Non-goals and canonical anchors

Non-goals:
- no `ilc_core/` runtime implementation in this phase,
- no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- no expansion into D2e-06/D2e-07 feature lanes.

Canonical anchors:
- `docs/specs/ilc_phase_298_307_sequence_lock_v0.1.md`
- `docs/specs/ilc_d2e_04_identity_subsystem_contract_293_v0.1.md`
- `docs/specs/ilc_d2e_04_identity_subsystem_handoff_294_v0.1.md`
- `docs/specs/ilc_sdk_boundary_contract_234_v0.1.md`
- `docs/specs/ilc_mutation_canary_gate_contract_297_v0.1.md`
