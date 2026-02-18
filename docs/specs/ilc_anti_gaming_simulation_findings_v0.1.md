# ILC Anti-Gaming Simulation Findings v0.1

Status: reviewer context summary
Date: 2026-02-18
Scope: anti-gaming rationale and implementation-state mapping

## 1. Purpose

Capture anti-gaming design rationale in one reviewer-facing artifact that links historical corpus context to current ratified implementation surfaces.

## 2. Evidence basis

This summary is based on:
- historical corpus extraction outputs:
  - `docs/research/constitution_dredge_raw_v0.1.jsonl`
  - `docs/research/constitution_dredge_matrix_v0.2.md`
- ratified constitutional and governance artifacts:
  - `docs/specs/ilc_constitutional_decision_log_v0.1.md`
  - `docs/specs/ilc_governance_conflict_set_ratification_v0.1.md`
  - `docs/specs/ilc_cdl_011_015_ratification_evidence_bundle_v0.1.md`
- implemented code and tests through Phase 224.

## 3. Historical corpus signals relevant to gaming defense

Representative raw-ledger examples indicating long-running focus on stake, challenge, quorum, and anti-spam economics:
- `raw-000018` stake requirement for high-value work.
- `raw-001378` contradiction rewards tied to invalidation success.
- `raw-001693` validator staking and slashing expectations.
- `raw-002086` quorum or validator checks for pruning decisions.
- `raw-005021` graph-weighted validation to disincentivize spam through low reuse.
- `raw-006773` quorum threshold framing for governance actions.
- `raw-006854` stake and earned influence framing for public graph publication.

Source anchor: `docs/research/constitution_dredge_raw_v0.1.jsonl`.

## 4. Implemented anti-gaming controls (current)

### 4.1 Refutation-profitability invariant

- Mechanism: refutation utility multiplier and pairwise profitability assertion for equivalent work.
- Economic intent: make correction of bad claims more profitable than passive validation.
- Anchors:
  - `ilc_core/analysis/utility_flow_rewards.py`
  - `tests/test_refutation_profitability_invariant_phase_212.py`
  - `tools/check_refutation_profitability_invariant_phase_212.sh`

### 4.2 Reuse-diversity anti-Sybil weighting

- Mechanism: concentration penalties and floor-bounded multiplier based on distinct-agent reuse and max single-agent share.
- Economic intent: penalize single-actor reuse inflation and reward cross-agent reuse.
- Current default policy anchors:
  - `min_distinct_agents = 2`
  - `max_single_agent_share = 0.75`
  - `penalty_floor = 0.85`
- Anchors:
  - `ilc_core/analysis/reuse_diversity_invariants.py`
  - `tests/test_reuse_diversity_invariants_phase_216.py`
  - `tools/check_reuse_diversity_invariants_phase_216.sh`

### 4.3 Freshness gate with Genesis exemption

- Mechanism: exponential decay with bounded floor and Genesis bypass.
- Economic intent: reduce stale-claim passive capture while preserving permanent Genesis axioms.
- Current default policy anchors:
  - `decay_lambda = 0.25`
  - `freshness_floor = 0.85`
  - `genesis_exempt = True`
- Anchors:
  - `ilc_core/analysis/freshness_gate.py`
  - `tests/test_freshness_gate_phase_217.py`
  - `tools/check_freshness_gate_invariants_phase_217.sh`

### 4.4 Path-lift counterfactual with provenance

- Mechanism: replayable path-lift scoring with witness-level node and agent provenance preservation.
- Economic intent: provide marginal-contribution signal while retaining visibility for downstream detection of self-referential inflation patterns.
- Anchors:
  - `ilc_core/analysis/path_lift_counterfactual.py`
  - `docs/specs/ilc_path_lift_counterfactual_contract_v0.1.md`
  - `tests/test_path_lift_counterfactual_phase_214.py`

### 4.5 Genesis accrual governor hard-cap and taper

- Mechanism: cap and taper for Genesis share trajectory.
- Economic intent: bound early concentration while preserving deterministic issuance controls.
- Locked constants:
  - `theta_hard = 1/20`
  - `theta_soft = exp(-3)`
- Anchors:
  - `ilc_core/analysis/genesis_accrual_governor.py`
  - `tests/test_genesis_accrual_governor_phase_218.py`
  - `tools/check_genesis_accrual_governor_phase_218.sh`

### 4.6 Consolidated conformance and full-stack smoke

- Mechanism: composition-level conformance plus deterministic end-to-end integration and install-import checks.
- Economic intent: prevent hidden cross-module seams that reintroduce exploitable behavior.
- Anchors:
  - `ilc_core/analysis/node_value_governance_conformance.py`
  - `tests/test_node_value_governance_conformance_phase_219.py`
  - `tests/test_genesis_integration_smoke_phase_224.py`
  - `tests/test_genesis_install_smoke_phase_224.py`
  - `tools/check_genesis_integration_smoke_phase_224.sh`

## 5. Residual anti-gaming risk categories (not fully solved)

1. Multi-agent coalition inflation:
   - coordinated groups can imitate diversity while mutually inflating reuse.
2. Model-family monoculture risk in bootstrap cohorts:
   - independent agent IDs do not guarantee independent epistemic priors.
3. Long-horizon local maxima:
   - community-wide high-confidence but later-overturned consensus can persist for many epochs.
4. True counterfactual complexity gap:
   - current path-lift method is Shapley-adjacent, not full node-removal recomputation.

## 6. Documented deferred follow-ups

Tracked in handoff and TODO artifacts:
- single shared policy source for refutation multiplier and dependent safety floors,
- true node-removal counterfactual research and complexity study,
- runtime governor monitoring support for decreasing Genesis share trajectories.

Anchors:
- `docs/specs/ilc_main_track_return_213_220_handoff_v0.1.md`
- `TODO.txt`

## 7. Reviewer guidance

When evaluating anti-gaming proposals:
1. Check whether proposal preserves ratified invariants (`CDL-011` to `CDL-015`).
2. Check whether proposal changes economics or only diagnostics.
3. Require deterministic replay evidence and gate coverage.
4. Route constitutional policy changes through decision-log workflow.

## 8. Companion document

For full project orientation and precedence rules, read:
- `docs/specs/ilc_reviewer_context_pack_v0.1.md`
