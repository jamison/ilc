# ILC SIM-CENTRALITY-01 and SIM-NOVELTY-01 Calibration v0.1

Status: sufficient
Date: 2026-03-30
Window: 525-534
Simulations: SIM-CENTRALITY-01, SIM-NOVELTY-01

## 1. Simulation purpose and scope

This document calibrates the direct-use centrality and novelty-bonus parameters required for
ADR-0023 v1. The simulation scope is limited to single-hop direct-use centrality and does not
open any constitutional lane by itself.

## 2. SIM-AESTHETIC-01 baseline constants consumed

SIM-AESTHETIC-01 established a diversity-maximizing Register 2 panel and preserved the
informational-only Layer 2 boundary. Those inputs are consumed here as fixed upstream
assumptions.

## 3. SIM-CENTRALITY-01: incremental centrality convergence

`incremental_centrality_convergence` is accepted as sufficient for v1 direct-use scoring.
Bahmani et al. (2010) provides the convergence basis for incremental updates over a changing
link graph. Window 525-534 keeps the runtime at single-hop direct-use only.

recommended_u_floor: 0.05

The recommended use floor zeroes out dust-level churn and preserves a bounded passive pool in
future windows.

## 4. SIM-NOVELTY-01: novelty bonus calibration

The calibrated discovery formula remains:
`discovery_weight = alpha * aesthetic_score + beta * (1 / (1 + centrality))`

recommended_alpha: 0.60
recommended_beta: 0.40
recommended_gamma: 0.15

The selected parameters preserve early discovery support while ensuring the novelty bonus
self-damps toward zero as centrality grows. The gamma recommendation preserves the bounded
quality-factor map `m_i = 1 + gamma * (2*q_i - 1)` with a symmetric v1 band.

## 5. Multi-hop deferral boundary

`multi_hop_centrality_deferred`

SIM-MULTI-HOP-01 remains a Window 535+ concern. Single-hop direct-use centrality is sufficient
for CDL-059 v1 scope.

## 6. Simulation sufficiency declarations

`sim_centrality_01_sufficient`

`sim_novelty_01_sufficient`

Both sufficiency declarations are satisfied for the Phase 528 synthesis gate.
