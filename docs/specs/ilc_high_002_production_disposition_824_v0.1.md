# ILC HIGH-002 Production Disposition Record 824 v0.1

**Phase:** 824
**Date:** 2026-04-24
**Status:** bounded production-hardening item

`high_002_disposition_record_published_824`
`high_002_documented_liveness_limitation_not_safety_break`

## 1. Restatement

HIGH-002 is a liveness limitation caused by the all-N aggregate-signature
requirement in the epoch checkpoint path. The prompt names
`ilc_consensus/src/fast_path.rs` as the background file, but the current
repository call site is
`ilc_consensus/src/epoch_settlement.rs` in `EpochSettlementProtocol::process_epoch_checkpoint`.

That function reconstructs public-key references for every validator in the
active `ValidatorSet` and calls:

`fast_aggregate_verify(true, msg, ILC_EPOCH_SIG_DST, pk_refs)`

Because `pk_refs` contains all N validators rather than the actual `2F+1`
signer subset, a checkpoint that should be valid under quorum semantics can
stall if any validator is offline or absent from the aggregate. The observable
failure mode is epoch checkpoint liveness loss, not acceptance of an invalid
checkpoint.

## 2. Safety Argument

This is not a safety break.

The current path still verifies BLS aggregate-signature validity before writing
the epoch record. An offline validator can prevent progress by being required
in the all-N aggregate, but it cannot forge a valid checkpoint, bypass BLS
verification, or cause two valid conflicting checkpoints to be accepted.

The production fix is to carry signer membership with the checkpoint, verify
the signer subset against the active validator set, require the ratified quorum
threshold, and pass only the signer public keys into `fast_aggregate_verify`.

## 3. Testnet Posture

The limitation is acceptable for the current controlled testnet posture:

- 7 agents / 3 machines remain a bounded testnet target,
- Genesis authority is still operative,
- first non-Genesis validator deployment is human-gated,
- validator processes are operator-controlled during drills,
- the failure mode is visible checkpoint stall rather than silent corruption.

This posture does not carry into public RC or independently operated validator
sets without the hardening item below.

## 4. Production-Hardening Entry Conditions

HIGH-002 must be addressed before the first independently operated production
validator set, and no later than the first validator set with `N >= 4` and
fault tolerance `F >= 1`.

The hardening window may open only after:

- first non-Genesis validator deployment has occurred under the human gate,
- the active validator-set operation path is producing real checkpoint traffic,
- a local-reviewer-approved implementation plan or TLA+ extension specifies
  signer-subset semantics,
- tests cover missing-signer liveness without weakening BLS verification.

## 5. Scope Boundary

HIGH-002 hardening is not:

- a CDL mutation,
- a protocol incompatibility with the current controlled testnet,
- a blocker for Window 823-829,
- a blocker for H-013 implementation,
- a blocker for first-validator deployment at controlled testnet scale.

It remains a scheduled production-hardening obligation.
