# ILC Public Receipt Representation Cluster Lock 586 v0.1

Status: locked
Date: 2026-04-04
Phase: 586
Owner lane: G8 public-release constitutional closure

## 1. Public receipt cluster target

Phase 586 locks the tight public receipt-representation pre-work required by
ADR-0027 before any public-runtime integration or public release-claim may be
treated as authoritative.

`phase_586_carries_window_585_594_dependency_bundle`.

Binding dependency bundle for this packet:
- `docs/specs/ilc_window_585_594_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_phase_585_594_sequence_lock_v0.1.md`
- `docs/specs/ilc_phase_585_genesis_authority_and_sunset_dependency_note_v0.1.md`
- `docs/adr/ADR_0006_EVE_Canonical_Capsule_Integrity.md`
- `docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md`
- `docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`
- `docs/research/ilc_cryptographic_economic_coupling_memo_v0.1.md`
- `docs/research/ilc_canonical_self_describing_bootstrap_and_receipt_boundary_note_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

Minimum decision-log cluster carried by this packet:
- `CDL-001`
- `CDL-002`
- `CDL-003`
- `CDL-004`
- `CDL-007`
- `CDL-009`
- `CDL-013`
- `CDL-022`
- `CDL-023`
- `CDL-040`
- `CDL-042`
- `CDL-045`
- `CDL-V6`

Required governance tokens:
- `public_receipt_representation_cluster_locked`
- `public_identity_activation_receipt_required`
- `public_quorum_eligibility_receipt_or_proof_required`
- `settlement_linked_public_legitimacy_receipt_required`
- `public_namespace_authority_receipt_required`
- `receipt_representation_must_be_self_describing_lineage_aware_and_attested`
- `public_authority_boundaries_require_signed_cryptographic_attestation`
- `receipt_schema_and_verification_rules_precede_public_runtime_integration`
- `promotion_receipt_is_precedent_not_substitute_for_public_authority_cluster`
- `non_equal_canon_receipt_sources_must_be_labeled`
- `phase_586_carries_window_585_594_dependency_bundle`
- `receipt_schema_v0_1_draft_is_supporting_context_only`

## 2. Receipt classes in scope

The minimum public-authority receipt cluster for Window 585-594 includes:
- public identity activation receipt
- public namespace authority receipt
- public quorum eligibility receipt or proof
- settlement-linked public legitimacy receipt

`public_identity_activation_receipt_required`.
`public_namespace_authority_receipt_required`.
`public_quorum_eligibility_receipt_or_proof_required`.
`settlement_linked_public_legitimacy_receipt_required`.

These receipt classes are distinct public-legitimacy surfaces even when later
runtime code shares encoders, validators, or adjacent manifests.

## 3. Uniform representation discipline

All public-authority receipts and proofs in this cluster must share a uniform
representation discipline.

`receipt_representation_must_be_self_describing_lineage_aware_and_attested`.

The minimum discipline requires:
- explicit artifact kind and schema version
- canonical serialization rule
- stable machine-legible field names
- signer or attestor identity
- authority scope
- lineage or predecessor references where applicable
- deterministic verification references or material
- explicit verification outcome or failure-token vocabulary

This cluster does not require a universal schema for every ILC object. It does
require one coherent representation discipline across the public-authority
receipt boundary.

## 4. Common public-authority field set

Every receipt or proof in this cluster must carry stable equivalents for:
- `artifact_kind`
- `schema_version`
- `receipt_id` or `proof_id`
- `signer_agent_id` or `attestor_agent_id`
- `authority_scope`
- `lineage_ref`
- `epoch_id`
- `issued_at`
- `verification_material_ref`
- `verification_status`

The field names may be encoded according to the canonical serialization rule,
but the machine-legible meaning of these fields must remain stable across the
public-authority receipt surface.

## 5. Receipt-class specific requirements

Identity activation receipt requirements:
- carries canonical key-derived `agent_id`
- carries activation authority reference
- carries admission or stake binding reference

Quorum eligibility receipt or proof requirements:
- carries the eligibility subject
- carries the canonical snapshot or epoch-root reference
- carries deterministic proof material

Settlement-linked public legitimacy receipt requirements:
- carries the settled public action
- carries quorum linkage
- carries settlement linkage
- carries payout or attribution linkage

Promotion-receipt precedent boundary:
- `CDL-038` may inform receipt-specific extension structure
- `promotion_receipt_is_precedent_not_substitute_for_public_authority_cluster`
- private-to-public promotion precedent is not the governing authority for the
  public identity, namespace, quorum, or settlement receipt boundary

## 6. Namespace authority receipt disposition

Public namespace authority carries a first-class receipt surface in the
public-release lane.

That namespace authority receipt must:
- bind handle or namespace label to canonical key-derived identity lineage plus
  admitted activation state
- carry explicit reference to the identity activation receipt lineage
- carry explicit reference to settlement-linked legitimacy where required for
  public continuity
- never float free of the identity activation and settlement-linked legitimacy
  chain

This closes the Phase 585 requirement that public namespace authority receipt
disposition be explicit.

## 7. Verification and failure-token discipline

`public_authority_boundaries_require_signed_cryptographic_attestation`.

Public-authority boundaries require signed and cryptographically attested
artifacts.

Verification rules and deterministic failure tokens must be machine-legible.

Receipt or proof verification must fail closed on:
- missing lineage
- missing authority scope
- missing attestation
- schema or version mismatch

Representative deterministic failure tokens for this cluster include:
- `public_receipt_lineage_missing`
- `public_receipt_authority_scope_missing`
- `public_receipt_attestation_missing`
- `public_receipt_schema_version_invalid`

`receipt_schema_and_verification_rules_precede_public_runtime_integration`.

Public-runtime integration may not be treated as authoritative until this
representation discipline is explicit and passed.

## 8. Explicit deferrals to later phases

Deferred beyond Phase 586:
- final public identity activation governance policy
- final public quorum-selection or VRF mechanics
- runtime implementation of receipt issuance or validation
- broader payout economics and reputation portability closure

Supporting-context labeling rules:
- `docs/specs/ilc_receipt_schema_v0.1.md` is draft supporting context only, not
  equal canon for this public-authority cluster
- `CDL-038` is a narrow receipt precedent for extension structure, not the
  governing authority for public identity, namespace, quorum, or settlement
  legitimacy receipts
- `receipt_schema_v0_1_draft_is_supporting_context_only`
- `non_equal_canon_receipt_sources_must_be_labeled`
