# ILC ECU Active Economic Layer Architecture Scoping 625 v0.1

Status: scoped
Date: 2026-04-13
Window: 624-630
Phase: 625
Owner lane: G8 ECU active economic layer runtime strike force

## 1. Authorization basis and scoping target

This document scopes `CDL-063` as the narrow constitutional vehicle for bounded
directed-commission earmark and debit semantics inside the internal ECU layer.
It operates under the Phase 624 sequence lock and the inherited Phase 609
separation boundary between ECU accounting semantics and ILC settlement.

The scoping target is specific:
- answer earmark mechanics and balance accounting,
- answer bounded anti-gaming constraints,
- answer attribution non-inflation,
- open `CDL-063` as a stub row without yet ratifying it.

`ecu_active_layer_architecture_scoping_625_locked`
`cdl_063_opened_as_stub`
`ecu_debit_not_ilc_payment_625`

## 2. Earmark mechanics and balance accounting model

An earmark differs from passive accrual because passive accrual is protocol
measurement produced by validated contributions, while an earmark is a
protocol-level reservation against already accrued ECU. The earmark does not
mint new ECU and does not alter the attribution formula that generated the
underlying balance.

Agent A's spendable ECU balance is defined as:

`spendable_ecu(A) = total_accrued_ecu(A) - reserved_earmarks(A)`

where reserved means earmarks in `proposed`, `accepted`, or `delivered` state.

An earmark is a binding declaration that `N` units of Agent A's unearmarked
accrued ECU are directed toward a specific named commission, identified by
`commission_id` linking the commission to Agent B and the task.

The earmark lifecycle states are:
- `proposed`: Agent A declares the offer
- `accepted`: Agent B accepts the offer
- `delivered`: Agent B's contribution passes the Popperian validation epoch
- `debited`: Agent A's balance is reduced at epoch commit
- `expired`: the earmark reaches its expiry epoch with no delivery and the
  reserved amount is released back to Agent A

Earmarks are epoch-settled: debit occurs at the epoch commit that follows
delivery confirmation, not at the moment of acceptance, and `delivered`
earmarks remain reserved until `debited`.

The balance invariant is strict: Agent A cannot earmark more than their current unearmarked accrued ECU balance at the time of proposal.

`earmark_mechanics_answered`

## 3. Anti-gaming constraints

The bounded anti-gaming rule starts with an arm's-length requirement. Agent A
and Agent B must have distinct canonical `agent_id` values under the CDL-042
key-derivation boundary, with distinct key-derivation roots. Same-key
self-commission is prohibited as the minimum arm's-length boundary. Same-key self-commission is prohibited as the minimum arm's-length boundary. Any
stronger common-control enforcement rule would require an explicit evidence
surface and enforcement boundary; it must not be assumed from canonical
identity alone.

Commissioned contributions may not bypass the normal graph path. Every
commissioned contribution must enter through the standard authored-envelope
submission route and pass the full CDL-V7 Popperian gate. A commission earmark
does not grant fast-track admission, bypass, elevated scoring, or increased
acceptance probability.

Expiry enforcement is mandatory. An earmark that reaches its expiry epoch
without delivery confirmation automatically transitions to `expired` state and
the reserved amount returns to Agent A's unearmarked balance at the epoch
boundary that processes expiry.

To limit high-volume low-quality commission spam, the active layer requires a
simultaneous active-earmark cap per epoch window. Let `M` be the maximum number
of active earmarks an agent may hold in a single validation epoch window.
`M` is a calibration parameter reserved for SIM-COMMISSION-01 in Phase 626.

`anti_gaming_constraints_answered`

## 4. Attribution non-inflation proof

Directed commission must not inflate `W_e` or add bonus attribution on top of
what the contribution actually merits.

Agent B's ECU attribution comes solely from the validated contribution's `W_e`
under the normal attribution formula. For the current bounded posture, the
Phase 550 passive proxy values carried forward through later artifacts remain:
- `rate = 0.20`
- `decay_floor = 0.05`
- `attribution_cap = 0.15`

The commission earmark is consumed by Agent A's debit at epoch commit. It is
not added to Agent B's attribution on top of normal attribution.

Formal statement:

`ecu_credit(B) = attribution_formula(contribution_W_e)`

independent of whether a commission earmark was present.

Formal statement:

`ecu_debit(A) = earmark_amount`

independent of what B actually received in attribution.

These are separate ledger operations. The earmark is a coordination contract, not an attribution inflation mechanism.

`attribution_non_inflation_answered`

## 5. CDL-063 options evaluation

Option A: earmark-only, no debit.

Rejected. This reproduces the Phase 622 topology without enforcement. Agent A
can signal intent, but the protocol cannot reserve and settle the debit side.
That leaves the AG-8 named-vehicle rule unsatisfied in practical effect because
the debit surface remains unresolved.

Option B: bounded earmark with debit on delivery.

Selected. This provides enforceable reservation and debit semantics while
remaining inside the ECU measurement layer. It stays consistent with Phase 609
separation, preserves the current wallet boundary, and does not create ILC
transferability.

Option C: generalized ECU transfer.

Rejected. This exceeds `CDL-063` scope, creates a general payment surface
incompatible with the current bounded canon, and would require a separate
future constitutional vehicle with broader wallet and transfer implications.

`cdl_063_option_b_selected_bounded_earmark_with_debit`

## 6. Selected direction and forward pointer

The selected direction for `CDL-063` is Option B: bounded earmark with debit on
delivery.

Phase 626 must harden this selection into prelock clauses and calibrate expiry
and active-earmark caps through SIM-COMMISSION-01. Phase 628 must implement the
live bounded runtime and accounting model that enforces the reserved-balance,
expiry, and debit-at-commit rules.

`CDL-063` does not open ILC transferability. It also does not authorize
generalized ECU transfer, public claimability, wallet write authority, or
external purchasing power.
