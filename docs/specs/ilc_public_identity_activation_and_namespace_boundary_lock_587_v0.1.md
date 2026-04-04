# ILC Public Identity Activation and Namespace Boundary Lock 587 v0.1

Status: locked
Date: 2026-04-04
Phase: 587
Owner lane: G8 public-release constitutional closure

## 1. Public identity boundary target

Phase 587 locks the public identity activation and namespace authority boundary
for Window 585-594.

This packet preserves the already-ratified key-derived agent identity rule while
making explicit that canonical public participation requires more than local key
existence.

Required governance tokens:
- `public_agent_id_remains_key_derived`
- `public_identity_activation_requires_settled_admission_or_stake_binding_receipt`
- `public_write_path_requires_activation_receipt`
- `unbound_key_is_not_canonical_public_participant`
- `public_namespace_authority_is_first_class_receipt_surface`
- `namespace_authority_must_bind_to_admitted_identity_lineage`
- `canonical_root_key_lineage_not_transaction_hash_identity`
- `cdl_040_admission_scope_not_claim_acceptance`
- `display_aliases_are_derivative_not_authoritative`
- `local_private_identity_remains_permitted_outside_public_legitimacy`
- `namespace_authority_must_not_float_free_of_activation_lineage`
- `namespace_authority_must_remain_compatible_with_settlement_linked_legitimacy`
- `cdl_042_ratification_anchor_prelock_reference_only`

## 2. Dependency and inherited canon

Minimum dependency bundle carried by this packet:
- `docs/specs/ilc_window_585_594_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_phase_585_594_sequence_lock_v0.1.md`
- `docs/specs/ilc_public_receipt_representation_cluster_lock_586_v0.1.md`
- `docs/specs/ilc_phase_585_genesis_authority_and_sunset_dependency_note_v0.1.md`
- `docs/adr/ADR_0014_Identity_Sybil_and_Admission_Control_Envelope.md`
- `docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.2.md`
- `docs/specs/ilc_cdl_040_admission_control_and_identity_envelope_ratification_evidence_393_v0.1.md`
- `docs/specs/ilc_cdl_042_agent_identity_namespace_ratification_evidence_407_v0.1.md`
- `docs/specs/ilc_cdl_042_agent_identity_namespace_prelock_hardening_403_v0.1.md`
- `docs/specs/ilc_cdl_001_signer_lineage_trust_root_contract_v0.1.md`

Tier rule for mixed CDL-042 sources:
- `docs/specs/ilc_cdl_042_agent_identity_namespace_ratification_evidence_407_v0.1.md`
  is the binding ratification anchor for the key-derived `agent_id` rule.
- `docs/specs/ilc_cdl_042_agent_identity_namespace_prelock_hardening_403_v0.1.md`
  is historical prelock reference and supporting context only, not equal canon.
- `cdl_042_ratification_anchor_prelock_reference_only`.

Inherited canon:
- `public_agent_id_remains_key_derived`.
- `canonical_root_key_lineage_not_transaction_hash_identity`.
- `cdl_040_admission_scope_not_claim_acceptance`.
- `local_private_identity_remains_permitted_outside_public_legitimacy`.

## 3. Public identity activation boundary

`public_agent_id_remains_key_derived`.

Canonical public identity remains derived from canonical key material through the
ratified CDL-042 rule anchored to the CDL-001 signer-lineage root.

`public_identity_activation_requires_settled_admission_or_stake_binding_receipt`.

A canonical public participant requires a settled admission or stake binding
receipt before public activation is recognized.

`public_write_path_requires_activation_receipt`.

Public write-path authority requires an activation receipt bound to the
key-derived agent identity.

`unbound_key_is_not_canonical_public_participant`.

A local key or local agent_id may exist without public activation, but it is
not canonical public write-path authority.

`local_private_identity_remains_permitted_outside_public_legitimacy`.

Local/private identity and local/private agent use remain permitted outside the
canonical public legitimacy boundary.

## 4. Public namespace authority boundary

`public_namespace_authority_is_first_class_receipt_surface`.

Public namespace authority is a first-class receipt surface in the public lane.

`namespace_authority_must_bind_to_admitted_identity_lineage`.

A namespace authority receipt must bind handles, usernames, or public labels to
admitted identity lineage rather than to a free-floating key or operator label.

`namespace_authority_must_not_float_free_of_activation_lineage`.

Namespace authority must not float free of the activation receipt lineage.

`namespace_authority_must_remain_compatible_with_settlement_linked_legitimacy`.

Namespace authority must preserve the reference slot needed for the later
settlement-linked legitimacy chain where public continuity requires it.

Public handles, usernames, and labels are authoritative only through the
namespace authority receipt chain.

`display_aliases_are_derivative_not_authoritative`.

Display aliases, local labels, and operator-friendly naming layers are
derivative only and are not canonical public authority.

## 5. Lineage, signer-root, and admission binding

`canonical_root_key_lineage_not_transaction_hash_identity`.

Canonical public agent identity continuity follows the CDL-001 signer-lineage
root and the ratified CDL-042 key-derived agent_id rule.

Operational signer rotation does not create a new public agent identity.
Identity continuity is carried by signer-lineage linkage back to the same
canonical_root_key, not by transaction-hash-derived identity.

`cdl_040_admission_scope_not_claim_acceptance`.

CDL-040 admission control and identity-envelope scope remains distinct from
knowledge-claim acceptance and from later public legitimacy closure.

Admission and activation are public authority prerequisites; they do not, by
themselves, constitute knowledge-claim acceptance, quorum legitimacy, or
settlement legitimacy.

## 6. Forbidden interpretations and exclusions

The following interpretations are forbidden:
- deriving canonical public identity from transaction hashes
- treating operator labels or display aliases as canonical public authority
- treating local/private agent existence as equivalent to canonical public
  activation
- treating namespace authority as a free-floating alias system
- reopening the protocol-vs-harness boundary through identity UX work

## 7. Explicit deferrals to later phases

Deferred beyond Phase 587:
- final quorum eligibility and stake-root proof closure to Phase 588
- settlement-linked public legitimacy and payout traceability closure to Phase 589
- Genesis authority, sunset, and fork-legitimacy coherence closure to Phase 590
- runtime implementation of activation or namespace receipt issuance or
  validation
