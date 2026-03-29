# ILC Genesis Validator Bootstrap Runtime Handoff 480 v0.1

Status: runtime handoff
Date: 2026-03-29
Owner lane: G8 Constitution Cluster A

## 1. Phase 480 runtime scope summary

Phase 480 extends `ilc_core/genesis/` with enrollment-record tooling and epoch-zero state
materialization.

## 2. Ratified constitutional anchors

Phase 480 is anchored to:
- CDL-051 ratified finality dependency,
- CDL-042 key-derived validator identity,
- the Phase 479 bootstrap specification.

## 3. Enrollment record generation contract

`generate_validator_enrollment_record(...)` produces a deterministic enrollment record.
`verify_genesis_enrollment(enrollment_record)` validates the generated structure.

GENESIS_BOOTSTRAP_VERSION = "genesis_validator_bootstrap_runtime_480.v0.1"
validator_id is computed using the CDL-042 key-derivation method from ilc_core.identity.agent_id_runtime.
CDL_051_RATIFICATION_DEPENDENCY is re-exported from ilc_core.consensus.finality_evaluator.
CDL_042_DEPENDENCY is re-exported from ilc_core.identity.agent_id_runtime.

## 4. Epoch-zero state materialization contract

`materialize_epoch_zero_state(genesis_block_cid, validator_enrollment_records)` produces
the deterministic epoch-zero state.
`verify_epoch_zero_state(epoch_zero_state)` validates the state record.

quorum_record_seed is deterministically derived from genesis_block_cid and validator_set_hash.

## 5. Deterministic failure-token catalog

Failure tokens surfaced by Phase 480:
- `GENESIS_BOOTSTRAP_INVALID_PUBLIC_KEY`
- `GENESIS_BOOTSTRAP_INVALID_CLUSTER_ID`
- `GENESIS_BOOTSTRAP_INVALID_VOTE_WEIGHT`
- `GENESIS_BOOTSTRAP_INVALID_ENROLLED_BY`
- `GENESIS_BOOTSTRAP_MISSING_REQUIRED_FIELD`
- `GENESIS_BOOTSTRAP_INVALID_VALIDATOR_ID`
- `GENESIS_BOOTSTRAP_INVALID_EPOCH_ZERO`
- `GENESIS_BOOTSTRAP_INVALID_EPOCH_STATE`
- `GENESIS_BOOTSTRAP_INVALID_GENESIS_BLOCK`
- `GENESIS_BOOTSTRAP_INVALID_VALIDATOR_SET`

Admission-control enforcement is not implemented in Phase 480.
No decision-log mutation occurred in Phase 480.

## 6. Non-goals and Phase 481 pointer

Phase 480 does not implement admission-control enforcement, validator network join, recovery
flow, or private-key handling.

Phase 481 is the next authorized phase.
