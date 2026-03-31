# ILC Integration Coherence Report 553 v0.1

Status: synthesis report
Date: 2026-03-31
Owner lane: G8 Constitution Cluster A

## 1. Window 545-554 summary

Window 545-554 remains active at Phase 553.

CDL-060 gossip runtime implemented in Phase 548.
Passive ECU attribution runtime implemented in Phase 550.
SIM-MULTI-HOP-01 disposition produced in Phase 552.

## 2. CDL-060 gossip runtime record

`CDL_060_GOSSIP_RUNTIME_VERSION = "cdl_060_gossip_runtime_548.v0.1"`
`ACCUMULATION_MODEL = "epoch_boundary_atomic"`

The epoch-boundary semantics decision was `epoch_boundary_commit_semantics_decision` in Phase 546.
Phase 548 implemented the ratified single-hop bounded-fanout gossip runtime with explicit one-epoch
attribution lag and explicit crash-recovery zero logging.

## 3. Passive ECU attribution runtime record

`PASSIVE_ECU_ATTRIBUTION_RUNTIME_VERSION = "passive_ecu_attribution_runtime_550.v0.1"`
`PASSIVE_ATTRIBUTION_RATE = 0.20`
`DECAY_FLOOR = 0.05`
`ATTRIBUTION_CAP = 0.15`

Authorship primacy invariant holds: passive_ecu < base_reward for all valid inputs.
The runtime applies the output-layer clamp `min(raw, base_reward * ATTRIBUTION_CAP)` and preserves the
bounded quality-factor band implied by `GAMMA = 0.15`.

## 4. Simulation evidence chain

Phase 542 established `sim_passive_ecu_01_sufficient` as the direct upstream calibration for the
Phase 550 passive ECU runtime.
Phase 552 established `sim_multi_hop_01_insufficient`.
`cdl_060_single_hop_lane_remains_complete`

The evidence chain therefore supports the implemented single-hop gossip plus passive-attribution v1
lane while deferring any multi-hop constitutional opening.

## 5. Signal-floor policy disposition

Phase 547 selected `signal_floor_governance_adm_only`.
Window 555+ must document the cross-module invariant `recommended_decay_floor >= recommended_u_floor`
in the ADR-level quality-signal guidance rather than opening a new signal-floor CDL.

## 6. Carry-forward obligations

Window 555+ carry-forwards are:
- multi-hop centrality deferred pending future evidence
- `signal_floor_governance_adm_only` remains the active disposition until the ADR update lands
- CDL-053 remains reserved and unopened
- Phase 554 is the closure gate for Window 545-554

No multi-hop CDL opening is warranted from SIM-MULTI-HOP-01 in the next window.

## 7. Snapshot isolation verification

No CDL mutation occurs in Phase 553.
No `ilc_core/` mutation occurs in Phase 553.
Canonical `out/monitoring/` files are not touched by this synthesis phase.
