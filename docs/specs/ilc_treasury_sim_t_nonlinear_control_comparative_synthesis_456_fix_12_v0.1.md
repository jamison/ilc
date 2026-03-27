# ILC Treasury SIM-T Nonlinear-Control Comparative Synthesis 456 Fix 12 v0.1

Status: Phase-456 Fix-12 nonlinear-control comparative synthesis
Date: 2026-03-27
Owner lane: G8 Constitution Cluster A

## 1. Evidence base

The evidence base for Fix 12 is `docs/specs/ilc_treasury_sim_t_nonlinear_control_evidence_package_456_fix_12_v0.1.md` plus the raw outputs under `out/treasury_sim/phase_456_fix_12/`.

The frozen field contains four candidates only.

Legacy production-band carry-forwards and oscillator candidates remained outside the Fix 12 field.

## 2. Candidate ranking

Field ranking:

1. `nonlinear_curve_k58_g18_f22_frontier_first`
2. `nonlinear_curve_k56_g18_f22_frontier_first`
3. `nonlinear_curve_k60_g18_f22_frontier_first`
4. `mixed_queue_and_production`

Execution in Fix 12 is limited to the implemented Fix-10 surface and does not add explicit adjacency-state graph simulation.

Fix 12 used only the implemented Fix-10 surface and did not add explicit adjacency-state graph simulation.

## 3. Threshold evaluation

Primary-observable threshold evaluation remains based on absolute percentage-point difference.

The leader must be evaluated against the best remaining alternative in the full candidate field frozen in this brief.

Against `nonlinear_curve_k56_g18_f22_frontier_first`, the leader `nonlinear_curve_k58_g18_f22_frontier_first` separates by:

- `0.2` percentage points on organic ECU production rate (`0.981 - 0.979`),
- `0.1` percentage points on P_e clamp-respect rate (`0.914 - 0.913`).

Duration and cost remain secondary observables after primary-observable threshold clearance.

Those primary-observable gaps do not approach the registered `10` and `5` percentage-point margins.

## 4. Outcome declaration

Outcome catalog:

- `Outcome A - Blocker 1 remains open`
- `Outcome B - Blocker 1 evidence closes`
- `Outcome C - Waggle Dance field remains internally ambiguous`

Selected outcome: `Outcome A - Blocker 1 remains open`

Blocker 1 remains open.

## 5. Non-authorization statement

No CDL-050 opening or ratification occurs in Phase 456 Fix 12.

This execution records evidence only and does not authorize any ratification step by itself.
