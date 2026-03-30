# ILC SIM-PASSIVE-ECU-01 Attribution Formula Calibration v0.1

Status: sufficient
Date: 2026-03-30
Window: 535-544
Simulation: SIM-PASSIVE-ECU-01

## 1. Simulation purpose and scope

This document calibrates the v1 passive ECU attribution formula for single-hop content reuse
under ADR-0023 Layer 3 economics. The scope is limited to formula constants and sufficiency for
Window 545+ runtime work; no runtime is implemented here.

## 2. Upstream constants consumed

The following inputs are consumed as fixed upstream constants:
- `recommended_u_floor = 0.05` from Phase 527 as the lower bound for any passive attribution
  floor
- `recommended_gamma = 0.15` from Phase 527 as the quality-factor map coefficient
- CDL-060 ratified in Phase 541, providing the constitutional single-hop centrality basis for
  v1 passive attribution

## 3. Attribution formula model

The calibrated formula is:
`passive_ecu = base_reward * passive_attribution_rate * centrality_score * m_i`

where:
- `m_i = 1 + gamma * (2*q_i - 1)`
- `gamma = 0.15`
- `centrality_score >= decay_floor` must hold for any passive attribution to apply
- single-hop centrality is the only in-scope source of `centrality_score`

`single_hop_attribution_scope`

## 4. Calibration results

`passive_attribution_formula_calibrated`

The recommended v1 constants are:
- `recommended_passive_attribution_rate: 0.20`
- `recommended_decay_floor: 0.05`
- `recommended_attribution_cap: 0.15`

These constants preserve a conservative passive lane: attribution begins only at or above the
Phase 527 floor, the passive rate remains materially below the direct authorship reward, and
single-path accumulation is capped before it can dominate the ECU pool.

## 5. Boundary conditions and pathological cases

(a) Zero-centrality case: if `centrality_score < decay_floor`, passive attribution is zero.
This uses `recommended_decay_floor: 0.05` to suppress dust-level churn.

(b) Maximum-cap accumulation case: a highly-reused node cannot drain the ECU pool through a
single passive path because `recommended_attribution_cap: 0.15` caps the path-level fraction.

(c) ADR-0023 authorship primacy invariant: passive attribution must not exceed the direct
reward. With `recommended_passive_attribution_rate: 0.20` and `recommended_attribution_cap:
0.15`, the passive lane remains subordinate to authorship even when `m_i` reaches the high end
of the bounded Phase 527 quality-factor map.

## 6. Simulation sufficiency declaration

`sim_passive_ecu_01_sufficient`

`window_545_runtime_gate`

Window 545+ passive ECU attribution runtime is authorized after sim_passive_ecu_01_sufficient
is established.
