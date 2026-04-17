# ILC SIM-TOPOLOGY-01 Commissioning 711 v0.1

**Date:** 2026-04-17  
**Phase:** 711  
**Status:** Commissioned

Tokens:
- `sim_topology_01_commissioned`
- `topology_commissioning_only_in_window_707_712`
- `epoch_hash_testnet_acceptable_vrf_production_open`
- `sim_topology_01_results_feed_later_cdl_039_authorization`

## 1. Commissioned questions

`SIM-TOPOLOGY-01` is commissioned to answer three coupled questions:

1. **Connectivity:** does the chosen shuffle process preserve connected or
   acceptably resilient validator communication graphs across epoch transitions?
2. **Privacy:** does the proposed assignment method preserve the `CDL-039`
   topology-privacy boundary rather than leaking global structure?
3. **Resilience:** how does the shuffled graph behave under tolerated Byzantine
   faults, churn, and temporary node absence?

## 2. Inputs, scenarios, and measured outputs

The simulation must vary at minimum:

- validator count `N`,
- tolerated Byzantine set `F`,
- target neighborhood degree / subgraph density,
- shuffle cadence,
- epoch-hash seeding versus VRF seeding as compared options,
- node churn and silent-validator scenarios,
- gossip fanout assumptions consistent with the hybrid push-pull posture.

Measured outputs must include:

- connectivity / fragmentation results,
- recovery time after shuffle transitions,
- topology-inference or exposure risk indicators,
- parameter combinations where privacy and resilience goals conflict.

## 3. Commissioning-only boundary and completion path

`topology_commissioning_only_in_window_707_712`

This phase is commissioning-only, not results-bearing.

Window `707-712` closes successfully if the simulation is honestly commissioned
with explicit questions, inputs, and completion criteria. The simulation results
may complete later if needed.

Completion path:

- Phase `711` commissions the work,
- later simulation execution produces the actual evidence,
- later `CDL-039` authorization work and `CDL-017` convergence consume the results
  instead of treating this commissioning note as sufficient evidence.

## 4. Failure conditions and carry-forward meaning

`epoch_hash_testnet_acceptable_vrf_production_open`

`sim_topology_01_results_feed_later_cdl_039_authorization`

Failure conditions for the later simulation run are explicit:

- the shuffled graph disconnects or fragments beyond tolerated bounds,
- the assignment method leaks topology structure incompatible with `CDL-039`,
- recovery after churn or Byzantine stress exceeds acceptable epoch budgets,
- epoch-hash and VRF comparisons reveal unresolved tradeoffs with no bounded
  authorization path.

The carry-forward meaning is also explicit:

- epoch-hash remains acceptable for testnet framing,
- production VRF remains open,
- this note does not select the final production seed,
- later results must determine whether the candidate diversity metric from
  Phase `710` is workable under real shuffle conditions.
