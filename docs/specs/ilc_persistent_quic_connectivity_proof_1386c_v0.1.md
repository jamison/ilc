# ILC Persistent QUIC Connectivity Proof 1386c v0.1

**Phase:** 1386c
**Date:** 2026-05-18
**Status:** complete

## Tokens

```text
persistent_validator_quic_sessions_proven_phase_1386c
direct_quic_path_proven_phase_1386c
cdl_078_relay_fallback_implemented_phase_1386c
no_hardcoded_peer_list_activation_path_confirmed_phase_1386c
write_path_projection_rejected_phase_1386c
```

## Summary

Phase 1386c implements and tests persistent per-topology-epoch QUIC sessions in
`ilc_consensus/`. The new session path is driven by an ADR-0039 endpoint
projection rebuilt from signed `QUIC_ENDPOINT` edges, not by a hardcoded peer
list. Direct QUIC is tried first. If direct QUIC fails and a signed relay edge
exists, the session manager selects the CDL-078 relay fallback path.

The production activation guard now rejects `settlement_path=mysticeti_fast_path`
unless `endpoint_projection_path` is present. Legacy config `peers` remain
available only under `settlement_path=none`, which is the non-activation/testnet
posture.

## Claim Verification Table

| Claim | File/symbol checked | Result |
|-------|---------------------|--------|
| Phase 1386b ADR is committed | `docs/adr/ADR_0039_Validator_Endpoint_Registry.md`; `docs/phases/STATUS.md` | confirmed |
| ADR-0038/CDL-090 identity bootstrap supplies endpoint-claim authority | ADR-0039 direct read; Phase 1386b STATUS entry | confirmed |
| QUIC session management exists in `ilc_consensus/` | `ilc_consensus/src/network.rs`; `ilc_consensus/src/node.rs` | confirmed |
| Existing `NodeRunner` used transient config peer addresses before this phase | `ilc_consensus/src/main.rs`; `ilc_consensus/src/node.rs` | confirmed |
| CDL-078 relay is ratified but service is not activated | `docs/specs/ilc_constitutional_decision_log_v0.1.md`; ADR-0039 non-goals | confirmed |
| Phase 1360 Fix2 proof was injected-checkpoint/local-commit only | `docs/research/ilc_validator_connectivity_production_model_v0.1.md`; sequence lock | confirmed |
| macOS inbound QUIC issue remained a connectivity concern | Phase 1360 Fix2/Fix2a planning references | confirmed |

## Implementation

New Rust module:

```text
ilc_consensus/src/persistent_quic.rs
```

Main elements:

| Element | Purpose |
|---------|---------|
| `QuicEndpointEdge` | Runtime representation of a signed ADR-0039 `QUIC_ENDPOINT` edge |
| `EndpointProjection::rebuild_from_signed_edges` | Sole projection constructor; rejects stale topology epochs, empty source hashes, empty signer fields, and duplicate endpoint entries |
| `PersistentQuicSessionManager` | Maintains one persistent QUIC connection per validator for the current topology epoch |
| `SessionPath::DirectQuic` | Primary direct peer-to-peer QUIC path |
| `SessionPath::Cdl078RelayFallback` | Secondary relay pass-through fallback selected only after direct failure |
| `projection_source_rejects_write_path_1386c` | Acceptance guard for write/update/set/insert/delete projection methods |

Activation guard changes:

| File | Change |
|------|--------|
| `ilc_consensus/src/config.rs` | Adds optional `endpoint_projection_path` to `NodeConfig` |
| `ilc_consensus/src/main.rs` | Requires `endpoint_projection_path` for `settlement_path=mysticeti_fast_path`; otherwise returns an error |
| `ilc_consensus/src/node.rs` | Wires `NodeRunner` to use `PersistentQuicSessionManager` when a production projection is loaded |
| `ilc_consensus/src/lib.rs` | Exports `persistent_quic` |
| `ilc_consensus/Cargo.toml` | Enables `rand_core/std`, required for existing `pq_sign_main.rs` test compilation |

## Proof Evidence

Required command:

```bash
cd ilc_consensus && /Users/jamison/.cargo/bin/cargo test test_persistent_quic_sessions_1386c -- --nocapture
```

Result:

```text
test persistent_quic::tests::test_persistent_quic_sessions_1386c ... ok
test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 90 filtered out
```

This test proves:

- Direct QUIC path: a client endpoint builds a session from a projection direct
  edge, opens a persistent QUIC connection, sends a `MissingEpochSync` envelope,
  and the server receives it through mTLS-bound `PeerNetwork::receive`.
- Persistence: a second `ensure_session()` call for the same validator and
  topology epoch reuses the existing live connection.
- Relay fallback: a projection containing an unreachable direct endpoint plus a
  signed relay endpoint selects `SessionPath::Cdl078RelayFallback` and delivers
  the same envelope through the relay endpoint.

Required command:

```bash
cd ilc_consensus && /Users/jamison/.cargo/bin/cargo test test_write_path_projection_rejected_1386c -- --nocapture
```

Result:

```text
test persistent_quic::tests::test_write_path_projection_rejected_1386c ... ok
test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 90 filtered out
```

This test proves:

- Read-only projection source with `rebuild_from_signed_edges` and read methods
  is accepted.
- A projection source containing `update_endpoint` is rejected and emits
  `write_path_projection_rejected_phase_1386c`.

Additional in-module test:

```text
test_projection_rebuild_rejects_stale_epoch_1386c
```

This verifies stale topology-epoch edges cannot build the projection.

## No Hardcoded Peer List Activation Path

`main.rs` now gates live Mysticeti activation as follows:

```text
settlement_path=mysticeti_fast_path
  -> endpoint_projection_path required
  -> bounded projection JSON loaded from signed-edge snapshot
  -> NodeRunner uses PersistentQuicSessionManager for outbound sends

settlement_path=none
  -> legacy config peers allowed for non-activation/testnet posture only
```

This satisfies `no_hardcoded_peer_list_activation_path_confirmed_phase_1386c`.

## macOS QUIC Issue Status

Phase 1360 Fix2 observed a macOS inbound QUIC issue consistent with
Tailscale/QUIC routing, with exact root cause unconfirmed without packet
capture. Phase 1386c addresses the production-design risk by proving:

- direct QUIC remains the primary path when reachable;
- direct failure does not block consensus connectivity if a signed relay edge
  is available;
- the fallback is selected from the same read-only endpoint projection and does
  not reintroduce a hardcoded peer list.

This phase does not claim the historical macOS packet-routing root cause was
forensically resolved.

## Non-Authorizations

Phase 1386c does not:

- mutate any CDL register row;
- mutate `ilc_core/`;
- activate CDL-078 relay service;
- publish endpoint claims publicly;
- activate public P2P;
- deploy production validators;
- activate wallet, ECU, ILC, settlement, value-path, claimability, mining, or
  public RC behavior.

## Graph Delta

```text
graph_delta=load_bearing_artifact_added:ilc_consensus/src/persistent_quic.rs -> validator-connectivity/persistent-quic-session-manager
graph_delta=load_bearing_artifact_changed:ilc_consensus/src/main.rs -> validator-connectivity/no-hardcoded-peer-list-activation-guard
graph_delta=load_bearing_artifact_changed:ilc_consensus/src/node.rs -> validator-connectivity/persistent-quic-node-runner-integration
graph_delta=load_bearing_artifact_changed:ilc_consensus/src/config.rs -> validator-connectivity/endpoint-projection-config-field
graph_delta=load_bearing_artifact_added:docs/specs/ilc_persistent_quic_connectivity_proof_1386c_v0.1.md -> phase-1386c-persistent-quic-proof
```
