# ILC D2d Abstract Interface Runtime Handoff 380 v0.1

Status: implementation handoff artifact  
Date: 2026-03-07  
Owner lane: G8 Constitution Cluster A

## 1. Implementation scope summary

Phase 380 implements only D2d abstract interface surfaces in `ilc_core/network/d2d/` and defers behavioral networking logic to later phases.

## 2. Dependency and version lock section

Locked constants:
- `D2D_INTERFACE_RUNTIME_VERSION = "d2d_interface_runtime_380.v0.1"`
- `D2D_INTERFACE_DEPENDENCY = "d2d_interface_380.v0.1"`
- `WIRE_TRANSPORT_DEPENDENCY = "wire_transport_runtime_323.v0.1"`

## 3. D2d abstract interface surface summary

Implemented interface surfaces:
- `D2dMessage` dataclass for normalized abstract envelope shape,
- `D2dPeer` protocol contract for later peering-loop behavior,
- `D2dTopology` protocol contract for deterministic candidate-peer surface,
- `D2dChannel` opaque transport identifier helper.

## 4. No-asyncio/no-I-O boundary statement

Phase 380 is abstract-interface only; no asyncio, no peering loop, no gossip loop.

No socket binds, DNS lookups, or network I/O operations are implemented in this phase.

## 5. Deterministic validation-failure token catalog

Deterministic validation tokens exposed in runtime validators:
- `d2d_channel_invalid`
- `d2d_channel_not_opaque`
- `d2d_peer_id_invalid`
- `d2d_message_envelope_not_object`
- `d2d_message_id_invalid`
- `d2d_payload_cid_invalid`
- `d2d_transport_headers_not_object`
- `d2d_transport_header_key_invalid`
- `d2d_transport_header_value_invalid`

## 6. Mutation-scope boundary statement

Phase-380 runtime mutations are limited to:
- `ilc_core/network/d2d/__init__.py`
- `ilc_core/network/d2d/interface.py`

No runtime implementation of CDL-039 invariants occurs in Phase 380.

## 7. Carry-forward constraints for Phase 381

Phase 381 consumes this artifact for peering-loop implementation.

Carry-forward constraints:
- preserve Phase-380 dependency constants unchanged,
- import and use Phase-380 protocol/dataclass surfaces,
- keep deterministic test harness policy (no real socket, DNS, wall-clock waits),
- introduce asyncio only in Phase-381 behavior modules.

## 8. Non-goals

Non-goals in Phase 380:
- no decision-log mutation,
- no CDL ratification action,
- no peering-loop behavior,
- no gossip-loop behavior,
- no transport-layer runtime enforcement of CDL-039 invariants.
