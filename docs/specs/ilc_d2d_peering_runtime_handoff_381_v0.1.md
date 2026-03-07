# ILC D2d Peering Runtime Handoff 381 v0.1

Status: implementation handoff artifact  
Date: 2026-03-07  
Owner lane: G8 Constitution Cluster A

## 1. Implementation scope summary

Phase 381 implements deterministic D2d peering-loop runtime primitives in `ilc_core/network/d2d/peer.py` and keeps all behavior test-harness-only with no external networking.

## 2. Dependency/version lock section

Locked constants:
- `D2D_PEERING_RUNTIME_VERSION = "d2d_peering_runtime_381.v0.1"`
- `D2D_PEERING_DEPENDENCY = "d2d_peering_381.v0.1"`
- interface anchor import: `D2D_INTERFACE_DEPENDENCY` must remain `d2d_interface_380.v0.1`

Exact token:
- `D2D_PEERING_DEPENDENCY = "d2d_peering_381.v0.1"`

## 3. Peering state model summary

Lifecycle states:
- `disconnected`
- `handshaking`
- `connected`
- `backoff`

Deterministic state object:
- `PeeringState(peer_id, state, attempt, last_error)`

## 4. Deterministic handshake/reconnect strategy

Handshake path behavior:
- disconnected/backoff -> handshaking via `transition_to_handshaking`,
- handshaking -> connected on handshake success,
- handshaking -> backoff on handshake failure with explicit reason and incremented attempt count.

Reconnect selection behavior:
- `deterministic_reconnect_candidates` returns stable seeded ordering over candidate peers.

## 5. Asyncio boundary statement

Phase 381 introduces asyncio-compatible peering orchestration with deterministic mock-loop testing only.

No real socket, DNS, or wall-clock timeout behavior is implemented in Phase 381.

## 6. Deterministic validation-failure token catalog

Deterministic tokenized failures:
- `d2d_peering_state_invalid`
- `d2d_peering_transition_forbidden`
- `d2d_peering_handshake_reason_missing`
- `d2d_peering_limit_invalid`

## 7. Mutation-scope boundary statement

Phase-381 runtime mutations are limited to:
- `ilc_core/network/d2d/peer.py`

No decision-log mutation and no legacy network module mutation occur in this phase.

## 8. Carry-forward constraints for Phase 382

Phase 382 consumes this artifact for gossip state machine and CDL-039 invariant enforcement runtime.

Carry-forward constraints:
- preserve `D2D_PEERING_DEPENDENCY` constant unchanged,
- preserve imported interface dependency anchor to Phase 380,
- retain deterministic, non-network peering transition primitives as gossip-layer inputs,
- do not retroactively weaken no-real-network/no-wall-clock test-harness constraints.

## 9. Non-goals

Non-goals in Phase 381:
- no decision-log mutation,
- no CDL ratification action,
- no real socket or DNS operations,
- no wall-clock timeout behavior,
- no gossip-loop runtime implementation.
