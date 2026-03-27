# ILC Phase 459 Post4 Local Hysteretic Oscillator Field Attestation and Brief Freeze v0.1

Status: completed post-window supplement
Date: 2026-03-27
Owner lane: G8 Constitution Cluster A

## 1. Post-window boundary

Window 450-459 is closed.
CDL-050 is ratified.
CDL-051 is ratified.
Phase 459 Post4 records the reduced-attack-surface local solution without reopening Window 450-459.
Phase 459 Post4 does not reopen, prelock, amend, or ratify any CDL row.
Phase 459 Post4 preserves the ratified CDL-050 and CDL-051 record unchanged.
No Scenario-5 execution occurs in Phase 459 Post4.

## 2. Strike Path source basis

The source basis is the shard-local Strike Path sweep recorded in:
- `docs/research/ilc_strike_path_local_hysteretic_oscillator_search_2026_03_27_v0.1.md`
- `simulations/sim_treasury_scenario5_local_hysteretic_oscillator_recovery_rule.py`

The governing engineering choice is the lowest-attack-surface family that still clears Blocker 1 inside a frozen contrast field:
- `LOCAL_CODENAME=Shard Thermostat`
- `LOCAL_MECHANISM_STATUS=implemented`
- `local_hysteretic_oscillator_recovery_rule`
- `one rule for all shards`

No new constitutional authority is inferred from Strike Path evidence alone.

## 3. Implemented shard-local surface

Implemented surface:
- `simulations/sim_treasury_scenario5_local_hysteretic_oscillator_recovery_rule.py`

The default rule is shard-local hysteresis only:
- enter enforce above `threshold_high`
- return to release below `threshold_low`
- keep separate minimum enforce and release dwell times
- use local memory only
- do not rely on recruitment, graph propagation, or central cadence

Bounded randomized graph jumping is excluded from the default local rule.
Optional later experimental extension: weak bounded local smoothing.

## 4. Frozen execution field

The contrast execution field is frozen to four local-hysteretic candidates plus mixed_queue_and_production.
The frozen field is intentionally high-separation and is not a local-neighborhood probe.
The preferred default remains shard-local hysteresis without randomized nonlocal jumping.

Frozen candidates:
- `local_hysteretic_oscillator_t65_l45_g11_f12_e1_r2`
- `local_hysteretic_oscillator_t55_l30_g15_f04_e4_r4`
- `local_hysteretic_oscillator_t55_l30_g15_f20_e4_r4`
- `local_hysteretic_oscillator_t55_l30_g15_f04_e1_r4`
- `mixed_queue_and_production`

## 5. Attack-surface boundary

This field is carried forward because it minimizes attack surface relative to the graph-aware Waggle families and the post-window hybrid supplements.

Specifically removed from the default local rule:
- frontier targeting
- recruitment amplification
- adjacency-weight dependence
- graph-propagation lock-in
- randomized nonlocal shard jumping

Retained in the default local rule:
- local observed pressure
- independent on/off thresholds
- independent enforce/release dwell timers
- bounded local release floor
