# CCSS D2d Transport Specification v0.1

**Status:** Pre-canon — describes the Option C destination.  
**Depends on:** D2d gossip layer (phases 380–382), CDL-094 TransportPrincipal  
**Does not change:** CCSS-003 envelope format (remains 4156 bytes, X25519 + ChaCha20-Poly1305)

---

## 1. Problem

The Tor transport (`TorTransport`) requires each agent to run a persistent hidden
service and exposes a separate addressing namespace (onion addresses) alongside
the ILC agent identity namespace (agent_id).  This creates two parallel routing
stacks doing the same job.

The direct TCP transport (`DirectTransport`) removes Tor but still requires
fixed IP reachability — impractical for ephemeral or mobile agents.

## 2. Option C: D2d as CCSS transport

The ILC D2d peer network (phases 380–382) already provides:

- Content-addressed agent identity (`agent_id` — CDL-042)
- Peer discovery and routing via the gossip layer
- Opaque blob propagation (gossip messages are already typed payloads)
- Store-and-forward semantics through gossip propagation

Adding CCSS as a D2d message type makes the ILC peer network the transport.
No per-agent Tor hidden service is required.  Agents are reachable by
`agent_id` alone.

## 3. Wire model

```
Sender                    D2d gossip network              Recipient
  │                              │                              │
  │── CCSS_ENVELOPE msg ────────►│                              │
  │   {type, recipient_id,       │── route by recipient_id ───►│
  │    envelope: 4156 bytes}     │                              │
  │                              │                        write to inbox
  │◄── CCSS_RECEIPT msg ─────────┤◄── receipt ──────────────────│
```

The envelope is already opaque and E2E encrypted.  Routing peers see only
`recipient_id` (the agent_id) and the fixed-size blob.  They cannot read
the message content.

## 4. D2d message types (to be registered)

### `CCSS_ENVELOPE`
Sender → network → recipient.

```json
{
  "type": "CCSS_ENVELOPE",
  "version": "ccss-003-v1",
  "recipient_id": "<agent_id hex>",
  "envelope": "<base64-encoded 4156 bytes>"
}
```

### `CCSS_RECEIPT`
Recipient → sender (best-effort, not guaranteed).

```json
{
  "type": "CCSS_RECEIPT",
  "receipt_token": "<sha256 of envelope hex>",
  "status": "accepted"
}
```

## 5. Recipient pubkey registration

Agents declare their CCSS receive pubkey at INIT time alongside their agent_id.
The pubkey is the same X25519 key used in CCSS-003 envelope encryption.

Proposed INIT record field:

```json
{
  "ccss_recipient_pubkey": "<32-byte X25519 pubkey hex>"
}
```

This allows any peer that knows an agent's `agent_id` to look up their CCSS
pubkey from the graph and send them a message without any out-of-band
configuration.

## 6. Transport priority (already implemented in ccss_transport.py)

```
1. DirectTransport   ccss_peer_endpoint host:port   fastest; direct IP
2. TorTransport      ccss_contact_onion .onion       anonymous; no direct IP needed
3. D2dTransport      agent_id                        ILC-native; this spec
```

Priority 1 and 2 are live.  Priority 3 activates when:
- D2d gossip layer has live peered agents
- `CCSS_ENVELOPE` message type is registered in the D2d schema
- Agents publish `ccss_recipient_pubkey` in INIT records

## 7. Privacy properties

| Property | TorTransport | DirectTransport | D2dTransport |
|---|---|---|---|
| Content confidentiality | ✓ E2E encrypted | ✓ E2E encrypted | ✓ E2E encrypted |
| Sender IP hidden from recipient | ✓ Tor circuit | ✗ Direct TCP | ✓ Gossip routing |
| Sender IP hidden from network | ✓ Tor circuit | ✗ Direct TCP | Partial (CDL-094) |
| No central infrastructure | ✓ Per-agent HS | ✓ Direct | ✓ Peer network |
| Works while agent offline | ✗ | ✗ | ✓ Gossip store-and-forward |

CDL-094 TransportPrincipal governs the network-layer privacy properties of D2d
transport.  Full sender anonymity in Option C depends on CDL-094 ratification.

## 8. What does NOT change

- CCSS-003 envelope format: 4156 bytes, X25519 ECDH + ChaCha20-Poly1305, HKDF-SHA256
- Inner/outer envelope structure and padding
- Inbox storage format (`.envelope` files, SHA-256 receipt tokens)
- `ccss_cli.py` / `ccss_chat_ui.py` call surface — `resolve_transport()` adds D2d
  transparently when the contact has a live `agent_id` and D2d is live

## 9. Implementation gate

`D2dTransport.send()` in `tools/ccss_send/ccss_transport.py` raises
`NotImplementedError` until this spec is implemented.  The gate condition:

```
D2D_CCSS_TRANSPORT_LIVE = "ccss_d2d_transport_<phase>.v0.1"
```

This token must be emitted by the phase that:
1. Registers `CCSS_ENVELOPE` / `CCSS_RECEIPT` in the D2d message type registry
2. Implements gossip routing for CCSS envelopes in `ilc_core/network/`
3. Adds `ccss_recipient_pubkey` to the INIT record schema (CDL work)
4. Updates `D2dTransport.send()` to call the D2d gossip send path

Until that token exists, `ccss_transport.resolve_transport()` skips D2d and
falls through to Tor or Direct.
