# ILC Minimal Staking Contract Specification 463 v0.1

Status: completed constitutional surface specification
Date: 2026-03-27
Owner lane: G8 Constitution Cluster A

## 1. Staking obligations for node submission

Submission staking is required for all nodes entering the Popperian evaluation path (Mode 2, triggered by `refutation_criterion` field presence).

When the novelty check fails at submission time:
- stake is returned in full,
- a failed novelty record is added to reputation history,
- the node does not enter the active refutation path.

When a submitted node is successfully challenged post-submission:
- the submission-side stake is partially slashed,
- the slash amount contributes to the reward pool for the successful challenger,
- the submitter's reputation record is updated to reflect the failed claim surface.

## 2. Staking obligations for refutation submission

Refutation staking is required to submit a refutation against a Mode 2 node.

On a failed refutation challenge:
- a portion of stake goes to the defender or challenger-side reward pool,
- the failed challenger receives a negative reputation event,
- the failed refutation is retained as an auditable unsuccessful challenge record.

On a successful refutation:
- reward is earned,
- reward is proportional to the reuse centrality of the refuted node at refutation submission time,
- the exact proportionality coefficients remain deferred.

## 3. Penalty structure

The penalty structure is asymmetric by role:
- failed novelty at node submission is reputationally negative but non-destructive to principal stake,
- successfully challenged submitted nodes incur slash exposure,
- failed refutation challengers incur slash exposure,
- repeated failed participation flows into reputation history and future scrutiny.

## 4. Reward proportionality formula

Refutation reward is a function of the reuse centrality of the refuted node at refutation submission time, not at the original node's creation time.
The exact formula coefficients are TBD.
The constitutional contract fixes the relationship direction and timing reference only.

## 5. Reputation feed-through mechanism

Every staking outcome feeds into persistent reputation history.
Successful novelty-bearing contribution improves standing.
Failed novelty submissions, failed challenges, and successfully challenged submissions produce negative reputation events.
This reputation feed-through is part of the anti-gaming surface and is not optional.

## 6. Parameter deferral and simulation dependency

All numeric staking parameters are TBD pending a future simulation lane.
The parameter calibration path follows the CDL-050 SIM-T precedent: constitutional surface specification first, numeric calibration via simulation evidence in a future dedicated lane.
Staking implementation in ilc_core/ is deferred until after CDL-052 ratification.

## 7. Gate 3 clearance statement

Gate 3 cleared.
No CDL-052 opening occurs in Phase 463.
