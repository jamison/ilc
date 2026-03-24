# ILC Treasury SIM-T Comparative Synthesis 455 v0.1

Status: Phase-455 SIM-T comparative synthesis
Date: 2026-03-24
Owner lane: G8 Constitution Cluster A

## 1. Evidence base

This synthesis uses the fixed Phase 454 evidence package and applies only the pre-registered
comparison rules from the Phase 453 commission brief.

Primary evidence inputs:
- `docs/specs/ilc_treasury_sim_t_evidence_package_454_v0.1.md`
- `out/treasury_sim/phase_454/scenario_results.csv`
- `out/treasury_sim/phase_454/scenario_results.tsv`
- `out/treasury_sim/phase_454/summary_table.md`
- `docs/specs/ilc_treasury_sim_t_commission_brief_453_v0.1.md`
- `docs/specs/ilc_treasury_objective_function_and_observables_contract_451_v0.1.md`

No new scenarios were executed in Phase 455.

## 2. Candidate comparison

| Scenario family | Ranked candidates | Comparative synthesis |
| --- | --- | --- |
| `Scenario 1 - Escrow multiplier discrimination` | `escrow_5x > escrow_10x > escrow_2x > escrow_20x` | `escrow_5x` is the strongest combined queue/organic candidate inside the registered family. `escrow_10x` improves clamp behavior but gives back too much productive continuity. `escrow_20x` is dominated by queue starvation and cost drag. |
| `Scenario 2 - Vesting lock duration discrimination` | `vesting_25_epoch > vesting_50_epoch > vesting_10_epoch > vesting_100_epoch` | `vesting_50_epoch` is the strongest release-shock suppressor, but the `25` and `50` candidates do not separate cleanly enough to treat `50` as a decisive winner on the registered thresholds once duration, cost, and productive continuity are included. `vesting_25_epoch` therefore ranks first on overall balance while `vesting_50_epoch` remains the best pure stability candidate. |
| `Scenario 3 - L1/L2 contagion isolation test` | `boundary_enforced > partial_leakage > contagion_coupled` | `boundary_enforced` materially outperforms both weaker counterfactuals on clamp, organic production, queue behavior, duration, and cost. The catastrophic cross-layer signal remains boundary evidence only and does not expand normal operating scope. |
| `Scenario 4 - Long-tail zero-issuance stress test` | `mixed_control > escrow_focus > bounty_focus` | `mixed_control` is the only candidate that keeps queue behavior inside a materially stronger band under the registered `300%` stress case. `escrow_focus` is cheaper than `bounty_focus`, but both trail `mixed_control` on the governing stress behavior. |
| `Scenario 5 - Recovery criterion exit validation` | `production_band_5_epoch > production_band_3_epoch > mixed_queue_and_production` | `production_band_5_epoch` is the strongest false-exit-resistant rule in the registered family. `production_band_3_epoch` exits faster but carries higher replay-note false-exit exposure. `mixed_queue_and_production` is cheaper and shorter, but weaker on the recovery-rule success objective. |

## 3. Discrimination assessment

Family-by-family discrimination judgment:

- `Scenario 1 - Escrow multiplier discrimination`: materially discriminating. `escrow_5x` clears the next-best productive candidates on the governing queue and organic surfaces while avoiding the starvation/cost profile of `escrow_20x`.
- `Scenario 2 - Vesting lock duration discrimination`: partially discriminating, not cleanly decisive. The family separates the long lock (`100`) and short lock (`10`) from the middle pair, but the `25` versus `50` comparison remains a balance judgment rather than a single-surface landslide.
- `Scenario 3 - L1/L2 contagion isolation test`: materially discriminating. `boundary_enforced` is clearly separated from both `partial_leakage` and `contagion_coupled`.
- `Scenario 4 - Long-tail zero-issuance stress test`: materially discriminating. `mixed_control` clears the governing queue threshold against both alternatives under the registered stress case.
- `Scenario 5 - Recovery criterion exit validation`: directionally discriminating, but not numerically dominant on every registered surface. The `5`-epoch band leads on the success objective, yet the family still carries practical tradeoff ambiguity around duration/cost.

Overall judgment:

The Phase 454 evidence is strong enough to rank candidates and to support a clean Blocker 3
judgment for Phase 456, but it does not make every family equally settled. Scenario families
2 and 5 still contain practical tradeoff ambiguity even after ranking.

## 4. Candidate ranking

1. `Scenario 1 - Escrow multiplier discrimination`
   - `escrow_5x`
   - `escrow_10x`
   - `escrow_2x`
   - `escrow_20x`

2. `Scenario 2 - Vesting lock duration discrimination`
   - `vesting_25_epoch`
   - `vesting_50_epoch`
   - `vesting_10_epoch`
   - `vesting_100_epoch`

3. `Scenario 3 - L1/L2 contagion isolation test`
   - `boundary_enforced`
   - `partial_leakage`
   - `contagion_coupled`

4. `Scenario 4 - Long-tail zero-issuance stress test`
   - `mixed_control`
   - `escrow_focus`
   - `bounty_focus`

5. `Scenario 5 - Recovery criterion exit validation`
   - `production_band_5_epoch`
   - `production_band_3_epoch`
   - `mixed_queue_and_production`

## 5. Blocker 3 disposition

Blocker 3 disposition: cleared

Reasoning:

The registered Blocker 3 family is `Scenario 4 - Long-tail zero-issuance stress test`.
`mixed_control` is materially separated from both competing candidates on the governing
stress-response surface. In particular, its queue-clearance behavior exceeds `bounty_focus`
by `19` percentage points and `escrow_focus` by `11` percentage points under the fixed
`300%` verification-request spike. That is sufficient to move the family from merely
directional evidence to discriminating evidence under the Phase 453 commission brief.

## 6. Non-authorization statement

No comparison criteria outside the Phase 453 commission brief were applied.

No CDL-050 opening or ratification occurs in Phase 455.

Phase 455 ranks candidates and records a Blocker 3 synthesis judgment only. Phase 456
remains the blocker-clearance gate.
