# ILC CDL-064 Exact Numeric Representation Ratification Evidence 634 v0.1

Status: ratification evidence
Date: 2026-04-13
Window: 631-636
Phase: 634
Owner lane: G8 tier-0 economic numeric determinism strike force

## 1. Ratification identity and prelock lineage

CDL-064 is ratified in Phase 634 on 2026-04-13.

This ratification consumes four inputs:
- Phase 631 sequence lock:
  `docs/specs/ilc_phase_631_636_sequence_lock_v0.1.md`
- Phase 632 inventory and opening stub:
  `docs/specs/ilc_tier0_numeric_surface_inventory_and_risk_classification_632_v0.1.md`
- Phase 633 prelock:
  `docs/specs/ilc_cdl_064_exact_numeric_representation_prelock_633_v0.1.md`
- Phase 633 simulation:
  `docs/specs/ilc_sim_numeric_01_representation_evaluation_633_v0.1.md`

CDL-064 was read from the Phase 633 commit snapshot and confirmed `status: open`
before ratification.

`cdl_064_ratified_634`

## 2. Final constitutional clause text

**Clause A — Exact numeric representation requirement**

Tier-0 runtime-critical economic, ledger, staking, and direct settlement
surfaces must not use binary float as the canonical internal representation for
balances, stake totals, reward totals, or settlement deltas.

`cdl_064_exact_numeric_boundary_ratified`

**Clause B — Exact arithmetic requirement**

Tier-0 correctness, replay, settlement, and staking calculations must use exact
arithmetic. Rounding-tolerance and epsilon-based correctness checks are not
constitutional substitutes for exact arithmetic on Tier-0 surfaces.

`cdl_064_exact_arithmetic_rule_ratified`

**Clause C — Canonical machine serialization rule**

Tier-0 exact numeric values must serialize as normalized base-10 decimal
strings with the following canonical properties:
- no exponent notation
- no negative zero
- no superfluous leading zeros
- trailing fractional zeros stripped
- integral values emitted without a trailing decimal point

`cdl_064_canonical_serialization_rule_ratified`

**Clause D — Tier-0 scope boundary and non-goals**

CDL-064 governs Tier-0 runtime-critical economic, ledger, staking, and directly
coupled export/validation companions only. It does not open wallet widening,
generalized ECU transfer, ILC transferability, sovereign substrate selection,
`CDL-062`, or repo-wide simulation cleanup.

`cdl_064_tier0_scope_boundary_ratified`

## 3. Representation decision and canonical serialization rule

The selected representation direction locked by this ratification is:
- `exact-decimal-runtime-contract`

The canonical machine serialization rule ratified by CDL-064 is:
- Tier-0 exact numeric values serialize as normalized decimal strings
- canonical examples: `0`, `0.05`, `1`, `1.25`, `400`
- non-canonical examples: `0.0`, `01.25`, `1.2500`, `1e-3`, `-0`

What CDL-064 does not decide beyond Tier-0 scope:
- it does not ratify a universal minor-unit scale for all future ECU/ILC
  quantities
- it does not require repo-wide float cleanup outside the Tier-0 boundary
- it does not widen any payment, wallet, or Option-B surface

`cdl_064_selected_representation_locked`
`float_retention_rejected_by_cdl_064`

## 4. Ratification readiness evidence checklist satisfaction

1. Phase 632 inventory exists and contains Tier-0 risk classification:
   `tier0_numeric_inventory_632_locked`
2. Phase 633 prelock exists and defines migration invariants:
   `cdl_064_prelock_633_locked`
3. SIM-NUMERIC-01 evaluated all required options:
   option A `retain-float-rounding-and-tolerance`, option B
   `exact-decimal-runtime-contract`, option C
   `fixed-point-minor-unit-contract`
4. Float retention was explicitly rejected for Tier-0:
   `float_retention_rejected_for_tier0`
5. CDL-064 remains narrow and does not widen Option-B, wallet, or
   ILC-transfer scope:
   `cdl_064_tier0_scope_boundary_ratified`

## 5. Mutation scope and invariants

CDL-064 is the only CDL row mutated in Phase 634.

No `ilc_core/` mutation occurs in Phase 634.

No wallet widening occurs in Phase 634.
