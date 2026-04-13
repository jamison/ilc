# ILC SIM-NUMERIC-01 Representation Evaluation 633 v0.1

Status: simulation synthesis
Date: 2026-04-13
Window: 631-636
Phase: 633
Owner lane: G8 tier-0 economic numeric determinism strike force

## 1. Simulation identity and question

SIM-NUMERIC-01 evaluates which exact-numeric direction is the best fit for the
bounded Tier-0 strike-force lane.

Question:
- which representation should CDL-064 ratify now for Tier-0 runtime-critical
  economic, ledger, and staking surfaces?

`sim_numeric_01_representation_evaluation_complete`

## 2. Parameters and assumptions

The simulation packet evaluates three options:
- option A: `retain-float-rounding-and-tolerance`
- option B: `exact-decimal-runtime-contract`
- option C: `fixed-point-minor-unit-contract`

Representative scenarios:
- repeated decimal accumulation and debit
- proportional reward distribution over stake shares
- settlement replay verification
- canonical export / persistence round-trip
- cross-language consumer reconstruction from machine output

Evaluation criteria:
- deterministic replay behavior
- arithmetic exactness
- canonical serialization stability
- storage/export compatibility
- migration complexity
- cross-language portability

Assumptions:
- the lane is bounded to Tier-0 and should not silently ratify a global ECU/ILC
  subunit policy unless necessary
- the ratified answer must be implementable inside Window 631-636
- simulations and analytics are not first-pass migration targets

## 3. Analysis

### Option A — retain float with rounding and tolerance

Pros:
- lowest short-run migration effort
- preserves current JSON and storage shapes

Cons:
- deterministic replay behavior still depends on epsilon and rounding heuristics
- arithmetic exactness fails on many decimal fractions
- canonical serialization stability remains representation-by-approximation
- storage/export compatibility is superficial because the exported contract is
  still inexact
- cross-language portability is weak because exactness is not part of the
  contract

### Option B — exact decimal runtime contract

Pros:
- deterministic replay behavior is strong when paired with canonical decimal
  strings
- arithmetic exactness is preserved for decimal economic values
- canonical serialization stability is strong with normalized base-10 strings
- storage/export compatibility is manageable because current JSON stores can
  carry decimal strings cleanly
- migration complexity is medium and bounded
- cross-language portability is strong enough because any implementation can
  consume canonical decimal strings and exact decimal arithmetic

Cons:
- not as compact as fixed-point integers
- requires careful canonicalization rules to avoid string-shape drift

### Option C — fixed-point minor-unit contract

Pros:
- deterministic replay behavior is strong
- arithmetic exactness is strong
- canonical serialization stability is strong once scale is fixed
- cross-language portability is strongest once a universal scale is ratified

Cons:
- storage/export compatibility requires ratifying and applying a canonical
  minor-unit scale first
- migration complexity is highest in this bounded lane
- choosing the scale now would smuggle a divisibility-policy decision into a
  numeric-hardening strike force

## 4. Results

| Criterion | Option A | Option B | Option C |
|---|---|---|---|
| deterministic replay behavior | fail | pass | pass |
| arithmetic exactness | fail | pass | pass |
| canonical serialization stability | weak | pass | pass |
| storage/export compatibility | medium | pass | medium |
| migration complexity | easiest | acceptable | hardest |
| cross-language portability | weak | pass | pass+ |

Simulation verdict:
- option A fails the mission because float retention keeps epsilon and rounding
  in the correctness path
- option B is the best bounded choice for this window
- option C is architecturally attractive but overreaches this lane because it
  requires ratifying a minor-unit scale that is not yet the subject of the
  strike force

`sim_numeric_01_option_a_float_rounding_rejected`
`sim_numeric_01_option_b_exact_decimal_recommended`
`sim_numeric_01_option_c_fixed_point_not_selected_for_cdl_064_v1`

## 5. Governance dispositions

Disposition 1:
- recommend ratifying option B `exact-decimal-runtime-contract` in Phase 634

Disposition 2:
- reject option A `retain-float-rounding-and-tolerance` for Tier-0

Disposition 3:
- keep option C `fixed-point-minor-unit-contract` available as a later
  architecture lane if the repo later chooses to ratify a canonical minor-unit
  scale deliberately rather than by accident

The simulation therefore recommends:
- exact decimal internal runtime arithmetic
- canonical decimal-string machine serialization
- explicit rejection of epsilon-based correctness after migration

## 6. Forward pointer

Phase 634 should ratify the option B direction in narrow form as CDL-064.
Phase 635 should migrate the Tier-0 target surface to exact decimal state and
canonical decimal-string serialization, while leaving repo-wide simulation and
analytics cleanup outside the initial strike-force boundary.
