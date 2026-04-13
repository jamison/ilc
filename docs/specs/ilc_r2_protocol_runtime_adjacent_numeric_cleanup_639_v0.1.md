# ILC R2 Protocol Runtime-Adjacent Numeric Cleanup 639 v0.1

Status: implemented
Date: 2026-04-13
Window: 637-641
Phase: 639
Owner lane: G8 residual exact-numeric cleanup

## 1. Ratified dependency and cleanup target

Phase 639 consumes ratified `CDL-064` and cleans up the remaining
runtime-adjacent `R2` numeric surfaces that could still project float semantics
back into resumed runtime work.

The target is narrow:
- `ilc_core/protocol/event_log.py`
- `ilc_core/ledger/settlement_metrics.py`
- `ilc_core/ledger/ecu_active_layer_runtime.py`

No decision-log mutation occurs in Phase 639. No ADR mutation occurs in
Phase 639.

`r2_protocol_runtime_adjacent_numeric_cleanup_639_locked`
`cdl_064_dependency_consumed_in_phase_639`

## 2. Runtime-adjacent files migrated

The runtime-adjacent files migrated in Phase 639 are:
- `ilc_core/protocol/event_log.py`
- `ilc_core/ledger/settlement_metrics.py`
- `ilc_core/ledger/ecu_active_layer_runtime.py`

Directly coupled tests updated for coherence:
- `tests/test_event_log_validators.py`
- `tests/test_settlement_metrics.py`
- `tests/test_ecu_active_layer_runtime.py`
- `tests/test_ecu_active_layer_runtime_hardening.py`

## 3. Numeric validator and metrics cleanup

Event-log cleanup applied in Phase 639:
- non-commit economic numeric validators for `task_outcome` and
  `epoch_summary` now parse through exact decimal logic rather than float
  checks
- helper constructors for `make_task_outcome_event(...)` and
  `make_epoch_summary_event(...)` no longer expose float-only economic amount
  contracts and now emit canonical decimal strings
- non-finite ingress is rejected where parsing occurs, including `NaN`,
  `Infinity`, and `-Infinity`
- invalid helper-constructor numeric ingress now raises
  `EventLogValidationError` instead of leaking raw `ValueError`

Settlement-metrics cleanup applied in the same phase:
- reward aggregation in `ilc_core/ledger/settlement_metrics.py` no longer uses
  float totals
- aggregate outputs now emit CDL-064 canonical decimal strings for
  `total_rewards_distributed` and `total_rewards_stubbed`

Active-layer compatibility decision in the same phase:
- compatibility getters in `ilc_core/ledger/ecu_active_layer_runtime.py`
  were changed to canonical decimal-string egress for accrued and spendable ECU
- active-layer ingress already rejected non-finite values before this phase and
  remains aligned to that rule

`event_log_non_commit_numeric_validators_cleaned`
`settlement_metrics_float_aggregation_removed`
`active_layer_runtime_compatibility_egress_reviewed`
`non_finite_numeric_boundary_rejection_applied_in_phase_639`

## 4. Compatibility boundary and residual float exposure

The bounded compatibility posture after Phase 639 is:
- touched external economic amount boundaries may still accept legacy float
  ingress for compatibility, but those values are immediately parsed through
  exact decimal conversion and do not remain float contracts
- touched machine-legible outputs now emit canonical decimal strings rather
  than float totals or float compatibility getters
- no touched Phase 639 boundary allows non-finite decimal values to pass after
  parsing

Residual float exposure still left after Phase 639:
- canon-export companion validators and related scalar contracts remain in
  Phase 640
- untouched downstream callers may still treat returned canonical numeric
  strings as display values rather than exact arithmetic inputs until the full
  residual cleanup window closes

## 5. Verification and carry-forward

Verification used for Phase 639:
- prompt validation
- Phase 638 cleanup gate
- direct event-log validator tests
- direct settlement-metrics tests
- direct active-layer runtime and hardening tests
- decision-log no-diff guard

Residual carry-forward after this phase:
- canon-export companion numeric cleanup moves to Phase 640
- final residual float hardening and closure move to Phase 641

`phase_639_verification_defined`
`window_637_641_moves_to_r3_numeric_companion_cleanup`
