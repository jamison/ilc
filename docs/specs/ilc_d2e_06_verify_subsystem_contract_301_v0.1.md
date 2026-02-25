# ILC D2e-06 Verify Subsystem Contract 301 v0.1

Status: Phase-301 contract artifact  
Date: 2026-02-25  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

Lock the D2e-06 verify subsystem command contract and JSON schema boundaries before runtime implementation.

This is a contract-only lane.
This phase does not implement verify runtime behavior.

## 2. Verify command surface contract

Base command:
- `ilc verify`

Contracted subcommands for Phase-302 implementation:
- `ilc verify claim --claim-id <id>`
- `ilc verify node --node-id <id>`
- `ilc verify lineage --lineage-id <id>`

Lineage scope boundary for Phase 302:
- `verify lineage` validates against local identity-state surface only,
- Phase 302 does not import or mutate CDL-001 signer-lineage runtime modules in `ilc_core/security/`.

Command-surface compatibility requirements:
- `--help` must print usage and exit `0`,
- unknown arguments must exit `2`,
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

`meta.schema_version` contract tag for this lane:
- `301.v0.1`.

Success `data` minimum shape:
- `subject`: object with identifier fields for verified target,
- `verdict`: object with `verified` boolean and `verdict_code` token,
- `checks`: list of check-result objects.

Minimum check-result schema:
- `check_type`: string token,
- `passed`: boolean,
- additional fields are permitted but must be deterministic.

Schema boundary:
- response `data` shape must be command-specific and versioned,
- no undocumented top-level fields may appear without schema-version bump.

## 4. Error-code and exit-code contract

Exit code contract:
- `0`: success,
- `2`: argument/usage failure,
- `1`: runtime/processing failure.

Error code tokens (minimum set):
- `verify_invalid_input`,
- `verify_not_found`,
- `verify_signature_mismatch`,
- `verify_policy_rejected`,
- `verify_backend_unavailable`,
- `verify_internal_error`.

## 5. Determinism, ordering, and policy-read-only boundary

Determinism requirements:
- identical request input over identical backing state must yield byte-equivalent JSON after stable serialization,
- map/object keys in emitted JSON must be sorted lexicographically,
- `checks` list ordering must be stable and explicitly documented per subcommand.

Timestamp boundary:
- `meta.generated_at` is operational metadata and may vary,
- deterministic comparison mode for tests must ignore `meta.generated_at` or normalize it.

Policy-read-only boundary:
- verify may consume existing anti-abuse context signals as opaque fields where present,
- verify must not introduce or derive new anti-abuse/reputation scoring constants in this lane.

## 6. Phase-302 handoff entry criteria

Phase 302 may begin only when:
1. this Phase-301 contract artifact exists and contract tests pass,
2. command surface and error/exit semantics are unchanged from this contract,
3. implementation scope is restricted to D2e-06 runtime behavior in `ilc_core/` without decision-log mutation,
4. Phase-300 query regression remains green.

## 7. Non-goals and canonical anchors

Non-goals:
- no `ilc_core/` runtime implementation in this phase,
- no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- no expansion into D2e-07 feature lanes.

Canonical anchors:
- `docs/specs/ilc_phase_298_307_sequence_lock_v0.1.md`
- `docs/specs/ilc_d2e_05_query_subsystem_contract_299_v0.1.md`
- `docs/specs/ilc_d2e_05_query_subsystem_handoff_300_v0.1.md`
- `docs/specs/ilc_reuse_diversity_anti_sybil_contract_v0.1.md`
- `docs/specs/ilc_subjective_objective_epistemic_type_and_sybil_guardrails_precanon_v0.1.md`
