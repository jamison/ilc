# ILC Public Receipt Schema and Query Contract Spec 616 v0.1

Status: locked
Date: 2026-04-13
Phase: 616
Owner lane: G8 MVP gate spec lane

`public_receipt_schema_and_query_contract_spec_locked`

## 1. Receipt schema contract target and inherited discipline

Phase 616 locks the receipt issuance and query touchpoint of the Phase 612
minimum participant-touch package.

This spec anchors to the Phase 586 public receipt representation cluster and
converts that representation discipline into a concrete machine-legible minimum
schema plus a bounded read-only query contract. It also inherits the public
identity and admission constraints from Phases 587 and 614 and the bounded
lifecycle visibility contract from Phase 615.

`public_receipt_schema_anchors_to_phase_586_cluster`.
`phase_616_carries_phase_612_mvp_gate_dependency`.
`receipt_issuance_and_query_is_second_of_five_mvp_touchpoints`.
`receipt_schema_does_not_widen_wallet_or_admission_authority`.

The governing representation discipline is Phase 586's public receipt
representation cluster. The common field set follows Phase 586 Section 4 exactly, no new receipt classes may be introduced beyond those locked in Phase 586 Section 2, CDL-062 is not opened, and no substrate selection occurs here.

## 2. Minimum common public-authority field schema

`minimum_common_field_schema_is_locked`.

The minimum common public-authority field schema is:
- `artifact_kind` (string): identifies the receipt class carried by the object.
- `schema_version` (string): records the semantic version of the receipt schema.
- `receipt_id` (string): carries the unique deterministic receipt identifier.
- `signer_agent_id` (string): records the key-derived `agent_id` of the
  issuing or attesting agent.
- `authority_scope` (string): states the bounded scope of this receipt's
  authority.
- `lineage_ref` (string or null): points to the predecessor receipt or Genesis
  artifact reference when lineage is required.
- `epoch_id` (string): records the validation epoch or issuance epoch
  identifier.
- `issued_at` (integer): stores the UTC issuance timestamp in seconds since the
  Unix epoch.
- `verification_material_ref` (string or null): references deterministic
  verification material such as a signature, proof, or hash.
- `verification_status` (string): records one of `valid`, `failed`, or
  `pending`.

These names are JSON-compatible and their machine-legible meaning is stable
across the public-authority receipt surface.

## 3. Receipt class schemas

Phase 586 Section 2 locks exactly four receipt classes, and this phase closes
their minimum schema extensions over the common field set:

- public identity activation receipt:
  `activated_agent_id` (string, key-derived canonical agent_id),
  `admission_authority_scope` (string),
  `stake_binding_ref_or_null` (string or null)
- public namespace authority receipt:
  `namespace_label` (string),
  `bound_agent_id` (string),
  `activation_receipt_ref` (string)
- public quorum eligibility receipt or proof:
  `eligibility_subject_agent_id` (string),
  `snapshot_or_epoch_root_ref` (string),
  `proof_material_ref` (string)
- settlement-linked public legitimacy receipt:
  `settled_public_action_ref` (string),
  `quorum_receipt_ref` (string),
  `settlement_receipt_ref` (string),
  `payout_or_attribution_ref` (string)

No fifth receipt class is introduced by this spec.

## 4. Receipt query contract

`receipt_query_contract_is_read_only`.

Receipts are queryable by:
- `receipt_id`
- `signer_agent_id`
- `artifact_kind + epoch_id`

The query response is a JSON array of matching receipt objects.

The query surface is read-only. No mutation operations, write paths, issuance
actions, revocation actions, or state changes are part of this contract.

Query must fail closed if a required index is unavailable: return an explicit error object with a machine-legible failure token, not an empty array that pretends no matching receipt exists.

The query contract must respect the Phase 576 wallet boundary: visibility and
accounting only. Receipt query does not widen wallet authority, payment
authority, or public claimability.

## 5. Verification and failure-token discipline

`receipt_verification_must_fail_closed`.

Receipt verification must fail closed on:
- missing `lineage_ref` when required
- missing `authority_scope`
- missing attestation or `verification_material_ref`
- schema mismatch
- version mismatch

Failure tokens must be machine-legible strings, not unstructured error prose.
Verification failure must set `verification_status: failed` and include a
`failure_token` field with a structured code.

Minimum failure tokens:
- `missing_lineage`
- `missing_scope`
- `missing_attestation`
- `schema_mismatch`
- `version_mismatch`
- `receipt_not_found`

## 6. Explicit exclusions and deferred items

The following items remain explicitly deferred:
- runtime implementation of receipt issuance
- runtime implementation of receipt query
- public claimability or settlement semantics bound to receipt state
- VRF mechanics for quorum eligibility proofs
- final governance policy for receipt succession or revocation

This phase does not widen wallet or admission authority, does not introduce new
receipt classes, and does not perform substrate selection or runtime execution.
