# ILC CDL-060 Gossip Centrality Extension Opening Stub v0.1

Status: open
Date: 2026-03-30
CDL: CDL-060

## 1. Lane identity

CDL-060 opens a constitutional lane for `centrality_delta` gossip under the CDL-036
dissemination baseline and the CDL-039 topology-privacy boundary.
`cdl_060_governs_centrality_delta_gossip_protocol`

## 2. Problem statement

CDL-036 does not presently define a `centrality_delta` message type. ADR-0023 Layer 3 reuse
centrality requires a propagation mechanism, and any such mechanism must preserve CDL-039
topology privacy constraints rather than weakening them.

## 3. Candidate options

Options considered:
- retain ADR-0023 gossip extension as unratified guidance
- centrality_delta gossip message type with CDL-039-compliant opaque channel and bounded fanout
- centrality_delta with dedicated gossip channel

The dedicated-gossip-channel option is rejected because it is not CDL-039 compliant and makes
topology inference easier.

## 4. Selected option

`selected_option: centrality_delta_gossip_cdl_039_compliant`

The selected option is a `centrality_delta` gossip message type with an opaque channel,
bounded fanout, and single-hop scope.

## 5. Evidence anchors

`sim_centrality_02_evidence_anchored`

Phase 536 established `cdl_060_scoping_complete`.
Phase 538 established `sim_centrality_02_sufficient`.

## 6. Governance tokens

- `cdl_060_governs_centrality_delta_gossip`
- `cdl_039_privacy_preserved`
- `single_hop_scope_locked`
- `cdl_036_related_clause`
- `sim_centrality_02_evidence_anchored`
- `CDL-060 remains status: open in Phase 539.`

## 7. Forward obligations

- Phase 540 prelock hardening is required.
- Phase 541 ratification is required.
- CDL-060 gossip runtime implementation is a Window 545+ carry-forward.
