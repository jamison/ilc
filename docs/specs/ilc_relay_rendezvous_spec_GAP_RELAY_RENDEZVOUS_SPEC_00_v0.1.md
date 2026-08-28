# ILC Relay Rendezvous Semantics and Abuse Limits
Version: v0.1
Phase: GAP-RELAY-RENDEZVOUS-SPEC-00
Date: 2026-08-28
Status: ratified-spec-candidate
Governs: relay admission, relay slot lifecycle, pass-through invariant, abuse limits, pre-RC relay host governance
Authority: ADR-0039, CDL-078, GAP-CONNECTIVITY-RECONCILE-00, GAP-AUTO-NAT-TRAVERSAL-POLICY-00

Output token: `relay_rendezvous_spec_committed_GAP_RELAY_RENDEZVOUS_SPEC_00`

## 1 - Design Boundary

The relay/rendezvous path is an ILC-native reachability fallback for NAT-blocked or firewall-constrained installs. It helps a valid AgentID receive inbound traffic when direct reachability is unavailable, but it does not create validator authority, economic authority, claimability authority, or public ledger authority.

Relay/rendezvous sits below signed graph authority. It forwards encrypted transport bytes and advertises a temporary forwarding address only after admission succeeds. The relay is not the source of truth for identity, endpoint claims, validator set membership, or consensus message validity.

The pre-RC deployment model is a Genesis-controlled relay host. A post-RC relay operator market is deferred and requires separate governance before any non-Genesis relay may receive rewards or authority.

## 2 - Option A Admission

Relay admission policy is Option A: invite-provenance-gated.

A relay slot may be granted only to a request that proves all of the following:

| Requirement | Verification basis |
|---|---|
| Installed AgentID | The requester presents a 96-character AgentID produced by the onboarding identity path. |
| Invite provenance | The requester presents a completed invite redemption record rooted in a Genesis-traced invite batch. |
| Proof of possession | The requester signs the relay admission transcript with the onboarded key, reusing the invite PoP mechanism from GAP-AGENT-ONBOARDING-00d. |
| Nullifier binding | The request references the invite nullifier or a successor privacy-preserving nullifier proof. |
| Software profile | The request declares the installed ILC software version and network profile. |
| Slot uniqueness | The relay confirms no active slot already exists for the AgentID unless an explicit future policy allows rotation. |

The admission transcript must be canonical JSON with sorted keys, compact separators, and no floats. Minimum fields:

```json
{
  "agent_id": "<96-lowercase-hex>",
  "admission_epoch": 0,
  "domain": "ilc-relay-rendezvous-admission-v1",
  "invite_nullifier": "<sha256-hex-or-successor-proof-ref>",
  "network_id": "public-rc",
  "requested_internal_port": 50151,
  "requested_protocol": "quic",
  "software_version": "0.4.x"
}
```

The relay server must reject missing, malformed, stale, or replayed admission transcripts. A successful relay admission creates a relay slot only; it does not admit the AgentID as an active validator.

## 3 - Relay Slot Lifecycle

A relay slot is a bounded grant allowing one admitted AgentID to receive pass-through inbound traffic through a relay endpoint.

Lifecycle states:

| State | Meaning | Exit condition |
|---|---|---|
| `requested` | Client submitted an admission request. | Grant, rejection, or timeout. |
| `granted` | Relay assigned endpoint, slot ID, and TTL. | Activation after client acknowledgement. |
| `active` | Relay forwards traffic for the slot. | TTL expiry, release, revocation, or abuse limit. |
| `renewing` | Client requests a per-epoch keepalive/renewal. | Renewal accepted or slot expires. |
| `released` | Client gracefully closed the slot. | Terminal. |
| `revoked` | Relay closed the slot for abuse, invalid proof, stale epoch, or operator safety. | Terminal until fresh admission. |
| `expired` | Slot TTL elapsed without successful renewal. | Terminal until fresh admission. |

Keepalive cadence is per protocol epoch, not per second. Wall-clock timers may be used only for local socket timeout safety, not for protocol validity decisions. A relay implementation must not call `datetime.now()` or `time.time()` to decide whether a protocol epoch is valid.

Slot grant fields:

| Field | Type | Rule |
|---|---|---|
| `slot_id` | string | Relay-generated opaque identifier, unique for active slots. |
| `agent_id` | string | Bound to admitted AgentID. |
| `relay_endpoint` | object | Host, port, transport, and relay mode. |
| `target_internal_port` | uint16 | Single local port requested by the client. |
| `granted_epoch` | uint64 | Protocol epoch of grant. |
| `ttl_epochs` | uint16 | Bounded slot lifetime. Suggested pre-RC maximum: 4 epochs. |
| `max_bytes_per_epoch` | uint64 | Per-slot byte budget. |
| `max_concurrent_streams` | uint16 | Per-slot stream cap. |
| `revocation_ref` | string or null | Populated when revoked. |

## 4 - Non-Termination Invariant

The relay mode for consensus-compatible traffic is `pass_through_consensus_quic`.

The relay MUST NOT terminate, decrypt, inspect, re-sign, rewrite, or re-origin consensus messages. It may route encrypted bytes between a client and remote peer, enforce byte/connection limits at the transport envelope level, and drop traffic when policy limits are exceeded. It must not become a hidden consensus gateway.

Allowed relay behavior:

| Behavior | Allowed? | Notes |
|---|---:|---|
| Forward encrypted QUIC bytes | Yes | Pass-through only. |
| Track slot ID, AgentID, byte counts, and TTL | Yes | Required for abuse limits. |
| Drop traffic over limit | Yes | Must be receipted. |
| Terminate TLS/QUIC for consensus payloads | No | Violates ADR-0039. |
| Re-sign validator messages | No | Validator signatures remain end-to-end. |
| Rewrite validator identity or endpoint claims | No | Graph authority remains canonical. |
| Inspect application payloads | No | Relay does not parse consensus payload content. |

For non-consensus slow-path gossip, the same relay may provide pass-through forwarding or rendezvous metadata, but it still must not claim graph authority for the payload. Signed payload verification remains end-to-end.

## 5 - Abuse Limits

Pre-RC relay service is operator-funded and must be conservative.

Required limits:

| Control | Pre-RC rule |
|---|---|
| Active slots per AgentID | Maximum 1 active slot. |
| Concurrent streams per slot | Bounded by relay configuration; suggested default 8. |
| Bytes per epoch per slot | Bounded by relay configuration; suggested default 64 MiB. |
| Admission retries | Bounded; suggested default 5 failed attempts per epoch per AgentID. |
| Slot TTL | Bounded; suggested maximum 4 epochs. |
| Keepalive | Per-epoch only; no high-frequency liveness ping requirement. |
| Revocation | Relay may revoke for malformed proofs, replay, overload, abuse, or operator emergency. |
| Starvation protection | Relay should reserve a minimum slot fraction for first-time Genesis-traced installs. |

Sybil resistance comes from invite provenance, not IP reputation. IP addresses may help rate-limit obvious abuse, but IP identity is weak and must not be treated as protocol identity.

Relay denial-of-service defenses must fail closed:

1. Reject oversized admission requests before parsing nested payloads.
2. Cap concurrent admission handshakes.
3. Use explicit socket timeouts.
4. Avoid unbounded queues.
5. Emit rejection receipts without exposing private invite material.

## 6 - Relay Host Governance

Pre-RC relay hosts are Genesis-controlled operational infrastructure. They may help bootstrap reachability, but they are not governance actors solely because they relay traffic.

Pre-RC relay host requirements:

| Requirement | Rule |
|---|---|
| Operator | Genesis-controlled or explicitly authorized by Genesis for the pre-RC ceremony. |
| Endpoint publication | Relay endpoint must be carried in a signed bootstrap record or later ConnectivityAdvertisement. |
| Logs | Logs must avoid private invite nonce material and payload plaintext. |
| Rotation | Relay endpoint rotation must produce a new signed record and preserve the old record as superseded. |
| Shutdown | Shutdown must revoke active slots and emit revocation receipts when possible. |

Post-RC operator relay markets, relay compensation, relay reputation, and non-Genesis relay admission are deferred. CDL-078 already defines a serve-event to centrality-delta path, but this phase does not activate relay infrastructure rewards or per-hop ECU payments.

## 7 - CDL-112 Relationship

CDL-112 is the proposed governance surface for a future `ConnectivityAdvertisement` schema. Relay/rendezvous depends on CDL-112 for advertisement of granted relay endpoints, candidate endpoint lists, connectivity mode, and probe receipt references.

This spec does not open, amend, prelock, or ratify CDL-112. It defines the relay semantics that CDL-112 should reference when a peer advertises `relay_endpoint`.

Minimum future advertisement fields for relay slots:

| Field | Rule |
|---|---|
| `connectivity_mode` | `relay_reachable`, `validator_observer_relay`, or `validator_relay` only when corresponding authority exists. |
| `relay_endpoint` | Present only after relay slot grant. |
| `relay_slot_ref` | Hash or opaque reference to active slot grant. |
| `relay_mode` | `pass_through_consensus_quic` for consensus-compatible relay. |
| `probe_receipt_ref` | Optional proof that the relay path was tested. |

CDL-103 remains the dynamic peer discovery authority for signed peer advertisements v1. It must not be silently expanded to carry relay semantics under the existing v1 schema.

## 8 - Receipts

Relay implementations must emit deterministic receipts for:

| Receipt | Required fields |
|---|---|
| Admission request | AgentID, admission epoch, invite proof ref, software version, requested port, canonical request hash. |
| Admission result | Slot ID or rejection token, relay endpoint if granted, TTL, limits, canonical response hash. |
| Keepalive | Slot ID, AgentID, epoch, previous grant hash, renewal result. |
| Revocation | Slot ID, AgentID, epoch, reason token, bytes/stream counters. |
| Release | Slot ID, AgentID, epoch, release result. |

All receipt JSON must be deterministic:

```python
json.dumps(receipt, sort_keys=True, separators=(",", ":"), allow_nan=False)
```

No floats are permitted in relay receipts.

## 9 - Non-Claims

| Non-claim | Reason |
|---|---|
| No relay server implementation | Runtime implementation is deferred to GAP-RELAY-RENDEZVOUS-IMPL-00 and deployment to GAP-RELAY-RENDEZVOUS-DEPLOY-00. |
| No relay activation | This phase defines semantics only. |
| No guard clearance | No runtime guard is changed. |
| No CDL mutation | CDL-112 is referenced as proposed future scope only. |
| No CDL-078 reward activation | CDL-078 remains centrality-delta authority for serve events; no production relay rewards are activated here. |
| No DHT | Relay/rendezvous is seed/relay-assisted, not DHT discovery. |
| No UPnP implementation | Router traversal implementation is separate and remains opt-in by policy. |
| No validator admission authority | Relay reachability is not admission, stake, endpoint assertion, liveness, or BFT membership. |
| No public mirror push | Mirror refresh remains a later phase. |
| No public RC activation | This spec is pre-RC planning/runtime substrate only. |

## 10 - Implementation Requirements For Later Phases

Later relay implementation phases must:

1. Keep server-side admission request bodies bounded before JSON parsing.
2. Use explicit socket timeouts for all outbound calls.
3. Avoid wall-clock protocol decisions.
4. Keep relay client guard active until live relay deployment is explicitly authorized.
5. Preserve the pass-through invariant for consensus traffic.
6. Test loopback relay behavior without external network calls.
7. Prove relay endpoint discovery uses signed bootstrap or signed graph records, not hardcoded production peers.
