# ILC Public Quorum Eligibility and Genesis-Lineage Authority Boundary Lock 588 v0.1

Status: locked
Date: 2026-04-04
Phase: 588
Owner lane: G8 public-release constitutional closure

## 1. Public quorum authority target

Phase 588 locks the public quorum eligibility and Genesis-lineage authority
boundary for Window 585-594.

This packet defines the minimum public-authority gate that must be satisfied
before an activated identity can participate in canonical public 7+1 authority.
It freezes the lineage and snapshot-root boundary for public quorum authority
without closing the final panel-seating or VRF algorithm.

Required governance tokens:
- `public_quorum_authority_requires_eligibility_receipt_or_proof`
- `quorum_eligibility_must_bind_to_activated_identity_lineage`
- `quorum_eligibility_must_bind_to_canonical_snapshot_or_epoch_root`
- `bootstrap_validator_set_or_quorum_seed_lineage_required_for_public_quorum_authority`
- `unactivated_or_unproven_identity_is_not_public_quorum_authority`
- `public_quorum_authority_must_preserve_cdl_v3_diversity_boundary`
- `public_quorum_authority_must_remain_compatible_with_cdl_051_quorum_record_chain`
- `genesis_rooted_bootstrap_lineage_required_for_public_quorum_authority`
- `cdl_v6_extraordinary_intervention_not_ordinary_quorum_eligibility`
- `seven_plus_one_panel_case_evaluation_not_constitutional_governance`
- `activation_and_quorum_authority_must_respect_cdl_001_canonical_authority_state_gating`
- `supporting_panel_selection_context_not_equal_canon`
- `exact_selection_algorithm_deferred_but_not_ad_hoc`

## 2. Dependency and inherited canon

Minimum dependency bundle carried by this packet:
- `docs/specs/ilc_window_585_594_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_phase_585_594_sequence_lock_v0.1.md`
- `docs/specs/ilc_public_receipt_representation_cluster_lock_586_v0.1.md`
- `docs/specs/ilc_public_identity_activation_and_namespace_boundary_lock_587_v0.1.md`
- `docs/specs/ilc_phase_585_genesis_authority_and_sunset_dependency_note_v0.1.md`
- `docs/adr/ADR_0014_Identity_Sybil_and_Admission_Control_Envelope.md`
- `docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`
- `docs/specs/ilc_cdl_v3_quorum_diversity_ratification_evidence_332_v0.1.md`
- `docs/specs/ilc_cdl_051_constitutional_consensus_and_epoch_finality_ratification_evidence_443_v0.1.md`
- `docs/specs/ilc_cdl_045_operational_emergency_response_ratification_evidence_408_v0.1.md`
- `docs/specs/ilc_cdl_v6_genesis_intervention_protocol_ratification_evidence_334_v0.1.md`
- `docs/specs/ilc_cdl_001_signer_lineage_trust_root_contract_v0.1.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.2.md`

Tier rule for mixed panel-selection sources:
- `docs/specs/ilc_antigravity_context_capsule_v3.0.md` and earlier capsule
  versions carrying equivalent 7+1 panel-selection language are supporting
  context only, not equal canon with the ratified CDL layer.
- `docs/specs/ilc_rc0_1_7_plus_1_panel_live_submission_integration_580_v0.1.md`
  is runtime/supporting context only, not the governing public-release
  authority contract.
- `supporting_panel_selection_context_not_equal_canon`.

Inherited canon:
- `public_identity_activation_requires_settled_admission_or_stake_binding_receipt`.
- `activation_and_namespace_authority_must_respect_cdl_001_canonical_authority_state_gating`.
- `canonical_public_legitimacy_must_flow_through_genesis_rooted_lineage`.

## 3. Public quorum eligibility boundary

`public_quorum_authority_requires_eligibility_receipt_or_proof`.

Canonical public quorum authority requires an eligibility receipt or proof. Raw
panel participation, local orchestration success, or operator-local assignment
is not enough.

`quorum_eligibility_must_bind_to_activated_identity_lineage`.

Public quorum eligibility must bind to activated identity lineage. The subject
of a public eligibility proof is an already-activated public identity, not a
raw key or operator-local alias.

`quorum_eligibility_must_bind_to_canonical_snapshot_or_epoch_root`.

Public quorum eligibility must bind to a canonical snapshot or epoch root so
that public authority is checked against a settled canonical view rather than a
mutable local runtime convenience.

`unactivated_or_unproven_identity_is_not_public_quorum_authority`.

An unactivated identity, or an activated identity without an eligibility proof,
is not canonical public quorum authority.

The public quorum eligibility surface is a public-authority gate, not a local
runtime convenience.

## 4. Canonical snapshot and diversity binding

`public_quorum_authority_must_preserve_cdl_v3_diversity_boundary`.

Any public quorum authority surface must preserve the ratified CDL-V3 diversity
boundary. Later panel-seating or VRF logic may refine selection mechanics, but
it may not erase the diversity floor.

`public_quorum_authority_must_remain_compatible_with_cdl_051_quorum_record_chain`.

Any public quorum eligibility proof must remain compatible with the CDL-051
quorum-record chain so later public legitimacy can trace the quorum decision
through a stable epoch-state lineage.

`bootstrap_validator_set_or_quorum_seed_lineage_required_for_public_quorum_authority`.

Public quorum eligibility proof must preserve stable references for the
activated identity subject, the canonical snapshot or epoch root, and the
bootstrap lineage anchor such as `validator_set_hash`, `quorum_record_seed`, or
a stable equivalent proving continuity back to the canonical Genesis-rooted
authority chain.

Public quorum eligibility proof must also preserve the quorum-state or
epoch-state lineage needed for later public legitimacy.

Exact panel seating or VRF algorithm is not closed here, but any later
algorithm must remain bounded by the ratified diversity and quorum-record
chain.

`exact_selection_algorithm_deferred_but_not_ad_hoc`.

## 5. Genesis-lineage and ordinary-authority distinction

`genesis_rooted_bootstrap_lineage_required_for_public_quorum_authority`.

Ordinary public quorum authority must remain continuous with the canonical
Genesis-rooted bootstrap lineage. A public eligibility proof that cannot trace
back to the canonical bootstrap lineage is not canonical public quorum
authority.

`cdl_v6_extraordinary_intervention_not_ordinary_quorum_eligibility`.

CDL-V6 extraordinary intervention is not ordinary public quorum eligibility. It
is a bounded emergency path and may not be treated as a substitute for ordinary
public-authority proof.

`seven_plus_one_panel_case_evaluation_not_constitutional_governance`.

The 7+1 panel remains case-evaluation machinery, not constitutional governance.
Its authority is bounded by the public-authority and lineage rules in this
window.

`activation_and_quorum_authority_must_respect_cdl_001_canonical_authority_state_gating`.

Ordinary public quorum authority must flow through admitted activation lineage
and canonical eligibility proof, not through Genesis override or emergency
posture. Public quorum authority must also respect CDL-001 canonical-authority
state gating: rotated or revoked lineage is not current public authority until
the canonical recovered-state path completes.

## 6. Forbidden interpretations and exclusions

The following interpretations are forbidden:
- treating raw panel participation as equivalent to canonical public quorum authority
- treating Genesis extraordinary authority as ordinary quorum eligibility
- allowing unactivated identities to become public quorum participants
- allowing operator-local or harness-local panel assignment rules to substitute for canonical eligibility proof
- treating supporting-context 7+1 or VRF language as equal canon by silence
- treating local snapshot convenience as equivalent to canonical snapshot or epoch-root lineage

## 7. Explicit deferrals to later phases

Deferred beyond Phase 588:
- settlement-linked public legitimacy and payout traceability closure to Phase 589
- Genesis authority, sunset, and fork-legitimacy coherence closure to Phase 590
- runtime implementation of public eligibility-proof issuance or validator selection
- any final public reputation weighting or incentive consequences for quorum service
