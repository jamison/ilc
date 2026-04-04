# ILC Settlement-Linked Public Legitimacy and Payout Traceability Lock 589 v0.1

Status: locked
Date: 2026-04-04
Phase: 589
Owner lane: G8 public-release constitutional closure

## 1. Settlement-linked public legitimacy target

Phase 589 locks the settlement-linked public legitimacy and payout traceability
boundary for Window 585-594.

This packet defines what makes a public action canonically legitimate after the
identity and quorum boundaries are frozen, and what trace chain a public payout
or attribution must preserve before any later public-runtime integration can be
treated as authoritative.

Required governance tokens:
- `settlement_linked_public_legitimacy_requires_settled_receipt_chain`
- `public_legitimacy_must_reference_activation_quorum_and_settlement_lineage`
- `panel_result_or_claim_batch_alone_not_public_legitimacy`
- `payout_traceability_must_reference_quorum_settlement_and_beneficiary_lineage`
- `payout_traceability_must_preserve_task_epoch_and_claim_batch_identity`
- `namespace_continuity_must_not_bypass_settlement_linked_legitimacy`
- `public_reward_or_attribution_requires_canonical_lineage_membership`
- `promotion_or_provenance_continuity_not_public_legitimacy_substitute`
- `validation_or_quarantine_state_not_settlement_legitimacy_by_itself`
- `settlement_legitimacy_must_fail_closed_on_quorum_or_lineage_mismatch`
- `receipt_envelope_candidate_is_supporting_context_only`
- `public_wallet_visibility_not_public_claimability`
- `reputation_carry_forward_and_minting_semantics_deferred`

## 2. Dependency and inherited canon

Minimum dependency bundle carried by this packet:
- `docs/specs/ilc_window_585_594_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_phase_585_594_sequence_lock_v0.1.md`
- `docs/specs/ilc_public_receipt_representation_cluster_lock_586_v0.1.md`
- `docs/specs/ilc_public_identity_activation_and_namespace_boundary_lock_587_v0.1.md`
- `docs/specs/ilc_public_quorum_eligibility_and_genesis_lineage_authority_boundary_lock_588_v0.1.md`
- `docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`
- `docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_ratification_evidence_350_v0.1.md`
- `docs/specs/ilc_cdl_038_private_to_public_promotion_and_promotion_receipt_ratification_evidence_353_v0.1.md`
- `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md`
- `docs/specs/ilc_rc0_1_ecu_settlement_wallet_query_integration_581_v0.1.md`

Tier rule for mixed payout-trace sources:
- `docs/specs/ilc_receipt_envelope_and_payout_trace_contract_candidate_v0.1.md`
  is supporting context only and not equal canon with the ratified CDL or
  locked Phase 586 receipt boundary.
- RC0.1 settlement/runtime artifacts are bounded implementation context, not by
  themselves the public-release legitimacy contract.
- `receipt_envelope_candidate_is_supporting_context_only`.

Inherited canon:
- `public_quorum_authority_requires_eligibility_receipt_or_proof`.
- `namespace_authority_must_remain_compatible_with_settlement_linked_legitimacy`.
- `settlement_linked_public_legitimacy_receipt_required`.

## 3. Public legitimacy receipt-chain boundary

`settlement_linked_public_legitimacy_requires_settled_receipt_chain`.

Settlement-linked public legitimacy requires a settled receipt chain. A public
action is not canonically legitimate merely because it was observed, broadcast,
or staged locally.

`public_legitimacy_must_reference_activation_quorum_and_settlement_lineage`.

Public legitimacy must reference activation lineage, quorum lineage, and
settlement lineage together. The canonical public chain is broken if any one of
those surfaces is missing.

`panel_result_or_claim_batch_alone_not_public_legitimacy`.

A panel result or a claim batch alone is not public legitimacy. Public
legitimacy requires stable equivalents for activation lineage reference,
quorum eligibility reference, quorum outcome or decision linkage, and
settlement receipt linkage.

`settlement_legitimacy_must_fail_closed_on_quorum_or_lineage_mismatch`.

Settlement-linked public legitimacy must fail closed on quorum mismatch,
lineage mismatch, or a broken settled receipt chain.

## 4. Payout traceability and beneficiary identity boundary

`payout_traceability_must_reference_quorum_settlement_and_beneficiary_lineage`.

Public payout or attribution traceability must preserve machine-legible links
among the settled action, quorum result, settlement lineage, and beneficiary
identity lineage.

`payout_traceability_must_preserve_task_epoch_and_claim_batch_identity`.

Public payout or attribution traceability must preserve stable equivalents for
`task_id`, `epoch_id` or `epoch_index`, and `claim_batch_sha256` where the
settled receipt chain represents a bounded claim batch.

The current RC0.1 runtime anchor for bounded claim-batch identity is
`claim_batch_sha256` in `ilc_core/rc/economic_cycle_runtime.py`; later runtimes
may use a stable equivalent, but this packet names the current anchor
explicitly.

`namespace_continuity_must_not_bypass_settlement_linked_legitimacy`.

Namespace continuity must not bypass settlement-linked legitimacy. A public
handle or beneficiary label only remains authoritative if the settled receipt
chain preserves canonical lineage continuity.

`public_reward_or_attribution_requires_canonical_lineage_membership`.

Public reward or attribution requires canonical lineage membership.

`public_wallet_visibility_not_public_claimability`.

Public wallet visibility or internal balance visibility is not public
claimability by itself.

## 5. Promotion, provenance, and non-shortcut rules

`promotion_or_provenance_continuity_not_public_legitimacy_substitute`.

Promotion, provenance continuity, or publication continuity do not by
themselves establish public legitimacy or public payout authority.

`validation_or_quarantine_state_not_settlement_legitimacy_by_itself`.

Validation lifecycle state, quarantine state, or operator-visible state is not
settlement-linked public legitimacy by itself.

`CDL-038` promotion precedent may inform lineage continuity only. It may not be
used as a shortcut to public legitimacy or reward continuity.

## 6. Forbidden interpretations and exclusions

The following interpretations are forbidden:
- treating panel pass, claim-batch construction, or broadcast success as sufficient public legitimacy
- treating wallet visibility or internal balance visibility as public claimability
- treating promotion receipts or provenance continuity as public reward legitimacy
- treating validation lifecycle state as equivalent to settlement-linked public legitimacy
- using supporting payout-trace candidates as equal canon by silence

## 7. Explicit deferrals to later phases

Deferred beyond Phase 589:
- Genesis authority, sunset, and fork-legitimacy coherence closure to Phase 590
- runtime issuance or settlement execution for public receipts
- final public minting, withdrawal, transfer, or spend semantics
- public reputation portability or carry-forward consequences beyond the minimal no-shortcut rule

`reputation_carry_forward_and_minting_semantics_deferred`.
