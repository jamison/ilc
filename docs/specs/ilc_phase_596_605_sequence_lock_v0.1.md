# ILC Phase 596-605 Sequence Lock v0.1

Status: locked
Date: 2026-04-09
Phase: 596
Owner lane: G8 Genesis carry-forward canon closure

## 1. Window summary

Window 596-605 is the dedicated Genesis carry-forward closure lane that opens
immediately after the bounded RC0.1 Strike Force phase.

It is not a generic continuation of runtime/testnet work. It exists to close
the remaining Genesis support-canon cluster around governance dilution,
freshness privilege, Genesis ILC generation/accrual semantics,
post-Genesis capability-proof disposition, and the public tokenomics statement,
while preserving the already-frozen public and RC boundaries from Phases
585-595.

Required lock tokens:
- `window_596_605_genesis_carry_forward_primary_gate`
- `phase_595_bounded_rc0_1_closure_remains_frozen_input`
- `window_596_605_closes_remaining_genesis_support_canon`
- `genesis_governance_dilution_must_not_remain_supporting_context_by_silence`
- `freshness_gate_provenance_must_be_dispositioned`
- `genesis_accrual_governor_provenance_must_be_reconciled`
- `genesis_generation_and_fade_away_semantics_must_be_explicit`
- `capability_proof_lane_must_be_dispositioned_not_implicitly_imported`
- `topological_exemption_rationale_boundary_must_be_explicit`
- `tokenomics_public_statement_must_match_ratified_governor_surfaces`
- `window_596_605_preserves_585_595_frozen_public_and_rc_boundaries`
- `no_inbound_payment_ingress_or_harness_drift_inside_genesis_carry_forward_window`

## 2. Hard pass condition

Window 596-605 only passes if all of the following are true:
1. Genesis governance dilution and any bounded brake semantics are explicit at
   the correct canon tier rather than left in supporting context by silence.
2. Freshness-gate provenance and the Genesis exemption posture are explicitly
   dispositioned as ratified closure, evidence-supplemented closure, or named
   later-lane defer.
3. Genesis accrual-governor provenance, denominator semantics, and public
   tokenomics language are reconciled against ratified governor/allocation
   surfaces.
4. Genesis generation/accrual fade-away semantics are stated without relying on
   analysis artifacts by silence.
5. The capability-proof lane is explicitly dispositioned without silent import
   into current governance or minting law.
6. The public/runtime boundaries from Phases 585-595 remain frozen and are not
   reopened by Genesis carry-forward cleanup.
7. The window states exactly what remains deferred after Window 596-605.

`window_596_605_genesis_carry_forward_primary_gate`.
`window_596_605_closes_remaining_genesis_support_canon`.
`genesis_governance_dilution_must_not_remain_supporting_context_by_silence`.
`freshness_gate_provenance_must_be_dispositioned`.
`genesis_accrual_governor_provenance_must_be_reconciled`.
`genesis_generation_and_fade_away_semantics_must_be_explicit`.
`capability_proof_lane_must_be_dispositioned_not_implicitly_imported`.
`tokenomics_public_statement_must_match_ratified_governor_surfaces`.
`window_596_605_preserves_585_595_frozen_public_and_rc_boundaries`.

## 3. Mandatory dependency bundle

Every Phase 596-605 artifact must carry the mandatory dependency bundle from
`docs/specs/ilc_window_596_605_candidate_phase_grouping_v0.1.md`.

Binding references for the window:
- `docs/specs/ilc_window_596_605_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_phase_585_genesis_authority_and_sunset_dependency_note_v0.1.md`
- `docs/specs/ilc_genesis_authority_sunset_and_fork_legitimacy_coherence_lock_590_v0.1.md`
- `docs/specs/ilc_window_585_594_handoff_594_v0.1.md`
- `docs/specs/ilc_rc0_1_strike_force_consolidation_and_runtime_hardening_595_v0.1.md`
- `docs/specs/ilc_integration_coherence_report_593_v0.1.md`
- `docs/adr/ADR_0006_EVE_Canonical_Capsule_Integrity.md`
- `docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md`
- `docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`
- `docs/research/ilc_rc_phase_575_execution_packets_v0.1.md`
- `docs/research/ilc_cryptographic_economic_coupling_memo_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

Minimum decision-log cluster for the window:
- `CDL-001`
- `CDL-003`
- `CDL-004`
- `CDL-013`
- `CDL-019`
- `CDL-022`
- `CDL-023`
- `CDL-026`
- `CDL-027`
- `CDL-029`
- `CDL-030`
- `CDL-031`
- `CDL-045`
- `CDL-V4`
- `CDL-V6`

Supporting context bundle for the window, never equal canon by silence:
- `docs/adr/ADR_0008_Node_Usefulness_vs_Governance_Weight_and_Genesis_Dilution.md`
- `docs/specs/ilc_freshness_gate_contract_v0.1.md`
- `docs/specs/ilc_genesis_accrual_governor_contract_v0.1.md`
- `docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.3.md`
- `docs/specs/ilc_genesis_accrual_reconciliation_8pct_vs_theta_hard_266_v0.1.md`
- `docs/specs/ilc_phase_305_genesis_accumulation_canonicalization_checklist_v0.1.md`
- `docs/specs/ilc_constitutional_context_audit_v0.1.md`
- `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md`
- `docs/specs/ilc_post_genesis_capability_proof_activation_sequence_230_239_v0.1.md`
- `docs/research/ilc_genesis_authority_and_sunset_canon_briefing_v0.1.md`
- `whitepaper/02_design_principles.md`

Supporting context may inform this window only when it is explicitly labeled as
supporting context, analysis only, or unresolved carry-forward. No supporting
context source is equal canon with ratified CDL or accepted ADR surfaces by
silence.

## 4. Pre-lock blockers

The following blockers are mandatory before any Genesis carry-forward execution
lock may pass:
- Phase 590, Phase 594, and Phase 595 are frozen inherited boundaries and must
  be preserved verbatim as inherited law.
- every carry-forward item in this window must end as ratified closure,
  evidence-supplemented closure, or explicit later-lane defer with named
  reason and boundary.
- deterministic evidence is mandatory for any simulation or parameter-closure
  claim.
- no boundary widening into inbound payments, transport/security hardening,
  harness/product work, or hostile-internet admission.
- supporting context may inform the window but may not be treated as equal
  canon by silence.

`phase_595_bounded_rc0_1_closure_remains_frozen_input`.
`window_596_605_preserves_585_595_frozen_public_and_rc_boundaries`.
`no_inbound_payment_ingress_or_harness_drift_inside_genesis_carry_forward_window`.

## 5. Phase table

| Phase | Description | Primary output | Sensitive? |
|---|---|---|---|
| 596 | Window 596-605 sequence lock and dependency freeze | `ilc_phase_596_605_sequence_lock_v0.1.md` | No |
| 597 | Genesis governance dilution and brake-semantics closure | Genesis governance closure artifact | YES |
| 598 | Freshness-gate provenance and Genesis exemption closure | freshness provenance closure artifact | YES |
| 599 | Genesis accrual-governor provenance reconciliation | Genesis accrual reconciliation lock | YES |
| 600 | Deterministic Genesis economics evidence and parameter closure | Genesis economics evidence pack | YES |
| 601 | Post-Genesis capability-proof disposition and bootstrap transition boundary | capability-proof disposition artifact | YES |
| 602 | Topological Exemption boundary and public tokenomics statement | rationale boundary + tokenomics statement | YES |
| 603 | Genesis carry-forward synthesis and readiness-delta addendum | synthesis + readiness-delta addendum | No |
| 604 | Coherence report and capsule v3.2 | report + capsule | No |
| 605 | Window 596-605 closure gate and handoff | gate script + handoff | YES |

## 6. Locked implementation decisions

The following decisions are locked for the full Genesis carry-forward window:
- Window 596-605 is the dedicated Genesis carry-forward closure lane after the
  bounded RC0.1 Strike Force phase.
- the public boundary from Phases 585-594 remains frozen and is not reopened by
  Genesis carry-forward cleanup.
- the Phase 595 bounded RC0.1 runtime/testnet closure remains frozen and is not
  widened by this window.
- Genesis bootstrap specialness remains bootstrap-only and bounded.
- Genesis governance, Genesis centrality/persistence, and Genesis ILC
  generation/accrual language must be made explicit at the correct canon tier.
- capability-proof planning remains a separate lane unless and until explicitly
  dispositioned.
- Topological Exemption remains rationale unless a ratified artifact elevates
  it.
- inbound HTTP machine-payment ingress remains outside this window.

`phase_595_bounded_rc0_1_closure_remains_frozen_input`.
`window_596_605_closes_remaining_genesis_support_canon`.
`genesis_generation_and_fade_away_semantics_must_be_explicit`.
`capability_proof_lane_must_be_dispositioned_not_implicitly_imported`.
`topological_exemption_rationale_boundary_must_be_explicit`.
`tokenomics_public_statement_must_match_ratified_governor_surfaces`.
`window_596_605_preserves_585_595_frozen_public_and_rc_boundaries`.
`no_inbound_payment_ingress_or_harness_drift_inside_genesis_carry_forward_window`.

## 7. Protected boundaries and anti-pattern exclusions

The following exclusions are mandatory for Window 596-605:
- treating supporting-context Genesis artifacts as equal canon.
- reopening the public identity/quorum/settlement/fork boundaries already
  frozen in Phases 587-590.
- reopening the bounded RC0.1 runtime/testnet lane frozen in Phase 595.
- treating Genesis bootstrap necessity as authority for permanent public
  privilege.
- treating whitepaper Topological Exemption language as self-executing law.
- silently importing capability proofs into current governance or minting law.
- pushing inbound HTTP machine-payment ingress, harness/product work, or
  transport/security hardening into this window.

`window_596_605_preserves_585_595_frozen_public_and_rc_boundaries`.
`no_inbound_payment_ingress_or_harness_drift_inside_genesis_carry_forward_window`.
`capability_proof_lane_must_be_dispositioned_not_implicitly_imported`.
`topological_exemption_rationale_boundary_must_be_explicit`.

## 8. Sequence integrity rule

Window 596-605 must execute in this order:
1. Phase 596 sequence lock and dependency freeze.
2. Phase 597 Genesis governance dilution and brake-semantics closure.
3. Phase 598 freshness-gate provenance and Genesis exemption closure.
4. Phase 599 Genesis accrual-governor provenance reconciliation.
5. Phase 600 deterministic Genesis economics evidence and parameter closure.
6. Phase 601 post-Genesis capability-proof disposition and bootstrap transition
   boundary.
7. Phase 602 Topological Exemption boundary and public tokenomics statement.
8. Phase 603 Genesis carry-forward synthesis and readiness-delta addendum.
9. Phase 604 coherence report and capsule v3.2.
10. Phase 605 closure gate and handoff.

This ordering prevents Genesis governance, freshness, accrual, capability-proof,
and tokenomics language from hardening against silent supporting-context
assumptions or from widening back into the already-frozen public and RC lanes.
