# ILC Phase 624-630 Sequence Lock v0.1

Status: locked
Date: 2026-04-13
Phase: 624
Owner lane: G8 ECU active economic layer runtime strike force

## 1. Window identity and authorization basis

Window 624-630 is the bounded ECU active-layer runtime strike-force lane. It
upgrades the Phase 622 bounded commission topology into a constitutional and
runtime lane with ratification, implementation, hardening, and closure inside a
single window.

The authorization basis is explicit and bounded:
- Human authorization 2026-04-13: the debit-side gap in Phase 622 was approved
  as the next active constitutional/runtime target for agent economic agency.
- Human authorization 2026-04-13: `Disposition B` is rejected for this lane and
  no deferred-runtime exit is permitted from Window 624-630.
- Phase 622 `bounded_ecu_exchange_model_622_locked` established the topology
  that this window upgrades into bounded internal runtime enforcement.
- AG-8 named-vehicle rule applies from Window 624 forward and is satisfied here
  by naming `CDL-063` and requiring runtime implementation plus a dedicated
  hardening gate inside this window.

Required lock tokens:
- `window_624_630_sequence_lock_primary_gate`
- `cdl_063_named_as_vehicle_for_ecu_directed_commission`
- `ag8_named_vehicle_rule_satisfied_window_624_630`
- `window_624_630_parallel_to_window_623_plus`
- `cdl_062_remains_not_authorized_in_window_624_630`
- `option_d_posture_active_in_window_624_630`
- `wallet_boundary_576_581_unchanged_in_window_624_630`
- `ecu_debit_not_ilc_payment_window_624_630`
- `window_624_630_requires_window_620_622_complete`
- `sim_commission_01_required_in_phase_626`
- `disposition_b_not_permitted_window_624_630`
- `runtime_hardening_gate_required_in_phase_629`

## 2. Phase map and hard pass conditions

| Phase | Description | Primary output | Sensitive? |
|---|---|---|---|
| 624 | Window 624-630 sequence lock | `ilc_phase_624_630_sequence_lock_v0.1.md` | YES |
| 625 | ECU active layer architecture scoping + `CDL-063` opening stub | `ilc_ecu_active_economic_layer_architecture_scoping_625_v0.1.md` | No |
| 626 | `CDL-063` prelock hardening + SIM-COMMISSION-01 | `ilc_cdl_063_ecu_directed_commission_prelock_626_v0.1.md` | No |
| 627 | `CDL-063` ratification evidence | `ilc_cdl_063_ecu_directed_commission_ratification_evidence_627_v0.1.md` | No |
| 628 | ECU active-layer runtime implementation and accounting spec | `ilc_ecu_active_layer_runtime_and_accounting_spec_628_v0.1.md` | No |
| 629 | Runtime hardening gate | `ilc_ecu_active_layer_runtime_hardening_gate_629_v0.1.md` | No |
| 630 | Coherence report, capsule update, and handoff | `ilc_window_624_630_handoff_630_v0.1.md` | No |

The hard pass condition for Window 624-630 is:
1. `CDL-063` is opened as a stub row in Phase 625 and ratified in Phase 627.
2. SIM-COMMISSION-01 runs in Phase 626 and produces calibrated expiry guidance.
3. Phase 628 runtime implementation and accounting spec both exist and pass tests.
4. Phase 629 runtime hardening gate passes with no wallet widening and no ILC transferability.
5. Phase 630 handoff records ratification, runtime implementation, hardening verdict, and deferred items.

`window_624_630_sequence_lock_primary_gate`.
`window_624_630_parallel_to_window_623_plus`.
`disposition_b_not_permitted_window_624_630`.
`runtime_hardening_gate_required_in_phase_629`.

## 3. AG-gate design basis

The AG-gate artifact remains a planning design filter rather than repo-wide
ratified law. For this window, AG-8 requires a named constitutional vehicle,
live bounded runtime implementation, and a dedicated hardening gate before the
window may claim active economic agency. No window-level AG-gate assessment is
a FAIL.

| Gate | Assessment | Notes |
|---|---|---|
| AG-1 Co-flourishing mission | advance | The window aims to give agents bounded internal economic agency while preserving the current public and human-facing safety boundaries. |
| AG-2 W_e increase | advance | Directed commission can route effort toward higher-value graph work if bounded debit and expiry remain machine-enforced. |
| AG-3 Epistemic integrity | pass | Popperian validation remains mandatory; commissions do not bypass graph admission, validation, or challenge paths. |
| AG-4 ECU-ILC separation | pass | ECU debit remains internal measurement-layer semantics; `ecu_debit_not_ilc_payment_window_624_630`; no ILC payment path or wallet-write widening is authorized. |
| AG-5 Harness-agnostic | neutral | The active layer is a protocol/runtime surface rather than a harness-owned convenience layer. |
| AG-6 Near-infinite scale | pass | Reserved-balance accounting, bounded expiry, and machine-legible state transitions must prevent unbounded drift or central manual approvals. |
| AG-7 Machine-legible first | advance | Earmark interfaces, state transitions, and hardening outputs are required to be machine-legible and testable. |
| AG-8 Outbound economic loop | advance | `ag8_named_vehicle_rule_satisfied_window_624_630`; named vehicle, runtime implementation, SIM-COMMISSION-01, and runtime hardening gate are all required in-window. |

## 4. CDL-063 vehicle declaration

`cdl_063_named_as_vehicle_for_ecu_directed_commission`.

`CDL-063` title: *ECU Directed-Commission Earmark and Bounded Debit Semantics*.

The dependency chain for `CDL-063` is:
- CDL-027 epoch issuance boundary,
- CDL-044 local-first wallet/account surfacing boundary,
- Phase 622 bounded commission topology,
- Phase 550 passive ECU proxy values.

Phase 625 must evaluate these options explicitly:
- option A: earmark-only with no debit,
- option B: bounded earmark with debit on delivery,
- option C: generalized ECU transfer.

The selected direction for this window is option B. `CDL-063` does not open
ILC transferability or generalized ECU transfer.

## 5. Inherited boundary state

The following inherited boundaries remain unchanged in Window 624-630:
- the Phase 576 and Phase 581 read-only wallet boundary remains frozen;
  `wallet_boundary_576_581_unchanged_in_window_624_630`
- the Phase 609 ECU / ILC / runtime layer separation remains the controlling
  canon; `ecu_debit_not_ilc_payment_window_624_630`
- the Phase 612 two-form MVP gate requirement remains active; Window 623+
  runtime/interface closure is still required before broader public RC claims
  may proceed
- ADR-0028 keeps `Option D` as the active posture;
  `option_d_posture_active_in_window_624_630`
- Phase 622 topology inheritance remains authoritative for the six-step bounded
  commission model that this window upgrades from spec-form-only coordination
  into bounded runtime enforcement;
  `window_624_630_requires_window_620_622_complete`

## 6. Per-phase scope constraints

| Phase | In scope | Out of scope | Hard constraint |
|---|---|---|---|
| 624 | Sequence lock, authorization basis, AG-gate table, vehicle declaration, inherited boundary confirmation, window exclusions | Any decision-log row mutation, any `ilc_core/` mutation, any ADR mutation, any wallet widening, any Option B selection claim | The window must be locked as no-`Disposition B`, no-`CDL-062`, runtime-hardening-required. |
| 625 | Architecture scoping, `CDL-063` opening stub row, earmark mechanics, anti-gaming boundary, attribution non-inflation answer | Ratification, runtime implementation, generalized ECU transfer, ILC transferability, wallet widening | The opening stub must remain narrow and must not silently widen into general payments. |
| 626 | Prelock hardening, SIM-COMMISSION-01, expiry and volume-cap calibration, anti-gaming evidence basis | Decision-log ratification update, runtime implementation, wallet widening, public settlement work | `sim_commission_01_required_in_phase_626` and its calibration output must exist before ratification. |
| 627 | `CDL-063` ratification evidence and row update from open to ratified | Runtime implementation, generalized transfer, ILC transferability, `CDL-062` opening | Ratification must remain bounded to directed commission, earmark reservation, debit-at-commit, expiry release, and non-inflation. |
| 628 | Bounded ECU active-layer runtime implementation, accounting spec, runtime tests, machine-legible state interfaces | `Disposition B`, wallet widening, public claimability, ILC transfer, generalized ECU transfer | Runtime must land complete and passing in this phase; deferred-runtime exit is not permitted. |
| 629 | Dedicated runtime hardening gate, Fix-1..N inside the phase if required, hardening verdict for reserve integrity and bounded semantics | Immediate closure without hardening, wallet widening, ILC transferability, generalized transfer | `runtime_hardening_gate_required_in_phase_629` is mandatory before closure may claim live enforcement. |
| 630 | Coherence report, capsule update, handoff, closure record, deferred-items map | Reopening constitutional scope, changing Option-D posture, claiming sovereign settlement authorization | Closure may record live bounded runtime only if ratification, implementation, and hardening all passed in-window. |

## 7. Window-level exclusions

The following exclusions are mandatory for every Window 624-630 phase:
- No decision-log mutation except the `CDL-063` row in Phase 625 and Phase 627.
- No `CDL-062` opening; `cdl_062_remains_not_authorized_in_window_624_630`.
- No `Option B` selection claim.
- No ILC transferability or wallet-write widening.
- No generalized ECU transfer between arbitrary parties.
- No external purchasing power claim.
- No prescription about Window 623+ runtime sequencing.

Window 624-630 may run in parallel to Window 623+, but it does not authorize,
block, sequence, or substitute for the MVP runtime/interface closure required
there.
