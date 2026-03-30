# ILC CDL-060 Gossip Centrality Extension Scoping v0.1

Status: scoped
Date: 2026-03-30
Window: 535-544
Phase: 536

## 1. Scoping purpose

This document scopes CDL-060 as a new constitutional row governing a `centrality_delta`
gossip message type for single-hop reuse-centrality propagation. The scoping task is to
establish whether CDL-036 requires a new row, and which CDL-039 privacy invariants must be
preserved before any opening stub can be drafted.

`cdl_060_scoping_complete`

## 2. CDL-036 amendment requirement analysis

CDL-036 governs header-first dissemination and CID-addressed pull fetch. It does not currently
define a `centrality_delta` message type, nor does it describe reuse-centrality propagation as
a first-class gossip payload. A direct edit to the existing CDL-036 row would collapse two
separate constitutional concerns into one artifact.

`centrality_delta_message_type_required`

The correct vehicle is a new CDL row that cites CDL-036 and CDL-039 as related clauses while
preserving the existing CDL-036 row byte-for-byte. CDL-060 therefore exists to govern a new
message type rather than to rewrite baseline dissemination semantics.

## 3. CDL-039 topology privacy constraint analysis

`cdl_039_privacy_analysis_complete`

`cluster_membership_non_inferrable`

The `centrality_delta` gossip design must satisfy three topology privacy constraints derived
from CDL-039:
- opaque channel only: the channel field must be opaque so routing topology cannot be inferred
  from the transport envelope
- cluster membership non-inferrable: message content must not reveal validator-cluster or
  peer-cluster membership from the delta payload itself
- bounded fanout consistency: fanout must remain bounded so propagation patterns do not expose
  membership topology through deterministic oversharing

These constraints preserve CDL-039's privacy boundary while still allowing bounded single-hop
propagation of reuse-centrality deltas.

## 4. CDL-060 design requirements

`single_hop_scope_enforced`

CDL-060 design requirements are:
- define a `centrality_delta` message type with fields `cid`, `score_delta`, `epoch`, and
  `signature`
- require CDL-039-compliant opaque channel usage for every message instance
- keep propagation in single-hop scope for v1; no transitive or recursive centrality routing
- define a bounded fanout range to be calibrated by SIM-CENTRALITY-02 before any opening stub
- keep the gossip payload orthogonal to passive ECU attribution formula work, which remains a
  separate evidence lane

## 5. Rejected scope expansions

The following expansions are rejected at scoping time:
- direct modification of the existing CDL-036 row; CDL-060 must be a new row
- multi-hop centrality in v1 scope; this remains a Window 545+ concern
- gossip runtime implementation in Window 535-544; runtime delivery is a Window 545+
  carry-forward
- CDL-039 topology privacy relaxation; the new lane must preserve rather than weaken privacy

## 6. Authorization for Phase 537 and SIM-CENTRALITY-02

Phase 537 reuse centrality runtime advancement is authorized to replace the existing stub with
single-hop direct-use scoring inside `ilc_core/epistemic/reuse_centrality_runtime.py`.
SIM-CENTRALITY-02 is authorized as the calibration gate required before CDL-060 can open.

`CDL-060 remains absent in Phase 536.`
