# ILC Treasury SIM-T Nonlinear-Control Evidence Package 456 Fix 12 v0.1

Status: Phase-456 Fix-12 nonlinear-control evidence package
Date: 2026-03-27
Owner lane: G8 Constitution Cluster A

## 1. Commission brief reference

This execution follows `docs/specs/ilc_treasury_sim_t_nonlinear_control_commission_brief_456_fix_11_v0.1.md`.

Scenario 5 only.

No Scenarios 1-4 were executed in Phase 456 Fix 12.

## 2. Scenario 5 candidate field executed

The frozen execution field for Fix 12 is:

- `nonlinear_curve_k56_g18_f22_frontier_first`
- `nonlinear_curve_k58_g18_f22_frontier_first`
- `nonlinear_curve_k60_g18_f22_frontier_first`
- `mixed_queue_and_production`

Legacy production-band carry-forwards and oscillator candidates remained outside the Fix 12 field.

## 3. Manifest and reproducibility record

Raw outputs are reproducible from the manifests recorded in this artifact.

The manifest record is preserved in `out/treasury_sim/phase_456_fix_12/run_manifest.json`.

Execution in Fix 12 is limited to the implemented Fix-10 surface and does not add explicit adjacency-state graph simulation.

## 4. Raw output summary

Raw Scenario-5 measurements are preserved in `out/treasury_sim/phase_456_fix_12/scenario_5_results.csv`, `out/treasury_sim/phase_456_fix_12/scenario_5_results.tsv`, and `out/treasury_sim/phase_456_fix_12/summary_table.md`.

| Candidate | organic ECU production rate | P_e clamp-respect rate | intervention duration epochs | intervention cost units |
| --- | --- | --- | --- | --- |
| `nonlinear_curve_k56_g18_f22_frontier_first` | 0.979 | 0.913 | 9 | 0.247 |
| `nonlinear_curve_k58_g18_f22_frontier_first` | 0.981 | 0.914 | 9 | 0.247 |
| `nonlinear_curve_k60_g18_f22_frontier_first` | 0.979 | 0.913 | 9 | 0.247 |
| `mixed_queue_and_production` | 0.830 | 0.820 | 7 | 0.220 |

## 5. Observable measurements

The observable measurements section records exact values for all four observables for each frozen candidate.

The field exhibits a tight top cluster among the three Waggle Dance candidates.

Primary-observable comparison remains based on absolute percentage-point difference.

## 6. Field leader

Field leader: `nonlinear_curve_k58_g18_f22_frontier_first`

The best remaining alternative is `nonlinear_curve_k56_g18_f22_frontier_first` by deterministic tie-break over `nonlinear_curve_k60_g18_f22_frontier_first`, because both challengers are metrically identical and the lower `response_knee` is selected first.

## 7. Non-authorization statement

No CDL-050 opening or ratification occurs in Phase 456 Fix 12.

This execution records evidence only and does not authorize any ratification step by itself.
