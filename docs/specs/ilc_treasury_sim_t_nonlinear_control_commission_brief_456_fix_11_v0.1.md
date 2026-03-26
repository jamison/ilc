# ILC Treasury SIM-T Nonlinear-Control Commission Brief 456 Fix 11 v0.1

Status: Phase-456 Fix-11 nonlinear-control commission brief freeze
Date: 2026-03-26
Owner lane: G8 Constitution Cluster A

## 1. Mechanism surface reference

The executable mechanism surface for this lane is `simulations/sim_treasury_scenario5_waggle_dance_recovery_rule.py`.

`waggle_dance_codename=Waggle Dance`

`nonlinear_control_curve`

`nonlinear_control_curve_status=implemented`

This brief freezes only candidates already exposed by the implemented Fix-10 surface.

## 2. Reference stack and paper basis

This brief is motivated by the following reference stack:

- `A model of collective nectar source selection by honey bees: Self-organization through simple rules`
- `How Information-Mapping Patterns Determine Foraging Behaviour of a Honey Bee Colony`
- `Multiagent Decision-Making Dynamics Inspired by Honeybees`
- `Ovarian Control of Nectar Collection in the Honey Bee (Apis mellifera)`
- `How to Model Honeybee Colonies`

The paper stack motivates the family framing but does not substitute for measured Scenario-5 evidence.

The literature is used here to justify a disciplined family interpretation, not to claim that the Treasury mechanism is already ratified by analogy.

## 3. Fix-12 candidate field

The Fix-12 field is frozen to the three implemented Waggle Dance candidates plus mixed_queue_and_production.

The frozen Fix-12 candidate field is:

- `nonlinear_curve_k56_g18_f22_frontier_first`
- `nonlinear_curve_k58_g18_f22_frontier_first`
- `nonlinear_curve_k60_g18_f22_frontier_first`
- `mixed_queue_and_production`

Legacy production-band carry-forwards and oscillator candidates remain outside the Fix 12 field.

Fix 12 may execute only the candidate field frozen in this brief.

## 4. Local-to-aggregate control interpretation

Local linear response may aggregate into nonlinear recruitment across the graph.

Graph-indexed recruitment is a motivating interpretation for the Waggle Dance family, constrained to the implemented Fix-10 surface in Fix 11.

Graph-indexed recruitment is conceptual support for the family and not a claim that explicit adjacency-state execution already exists in Fix 10.

Within this brief, the implemented nonlinear-control candidates are treated as bounded proxies for a graph-aware family in which local calibration and distributed propagation could produce aggregate nonlinear control.

## 5. Parameter freeze

The frozen nonlinear-control candidates retain the Fix-10 parameter surface only:

- `nonlinear_curve_k56_g18_f22_frontier_first` with `response_knee=0.56`, `control_gain=1.8`, `release_floor=0.22`, `bias=frontier_first`
- `nonlinear_curve_k58_g18_f22_frontier_first` with `response_knee=0.58`, `control_gain=1.8`, `release_floor=0.22`, `bias=frontier_first`
- `nonlinear_curve_k60_g18_f22_frontier_first` with `response_knee=0.60`, `control_gain=1.8`, `release_floor=0.22`, `bias=frontier_first`

No legacy production-band parameters are reintroduced in this brief.

No oscillator parameters are frozen in this brief.

## 6. Success criteria and thresholds

Primary-observable threshold evaluation remains based on absolute percentage-point difference.

A Fix-12 leader clears only if it separates from the best remaining alternative in the full candidate field frozen in this brief by the registered materiality margins.

Duration and cost remain secondary observables only after primary-observable threshold clearance.

Fix 11 does not reinterpret Window 450-459 as passed.

## 7. Non-execution and non-authorization statement

No Scenario-5 execution occurs in Phase 456 Fix 11.

No CDL-050 opening or ratification occurs in Phase 456 Fix 11.

Fix 11 does not authorize Fix 12 execution by itself.
