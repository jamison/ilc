# ILC CDL-030 ECU Price Clamp Candidate Lock 277 Pre1 v0.1

Status: Phase-277-pre1 non-ratifying evidence artifact
Date: 2026-02-23
Owner lane: G8 Constitution Cluster A
Target decision: `CDL-030`

## 1. Purpose and non-ratifying boundary

This artifact publishes a deterministic, simulation-backed candidate lock for `CDL-030` (`P_min`, `P_max`) before sensitive ratification in Phase 277.

Non-ratifying boundary:
- no CDL status mutation,
- no decision-log field mutation,
- no runtime behavior changes.

No decision-log mutation occurred in this phase.

## 2. Ratified schedule dependency anchor (Phase 276)

Clamp candidate derivation is anchored to ratified `CDL-027` schedule constants:
- formulation: `halving`,
- constant: `H=48`,
- epoch duration: `1 month`.

Source: `docs/specs/ilc_cdl_027_decay_formulation_ratification_evidence_276_v0.1.md`.

## 3. Parameter-envelope rationale and validity filters

Envelope for this prelock sweep:
- `P_min` range: `0.60` to `0.95` (`0.05` step),
- `P_max` range: `1.05` to `1.80` (`0.05` step).

Validity filters:
- `P_max > P_min`,
- clamp width floor: `P_max - P_min >= 0.20`,
- clamp width ceiling: `P_max - P_min <= 0.90`.

Rationale:
- floor/ceiling constraints avoid degenerate narrow or ultra-wide clamp surfaces,
- envelope provides a broad 2D search while preserving bounded governance semantics,
- candidate selection remains deterministic and replayable.

## 4. Modeling coverage against Phase-275 CDL-030 methodology

This prelock sweep covers Phase-275 methodology requirements:
- issuance-schedule dependency anchoring,
- volatility scenario evaluation (`low`, `medium`, `high`),
- bound-respect and stability scoring,
- convergence and anti-oscillation scoring,
- utility continuity scoring,
- deterministic candidate ranking under hard constraints.

## 5. Candidate sweep setup and deterministic methodology

Simulation artifact: `simulations/sim_cdl_030_price_clamp_candidate_sweep_277_pre1.py`

Deterministic controls:
- seed: `20260223`,
- stable hash-based micro-perturbation for non-flat deterministic scoring,
- deterministic output ordering and serialization.

Output artifacts:
- CSV sweep table: `out/phase_277_pre1/cdl_030_price_clamp_candidate_sweep.csv`
- JSON candidate lock: `out/phase_277_pre1/cdl_030_price_clamp_candidate_selection.json`

Observed valid candidate count: `102`.

Hard constraints before ranking:
- `bound_respect_score <= 0.05`,
- `clamp_stability_score <= 0.20`,
- `anti_oscillation_score <= 0.20`.

## 6. Robustness summary over top-ranked valid candidates

Top-ranked valid candidates by composite score:
1. `P_min=0.75`, `P_max=1.30`, width `0.55`, composite `0.056040` (selected)
2. `P_min=0.75`, `P_max=1.35`, width `0.60`, composite `0.057076`
3. `P_min=0.80`, `P_max=1.35`, width `0.55`, composite `0.059724`

Interpretation:
- top-ranked candidates cluster around width `0.55` to `0.60`,
- stability and anti-oscillation constraints prune wider/high-variance candidates,
- selected candidate is not a hand-picked pair; it emerges from the 2D mesh and hard constraints.

## 7. Selected canonical `P_min` / `P_max` candidate for Phase 277 ratification input

Selected candidate from deterministic sweep:
- `P_min = 0.75`
- `P_max = 1.30`
- clamp width: `0.55`

Selection basis:
- lowest composite score among candidates that pass all hard constraints.

This is a pre-ratification lock only.
Final ratification remains in sensitive Phase 277 (`CDL-030` lane).

## 8. Residual evidence gaps and downstream treatment

Residual gaps:
- no live-market replay in this phase,
- no long-horizon adaptive retuning policy in this phase,
- no runtime activation evidence in this phase.

Downstream treatment:
- Phase 277 ratification may only bind `P_min`/`P_max` values from this artifact,
- any adaptive retuning policy remains out-of-scope and requires a separate CDL lane,
- runtime integration remains deferred until post-ratification implementation windows.

## 9. Canonical anchors

- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_issuance_parameter_analysis_256_v0.1.md`
- `docs/specs/ilc_issuance_evidence_closure_c_275_v0.1.md`
- `docs/specs/ilc_cdl_027_decay_formulation_ratification_evidence_276_v0.1.md`
- `docs/specs/ilc_economic_risk_monitoring_contract_v0.1.md`
- `out/phase_277_pre1/cdl_030_price_clamp_candidate_sweep.csv`
- `out/phase_277_pre1/cdl_030_price_clamp_candidate_selection.json`
