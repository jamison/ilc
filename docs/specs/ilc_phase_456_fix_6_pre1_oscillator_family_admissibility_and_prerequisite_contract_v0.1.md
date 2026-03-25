# ILC Phase 456 Fix 6 Pre1 Oscillator Family Admissibility and Prerequisite Contract v0.1

Status: Phase-456 Fix-6-Pre1 oscillator admissibility and prerequisite contract
Date: 2026-03-26
Owner lane: G8 Constitution Cluster A

## 1. Admissible oscillator candidates

The admissible first oscillator candidates are:

- `oscillating_production_band_short_period`
- `oscillating_production_band_tuned_period`
- `oscillating_production_band_long_period`

These names are admissible only as oscillator-family candidates and do not authorize execution by themselves.

## 2. Field-composition rule

`mixed_queue_and_production remains the default weak-field challenger for the oscillator lane.`

Legacy production-band carry-forwards are excluded unless a later brief re-admits them explicitly with structural-threshold justification.

The oscillator lane is allowed to define its own frozen field rather than inheriting the exhausted Fix-5 field automatically.

## 3. Implementation exit criteria

A later oscillator implementation phase must establish:

- a runnable oscillator mechanism surface in `simulations/`,
- explicit support for `oscillation_period`, `oscillation_amplitude`, and `phase_offset`,
- deterministic candidate registration for the admissible oscillator family,
- and enough documentation to freeze a brief without hidden widening.

## 4. Brief-freeze prerequisite

A later oscillator brief may freeze candidates only after an implemented oscillator mechanism surface exists in simulations/.

A later oscillator brief must also state the frozen execution field explicitly and must not rely on implicit carry-forward from the legacy production-band family.

## 5. Non-authorization statement

No CDL-050 opening or ratification occurs in Phase 456 Fix 6 Pre1.

This prerequisite contract opens only the oscillator mechanism path. It does not authorize an execution phase yet.
