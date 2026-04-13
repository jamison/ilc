# ILC Tier-0 Numeric Hardening And Window 631-636 Closure 636 v0.1

Status: hardening gate and closure artifact
Date: 2026-04-13
Phase: 636
Window: 631-636
Owner lane: G8 tier-0 economic numeric determinism strike force

## 1. Gate identity and authority

Phase 636 executes the hardening gate for the bounded Tier-0 exact-numeric
migration authorized by:
- `docs/specs/ilc_phase_631_636_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_064_exact_numeric_representation_ratification_evidence_634_v0.1.md`
- `docs/specs/ilc_tier0_exact_numeric_runtime_migration_635_v0.1.md`

This gate closes Window 631-636 only if the migrated Tier-0 runtime foundation
holds under direct exact-arithmetic, replay-stability, serialization-stability,
and no-tolerance checks.

`tier0_numeric_hardening_gate_636_locked`
`runtime_numeric_hardening_gate_phase_636_executed`

## 2. Tier-0 runtime surface under test

The hardening gate covers the Phase 635 migrated Tier-0 surface:
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

Adjacent bounded hardening fix landed during this gate:
- `ilc_core/ledger/ecu_active_layer_runtime.py`
- `docs/specs/ilc_ecu_active_layer_runtime_and_accounting_spec_628_v0.1.md`

That adjacent fix did not widen runtime authority. It only closed a numeric
ingress defect where a local Decimal parser could admit or mishandle non-finite
values.

## 3. Hardening suite executed

The hardening suite executed:
- `tests/test_tier0_numeric_hardening.py`
- `tests/test_phase_636_tier0_numeric_hardening_and_closure.py`
- `tools/run_window_631_636_numeric_determinism_gate_phase_636.sh`

The gate verified:
- exact arithmetic across migrated balance/stake/reward flows
- replay stability on repeated settlement operations
- canonical decimal-string serialization stability
- absence of float-backed internal Tier-0 accounting in the migrated path
- absence of epsilon/tolerance settlement logic in the migrated correctness path
- non-finite numeric ingress rejection at both the Phase 635 exact-helper
  boundary and the bounded active-layer runtime boundary

`tier0_exact_arithmetic_hardening_pass`
`tier0_no_float_runtime_accounting_confirmed`
`tier0_no_tolerance_settlement_logic_confirmed`

## 4. Findings and fix-loop disposition

Hardening verdict:
- no blocking defects remained in the Phase 635 migrated Tier-0 runtime set
- one bounded adjacent defect was found and fixed during Phase 636

Fix-loop item closed in this phase:
- the bounded ECU active-layer runtime used a local Decimal parser that could
  admit or mishandle non-finite amounts (`NaN`, `Infinity`, signed infinity)
- the runtime now rejects non-finite accrued-ECU ingress with
  `accrued_ecu_cannot_be_non_finite`
- `earmark_propose(...)` now rejects non-finite earmark amounts with
  `invalid_earmark_amount_non_finite`
- Phase 628 runtime tests and the Phase 628 spec gate were updated so this edge
  case remains covered

No broader scope widening was needed. The fix stayed inside numeric validation
and machine-legible failure signaling.

## 5. Closure verdict and carry-forward

Window 631-636 changed the runtime frontier in three ways:
- `CDL-064` is now ratified and consumed
- the bounded Tier-0 economic/staking/settlement runtime foundation is exact
  rather than float-backed
- the exact foundation is now hardened enough for the broader runtime roadmap
  to resume on top of it

Still deferred outside this window:
- shared `ilc_core/types.py` contract widening beyond the bounded Tier-0 target
- lower-risk R3 cleanup outside the migrated strike-force set
- public runtime/interface closure for the MVP touchpoints
- coupling-invariants governance lock and later Option-B graduation blockers

Closure verdict: PASS.

`window_631_636_closure_verdict_pass`
`window_623_plus_may_resume_on_exact_numeric_tier0_foundation`

## 6. Capsule and handoff updates

Phase 636 advances the frontier documents to:
- `docs/specs/ilc_antigravity_context_capsule_v3.5.md`
- `docs/specs/ilc_window_631_636_handoff_636_v0.1.md`

The capsule update records that:
- Window 624-630 remains closed and inherited
- Window 631-636 is now closed as the exact-numeric Tier-0 strike force
- `Option D` remains active
- Window 623+ may now resume on the exact numeric Tier-0 foundation

The handoff records the routing back into the broader runtime roadmap without
claiming Option-B selection or broader wallet/payment widening.
