# ILC CDL-060 Gossip Centrality Extension Prelock Hardening v0.1

Status: prelock
Date: 2026-03-30
CDL: CDL-060

## 1. Prelock scope

This document locks CDL-060 to a narrow constitutional lane for single-hop `centrality_delta`
gossip under the CDL-036 dissemination baseline and the CDL-039 topology-privacy boundary.

## 2. CDL-039 topology privacy lock

`cdl_039_privacy_locked`

The three topology-privacy constraints are locked:
- opaque channel field: `centrality_delta` messages must use CDL-039-compliant opaque channel
  values
- cluster membership non-inferrable: gossip fanout and message content must not reveal cluster
  membership
- fanout bounds locked: no unbounded propagation is permitted beyond the calibrated v1 range

## 3. Gossip propagation parameter lock

`single_hop_scope_locked`

`bounded_fanout_locked`

Phase 538 calibration constants are the v1 constitutional baseline:
- `recommended_fanout: 3`
- `recommended_convergence_epochs: 4`
- `recommended_privacy_budget_fraction: 0.25`

These values are consumed as the bounded single-hop starting point for later runtime work.

## 4. Rejected scope expansions

The following remain out of scope for Phase 541 ratification:
- multi-hop centrality
- direct modification of CDL-036 row
- CDL-039 topology privacy relaxation
- gossip runtime implementation
- passive ECU attribution formula

## 5. Ratification readiness

`cdl_060_prelock_complete`

Phase 541 ratification may proceed only on the locked lane: `centrality_delta` gossip with
CDL-039-compliant opaque channel, bounded fanout, single-hop scope, and preserved Layer 3
orthogonality with CDL-052.

`CDL-060 remains status: open in Phase 540.`
