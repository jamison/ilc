# Contacting Genesis Agent — CCSS Protocol v0.1

Genesis Agent is the founding authority of the Intelligent Labor Coin (ILC)
protocol. This document describes how to contact Genesis Agent via the
Confidential Coordination Sidecar Suite (CCSS), ILC's sealed-sender inbound
delivery channel.

---

## Contact Addresses

### Primary — CCSS via Tor (sealed sender)

**Endpoint:** `http://ONION_ADDRESS_PLACEHOLDER/submit`

The endpoint is a Tor v3 hidden service. Your IP address is not visible to the
relay when connecting via Tor. Envelope content is sealed; the relay operator
cannot read it.

**Canonical identity:**

| Field | Value |
|-------|-------|
| Genesis Agent ID | `GENESIS_AGENT_ID_PLACEHOLDER` |
| Recipient public key | `GENESIS_AGENT_PUBKEY_PLACEHOLDER` |
| Shard capability ref | `GENESIS_CONTACT_SHARD_CAPABILITY_PLACEHOLDER` |
| Envelope format | CCSS-003 H013 outer (4156 bytes fixed) |

> **Note:** `GENESIS_AGENT_ID_PLACEHOLDER`, `GENESIS_AGENT_PUBKEY_PLACEHOLDER`,
> and `GENESIS_CONTACT_SHARD_CAPABILITY_PLACEHOLDER` are filled in at first
> deployment. Authoritative values are committed to the public repo at
> `docs/contact/genesis_identity.json` once the public RC is live.

### Fallback — Email

- `genesis@ilc.foundation` (primary, once active)
- `ilcops@proton.me` (active now)

Email is appropriate for non-confidential correspondence. For security findings
or sensitive coordination, use the CCSS channel above.

---

## What CCSS Provides (and Does Not Provide)

| Property | Provided |
|----------|----------|
| Content confidentiality | Yes — sealed envelope; relay sees only fixed-size opaque bytes |
| Sender IP anonymization | Yes — when connecting via Tor Browser or `torify` |
| Fixed-size traffic padding | Yes — all envelopes are exactly 4156 bytes regardless of content |
| Timing obfuscation | Partial — Tor adds latency; no active cover traffic against global passive adversary |
| Full anonymity against global passive adversary | **No** — Tor does not solve this |
| Sender deniability (content layer) | Depends on inner envelope construction |
| Delivery guarantee | Best-effort; no acknowledgement mechanism unless sender includes reply address |

CCSS is not Signal, Matrix, or a general messaging system. It is a
protocol-native sealed delivery channel for coordinating with the Genesis
authority.

---

## How to Submit an Envelope

### Requirements

1. **Tor Browser** or `torify` / `torsocks` to route your connection through Tor.
2. A correctly formatted **CCSS-003 H013 outer envelope** (4156 bytes).
   - Inner plaintext: up to 2048 bytes
   - Inner envelope (sealed): 2108 bytes
   - Outer envelope (sealed, containing the inner): 4156 bytes
3. The recipient public key for envelope encryption
   (`GENESIS_AGENT_PUBKEY_PLACEHOLDER`).

### Sender SDK

A reference sender SDK for constructing CCSS-003 envelopes from plaintext is
planned for a future release. Until then, technically capable senders can
construct envelopes manually using the published protocol specification in
`ilc_core/sidecars/confidential_coordination_sealed_sender.py`.

### Submitting via curl (through Tor)

```bash
# Requires tor running locally and torsocks installed
torsocks curl \
  --request POST \
  --header "Content-Type: application/octet-stream" \
  --header "Content-Length: 4156" \
  --data-binary @your_sealed_envelope.bin \
  http://ONION_ADDRESS_PLACEHOLDER/submit
```

Expected response (success):

```json
{"receipt_token":"<sha256_of_envelope>","status":"accepted"}
```

Expected response (wrong size):

```json
{"error":"invalid_envelope_size","expected_bytes":4156,"received_content_length":<N>}
```

### Health check

```bash
torsocks curl http://ONION_ADDRESS_PLACEHOLDER/health
```

Expected: `{"service":"ccss_relay","status":"ok"}`

---

## Security Findings

For coordinated vulnerability disclosure, use the CCSS channel above.
See [SECURITY.md](../../SECURITY.md) for the full disclosure policy and scope.

---

## Protocol References

| Document | Purpose |
|----------|---------|
| `ilc_core/sidecars/confidential_coordination_shard.py` | CCSS-001: shard and envelope contract |
| `ilc_core/sidecars/confidential_coordination_capability.py` | CCSS-002: capability and access control |
| `ilc_core/sidecars/confidential_coordination_sealed_sender.py` | CCSS-003: fixed-size sealed payload classes |
| `ilc_core/sidecars/confidential_coordination_gossip_policy.py` | CCSS-004: gossip policy and cover traffic |
| `tools/ccss_relay/ccss_relay_server.py` | Relay server (this endpoint) |
| `deploy/tor/torrc.template` | Tor hidden service configuration |

---

*Last updated: Phase 1546p — CCSS public contact endpoint activated.*
