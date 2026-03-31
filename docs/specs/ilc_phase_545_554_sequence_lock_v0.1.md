# ILC Phase 545-554 Sequence Lock v0.1

Status: locked
Date: 2026-03-31
Window: 545-554
Owner lane: G8 Constitution Cluster A

## 1. Window identity

Window 545-554 is the first runtime implementation tranche for the reuse-centrality gossip
and passive-ECU lane ratified in Window 535-544. It inherits the Phase 544 handoff and
freezes the ten-phase program below.

## 2. Carry-forward freeze

- `epoch_boundary_commit_semantics_required_before_cdl_060_gossip_runtime`
- `passive_ecu_runtime_depends_on_cdl_060_gossip_runtime`
- `CDL-053 remains reserved and unopened throughout Window 545-554.`
- `Phase 554 is the closure gate.`
- `sim_multi_hop_01_deferred`
- `phase_542_exact_value_assertions_confirmed`
- `attribution_cap` is applied at the passive-ECU output layer:
  `passive_ecu = min(base_reward * passive_attribution_rate * centrality_score * m_i, base_reward * attribution_cap)`.
- The direct authorship reward baseline is `1.0 * base_reward`, and authorship primacy requires
  `passive_attribution_rate * m_i_max < 1.0`; with `0.20 * 1.15 = 0.23`, the passive lane remains subordinate.
- `recommended_decay_floor >= recommended_u_floor` is locked at the minimum valid v1 configuration:
  `recommended_decay_floor = 0.05` and `recommended_u_floor = 0.05`.

## 3. Non-goals

This sequence lock does not:
- mutate the constitutional decision log
- modify `ilc_core/`
- open any new CDL row
- implement the CDL-060 gossip runtime before Phase 546 decides commit semantics
- implement passive ECU attribution runtime before the CDL-060 gossip runtime exists
- authorize multi-hop runtime or amend CDL-060 from its ratified single-hop lane

## 4. Phase sequence and primary deliverables

| Phase | Primary deliverable |
|---|---|
| 545 | `docs/specs/ilc_phase_545_554_sequence_lock_v0.1.md` |
| 546 | `docs/specs/ilc_epoch_boundary_commit_semantics_decision_546_v0.1.md` |
| 547 | `docs/specs/ilc_signal_floor_policy_consistency_scoping_547_v0.1.md` |
| 548 | `ilc_core/network/d2d/centrality_delta_gossip_runtime.py` |
| 549 | `ilc_core/network/d2d/centrality_delta_gossip_runtime.py` and `tools/run_mutation_canary_phase_297.py` |
| 550 | `ilc_core/economics/passive_ecu_attribution_runtime.py` |
| 551 | `ilc_core/economics/passive_ecu_attribution_runtime.py` |
| 552 | `docs/specs/ilc_sim_multi_hop_01_centrality_calibration_552_v0.1.md` |
| 553 | `docs/specs/ilc_integration_coherence_report_553_v0.1.md` and `docs/specs/ilc_antigravity_context_capsule_v2.8.md` |
| 554 | `tools/check_window_545_554_closure_gate_phase_554.sh` |

## 5. Entry conditions from Window 535-544

Window 535-544 is closed.
`CDL-036`, `CDL-039`, `CDL-052`, `CDL-059`, and `CDL-060` are ratified at window entry.
`CDL-053` remains reserved and unopened.
`CDL-061` remains absent at Phase 545 entry.
`ilc_core/epistemic/reuse_centrality_runtime.py` remains advanced to `incremental_direct_use_v1`.
The Phase 542 passive-ECU calibration exact-value assertions remain active in baseline.
