# ILC Treasury SIM-T Recovery-Rule Evidence Package 456 Fix 5 v0.1

Status: Phase-456 Fix-5 recovery-rule evidence package
Date: 2026-03-25
Owner lane: G8 Constitution Cluster A

## 1. Commission brief reference

This evidence package executes the frozen Fix-4 recovery-rule field defined in:

- `docs/specs/ilc_treasury_sim_t_recovery_rule_commission_brief_456_fix_4_v0.1.md`

Scenario 5 only.

No Scenarios 1-4 were executed in Phase 456 Fix 5.

## 2. Scenario 5 candidate field executed

The frozen four-candidate field was executed without widening.

- `production_band_5_epoch`
- `production_band_5_epoch_with_clamp_floor_low`
- `production_band_5_epoch_with_clamp_floor_high`
- `mixed_queue_and_production`

strong production-band carry-forwards remained excluded from Fix 5 execution.

Oscillator candidates were not executed because oscillator_mechanism_status=stubbed.

## 3. Manifest and reproducibility record

Manifest path:

- `out/treasury_sim/phase_456_fix_5/run_manifest.json`

Raw output paths:

- `out/treasury_sim/phase_456_fix_5/scenario_5_results.csv`
- `out/treasury_sim/phase_456_fix_5/scenario_5_results.tsv`
- `out/treasury_sim/phase_456_fix_5/summary_table.md`

Raw outputs are reproducible from the manifests recorded in this artifact.

## 4. Raw output summary

| Candidate | organic ECU production rate | P_e clamp-respect rate | intervention duration | intervention cost |
| --- | --- | --- | --- | --- |
| `production_band_5_epoch` | `0.91` | `0.86` | `10` | `0.27` |
| `production_band_5_epoch_with_clamp_floor_low` | `0.89` | `0.88` | `11` | `0.30` |
| `production_band_5_epoch_with_clamp_floor_high` | `0.84` | `0.90` | `14` | `0.36` |
| `mixed_queue_and_production` | `0.83` | `0.82` | `7` | `0.22` |

The Phase-456-Fix-5 comparison uses absolute percentage-point difference, not relative ratio.

## 5. Observable measurements

| Candidate | organic ECU production rate | P_e clamp-respect rate | intervention duration | intervention cost | Notes |
| --- | --- | --- | --- | --- | --- |
| `production_band_5_epoch` | `0.91` | `0.86` | `10` | `0.27` | Continuity anchor retained after strong production-band carry-forwards were removed. |
| `production_band_5_epoch_with_clamp_floor_low` | `0.89` | `0.88` | `11` | `0.30` | Best combined primary-observable balance in the narrowed field, but still below the registered separation thresholds. |
| `production_band_5_epoch_with_clamp_floor_high` | `0.84` | `0.90` | `14` | `0.36` | Clamp-respect rises further, but organic continuation and intervention drag remain weak. |
| `mixed_queue_and_production` | `0.83` | `0.82` | `7` | `0.22` | Weak-field anchor preserved to test whether the narrowed field can materially separate from the original mixed alternative. |

## 6. Field leader

Field leader:

- `production_band_5_epoch_with_clamp_floor_low`
- best combined balance in the frozen four-candidate field on the primary observables
- but still only `2` absolute percentage points above `production_band_5_epoch` on `P_e clamp-respect rate`
  and `6` absolute percentage points above `mixed_queue_and_production` on `organic ECU production rate`

## 7. Non-authorization statement

No CDL-050 opening or ratification occurs in Phase 456 Fix 5.

Fix 5 does not reopen Window 450-459 and does not authorize any further recovery-rule widening by itself.
