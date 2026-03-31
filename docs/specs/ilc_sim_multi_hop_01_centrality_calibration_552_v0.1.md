# ILC SIM-MULTI-HOP-01 Multi-Hop Centrality Calibration v0.1

Status: insufficient
Date: 2026-03-31
Window: 545-554
Simulation: SIM-MULTI-HOP-01

## 1. Simulation purpose and scope

SIM-MULTI-HOP-01 evaluates whether multi-hop centrality propagation preserves enough signal to
justify a new CDL opening in Window 555+. The analysis is limited to 2-hop and 3-hop
propagation, does not amend CDL-060, and does not authorize any runtime implementation.

## 2. Upstream inputs consumed

This simulation consumes the fixed upstream inputs already locked in the current lane:
- `recommended_fanout = 3` from Phase 538
- `recommended_convergence_epochs = 4` from Phase 538
- `U_FLOOR = 0.05` from Phase 527 and Phase 537 carry-forward
- CDL-060 single-hop centrality gossip as the ratified v1 baseline

The baseline assumption is that hop-1 is the only constitutionally ratified attribution lane.
Any hop-depth greater than 1 must outperform the floor and remain distinguishable from noise
before a new CDL opening is warranted.

## 3. Multi-hop signal model

The model treats hop-1 as the normalized baseline signal `S(1) = 1.0`. Each additional hop
incurs two multiplicative penalties:
- bounded-fanout dilution across `recommended_fanout = 3`
- epoch-boundary aggregation lag across `recommended_convergence_epochs = 4`

The retained signal by hop depth `h` is therefore modeled as:

`S(h) = 1 / (recommended_fanout * recommended_convergence_epochs)^(h - 1)`

With the fixed constants in this window:
- hop-2 signal: `S(2) = 1 / (3 * 4) = 1 / 12 = 0.0833`
- hop-3 signal: `S(3) = 1 / (3 * 4)^2 = 1 / 144 = 0.0069`

The noise term uses the minimum meaningful attribution floor scaled by the number of candidate
relay branches created at each additional hop:

`N(h) = U_FLOOR * recommended_fanout^(h - 1)`

This yields:
- hop-2 noise: `N(2) = 0.05 * 3 = 0.15`
- hop-3 noise: `N(3) = 0.05 * 9 = 0.45`

## 4. Signal-to-noise analysis

Signal-to-noise ratio is evaluated as `SNR(h) = S(h) / N(h)` relative to the hop-1 baseline.

Computed values:
- hop-1 baseline: `SNR(1) = 1.0 / 0.05 = 20.0`
- hop-2: `SNR(2) = 0.0833 / 0.15 = 0.56`
- hop-3: `SNR(3) = 0.0069 / 0.45 = 0.015`

Findings:
- signal-to-noise falls below `1.0` at hop-2
- hop-2 remains above `U_FLOOR = 0.05`, but it is already below the distinguishability threshold
- hop-3 falls below both the `U_FLOOR` threshold and the `SNR = 1.0` threshold

The practical implication is that 2-hop propagation still emits a measurable number, but not one
that is reliable enough for constitutional attribution. By hop-3 the signal is operationally dust.

## 5. CDL-039 privacy implications

Multi-hop propagation exposes more topology than the ratified single-hop lane because each relay
creates an additional observation point and a larger set of candidate upstream paths. That weakens
CDL-039's requirement that cluster membership must not be inferrable.

Relative to the CDL-060 single-hop lane:
- multi-hop messages expose more topology than single-hop because correlated relay timing and
  repeated forwarding enlarge the observable propagation surface
- even with opaque channels preserved, multi-hop increases the path-inference surface beyond the
  current bounded single-hop design

A privacy-preserving multi-hop design is only conceivable under a stricter bounding constraint:
- hop depth capped at 2
- epoch-boundary batching preserved
- relay aggregation before forwarding
- per-hop opaque channel re-randomization
- no upstream path identifiers or creator metadata in transport headers

Even under that bound, the hop-2 SNR in this simulation remains below `1.0`, so the privacy cost
is not justified by the retained signal.

## 6. Simulation sufficiency declaration

`sim_multi_hop_01_insufficient`

`cdl_060_single_hop_lane_remains_complete`

`multi_hop_deferred_pending_future_evidence`

SIM-MULTI-HOP-01 does not justify a Window 555+ CDL opening for multi-hop centrality. The ratified
CDL-060 single-hop lane remains the complete v1 scope, and any future multi-hop planning requires
new evidence with a stronger signal model and a tighter CDL-039 privacy argument.
