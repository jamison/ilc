# ILC Freshness-Gate Contract v0.1

Status: Draft
Date: 2026-02-18
Owner lane: G8 Constitution Cluster A

## 1. Purpose

Define deterministic freshness-gate behavior for node-value scoring so stale non-Genesis claims decay in utility-flow influence without violating constitutional reward invariants.

## 2. Scope

This contract defines:
- freshness policy schema and deterministic defaults,
- age and genesis input contracts,
- function shape and numeric bounds,
- scoring and payout boundary behavior,
- interaction constraints with diversity weighting and refutation-profitability invariants.

This contract does not alter Phase 218 Genesis accrual governor constants (`theta_hard`, `theta_soft`).

## 3. Policy Contract

Required policy keys:
- `decay_lambda: float` (`>= 0`, finite)
- `freshness_floor: float` (`0 < floor <= 1.0`, finite)
- `genesis_exempt: bool`

Default policy:
- `decay_lambda = 0.25`
- `freshness_floor = 0.85`
- `genesis_exempt = true`

Constitutional safety bound:
- `freshness_floor` must be `>= 1 / refutation_multiplier` (plus tolerance), where `refutation_multiplier` is sourced from the reward action-multiplier policy surface.
- This prevents freshness penalties from structurally inverting refutation profitability in matched pairings.

## 4. Input Contract

Freshness input fields:
- `age_epochs: float` (`>= 0`, finite)
- `is_genesis: bool`

Scoring input metadata:
- `age_epochs` and `is_genesis` are explicit in canonical scoring evidence vectors.
- `target_age_epochs` and `target_is_genesis` may be carried on claim/refutation payloads to annotate target-node freshness metadata.

Fail-closed rules:
- negative/non-finite age values are invalid,
- non-boolean genesis markers are invalid.

## 5. Function Shape

Locked shape:

`freshness_gate(age_epochs, is_genesis) = 1.0 if (genesis_exempt and is_genesis) else max(floor, exp(-lambda * age_epochs))`

Properties:
- deterministic and host-independent,
- monotonic non-increasing by age,
- bounded in `[freshness_floor, 1.0]`,
- Genesis exemption keeps axioms at `1.0` regardless of age.

## 6. Boundary Behavior

Scoring boundary (`node_value_kernel`):
- invalid freshness policy or inputs fail closed with explicit contract tokens,
- freshness gate is computed per node evidence row before utility-flow computation.

Payout boundary (`utility_flow_rewards`):
- if freshness was already applied in scoring, payout effective freshness multiplier is `1.0` (no double penalty),
- if legacy payout rows omit freshness metadata, payout falls back to neutral `1.0` and emits a warning.

## 7. Interaction Constraints

Must remain true after freshness integration:
- Phase 212 refutation-profitability invariant,
- Phase 216 reuse-diversity anti-Sybil weighting invariant,
- deterministic replay behavior for node-score output ordering and values.

Required checks include a mixed fixture where refuter freshness is lower than validator freshness under equal pairing conditions, while refuter remains net more profitable.

## 8. Non-Goals

- No Phase 218 governor-trajectory logic changes.
- No additional constitutional ratification state changes in this phase.
