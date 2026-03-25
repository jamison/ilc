# ILC Treasury SIM-T Recovery-Rule Commission Brief 456 Fix 4 v0.1

Status: Phase-456 Fix-4 recovery-rule commission brief freeze
Date: 2026-03-25
Owner lane: G8 Constitution Cluster A

## 1. Mechanism surface reference

This brief freezes the next recovery-rule execution field using the implemented mechanism surface in `simulations/sim_treasury_scenario5_recovery_rule.py`.

Only candidates runnable from the Fix-3 mechanism surface are admissible in Fix 5, and `mixed_queue_and_production` remains available as the fixed weak-field anchor.

## 2. Fix-5 candidate field

The Fix-5 candidate field is frozen as:

- `production_band_5_epoch`
- `production_band_5_epoch_with_clamp_floor_low`
- `production_band_5_epoch_with_clamp_floor_high`
- `mixed_queue_and_production`

Fix 5 may execute only the candidate field frozen in this brief.

## 3. Field-composition decision

Fix 5 field composition decision

`strong production-band carry-forwards are removed from the Fix 5 comparison field.`

Retaining strong production-band carry-forwards may make the 10 percentage-point organic-production threshold structurally unachievable.

The removed carry-forwards are not treated as invalid. They are excluded so Fix 5 can test whether the current mechanism surface yields any threshold-clearing discrimination once the strongest inherited production-band cluster is not automatically the best remaining alternative.

## 4. Oscillator admissibility disposition

`oscillator_mechanism_status=stubbed`

Oscillator candidates are excluded from Fix 5 because oscillator_mechanism_status=stubbed.

Fix 4 records the oscillator disposition only. It does not authorize oscillator execution and does not reinterpret the Fix-3 implementation boundary.

## 5. Parameter freeze

Frozen Fix-5 parameters:

- `production_band_5_epoch` uses `window_epochs=5`
- `production_band_5_epoch_with_clamp_floor_low` uses `window_epochs=5` and `clamp_floor=0.87`
- `production_band_5_epoch_with_clamp_floor_high` uses `window_epochs=5` and `clamp_floor=0.90`
- `mixed_queue_and_production` remains the fixed weak-field anchor

No additional candidates or parameter overrides may be introduced in Fix 5.

## 6. Success criteria and thresholds

Primary-observable threshold evaluation remains based on absolute percentage-point difference.

The lead candidate must clear the registered Phase-453 thresholds against the best remaining alternative in the full candidate field frozen in this brief.

Duration and cost remain secondary observables and may break ties only after primary-observable threshold clearance.

Fix 4 does not reinterpret Window 450-459 as passed, and Fix 4 does not authorize Fix 5 execution by itself.

## 7. Non-execution and non-authorization statement

No Scenario-5 execution occurs in Phase 456 Fix 4.

No CDL-050 opening or ratification occurs in Phase 456 Fix 4.
