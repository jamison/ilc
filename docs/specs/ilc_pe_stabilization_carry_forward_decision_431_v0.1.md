# ILC P_e Stabilization Carry-Forward Decision 431 v0.1

Status: Phase-431 carry-forward publication artifact
Date: 2026-03-17
Owner lane: G8 Constitution Cluster A

## 1. Scope and non-ratifying boundary

Phase 431 is a non-ratifying carry-forward decision publication and does not open, amend, or ratify any CDL row.

This artifact formally closes the Treasury P_e branch for Window 424-433 under Scenario B. CDL-050
was not opened in Window 424-433, and Phase 431 does not amend CDL-047 or lock any Treasury P_e
constants.

## 2. Window 424-433 P_e branch summary

Scenario B is the authorized tail path for Window 424-433 as determined by Phase 426.

Phase 426 concluded that SIM-009 was required before any Treasury P_e constitutional locking could
be justified. Phase 429 commissioned and ran SIM-009. Phase 430 synthesized the commissioned
results, concluded that the model is insufficient for in-window constitutional locking, and
constrained Phase 431 to publish the carry-forward decision rather than open or ratify a new
constitutional lane.

## 3. SIM-009 established findings

The SIM-009 recommendation pair 0.2 / 0.02 is a provisional planning anchor for the P_e constitutional lane.

Phase 430 is the authoritative source for the three findings that govern this carry-forward
decision:
- the trigger-coupled recovery criterion creates a built-in scoring advantage for higher trigger
  thresholds,
- the intervention-limit differentiation inside the trigger = 0.20 cluster is too weak to support
  a constitutionally robust selection,
- the floating-point boundary at `(shock_magnitude = 0.10, trigger_threshold = 0.10)` behaves as a
  no-intervention case in the deterministic implementation.

Treasury P_e trigger and limit constants are not constitutionally justified for immediate locking on the basis of SIM-009 alone.

## 4. Prerequisites for P_e constitutional lane advancement

Window 434+ may advance the Treasury P_e constitutional lane only after satisfying at least one of
the following carry-forward prerequisites sourced from Phase 430:
- a recovery criterion decoupled from the trigger threshold,
- an explicit treasury-risk tolerance judgment,
- additional simulation evidence that directly discriminates intervention-limit trade-offs.

These are conditions for future advancement, not mandates on a single implementation path.

## 5. Carry-forward decision

The P_e constitutional lane carries into Window 434+ as the default continuation target.

Phase 431 adopts the SIM-009 recommendation pair `0.2 / 0.02` as a provisional planning anchor
only. No Treasury P_e trigger or limit constants are locked by this decision. Any future
constitutional action on the Treasury P_e lane must first satisfy at least one of the Section 4
prerequisites and then respect standard constitutional opening, prelock, and ratification
discipline.

CDL-049 remains independent of the Treasury P_e lane and is unaffected by Phase 431.

## 6. Non-goals and canonical anchors

Non-goals:
- no mutation to `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- no opening of `CDL-050`,
- no amendment to `CDL-047`,
- no changes to Phase 426, Phase 429, or Phase 430 artifacts,
- no `ilc_core/` runtime mutation.

Canonical anchors:
- `docs/specs/ilc_treasury_pe_stabilization_governance_review_426_v0.1.md`
- `docs/specs/ilc_sim_009_pe_stabilization_commissioning_429_v0.1.md`
- `docs/specs/ilc_sim_009_results_synthesis_and_pe_stabilization_disposition_430_v0.1.md`
- `out/simulations/sim_009_pe_stabilization/summary_table.md`
- `out/simulations/sim_009_pe_stabilization/run_manifest.json`
- `out/simulations/sim_009_pe_stabilization/results.csv`

No decision-log mutation occurred. No ilc_core runtime files were changed.
