# ILC Tier-0 Exact Numeric Runtime Migration 635 v0.1

Status: implemented
Date: 2026-04-13
Window: 631-636
Phase: 635
Owner lane: G8 tier-0 economic numeric determinism strike force

## 1. Ratified dependency and migration target

Phase 635 consumes ratified `CDL-064` and implements the selected
`exact-decimal-runtime-contract` across the bounded Tier-0 runtime-critical
economic, ledger, staking, and directly coupled export/validation surface set.

This migration removes float from the internal Tier-0 accounting path for:
- balances
- stake snapshots
- reward totals
- settlement deltas
- RC0.1 economic reward reconciliation
- validator staking/liveness penalty fractions

The migration remains bounded:
- no decision-log mutation
- no wallet widening
- no generalized ECU transfer widening
- no `Option B` or `CDL-062` work

`tier0_exact_numeric_runtime_migration_635_locked`
`cdl_064_dependency_consumed`

## 2. Tier-0 modules migrated

The migrated Tier-0 implementation set for Phase 635 is:
- `ilc_core/ledger/exact_numeric.py`
- `ilc_core/ledger/backend.py`
- `ilc_core/ledger/stake_snapshot.py`
- `ilc_core/ledger/settlement_verification.py`
- `ilc_core/ledger/ledger_export.py`
- `ilc_core/ledger/canon_export.py`
- `ilc_core/ledger/lmdb_backend.py`
- `ilc_core/ledger/persistent_backend.py`
- `ilc_core/rc/economic_cycle_runtime.py`
- `ilc_core/validator/staking_liveness_runtime.py`
- `ilc_core/protocol/event_log.py`
- `ilc_core/protocol/schemas/commit_epoch_event_schema_v0.1.json`
- `tools/query_rc0_1_economic_state.py`
- `tools/check_rc0_1_economic_state.py`
- `tools/testbed/run_economic_negative_path_drills.py`
- `tools/testbed/run_economic_replay_drills.py`

The migrated set covers the highest-load-bearing R1 surface plus the direct
runtime/export/validation companions required to keep persisted RC0.1 economic
state coherent once exact numeric values stop serializing as binary float.

## 3. Exact arithmetic and serialization implementation

Phase 635 implements one exact helper boundary in
`ilc_core/ledger/exact_numeric.py` and routes the migrated Tier-0 surfaces
through it.

Applied runtime rules:
- internal balances, stake amounts, reward totals, and settlement deltas use
  `Decimal`
- reward distribution uses exact `Decimal` share arithmetic
- reward reconciliation uses exact equality instead of epsilon tolerance
- non-finite numeric ingress (`NaN`, `Infinity`, signed infinity) is rejected
  at the exact-helper boundary before runtime/accounting use
- persisted LMDB/file backends store canonical decimal strings for Tier-0
  numeric balances and stake maps
- RC0.1 economic runtime exports canonical decimal strings at machine surfaces
- commit.epoch summary `reward_total` and `stake_total` are emitted as canonical
  decimal strings by the runtime helper

Applied canonical serialization rule from CDL-064:
- exact numeric values serialize as normalized base-10 decimal strings
- no exponent notation
- no negative zero
- no superfluous leading zeros
- trailing fractional zeros stripped
- integral values serialized without a trailing decimal point

Examples now emitted by the migrated runtime:
- `0`
- `0.25`
- `3`
- `4`
- `400`

`tier0_exact_serialization_runtime_applied`

## 4. Removed float/tolerance surfaces

Removed from the migrated Tier-0 accounting path:
- float-backed `ledger.balances` internal state
- float-backed `StakeSnapshot.stakes` and `StakeSnapshot.total_stake`
- epsilon-based settlement verification gates
- `round(..., 12)` replay correctness in RC0.1 economic reward aggregation
- `1e-9` reward-total mismatch tolerance in RC0.1 settlement checks
- float-backed persisted LMDB/file balance and stake snapshot writes
- float-backed validator penalty fraction runtime outputs

The migrated Tier-0 path is therefore exact at the load-bearing balance/stake/
reward/settlement boundary even where bounded compatibility parsing still
accepts legacy numeric ingress on selected validation helpers.

`tier0_internal_float_accounting_removed`
`tier0_tolerance_equality_removed`

## 5. Verification and residual defers

Verification used for Phase 635:
- prompt validation
- Phase 634 ratification test
- targeted Tier-0 runtime/export/RC suites covering ledger backend,
  settlement verification, export, canon export/load, validator runtime,
  persistence, and RC0.1 economic-cycle runtime

Residual defers left outside the bounded migrated set:
- `ilc_core/types.py` remains deferred because widening the shared
  `Node` / `ClaimRecord` numeric contract would spill outside the bounded
  Tier-0 runtime/export strike-force target
- lower-risk R3 canon-export validation companions remain a later cleanup lane
  unless Phase 636 hardening shows they block exact replay
- the bounded ECU active-layer runtime already uses exact internal `Decimal`;
  its public getter return-shape compatibility is not a blocking Tier-0
  settlement correctness issue for this phase

Phase 635 therefore lands the exact runtime foundation needed for Phase 636
hardening without claiming repo-wide float removal.

`tier0_runtime_migration_verification_defined`
`window_631_636_moves_to_numeric_hardening_gate`
