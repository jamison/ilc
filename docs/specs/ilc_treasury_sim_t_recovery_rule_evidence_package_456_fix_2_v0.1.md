# ILC Treasury SIM-T Recovery-Rule Evidence Package 456 Fix 2 v0.1

Status: Phase-456 Fix-2 recovery-rule evidence package
Date: 2026-03-25
Owner lane: G8 Constitution Cluster A

## 1. Commission brief reference

This evidence package executes the frozen Fix-1 recovery-rule lane defined in:

- `docs/specs/ilc_phase_456_fix_1_recovery_rule_sequence_lock_v0.1.md`
- `docs/specs/ilc_treasury_sim_t_recovery_rule_commission_brief_456_fix_1_v0.1.md`

Scenario 5 only.

No Scenarios 1-4 were executed in Phase 456 Fix 2.

## 2. Scenario 5 candidate families executed

The registered seven-candidate family was executed without widening.

- `Subfamily A - epoch-window variants`
  - `production_band_5_epoch`
  - `production_band_6_epoch`
  - `production_band_7_epoch`
  - `production_band_8_epoch`
  - `production_band_10_epoch`
- `Subfamily B - clamp-floor variants`
  - `production_band_5_epoch_with_clamp_floor_low`
  - `production_band_5_epoch_with_clamp_floor_high`

## 3. Manifest and reproducibility record

Manifest path:

- `out/treasury_sim/phase_456_fix_2/run_manifest.json`

Raw output paths:

- `out/treasury_sim/phase_456_fix_2/scenario_5_results.csv`
- `out/treasury_sim/phase_456_fix_2/scenario_5_results.tsv`
- `out/treasury_sim/phase_456_fix_2/summary_table.md`

Raw outputs are reproducible from the manifests recorded in this artifact.

## 4. Raw output summary

The Fix-2 run preserves a single Scenario 5 field and records exact measurements for the four
registered observables.

| Candidate | Subfamily | organic ECU production rate | P_e clamp-respect rate | intervention duration | intervention cost |
| --- | --- | --- | --- | --- | --- |
| `production_band_5_epoch` | `Subfamily A - epoch-window variants` | `0.91` | `0.86` | `10` | `0.27` |
| `production_band_6_epoch` | `Subfamily A - epoch-window variants` | `0.92` | `0.87` | `11` | `0.29` |
| `production_band_7_epoch` | `Subfamily A - epoch-window variants` | `0.93` | `0.89` | `12` | `0.31` |
| `production_band_8_epoch` | `Subfamily A - epoch-window variants` | `0.92` | `0.90` | `13` | `0.34` |
| `production_band_10_epoch` | `Subfamily A - epoch-window variants` | `0.86` | `0.92` | `15` | `0.39` |
| `production_band_5_epoch_with_clamp_floor_low` | `Subfamily B - clamp-floor variants` | `0.89` | `0.88` | `11` | `0.30` |
| `production_band_5_epoch_with_clamp_floor_high` | `Subfamily B - clamp-floor variants` | `0.84` | `0.90` | `14` | `0.36` |

The Phase-456-Fix-2 comparison uses absolute percentage-point difference, not relative ratio.

## 5. Observable measurements

### Subfamily A - epoch-window variants

| Candidate | organic ECU production rate | P_e clamp-respect rate | intervention duration | intervention cost | Notes |
| --- | --- | --- | --- | --- | --- |
| `production_band_5_epoch` | `0.91` | `0.86` | `10` | `0.27` | Replayed the Phase-454 baseline inside the narrowed Fix-2 field. |
| `production_band_6_epoch` | `0.92` | `0.87` | `11` | `0.29` | Slightly longer confirmation window improves both primary observables modestly. |
| `production_band_7_epoch` | `0.93` | `0.89` | `12` | `0.31` | Best combined balance in the epoch-window family. |
| `production_band_8_epoch` | `0.92` | `0.90` | `13` | `0.34` | Clamp-respect rises further, but organic ECU production rate no longer separates materially. |
| `production_band_10_epoch` | `0.86` | `0.92` | `15` | `0.39` | Strongest clamp-respect in the subfamily, but productive continuation falls back sharply. |

### Subfamily B - clamp-floor variants

| Candidate | organic ECU production rate | P_e clamp-respect rate | intervention duration | intervention cost | Notes |
| --- | --- | --- | --- | --- | --- |
| `production_band_5_epoch_with_clamp_floor_low` | `0.89` | `0.88` | `11` | `0.30` | Low clamp floor improves clamp behavior without overtaking the best epoch-window candidate. |
| `production_band_5_epoch_with_clamp_floor_high` | `0.84` | `0.90` | `14` | `0.36` | High clamp floor reaches the stronger clamp band, but productive continuation degrades materially. |

## 6. Intra-subfamily leaders

Subfamily A leader:

- `production_band_7_epoch`
- strongest combined primary-observable balance inside `Subfamily A - epoch-window variants`
- but only `1` absolute percentage-point above `production_band_8_epoch` on organic ECU production rate
  and `1` absolute percentage-point below `production_band_8_epoch` on `P_e clamp-respect rate`

Subfamily B leader:

- `production_band_5_epoch_with_clamp_floor_low`
- stronger organic ECU production rate than `production_band_5_epoch_with_clamp_floor_high`
- but still below the Subfamily A lead on both primary observables

## 7. Non-authorization statement

No CDL-050 opening or ratification occurs in Phase 456 Fix 2.

CDL-050 remains unopened regardless of Blocker-1 verdict.
