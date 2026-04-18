# ILC Private/Gated Shard Header and Capability-Token Contract Hardening 730 v0.1

**Phase:** 730  
**Window:** 727-732  
**Date:** 2026-04-18  
**Author:** Codex

`private_gated_header_minimum_surface_hardened_for_planning`

## 1. Baseline

Window `727-732` is active under the Phase `727` sequence lock, Phase `728`
carry-forward selection, and the Phase `729` rights/licensing disposition.

This phase does not implement gated shard logic. It hardens the planning
contract for what the minimum public header and bounded access-right reference
surface should be so later implementations do not drift incompatibly.

## 2. Minimum public header surface

The minimum public header surface for a private or gated shard should preserve:

- `shard_id`,
- `creator_agent_id`,
- `visibility_mode`,
- `anchor_mode`,
- `anchor_ref`,
- `root_commitment_ref`,
- `gate_control_ref`,
- `access_model`,
- `lineage_policy_ref`,
- `content_disclosure_level`,
- `epoch_created`,
- `status`.

The design rule is:

- enough public surface to prove existence, anchoring, continuity, and
  navigability,
- not enough public surface to reconstruct private contents without the
  corresponding access rights.

The header therefore belongs at the bounded shard-contract layer rather than
being improvised separately by each implementation.

## 3. Access-right reference model

The bounded planning model for access rights is a capability-token or
contract-reference surface with at least these conceptual fields:

- `access_grant_id`,
- `target_shard_id`,
- `grantor_agent_id`,
- `grantee_ref`,
- `scope`,
- `content_scope`,
- `valid_from_epoch`,
- `valid_to_epoch`,
- `revocation_ref`,
- `payment_ref`,
- `signature`.

`capability_token_reference_model_bounded_for_planning`

The hardening decision here is limited:

- the protocol needs a place to point to access rights,
- the full custody, cryptography, delivery, and enterprise-policy mechanics
  remain deferred to later implementation lanes.

This stays consistent with Phase `729` by keeping rich business logic out of
L1 while still preventing schema drift at the reference boundary.

## 4. Promotion and lineage continuity

Private/gated hardening must preserve continuity with `CDL-038` and
`CDL-041`.

`private_to_public_promotion_continuity_preserved`

That means:

- private/gated promotion still uses successor public node, promotion receipt,
  and disclosed lineage,
- no automatic public corroboration carry-forward,
- no automatic public reputation carry-forward,
- promoted outputs may reference originating `shard_id`, header or root
  commitment, gate policy reference, and optionally disclosed review-history
  hashes,
- shard formation remains an explicit shard-lifecycle event, not an implicit
  side effect of creating a node.

This keeps private rehearsal or gated access continuity legible without turning
private history into automatic public legitimacy.

## 5. Deferred implementation and constitutional questions

The following remain deferred:

- runtime implementation of capability-token custody and validation,
- revocation propagation mechanics across snapshots,
- richer privacy and disclosure policy tuning,
- subscription and payment execution logic,
- whether any future portion of this surface needs dedicated constitutional
  lock rather than spec-level hardening only,
- any new CDL opening tied to this lane.

`no_new_cdl_recommended_in_phase_730`
`no_runtime_mutation_in_phase_730`

## 6. Non-goals

This phase does not include:

- decision-log mutation,
- any CDL ratification,
- runtime implementation of access tokens or gated shard logic,
- financial-shard activation,
- any mutation of `ilc_core/` or `ilc_consensus/`.

This phase is a planning hardening note, not an implementation or
constitutional-closing phase.

## 7. Source inputs

- `docs/PLANNING_INDEX.md`
- `docs/specs/ilc_phase_727_732_sequence_lock_v0.1.md`
- `docs/specs/ilc_adjacent_gated_economy_carry_forward_selection_728_v0.1.md`
- `docs/specs/ilc_rights_licenses_and_gated_access_surfaces_disposition_729_v0.1.md`
- `docs/research/ilc_rights_licenses_and_gated_access_surfaces_memo_v0.1.md`
- `docs/specs/ilc_private_gated_shard_header_and_capability_token_contract_candidate_v0.1.md`
- `docs/adr/ADR_0022_Local_First_Private_Use_and_Publication_Bound_Economics.md`
- `docs/specs/ilc_cdl_038_private_to_public_promotion_and_promotion_receipt_ratification_evidence_353_v0.1.md`
- `docs/specs/ilc_cdl_041_shard_lifecycle_ratification_evidence_394_v0.1.md`
- `docs/phases/STATUS.md`
