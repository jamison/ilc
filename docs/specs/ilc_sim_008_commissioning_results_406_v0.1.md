# ILC SIM-008 Commissioning Results 406 v0.1

Status: Phase-406 commissioning artifact
Date: 2026-03-13
Owner lane: G8 Constitution Cluster A

## 1. Scope and non-ratifying boundary

Phase 406 commissions `SIM-008` as the late-economy post-issuance transition evidence lane for Window 414+ economic CDL planning.

Modeled outputs are non-ratifying evidence inputs.

## 2. Implemented simulation module and late-economy modeling scope

Implemented modules:
- `simulations/sim_008_post_issuance_transition_406.py`
- `simulations/run_phase_406_sim_008.py`

The model sweeps deterministic scenario combinations for lost-coin attrition, fee-revenue strength, activity index, late-epoch burn ratio, bounty-cap fraction of `B_e`, and ECU mandatory conversion deadline.

SIM-009 remains out-of-scope in Phase 406.

## 3. Parameter grid and issuance-epoch model context

SIM-008 epoch context is issuance_epoch and all late-economy projections are monthly cadence projections.

Parameter grid:
- `lost_coin_rate_annual = [0.01, 0.02, 0.03]`
- `fee_revenue_index = [0.8, 1.0, 1.2]`
- `activity_index = [0.75, 1.0, 1.25]`
- `late_epoch_burn_ratio = [0.00, 0.05, 0.10, 0.15]`
- `bounty_cap_fraction_of_budget = [0.05, 0.10, 0.15, 0.20, 0.25]`
- `ecu_conversion_deadline_epochs = [4, 6, 8, 12]`

## 4. Output artifacts and reproducibility declaration

Published output root:
- `out/simulations/sim_008_post_issuance_transition/results.csv`
- `out/simulations/sim_008_post_issuance_transition/results.tsv`
- `out/simulations/sim_008_post_issuance_transition/summary_table.md`
- `out/simulations/sim_008_post_issuance_transition/requirements_summary.md`
- `out/simulations/sim_008_post_issuance_transition/run_manifest.json`

The runner is deterministic, uses a fixed seed, emits only text artifacts, and reproduces byte-identical outputs on rerun.

## 5. Recommended bounty-cap and ECU-deadline results

SIM-008 recommends a per-epoch bounty issuance cap candidate of 0.15 * B_e for Treasury Governance CDL planning.

SIM-008 recommends an ECU mandatory conversion deadline candidate of 4 issuance epochs for future CDL opening.

These recommendations maximize average policy score across the commissioned scenario grid while keeping treasury drawdown bounded under low-fee cases.

## 6. Recommended burn-floor and velocity-threshold results

SIM-008 recommends a late-economy fee-burn floor candidate of 0.05 and a velocity alert floor candidate of 0.91.

The recommended burn floor preserves a non-zero sink while outperforming zero-burn and high-burn alternatives on combined stability and resilience metrics.

The recommended velocity alert floor is the conservative lower-tail planning threshold from the selected policy lane.

## 7. Carry-forward constraints for Window 414+ economic CDLs

Treasury Governance CDL cluster and ECU mandatory conversion deadline CDL remain deferred to Window 414+; Phase 406 commissions evidence only.

The Treasury Governance CDL cluster should use the bounty-cap recommendation as the initial prelock calibration anchor.

The ECU mandatory conversion deadline CDL should use the deadline recommendation as the initial candidate while preserving later constitutional review.

## 8. Out-of-scope and non-goals

No decision-log mutation occurred. No ilc_core runtime files were changed.

Phase 406 does not open or ratify any economic CDL row.

Phase 406 does not commission SIM-009.
