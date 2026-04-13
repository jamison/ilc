# ILC ECU Active Layer Runtime Hardening Gate 629 v0.1

Status: hardening gate passed
Date: 2026-04-13
Window: 624-630
Phase: 629
Owner lane: G8 ECU active economic layer runtime strike force

## 1. Gate identity and authority

This artifact records the dedicated hardening gate for the bounded ECU active
layer landed in Phase 628.

The gate runs under:
- the Phase 624 sequence lock,
- the ratified `CDL-063` boundary,
- the Phase 628 runtime implementation,
- and the explicit no-`Disposition B` strike-force rule.

`ecu_active_layer_runtime_hardening_gate_629_locked`
`runtime_hardening_gate_phase_629_executed`

## 2. Runtime surface under test

The runtime surface under test is:
- `ilc_core/ledger/ecu_active_layer_runtime.py`

The hardening scope covers:
- proposal-time oversubscription checks
- reserved-balance integrity across `proposed`, `accepted`, and `delivered`
- performing-agent verification on acceptance and delivery
- epoch-bound debit only
- expiry release without rollover
- idempotent processing for already terminal earmarks
- stable `earmark_status` and `earmark_history` output
- bounded runtime with no wallet widening and no ILC transfer path

## 3. Hardening suite executed

The hardening suite executed in this phase covers at minimum:
- oversubscription prevention across `proposed`, `accepted`, and `delivered`
- delivered earmarks remain reserved until `debited`
- epoch-commit debit only
- expiry release without rollover
- idempotent commit processing for previously debited and expired earmarks
- stable `earmark_status` and `earmark_history` output
- no wallet widening and no ILC transfer path

Additional hardening executed in this phase:
- Decimal-based exact internal accounting replaced binary float balance and
  earmark arithmetic
- decimal-boundary reservation tests prove `0.1` plus `0.2` can consume `0.3`
  exactly without false oversubscription
- repeated small debit tests prove exact drain to zero without precision drift

## 4. Findings and fix-loop disposition

Findings:
- Fix-1 required: the Phase 628 runtime used Python `float` for accrued ECU and
  earmark amounts. That primitive is unsafe for reserve integrity and debit
  arithmetic because binary precision drift can create false oversubscription
  failures or non-zero dust balances.

Fix-loop disposition:
- Fix-1 landed in Phase 629: internal accounting was converted to `Decimal`
  while preserving the bounded public runtime surface.
- No additional fix loop was required after the Decimal conversion and the
  hardening suite passed cleanly.

`fix_loop_completed_within_phase_629`

## 5. Gate verdict

Verdict: PASS.

The runtime now satisfies the bounded hardening criteria:
- reserve integrity preserved
- decimal-exact debit arithmetic preserved
- no rollover
- no wallet widening
- no ILC transferability
- no generalized ECU transfer semantics introduced

`bounded_ecu_runtime_no_wallet_widening_confirmed`
`ecu_debit_not_ilc_payment_629`
`runtime_hardening_gate_verdict_pass`

## 6. Carry-forward constraints

The following remain unchanged after hardening:
- ECU debit is internal accounting only and is not ILC payment
- no wallet write surface is exposed
- no public claimability widening is introduced
- no generalized ECU transfer between arbitrary parties is authorized
- `CDL-062` remains unopened and unauthorized
- Window 623+ remains the highest-priority continuation for the MVP public
  runtime/interface lane

The Decimal hardening in this phase is runtime-only. It does not widen the
constitutional scope ratified in Phase 627.
