# ILC Node Dissemination Runtime Handoff 362 v0.1

Status: runtime handoff artifact
Date: 2026-03-05
Phase: 362

## 1. Implementation scope

Phase 362 implements the CDL-036 dissemination runtime tranche for header-first dissemination, CID-addressed pull fetch, signature-scope integrity, and routing-only visibility/channel handling.

Implemented runtime module:
- `ilc_core/node/node_dissemination_runtime_362.py`

## 2. Dependency and version locks

Locked constants:
- `NODE_DISSEMINATION_RUNTIME_VERSION = "node_dissemination_runtime_362.v0.1"`
- `CDL_036_DEPENDENCY = "cdl_036_ratified_351.v0.1"`
- `VALIDATION_LIFECYCLE_DEPENDENCY = "validation_lifecycle_runtime_361.v0.1"`

## 3. Header schema and signature-scope contract

Header-first dissemination is enforced with the exact candidate header field set:
- `node_id`, `creator_agent_id`, `epistemic_type`, `visibility`, `channel`, `epoch_created`, `payload_cid`, `signature`

The header signature must commit to header fields plus `payload_cid`.

Signature-scope mismatches and malformed header field sets fail with deterministic tokens.

## 4. Fetch contract and idempotence semantics

CID-addressed pull fetch is enforced:
- `fetch_mode = cid_pull`
- retry-safe semantics required,
- idempotence key derived from `node_id + payload_cid`,
- content-addressed verification before interpretation is mandatory.

## 5. Visibility/channel routing-only contract

Visibility and channel remain routing inputs only.

Transport and protocol interpretation envelopes carry routing inputs for dissemination policy, while authored payload remains immutable and free of transport-routing mutation.

## 6. Orderer-agnostic boundary statement

Runtime remains orderer-agnostic and rejects fixed-orderer configuration.

`pull-dominant with soft push-signals` is enforced as the dissemination mode.

No permanent validator-core orderer or transport binding is introduced.

## 7. Validation failure token catalog

Representative deterministic tokens:
- `node_dissemination_header_field_set_invalid`
- `node_dissemination_signature_scope_violation`
- `node_dissemination_payload_cid_mismatch`
- `node_dissemination_fetch_mode_invalid`
- `node_dissemination_idempotence_key_invalid`
- `node_dissemination_orderer_mode_forbidden`

## 8. Carry-forward constraints for phase 363

Phase 363 must preserve:
- header-first dissemination boundary,
- CID-addressed pull fetch contract,
- authored payload immutability under transport operations,
- orderer-agnostic runtime posture.

Executable-node runtime work in Phase 363 must stay subordinate to the CDL-036 transport contract and must not collapse transport semantics into authored payload.

## 9. Non-goals

This tranche does not:
- implement CDL-037 executable runtime,
- mutate decision-log state,
- introduce full-payload push as default dissemination,
- lock a fixed orderer,
- alter transport-binding authority beyond CDL-024.
