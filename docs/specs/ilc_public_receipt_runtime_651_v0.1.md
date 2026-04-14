# ILC Public Receipt Runtime 651 v0.1

Status: implemented
Date: 2026-04-14
Phase: 651
Owner lane: G8 MVP runtime closure

`public_receipt_runtime_651_live`

## 1. Runtime target and inherited schema discipline

Phase 651 implements the bounded runtime/interface form of the Phase 616 public
receipt issuance and query contract.

Phase 586 remains the governing receipt representation cluster. Phase 616 is the concrete schema/query contract derived from that cluster for machine-legible runtime surfaces.

`receipt_runtime_preserves_phase_586_schema_discipline`

The runtime remains bounded to the four locked public receipt classes only:
- `public_identity_activation_receipt`
- `public_namespace_authority_receipt`
- `public_quorum_eligibility_receipt`
- `settlement_linked_public_legitimacy_receipt`

`exactly_four_public_receipt_classes_supported_in_runtime`

No fifth receipt class is accepted, emitted, or indexed by this runtime.

## 2. Receipt issuance and persistence contract

The bounded issuance surface is `POST /v1/public/receipt`.

The runtime accepts a receipt payload for one of the four locked classes,
verifies the common Phase 616 fields plus the class-specific field set, derives
`receipt_id` as canonical SHA-256 over compact sorted JSON bytes, and persists
the receipt through the LMDB public receipt store.

Persistence contract:
- primary persistence by `receipt_id`
- secondary index by `signer_agent_id`
- secondary index by `artifact_kind + epoch_id`
- canonical JSON remains compact, sorted, and `allow_nan=False`

The runtime also preserves Phase 650 compatibility: admission receipts issued by
`POST /v1/public/init/admission` are stored through the same bounded public
receipt store and become queryable through the Phase 651 read-only query
surface.

## 3. Read-only query modes and indexing

`receipt_query_read_only_runtime_live`

The bounded read-only query modes are:
- `GET /v1/public/receipt/{receipt_id}`
- `GET /v1/public/receipts?signer_agent_id=...`
- `GET /v1/public/receipts?artifact_kind=...&epoch_id=...`

Each query response is machine-legible:
- `ok: true`
- `token: receipt_query_result`
- `receipts: [...]`

Query is read-only. No mutation, revocation, succession, receipt rewriting, or
state-transition operation is part of the query surface.

The runtime indexes exactly the locked query modes and does not expose
unbounded receipt scans outside those bounded selectors.

## 4. Verification, failure tokens, and fail-closed behavior

`receipt_query_fails_closed_with_machine_tokens`

The runtime fails closed on:
- unsupported receipt class
- version mismatch
- missing required lineage when the class requires lineage
- missing scope
- missing attestation / `verification_material_ref`
- malformed class-specific fields
- invalid query mode
- missing `epoch_id` for `artifact_kind` query
- `receipt_id` lookup miss

Minimum machine tokens surfaced by the runtime:
- `unsupported_receipt_class`
- `version_mismatch`
- `missing_lineage`
- `missing_scope`
- `missing_attestation`
- `schema_mismatch`
- `invalid_query_mode`
- `epoch_id_required`
- `receipt_not_found`

Retrieved receipts are revalidated against the locked schema discipline before
they are returned. Corrupt or drifted persisted receipts therefore fail closed
instead of being emitted optimistically.

## 5. Explicit exclusions and preserved boundaries

`no_revocation_or_wallet_write_widening_in_651`

Phase 651 preserves these exclusions:
- no revocation or succession policy opening
- no wallet write, transfer, withdrawal, or spend authority
- no public claimability widening
- no quorum VRF opening
- no fifth receipt class
- no constitutional mutation

Receipt issuance and query remain bounded runtime surfaces only. They do not
create payment authority, wallet authority, or new admission law.
