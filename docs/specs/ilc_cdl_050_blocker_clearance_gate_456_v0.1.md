# ILC CDL-050 Blocker-Clearance Gate 456 v0.1

Status: Phase-456 blocker-clearance gate
Date: 2026-03-25
Owner lane: G8 Constitution Cluster A

## 1. Gate conditions evaluated

Phase 456 evaluates the four gate conditions that must all clear before Phase 457 may open
`CDL-050`:

- `Blocker 1` - recovery-rule closure
- `Blocker 2` - risk-tolerance closure
- `Blocker 3` - discriminating-evidence closure
- `L1/L2 prerequisite` - explicit prerequisite satisfaction against the Phase-452 boundary

Evidence base used for this gate:

- `docs/specs/ilc_treasury_objective_function_and_observables_contract_451_v0.1.md`
- `docs/specs/ilc_cdl_050_l1_l2_prerequisite_disposition_452_v0.1.md`
- `docs/specs/ilc_treasury_sim_t_commission_brief_453_v0.1.md`
- `docs/specs/ilc_treasury_sim_t_evidence_package_454_v0.1.md`
- `docs/specs/ilc_treasury_sim_t_comparative_synthesis_455_v0.1.md`
- `out/treasury_sim/phase_454/scenario_results.csv`

No decision-log mutation occurs in Phase 456.

## 2. Blocker 1 verdict

phase_456_blocker_1_verdict=remains_open

Verdict: `remains open`

Reasoning:

The structural anti-coupling requirements are satisfied: the registered recovery-rule family uses
an organic-production observable distinct from the trigger observable, multiple candidate rules
were compared, and false-exit / late-exit behavior was explicitly measured under the registered
Scenario 5 family.

The blocker nevertheless remains open because the registered recovery-rule success objective is not
cleanly satisfied by the evidence surface. Phase 455 records Scenario 5 as only directionally
rather than materially discriminating. `production_band_5_epoch` is the strongest false-exit-
resistant candidate, but it does not clear the registered materiality thresholds on the scenario's
primary observables.

Against `production_band_3_epoch`, the lead candidate improves:

- organic ECU production from `0.88` to `0.91`, which is only `3.4` percentage points and does
  not clear the registered `10` percentage-point separation threshold,
- `P_e` clamp-respect from `0.84` to `0.86`, which is only `2.4` percentage points and does not
  clear the registered `5` percentage-point separation threshold.

Against `mixed_queue_and_production`, the lead candidate improves:

- organic ECU production from `0.83` to `0.91`, which is `9.6` percentage points and still falls
  just short of the registered `10` percentage-point separation threshold,
- `P_e` clamp-respect from `0.82` to `0.86`, which is `4.9` percentage points and still falls
  just short of the registered `5` percentage-point separation threshold.

Duration and cost do separate inside the family. The actual failure surface is insufficient
separation on organic-production and clamp-respect.

Under the Phase-453 ambiguous-outcome policy, that ambiguity preserves the blocker rather than
forcing closure.

## 3. Blocker 2 verdict

phase_456_blocker_2_verdict=cleared

Verdict: `cleared`

Reasoning:

Every ECU-side lever family used in Window 450-459 is explicitly bounded in the Phase-453
commission brief:

- escrow multiplier family: `2x`, `5x`, `10x`, `20x`
- vesting-extension family: `10`, `25`, `50`, `100` additional epochs
- recovery-rule family: bounded to the registered candidate set
- stress and cost accounting families: frozen before execution

No uncapped lever remains inside the registered SIM-T surface because Phase 453 bars post-start
family widening without invalidating the brief.

Categorical prohibitions are explicit in Phase 452: L1 Treasury does not read or respond directly
to L2 derivative-market state, and L2 liquidation pressure is not a direct L1 intervention input.

Worst-case intervention cost is bounded from simulation evidence. Across the registered Phase-454
runs, the highest measured intervention profile is `18 epochs / 0.49 units` in the contagion-
coupled counterfactual, which establishes a finite upper bound for the tested window even though
that counterfactual is not the adopted boundary model.

## 4. Blocker 3 verdict

phase_456_blocker_3_verdict=cleared

Verdict: `cleared`

Reasoning:

Phase 455 resolves the registered Blocker 3 family (`Scenario 4 - Long-tail zero-issuance stress
 test`) as materially discriminating.

`mixed_control` exceeds `bounty_focus` by `19` percentage points and `escrow_focus` by `11`
percentage points on the governing queue-clearance surface under the fixed `300%` verification-
request spike. That clears the registered discrimination threshold and satisfies the requirement
that the lead choice be materially separated rather than merely directionally preferred.

## 5. L1/L2 prerequisite verdict

phase_456_l1_l2_verdict=cleared

Verdict: `cleared`

Reasoning:

Phase 452 explicitly adopts L1/L2 separation as a CDL-050 prerequisite and freezes the interface
boundary.

Phase 454 and Phase 455 then test that boundary through `Scenario 3 - L1/L2 contagion isolation
 test`. `boundary_enforced` materially outperforms both `partial_leakage` and
`contagion_coupled` on the registered primary observables, and the catastrophic cross-layer signal
remains boundary evidence only rather than ordinary-operating authorization.

The prerequisite is therefore not merely asserted. It is both constitutionally adopted and
materially supported by the registered counterfactual evidence.

## 6. Overall gate verdict

phase_456_overall_verdict=fail

Overall verdict: `fail`

The overall gate fails because `Blocker 1` remains open. `Blocker 2`, `Blocker 3`, and the
L1/L2 prerequisite are cleared, but Phase 456 requires all four gate conditions to clear before
Phases 457-459 can proceed.

## 7. Authorization or carry-forward

Phases 457-459 must not proceed.

CDL-050 carry-forward memo:

- `Blocker 1` remains open because the registered recovery-rule family still carries practical
  ambiguity under Scenario 5 on organic-production and clamp-respect separation, not on
  duration/cost.
- Window 450-459 therefore stops at Phase 456 and does not authorize CDL-050 opening.
- Any future attempt to reopen the lane requires a new sequence lock or equivalent explicit
  authorization outside the failed Window 450-459 path.
- The required carry-forward focus is narrow: strengthen recovery-rule evidence until a candidate
  exits on normalized organic production and materially separates on organic-production and
  clamp-respect under the registered thresholds.
