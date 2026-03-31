# ILC CDL-061 Gossip HTTP Envelope Prelock v0.1

## 1. CDL-061 scope and purpose

CDL-061 governs the ILC gossip HTTP envelope contract for D2d gossip transport.
This lane locks the header field set, CDL-039 required exclusions, CDL-060
hop-count enforcement, HTTP status code semantics, payload encoding, and the
CDL-024 canonical transport-kind representation.

## 2. Candidate forms

- `http3_envelope_cbor`
- `http2_fallback_envelope_cbor`

HTTP/3 over QUIC is the production binding. HTTP/2 over TLS/TCP remains the
fallback binding for development and restricted environments.

## 3. Invariants to lock at ratification

- The gossip envelope remains an envelope-contract lane only.
- Header-layer privacy exclusions remain mandatory under CDL-039.
- `ILC-Hop-Count: 1` remains the only ratified hop-count value under CDL-060.
- HTTP status semantics remain limited to the six locked codes in Section 7.
- CBOR remains the required production payload encoding.
- CDL-024 kind mapping remains `kind=quic` for HTTP/3 production and
  `kind=http` for HTTP/2 fallback.

## 4. Required header field set

The request URL is `POST /ilc/gossip/{message_type}`.

```text
ILC-Gossip-Type:   {message_type}
ILC-Channel:       <opaque-value>
ILC-Epoch:         <validation_epoch_number>
ILC-Hop-Count:     <hop_depth>
ILC-Signature:     <base64-encoded signed envelope>
Content-Type:      application/cbor
```

## 5. CDL-039 required exclusions

1. `creator_agent_id` MUST NOT appear in any ILC gossip header.
2. `node_id` of the originating node MUST NOT appear in transport headers.
3. `ILC-Channel` value MUST be opaque: no semantically interpretable content
   that would allow cluster membership inference.

These exclusions are enforced at the envelope layer, not left to runtime discretion.

## 6. CDL-060 hop-count enforcement

- Single-hop lane: `ILC-Hop-Count: 1` is the only permitted value under the
  ratified CDL-060 scope.
- Requests with `ILC-Hop-Count` absent or `> 1` are rejected with `400 Bad Request`.

## 7. HTTP status code semantics

| Status | Gossip protocol meaning |
|---|---|
| `202 Accepted` | Delta buffered in epoch accumulation buffer |
| `204 No Content` | Delta suppressed (below `U_FLOOR`); not an error; no retry needed |
| `400 Bad Request` | Envelope malformed or CDL-039/CDL-060 violation detected |
| `409 Conflict` | Delta for an already-committed epoch; too late for this epoch |
| `429 Too Many Requests` | Fanout bound exceeded; sender must not retry this peer this epoch |
| `503 Service Unavailable` | Node mid-epoch crash recovery; buffer lost; sender may re-gossip |

## 8. Payload encoding

CBOR (`application/cbor`) is the required payload encoding for all ILC gossip messages.
JSON (`application/json`) is permitted as a debug/development fallback but MUST NOT be
used in production nodes.

## 9. CDL-024 kind canonical representation

| Binding | CDL-024 `kind` | Rationale |
|---|---|---|
| HTTP/3 over QUIC (production) | `kind=quic` | CDL-024 governs the wire layer; HTTP/3 IS QUIC |
| HTTP/2 over TLS/TCP (fallback) | `kind=http` | HTTP/2 over TCP; no QUIC |

## 10. Prelock governance tokens

- `cdl_061_gossip_http_envelope_prelock`
- `cdl_061_ratification_deferred_to_phase_561`
- `gossip_http_envelope_invariants_locked_at_prelock`
- `cdl_039_exclusions_enforced_at_header_layer`
