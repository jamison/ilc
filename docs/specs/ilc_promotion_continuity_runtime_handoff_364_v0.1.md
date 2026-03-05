# ILC Promotion Continuity Runtime Handoff 364 v0.1

Status: runtime handoff artifact
Date: 2026-03-05
Phase: 364

## 1. Implementation scope

Phase 364 implements the CDL-038 promotion continuity runtime tranche for successor-node promotion, promotion_receipt validation, one-way visibility transition, and carry-forward prohibitions.

Implemented runtime module:
- `ilc_core/node/promotion_continuity_runtime_364.py`

## 2. Dependency and version locks

Locked constants:
- `PROMOTION_CONTINUITY_RUNTIME_VERSION = "promotion_continuity_runtime_364.v0.1"`
- `CDL_038_DEPENDENCY = "cdl_038_ratified_353.v0.1"`
- `EXECUTABLE_DESCRIPTOR_DEPENDENCY = "executable_descriptor_runtime_363.v0.1"`

## 3. Successor-node and original-node immutability contract

The runtime enforces successor-node plus promotion_receipt without automatic reputation carry-forward.

Promotion changes visibility only by creating a successor public node plus a promotion_receipt, never by mutating the original node.

The original private node remains immutable after promotion.

## 4. promotion_receipt schema and field requirements

promotion_receipt must carry:
- `original_node_cid`
- `public_successor_node_cid`
- `disclosed_lineage_reference`
- `promotion_epoch`

promotion_receipt field-set and cross-reference mismatches fail with deterministic tokens.

## 5. Carry-forward prohibition contract

No automatic public corroboration or reuse credit carry-forward is allowed.

No automatic reputation carry-forward is allowed.

A promoted public successor node starts in proposed validation_state and does not inherit the original node validation history.

## 6. One-way visibility transition and lineage disclosure rules

Promotion is a one-way visibility transition.

Disclosed lineage is required; anonymous laundering of private work into public credit is not permitted.

Promotion preserves provenance continuity, not public legitimacy or reward continuity.

## 7. Validation failure token catalog

Representative deterministic tokens:
- `promotion_receipt_field_set_invalid`
- `promotion_in_place_visibility_mutation_forbidden`
- `promotion_successor_visibility_invalid`
- `promotion_validation_state_carry_forward_forbidden`
- `promotion_corroboration_carry_forward_forbidden`
- `promotion_reputation_carry_forward_forbidden`

## 8. Carry-forward constraints for phase 365

Phase 365 simulations and outputs must not reinterpret successful promotion as automatic reputation or corroboration transfer.

Phase 365 must keep promotion continuity subordinate to CDL-034 reserved-field and CDL-035 validation semantics.

## 9. Non-goals

This tranche does not:
- implement new ratification actions,
- mutate decision-log state,
- allow in-place visibility mutation of private nodes,
- allow automatic carry-forward of legitimacy or rewards.
