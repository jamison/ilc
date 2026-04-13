# ILC Phase 631-636 Sequence Lock v0.1

Status: locked
Date: 2026-04-13
Phase: 631
Owner lane: G8 tier-0 economic numeric determinism strike force

## 1. Window identity and authorization basis

Window 631-636 is the Tier-0 Economic Numeric Determinism strike-force lane. It
is a bounded corrective reprioritization: before broader runtime widening
continues, the Tier-0 economic and staking runtime surfaces must stop relying on
float-based accounting, tolerance equality, and rounding-based replay checks.

The authorization basis is explicit and bounded:
- Human direction 2026-04-13: Tier-0 float-based economic runtime is treated as
  an active architectural defect rather than deferred technical debt.
- Window 624-630 proved bounded internal economic agency but left broader
  float-dependent Tier-0 settlement and staking primitives intact.
- Existing canon still records Window 623+ as the highest-priority continuation,
  so this window is a bounded corrective lane rather than automatic carry-
  forward.
- Human activation is required to reprioritize this corrective lane ahead of the
  broader public runtime/interface closure.

Required lock tokens:
- `window_631_636_sequence_lock_primary_gate`
- `cdl_064_named_as_vehicle_for_exact_numeric_representation`
- `window_631_636_targets_tier0_runtime_surfaces_only`
- `window_631_636_reprioritization_requires_human_lock`
- `float_retention_not_acceptable_tier0_window_631_636`
- `window_631_636_does_not_select_option_b`
- `cdl_062_remains_not_authorized_in_window_631_636`
- `wallet_boundary_576_581_unchanged_in_window_631_636`
- `ecu_ilc_separation_preserved_in_window_631_636`
- `window_623_plus_priority_recorded_but_bracketed_by_numeric_strike_force`
- `cdl_064_stub_required_in_phase_632`
- `numeric_hardening_gate_required_in_phase_636`

## 2. Tier-0 target surface and hard pass conditions

The Tier-0 target surface for this window is:
- `ilc_core/ledger/`
- `ilc_core/rc/economic_cycle_runtime.py`
- `ilc_core/validator/staking_liveness_runtime.py`
- `ilc_core/types.py`
- directly coupled DTO/export/runtime files required for Tier-0 coherence

Simulation, analytics, and research helpers remain out of initial strike-force
scope unless direct Tier-0 coherence requires a narrower companion change.

| Phase | Description | Primary output | Sensitive? |
|---|---|---|---|
| 631 | Window 631-636 sequence lock | `ilc_phase_631_636_sequence_lock_v0.1.md` | YES |
| 632 | Tier-0 numeric inventory + `CDL-064` opening stub | `ilc_tier0_numeric_surface_inventory_and_risk_classification_632_v0.1.md` | No |
| 633 | `CDL-064` prelock + SIM-NUMERIC-01 | `ilc_cdl_064_exact_numeric_representation_prelock_633_v0.1.md` | No |
| 634 | `CDL-064` ratification evidence | `ilc_cdl_064_exact_numeric_representation_ratification_evidence_634_v0.1.md` | No |
| 635 | Tier-0 runtime migration implementation | `ilc_tier0_exact_numeric_runtime_migration_635_v0.1.md` | No |
| 636 | Tier-0 hardening gate + closure | `ilc_tier0_numeric_hardening_and_window_631_636_closure_636_v0.1.md` | No |

The hard pass condition for Window 631-636 is:
1. `CDL-064` is opened as a stub row in Phase 632 and ratified in Phase 634.
2. A complete Tier-0 numeric inventory exists and classifies all target
   surfaces by risk and migration class.
3. A ratified exact-numeric contract exists for Tier-0 economic runtime.
4. Tier-0 runtime migration lands in Phase 635.
5. Phase 636 hardening gate passes before closure.

`window_631_636_sequence_lock_primary_gate`.
`window_631_636_targets_tier0_runtime_surfaces_only`.
`cdl_064_stub_required_in_phase_632`.
`numeric_hardening_gate_required_in_phase_636`.

## 3. AG-gate design basis

The AG-gate artifact remains a planning design filter rather than repo-wide
ratified law. For this window, AG-4 and AG-6 are the most load-bearing: the
strike force must tighten exact arithmetic without collapsing ECU into ILC or
widening semantics beyond the current bounded runtime posture. No window-level
AG-gate assessment is a FAIL.

| Gate | Assessment | Notes |
|---|---|---|
| AG-1 Co-flourishing mission | advance | Exact arithmetic reduces the risk of silently invalid economic treatment for both human and agent participants. |
| AG-2 W_e increase | neutral | This is enabling runtime infrastructure rather than direct productivity expansion. |
| AG-3 Epistemic integrity | pass | No Popperian bypass or settled-graph mutability is introduced. |
| AG-4 ECU-ILC separation | pass | The strike force tightens numeric exactness without collapsing ECU into ILC or widening payment semantics. |
| AG-5 Harness-agnostic | pass | Numeric representation is protocol/runtime-side rather than harness-owned. |
| AG-6 Near-infinite scale | pass | Exact arithmetic and deterministic replay are prerequisites for scale-safe runtime. |
| AG-7 Machine-legible first | advance | Canonical exact serialization should improve replay and machine auditability. |
| AG-8 Outbound economic loop | neutral | The bounded active loop remains inherited from Window 624-630; this lane hardens its numeric foundation rather than widening semantics. |

## 4. CDL-064 vehicle declaration

`cdl_064_named_as_vehicle_for_exact_numeric_representation`.

`CDL-064` title: *Canonical Economic Numeric Representation and Exact
Arithmetic Boundary*.

`CDL-064` is the narrow constitutional vehicle for:
- exact numeric representation on Tier-0 economic, ledger, and staking runtime
  surfaces,
- exact arithmetic and replay invariants,
- canonical machine serialization for those exact numeric values,
- migration boundaries and non-goals.

Representation choice is not decided in Phase 631. Phase 633 must evaluate:
- option A: retain float with rounding and tolerance,
- option B: exact decimal runtime contract,
- option C: fixed-point minor-unit contract.

This vehicle does not open sovereign substrate selection, `CDL-062`, wallet
widening, ILC transferability, or `Option B`.

## 5. Inherited boundary state

The following inherited boundaries remain unchanged in Window 631-636:
- the Phase 576 and Phase 581 read-only wallet boundary remains frozen;
  `wallet_boundary_576_581_unchanged_in_window_631_636`
- the Phase 609 ECU / ILC / runtime layer separation remains controlling canon;
  `ecu_ilc_separation_preserved_in_window_631_636`
- the Phase 612 two-form MVP gate requirement remains active
- ADR-0028 keeps `Option D` as the active posture
- Window 624-630 bounded active-layer runtime remains inherited context, but not
  a substitute for broader runtime closure or numeric hardening

## 6. Per-phase scope constraints

| Phase | In scope | Out of scope | Hard constraint |
|---|---|---|---|
| 631 | Sequence lock, authorization basis, AG-gate table, vehicle declaration, inherited boundary confirmation, routing statement | Decision-log mutation, `ilc_core/` mutation, ADR mutation, wallet widening, `Option B` selection claims | The lock must force Tier-0 bounded scope, `CDL-064`, and hardening before closure. |
| 632 | Tier-0 inventory, risk classification, migration-class grouping, `CDL-064` opening stub row | Runtime migration, representation ratification, repo-wide float cleanup | The inventory must be complete for the Tier-0 target surface set. |
| 633 | `CDL-064` prelock, SIM-NUMERIC-01, representation evaluation, migration invariants | Decision-log ratification update, runtime implementation | Float retention must be evaluated and explicitly rejected or selected on evidence, not by inertia. |
| 634 | `CDL-064` ratification evidence and row update | Runtime implementation, wallet widening, `CDL-062` opening | Ratification must remain narrow to exact numeric representation and arithmetic rules. |
| 635 | Tier-0 runtime migration implementation and migration spec | Decision-log mutation, repo-wide simulation cleanup, semantic widening | No float-based internal Tier-0 accounting may remain after migration. |
| 636 | Tier-0 hardening gate, capsule update, handoff, closure record | Reopening constitutional scope, `Option B` selection, sovereign settlement authorization | Closure may claim success only if exact arithmetic and replay hardening passed. |

## 7. Window-level exclusions and routing

The following exclusions are mandatory for every Window 631-636 phase:
- No decision-log mutation except the `CDL-064` row in Phase 632 and Phase 634.
- No `CDL-062` opening; `cdl_062_remains_not_authorized_in_window_631_636`.
- No `Option B` selection claim; `window_631_636_does_not_select_option_b`.
- No ILC transferability or wallet-write widening.
- No generalized ECU transfer widening beyond already-ratified bounded active
  layer semantics.
- No repo-wide simulation or analytics float cleanup in this window.

Existing canon still records Window 623+ as the highest-priority continuation.
This corrective strike force brackets that priority rather than erasing it:
`window_623_plus_priority_recorded_but_bracketed_by_numeric_strike_force`.

If activated by human lock, Window 631-636 should run before or immediately
adjacent to the broader MVP public runtime/interface closure, so that broader
runtime widening does not continue on top of Tier-0 float-based settlement
primitives.
