# ILC Reuse-Diversity Anti-Sybil Contract v0.1

Status: Draft
Date: 2026-02-17
Owner lane: G8 Constitution Cluster A

## 1. Purpose

Define deterministic anti-Sybil reuse-diversity weighting used by node-value scoring and utility-flow payout linkage.

## 2. Scope

This contract covers:
- policy shape and bounds,
- scoring-boundary anti-circumvention rules,
- payout-boundary resilience behavior,
- interaction constraints with the refutation-profitability invariant.

This contract does not alter runtime consensus state transitions.

## 3. Policy Contract

Required keys:
- `min_distinct_agents: int` (>= 1)
- `max_single_agent_share: float` (0, 1]
- `penalty_floor: float` [0, 1]

Additional constitutional bound:
- `penalty_floor` must be >= `1 / 1.2` (plus numeric tolerance) so diversity penalties cannot structurally invert refutation premium.

Default policy:
- `min_distinct_agents = 2`
- `max_single_agent_share = 0.75`
- `penalty_floor = 0.85`

## 4. Metrics Contract

Required metrics:
- `reuse_count`
- `distinct_agent_count`
- `max_agent_reuse_share`

Validation rules:
- `reuse_count >= 0`
- `distinct_agent_count >= 0`
- `max_agent_reuse_share` in `[0, 1]`
- if `reuse_count > 0`, then `distinct_agent_count > 0` (fail-closed provenance requirement)

## 5. Scoring Boundary Behavior

Scoring (`node_value_kernel`) must fail closed when provenance/diversity metrics are missing or inconsistent.

Expected behavior:
- reject with explicit contract token,
- do not fallback to neutral weighting during scoring.

Rationale: avoids bypassing anti-Sybil controls by omitting provenance.

## 6. Payout Boundary Behavior

Payout (`utility_flow_rewards`) uses neutral fallback for missing diversity metadata:
- if diversity metadata is absent in payout row, use `1.0` multiplier and emit warning,
- if row declares diversity already applied in scoring, payout uses effective multiplier `1.0` to avoid double-penalty.

Rationale: preserve settlement resilience while retaining explicit warning signal.

## 7. Refutation Interaction Constraint

Diversity weighting must not invert the constitutional refutation-profitability invariant for a matched pairing.

Required checks:
- phase-212 invariant tests remain green after diversity integration,
- mixed-diversity fixture coverage confirms refuter net reward remains greater than validator net reward for equal pairing conditions.

## 8. Non-Goals

- This contract does not finalize Genesis accrual governor trajectory constants.
- This contract does not ratify additional constitutional decisions.
