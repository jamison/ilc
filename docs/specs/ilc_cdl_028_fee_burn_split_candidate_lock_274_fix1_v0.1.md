# ILC CDL-028 Fee-Burn Split Candidate Lock 274 Fix 1 v0.1

Status: Non-ratifying pre-ratification evidence artifact
Date: 2026-02-23
Window: Phase 274-fix1

## 1. Purpose and non-ratifying boundary

This artifact locks a deterministic simulation-backed candidate for `CDL-028` input to the sensitive Phase 274 ratification lane.

Boundary statement:
- This phase is non-ratifying.
- No decision-log mutation occurred in this phase.
- `CDL-028` remains open until the sensitive Phase 274 ratification lane executes.

## 2. Historical simulation provenance anchors

Recovered historical simulation lineage used for this prelock:
- `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt:6134-6389`
- `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt:6998-7198`
- `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt:19890-19926`
- `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt:20110-20230`

Recovered script copies:
- `simulations/historical_recovered/sim_controller_telemetry_80_epoch_recovered_20251009.py`
- `simulations/historical_recovered/sim_kappa_ab_recovered_20251009.py`

## 3. Modeling coverage against Phase-256 requirement set

Reference: `docs/specs/ilc_issuance_parameter_analysis_256_v0.1.md` section 4.

Coverage produced in this phase:
- long-horizon issuance sustainability across terminal model variants: covered via horizon set `{120, 360, 720}` and terminal models `{A, B, C}` with sustainability scoring,
- cap sensitivity and emission-curve sweeps: covered via cap-sensitivity scoring under emission curves `{halving, exp_decay, tail}`,
- fee-burn split incentive impact under adversarial usage: covered via adversarial pressure variants `{baseline, stressed}` and adversarial scoring,
- allocation split resilience under concentration/gaming: covered via allocation variants `{80/15/5, 75/20/5, 70/20/10}` and resilience scoring,
- clamp-bound stability under volatile reward demand: covered via clamp-volatility variants `{low, medium, high}` and clamp stability scoring.

## 4. Candidate sweep setup and deterministic methodology

Implementation artifact:
- `simulations/sim_cdl_028_fee_burn_candidate_sweep_274_fix1.py`

Determinism contract:
- fixed seed: `20260223`,
- deterministic scenario-key hash noise,
- deterministic candidate set: `0.05`, `0.10`, `0.15`, `0.20`, `0.30`, `0.50`.

Hard constraints applied before winner selection:
- `clamp_stability_score <= 0.15`,
- `allocation_resilience_score <= 0.35`,
- `adversarial_incentive_score <= 0.35`.

Selection rule:
- choose lowest `composite_score` among candidates that pass all hard constraints.

Calibration disclosure:
- penalty anchors in the scoring geometry (`0.10`, `0.11`, `0.12`) were calibrated to align with prior Phase-256/271 economic analysis; they are deterministic working parameters for this prelock and are not independently ratified policy constants.

Output artifacts:
- `out/phase_274_fix1/cdl_028_fee_burn_candidate_sweep.csv`
- `out/phase_274_fix1/cdl_028_candidate_selection.json`

## 5. Selected canonical candidate for Phase 274 ratification input

Selected candidate from deterministic sweep:
- decimal: `0.10`
- percentage: `10%`
- CDL-028 option token: `other percentages`
- composite score: `0.065477`

Runner-up candidates and rejection rationale:
1. candidate `0.15` (`15%`, option `other percentages`) — rejected due to higher composite score (`0.090559`) than selected candidate.
2. candidate `0.05` (`5%`, option `other percentages`) — rejected due to higher composite score (`0.096036`) than selected candidate.

Named-option viability under this constraint set:
- `0.30` (`30% burn`) and `0.50` (`50% burn`) failed hard constraints in this sweep and were not eligible for winner selection.

Phase 274 ratification carry-forward rule:
- the sensitive Phase 274 lane must copy this selected value unchanged and must not override it.

## 6. Residual evidence gaps and downstream treatment

Residual gaps after this prelock:
- objective-function policy formalization gap: the weighting model is deterministic here, but constitutional ratification of long-term weighting policy remains out of scope,
- downstream coupling gap for decay/clamp lanes: full integration with `CDL-027` and `CDL-030` remains in later phases.

Downstream treatment:
- carry residuals into Phase 275-277 evidence/ratification lanes,
- keep Phase 274 scoped to locking `CDL-028` using this candidate output, without widening policy scope.

Sensitive ratification boundary reminder:
- Phase 274 main lane remains the only lane allowed to mutate the `CDL-028` decision-log row.

## 7. Canonical anchors

- `docs/specs/ilc_issuance_parameter_analysis_256_v0.1.md`
- `docs/specs/ilc_issuance_evidence_closure_b_271_v0.1.md`
- `docs/specs/ilc_cdl_026_cmax_lock_ratification_evidence_273_v0.1.md`
- `docs/specs/ilc_cdl_028_simulation_recovery_and_gap_map_274_prep_v0.1.md`
- `docs/specs/ilc_phase_270_279_sequence_lock_v0.1.md`
- `docs/antigravity_tasks/antigravity_prompt__phase_274_g8_constitution_cluster_a_cdl_028_fee_burn_split_candidate_simulation_prelock_fix1.md`
