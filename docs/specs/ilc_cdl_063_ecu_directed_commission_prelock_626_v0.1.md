# ILC CDL-063 ECU Directed Commission Prelock 626 v0.1

Status: prelock hardening
Date: 2026-04-13
Window: 624-630
Phase: 626
Owner lane: G8 ECU active economic layer runtime strike force

## 1. Prelock identity and CDL-063 open state verification

This document converts the Phase 625 scoping answers for `CDL-063` into
constitutional-prelock form and binds ratification readiness to the
SIM-COMMISSION-01 expiry calibration.

CDL-063 was read at Phase 626 and confirmed `status: open`.

`cdl_063_prelock_626_locked`
`cdl_063_open_state_verified_at_626`

## 2. Earmark mechanics constitutional clause (prelock form)

CDL-063 earmark: a binding protocol-level reservation by commissioning agent A
of up to N units of A's unearmarked accrued ECU, directed toward a specific
performing agent B under a named commission_id. The earmark lifecycle states
are: proposed, accepted, delivered, debited, expired. The balance invariant is:
earmarked ECU may not exceed A's current unearmarked accrued balance at
proposal time. Debit occurs at the epoch commit following delivery
confirmation. `Delivered` earmarks remain reserved until `debited`. Expired
earmarks reaching the SIM-COMMISSION-01 calibrated expiry horizon without
delivery are released back to A's unearmarked balance at the epoch boundary
that processes expiry.

`earmark_mechanics_constitutional_clause_prelocked`

## 3. Anti-gaming constitutional clause (prelock form)

Arm's-length invariant: commissioning agent A and performing agent B must have
distinct canonical agent_ids under the current identity boundary; same-key
self-commission is prohibited. Any stronger common-control enforcement claim
must name the evidence surface and the enforcement boundary explicitly rather
than assuming automatic detectability.

Popperian invariant: commissioned contributions must pass the full CDL-V7
Popperian gate through the normal authored-envelope path. No earmark grants a
bypass, fast-track, or elevated admission probability.

Expiry invariant: earmarks not confirmed within the SIM-COMMISSION-01 calibrated expiry horizon are automatically released. No rollover or extension is permitted without a new earmark proposal.

`anti_gaming_constitutional_clause_prelocked`

## 4. Attribution non-inflation constitutional clause (prelock form)

`ecu_credit(B) = attribution_formula(contribution_W_e)` independent of earmark
presence.

`ecu_debit(A) = earmark_amount` independent of B's actual attribution.

These are separate epoch-settled ledger operations. The earmark is a
coordination contract; it is not an attribution supplement.

`attribution_non_inflation_constitutional_clause_prelocked`

## 5. SIM-COMMISSION-01 expiry parameter dependency

CDL-063 ratification in Phase 627 requires the SIM-COMMISSION-01 expiry value
from Phase 626 to be locked in. SIM-COMMISSION-01 recommends a fixed expiry
system for v1 rather than a tiered system.

The candidate fixed values carried forward into Phase 627 are:
- minimum viable expiry: `240` validation epochs
- nominal recommended expiry: `1440` validation epochs
- maximum sensible expiry: `10080` validation epochs

Because SIM-COMMISSION-01 rejects a tiered expiry system for v1, Phase 627 may
ratify the fixed-expiry direction directly without a second runtime branch.

`cdl_063_ratification_requires_sim_commission_01_expiry_value`

## 6. Mutation scope and invariants

CDL-063 opening is the only constitutional mutation in this window before Phase
627. The Phase 626 prelock document does not mutate the CDL row. It is
additive-only and preserves the current `status: open` row state for `CDL-063`
until ratification evidence lands in Phase 627.

`cdl_063_prelock_mutation_scope_additive_only`
