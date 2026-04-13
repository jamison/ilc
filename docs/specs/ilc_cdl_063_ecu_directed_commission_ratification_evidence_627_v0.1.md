# ILC CDL-063 ECU Directed Commission Ratification Evidence 627 v0.1

Status: ratification evidence
Date: 2026-04-13
Window: 624-630
Phase: 627
Owner lane: G8 ECU active economic layer runtime strike force

## 1. Ratification identity and prelock lineage

CDL-063 is ratified in Phase 627 on 2026-04-13.

This ratification consumes three inputs:
- Phase 625 scoping: `docs/specs/ilc_ecu_active_economic_layer_architecture_scoping_625_v0.1.md`
- Phase 626 prelock: `docs/specs/ilc_cdl_063_ecu_directed_commission_prelock_626_v0.1.md`
- Phase 626 simulation: `docs/specs/ilc_sim_commission_01_earmark_expiry_calibration_626_v0.1.md`

CDL-063 was read from the Phase 626 commit snapshot and confirmed `status: open`
before ratification.

`cdl_063_ratified_627`

## 2. Final constitutional clause text

**Clause A — Earmark semantics**

A commissioning agent may create a bounded earmark reserving up to N units of
their unearmarked accrued ECU toward a named commission directed to a distinct
performing agent. Earmark states: `proposed`, `accepted`, `delivered`,
`debited`, `expired`. The earmarked amount may not exceed the commissioning
agent's unearmarked accrued ECU balance at proposal time. Debit occurs at the
epoch commit following delivery confirmation.

`cdl_063_earmark_semantics_ratified`

**Clause B — Debit authority**

Upon epoch commit following delivery confirmation, the commissioning agent's
accrued ECU is debited by the earmarked amount. Expired earmarks reaching the
ratified expiry horizon without delivery are released back to the commissioning
agent's unearmarked balance at the epoch boundary that processes expiry. No manual override, rollover, or extension is permitted.

`cdl_063_debit_authority_ratified`

**Clause C — Anti-gaming invariants**

(i) Arm's-length: commissioning and performing agents must have distinct
canonical agent_ids under CDL-042 with distinct key-derivation roots;
same-key self-commission is prohibited. No stronger common-control rule is
ratified in this phase beyond the distinct-key-root boundary.

(ii) Popperian: commissioned contributions must pass the full CDL-V7 Popperian
gate without bypass or elevated admission probability.

(iii) Expiry: earmarks not confirmed within the ratified expiry horizon are
automatically released; no rollover permitted.

`cdl_063_anti_gaming_invariants_ratified`

**Clause D — Attribution non-inflation**

`ecu_credit(performing_agent) = attribution_formula(contribution_W_e)`,
independent of earmark presence.

`ecu_debit(commissioning_agent) = earmark_amount`,
independent of performing agent's actual attribution.

These are separate epoch-settled ledger operations. An earmark is a
coordination contract, not an attribution supplement.

`cdl_063_attribution_non_inflation_ratified`

## 3. SIM-COMMISSION-01 expiry parameter resolution

SIM-COMMISSION-01 recommended:
- minimum viable expiry: `240` validation epochs
- nominal recommended fixed expiry: `2880` validation epochs
- maximum sensible expiry: `10080` validation epochs
- fixed expiry for v1 rather than tiered expiry

The ratified expiry parameter is:

`cdl_063_expiry_parameter_locked: fixed_2880_validation_epochs`

The active-earmark cap recommendation from SIM-COMMISSION-01 remains a bounded
runtime carry-forward for Phase 628:
- `recommended_active_earmark_cap_per_agent = 8`

That runtime cap is not elevated into constitutional law by CDL-063 ratification.

## 4. Ratification readiness evidence checklist satisfaction

1. Phase 625 scoping document exists and contains all three answered questions:
   `ecu_active_layer_architecture_scoping_625_locked`
2. Phase 626 prelock document hardened all three questions into constitutional-
   prelock clauses: `cdl_063_prelock_626_locked`
3. SIM-COMMISSION-01 produced a calibrated expiry parameter:
   `sim_commission_01_expiry_calibration_complete`
4. All three options were evaluated in Phase 625; option B (bounded earmark
   with debit on delivery) was selected:
   `cdl_063_option_b_selected_bounded_earmark_with_debit`
5. ECU debit is explicitly not ILC payment and does not create ILC
   transferability: `cdl_063_not_ilc_payment_ratified`

`cdl_063_not_ilc_payment_ratified`

## 5. Mutation scope and invariants

CDL-063 is the only CDL row mutated in Phase 627.

No `ilc_core/` mutation occurs in Phase 627.

No wallet widening occurs in Phase 627.

`ecu_debit_not_ilc_payment_627`
