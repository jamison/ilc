# ILC Node Value and Governance Ratification Plan v0.1

Status: Draft for ratification sequencing
Date: 2026-02-12
Owners: Governance, economics, protocol tracks

## 1. Purpose
Lock node usefulness and governance-weight mechanisms in the correct order so implementation can proceed with minimal refactor risk.

This plan is driven by historical-corpus extraction and current architecture decisions:
- `docs/research/ilc_historical_formula_and_mechanism_catalog_v0.1.md`
- `docs/specs/ilc_node_usefulness_and_centrality_v0.1.md`
- `docs/adr/ADR_0008_Node_Usefulness_vs_Governance_Weight_and_Genesis_Dilution.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

## 2. Ratification Checklist (Decision Gates)

Each gate must be explicitly marked `ratified` before downstream implementation is considered stable.

1. Surface separation is final (`epistemic_weight`, `utility_flow`, `governance_weight`).
2. Node value is a posteriori and behavior-derived (not self-reported).
3. Epistemic-weight formula components and calibration method are fixed.
4. Utility-flow epoch function and freshness gate behavior are fixed.
5. Anti-Sybil/reuse-diversity weighting rules are fixed.
6. Path-level marginal contribution method is fixed (counterfactual definition).
7. Governance-weight decay for non-Genesis participants is fixed.
8. Genesis governance baseline rule and dilution semantics are fixed.
9. Emergency Genesis authority policy is fixed (or explicitly rejected).
10. Reward-link function from utility flow to payouts is fixed.
11. Global Genesis accrual governor policy (approximately 5 percent lifetime target) is fixed.
12. Conformance hooks and telemetry schema are fixed for all above rules.

## 3. Proposed Default Formula Set (Ratification Candidate)

### 3.1 Epistemic Weight
`EW_n = a*R_n + b*C_n + c*V_n + d*P_n`

Where:
- `R_n`: quality-weighted and diversity-weighted reuse
- `C_n`: contradiction resilience
- `V_n`: validation integrity
- `P_n`: path-level marginal utility uplift
- `a,b,c,d >= 0`, `a+b+c+d=1`

### 3.2 Utility Flow (Epoch)
`UF_n(e) = EW_n(e) * usage_window_n(e) * freshness_gate_n(e)`

### 3.3 Governance Weight (Non-Genesis)
`GW_i(e) = base_i * quality_i(e) * exp(-lambda * inactivity_i(e))`

### 3.4 Governance Share
`vote_share_i(e) = GW_i(e) / sum_j GW_j(e)`

### 3.5 Genesis Baseline (Candidate)
`GW_genesis(e) = genesis_baseline + contribution_bonus(e)`

Constraint:
- Share always global-normalized by total `GW`.
- Genesis influence must dilute as system participation grows.

## 4. Historical Anchors (High Signal)

- Reuse-driven reputation:
  - `Z_Past_Chats/2025_06_18_ILC - 4D Cognitive AI Model.txt:1934`
- A-posteriori valuation:
  - `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt:997`
- Centrality/PageRank family:
  - `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt:9043`
  - `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt:9346`
- Founder/governance constraints:
  - `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt:16117`
  - `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt:16260`
- Genesis bounded accrual framing:
  - `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt:20630`
  - `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt:20900`

## 5. Refactor-Avoidance Execution Order

Order is mandatory. Starting later steps before earlier gates are fixed increases rework risk.

1. **RA-01: Input Event Canon and Telemetry**
   - Freeze input event schema and replay windows for scoring inputs.
   - Add deterministic extraction hooks and signed provenance.
2. **RA-02: Offline Score Kernel**
   - Implement deterministic score computation for `EW` and `UF` in analysis mode only.
   - No governance coupling yet.
3. **RA-03: Conformance and Challenge Harness**
   - Add deterministic conformance tests and dispute windows for score claims.
4. **RA-04: Governance Weight Pipeline**
   - Add `GW` and share normalization with non-Genesis decay.
   - Add Genesis baseline as policy-gated feature.
5. **RA-05: Economics Linkage**
   - Wire `UF` into reward allocation and governor policy checks.
6. **RA-06: Policy Ratification and Migration**
   - Ratify unresolved options and migrate any temporary compatibility behavior.

## 6. Suggested Phase Packaging

This sequence is intended to map to future phases in order:

- `P-A`: RA-01 plus baseline conformance fixtures
- `P-B`: RA-02 plus deterministic score vectors
- `P-C`: RA-03 plus challenge-path validation
- `P-D`: RA-04 plus governance normalization tests
- `P-E`: RA-05 plus emissions/governor simulations
- `P-F`: RA-06 plus documentation and compatibility cleanup

## 7. Exit Criteria

This plan is complete only when:
- All 12 decision gates are `ratified` in the constitutional decision log.
- Corresponding conformance tests are green.
- Master plan and TODO sequencing references are updated and consistent.

