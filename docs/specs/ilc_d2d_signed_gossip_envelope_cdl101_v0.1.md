# ILC D2D Signed Gossip Envelope CDL-101 v0.1

Status: opened
Date: 2026-07-06
Phase: 1570
CDL: CDL-101
Dependency token: `cdl_101_d2d_signed_gossip_envelope_phase_1570.v0.1`
Public RC status: blocked
Runtime activation status: not authorized

## 1. Background And Motivation

The Block 6 deep code audit found that the private D2D gossip receiver validates
headers and records body-hash evidence, but it does not yet verify that
`ILC-Signature` was produced by an authorized ML-DSA-65 peer key. Commit
`086bfd81` hardened receipt/body binding, but that receipt remains
informational until signer identity, routing context, and `payload_sha256` are
cryptographically bound in one signed context.

The live transport stack currently contains these facts:

| Source | Current value |
|---|---|
| `ilc_core/network/d2d/gossip_transport.py` | `GOSSIP_TRANSPORT_RUNTIME_VERSION = "gossip_transport_runtime_558.v0.1"` |
| `ilc_core/network/d2d/gossip_transport.py` | `CDL_061_DEPENDENCY = "cdl_061_ratified_561.v0.1"` |
| `ilc_core/network/d2d/gossip_transport.py` | `REQUIRED_HEADERS = {"ILC-Gossip-Type", "ILC-Channel", "ILC-Epoch", "ILC-Hop-Count", "ILC-Signature", "Content-Type"}` |
| `ilc_core/network/d2d/gossip_transport.py` | `FORBIDDEN_HEADER_KEYS = {"creator_agent_id", "node_id", "ILC-Creator-Agent-Id", "ILC-Node-Id"}` |
| `ilc_core/network/d2d/gossip_peer_registry.py` | `GOSSIP_PEER_REGISTRY_VERSION = "gossip_peer_registry_562.v0.1"` |
| `ilc_core/network/d2d/gossip_peer_registry.py` | `MAX_PEERS = 16` |
| `ilc_core/network/d2d/gossip_peer_registry.py` | Static endpoint-only registry; no `mldsa_pubkey_hex` field exists today |
| `ilc_core/network/d2d/http_gossip_transport_runtime.py` | `signature_sha256` is recorded for audit, but no cryptographic verify call is made |
| `ilc_core/network/d2d/bootstrap_fetch_runtime.py` | Existing ML-DSA-65 verify pattern uses `oqs.Signature("ML-DSA-65").verify(signed_bytes, sig_bytes, pubkey_bytes)` |
| `ilc_core/crypto/cose_sign1.py` | Ed25519-only implementation |
| `ilc_core/identity/endorsement_packet_schema.py` | `COSE_ALG_MLDSA65_CANDIDATE = -48` exists as a candidate/stub, not a complete COSE ML-DSA implementation |

This document opens CDL-101 as a successor governance surface for the signed
D2D gossip envelope. It does not ratify CDL-101 and does not activate runtime
verification.

## 2. Scope And Non-Scope

In scope:

- Define the v1 signed D2D gossip envelope context.
- Lock the signing scheme decision for Phases 1571 and 1572.
- Define new transport headers needed to locate the peer key.
- Bind transport peer identity inside the signed bytes rather than trusting a
  standalone HTTP header.
- Define replay-cache identity and actor-binding rules.
- Preserve CDL-039 and CDL-061 boundaries.

Out of scope:

- No `ilc_core/` runtime implementation is authorized by this phase.
- No public P2P, public relay, public RC, wallet write, treasury write,
  settlement, minting, Genesis signing, or source export is authorized.
- No COSE/ML-DSA implementation is authorized in v1.
- No delegated signing model is authorized in v1.
- No claim is made that current receivers already enforce this envelope.

## 3. Governance Form

Locked decision:

```yaml
governance_form: cdl061bis_successor  # CDL-101
```

Rationale: existing code pins `CDL_061_DEPENDENCY = "cdl_061_ratified_561.v0.1"`.
Changing CDL-061 retroactively would blur the dependency chain. CDL-101 extends
the envelope with a new dependency token while preserving the historical CDL-061
runtime boundary.

The new dependency token is:

```python
CDL_101_SIGNED_ENVELOPE_DEPENDENCY = "cdl_101_d2d_signed_gossip_envelope_phase_1570.v0.1"
```

## 4. Signing Scheme

Locked decision:

```yaml
envelope_signing_scheme: canonical_json_v1
```

Rationale: the repository already contains an ML-DSA-65 verification pattern in
`bootstrap_fetch_runtime.py`. The COSE code path is currently Ed25519-only, and
`COSE_ALG_MLDSA65_CANDIDATE = -48` is only a candidate/stub. A COSE/ML-DSA
variant remains a future v2 design lane, not a Phase 1571 implementation
prerequisite.

## 5. Canonical Signed Context

The receiver reconstructs this exact dictionary from the envelope fields and
body bytes before verification. The signed message includes exactly these
fields and no others:

```json
{
  "channel": "<ILC-Channel value>",
  "content_type": "<Content-Type value>",
  "domain": "ILC-D2D-GossipEnvelope-v1",
  "envelope_version": "1",
  "epoch": 0,
  "gossip_type": "<ILC-Gossip-Type value>",
  "hop_count": 1,
  "key_id": "<stable key identifier, opaque string>",
  "payload_sha256": "<hex-encoded SHA-256 of body bytes>",
  "peer_id": "<sender static peer registry ID>",
  "signature_alg": "ML-DSA-65"
}
```

Canonical serialization:

```python
json.dumps(context, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
```

Required invariants:

- `domain` prevents cross-protocol replay.
- `envelope_version` is `"1"`; unknown versions fail closed.
- `peer_id` is reconstructed from `ILC-Sender-Peer-Id` and is signed.
- `key_id` is reconstructed from `ILC-Key-Id` and is signed.
- `signature_alg` is `"ML-DSA-65"` and is signed.
- `payload_sha256` is SHA-256 over the raw body bytes and is signed.
- `hop_count` is the integer value of `ILC-Hop-Count`; v1 requires `1`.
- `epoch` is the integer value of `ILC-Epoch`.
- `content_type`, `channel`, and `gossip_type` are all signed.

An attacker who changes `ILC-Sender-Peer-Id`, `ILC-Key-Id`, payload bytes, or
routing headers changes the reconstructed signed context and invalidates the
signature.

## 6. New Envelope Headers

CDL-101 introduces these v1 headers:

| Header | Meaning | Signed field |
|---|---|---|
| `ILC-Sender-Peer-Id` | Static transport peer registry identifier | `peer_id` |
| `ILC-Key-Id` | Stable identifier for the ML-DSA-65 public key entry | `key_id` |

These headers are routing hints until signature verification succeeds. They are
not independently trusted assertions.

The new headers do not collide with CDL-039 forbidden keys. CDL-101 does not
introduce `ILC-Creator-Agent-Id`, `ILC-Node-Id`, `creator_agent_id`, or
`node_id`.

## 7. CDL-039 Topology-Privacy Compatibility

`ILC-Sender-Peer-Id` is a transport-layer peer registry key. It is not an
agent ID, graph node ID, creator identity, or authorship claim unless the peer
registry explicitly maps it to authorized actors.

CDL-101 preserves the CDL-039 forbidden-header boundary:

- Do not add `ILC-Creator-Agent-Id`.
- Do not add `ILC-Node-Id`.
- Do not infer graph authorship from `ILC-Sender-Peer-Id`.
- Do not use the peer ID as a public CCSS anonymity or unlinkability surface.

## 8. Peer Registry Extension Requirements

Phase 1571 must extend the static peer registry without breaking `MAX_PEERS = 16`.
The v1 structured peer entry must support at least:

```json
{
  "endpoint": "https://example.invalid:443",
  "peer_id": "peer-main-1",
  "mldsa_pubkey_hex": "<ML-DSA-65 public key hex>",
  "key_id": "mldsa65-main-2026-07",
  "valid_from_epoch": 0,
  "valid_until_epoch": null,
  "authorized_actor_ids": ["<agent-or-panel-id>"]
}
```

Backward-compatible plain-string endpoint entries may remain loadable during
rollout, but they are unverifiable. Phase 1572 must buffer or reject them per
policy rather than treating them as signed/verified peers.

## 9. Replay Policy

Replay cache key:

```text
(peer_id, key_id, epoch, gossip_type, channel, payload_sha256)
```

Replay semantics:

- A duplicate cache key is rejected with HTTP 409.
- Cache TTL is 2 validation epochs.
- `signature_sha256` is audit metadata only and must not be part of replay
  identity.
- A receiver records a replay-cache entry only after key validity, signature
  verification, and actor-binding checks pass.
- The cache must fail closed on malformed epoch, missing key, unsupported
  signature algorithm, or unknown envelope version.

## 10. Actor-Binding Rule

Actor-binding mode:

```yaml
actor_binding_rule: peer_id_maps_to_authorized_actor_ids
delegation: out_of_scope_v1
```

For authority-bearing gossip types, the verified `peer_id` must authorize the
payload's claimed actor through the peer registry:

```text
claimed_actor in registry[peer_id].authorized_actor_ids
```

If not, the receiver rejects with HTTP 400 and token
`d2d_actor_binding_mismatch`.

The equality rule `peer_id == claimed_actor` is valid only when a deployment
explicitly chooses `peer_id_is_agent_id`. It is not the v1 default.

## 11. Authority-Bearing Gossip Types

Minimum v1 authority-bearing gossip types:

- `agent_submission`
- `panel_verdict`
- `ecu_claim_batch`

Any future gossip type that asserts a graph actor, panel actor, wallet actor, or
settlement actor must add an explicit actor extraction rule before it can be
treated as verified under CDL-101.

## 12. Forward Obligation

Delegation and key rotation require a separate safety model before activation
beyond static v1 mappings.

Forward obligation token:

```text
tla_plus_obligation_delegation_key_rotation_safety
```

The future model must prove, or mechanically check, at least:

- Key validity intervals cannot authorize stale signatures after expiry.
- Replay cache state cannot be poisoned by unauthenticated envelopes.
- Delegated actor authority cannot survive revocation.
- Key rotation cannot create an ambiguous signer for a given
  `(peer_id, key_id, epoch)` tuple.

## 13. Non-Activation Statement

Phase 1570 opens CDL-101 and defines the signed envelope specification. It does
not ratify CDL-101, implement receiver-side verification, modify runtime code,
clear production guards, activate public P2P, activate public relay serving,
activate CCSS public transport, execute wallet writes, execute treasury writes,
mint, settle, sign Genesis artifacts, publish public RC, or move epoch 0 to
epoch 1.
