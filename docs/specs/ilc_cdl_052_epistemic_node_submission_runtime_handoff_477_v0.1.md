# ILC CDL-052 Epistemic Node Submission Runtime Handoff 477 v0.1

Status: runtime handoff
Date: 2026-03-29
Owner lane: G8 Constitution Cluster A

## 1. Phase 477 runtime scope summary

Phase 477 creates the `ilc_core/epistemic/` package and implements the node-submission
envelope validator plus deterministic mode-routing.

## 2. Ratified constitutional anchors

The Phase 477 runtime is anchored to:
- Phase 462 refutation_criterion schema boundary,
- Phase 466 CDL-052 ratification,
- CDL-034 envelope separation,
- existing CDL-V7 Popperian gate runtime.

## 3. Node-submission and mode-routing contract

`route_epistemic_mode(submission)` returns:
- `"mode_1"` when no `refutation_criterion` is present,
- `"mode_2"` when a valid authored-envelope `refutation_criterion` is present,
- `"mode_3_boundary_detected"` when an anomaly signal is present.

`validate_epistemic_node_submission(submission)` validates the envelope and enforces the
Phase 462 collision boundary for `normative: true` plus `refutation_criterion`.

## 4. CDL-V7 Popperian gate integration boundary

Phase 477 imports CDL-V7 Popperian gate from ilc_core.consensus.popperian_gate_runtime.

The Phase 477 runtime delegates claim-form admissibility to the existing CDL-V7 gate and
does not re-implement the Popperian evaluation logic.

## 5. Deterministic failure-token catalog

Failure tokens surfaced by Phase 477:
- `MALFORMED_SUBMISSION`
- `MALFORMED_REFUTATION_CRITERION`
- `NORMATIVE_REFUTATION_COLLISION`
- `AUTHORED_ENVELOPE_VIOLATION`

EPISTEMIC_RUNTIME_PART1_VERSION = "epistemic_node_submission_runtime_477.v0.1"
CDL_052_DEPENDENCY = "cdl_052_ratified_466.v0.1"
Mode 3 execution is not implemented in Phase 477.
No decision-log mutation occurred in Phase 477.

## 6. Non-goals and Phase 478 pointer

Phase 477 does not implement refutation submission handling, novelty-check queries,
reuse-centrality queries, or Mode 3 auditor-review execution.

Phase 478 is the next authorized phase.
