# ILC Antigravity Context Capsule v3.0

Supersedes: docs/specs/ilc_antigravity_context_capsule_v2.9.md
Date: 2026-04-01
Owner lane: G8 implementation cluster

This capsule is self-contained.

## 1. Current window state

Capsule v3.0 supersedes v2.9.
Window 565-574 is at closure-gate stage.
Observed result through Phase 573: the implementation lane is complete, the
local deterministic three-node smoke proof passed, and the operator-guided
external three-machine proof is recorded for execution.

## 2. Current transport and startup state

The D2d sub-package now includes:
- `gossip_transport.py` as the ratified CDL-061 envelope helper
- `gossip_peer_registry.py` as the `static_v1` peer registry
- `http_gossip_transport_runtime.py` as the thin real-HTTP wrapper

The node/startup and packaging surfaces now include:
- `node_startup_runtime.py` for JSON config and genesis import reference loading
- `run_ilc_node_service_v1.py` for deterministic lifecycle execution
- `deploy/systemd/ilc-node-v1.service` for the testbed service path
- `run_three_machine_smoke_phase_572.sh` for local smoke and operator-guided
  external proof

## 3. Governance and scope state

ADR-0025 is Accepted. `kind=quic` remains the production binding and
`kind=http` remains the explicit fallback-proof lane for the current testbed.
CDL-061 remains ratified and bounded to the envelope contract.
Dynamic peer discovery, DHT, multi-hop, and agent-loop expansion remain out of
scope for the completed infrastructure window.

## 4. Security posture state

Window 565-574 uses server TLS plus `ILC-Signature`.
Mutual TLS is deferred to the first post-RC0 hardening tranche after the
Window 585-594 public release-candidate evaluation lane.
Automatic fallback negotiation is also deferred to that hardening tranche.

## 5. Post-574 priority order

1. Window 575-584: agent behavioral loop v1, 7+1 panel wiring, and outbound
   HTTP machine-payment skill
2. Window 585-594: deterministic RC0 public release-candidate integration pass
3. Post-RC0 hardening: mTLS, automatic fallback, stronger packaging, and fuller
   node-orchestration redesign
4. Window 595+: inbound HTTP machine-payment ingress as a separate
   treasury-governed lane

## 6. Naming and forward-language rule

Forward-looking language uses `HTTP machine-payment skill` and
`HTTP machine-payment ingress` only. No external wallet-brand nomenclature is
active in the current launch path.
