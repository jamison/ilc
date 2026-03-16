# ILC SIM-009 Results Synthesis and P_e Stabilization Disposition 430 v0.1

Status: Phase-430 synthesis artifact
Date: 2026-03-16
Owner lane: G8 Constitution Cluster A

## 1. Scope and non-ratifying boundary

Phase 430 is a non-ratifying synthesis phase and does not open, amend, or ratify any CDL row.

This artifact synthesizes the commissioned SIM-009 outputs for Treasury P_e stabilization planning.
It records what the Phase 429 model does and does not justify, and it constrains what Phase 431 may
publish as the carry-forward decision for the constitutional lane.

## 2. SIM-009 headline results recap

SIM-009 recommends a P_e trigger threshold candidate of 0.2 and a P_e intervention limit fraction candidate of 0.02 under the commissioned model.

The Phase 429 summary table shows the trigger `0.20` cluster occupying all four top positions by
average policy score, with `0.20 / 0.02` ranked first at `0.960457` and `0.20 / 0.10` effectively
adjacent at `0.960000`.

These outputs are evidence inputs for disposition planning, not constitutional locks.

## 3. Recovery-criterion coupling limitation

SIM-009's recovery criterion is trigger-coupled: pe_recovery_epochs is defined by |P_e - PE_TARGET| < pe_trigger_threshold.

This coupling creates a built-in scoring advantage for higher trigger thresholds and weakens the constitutional force of the recommended pair.
A trigger threshold of `0.20` is rewarded partly because the model declares recovery once the price
is within twenty percent of target, while smaller thresholds must satisfy a materially stricter
convergence condition.

## 4. Limit-fraction differentiation assessment

The score spread among trigger = 0.20 intervention-limit candidates is too small to treat 0.02 as a constitutionally robust winner.
The full spread from `0.20 / 0.02` to `0.20 / 0.15` is only about `0.007057`, and the gap between
`0.20 / 0.02` and `0.20 / 0.10` is about `0.000457`, which is not strong evidence for a durable
constitutional distinction among the leading intervention-limit choices.

Resolving the sub-choice among trigger = 0.20 intervention-limit candidates requires either a recovery criterion decoupled from the trigger threshold, an explicit treasury-risk tolerance judgment, or additional simulation evidence that directly discriminates intervention-limit trade-offs.

## 5. Floating-point trigger-boundary note

Floating-point boundary behavior means shock_magnitude = 0.10 and pe_trigger_threshold = 0.10 behaves as a no-intervention case in the current deterministic implementation.
In those rows, the absolute deviation falls infinitesimally below the trigger comparison threshold,
so Treasury drawdown remains `0.0` and the model records a maximal policy score for that case.
This behavior is deterministic and repeatable, but it weakens any attempt to interpret the
`0.10 / 0.10` boundary as a crisp intervention threshold in constitutional terms.

## 6. Disposition verdict for the Treasury P_e constitutional lane

Phase 430 disposition: SIM-009 is insufficient for in-window constitutional locking of Treasury P_e trigger and limit constants.

SIM-009 does support the narrower conclusion that high trigger thresholds perform best under the
commissioned model's scoring rules. It does not, however, justify locking a Treasury P_e trigger and
limit pair in Window 424-433 because the dominant trigger recommendation is partly model-induced and
the leading intervention-limit candidates remain weakly differentiated.

CDL-049 remains independent of the Treasury P_e lane and is unaffected by Phase 430.

## 7. Phase 431 carry-forward constraints

Phase 431 should publish the carry-forward decision for the Treasury P_e constitutional lane with Window 434+ as the default continuation target.

That publication should treat the SIM-009 recommendation pair `0.2 / 0.02` as a provisional
planning anchor only, preserve the Phase 426 Scenario B branch decision, and avoid any implication
that Treasury P_e constants are already constitutionally justified for immediate locking.

## 8. Non-goals and canonical anchors

Canonical anchors:
- `docs/specs/ilc_treasury_pe_stabilization_governance_review_426_v0.1.md`
- `docs/specs/ilc_sim_009_pe_stabilization_commissioning_429_v0.1.md`
- `out/simulations/sim_009_pe_stabilization/results.csv`
- `out/simulations/sim_009_pe_stabilization/summary_table.md`
- `out/simulations/sim_009_pe_stabilization/run_manifest.json`
- `docs/specs/ilc_cdl_030_ecu_price_clamp_candidate_lock_277_pre1_v0.1.md`
- `docs/specs/ilc_cdl_047_treasury_governance_ratification_evidence_418_v0.1.md`

No decision-log mutation occurred. No ilc_core runtime files were changed.
