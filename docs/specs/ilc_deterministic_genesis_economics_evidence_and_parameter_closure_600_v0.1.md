# ILC Deterministic Genesis Economics Evidence and Parameter Closure 600 v0.1

Status: locked
Date: 2026-04-09
Phase: 600
Owner lane: G8 Genesis carry-forward canon closure

## 1. Evidence closure target

Phase 600 runs a deterministic Genesis-economics evidence pass over the
realization surface ratified in Phase 599 and converts that evidence into
explicit closure, evidence-supplemented closure, or explicit fail-closed/defer
language.

This packet does not invent new tokenomics law. It tests whether the current
replayable evidence surface honestly supports full-tranche realization language
for the fixed Genesis tranche against `C_max`.

Required governance tokens:
- `deterministic_genesis_economics_evidence_required_for_target_plus_cap_confirmation`
- `ratified_realization_surface_must_drive_phase_600_evidence_matrix`
- `full_genesis_5pct_tranche_realization_must_be_tested_against_reproducible_outputs`
- `subsidy_factor_and_multiplier_interactions_must_be_evidence_bounded`
- `genesis_fade_away_language_must_be_backed_by_reproducible_outputs`
- `phase_600_evidence_must_not_outrun_phase_599_reconciliation`
- `phase_600_evidence_outputs_must_be_machine_legible_and_replayable`
- `phase_600_must_not_reopen_phase_599_reconciliation`
- `future_genesis_ecu_realization_controller_if_any_must_remain_separate_from_natural_centrality_measurement`
- `phase_601_capability_proof_disposition_must_consume_phase_600_parameter_state`

Required success marker:
- `phase_600_genesis_economics_parameter_closure_ok`

Required failure tokens carried by the runner/checker surface:
- `phase_600_input_contract_missing`
- `phase_600_deterministic_replay_failed`
- `phase_600_parameter_matrix_incomplete`
- `phase_600_provenance_alignment_missing`
- `phase_600_full_tranche_realization_not_demonstrated`
- `phase_600_unbounded_public_tokenomics_claim`

## 2. Dependency tiers and inherited canon

Minimum dependency bundle carried by this packet:
- `docs/specs/ilc_phase_596_605_sequence_lock_v0.1.md`
- `docs/specs/ilc_genesis_accrual_governor_provenance_reconciliation_599_v0.1.md`
- `docs/specs/ilc_phase_305_genesis_accumulation_canonicalization_checklist_v0.1.md`
- `docs/specs/ilc_genesis_accrual_governor_contract_v0.1.md`
- `docs/specs/ilc_genesis_accrual_reconciliation_8pct_vs_theta_hard_266_v0.1.md`
- `docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.3.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

Tier labels and inherited-canon rules:
- `docs/specs/ilc_genesis_accrual_governor_provenance_reconciliation_599_v0.1.md`
  is inherited canon for the authoritative realization surface and target-plus-cap posture.
- `docs/specs/ilc_phase_305_genesis_accumulation_canonicalization_checklist_v0.1.md`
  remains planning-checklist context rather than a completed canonical evidence package.
- `docs/specs/ilc_genesis_accrual_governor_contract_v0.1.md` remains draft
  conformance context and is authoritative only where its contents match the
  Phase 599 closure language.
- `docs/specs/ilc_genesis_accrual_reconciliation_8pct_vs_theta_hard_266_v0.1.md`
  remains reconciliation context only and cannot override ratified tranche law.
- `docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.3.md` remains
  analysis only and is not self-executing protocol law.

Inherited canon consumed here:
- `phase_600_genesis_economics_evidence_must_consume_phase_599_reconciliation`
- `genesis_fixed_tranche_against_cmax_is_authoritative_realization_surface`
- `issued_to_date_ratio_is_not_authoritative_for_full_tranche_realization`
- `genesis_5pct_tranche_is_target_plus_cap_not_cap_only`
- `genesis_generation_and_fade_away_semantics_must_be_explicit`

## 3. Deterministic evidence matrix and replay contract

`deterministic_genesis_economics_evidence_required_for_target_plus_cap_confirmation`.

`ratified_realization_surface_must_drive_phase_600_evidence_matrix`.

`full_genesis_5pct_tranche_realization_must_be_tested_against_reproducible_outputs`.

`phase_600_evidence_outputs_must_be_machine_legible_and_replayable`.

The deterministic evidence matrix used by this phase is:
- ratified supply cap `C_max = 25,920,000 ILC`,
- fixed Genesis tranche `0.05 * C_max = 1,296,000 ILC`,
- ratified halving schedule `H = 48` with a 480-epoch replay horizon,
- authoritative realization surface `fixed_tranche_against_cmax`,
- authoritative governor mode `theoretical_cap`,
- supporting sensitivity mode `issued_to_date`,
- subsidy-factor sweep `{0.20, 0.30, 0.40}`,
- bounded adjacent multiplier sensitivity `{1.0, 1.2}` for replay context,
- centrality, reputation, and network-growth sweeps copied into the runner as
  deterministic replay inputs rather than prose-only assumptions.

The runner/checker contract for this phase is:
- `tools/run_phase_600_genesis_economics_parameter_closure.py` emits a
  machine-legible manifest plus authoritative and supporting summary JSON files,
- `tools/check_phase_600_genesis_economics_parameter_closure.py` validates the
  manifest shape, replay status, closure decision fields, and bounded public
  statement discipline,
- the manifest records the input-contract hashes, parameter matrix,
  authoritative outputs, closure decisions, and replay-contract hashes,
- any alternative ratio-surface comparisons after Phase 599 are supporting sensitivity context only and not reopened closure candidates,
- any parameter closure claimed by this phase must be attached to reproducible outputs rather than prose alone.

The authoritative outputs produced by this packet are:
- `manifest.json`,
- `authoritative_summary.json`,
- `supporting_sensitivity_summary.json`.

## 4. Parameter-closure findings and authoritative outputs

`subsidy_factor_and_multiplier_interactions_must_be_evidence_bounded`.

`genesis_fade_away_language_must_be_backed_by_reproducible_outputs`.

`phase_600_evidence_must_not_outrun_phase_599_reconciliation`.

`future_genesis_ecu_realization_controller_if_any_must_remain_separate_from_natural_centrality_measurement`.

The deterministic Phase 600 outputs record these findings:
- authoritative `theoretical_cap` replay scenarios: `4,374`,
- full-tranche realization count on the authoritative surface: `4,374 / 4,374`,
- authoritative reach epoch p10 / p50 / p90: `15 / 22 / 42`,
- authoritative final Genesis cumulative p50: `1,296,000 ILC`,
- supporting `issued_to_date` sensitivity scenarios: `4,374`,
- supporting issued-to-date realization count within 480 epochs: `0 / 4,374`,
- supporting issued-to-date final Genesis cumulative p50:
  `1,241,995.6909391996 ILC`.

The authoritative outputs emitted by the runner/checker pair are therefore:
- `phase_600_genesis_economics_parameter_closure_ok`,
- deterministic replay status `passed`,
- authoritative realization surface `fixed_tranche_against_cmax`,
- authoritative mode `theoretical_cap`,
- supporting sensitivity mode `issued_to_date`.

This phase also emits one explicit evidence-limited token:
- `phase_600_parameter_matrix_incomplete`.

That token is emitted because the Phase 305 checklist exists but a completed
Phase 305 canonical output package does not yet exist. This phase therefore
bounds subsidy-factor and adjacent multiplier sensitivity with replayable
outputs, but it does not claim that every longer-horizon timing or implementation
alignment question is canonically closed beyond the emitted evidence.

The future Genesis-only ECU realization-controller boundary remains preserved:
- this packet does not ratify an active controller,
- this packet does not rewrite natural centrality measurement,
- this packet does not describe direct Genesis mint as the controlling mechanism.

## 5. Closure decisions versus evidence-limited deferments

This phase closes decisively on evidence:
- the ratified fixed Genesis tranche against `C_max` is compatible with full-
  tranche realization across the bounded authoritative replay matrix,
- issued-to-date remains non-authoritative for full-tranche realization after
  Phase 599,
- the bounded public statement for this phase may say that Genesis has a fixed
  5 percent tranche and that deterministic Phase 600 evidence demonstrates
  full-tranche realization across the bounded theoretical-cap matrix.

This phase closes only as evidence-supplemented boundary language:
- Genesis fade-away timing is bounded by reproducible outputs but is not elevated
  into standalone public timeline law,
- subsidy-factor sensitivity and adjacent multiplier sensitivity are bounded by
  replayable outputs but do not become ratified runtime constants here,
- implementation-alignment claims remain bounded until a later runtime lane
  explicitly aligns active code and/or a canonical Phase 305 evidence package.

This phase leaves as explicit defer because evidence is insufficient or the question exceeds this packet:
- completion of the Phase 305 canonical output package,
- any Genesis-only ECU realization-controller implementation packet,
- capability-proof disposition to Phase 601,
- public tokenomics wording and Topological Exemption boundary to Phase 602.

No parameter question may remain unnamed after this phase if it continues to
materially affect Genesis fade-away or public tokenomics language. The named
remaining questions are the incomplete Phase 305 output package and any later
implementation-alignment lane; neither silently reopens the authoritative
realization surface fixed in Phase 599.

If the current deterministic evidence surface had failed to demonstrate full-
tranche realization under the ratified realization surface and target-plus-cap
semantics, this phase would have failed closed into an explicit named follow-on obligation rather than softening the semantics by silence. That fail-closed path
remains present in the runner/checker surface even though it was not the
observed result of the emitted authoritative replay.

If a later Genesis-only ECU realization controller is discussed, it remains a
separate future implementation surface rather than an already-ratified active
mechanism.

## 6. Forbidden interpretations and exclusions

The following interpretations are forbidden:
- treating one simulation run as self-executing law without closure
  interpretation,
- using evidence outputs to override ratified CDL surfaces,
- using analysis-only artifacts as substitute for deterministic evidence,
- reopening accrual-governor or parameter reconciliation conclusions already
  closed in Phase 599,
- using evidence outputs to quietly downgrade target-plus-cap semantics back to
  cap-only language,
- using evidence outputs to quietly restore issued-to-date ratio as the
  authoritative full-tranche surface after Phase 599 closed on the fixed
  tranche against `C_max`,
- treating a future Genesis-only ECU realization controller as already-ratified
  law or as if it were the same thing as natural centrality measurement,
- claiming direct Genesis mint or an unratified controller as if it were already
  the active legal realization mechanism,
- letting this phase silently decide capability-proof or public-tokenomics
  wording beyond bounded evidence statements.

## 7. Explicit deferrals to later phases

Deferred beyond Phase 600:
- capability-proof disposition to Phase 601,
- Topological Exemption boundary and public tokenomics statement to Phase 602,
- any Genesis-only ECU realization-controller implementation packet to a later
  dedicated runtime lane,
- any fuller canonicalization lane that completes the Phase 305 checklist and
  runtime-alignment follow-on work.

`phase_601_capability_proof_disposition_must_consume_phase_600_parameter_state`.
