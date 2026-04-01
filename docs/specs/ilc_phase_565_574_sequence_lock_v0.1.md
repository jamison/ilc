# ILC Phase 565-574 Sequence Lock v0.1

Status: locked
Date: 2026-04-01
Phase: 565
Owner lane: G8 implementation cluster

## 1. Window summary

Window 565-574 operationalizes the ratified CDL-061 envelope over real HTTP for
the first three-machine ILC testbed. The window combines transport
operationalization and startup/package/genesis flow in one implementation lane,
while preserving a strict pass hierarchy: real HTTP transport is the primary
gate, and packaging plus genesis reproducibility is the supporting lane.

Required lock tokens:
- `three_machine_http_transport_primary_gate`
- `packaging_and_genesis_secondary_lane`
- `json_static_peer_config_v1`
- `http2_fallback_explicit_config_only`
- `server_tls_plus_ilc_signature_testbed_v1`
- `node_orchestration_redesign_deferred_post_574`
- `http_machine_payment_skill_deferred_to_575_584`
- `http_machine_payment_ingress_deferred_to_595_plus`

## 2. Hard pass condition

Window 565-574 passes only if all of the following are true:
1. Three separate machines start nodes from packaged environments.
2. Each node loads JSON static peer configuration into `GossipPeerRegistry`.
3. Each node imports the agreed genesis artifact successfully.
4. At least one machine sends ratified CDL-061 gossip traffic to the others over
   real HTTP transport.
5. Recipients validate the ratified envelope and record deterministic success or
   failure in operator-visible logs.
6. The ADR-0025 fallback lane under `kind=http` can be enabled explicitly and
   tested in an environment where QUIC or UDP is unavailable.
7. Restarting a node preserves the minimum required startup state.
8. No DHT, dynamic discovery, multi-hop behavior, or agent-loop expansion is
   introduced to satisfy the milestone.

## 3. Phase table

| Phase | Description | Primary output | Sensitive? |
|---|---|---|---|
| 565 | Window 565-574 sequence lock | `ilc_phase_565_574_sequence_lock_v0.1.md` | No |
| 566 | Transport operationalization boundary lock | `ilc_transport_operationalization_boundary_lock_566_v0.1.md` | No |
| 567 | Genesis, package, and lifecycle scoping | `ilc_genesis_package_lifecycle_scoping_567_v0.1.md` | No |
| 568 | Real HTTP transport wrapper runtime | `ilc_core/network/d2d/http_gossip_transport_runtime.py` | YES |
| 569 | Transport hardening and explicit fallback activation | Hardening tests + canary update | YES |
| 570 | Static peer-config JSON loader and startup wiring | `ilc_core/node/node_startup_runtime.py` | YES |
| 571 | venv + systemd packaging and lifecycle runtime | service runner + unit file(s) | YES |
| 572 | Deterministic three-machine smoke harness | smoke harness + fixtures | YES |
| 573 | Coherence report + capsule v3.0 | report + capsule | No |
| 574 | Window 565-574 closure gate and handoff | gate script + handoff | YES |

## 4. Locked implementation decisions

The following implementation decisions are locked for the full window:
- Same-window scope includes both transport operationalization and node
  startup/package flow.
- `three_machine_http_transport_primary_gate` remains the decisive window proof.
- `packaging_and_genesis_secondary_lane` remains required for reproducibility.
- `json_static_peer_config_v1` is the static operator configuration format.
- NDJSON remains the append-only log and trace format; it is not used for static
  configuration.
- `venv + systemd` is the packaging target for the first three-machine testbed.
- `http2_fallback_explicit_config_only` means the ADR-0025 fallback lane under
  `kind=http` is operator-selected only in this window.
- `server_tls_plus_ilc_signature_testbed_v1` is the security posture for the
  testbed.
- `node_orchestration_redesign_deferred_post_574` remains active; this window
  must leave clean seams for the later redesign rather than absorb it.

## 5. Carry-forward inputs from Window 555-564

The following carry-forwards are locked into this window:
- CDL-061 remains ratified and bounded to the envelope contract only.
- `gossip_transport.py` remains the canonical envelope helper surface.
- `gossip_peer_registry.py` remains `static_v1` with no DHT or dynamic discovery.
- `recommended_decay_floor >= recommended_u_floor` remains documented in ADR-0023.
- Multi-hop remains deferred under `sim_multi_hop_01_insufficient`.

## 6. Protected boundaries and anti-pattern exclusions

The following constraints are non-negotiable for Window 565-574:
- No placeholder remote/runtime branches with no real I/O.
- No counting manifests, file counts, or module counts as milestone evidence.
- No automatic fallback negotiation.
- No mTLS.
- No DHT or dynamic discovery.
- No multi-hop.
- No agent-loop expansion.
- No forward-looking use of third-party wallet-brand terminology; use
  `HTTP machine-payment skill` and `HTTP machine-payment ingress` instead.

## 7. Sequence integrity rule

Window 565-574 must execute in this order:
1. Phase 565 sequence lock.
2. Phase 566 transport operationalization boundary lock.
3. Phase 567 genesis/package/lifecycle scoping.
4. Phase 568 real HTTP transport wrapper runtime.
5. Phase 569 hardening and explicit fallback activation.
6. Phase 570 static peer-config loader and startup wiring.
7. Phase 571 venv + systemd packaging and lifecycle runtime.
8. Phase 572 deterministic three-machine smoke harness.
9. Phase 573 coherence report and capsule v3.0.
10. Phase 574 closure gate and handoff.

This ordering preserves the implementation-first lane while keeping governance,
transport contract boundaries, and the later node-orchestration redesign cleanly
separated.
