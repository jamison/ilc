# ILC SIM-CENTRALITY-02 Gossip Propagation Calibration v0.1

Status: sufficient
Date: 2026-03-30
Window: 535-544
Simulation: SIM-CENTRALITY-02

## 1. Simulation purpose and scope

SIM-CENTRALITY-02 calibrates bounded gossip propagation for the proposed `centrality_delta`
message type. The simulation remains single-hop only and does not implement transport runtime
code inside Window 535-544.

## 2. CDL-039 privacy constraint baseline consumed

Phase 536 established three fixed privacy constraints for any CDL-060 lane:
- opaque channel transport
- cluster membership non-inferrable from message content
- bounded fanout consistency with CDL-039

These are consumed as non-negotiable baseline inputs.

## 3. Gossip propagation model

The model assumes a bounded, opaque-channel gossip round where each sender forwards a
`centrality_delta` payload to a small subset of peers. The simulation treats centrality
propagation as single-hop only and evaluates how quickly a bounded-fanout message reaches its
authorized recipients without exposing routing structure.

`single_hop_propagation_scope`

## 4. Calibration results

recommended_fanout: 3
recommended_convergence_epochs: 4
recommended_privacy_budget_fraction: 0.25

The selected fanout keeps the propagation set narrow enough to avoid topology leakage while
remaining operationally sufficient for the single-hop v1 lane. Four validation epochs is a
bounded convergence window for the selected fanout. The privacy budget fraction limits how much
centrality change information is surfaced in any one gossip round.

## 5. CDL-039 compliance verification

`cdl_039_privacy_preserved_in_gossip`

`cluster_membership_not_inferrable_from_delta_messages`

The Phase 536 privacy constraints remain satisfied:
- opaque channel preserved: `centrality_delta` continues to require opaque channel values
- cluster membership non-inferrable: the payload exposes only bounded score deltas and cannot
  reveal cluster membership from the delta message itself
- bounded fanout consistent: `recommended_fanout = 3` preserves a bounded propagation surface
  compatible with CDL-039 privacy requirements

## 6. Simulation sufficiency declaration

`sim_centrality_02_sufficient`

CDL-060 opening is authorized after sim_centrality_02_sufficient is established.
