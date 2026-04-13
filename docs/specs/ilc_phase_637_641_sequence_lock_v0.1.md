# ILC Phase 637-641 Sequence Lock v0.1

Status: locked
Date: 2026-04-13
Phase: 637
Owner lane: G8 residual exact-numeric cleanup

## 1. Window identity and authorization basis

Window 637-641 is the bounded residual `R2/R3` numeric cleanup lane. It exists
because Window 631-636 removed the Tier-0 blocker, but left shared contract,
protocol-mapping, runtime-adjacent, and companion export surfaces that can
still leak float semantics back into resumed runtime work.

The authorization basis is explicit and bounded:
- Human direction 2026-04-13: residual `R2/R3` float leakage is treated as a
  bounded corrective lane rather than indefinitely deferred cleanup.
- Window 631-636 closed the Tier-0 blocker and produced a clean exact-numeric
  foundation, but the Phase 632 inventory left residual `R2` and `R3` surfaces.
- `CDL-064` is already ratified, so this lane consumes an existing
  constitutional contract instead of opening a new one.
- Window 623+ remains the broader runtime/interface continuation, so this lane
  is justified only because shared and companion float leakage can silently
  contaminate resumed runtime work.

Required lock tokens:
- `window_637_641_sequence_lock_primary_gate`
- `window_637_641_targets_residual_r2_r3_surfaces_only`
- `cdl_064_consumed_not_reopened_in_window_637_641`
- `types_py_and_protocol_mapper_named_as_primary_r2_targets`
- `window_623_plus_priority_preserved_in_window_637_641`
- `window_637_641_does_not_reopen_constitutional_vehicle`
- `window_637_641_does_not_select_option_b`
- `cdl_062_remains_not_authorized_in_window_637_641`
- `wallet_boundary_576_581_unchanged_in_window_637_641`
- `ecu_ilc_separation_preserved_in_window_637_641`
- `residual_numeric_hardening_gate_required_in_phase_641`

## 2. Residual target surface and hard pass conditions

The bounded residual target surface for Window 637-641 is:
- `ilc_core/types.py`
- `ilc_core/protocol/mapper.py`
- `ilc_core/protocol/event_log.py` (non-commit numeric validators and helper
  constructors only)
- `ilc_core/ledger/settlement_metrics.py`
- `ilc_core/ledger/ecu_active_layer_runtime.py` compatibility getter/egress
  surface
- `ilc_core/ledger/canon_export_validate.py`
- `ilc_core/ledger/canon_export_bundle_validate.py`
- `ilc_core/ledger/canon_export_bundle.py`
- `ilc_core/ledger/canon_export_format.py`
- `ilc_core/ledger/canon_bundle_audit_artifact.py`

The hard pass condition for Window 637-641 is:
1. shared contract float leakage in `types.py` / `mapper.py` is closed
2. runtime-adjacent numeric helpers no longer reintroduce float semantics
3. canon-export companion validators and scalar contracts align with exact
   numeric rules and reject non-finite numeric values at touched boundaries
4. Phase 641 residual numeric hardening gate passes before closure

`window_637_641_sequence_lock_primary_gate`.
`window_637_641_targets_residual_r2_r3_surfaces_only`.
`types_py_and_protocol_mapper_named_as_primary_r2_targets`.
`residual_numeric_hardening_gate_required_in_phase_641`.

## 3. AG-gate design basis

The AG-gate artifact remains a planning design filter rather than repo-wide
ratified law. For this window, AG-5 and AG-7 are the most load-bearing:
shared contract and export coherence must stop varying by harness, and the
machine-legible exact-numeric contract must stay consistent with CDL-064.
No window-level AG-gate assessment is a FAIL.

| Gate | Assessment | Notes |
|---|---|---|
| AG-1 Co-flourishing mission | advance | Closing residual numeric leakage protects both human and agent participants from inconsistent runtime contracts. |
| AG-2 W_e increase | neutral | This lane is enabling cleanup rather than direct productivity expansion. |
| AG-3 Epistemic integrity | pass | No Popperian bypass or settled-graph mutability is introduced. |
| AG-4 ECU-ILC separation | pass | The lane tightens numeric contract coherence without collapsing ECU into ILC. |
| AG-5 Harness-agnostic | advance | Shared types, mappers, and companion validators stop leaking harness-specific float assumptions. |
| AG-6 Near-infinite scale | pass | Exact shared contracts reduce replay and export drift at scale. |
| AG-7 Machine-legible first | advance | Canonical decimal-string machine surfaces become more coherent across the residual boundary. |
| AG-8 Outbound economic loop | neutral | The bounded economic loop remains active context, but this lane only hardens its residual numeric contracts. |

## 4. CDL-064 consumption boundary

`cdl_064_consumed_not_reopened_in_window_637_641`.
`window_637_641_does_not_reopen_constitutional_vehicle`.

`CDL-064` is already ratified and is only being consumed in Window 637-641.
No new CDL or ADR opening is authorized in this window. This lane is implementation and hardening only.

Window 637-641 therefore does not:
- reopen the decision log,
- modify ADR-0028,
- widen wallet or payment scope,
- open `CDL-062`,
- or make any `Option B` selection claim.

## 5. Inherited boundary state

The following inherited boundaries remain unchanged in Window 637-641:
- the Phase 576 and Phase 581 read-only wallet boundary remains frozen;
  `wallet_boundary_576_581_unchanged_in_window_637_641`
- the Phase 609 ECU / ILC / runtime layer separation remains controlling canon;
  `ecu_ilc_separation_preserved_in_window_637_641`
- ADR-0028 keeps `Option D` active;
  `window_637_641_does_not_select_option_b`
- `CDL-062` remains unopened;
  `cdl_062_remains_not_authorized_in_window_637_641`
- Window 631-636 remains the immediately preceding corrective lane whose exact
  numeric foundation is inherited, not reopened

## 6. Per-phase scope constraints

| Phase | In scope | Out of scope | Hard constraint |
|---|---|---|---|
| 637 | Sequence lock, target surface, AG-gate table, CDL-064 consumption boundary, inherited-state routing | Decision-log mutation, ADR mutation, `ilc_core/` mutation | The lock must keep the lane bounded to residual `R2/R3` surfaces and require hardening before closure. |
| 638 | Shared contract cleanup in `types.py` and `mapper.py`, direct tests/helpers | Decision-log mutation, ADR mutation, event-log helper cleanup, companion cleanup | Shared exact numeric fields must stop leaking float and mapped machine surfaces must follow CDL-064 canonical decimal strings. |
| 639 | Runtime-adjacent cleanup in `event_log.py`, `settlement_metrics.py`, and active-layer compatibility egress | Commit-epoch validator reopening, companion cleanup | Non-commit numeric validators and helper constructors must stop exposing float-only contracts and reject non-finite numeric ingress where touched. |
| 640 | Canon-export companion scalar/validator cleanup | Further shared contract changes, repo-wide export cleanup | Companion validators and scalar contracts must align with exact-numeric decimal-string rules and non-finite rejection. |
| 641 | Residual hardening gate, capsule, handoff, closure | Reopening constitutional scope, runtime widening beyond CDL-064 | Closure may claim success only if residual float leakage is closed and non-finite rejection hardening passes. |

## 7. Window-level routing and exclusions

The following exclusions are mandatory for every Window 637-641 phase:
- No decision-log mutation.
- No ADR mutation.
- No new constitutional vehicle opening.
- No `CDL-062` opening; `cdl_062_remains_not_authorized_in_window_637_641`.
- No `Option B` selection claim; `window_637_641_does_not_select_option_b`.
- No wallet-write widening or ILC transferability.
- No repo-wide simulation or analytics float cleanup.

Window 623+ remains the broader runtime/interface continuation:
`window_623_plus_priority_preserved_in_window_637_641`.

This residual lane may run before or directly alongside early resumed runtime
work, but only because shared and companion float leakage would otherwise be
reintroduced through bounded `R2/R3` contracts even after the Tier-0 strike
force closed.
