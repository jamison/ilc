# ILC D2e-04 Identity Subsystem Contract 293 v0.1

Status: Phase-293 contract lock artifact  
Date: 2026-02-24  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

Define the identity subsystem contract for D2e-04 prior to runtime implementation.

Scope:
- command surface and behavior contract,
- JSON I/O envelope contract,
- deterministic persistence and error semantics.

## 2. Command surface contract

Base command:
- `ilc identity`

Subcommands targeted for phase-294 implementation:
- `ilc identity init`
- `ilc identity show`
- `ilc identity rotate`
- `ilc identity export`

Contract rule:
- command dispatch and argument validation must align with JSON-first output requirements.

## 3. Request/response schema contract

Request model:
- CLI flags map to typed request payloads.

Response envelope (JSON-first):
```json
{
  "schema_version": "254.v0.1",
  "command": "identity",
  "ok": true,
  "ts_utc": "2026-02-24T00:00:00Z",
  "data": {}
}
```

Error envelope:
```json
{
  "schema_version": "254.v0.1",
  "command": "identity",
  "ok": false,
  "error": true,
  "code": "1",
  "message": "stable error token or usage message",
  "details": {}
}
```

## 4. Error-code and exit-code contract

Exit code contract:
- `0`: successful command execution,
- `1`: contract-level operation failure,
- `2`: argument/usage contract violation,
- `3`: transport/network error path (shared CLI envelope behavior).

Error code contract:
- numeric `code` field is the machine-readable discriminator (`0/1/2/3`),
- `message` may include argparse usage text for usage errors,
- deterministic envelope keys are mandatory even when `message` is free-form.

## 5. Persistence and determinism boundaries

Persistence boundary:
- identity state persisted to declared local path only.

Determinism boundary:
- repeated identical inputs must produce stable JSON envelope shape,
- timestamp/random fields must be explicitly identified when nondeterministic.

## 6. Non-goals and rollout boundary

Non-goals in this phase:
- no runtime implementation in `ilc_core/`,
- no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- no wallet-provider backend implementation.

Rollout boundary:
- runtime implementation is deferred to Phase 294.

## 7. Canonical anchors

- `docs/specs/ilc_d2e_03_prototype_contract_263_v0.1.md`
- `docs/specs/ilc_d2e_03_prototype_handoff_265_v0.1.md`
- `docs/specs/ilc_sdk_boundary_contract_234_v0.1.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md`

Boundary statement:
- this contract lane performs no runtime changes and no decision-log mutation.
