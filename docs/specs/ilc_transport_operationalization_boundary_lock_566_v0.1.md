# ILC Transport Operationalization Boundary Lock 566 v0.1

Status: locked
Date: 2026-04-01
Phase: 566
Owner lane: G8 implementation cluster

## 1. Purpose and pass target

Phase 566 locks the runtime boundary for the first operational transport
implementation. The purpose is to authorize a thin real-HTTP wrapper around the
ratified CDL-061 envelope helper without allowing this window to collapse into a
full node-orchestration rewrite.

## 2. Selected runtime boundary

The selected runtime boundary is a new wrapper module:
- `ilc_core/network/d2d/http_gossip_transport_runtime.py`

This wrapper must:
- consume `gossip_transport.py`
- consume `gossip_peer_registry.py`
- must not duplicate the CDL-061 header contract
- leave a clean adapter seam for the later node-orchestration redesign

The selected boundary is recorded as `minimal_http_transport_wrapper_selected`.

## 3. Transport-kind operationalization rule

Transport-kind behavior is locked as follows:
- ADR-0025 continues to define `kind=quic` as the production binding.
- The first operational three-machine proof may use `kind=http` when explicitly
  selected by configuration for environments where QUIC or UDP is blocked.
- This phase only authorizes the explicit `kind=http` fallback-proof lane; it
  does not authorize hidden downgrade logic or protocol-level renegotiation.
- This does not reopen or weaken ADR-0025.
- Automatic fallback remains out of scope for Window 565-574.

## 4. TLS and identity posture

The testbed identity and security posture is locked as follows:
- server TLS plus `ILC-Signature` is required for Window 565-574
- mTLS is deferred to a post-testbed hardening tranche
- transport logs must expose selected transport kind and failure lane clearly

## 5. Explicit exclusions

This phase explicitly rejects:
- placeholder transport branches
- direct edits to `gossip_transport.py` that expand the envelope contract
- agent-loop wiring
- DHT or discovery work
- multi-hop

## 6. Governance tokens

Required governance tokens locked by this phase:
- `minimal_http_transport_wrapper_selected`
- `fallback_first_operational_proof_permitted_under_explicit_config`
- `kind_quic_remains_production_binding`
- `kind_http_may_satisfy_testbed_proof_when_explicitly_selected`
- `server_tls_plus_ilc_signature_locked_for_565_574`
- `full_node_orchestration_redesign_deferred_post_574`
