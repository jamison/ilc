# ILC Integration Coherence Report 563 v0.1

Status: synthesis report
Date: 2026-03-31
Owner lane: G8 Constitution Cluster A

## 1. Window 555-564 summary

Window 555-564 is coherent through Phase 563.

Phase 555 sequence-locked the transport window around ADR-0025 and the future
CDL-061 lane. Phase 556 closed the ADR-level signal floor obligation.
Phase 557 opened CDL-061. Phases 558-560 implemented and hardened the HTTP
envelope contract. Phase 561 ratified CDL-061. Phase 562 added the static peer
registry and preserved the no-DHT v1 scope.

## 2. CDL-061 ratification coherence

`cdl_061_ratified_phase_561`

CDL-061 now governs the ILC gossip HTTP envelope contract as a ratified lane.
The row is ratified in the decision log with the HTTP envelope scope preserved:
header field set, CDL-039 exclusions, CDL-060 hop-count enforcement, status
code semantics, required CBOR production encoding, and the CDL-024 canonical
kind mapping described by ADR-0025.

## 3. Transport adapter dep chain

`gossip_transport_dep_chain_cdl_060_to_cdl_061_complete`

The full dep chain established in Window 555-564 is:

```text
CDL-039 (ratified 379) ──────────────────┐
CDL-060 (ratified 541) ──┐               │
                          ▼               ▼
                 centrality_delta_gossip_runtime (548)
                          │
                          ▼
                 gossip_transport (558) ──── CDL-061 (ratified 561)
                          │
                          ▼
                 gossip_peer_registry (562)
```

This chain is now live in code and ratified governance.

## 4. Signal floor invariant closure (Phase 556)

`signal_floor_invariant_documented_and_closed_phase_556`

Phase 556 documented `recommended_decay_floor >= recommended_u_floor` in
ADR-0023 and closed the cross-module signal-floor consistency obligation for
this window. Window 555-564 did not reopen that lane constitutionally.

## 5. CDL-039 topology privacy enforcement surface

`cdl_039_topology_privacy_enforced_at_header_layer`

Topology privacy is enforced at two distinct surfaces in the final window state:

- `gossip_transport.py` rejects forbidden header keys and opaque-channel violations
- `gossip_peer_registry.py` keeps peer inventory local and static, without any
  dynamic discovery or DHT layer that would widen topology exposure

The envelope layer therefore preserves CDL-039 privacy constraints while the
static registry avoids introducing new topology-discovery semantics.

## 6. Static peer registry scope and Window 565+ forward obligations

`static_peer_registry_v1_scope_no_dht`

Phase 562 implemented a static peer registry only. No DHT, mDNS, or dynamic
peer-discovery surface exists in the current lane. The pre-563 audit fix also
closed the duplicate-endpoint bug so fanout selection now operates on unique
normalized peers only.

`window_565_multi_machine_packaging_carry_forward`

Window 565+ must treat the registry as a local configuration primitive, then
carry it into multi-machine operational packaging.

## 7. Open items and forward obligations for Window 565-574

1. Multi-machine packaging: Python venv + systemd unit or container spec needed
2. Genesis state serialization for multi-machine import
3. Node lifecycle runtime (startup/shutdown/crash per CDL-046)
4. Ops playbook v1
5. Static peer config format (JSON/TOML/env vars) for `GossipPeerRegistry` initialization
6. HTTP/2 fallback activation path — document how test environments enable fallback
   when UDP/QUIC is blocked per ADR-0025
