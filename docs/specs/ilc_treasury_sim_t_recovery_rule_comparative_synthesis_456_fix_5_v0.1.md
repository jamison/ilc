# ILC Treasury SIM-T Recovery-Rule Comparative Synthesis 456 Fix 5 v0.1

Status: Phase-456 Fix-5 recovery-rule comparative synthesis
Date: 2026-03-25
Owner lane: G8 Constitution Cluster A

## 1. Evidence base

This synthesis evaluates the frozen four-candidate field from:

- `docs/specs/ilc_treasury_sim_t_recovery_rule_evidence_package_456_fix_5_v0.1.md`
- `docs/specs/ilc_treasury_sim_t_recovery_rule_commission_brief_456_fix_4_v0.1.md`

The frozen field contains four candidates only.

strong production-band carry-forwards remained excluded from Fix 5 execution.

This narrowed field preserves the Fix-4 exclusion boundary rather than restoring the previously removed stronger production-band carry-forwards.

Oscillator candidates remained excluded because oscillator_mechanism_status=stubbed.

## 2. Candidate ranking

1. `production_band_5_epoch_with_clamp_floor_low`
2. `production_band_5_epoch`
3. `production_band_5_epoch_with_clamp_floor_high`
4. `mixed_queue_and_production`

`production_band_5_epoch_with_clamp_floor_low` ranks first because it preserves near-anchor organic performance while improving `P_e clamp-respect rate` more than the continuity anchor without collapsing into the weak-field baseline.

## 3. Threshold evaluation

Threshold evaluation uses absolute percentage-point difference and measures the lead candidate against the best remaining alternative in the full candidate field frozen in this brief.

For `production_band_5_epoch_with_clamp_floor_low`, the best remaining alternative in the full candidate field frozen in this brief is `production_band_5_epoch`.

Against `production_band_5_epoch`, the lead candidate is:

- `-2` absolute percentage points on `organic ECU production rate`
- `+2` absolute percentage points on `P_e clamp-respect rate`

Against `mixed_queue_and_production`, the lead candidate is:

- `+6` absolute percentage points on `organic ECU production rate`
- `+6` absolute percentage points on `P_e clamp-respect rate`

Duration and cost remain secondary observables after primary-observable threshold clearance, so they do not rescue a field that fails the primary thresholds.

## 4. Outcome declaration

Outcome A - Blocker 1 remains open

Blocker 1 remains open.

## 5. Non-authorization statement

No CDL-050 opening or ratification occurs in Phase 456 Fix 5.

This comparative synthesis does not authorize any further recovery-rule widening or automatic replay of previously excluded candidates.
