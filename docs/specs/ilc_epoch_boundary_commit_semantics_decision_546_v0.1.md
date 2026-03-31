# ILC Epoch-Boundary Commit Semantics Decision 546 v0.1

Status: decided
Date: 2026-03-31
Phase: 546
Owner lane: G8 Constitution Cluster A

## 1. Decision scope

This phase selects the accumulation model for `centrality_delta` gossip messages under the
ratified CDL-060 single-hop lane. The decision is limited to write-through versus
epoch-boundary atomic commit semantics. No runtime is implemented in this phase.

## 2. Model A: write-through per message

Write-through applies each received `centrality_delta` message directly to the target node's
centrality score as soon as the message arrives.

Advantages:
- simplest runtime model and lowest implementation complexity
- attribution credits the earliest propagation moment without waiting for epoch closure
- reduced buffering requirements and no per-epoch pending state

CDL-039 exposure:
- repeated small-delta traffic creates a finer-grained timing surface
- even with an opaque channel and bounded fanout, observers get more arrival-time signal
- cluster membership remains non-inferrable only if traffic timing itself is not overfit by adversaries

Failure recovery:
- crash after partial application leaves state in an intermediate condition
- safe recovery requires explicit idempotency or rollback semantics at the message boundary
- repeated replay of already-applied deltas is harder to distinguish from new traffic

## 3. Model B: epoch-boundary atomic commit

Epoch-boundary atomic commit buffers `centrality_delta` messages in memory for the current
validation epoch and commits the buffered deltas atomically at epoch boundary.

Advantages:
- intermediate updates are not materialized into the visible score state
- the observable timing surface is reduced to epoch-boundary intervals rather than per-message events
- this is analogous to deferred materialization / operator fusion: intermediate deltas stay buffered until commit

CDL-039 exposure:
- bounded-fanout opaque-channel gossip still applies
- observers may detect that an epoch-boundary flush occurred, but not the individual arrival sequence inside the epoch
- topological privacy is stronger because message-level timing correlation is removed from the committed state path

Failure recovery:
- if a node crashes mid-epoch, the in-memory buffer for that epoch is lost
- recovery is by re-gossip of the lost epoch's messages or graceful zeroing of that epoch's uncommitted delta set
- this does not require a new CDL-046 scope extension because no node-lifecycle rule changes are introduced

## 4. CDL-039 privacy analysis

Both models preserve the ratified CDL-039 invariants at the transport layer: opaque channel,
bounded fanout, and cluster membership non-inferrable. The difference is the size of the
observable timing surface that remains after those invariants are applied.

Write-through exposes a denser correlation surface because committed score changes track
message arrival cadence. Epoch-boundary atomic commit collapses that cadence into coarse
epoch-boundary commit events and therefore provides the stronger topological privacy posture.

## 5. Failure-recovery analysis

Under CDL-046 timed-out lifecycle context, neither model requires a new node-lifecycle
constitutional lane. Write-through shifts the recovery burden into per-message replay safety.
Epoch-boundary atomic shifts the burden into bounded per-epoch buffer loss handling.

The epoch-boundary atomic path is operationally clearer: a lost in-memory epoch buffer is
either re-gossiped or treated as zero for that epoch without mutating CDL-046 semantics.
No new CDL-046 scope extension is warranted by this decision.

## 6. Selected model and rationale

Selected model: `accumulation_model_epoch_boundary_atomic`

`epoch_boundary_commit_semantics_decision`
`ACCUMULATION_MODEL = "epoch_boundary_atomic"`

Epoch-boundary atomic commit is selected because it provides the stronger CDL-039 privacy
posture while still preserving the ratified single-hop bounded-fanout lane. It removes the
message-level committed timing surface that write-through would expose, which is the more
important concern at this stage than per-message immediacy. The recovery path is also easier
to reason about constitutionally: loss is bounded to a single epoch buffer and does not
require a new CDL-046 extension.

## 7. Phase 548 unblock declaration

`cdl_060_gossip_runtime_design_unblocked`

Phase 548 CDL-060 gossip runtime implementation is authorized.
