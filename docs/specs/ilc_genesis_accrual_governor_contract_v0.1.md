# ILC Genesis Accrual Governor Contract v0.1

Status: Draft
Date: 2026-02-18
Owner lane: G8 Constitution Cluster A

## 1. Purpose

Define a deterministic Genesis accrual governor contract for simulation and policy checks that enforces constitutional cap behavior and taper trajectory constraints.

## 2. Scope

This contract covers:
- policy schema and constant locks,
- share-ratio and taper computation rules,
- trajectory simulation contract,
- fail-closed validation requirements.

This contract does not directly mutate runtime payout allocation semantics.

## 3. Locked Constants

- `theta_hard = 1 / 20 = 0.05`
- `theta_soft = exp(-3) ~= 0.049787068367863944`

These are constitutional constants and must not be replaced by rounded alternates.

## 4. Policy Contract

Required keys:
- `theta_hard: float`
- `theta_soft: float`
- `taper_steepness: float` (`k > 0`)

Rules:
- `theta_hard` must equal `1/20` within strict numeric tolerance.
- `theta_soft` must equal `exp(-3)` within strict numeric tolerance.
- all policy numerics must be finite and non-negative.
- `theta_soft <= theta_hard`.

Default policy:
- `theta_hard = 1/20`
- `theta_soft = exp(-3)`
- `taper_steepness = 40.0`

## 5. Signal Contract

Input fields:
- `genesis_cumulative_accrual`
- `total_cumulative_issuance`

Validation:
- both must be finite and non-negative,
- if `total_cumulative_issuance == 0`, then `genesis_cumulative_accrual` must be `0`,
- `genesis_cumulative_accrual` must not exceed `total_cumulative_issuance`.

Share ratio:
- `r = genesis_cumulative_accrual / total_cumulative_issuance`
- if both numerator and denominator are zero, `r = 0`.

## 6. Taper Function

Locked shape:
- `taper_multiplier(r) = 0` when `r >= theta_hard`.
- otherwise:
  - numerator: `sigmoid(k * (theta_soft - r))`
  - denominator: `sigmoid(k * theta_soft)`
  - `m = clamp(numerator / denominator, 0, 1)`

Properties:
- deterministic and host-independent,
- non-increasing with increasing `r`,
- bounded in `[0, 1]`,
- exact zero at and above hard cap.

## 7. Trajectory Simulation Contract

Simulation input is an ordered cumulative sequence of signal rows.

For each row output:
- `step_index`
- cumulative signal values
- computed `genesis_share_ratio`
- computed `taper_multiplier`
- `cap_blocked` boolean

Monotonic cumulative constraints:
- accrual must be non-decreasing across steps,
- issuance must be non-decreasing across steps,
- implied ratio must be non-decreasing.

## 8. Required Invariants

- Hard-cap invariant: `r >= theta_hard => taper_multiplier == 0`.
- Below-cap invariant: `0 <= r < theta_hard => 0 < taper_multiplier <= 1`.
- Monotonic taper invariant over increasing ratio.
- Deterministic output invariant for repeated simulation runs.

## 9. Non-Goals

- No runtime reward-allocation integration in this phase.
- No changes to Phase 212 refutation-profitability invariant semantics.
- No constitutional decision-log ratification mutation in this phase.
