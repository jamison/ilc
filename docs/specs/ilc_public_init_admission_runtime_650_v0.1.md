# ILC Public Init/Admission Runtime 650 v0.1

Status: implemented
Date: 2026-04-14
Phase: 650
Owner lane: G8 MVP runtime closure

`public_init_admission_runtime_650_live`

## 1. Runtime target and inherited contract

Phase 650 implements the bounded runtime/interface form of the Phase 614 public
init/admission contract. The runtime remains a narrow public activation request
surface tied to canonical key-derived identity, receipt lineage, and admission
receipt issuance.

Inherited contract carried into runtime:
- Phase 614 public init/admission contract
- Phase 616 receipt schema/query discipline
- Phase 587 public identity activation boundary
- Phase 576/581 wallet boundary
- Window 642-648 exact-numeric, non-finite, and canonical JSON guardrails

The runtime is limited to admission-shaped receipt issuance and persistence. It
does not authorize permissionless participation, chain-side activation,
payment/runtime settlement, wallet write authority, or public claimability.

## 2. Bounded request and response contract

The bounded public request is `POST /v1/public/init/admission`.

Required request fields:
- `agent_id`
- `canonical_root_key_hex`
- `authority_scope`
- `lineage_ref`
- `verification_material_ref`

Optional request field:
- `stake_binding_ref_or_null`

`init_request_requires_canonical_agent_id_and_lineage_inputs`

Request validation is fail-closed:
- `agent_id` must match the CDL-042 key-derived identity computed from
  `canonical_root_key_hex`
- `authority_scope` must remain the bounded `public_init_admission` scope
- `lineage_ref` must be present
- `verification_material_ref` must be present as the admission attestation
  anchor

Success response is machine-legible:
- `ok: true`
- `token: admission_receipt_issued`
- `persisted: true`
- `receipt: {...}`

Failure response is machine-legible:
- `ok: false`
- `token: <machine_token>`

Minimum failure tokens:
- `missing_agent_id`
- `missing_canonical_root_key`
- `canonical_root_key_invalid_hex`
- `canonical_root_key_empty`
- `canonical_agent_id_mismatch`
- `missing_scope`
- `authority_scope_forbidden`
- `missing_lineage`
- `missing_attestation`
- `stake_binding_ref_invalid_type`

## 3. Admission receipt issuance and persistence

`bounded_admission_receipt_runtime_issued_and_persisted`

The runtime issues a public identity activation receipt with the bounded Phase
616 field discipline:
- `artifact_kind`
- `schema_version`
- `receipt_id`
- `signer_agent_id`
- `authority_scope`
- `lineage_ref`
- `epoch_id`
- `issued_at`
- `verification_material_ref`
- `verification_status`
- `activated_agent_id`
- `admission_authority_scope`
- `stake_binding_ref_or_null`

Receipt issuance rules:
- `artifact_kind` is `public_identity_activation_receipt`
- `schema_version` remains `v0.1`
- `receipt_id` is deterministic SHA-256 over canonical compact JSON bytes of
  the receipt payload
- `issued_at` is derived deterministically from the bounded `epoch_id` rather
  than from local wall-clock time
- `signer_agent_id` and `activated_agent_id` both bind to the canonical
  key-derived identity
- `verification_status` is `valid` on successful bounded issuance

Persistence rules:
- the receipt is persisted in LMDB by `receipt_id`
- persistence uses canonical compact JSON with sorted keys
- machine-consumed serialization remains compact and uses `allow_nan=False`

## 4. Failure-token and fail-closed discipline

`init_admission_runtime_fails_closed_with_machine_tokens`

The runtime never infers activation from local operator state. Missing or
invalid identity, lineage, scope, or attestation inputs return an explicit
machine token and no receipt is persisted.

The runtime touches no external numeric input fields. For storage and emitted
machine payloads it preserves the inherited exact-numeric and non-finite guard:
canonical JSON remains compact, sorted, and `allow_nan=False`.

The bounded response contract is therefore:
- fail closed on missing lineage/scope/attestation
- fail closed on canonical root-key mismatch
- succeed only by issuing and persisting a receipt artifact

## 5. Explicit exclusions and preserved boundaries

`wallet_boundary_576_581_preserved_in_650`
`no_chain_side_or_permissionless_admission_in_650`

Phase 650 preserves these exclusions:
- no wallet write, transfer, withdrawal, or spend authority
- no public claimability widening
- no permissionless admission
- no chain-side admission
- no payment runtime
- no Agent Skills opening
- no constitutional mutation

The runtime creates a bounded public activation request plus admission receipt
artifact only. A visible admission receipt is not wallet authority, public
claimability, or chain settlement.
