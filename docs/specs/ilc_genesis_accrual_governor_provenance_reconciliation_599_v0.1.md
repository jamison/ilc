# ILC Genesis Accrual-Governor Provenance Reconciliation 599 v0.1

Status: locked
Date: 2026-04-09
Phase: 599
Owner lane: G8 Genesis carry-forward canon closure

## 1. Accrual-governor closure target

Phase 599 reconciles the Genesis accrual-governor provenance stack so Genesis
ILC generation and accrual semantics no longer depend on scattered analysis
notes, mixed denominator assumptions, or silent carry-forward from pre-lock
artifacts.

This packet closes the constitutional realization surface for the Genesis 5
percent economic tranche without reopening the governance closure from Phase 597,
the freshness closure from Phase 598, or the frozen public/RC boundaries from
Phases 590 and 595.

Required governance tokens:
- `genesis_accrual_governor_provenance_closure_exits_analysis_only_state`
- `genesis_economic_tranche_is_distinct_from_governance_privilege`
- `genesis_5pct_tranche_is_target_plus_cap_not_cap_only`
- `theta_hard_theta_soft_and_allocation_surfaces_must_be_provenance_aligned`
- `historical_8pct_language_is_analysis_only_not_hard_cap_or_target`
- `genesis_fixed_tranche_against_cmax_is_authoritative_realization_surface`
- `issued_to_date_ratio_is_not_authoritative_for_full_tranche_realization`
- `future_genesis_ecu_realization_controller_if_used_must_be_separate_from_natural_centrality_measurement`
- `subsidy_factor_and_multiplier_interactions_must_be_named_for_phase_600_evidence`
- `genesis_generation_and_accrual_language_must_match_ratified_target_plus_cap`
- `phase_599_reconciliation_must_not_reopen_phase_597_598_closures`
- `phase_600_genesis_economics_evidence_must_consume_phase_599_reconciliation`

## 2. Dependency tiers and inherited canon

Minimum dependency bundle carried by this packet:
- `docs/specs/ilc_phase_596_605_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_596_605_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_genesis_governance_dilution_and_brake_semantics_closure_597_v0.1.md`
- `docs/specs/ilc_freshness_gate_provenance_and_genesis_exemption_closure_598_v0.1.md`
- `docs/specs/ilc_genesis_authority_sunset_and_fork_legitimacy_coherence_lock_590_v0.1.md`
- `docs/specs/ilc_genesis_accrual_governor_contract_v0.1.md`
- `docs/specs/ilc_genesis_accrual_reconciliation_8pct_vs_theta_hard_266_v0.1.md`
- `docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.3.md`
- `docs/specs/ilc_phase_305_genesis_accumulation_canonicalization_checklist_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

Tier labels and inherited-boundary rules:
- `docs/specs/ilc_genesis_accrual_governor_contract_v0.1.md` and the
  reconciliation note were supporting context only before this phase and are
  dispositioned here only to the extent explicitly narrowed into ratified
  closure language.
- `docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.3.md` remains
  analysis only and is not self-executing protocol law.
- Phase 597 and Phase 598 are inherited canon for governance/freshness boundaries and must not be reopened by accrual reconciliation.

Inherited canon consumed here:
- `phase_599_accrual_reconciliation_must_consume_phase_598_freshness_closure`
- `no_standing_genesis_governance_bonus_survives_closure`
- `freshness_closure_must_not_reopen_phase_597_governance_rules`
- `genesis_dilution_caps_and_emergency_bounds_not_silent_discretion`

## 3. Ratified issuance and cap surfaces carried into the governor stack

`genesis_economic_tranche_is_distinct_from_governance_privilege`.

`genesis_5pct_tranche_is_target_plus_cap_not_cap_only`.

`theta_hard_theta_soft_and_allocation_surfaces_must_be_provenance_aligned`.

`genesis_fixed_tranche_against_cmax_is_authoritative_realization_surface`.

`issued_to_date_ratio_is_not_authoritative_for_full_tranche_realization`.

`genesis_generation_and_accrual_language_must_match_ratified_target_plus_cap`.

The ratified issuance surfaces carried into this packet are:
- `CDL-026` total supply cap: `C_max = 25,920,000 ILC`,
- `CDL-027` monthly decay schedule with `H = 48`,
- `CDL-029` allocation continuity and `theta_hard = 1 / 20 = 0.05`,
- `CDL-030` ECU clamp continuity,
- `CDL-031` dynamic ranking multiplier policy as an existing adjacent surface,
- founder-cap and fade-out governance constraints already closed outside
  ordinary economic privilege in Phase 597.

The fixed Genesis tranche derived from ratified supply law is:
- `0.05 * C_max = 1,296,000 ILC`.

This phase closes the constitutional surface as follows:
- the Genesis-designated economic tranche is fixed against `C_max`,
- the tranche is target-plus-cap rather than cap-only language,
- governance privilege and economic tranche realization remain distinct
  surfaces,
- governance sunset does not cancel or shrink the tranche,
- issued-to-date share ratio is not the authoritative measurement surface for
  full-tranche realization,
- this phase does not ratify direct Genesis mint as the only permissible
  realization mechanism.

## 4. Contract-versus-analysis provenance reconciliation

`genesis_accrual_governor_provenance_closure_exits_analysis_only_state`.

`historical_8pct_language_is_analysis_only_not_hard_cap_or_target`.

The historical `8%` phrasing is retired as closure-grade law. It remains
analysis-only language tied to earlier exploratory framing and must not be read
as either a hard cap or a realized-target rule after this packet.

The exact reconciliation is:
- `theta_hard = 1 / 20 = 0.05` is the ratified hard bound,
- the Genesis 5 percent tranche is the ratified target-plus-cap economic
  surface,
- the draft governor contract records a current conformance shape using
  `genesis_cumulative_accrual / total_cumulative_issuance`,
- that issued-to-date ratio may remain an implementation-context or sensitivity
  surface, but it is not the authoritative closure surface for full-tranche
  realization after this phase,
- the dynamics analysis remains analysis-only evidence about trajectory
  sensitivity and not self-executing law.

This phase therefore narrows the contract-versus-analysis stack into one
explicit posture: ratified supply law controls the Genesis tranche, historical
analysis cannot override it, and the draft contract is authoritative only where
its contents match the closure language ratified here.

## 5. Open parameter and realization-surface questions

`subsidy_factor_and_multiplier_interactions_must_be_named_for_phase_600_evidence`.

`future_genesis_ecu_realization_controller_if_used_must_be_separate_from_natural_centrality_measurement`.

The authoritative realization surface closes here rather than drifting into
Phase 600:
- the Genesis fixed tranche against `C_max` is authoritative,
- issued-to-date ratio is not authoritative for full-tranche realization,
- Phase 600 must test timing, trajectory, and implementation-aligned
  realization against the fixed-tranche target-plus-cap surface.

The remaining named evidence questions for Phase 600 are:
- whether the current deterministic evidence surface demonstrates full-tranche
  realization under the fixed-tranche closure,
- how subsidy-factor sensitivity affects the timing or path to realization,
- how multiplier interactions from adjacent ranking policy affect the evidence
  surface,
- whether the current draft governor contract or later implementation work must
  be aligned more explicitly with the ratified realization surface.

If a later Genesis-only ECU realization controller is used, this phase closes
its boundary now:
- it is a later implementation surface, not presently ratified active law,
- it must be separate from natural centrality measurement,
- it must not rewrite graph centrality itself,
- it must not be described as direct mint,
- it must exist only to realize the already-ratified tranche rather than to
  redefine that tranche.

## 6. Residual non-closure and explicit defer discipline

This phase closes decisively:
- the constitutional realization surface for the Genesis tranche,
- the rule that the Genesis economic tranche is target-plus-cap rather than
  cap-only,
- the rule that issued-to-date ratio is not authoritative for full-tranche
  realization,
- the retirement of historical `8%` language as closure-grade law.

This phase leaves as supporting context only:
- broader draft-governor or analysis language not explicitly narrowed into the
  closure rules above,
- exploratory trajectory intuition that is not attached to the ratified
  realization surface.

This phase leaves as explicit evidence-dependent follow-on to Phase 600:
- deterministic confirmation or fail-closed non-confirmation of full-tranche
  realization,
- bounded evidence on subsidy-factor sensitivity and multiplier interaction
  effects,
- any implementation-alignment claim that would go beyond the constitutional
  closure completed here.

This phase leaves as explicit later-lane defer only:
- capability-proof disposition to Phase 601,
- Topological Exemption and public tokenomics wording to Phase 602,
- any bounded Genesis-only ECU realization-controller implementation packet to a
  later runtime lane.

No provenance question affecting the constitutional realization surface remains
silently open after this packet.

## 7. Forbidden interpretations and exclusions

The following interpretations are forbidden:
- using historical `8%` language as override of ratified issuance surfaces,
- using historical `8%` language as either hard cap or realized-target law,
- using draft governor-contract language as self-executing law by silence,
- reopening governance-dilution or freshness conclusions already closed in
  Phases 597-598,
- claiming Genesis fade-away semantics are settled when parameter questions
  remain unnamed,
- treating Genesis governance sunset as cancellation or shrinkage of the
  ratified Genesis economic tranche,
- treating cap-only language as equivalent to target-plus-cap closure after this
  phase,
- treating issued-to-date ratio as authoritative for full-tranche realization
  after this phase closes on the fixed-tranche surface,
- treating any future Genesis-only ECU realization controller as if it were
  already-ratified active law in this phase,
- rewriting natural centrality measurement as a hidden tranche controller rather
  than naming a separate bounded policy-control layer.

## 8. Explicit deferrals to later phases

Deferred beyond Phase 599:
- deterministic economics evidence and parameter closure to Phase 600,
- capability-proof disposition to Phase 601,
- Topological Exemption boundary and public tokenomics wording to Phase 602,
- any bounded Genesis-only ECU realization-controller implementation packet to a
  later dedicated runtime lane.

`phase_599_reconciliation_must_not_reopen_phase_597_598_closures`.

`phase_600_genesis_economics_evidence_must_consume_phase_599_reconciliation`.
