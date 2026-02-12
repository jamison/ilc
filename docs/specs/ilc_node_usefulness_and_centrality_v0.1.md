# ILC Node Usefulness and Centrality v0.1

Status: Draft
Date: 2026-02-11
Owner: Economics and governance track

## 1. Objective
Define a concrete, testable method for measuring node usefulness and centrality in ILC, while separating:
- epistemic importance of nodes, and
- governance voting influence of agents.

## 2. Design Principles
1. Usefulness is behavior-derived (reuse, validation, contradiction resistance), not declared.
2. Path-level contribution matters, not only node-local efficiency.
3. Epistemic centrality and governance power are distinct surfaces.
4. Metrics must be anti-gaming and machine-verifiable.

## 3. Metric Surfaces

### 3.1 Epistemic Weight (node-level, persistent)
`epistemic_weight(node, t)` captures long-horizon knowledge importance.

Proposed decomposition:
- `reuse_score`: weighted downstream reuse count
- `resilience_score`: contradiction resistance over review windows
- `validation_score`: verifier confidence and survival outcomes
- `path_lift_score`: counterfactual path efficiency gain (with/without node)

Candidate formula:
`EW_n = a*R_n + b*C_n + c*V_n + d*P_n`

Where:
- `R_n`: quality-weighted and diversity-weighted reuse
- `C_n`: contradiction-resilience score
- `V_n`: validation integrity score
- `P_n`: path-level marginal utility uplift
- `a,b,c,d >= 0`, `a+b+c+d=1`

Notes:
- No mandatory automatic time-decay of `EW_n`.
- `EW_n` may rise or fall as new evidence/reuse appears.

### 3.2 Utility Flow (epoch-level, payout surface)
`utility_flow(node, epoch)` captures near-term measurable impact for reward allocation.

Candidate formula:
`UF_n(e) = EW_n(e) * usage_window_n(e) * freshness_gate_n(e)`

Where:
- `usage_window_n(e)`: rolling epoch usage intensity
- `freshness_gate_n(e)`: bounded factor for stale-but-unused periods (prevents pure historical rent extraction while preserving persistent epistemic weight)

### 3.3 Agent Governance Weight (vote surface)
`governance_weight(agent, epoch)` is used for governance voting only.

Candidate formula for non-Genesis agents:
`GW_i(e) = base_i * quality_i(e) * exp(-lambda * inactivity_i(e))`

This decays governance influence with inactivity/time.

## 4. Genesis Treatment

### 4.1 Epistemic side
- Genesis nodes are scored by the same `EW_n` function.
- If heavily reused and resilient, they remain central.
- No forced "old-node penalty" simply due to age.

### 4.2 Governance side
- Genesis can be exempted from the inactivity decay term on a narrow baseline component:
  - `GW_genesis(e) = genesis_baseline + contribution_bonus(e)`
- Voting share is normalized globally:
  - `vote_share_i(e) = GW_i(e) / sum_j GW_j(e)`

Result:
- As network participation grows, Genesis voting share naturally dilutes, even if baseline is not decayed.
- If Genesis contributes new verified work, contribution bonus can increase within policy bounds.

## 5. Reward Link (Economics)
Node rewards should reference `UF_n(e)` and global budget constraints, not direct static centrality alone.

Candidate payout share:
`reward_share_n(e) = UF_n(e) / sum_k UF_k(e)`

Genesis accrual target can be bounded with a global governor to trend toward long-run approximately 5 percent lifetime share, consistent with constitutional direction.

## 6. Anti-Gaming Requirements
1. Self-reuse discounting and anti-Sybil weighting.
2. Diversity weighting on reusers (cluster and sponsor independence).
3. Counterfactual validation for path-lift claims.
4. Challenge windows for disputed centrality claims.
5. Audit trails for all score inputs and windows.

## 7. Conformance Hooks (Proposed)
- CH-USE-001: deterministic score computation from signed input events
- CH-USE-002: reproducible path-lift counterfactual test harness
- CH-USE-003: anti-Sybil weighting invariants
- CH-USE-004: governance share normalization and cap checks

## 8. Open Decisions
1. Exact weights `a,b,c,d` and calibration method.
2. Freshness gate shape and bounds.
3. Genesis baseline bounds and emergency-power separation.
4. Whether transition-only suspensive brake exists (outside normal vote surface).

## 9. Historical Anchors
- `docs/research/ilc_historical_formula_and_mechanism_catalog_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

## 10. Ratification and Phase Ordering
- Ratification checklist and implementation ordering are defined in:
  - `docs/specs/ilc_node_value_and_governance_ratification_plan_v0.1.md`
- This spec should not be executed out of order with governance/reward integration work.
