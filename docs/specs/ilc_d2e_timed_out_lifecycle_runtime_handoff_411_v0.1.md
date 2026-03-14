# ILC D2e Timed-Out Lifecycle Runtime Handoff 411 v0.1

Status: Phase-411 implementation handoff artifact
Date: 2026-03-14
Owner lane: G8 Constitution Cluster A

## 1. Implementation scope summary

Phase 411 implements the constitutionally locked CDL-046 timed-out lifecycle runtime in `ilc_core/node/`:
- `ilc_core/node/timed_out_lifecycle_runtime_411.py` exports the ratified timeout and recovery constants,
- `is_claim_timed_out()` provides the issuance-epoch timeout check for orphaned claims,
- `get_recovery_policy()` returns the ratified recovery-policy constant,
- `ilc_core/node/__init__.py` now re-exports the new runtime surface without modifying prior node runtime modules.

No decision-log mutation occurred in Phase 411.

## 2. Dependency/version lock section

Version and dependency locks:
- `TIMED_OUT_LIFECYCLE_RUNTIME_VERSION = "timed_out_lifecycle_runtime_411.v0.1"`
- `CDL_046_DEPENDENCY = "cdl_046_ratified_409.v0.1"`
- `LIFECYCLE_BASE_DEPENDENCY = "cdl_035_ratified_350.v0.1"`

Dependency interpretation:
- `CDL_046_DEPENDENCY` binds the runtime to the ratified timed_out amendment.
- `LIFECYCLE_BASE_DEPENDENCY` binds the amendment to the base CDL-035 validation lifecycle runtime that it constitutionally amends.

## 3. CDL-046 ratified constants specification

ORPHAN_TIMEOUT_EPOCHS = 4 and RECOVERY_POLICY = "stake_full_release" are constitutionally locked by CDL-046 ratified in Phase 409.

Operational interpretation:
- timeout context is issuance epochs,
- a claim transitions to `timed_out` when the orphan duration reaches or exceeds four issuance epochs,
- the ratified recovery policy for timed-out claims is `stake_full_release`.

## 4. Deterministic failure-token catalog

Defined failure tokens:
- `cdl_046_current_epoch_invalid` — `current_epoch` is not a non-negative integer,
- `cdl_046_orphaned_since_epoch_invalid` — `orphaned_since_epoch` is not a non-negative integer.

Silent non-error behavior:
- impossible epoch ordering (`orphaned_since_epoch > current_epoch`) is not raised as an error in this runtime,
- the helper returns `False` silently because full lifecycle state-machine validation remains deferred outside this constants-runtime phase.

## 5. CDL-035 amendment boundary statement

timed_out transition semantics remain bounded by CDL-035's attached lifecycle envelope with bounded operational relevance.

Phase 411 implements only the ratified CDL-046 constants-runtime surface. It does not reopen other CDL-035 lifecycle states, does not extend `ALLOWED_LIFECYCLE_STATES`, and does not change verdict-attachment or quarantine behavior in the existing lifecycle runtime.

## 6. Mutation-scope boundary statement

Phase 411 modifies only the authorized node runtime paths:
- `ilc_core/node/timed_out_lifecycle_runtime_411.py`
- `ilc_core/node/__init__.py`

No mutation occurred to:
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- `ilc_core/node/validation_lifecycle_runtime_361.py`,
- any non-node `ilc_core/` package,
- `ilc_core/cli/main.py`.

## 7. Non-goals and carry-forward to Phase 412

Non-goals in Phase 411:
- no CLI integration for D2e-04 identity commands,
- no modification of the base validation lifecycle state machine,
- no wallet-provider backend integration,
- no balance or epoch subsystem work,
- no Window-414+ runtime scope.

D2e Agent SDK CLI integration and Window-414+ runtime work are the authorized next implementation slots.

Canonical anchors:
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_cdl_046_timed_out_amendment_ratification_evidence_409_v0.1.md`
- `docs/specs/ilc_phase_402_413_sequence_lock_v0.1.md`
- `ilc_core/node/validation_lifecycle_runtime_361.py`
- `docs/specs/ilc_d2e_agent_id_runtime_handoff_410_v0.1.md`
