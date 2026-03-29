# ILC CDL-052 Epistemic Runtime Part 2 Handoff 478 v0.1

Status: runtime handoff
Date: 2026-03-29
Owner lane: G8 Constitution Cluster A

## 1. Phase 478 runtime scope summary

Phase 478 completes the bounded CDL-052 runtime by adding refutation submission handling,
novelty-check queries, and reuse-centrality queries to `ilc_core/epistemic/`.

## 2. Refutation submission contract

`validate_epistemic_refutation_submission(submission)` validates the refutation envelope.
`process_refutation_submission(...)` records the symbolic stake-action path and reputation
feed-through stub.

EPISTEMIC_RUNTIME_PART2_VERSION = "epistemic_refutation_novelty_reuse_runtime_478.v0.1"
EPISTEMIC_PART1_DEPENDENCY = "epistemic_node_submission_runtime_477.v0.1"
All numeric staking constants are TBD pending a future simulation lane.

## 3. Novelty-check contract

`check_novelty(query)` returns a deterministic `NoveltyCheckResult`.
Known duplicate CIDs return `NOVELTY_CHECK_DUPLICATE`.

## 4. Reuse-centrality query contract

`query_reuse_centrality(query)` returns a deterministic `ReuseCentralityResult`.
Reuse-centrality computation backend is a stub in Phase 478.

## 5. Deferred items and simulation dependency

Deferred items in Phase 478:
- calibrated staking amounts,
- full reuse-centrality computation,
- Mode 3 auditor-review execution,
- downstream simulation calibration.

Mode 3 auditor-review execution is not implemented in Phase 478.
No decision-log mutation occurred in Phase 478.

## 6. Non-goals and Phase 479 pointer

Phase 478 does not implement Mode 3 execution or a non-stub reuse-centrality backend.

Phase 479 is the next authorized phase.
