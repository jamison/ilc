# ILC CDL-064 Exact Numeric Representation Prelock 633 v0.1

Status: prelock hardening
Date: 2026-04-13
Window: 631-636
Phase: 633
Owner lane: G8 tier-0 economic numeric determinism strike force

## 1. Authorization basis and prelock target

This document converts the Phase 632 inventory and CDL-064 opening rationale
into prelock form. Phase 632 established that float retention is not acceptable
for Tier-0 runtime-critical economic, ledger, and staking surfaces, but did not
yet select the exact replacement direction.

Phase 633 consumes SIM-NUMERIC-01, selects a single direction for ratification,
and defines the migration invariants Phase 635 must implement.

`cdl_064_prelock_633_locked`
`sim_numeric_01_consumed_for_prelock`

## 2. Representation options and evaluation criteria

`representation_options_evaluated`

The three candidate directions are:

- option A: `retain-float-rounding-and-tolerance`
- option B: `exact-decimal-runtime-contract`
- option C: `fixed-point-minor-unit-contract`

The evaluation criteria are:
- deterministic replay behavior
- arithmetic exactness
- canonical serialization stability
- storage/export compatibility
- migration complexity
- cross-language portability

Prelock reading of the option set:

| Option | Deterministic replay behavior | Arithmetic exactness | Canonical serialization stability | Storage/export compatibility | Migration complexity | Cross-language portability | Prelock verdict |
|---|---|---|---|---|---|---|---|
| A `retain-float-rounding-and-tolerance` | weak: requires epsilon and rounding heuristics | fail: binary float cannot represent many decimal fractions exactly | weak: float JSON emission is stable enough locally but not an exact protocol contract | superficially easy because it preserves current shape | lowest | weak because exactness still depends on language/runtime-specific float behavior | reject |
| B `exact-decimal-runtime-contract` | strong if canonical string serialization is locked | pass | strong with normalized decimal-string rule | medium: export surfaces must move from float to exact string form | medium | strong enough because decimal-string canon is portable | select |
| C `fixed-point-minor-unit-contract` | strong once scale is fixed | pass | strong once integer minor-unit canon is fixed | medium to hard: all Tier-0 surfaces need a ratified unit-scale contract | highest in this bounded lane because it smuggles divisibility policy | strongest long-term if scale is already ratified | defer for later consideration, do not select in CDL-064 |

## 3. Selected exact-numeric direction

Phase 633 selects option B: `exact-decimal-runtime-contract` for ratification in
Phase 634.

Reason:
- it delivers exact arithmetic now on the bounded Tier-0 target surface
- it is consistent with the already-hardened bounded ECU active-layer runtime
  that moved internal arithmetic to `Decimal`
- it allows canonical machine serialization to be locked without first ratifying
  a universal minor-unit scale for ECU, ILC, stake, and reward quantities
- it avoids turning the numeric strike force into a hidden divisibility-policy
  window

Option A is rejected.
- float plus rounding/tolerance remains a non-exact contract and therefore
  cannot satisfy the strike-force target

Option C is not selected for CDL-064 v1.
- fixed-point minor units remain structurally attractive, but selecting them now
  would require ratifying canonical subunit scale choices that this bounded lane
  was not opened to decide

The ratification target is therefore:
- internal Tier-0 exact numeric state uses decimal exact arithmetic
- canonical machine serialization uses normalized decimal strings
- no Tier-0 correctness rule may depend on epsilon or rounding tolerance after
  migration

`exact_numeric_direction_selected_for_ratification`
`float_retention_rejected_for_tier0`

## 4. Tier-0 migration invariants

`tier0_migration_invariants_defined`

Phase 635 must implement these invariants at minimum:

1. No float in Tier-0 internal balances, stake totals, reward totals, or
   settlement deltas after migration.
2. No epsilon-based equality in Tier-0 settlement correctness checks after
   migration.
3. No rounding-based replay correctness in Tier-0 runtime after migration.
4. Canonical machine serialization rule:
   - Tier-0 exact numeric values serialize as normalized base-10 strings
   - no exponent notation
   - no negative zero
   - no superfluous leading zeros
   - trailing fractional zeros are stripped
   - integral values serialize without a trailing decimal point
5. Migration boundary:
   - Tier-0 runtime-critical economic, ledger, staking, and directly coupled
     export/validation companions are in scope
   - simulations, analytics, research helpers, and public runtime widening stay
     out of scope unless direct Tier-0 coherence requires a narrow companion
     change

Examples of canonical numeric serialization after migration:
- `0`
- `0.05`
- `1`
- `1.25`
- `400`

Non-canonical examples after migration:
- `0.0`
- `01.25`
- `1.2500`
- `1e-3`
- `-0`

## 5. Constitutional clause draft

Clause class 1 — exact numeric representation requirement:
- Tier-0 runtime-critical economic, ledger, staking, and direct settlement
  surfaces must not use binary float as the canonical internal representation
  for balances, stake totals, reward totals, or settlement deltas.

Clause class 2 — exact arithmetic requirement:
- Tier-0 correctness, replay, settlement, and staking calculations must use
  exact arithmetic. Rounding-tolerance and epsilon-based correctness gates are
  not constitutional substitutes for exact arithmetic on Tier-0 surfaces.

Clause class 3 — canonical serialization requirement:
- Tier-0 exact numeric values must serialize through a canonical normalized
  decimal-string rule that is machine-legible, replay-stable, and portable
  across implementations.

Clause class 4 — migration boundary and non-goals:
- CDL-064 governs Tier-0 exact numeric representation only. It does not open
  wallet widening, generalized ECU transfer, sovereign substrate selection,
  `CDL-062`, or repo-wide simulation cleanup.

## 6. Forward pointer to ratification and runtime migration

Phase 634 must ratify the exact-decimal runtime contract and the canonical
decimal-string serialization rule as CDL-064.

Phase 635 must implement the migration across the Tier-0 target surface and its
direct export/validation companions, with no float-based Tier-0 arithmetic
remaining when Phase 636 hardening begins.

`window_631_636_moves_to_cdl_064_ratification`
