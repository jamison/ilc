# ILC CCSS-003 Sealed Sender Local Delivery Boundary 1326 v0.1

**Phase:** 1326
**Status:** Local/private contract recorded.
**Authority:** This document and its implementation do not activate public P2P,
public relay serving, public confidential coordination serving, public
confidential messaging, source publication, release material, signing, identity
bootstrap, wallet actions, ECU minting, ILC settlement, or value-path activation.

```text
ccss_003_sealed_sender_local_delivery_boundary_phase_1326.v0.1
sealed_sender_fixed_size_payload_boundary_recorded_phase_1326
h013_h015_dependency_seams_recorded_phase_1326
public_p2p_not_activated_by_ccss_phase_1326
phase_1327_ccss_gossip_jitter_cover_policy_next
public_rc_remains_blocked_after_phase_1326
```

## 1. Scope

CCSS-003 records the private/local sealed-sender delivery boundary for the
Confidential Coordination Sidecar Suite. It defines deterministic record shapes
for fixed-size sealed payload classes, local delivery intents, local delivery
receipts, and safe delivery-state projections.

This phase reuses the existing H-013/H-015 seams as dependencies:

- H-013 sealed-sender primitive: `run_h013_d2d_sealed_sender_adr_verdict=accepted`
- H-015 routing primitive: `spectral_routing_runtime_h015.v0.1`

The sidecar does not import or activate D2d transport. The boundary is
contract-only and local/private.

## 2. Record Surface

Implementation path:
`ilc_core/sidecars/confidential_coordination_sealed_sender.py`

| Record | Purpose |
|--------|---------|
| `sealed_payload_class_ref` | Records allowed H-013 fixed-size sealed payload classes: 2108-byte inner envelope and 4156-byte outer envelope. |
| `sealed_local_delivery_intent` | Records a local delivery intent using opaque private-shard, capability, sealed-payload digest, relay-instruction, channel, and delivery-token refs. |
| `sealed_local_delivery_receipt` | Records local receipt without revealing recipient identity, route history, IP address, harness identity, or payload. |
| `sealed_delivery_projection` | Records private/local delivery state only. |

Delivery states:

```text
sealed_pending_local
sealed_delivered_local
rejected_size_class
rejected_metadata_leak
rejected_replay
blocked_public_transport
```

## 3. Security Invariants

- Canonical JSON uses deterministic key ordering, compact separators, and
  `allow_nan=False`.
- Payload traversal rejects floats, tuples, cycles, over-depth trees,
  over-node trees, oversized strings, oversized integers, mapping-key abuse,
  ASCII control characters, and oversized canonical payloads before final JSON
  serialization.
- Epochs and sequences are positive and bounded.
- Record refs are SHA-256 canonical-body commitments.
- Public flags are required false, including public P2P, public relay serving,
  public confidential coordination serving, public confidential messaging,
  non-loopback listener, network transport, unbounded queues, and wall-clock
  expiry as protocol truth.
- Projection records expose state only and do not expose sender identity,
  recipient identity, route history, retry schedule, IP address, harness
  identity, plaintext, raw sealed payloads, agent IDs, wallet IDs, seed material,
  private keys, secret material, or ZK witnesses.

## 4. Non-Claims

Phase 1326 does not claim Signal compatibility, a messaging product, anonymity,
public relay serving, public confidential coordination serving, or public P2P.
H-013/H-015 are dependency seams only. Phase 1327 remains responsible for
gossip announce/pull, jitter, batching, cover-policy, and traffic-analysis
negative tests.

## 5. Verification

Focused tests:

```bash
.venv/bin/python -m pytest tests/test_phase_1326_ccss_003_sealed_sender_local_delivery_boundary.py
```

Sensitive runtime guardrail:

```bash
.venv/bin/python -m pytest tests/test_sensitive_runtime_coding_taboos.py
```

Package-profile audit was refreshed because the local sidecar surface changed.

## 6. Graph Delta

```text
graph_delta=load_bearing_artifact_added:ilc_core/sidecars/confidential_coordination_sealed_sender.py -> graph-native-sidecars/confidential-coordination/ccss-003-sealed-sender-local-delivery-boundary
graph_delta=load_bearing_artifact_changed:ilc_core/sidecars/registry_manifest.py -> graph-native-sidecars/registry/confidential-coordination
graph_delta=load_bearing_artifact_added:docs/specs/ilc_ccss_003_sealed_sender_local_delivery_boundary_1326_v0.1.md -> graph-native-sidecars/confidential-coordination/ccss-003-sealed-sender-local-delivery-boundary
```
