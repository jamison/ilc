# ILC Consensus Diversity-Floor Finality Runtime Handoff 470 v0.1

Status: runtime handoff artifact
Date: 2026-03-28
Owner lane: G8 Constitution Cluster A

## 1. Phase 470 runtime scope summary

Phase 470 implements a diversity-aware finality evaluation path for CDL-051 using ratified CDL-V3 constraints.

The new runtime surface evaluates quorum threshold and diversity constraints together when explicit
validator-cluster metadata and explicit diversity policy input are supplied.

## 2. Ratified constitutional anchors

The runtime anchors are:
- CDL-051 ratification for epoch-finality semantics,
- CDL-V3 ratification for cluster diversity floor and concentration ceiling,
- Phase 397 runtime helpers for deterministic diversity-floor computation.

The legacy two-argument evaluate_epoch_finality surface remains available for historical compatibility.

## 3. Diversity-aware finality evaluation contract

The diversity-aware path requires:
- quorum records with `validator_id`,
- explicit `validator_clusters` mapping,
- explicit `diversity_policy` carrying `distinct_cluster_floor` and `max_cluster_share_ceiling`.

One candidate may finalize only if:
- it clears the quorum threshold, and
- it clears both the distinct-cluster floor and max-cluster-share ceiling.

If quorum passes but diversity fails, the runtime returns `insufficient_diversity`.

## 4. Deterministic failure-token catalog

Runtime tokens introduced or consumed in the diversity-aware path:
- `consensus_diversity_finality_validator_id_missing`
- `consensus_diversity_finality_validator_clusters_invalid`
- `consensus_diversity_finality_validator_cluster_missing`
- `consensus_diversity_finality_diversity_policy_invalid`

## 5. Historicalization boundary

Phase 447 assertions that depended on the pre-470 flat evaluator source are historicalized against
the qualifying Phase 447 commit snapshot.

No decision-log mutation occurred in Phase 470.
No CDL-052 runtime implementation occurs in Phase 470.

## 6. Non-goals and Phase 471 pointer

Non-goals in Phase 470:
- no distributed measurement harness,
- no bridge-realism transport exercise,
- no decision-log edits,
- no CDL-051 constitutional amendment.

Phase 471 is the next authorized phase.
