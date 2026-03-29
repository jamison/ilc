# ILC Genesis Validator Bootstrap Runtime Part 2 Handoff v0.1

Status: Runtime handoff artifact
Phase: 481
Date: 2026-03-29

## 1. Phase 481 runtime scope summary

Phase 481 completes the genesis validator bootstrap runtime by adding deterministic
admission-control bundle construction and enforcement inside `ilc_core/genesis/`.

The runtime surface introduced in Phase 481 is:
- `build_genesis_admission_control_bundle(enrollment_records, epoch_zero_state) -> dict`
- `verify_admission_control_bundle(bundle) -> None`
- `enforce_genesis_admission(validator_id, bundle) -> bool`

GENESIS_BOOTSTRAP_PART2_VERSION = "genesis_admission_control_bootstrap_481.v0.1"
GENESIS_BOOTSTRAP_PART1_DEPENDENCY = "genesis_validator_bootstrap_runtime_480.v0.1"

## 2. Ratified constitutional anchors

Phase 481 is grounded in the following already-ratified authorities:
- CDL-040 admission-control semantics
- CDL-042 agent-identity derivation
- CDL-051 genesis/finality dependency chain
- Phase 479 genesis validator bootstrap specification
- Phase 480 genesis validator bootstrap runtime Part 1

CDL_040_DEPENDENCY = "cdl_040_ratified_393.v0.1"
CDL_040_DEPENDENCY is declared locally in Phase 481 because no canonical runtime export exists yet.

## 3. Admission-control bundle contract

The admission-control bundle is the deterministic pre-populated validator set used to admit
genesis validators at epoch zero.

The canonical bundle payload contains:
- `enrollment_records`
- `epoch_zero_state`
- `admitted_validator_ids`
- `part1_dependency`

`bundle_integrity_hash` is computed as `sha256` over the deterministically serialized payload.
Enrollment records are normalized and sorted by `validator_id` before hashing. The epoch-zero
state must already satisfy the Phase 480 verification contract.

## 4. Enforcement contract

`enforce_genesis_admission(validator_id, bundle)` returns `True` when `validator_id` belongs to the
admitted validator set carried by the verified bundle. It returns `False` for well-formed but
unenrolled validator ids. It raises `GenesisBootstrapError` for invalid bundle state and for
invalid validator-id inputs.

Validator network join and recovery flow is out of scope for Phase 481.

## 5. Deterministic failure-token catalog

Phase 481 introduces or relies on the following deterministic failure tokens:
- `ADMISSION_BUNDLE_INVALID_ENROLLMENT_RECORDS`
- `ADMISSION_BUNDLE_INVALID_STRUCTURE`
- `ADMISSION_BUNDLE_MISSING_REQUIRED_FIELD`
- `ADMISSION_BUNDLE_INVALID_PART1_DEPENDENCY`
- `ADMISSION_BUNDLE_INVALID_VALIDATOR_SET`
- `ADMISSION_BUNDLE_HASH_MISMATCH`
- `ADMISSION_BUNDLE_NOT_INITIALIZED`
- `ADMISSION_BUNDLE_INVALID_VALIDATOR_ID`
- inherited Phase 480 `GenesisBootstrapError` tokens through enrollment and epoch-state verification

## 6. Non-goals and Phase 482 pointer

No decision-log mutation occurred in Phase 481.
Private key handling remains out of scope.
Validator network join and recovery flow remains deferred beyond this window.
Phase 482 is the next authorized phase.
