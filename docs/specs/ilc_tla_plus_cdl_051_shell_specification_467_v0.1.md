# ILC TLA+ CDL-051 Shell Specification 467 v0.1

Status: specification-shell
Date: 2026-03-27
Owner lane: G8 Constitution Cluster A

## 1. Specification scope

This document defines a TLA+ shell for the ratified CDL-051 consensus and epoch-finality
contract.
This is a specification document only. No ilc_core/ implementation occurs in Phase 467.
CDL-051 semantics are formalized in this TLA+ shell.
CDL-051 is not amended by this specification.

The shell captures the abstract state-machine boundary needed to reason about validator
membership, weighted voting, epoch-record advancement, and finality safety. It does not lock
operator constants and it does not claim that TLC model checking has already been run.

## 2. State variables

The shell defines five state variables and maps each one to CDL-051 constitutional language.

- `validators`: a finite set of validator identities. Type: set-valued state variable. This maps
  to CDL-051's ratified validator-set and quorum-participation semantics.
- `cluster_membership`: a function from validator identity to cluster identifier. Type: total
  function over `validators`. This maps to CDL-051's diversity and cross-cluster participation
  requirements.
- `vote_weights`: a function from validator identity to weight. Type: total function over
  `validators` into numeric weights. This maps to CDL-051's weighted voting and threshold
  participation semantics.
- `epoch_records`: a sequence or mapping of epoch identifiers to finalized epoch-state records.
  Type: epoch-indexed record store. This maps to CDL-051's epoch-state and quorum-record
  constitutional contract.
- `finality_state`: a record describing the current finalized block, justified candidate, and
  quorum status. Type: structured record state variable. This maps to CDL-051's deterministic
  finality and tie-break semantics.

A shell module can therefore be sketched as:

```tla
VARIABLES validators, cluster_membership, vote_weights, epoch_records, finality_state
```

## 3. Safety property

The primary safety invariant is `NoTwoHonestNodesFinalizeDifferentBlocks`.

In shell form, the invariant states that no two honest validators may observe distinct finalized
blocks for the same epoch under the same ratified state-transition history. This maps directly to
CDL-051's finality-integrity claim and deterministic tie-break obligations.

A TLA+ shell would expose this as an invariant over `finality_state`, `epoch_records`, and the
honest-validator subset derived from `validators`.

## 4. Liveness condition

The liveness shell condition states that epochs eventually advance when quorum-participation and
cluster-diversity preconditions are sustained long enough.

This is not a completed proof. It is an informal liveness statement for the shell:
- if quorum remains achievable,
- if cluster diversity remains above the floor,
- if no ratified safety invariant is violated,
then the epoch machine should not remain permanently stuck below the next valid epoch boundary.

## 5. Tunable parameters

The shell leaves the following as operator-tunable TLA+ constants:
- `QUORUM_THRESHOLD`
- `CLUSTER_COUNT`
- `DIVERSITY_FLOOR`
- `VALIDATOR_COUNT`

These remain `CONSTANT` declarations in the TLA+ shell module. They are intentionally left
unlocked so operators can reason about distributed-network evolution without prematurely fixing
values in constitutional text.

A shell header can therefore be sketched as:

```tla
CONSTANTS QUORUM_THRESHOLD, CLUSTER_COUNT, DIVERSITY_FLOOR, VALIDATOR_COUNT
```

## 6. CDL-051 invariant mapping

The CDL-051 to TLA+ shell mapping is:

- validator-set integrity -> `validators`
- cluster diversity obligations -> `cluster_membership` with `DIVERSITY_FLOOR`
- quorum weighting rules -> `vote_weights` with `QUORUM_THRESHOLD`
- epoch-state / quorum-record continuity -> `epoch_records`
- deterministic finality / tie-break rules -> `finality_state`
- finality safety claim -> `NoTwoHonestNodesFinalizeDifferentBlocks`

This shell preserves CDL-051 as the constitutional source of truth and uses TLA+ only as an
abstract formalization layer.

## 7. Limitations and open items

The shell has explicit limits:
- model checking has not yet been performed,
- the liveness proof is informal and not mechanically discharged,
- TLA+ source code is not yet syntax-validated against a TLC checker,
- operator-constant calibration remains future work,
- no ilc_core runtime implementation is included in Phase 467.
