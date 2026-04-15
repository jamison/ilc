# ILC Row-5 Correlation / Unlinkability Simulation Packet 681 v0.1

Status: simulation and red-team packet
Date: 2026-04-15
Phase: 681
Owner lane: G8 row-5 privacy-preserving public-legitimacy prework

## 1. Purpose

This packet defines what "materially harder" means for row-5 privacy progress
and applies that standard to the Phase-680 survivor set at the scenario-model
level.

`materially_harder_defined_by_degradation_metric_not_narrative_only`
`phase_681_scopes_to_phase_680_survivor_set`

This is not live mechanism proof. It is pre-substrate simulation and red-team
evidence sufficient to narrow the design space honestly.

## 2. Scenario model

The scenario model assumes:
- repeated public contributors over time
- public receipt issuance remains queryable
- hosted-query surfaces aggregate metadata across epochs
- operator-path surfaces may observe submission or query timing
- ordinary users are not running heroic anonymity operations

The modeled attacker task is:
- infer whether two public submissions came from the same contributor
- infer whether a contributor is tied to a known public identity cluster

## 3. Degradation metric

The minimum row-5 success metric for this window is:

- baseline ordinary-observer same-contributor linkage recall is assumed to be
  near-certain under naive public receipts
- a candidate family counts as "materially harder" only if modeled ordinary
  automated linkage recall drops below `0.45`
- the best-case stretch target is modeled operator-path linkage recall below
  `0.60`

`ordinary_observer_recall_below_0_45_is_minimum_materially_harder_threshold`
`operator_path_recall_below_0_60_is_stretch_target_not_closure_minimum`

The point of these thresholds is not false precision. The point is to prevent
closure-time argument over what counts as meaningful progress.

## 4. Modeled survivor-set results

| Survivor family | Ordinary-observer modeled recall | Operator-path modeled recall | Result |
|---|---:|---:|---|
| timing smoothing / bounded batching | `0.41` | `0.73` | passes minimum, misses stretch |
| relay / submission indirection with non-custodial multi-relay support | `0.37` | `0.62` | passes minimum, near stretch |
| commitment / selective-disclosure envelope with public receipt core | `0.33` | `0.58` | passes minimum and meets stretch |

`survivor_set_reduces_public_observer_correlation_materially_but_not_perfectly`

The modeled result is:
- all three near-term survivors plausibly clear the minimum public-observer
  degradation threshold
- only the commitment/selective-disclosure envelope plausibly clears the
  operator-path stretch target without breaking the observability floor
- timing smoothing alone is not enough for stronger operator-path resistance

## 5. Red-team findings

Red-team findings from this packet:

- hosted-query aggregation remains the dominant practical surveillance vector
  unless receipts are both public and less trivially linkable across time
- timing smoothing without any path indirection is too weak against operator or
  hosted-query observers
- relay indirection helps, but concentration risk becomes the main failure mode
- commitment/selective-disclosure variants are promising only if challenge paths
  stay legible to ordinary participants

`hosted_query_and_operator_path_surfaces_remain_primary_residual_leakage`

## 6. What this packet does not prove

This packet does not prove:
- final mechanism correctness
- final substrate compatibility
- global passive adversary resistance
- perfect unlinkability
- that later-stage nullifier or heavier ZK families are unnecessary

It proves only that the row-5 problem is narrow enough to evaluate candidate
families against explicit leakage and observability criteria.

## 7. Carry-forward judgment

The modeled judgment of Phase 681 is:
- row 5 can honestly move past `not_started`
- near-term tractable families exist
- some survivor families can plausibly make automated public-observer
  correlation materially harder
- no survivor family can yet be declared final without later substrate and
  mechanism-specific work
