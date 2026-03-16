# ILC Treasury P_e Stabilization Governance Review 426 v0.1

Status: governance review artifact
Date: 2026-03-16
Owner lane: G8 Constitution Cluster A

## 1. Scope and non-ratifying boundary

Phase 426 is a non-ratifying governance review and does not open, amend, or ratify any CDL row.

This review is parallel to Phase 417 in Window 414-423: it assesses the Treasury P_e branch, publishes a disposition verdict, and does not block Phases 427 or 428 of the independent CDL-049 constitutional track.

## 2. Review corpus and methodology

Review corpus:
- `docs/specs/ilc_sim_008_commissioning_results_406_v0.1.md`
- `docs/specs/ilc_cdl_047_treasury_governance_ratification_evidence_418_v0.1.md`
- `docs/specs/ilc_cdl_030_ecu_price_clamp_candidate_lock_277_pre1_v0.1.md`
- `docs/specs/ilc_phase_424_433_sequence_lock_v0.1.md`

Method:
1. inspect SIM-008 for the exact parameter grid and identify which constants were calibrated,
2. compare those calibrated outputs against the already-ratified CDL-047 treasury framework,
3. distinguish the already-ratified treasury framework constants from the still-open Treasury P_e trigger and limit question,
4. assign the conditional tail slots without compressing constitutional lane discipline.

## 3. SIM-008 P_e calibration basis assessment

SIM-008 does not directly calibrate Treasury P_e trigger or limit constants.

docs/specs/ilc_sim_008_commissioning_results_406_v0.1.md

SIM-008 does directly calibrate the already-ratified Window 414-423 economic constants: `bounty_cap = 0.15 × B_e`, `burn_floor = 0.05`, `velocity_alert_floor = 0.91`, and `ecu_conversion_deadline = 4 issuance epochs`.

The SIM-008 parameter grid includes late-epoch burn ratio, bounty-cap fraction of `B_e`, and ECU mandatory conversion deadline sweeps, but it does not include any Treasury P_e trigger or limit sweep dimensions. That omission means the model does not directly support locking Treasury P_e intervention constants in this window.

## 4. Treasury P_e governance question: trigger and limit constants

The open Treasury P_e governance question is whether a constitutional lane should lock intervention trigger and limit constants for Treasury P_e stabilization beyond the already-ratified framework constants.

CDL-047 ratified the treasury framework constants but explicitly excluded P_e trigger and limit constants.

CDL-030 sets the P_e clamp range [0.75, 1.30] but does not set trigger or limit constants for intervention.

Because the clamp range and the treasury framework are already distinct constitutional surfaces, Treasury P_e stabilization requires either new P_e-specific calibration evidence or an explicit determination that the existing evidence basis is sufficient. Phase 426 finds that the existing evidence basis is not sufficient.

## 5. Disposition verdict and authorized scenario

Phase 426 disposition verdict: SIM-009 is warranted to generate P_e-specific calibration data before locking P_e trigger and limit constants.

Scenario B is therefore the authorized tail path for Window 424-433.

This verdict preserves the already-ratified CDL-047 treasury framework while refusing to over-read SIM-008 beyond the constants it actually calibrated.

## 6. Phase 429-431 forward assignment

Phase 429: SIM-009 commissioning.

Phase 430: SIM-009 results synthesis and P_e stabilization disposition.

Phase 431: P_e constitutional lane carry-forward decision publication.

If the P_e constitutional lane cannot complete within Phases 429-431 without compressing constitutional lane discipline, P_e stabilization carries into Window 434+.

## 7. CDL-049 track independence

The CDL-049 constitutional track is independent of the Treasury P_e branch; Phases 427 and 428 proceed regardless of the Phase 426 verdict.

Phase 426 therefore changes only the conditional Treasury tail assignment. It does not alter the constitutionally obligated CDL-049 lane, its prelock evidence, or its ratification schedule.

## 8. Non-goals and canonical anchors

Non-goals:
- no mutation to `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- no opening of `CDL-050`,
- no commissioning or execution of `SIM-009` in Phase 426,
- no patching of any Phase 424 or Phase 425 artifact,
- no `ilc_core/` runtime mutation.

Canonical anchors:
- `docs/specs/ilc_phase_424_433_sequence_lock_v0.1.md`
- `docs/specs/ilc_sim_008_commissioning_results_406_v0.1.md`
- `docs/specs/ilc_cdl_047_treasury_governance_ratification_evidence_418_v0.1.md`
- `docs/specs/ilc_cdl_030_ecu_price_clamp_candidate_lock_277_pre1_v0.1.md`
- `docs/specs/ilc_cdl_049_bounded_existential_alignment_prelock_hardening_425_v0.1.md`
