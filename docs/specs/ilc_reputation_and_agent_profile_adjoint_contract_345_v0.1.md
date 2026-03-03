# ILC Reputation and Agent-Profile Adjoint Contract v0.1

## 1. Purpose and scope

This artifact resolves the Window 338-347 reputation-model decision forced by the node-schema packet. It defines how reputation relates to lifecycle semantics, evaluator trust, and Agent Profile metadata without opening a dedicated constitutional lane. No decision-log mutation occurs in Phase 345. No runtime implementation occurs in Phase 345.

## 2. How reputation is derived

Reputation is derived from lifecycle outputs, not from a direct score field.

Reputation is downstream of lifecycle semantics, not a constitutional primitive.

The correct approach is to derive it from graph history rather than store mutable inline node state.

Mutable inline node-level reputation fields remain explicitly forbidden.

Authored payload mutation is barred by CDL-034; reputation cannot be embedded there.

The relevant constitutional anchors remain:
- `docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_evidence_prelock_340_v0.1.md`
- `docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_evidence_prelock_341_v0.1.md`
- `docs/specs/ilc_cdl_038_private_to_public_promotion_and_promotion_receipt_evidence_prelock_344_v0.1.md`
- `docs/specs/ilc_node_schema_concretization_proposals_v0.1.md`
- `docs/specs/ilc_phase_338_347_sequence_lock_v0.1.md`

## 3. Global integrity vs domain-scoped competency

The reputation model must distinguish global integrity from domain-scoped competency.

Global integrity summarizes broad trustworthiness across lifecycle participation, while domain-scoped competency remains contextual to a knowledge area and should not be flattened into a single universal number.

## 4. Agent Profile and derived trust data

`Agent Profile` is the correct publication surface for derived trust summaries.

The implementation direction is to publish derived trust summaries through `Agent Profile` and `Quorum Record-adjacent attestation objects`, not through authored-payload mutation.

Operationally, reputation gates panel eligibility and may weight reviewer selection.

Reputation should influence who gets trusted to evaluate, not what is true.

## 5. Forbidden patterns and boundary constraints

The L-tier ladder should not become a disguised reputation ladder.

The contract must do not lock quorum thresholds for reputation.

The contract must do not treat L-tier quorum levels as reputation tiers.

The contract must do not embed CDL-V3 diversity criteria as implicit reputation defaults.

The contract must do not create a de facto reputation CDL without opening one explicitly.

## 6. CDL decision: does reputation require its own lane in Window 348+?

Reputation adjunct contract is sufficient; no dedicated CDL lane is required in Window 348+.

The reason is that reputation remains an adjoint consequence of already-open lifecycle and envelope work, not an independent constitutional primitive.

## 7. Carry-forward constraints

Phase 346 coherence report must incorporate this adjoint contract verdict.

Phase 346 must preserve the boundary that reputation remains derived, non-inline, and non-constitutional unless a future explicit CDL lane is opened.
