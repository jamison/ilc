# ILC Phase 456 Fix 10 Nonlinear-Control Mechanism Surface Attestation v0.1

Status: Phase-456 Fix-10 nonlinear-control mechanism surface attestation
Date: 2026-03-26
Owner lane: G8 Constitution Cluster A

## 1. Implemented module boundary

The nonlinear-control mechanism surface is implemented in `simulations/sim_treasury_scenario5_waggle_dance_recovery_rule.py`.

This implementation is isolated from `ilc_core/` and does not alter the historical oscillator or production-band surfaces.

## 2. Runnable nonlinear-control candidates

The runnable nonlinear-control candidates are:

- `nonlinear_curve_k56_g18_f22_frontier_first`
- `nonlinear_curve_k58_g18_f22_frontier_first`
- `nonlinear_curve_k60_g18_f22_frontier_first`

Each candidate exposes `response_knee`, `control_gain`, `release_floor`, and `bias` through the runnable surface.

## 3. Weak-field challenger and field boundary

`mixed_queue_and_production` remains callable as the default weak-field challenger for the nonlinear-control lane.

Legacy production-band carry-forwards are not automatically included in the nonlinear-control execution field.

## 4. Mechanism status and codename

`waggle_dance_codename=Waggle Dance`

`nonlinear_control_curve`

`nonlinear_control_curve_status=implemented`

Fix 11 may freeze nonlinear-control candidates because nonlinear_control_curve_status=implemented.

## 5. Non-execution and non-authorization statement

No Scenario-5 execution occurs in Phase 456 Fix 10.

No CDL-050 opening or ratification occurs in Phase 456 Fix 10.
