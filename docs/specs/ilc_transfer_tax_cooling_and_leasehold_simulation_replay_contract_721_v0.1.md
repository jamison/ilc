# ILC Transfer Tax Cooling And Leasehold Simulation Replay Contract 721 v0.1

**Phase:** 721  
**Window:** 717-722  
**Date:** 2026-04-18  
**Author:** Codex

## 1. Baseline

Window `717-722` closes the ADR-0015 family at the doctrine / spec level, but
it does not claim simulation or replay outcomes. This artifact commissions the
evidence needed to calibrate the remaining numeric and deferred surfaces.

`simulation_and_replay_commissioning_only`

## 2. Scenario family

The commissioned scenario family covers:

- transfer-tax calibration under low, medium, and high transfer-frequency
  regimes,
- cooling-period challengeability under different epoch-count candidates,
- leasehold duration-class comparison across short, medium, and long lease
  horizons,
- reset-on-transfer versus continuity under repeated node transfer,
- late-economy reversion contribution under multiple reuse-growth profiles.

`transfer_tax_cooling_and_leasehold_questions_commissioned`

## 3. Pass criteria

The commissioned evidence should only count as successful if it can show:

- a transfer-tax candidate range that discourages speculative flipping without
  eliminating legitimate transfer,
- a cooling-period candidate that preserves a meaningful challenge window
  without freezing productive reuse,
- a leasehold candidate that does not collapse reuse incentives,
- explicit rejected candidates and the reason they fail,
- reproducible parameter tables rather than narrative-only conclusions.

## 4. Evidence format

The required evidence format is:

- scenario manifest,
- parameter table,
- replay or simulation procedure,
- output artifact with literal pass / fail rows,
- short summary of accepted, rejected, and still-open candidates.

## 5. Out-of-window results boundary

This window commissions the evidence only. Results are not claimed in Window
`717-722`.

`results_not_claimed_in_window_717_722`
