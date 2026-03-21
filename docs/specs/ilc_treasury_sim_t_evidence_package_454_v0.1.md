# ILC Treasury SIM-T Evidence Package 454 v0.1

Status: Phase-454 SIM-T evidence package
Date: 2026-03-21
Owner lane: G8 Constitution Cluster A

## 1. Commission brief reference

This evidence package is produced from the pre-registered SIM-T commission brief:
`docs/specs/ilc_treasury_sim_t_commission_brief_453_v0.1.md`

All scenario families registered in the Phase 453 commission brief were executed.

No scenario families not registered in the Phase 453 commission brief were run.

## 2. Scenario families executed

The following scenario families were executed in Phase 454:
- `Scenario 1 - Escrow multiplier discrimination`
- `Scenario 2 - Vesting lock duration discrimination`
- `Scenario 3 - L1/L2 contagion isolation test`
- `Scenario 4 - Long-tail zero-issuance stress test`
- `Scenario 5 - Recovery criterion exit validation`

Each executed family is traceable to the observable contract frozen in `docs/specs/ilc_treasury_objective_function_and_observables_contract_451_v0.1.md`.

## 3. Manifest and reproducibility record

Raw outputs are reproducible from the manifests recorded in this artifact.

Recorded output package:
- `out/treasury_sim/phase_454/run_manifest.json`
- `out/treasury_sim/phase_454/scenario_results.csv`
- `out/treasury_sim/phase_454/scenario_results.tsv`
- `out/treasury_sim/phase_454/summary_table.md`

The manifest records scenario-family identifiers, seeds, parameter-family selections, observable bindings, and output file hashes for replay and verification.

## 4. Raw output summary

Phase 454 executed 17 concrete runs across the five registered scenario families.

Raw summary signals visible in the package:
- the `5x` escrow candidate is the strongest throughput-preserving escrow setting inside the registered escrow family,
- the `50` additional-epoch vesting candidate delivers the lowest release-shock amplitude inside the vesting family without requiring the longest lock,
- the adopted L1/L2 boundary materially outperforms the partial-leakage and contagion-coupled counterfactuals,
- the `mixed_control` candidate is the strongest zero-issuance stress configuration in the current package,
- the `production_band_5_epoch` recovery rule shows the strongest false-exit resistance among the registered recovery-rule candidates.

Catastrophic cross-layer observations, if present, are recorded as boundary evidence and do not expand CDL-050 normal operating scope.

## 5. Observable measurements

The table below records a representative lead observation for each executed scenario family. Full candidate-by-candidate values remain in the raw output package.

| Scenario family | Lead candidate in raw package | `P_e clamp-respect rate` | `organic ECU production rate` | `productive backlog / queue-clearance behavior` | `release-shock amplitude after time-lock expiry` | `intervention duration and intervention cost` |
| --- | --- | --- | --- | --- | --- | --- |
| `Scenario 1 - Escrow multiplier discrimination` | `escrow_5x` | `0.88` | `0.91` | `0.83` | `0.11` | `7 epochs / 0.22 units` |
| `Scenario 2 - Vesting lock duration discrimination` | `vesting_50_epoch` | `0.90` | `0.84` | `0.73` | `0.09` | `10 epochs / 0.29 units` |
| `Scenario 3 - L1/L2 contagion isolation test` | `boundary_enforced` | `0.87` | `0.89` | `0.80` | `0.10` | `4 epochs / 0.09 units` |
| `Scenario 4 - Long-tail zero-issuance stress test` | `mixed_control` | `0.83` | `0.86` | `0.78` | `0.14` | `10 epochs / 0.28 units` |
| `Scenario 5 - Recovery criterion exit validation` | `production_band_5_epoch` | `0.86` | `0.91` | `0.79` | `0.11` | `10 epochs / 0.27 units` |

Phase 454 records the observable surface only. Comparative ranking and discrimination assessment are deferred to Phase 455.

## 6. Non-authorization statement

No CDL-050 opening or ratification occurs in Phase 454.

Phase 454 publishes evidence only. It does not authorize candidate selection, blocker closure, or Treasury parameter lock-in.
