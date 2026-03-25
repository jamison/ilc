# ILC Treasury SIM-T Oscillator Evidence Package 456 Fix 8 v0.1

Status: Phase-456 Fix-8 oscillator evidence package
Date: 2026-03-26
Owner lane: G8 Constitution Cluster A

## 1. Frozen execution field

The frozen execution field for Fix 8 is:

- `oscillating_production_band_short_period`
- `oscillating_production_band_tuned_period`
- `oscillating_production_band_long_period`
- `mixed_queue_and_production`

Legacy production-band carry-forwards remain excluded from the oscillator execution field.

## 2. Raw Scenario-5 measurements

Raw Scenario-5 measurements are preserved in `out/treasury_sim/phase_456_fix_8/scenario_5_results.csv`, `out/treasury_sim/phase_456_fix_8/scenario_5_results.tsv`, and `out/treasury_sim/phase_456_fix_8/summary_table.md`.

| Candidate | organic ECU production rate | P_e clamp-respect rate | intervention duration epochs | intervention cost units |
| --- | --- | --- | --- | --- |
| `oscillating_production_band_short_period` | 0.84 | 0.83 | 8 | 0.24 |
| `oscillating_production_band_tuned_period` | 0.95 | 0.89 | 9 | 0.26 |
| `oscillating_production_band_long_period` | 0.82 | 0.84 | 12 | 0.28 |
| `mixed_queue_and_production` | 0.83 | 0.82 | 7 | 0.22 |

## 3. Intra-field observations

`oscillating_production_band_tuned_period` is the field leader on both primary observables.

`oscillating_production_band_short_period` is the best remaining alternative because it has the strongest non-leader organic rate while preserving materially lower duration and cost than the long-period variant.

## 4. Non-authorization statement

No CDL-050 opening or ratification occurs in Phase 456 Fix 8.

This execution records evidence only and does not authorize any ratification step by itself.
