# ILC Treasury SIM-T Oscillator Commission Brief 456 Fix 7 v0.1

Status: Phase-456 Fix-7 oscillator commission brief freeze
Date: 2026-03-26
Owner lane: G8 Constitution Cluster A

## 1. Mechanism surface reference

This brief freezes the first oscillator execution field using the implemented mechanism surface in `simulations/sim_treasury_scenario5_oscillator_recovery_rule.py`.

`oscillator_mechanism_status=implemented`

## 2. Fix-8 candidate field

The Fix-8 candidate field is frozen as:

- `oscillating_production_band_short_period`
- `oscillating_production_band_tuned_period`
- `oscillating_production_band_long_period`
- `mixed_queue_and_production`

Fix 8 may execute only the candidate field frozen in this brief.

## 3. Field-composition decision

Legacy production-band carry-forwards remain excluded from the oscillator execution field.

`mixed_queue_and_production` remains the default weak-field challenger for the oscillator lane.

The oscillator field is treated as a materially different mechanism class rather than a continuation of the exhausted production-band family.

## 4. Parameter freeze

Frozen oscillator parameters:

- `oscillating_production_band_short_period` uses `oscillation_period=2`, `oscillation_amplitude=0.04`, `phase_offset=enforce_first`
- `oscillating_production_band_tuned_period` uses `oscillation_period=5`, `oscillation_amplitude=0.09`, `phase_offset=enforce_first`
- `oscillating_production_band_long_period` uses `oscillation_period=8`, `oscillation_amplitude=0.07`, `phase_offset=release_first`
- `mixed_queue_and_production` remains the fixed weak-field challenger

No additional oscillator variants or parameter overrides may be introduced in Fix 8.

## 5. Success criteria and thresholds

Primary-observable threshold evaluation remains based on absolute percentage-point difference.

The lead candidate must clear the registered Phase-453 thresholds against the best remaining alternative in the full candidate field frozen in this brief.

Duration and cost remain secondary observables and may break ties only after primary-observable threshold clearance.

## 6. Non-execution and non-authorization statement

No Scenario-5 execution occurs in Phase 456 Fix 7.

No CDL-050 opening or ratification occurs in Phase 456 Fix 7.
