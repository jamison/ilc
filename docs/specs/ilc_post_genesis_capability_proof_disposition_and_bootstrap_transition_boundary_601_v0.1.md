# ILC Post-Genesis Capability-Proof Disposition and Bootstrap Transition Boundary 601 v0.1

Status: locked
Date: 2026-04-09
Phase: 601
Owner lane: G8 Genesis carry-forward canon closure

## 1. Capability-proof disposition target

Phase 601 dispositions the capability-proof roadmap as an explicit later lane
and makes the Genesis bootstrap-transition boundary explicit.

This packet does not activate capability proofs as current governance,
minting, or public-release law. It states what the future lane is, what any
Genesis bootstrap relation may be, and what this phase refuses to treat as
current law.

Required governance tokens:
- `capability_proof_lane_is_explicit_future_lane_not_current_public_law`
- `capproof_does_not_directly_mint_additional_ilc`
- `genesis_capability_baseline_if_any_must_be_bootstrap_only_and_transitioned`
- `capability_proof_transition_must_end_in_non_privileged_reference_state`
- `snapshot_and_fast_bootstrap_provenance_must_be_explicit_where_relevant`
- `capability_proof_lane_must_not_reopen_585_595_frozen_boundaries`
- `phase_602_public_tokenomics_statement_must_consume_phase_601_capability_boundary`

## 2. Dependency tiers and inherited canon

Minimum dependency bundle carried by this packet:
- `docs/specs/ilc_phase_596_605_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_596_605_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_deterministic_genesis_economics_evidence_and_parameter_closure_600_v0.1.md`
- `docs/specs/ilc_phase_585_genesis_authority_and_sunset_dependency_note_v0.1.md`
- `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md`
- `docs/specs/ilc_post_genesis_capability_proof_activation_sequence_230_239_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

Tier labels and inherited-canon rules:
- `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md` is supporting context until dispositioned here and is not self-executing current law.
- `docs/specs/ilc_post_genesis_capability_proof_activation_sequence_230_239_v0.1.md`
  is historical planning context rather than self-executing current law.
- the 585-595 boundary stack is frozen inherited canon not reopened by this phase.
- Phase 600 remains inherited canon for the fixed Genesis tranche, target-plus-
  cap posture, and bounded evidence state.

Inherited canon consumed here:
- `phase_601_capability_proof_disposition_must_consume_phase_600_parameter_state`
- `capability_proof_lane_must_be_dispositioned_not_implicitly_imported`
- `phase_595_bounded_rc0_1_closure_remains_frozen_input`
- `window_595_plus_is_next_authorized_strategic_boundary`

## 3. Separate-lane disposition and current non-import rule

`capability_proof_lane_is_explicit_future_lane_not_current_public_law`.

`capproof_does_not_directly_mint_additional_ilc`.

This phase dispositions capability proofs as a dedicated later approved post-605 capability-proof activation cluster rather than as current public law.

The separate-lane rules are:
- no current governance, minting, or public-release claim may silently depend
  on capability-proof semantics after this phase,
- capability proofs are not a current public-release requirement by silence,
- capability proofs do not directly mint additional ILC,
- capability-proof planning cannot override the fixed Genesis tranche or the
  economic boundaries already closed in Phase 600,
- the capability-proof lane must not reopen the 585-595 frozen boundaries.

## 4. Genesis bootstrap baseline and transition boundary

`genesis_capability_baseline_if_any_must_be_bootstrap_only_and_transitioned`.

`capability_proof_transition_must_end_in_non_privileged_reference_state`.

If any capability-proof baseline uses Genesis as an initial reference, that
baseline is bootstrap only and must transition away from Genesis.

The transition boundary closed here is:
- any Genesis capability baseline is an epoch-0 or bootstrap-start reference only,
- the capability-proof transition must end in a non-privileged reference state,
- the non-privileged reference state must be rolling, synthetic, or governance-updated rather than permanently Genesis-anchored,
- Genesis bootstrap reference cannot become a standing privilege in governance,
  minting, or public legitimacy.

This phase does not choose the exact later implementation of that non-
privileged reference state. It closes only the rule that permanent Genesis reference status is forbidden.

## 5. Snapshot, fast-bootstrap, and provenance implications

`snapshot_and_fast_bootstrap_provenance_must_be_explicit_where_relevant`.

Where a later capability-proof bootstrap transition depends on inherited
bootstrap state, `CDL-023` snapshot and fast-bootstrap provenance must be made explicit.

The provenance rules closed here are:
- snapshot provenance may matter for transition integrity, with fast-bootstrap provenance carried alongside it,
- that provenance must be explicit where a capability-proof transition depends
  on inherited bootstrap state,
- snapshot provenance does not become a new public-legitimacy shortcut,
- snapshot provenance does not reopen fork legitimacy, Genesis lineage, or
  settlement legitimacy boundaries already frozen elsewhere.

## 6. Residual non-closure and explicit defer discipline

This phase dispositions decisively:
- capability proofs are a separate future lane rather than current public law,
- capability proofs do not directly mint additional ILC,
- any Genesis capability baseline is bootstrap only and must transition into a
  non-privileged reference state,
- snapshot and fast-bootstrap provenance must be explicit where a later
  transition depends on inherited bootstrap state.

This phase leaves as explicit later-lane defer:
- the actual capability-proof runtime lane,
- the exact reference-state implementation for a post-bootstrap capability
  baseline,
- any challenge-pool, AWP/IIH, or QATPS coupling details,
- any implementation-specific validator, scoring, or scheduling behavior.

This phase refuses to settle because it belongs to future capability-proof
implementation work:
- runtime activation semantics,
- reward/scheduling wiring,
- probe contracts,
- any live bootstrap-transition code.

## 7. Forbidden interpretations and exclusions

The following interpretations are forbidden:
- silently importing capability-proof semantics into current governance or
  minting law,
- treating capability proofs as current public-release requirement by silence,
- treating Genesis bootstrap baseline as permanent privileged reference state,
- using capability-proof planning as substitute for explicit Genesis closure
  elsewhere in this window,
- using capability-proof planning to reopen 585-595 frozen boundaries,
- treating snapshot provenance as a new public-legitimacy or minting shortcut,
- treating future capability-proof planning as if it already authorizes runtime
  implementation.

## 8. Explicit deferrals to later phases

Deferred beyond Phase 601:
- Topological Exemption boundary and public tokenomics statement to Phase 602,
- synthesis to Phase 603,
- any actual capability-proof runtime lane to a later approved window.

`phase_602_public_tokenomics_statement_must_consume_phase_601_capability_boundary`.
