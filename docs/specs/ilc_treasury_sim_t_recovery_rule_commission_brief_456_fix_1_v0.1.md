# ILC Treasury SIM-T Recovery-Rule Commission Brief 456 Fix 1 v0.1

Status: Phase-456 Fix-1 recovery-rule commission brief
Date: 2026-03-25
Owner lane: G8 Constitution Cluster A

This brief inherits the Phase-453 Scenario-5 measurement discipline and freezes the narrow
recovery-rule carry-forward family for Fix 2. No simulations are executed in Phase 456 Fix 1.

## 1. Recovery-rule subfamily matrix

Registered blocker-coverage objective:

- materially separate the leading recovery-rule candidate on `organic ECU production rate` and
  `P_e clamp-respect rate` under the registered thresholds,
- while preserving duration/cost only as secondary tie-break observables.

Registered subfamilies:

- `Subfamily A - epoch-window variants`
- `Subfamily B - clamp-floor variants`

## 2. Candidate set

Subfamily A - epoch-window variants:

- `production_band_5_epoch`
- `production_band_6_epoch`
- `production_band_7_epoch`
- `production_band_8_epoch`
- `production_band_10_epoch`

Subfamily B - clamp-floor variants:

- `production_band_5_epoch_with_clamp_floor_low`
- `production_band_5_epoch_with_clamp_floor_high`

No additional candidates may be added after Fix 1 is frozen.

## 3. Parameter freeze

The clamp-floor parameters are evidence-motivated from Phase-454 observed operating points:

- `clamp_floor_low=0.87`
- `clamp_floor_high=0.90`

`clamp_floor_low=0.87` matches the Phase-454 `boundary_enforced` clamp-respect operating point
and is the minimum floor value that sits above the registered `5` percentage-point separation
bar against the weakest Scenario-5 challenger.

`clamp_floor_high=0.90` matches the Phase-454 `vesting_50_epoch` and `escrow_10x`
clamp-respect operating points and tests whether a materially stronger clamp gate produces
separation against both Scenario-5 challengers.

These values are evidence-motivated parameters rather than assumed outcomes.

## 4. Success criteria

Primary observables:

- `organic ECU production rate`
- `P_e clamp-respect rate`

Secondary observables:

- `intervention duration`
- `intervention cost`

Success means a leading candidate clears the registered thresholds on the primary observables.

Duration and cost are secondary observables and may break ties only after threshold clearance
is satisfied.

Measured outcomes in Fix 2, not the parameter choices themselves, determine success or failure.

## 5. Discriminating thresholds

The threshold values from Phase 453 remain unchanged.

Registered thresholds:

- clamp-respect separation: at least `5` percentage points,
- organic-production separation: at least `10` percentage points relative difference between
  candidate outcomes.

threshold evaluation must be against the best remaining alternative in the full registered candidate set

No threshold may be lowered in Fix 1 or Fix 2.

## 6. Cross-subfamily reporting rule

If exactly one subfamily produces a threshold-clearing leader, that leader is the Fix-2 recommendation without requiring cross-subfamily tie-break.

Cross-subfamily tie-break applies only when both subfamilies produce threshold-clearing leaders.

Comparative synthesis in Fix 2 must report intra-subfamily ranking before any cross-subfamily
recommendation.

## 7. Ambiguous-outcome policy

If neither subfamily produces a threshold-clearing leader, Blocker 1 remains open.

Ambiguous outcomes preserve the blocker rather than forcing a winner.

No CDL-050 opening or ratification occurs in Phase 456 Fix 1.
