# ILC SIM-009 P_e Stabilization Commissioning 429 v0.1

Status: Phase-429 commissioning artifact
Date: 2026-03-16
Owner lane: G8 Constitution Cluster A

## 1. Scope and non-ratifying boundary

Phase 429 commissions SIM-009 as the Treasury P_e stabilization calibration evidence lane for Phase 430 synthesis.

Phase 429 commissions SIM-009 as the calibration evidence lane authorized by Phase 426 Scenario B disposition.
Modeled outputs are non-ratifying evidence inputs for Phase 430 synthesis and P_e stabilization disposition.
SIM-009 does not open, amend, or ratify any CDL row.

## 2. Implemented simulation module and P_e modeling scope

Implemented modules:
- `simulations/sim_009_pe_stabilization_429.py`
- `simulations/run_phase_429_sim_009.py`

The model sweeps deterministic P_e shock-and-recovery cases across positive and negative shock
 directions, trigger thresholds, intervention limit fractions, and treasury activity scenarios.

The commissioning scope is bounded to Treasury P_e stabilization evidence generation for
 `docs/specs/ilc_treasury_pe_stabilization_governance_review_426_v0.1.md` and does not determine
 the constitutional disposition itself.

## 3. Parameter grid and intervention model context

Parameter grid:
- `PE_TARGET = 1.0`
- `PE_SHOCK_MAGNITUDES = [0.10, 0.20, 0.30, 0.40]`
- `SHOCK_DIRECTIONS = ["negative", "positive"]`
- `PE_TRIGGER_THRESHOLDS = [0.05, 0.10, 0.15, 0.20]`
- `PE_INTERVENTION_LIMIT_FRACTIONS = [0.02, 0.05, 0.10, 0.15]`
- `ECONOMIC_SCENARIOS = ["low_activity", "medium_activity", "high_activity"]`

Economic scenarios modulate the Treasury budget baseline with `low_activity = 0.8 * B_e`,
`medium_activity = 1.0 * B_e`, and `high_activity = 1.2 * B_e`.

CDL-030 sets the P_e clamp range [0.75, 1.30] but does not set trigger or limit constants for intervention.
`docs/specs/ilc_sim_008_commissioning_results_406_v0.1.md` remains the prior late-economy evidence anchor, but Phase 426 determined it is insufficient on its own for Treasury P_e trigger and limit locking.

## 4. Output artifacts and reproducibility declaration

Published output root:
- `out/simulations/sim_009_pe_stabilization/results.csv`
- `out/simulations/sim_009_pe_stabilization/results.tsv`
- `out/simulations/sim_009_pe_stabilization/summary_table.md`
- `out/simulations/sim_009_pe_stabilization/run_manifest.json`

The runner is deterministic, uses a fixed seed contract, emits only text artifacts, and reproduces
byte-identical outputs on rerun.

## 5. Recommended P_e trigger threshold results

SIM-009 recommends a P_e trigger threshold candidate of 0.2.

The selected threshold maximizes mean `policy_score` across all commissioned shock magnitudes,
both shock directions, and all three economic scenarios after applying the deterministic tie-break
rule.

## 6. Recommended P_e intervention limit results

SIM-009 recommends a P_e intervention limit fraction candidate of 0.02.

The selected intervention limit fraction produces the best average stability/recovery trade-off in
this commissioned parameter sweep while preserving the same deterministic tie-break rule used for
the trigger threshold recommendation.

## 7. Carry-forward constraints for Phase 430 synthesis and P_e constitutional lane planning

Phase 430 must treat the SIM-009 recommendations as evidence inputs, not constitutional locks.

Phase 430 should evaluate whether the recommended pair `(0.2, 0.02)` is sufficient for a future
P_e constitutional lane or whether additional narrowing, carry-forward, or next-window sequencing is
still required.

The constitutional disposition remains downstream of `docs/specs/ilc_treasury_pe_stabilization_governance_review_426_v0.1.md` and the SIM-009 outputs produced here.

## 8. Out-of-scope and non-goals

- no CDL-050 opening in Phase 429,
- no P_e constants locked in Phase 429,
- no `ilc_core/` runtime mutation,
- no modification to CDL-030, CDL-047, SIM-008 commissioning results.

No decision-log mutation occurred. No ilc_core runtime files were changed.
