# ILC Antigravity Context Capsule v2.9

Supersedes: docs/specs/ilc_antigravity_context_capsule_v2.8.md
Date: 2026-03-31
Owner lane: G8 Constitution Cluster A

This capsule is self-contained.

## 1. Current window state

Capsule v2.9 supersedes v2.8.
Window 555-564 is COMPLETE.
Window 565-574 is the next planning window.

## 2. CDL status summary

CDL-052 is ratified.
CDL-059 is ratified.
CDL-060 is ratified.
CDL-061 (ILC gossip HTTP envelope — ratified Phase 561, http3_envelope_cbor + http2_fallback) is ratified.
CDL-053 remains reserved and unopened.

## 3. Window 555-564 summary

Window 555-564 ratified CDL-061, implemented `gossip_transport.py` in Phase 558,
implemented `gossip_peer_registry.py` in Phase 562, preserved the single-hop
CDL-060 lane, and kept dynamic peer discovery out of scope.

## 4. D2d and governance carry-forward state

ADR-0025 is Accepted. HTTP/3 over QUIC is the production transport binding and
HTTP/2 over TCP is the fallback binding.
Phase 556 closed the signal floor invariant note in ADR-0023.
The D2d sub-package now includes `gossip_transport.py` (558) and
`gossip_peer_registry.py` (562).
Canary coverage is now 8 probes.

## 5. Separate lanes

CDL-053 remains reserved and separate.
Multi-hop remains deferred because `sim_multi_hop_01_insufficient` is still the
active evidence disposition.
Static peer registry v1 remains separate from any future dynamic discovery lane.

## 6. Next window state

Window 565-574 is the next target window.
Primary carry-forwards are multi-machine packaging, genesis export/import, node
lifecycle runtime, static peer config format, HTTP/2 fallback activation path,
and ops playbook v1.
