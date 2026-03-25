# ILC Treasury SIM-T Recovery-Rule Comparative Synthesis 456 Fix 2 v0.1

Status: Phase-456 Fix-2 recovery-rule comparative synthesis
Date: 2026-03-25
Owner lane: G8 Constitution Cluster A

## 1. Evidence base

This synthesis uses only the fixed Fix-1 brief and the Scenario 5 raw outputs published in:

- `docs/specs/ilc_treasury_sim_t_recovery_rule_commission_brief_456_fix_1_v0.1.md`
- `docs/specs/ilc_treasury_sim_t_recovery_rule_evidence_package_456_fix_2_v0.1.md`
- `out/treasury_sim/phase_456_fix_2/scenario_5_results.csv`
- `out/treasury_sim/phase_456_fix_2/summary_table.md`

Threshold comparisons use absolute percentage-point difference.

## 2. Subfamily A ranking

`Subfamily A - epoch-window variants`

Ranking:

1. `production_band_7_epoch`
2. `production_band_8_epoch`
3. `production_band_6_epoch`
4. `production_band_5_epoch`
5. `production_band_10_epoch`

`production_band_7_epoch` leads the epoch-window family because it holds the strongest overall
balance between organic ECU production rate and `P_e clamp-respect rate` before duration/cost are
used as tie-breakers.

The lead still fails material separation inside the full field: it exceeds `production_band_8_epoch`
on organic ECU production rate by only `1` absolute percentage-point and trails `production_band_10_epoch`
on `P_e clamp-respect rate` by `3` absolute percentage points.

## 3. Subfamily B ranking

`Subfamily B - clamp-floor variants`

Ranking:

1. `production_band_5_epoch_with_clamp_floor_low`
2. `production_band_5_epoch_with_clamp_floor_high`

`production_band_5_epoch_with_clamp_floor_low` leads the clamp-floor family because it preserves
more organic ECU production rate while still improving clamp behavior over the unfloored `5_epoch`
baseline.

The clamp-floor lead still fails the registered thresholds against the broader field because
`production_band_7_epoch` remains `4` absolute percentage points stronger on organic ECU production
rate while also holding a higher overall balance on the primary observables.

## 4. Cross-subfamily evaluation

Cross-subfamily evaluation is measured against the best remaining alternative in the full registered
candidate set.

If exactly one subfamily produces a threshold-clearing leader, that leader is the Fix-2 recommendation without requiring cross-subfamily tie-break.

That condition is not met here. No candidate clears the registered `10` absolute percentage-point
organic-production threshold and the registered `5` absolute percentage-point clamp-respect threshold
against the best remaining alternative in the full registered candidate set.

Intra-subfamily ranking is therefore reported first, and the cross-subfamily comparison remains a
non-authorizing evidence judgment only.

## 5. Outcome declaration

Outcome A - Blocker 1 remains open

Blocker 1 remains open.

`production_band_7_epoch` is the strongest overall balance candidate, but it does not materially
separate from the field on the registered primary observables.

## 6. Non-authorization statement

No CDL-050 opening or ratification occurs in Phase 456 Fix 2.

CDL-050 remains unopened regardless of Blocker-1 verdict.
