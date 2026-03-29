# ILC CDL-055 Validator Staking and Liveness Enforcement Prelock Hardening 493 v0.1

Status: prelock hardening for an open lane
Date: 2026-03-29
Owner lane: G8 Constitution Cluster A

## 1. Liveness boundary

CDL-055 will govern validator-participation liveness only. It does not repurpose content-claim
orphan timeouts as validator liveness penalties.

## 2. Equivocation boundary

Equivocation is defined as signing conflicting `canonical_block_hash` values for the same epoch.
The full-slash boundary remains pre-ratification only in this phase.

## 3. Re-admission boundary

Re-admission after liveness or equivocation penalties remains a separate boundary and is not ratified in this window.

## 4. Future ratification conditions

CDL-055 remains status: open in Phase 493.
No decision-log mutation occurs in Phase 493.
Phase 494 is the next authorized phase.
