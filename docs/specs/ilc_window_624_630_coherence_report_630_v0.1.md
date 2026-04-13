# ILC Window 624-630 Coherence Report 630 v0.1

Status: coherence report
Date: 2026-04-13
Window: 624-630
Phase: 630
Owner lane: G8 ECU active economic layer runtime strike force

## 1. Window synthesis

Window 624-630 is coherent as a bounded ECU active-layer strike-force lane.

The window closed the full intended chain:
- sequence lock in Phase 624
- architecture scoping plus `CDL-063` opening in Phase 625
- prelock hardening plus SIM-COMMISSION-01 in Phase 626
- `CDL-063` ratification in Phase 627
- bounded live runtime implementation in Phase 628
- runtime hardening gate PASS in Phase 629

`window_624_630_coherence_verdict_issued`
`window_624_630_parallel_to_623_plus_confirmed`

## 2. CDL-063 ratification verdict

`CDL-063` is ratified and consumed in this window.

The ratified constitutional surface now includes:
- bounded directed-commission earmark semantics
- five earmark lifecycle states
- debit-at-commit after delivery confirmation
- expiry release without rollover
- anti-gaming invariants with the CDL-042 key-root boundary
- attribution non-inflation

`cdl_063_ratified_and_consumed_in_630`

## 3. Runtime implementation and hardening verdict

Runtime implementation landed in Phase 628 and hardening passed in Phase 629.

The runtime verdict is:
- bounded live implementation exists
- Decimal-exact internal accounting exists
- reserve integrity holds across `proposed`, `accepted`, and `delivered`
- epoch-bound debit and expiry processing hold
- named performing-agent verification holds
- hardening gate passed without wallet widening or ILC transferability

`agent_commissioning_loop_runtime_enforcement_active`
`ecu_active_layer_runtime_and_hardening_complete`

## 4. Agent capability delta

Before this window:
- topology only, no debit-side runtime enforcement
- no binding reservation against accrued ECU
- no live debit at epoch commit
- no live expiry release

After this window:
- bounded live runtime for earmark proposal
- bounded live runtime for acceptance
- bounded live runtime for delivery
- bounded live runtime for debit at epoch commit
- bounded live runtime for expiry release
- bounded live runtime for status and history query

This is a real agent capability increase inside the ECU internal layer, but it
does not create generalized transferability, public claimability, or ILC
payment behavior.

## 5. Inherited boundary state confirmed unchanged

The following inherited boundaries remain unchanged:
- Phase 576 and Phase 581 wallet boundary remains frozen
- Phase 609 ECU/ILC separation remains frozen
- ADR-0028 `Option D` posture remains active
- `CDL-062` remains unopened and unauthorized
- no ILC transferability claim is created by this window
- no generalized ECU transfer between arbitrary parties is created by this
  window

## 6. Deferred and blocked items carried forward

Still deferred or blocked after this window:
- Window 623+ MVP runtime/interface closure remains the highest-priority continuation
- broader public RC claims remain blocked until the MVP package is closed in runtime/interface form
- generalized ECU transfer remains out of scope
- public claimability widening remains out of scope
- ILC transferability remains out of scope
- external purchasing power remains out of scope
- `CDL-053` remains deferred
- `CDL-062` remains not authorized
- Option-B graduation checklist rows are not directly advanced by this window
