# ILC Phase 456 Fix 10 Pre1 Nonlinear-Control Family Admissibility and Prerequisite Contract v0.1

Status: Phase-456 Fix-10-Pre1 nonlinear-control admissibility and prerequisite contract
Date: 2026-03-26
Owner lane: G8 Constitution Cluster A

## 1. Admissible nonlinear-control candidates

The admissible first nonlinear-control candidates are:

- `nonlinear_curve_k56_g18_f22_frontier_first`
- `nonlinear_curve_k58_g18_f22_frontier_first`
- `nonlinear_curve_k60_g18_f22_frontier_first`

These names are admissible only as nonlinear-control-family candidates and do not authorize execution by themselves.

## 2. Field-composition rule

`mixed_queue_and_production remains the default weak-field challenger for the nonlinear-control lane.`

Legacy production-band carry-forwards are excluded unless a later brief re-admits them explicitly with structural-threshold justification.

The nonlinear-control lane is allowed to define its own frozen field rather than inheriting the oscillator field automatically.

## 3. Implementation exit criteria

A later nonlinear-control implementation phase must establish:

- a runnable nonlinear-control mechanism surface in `simulations/`,
- explicit support for `response_knee`, `control_gain`, `release_floor`, and `bias`,
- deterministic candidate registration for the admissible nonlinear-control family,
- and enough documentation to freeze a brief without hidden widening.

## 4. Brief-freeze prerequisite

A later nonlinear-control brief may freeze candidates only after an implemented nonlinear-control mechanism surface exists in simulations/.

A later nonlinear-control brief must also state the frozen execution field explicitly and must not rely on implicit carry-forward from the legacy production-band family.

## 5. Non-authorization statement

No CDL-050 opening or ratification occurs in Phase 456 Fix 10 Pre1.

This prerequisite contract opens only the nonlinear-control mechanism path. It does not authorize an execution phase yet.
