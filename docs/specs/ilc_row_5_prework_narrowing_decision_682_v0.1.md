# ILC Row-5 Prework Narrowing Decision 682 v0.1

Status: decision artifact
Date: 2026-04-15
Phase: 682
Owner lane: G8 row-5 privacy-preserving public-legitimacy prework

## 1. Decision target

This decision determines whether Window 677-682 reduced row 5 enough to move it
from `not_started` to a bounded `partial` posture.

`row_5_advances_to_partial_in_682_not_closed`
`window_677_682_meets_minimum_acceptable_result_not_best_case_only`

## 2. Evidence basis

The evidence basis for this decision is:
- Phase 677 sequence lock and canon inventory
- Phase 678 privacy threat model
- Phase 679 observability budget
- Phase 680 mechanism-family matrix
- Phase 681 simulation and red-team packet

The lane produced all artifacts promised by the minimum acceptable result.

## 3. Decision

Decision:
- row 5 advances from `not_started` to `partial`
- row 5 does not close in this window

Why:
- the privacy problem is now narrowed to public-submission correlation
  minimization and unlinkability
- the observability floor is fixed as a hard constraint
- candidate families are now classified into near-term, later-stage, and
  inadmissible buckets
- the lane has simulation and red-team evidence with an explicit degradation
  metric

What did not happen:
- no final mechanism-family winner was selected
- no final substrate-specific proof was produced
- no final live implementation or cryptographic proof package was produced

## 4. Remaining gap after this window

`remaining_gap_substrate_specific_mechanism_and_live_proof_not_yet_complete`
`later_cdl_vehicle_plausible_but_not_opened_here`

The explicit remaining gap after Window 677-682 is:
- choose or narrow further against a concrete later settlement architecture
- prove that a specific mechanism family satisfies the row-5 observability floor
  in real implementation terms
- validate real leakage behavior beyond this scenario-model packet
- decide whether a dedicated later CDL vehicle is needed for final mechanism
  closure

That remaining gap is now explicit rather than vague.

## 5. Carry-forward consequence

The carry-forward consequence is:
- row 5 is no longer blank
- row 5 remains unresolved at final-mechanism level
- later substrate and privacy work must inherit this narrowed problem statement
  and observability budget rather than re-expanding row 5 into generic privacy

Window 677-682 therefore succeeds as a narrowing lane and fails, by design, as
a full closure lane.
