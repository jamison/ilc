# ILC Consensus Diversity Measurement Contract 471 v0.1

Status: measurement-contract
Date: 2026-03-28
Owner lane: G8 Constitution Cluster A

## 1. Harness scope

Distributed and degraded-network measurement scoping is complete as of Phase 471.
The Phase 471 harness compares flat and diversity-aware finality evaluation under deterministic scenarios.

## 2. Scenario matrix

The harness covers:
- `local_nominal` - nominal quorum and diversity pass with two-cluster support.
- `degraded_latency` - reduced-slack degraded-delivery proxy where quorum still finalizes but with a delayed minority rival vote.
- `cross_cluster_loss` - quorum survives after losing one cluster, so diversity evaluation runs and the distinct-cluster floor fails.
- `concentration_edge` - quorum survives through one cluster, breaching both the diversity floor and the concentration ceiling.

Each scenario records legacy and diversity-aware outcomes plus timing overhead.
The degraded-latency scenario is a finality-input proxy, not a transport-runtime implementation.

## 3. Report contract

The harness writes:
- `out/consensus_measurement/phase_471_report.json`
- `out/consensus_measurement/phase_471_summary.md`

The report records semantic outcomes, aggregate quorum weights, and timing information for each scenario.

## 4. Non-goals

No decision-log mutation occurred in Phase 471.
This phase does not alter consensus semantics.
It does not run a bridge exercise.
Phase 472 is the next authorized phase.
