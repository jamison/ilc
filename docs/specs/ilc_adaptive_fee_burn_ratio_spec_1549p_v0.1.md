# ILC Adaptive Fee-Burn Ratio Spec 1549p v0.1

**Status:** PRE-RC SPECIFICATION
**Phase:** 1549p
**Window:** 1546p-1555p
**OBL:** OBL-028
**Runtime activation:** none

```text
obl_028_adaptive_fee_burn_spec_committed_phase_1549p
fee_burn_runtime_unchanged_phase_1549p
```

## 1. Purpose

This specification closes the pre-public-RC design gap for an adaptive
post-issuance fee-burn ratio. CDL-028 remains the active rule: 10% of epoch
fees route to the Genesis burn pool under the default-off Phase 1346 quote
runtime. This document does not amend that rule.

The adaptive mechanism described here is a candidate future governance rule for
post-issuance conditions, where scheduled issuance no longer offsets burn
pressure and fixed 10% burn can become too deflationary.

## 2. Canonical Inputs

| Input | Source | Role |
|---|---|---|
| CDL-028 fixed burn ratio | CDL register; `FEE_BURN_RATIO = Decimal("0.10")` | Active Genesis baseline |
| SIM-008 late-economy burn result | `docs/specs/ilc_sim_008_commissioning_results_406_v0.1.md` | 5% late-economy burn-floor candidate |
| ADR-0017 | `docs/adr/ADR_0017_Post_Issuance_Economic_Transition.md` | Rationale for adaptive post-issuance burn |
| Phase 1346 runtime | `ilc_core/epoch/fee_burn_split_runtime.py` | Current quote runtime; unchanged |

## 3. Candidate Adaptive Rule

The candidate rule is:

```text
target_burn_ratio =
  clamp(
    late_floor_ratio,
    genesis_burn_ratio,
    late_floor_ratio
      + (genesis_burn_ratio - late_floor_ratio) * issuance_offset_ratio
      - stress_discount
  )
```

Where:

| Symbol | Candidate value | Meaning |
|---|---:|---|
| `genesis_burn_ratio` | `0.10` | Current CDL-028 fixed ratio |
| `late_floor_ratio` | `0.05` | SIM-008 late-economy burn-floor candidate |
| `issuance_offset_ratio` | `scheduled_issuance / (scheduled_issuance + fee_revenue)` | Higher when new issuance offsets burns |
| `stress_discount` | bounded by floor | Downward pressure under low-velocity stress |
| `max_epoch_delta` | `0.01` | Maximum burn-ratio movement per issuance epoch |

The rate-limited applied ratio is:

```text
next_burn_ratio =
  current_burn_ratio
    + clamp(-max_epoch_delta, max_epoch_delta, target_burn_ratio - current_burn_ratio)
```

All ratios are exact decimal governance parameters. The SIM data committed in
Phase 1549p represents them as decimal strings.

## 4. Governance Boundary

This rule is not live. A future activation would require:

1. A CDL opening or amendment that decides whether CDL-028 should remain fixed,
   become adaptive, or split into early/late regime rules.
2. A ratified set of public dashboard inputs for scheduled issuance, fee
   revenue, and velocity index.
3. A runtime implementation using exact decimal or fixed-point arithmetic.
4. Rate-limit, floor, and ceiling tests.
5. A separate activation gate after public economic telemetry exists.

## 5. Deterministic SIM Summary

The Phase 1549p SIM evaluates four deterministic scenarios:

| Scenario | Issuance offset | Velocity index | Target ratio | Converged path |
|---|---:|---:|---:|---|
| early_growth | `0.90` | `1.05` | `0.095` | `0.100 -> 0.095` |
| transition_balanced | `0.50` | `0.95` | `0.075` | `0.100 -> 0.090 -> 0.080 -> 0.075` |
| late_healthy | `0.10` | `1.00` | `0.055` | `0.100 -> 0.090 -> 0.080 -> 0.070 -> 0.060 -> 0.055` |
| late_low_velocity | `0.10` | `0.80` | `0.050` | `0.100 -> 0.090 -> 0.080 -> 0.070 -> 0.060 -> 0.050` |

The SIM is deliberately small. Its purpose is not to ratify parameters; it is to
show that the candidate rule is deterministic, monotonic under the selected
scenarios, bounded by the 5% floor and 10% ceiling, and rate-limited.

## 6. Closure of OBL-028

OBL-028 required a pre-RC adaptive fee-burn ratio spec/SIM for post-issuance
conditions. This specification and the companion deterministic SIM close that
pre-RC obligation.

```text
obl_028_adaptive_fee_burn_sim_committed_phase_1549p
obl_028_closed_phase_1549p
fee_burn_runtime_unchanged_phase_1549p
```

## 7. Non-Authorization

This specification does not change CDL-028, does not alter
`FEE_BURN_RATIO = Decimal("0.10")`, does not activate adaptive fee burn, does
not clear `fee_burn_not_activated_phase_1346`, does not write wallet, treasury,
settlement, ledger, or minting state, does not open or ratify a CDL, does not
activate public RC, and does not transition epoch.
