# ILC D2e-07 Bundle Subsystem Contract 303 v0.1

Status: Phase-303 contract artifact  
Date: 2026-02-25  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

Lock the D2e-07 bundle subsystem command contract and provider-boundary rules before runtime implementation.

This is a contract-only lane.
This phase does not implement bundle runtime behavior.

## 2. Bundle command surface contract

Base command:
- `ilc bundle`

Contracted subcommands for Phase-304 implementation:
- `ilc bundle inspect --bundle-cid <cid>`
- `ilc bundle verify --bundle-cid <cid>`
- `ilc bundle validate-local --bundle-cid <cid> --graph-state <path>`

Argument precedence note:
- for `validate-local`, subcommand `--graph-state` is authoritative for validation input path,
- top-level CLI `--graph-state` (shared CLI flag) is not used for `validate-local` validation path resolution.

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
- `303.v0.1`.

Success `data` minimum shape:
- `subject`: object identifying target bundle and invocation context,
- `result`: object with `status` token and operation-specific summary fields,
- `checks`: list of check-result objects.

Design rationale:
- bundle lane uses `result` (not `verdict`) intentionally because bundle operations may return richer operational outcomes than binary verification judgments used in D2e-06 verify lane.

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
- `bundle_invalid_input`,
- `bundle_not_found`,
- `bundle_manifest_invalid`,
- `bundle_provider_blocked`,
- `bundle_backend_unavailable`,
- `bundle_internal_error`.

## 5. Determinism and ordering contract

Determinism requirements:
- identical request input over identical backing state must yield byte-equivalent JSON after stable serialization,
- map/object keys in emitted JSON must be sorted lexicographically,
- `checks` ordering must be stable and explicitly documented per subcommand.

Timestamp boundary:
- `meta.generated_at` is operational metadata and may vary,
- deterministic comparison mode for tests must ignore `meta.generated_at` or normalize it.

## 6. Provider boundary contract

Provider-boundary requirements:
- local provider path is mandatory baseline and must be supported without external dependencies,
- external provider adapters are optional and may be configured by operator policy,
- protocol core must not require a third-party facilitator service for baseline bundle operations,
- provider errors must fail closed with structured error tokens.

## 7. Phase-304 handoff entry criteria

Phase 304 may begin only when:
1. this Phase-303 contract artifact exists and contract tests pass,
2. command surface and error/exit semantics are unchanged from this contract,
3. implementation scope is restricted to D2e-07 runtime behavior in `ilc_core/` without decision-log mutation,
4. Phase-302 verify regression remains green.

## 8. Non-goals and canonical anchors

Non-goals:
- no `ilc_core/` runtime implementation in this phase,
- no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- no transport/payment ratification or provider-vendor lock-in decisions.

Canonical anchors:
- `docs/specs/ilc_phase_298_307_sequence_lock_v0.1.md`
- `docs/specs/ilc_d2e_06_verify_subsystem_contract_301_v0.1.md`
- `docs/specs/ilc_d2e_06_verify_subsystem_handoff_302_v0.1.md`
- `docs/specs/ilc_signing_provider_interface_262_v0.1.md`
- `docs/specs/ilc_sdk_boundary_contract_234_v0.1.md`
