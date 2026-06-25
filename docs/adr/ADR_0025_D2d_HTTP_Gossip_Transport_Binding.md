# ADR-0025: D2d HTTP/3 Gossip Transport Binding

**Status:** Accepted
**Date:** 2026-03-31
**Accepted:** 2026-03-31 (post-Phase 547 architectural review; Codex review confirmed architecture sound; ADR-0011 confirmed as the accepted baseline during the same review)
**Context:** Window 555-564 transport binding design; Post-Phase 547 architectural review
**Supersedes:** Nothing (extends CDL-024 and ADR-0011 for the gossip sub-layer)
**See also:** ADR-0011 (Native P2P Transport Baseline), CDL-024 (wire transport), CDL-039 (topology privacy), CDL-060 (gossip centrality extension), `docs/research/ilc_http_gossip_transport_x402_context_v0.1.md`

---

## Context

The D2d gossip layer (`ilc_core/network/d2d/`) currently operates in-process only using `InProcessGossipBus`. Window 555-564 is the first window to bind this layer to real network transport across machine boundaries.

CDL-024 permits three wire transport kinds: `http`, `libp2p`, `quic`. The question for Window 555-564 is which of these to use as the D2d gossip transport binding, and what protocol envelope to place on top.

Two design pressures exist in tension:

1. **ADR-0011** (Native P2P Transport Baseline) mandates QUIC-based encrypted streams as the primary network transport and states that "HTTP request/response payment flows and centralized brokers are not suitable as core transport for hot-path graph operations."

2. **Operational simplicity**: a custom binary protocol over raw TCP or libp2p adds implementation complexity, debuggability cost, and infrastructure friction that is disproportionate to the requirements of a bounded-fanout gossip layer operating at 1-minute validation epoch cadence.

The resolution is that these two pressures are not in conflict: **HTTP/3 runs over QUIC**. HTTP/3 is QUIC encrypted streams at the transport layer with HTTP/3 framing on top. Adopting HTTP/3 satisfies ADR-0011's QUIC requirement while enabling the lightweight, infrastructure-compatible HTTP envelope design described below.

---

## Decision

Adopt **HTTP/3 over QUIC** as the D2d gossip transport binding for Window 555-564, with **HTTP/2 over TLS/TCP** as a permitted development and test-environment fallback.

### Gossip envelope design

D2d gossip messages are transmitted as HTTP POST requests with a standard envelope:

```
POST /ilc/gossip/{message_type}  HTTP/3
ILC-Gossip-Type:  {centrality_delta | ...}
ILC-Channel:      <opaque-value>
ILC-Epoch:        <validation_epoch_number>
ILC-Hop-Count:    1  (fixed by CDL-060; future multi-hop requires a new CDL lane)
ILC-Signature:    <base64-encoded signed envelope>
Content-Type:     application/cbor

<CBOR-encoded payload>
```

**CDL-039 required field exclusions** (enforced at the envelope layer, not left to runtime discretion):
- `creator_agent_id` MUST NOT appear in any ILC gossip header
- `node_id` of the originating node MUST NOT appear in transport headers
- `ILC-Channel` value MUST be opaque (no semantically interpretable content that would allow cluster membership inference)

**CDL-060 enforcement** via `ILC-Hop-Count`:
- Single-hop lane: `ILC-Hop-Count: 1` is the only permitted value under the ratified CDL-060 scope
- Requests with `ILC-Hop-Count` absent or `> 1` are rejected with `400 Bad Request`

### TLS verification requirement (Fix81 amendment)

Production and public-RC D2d deployments MUST verify peer TLS certificates.
Development and private testbed runtimes MAY expose an explicit local escape
hatch for self-signed certificates, but that escape hatch MUST be inoperative
when public mode is enabled.

The canonical public-mode guard is:

- `ILC_D2D_PUBLIC_MODE=1` unconditionally requires TLS verification.
- `ILC_D2D_INSECURE_SKIP_TLS_VERIFY=1` is permitted only for local dev/test
  contexts and MUST NOT disable verification when `ILC_D2D_PUBLIC_MODE=1`.
- `verify=False`, `ssl=False`, `check_hostname=False`, `ssl.CERT_NONE`, or
  equivalent bypasses are forbidden in public or production D2d paths.
- Certificate trust failures must be fixed by configuring the CA bundle or
  certificate store, not by disabling TLS verification.

### HTTP status code semantics

The gossip receiver communicates protocol state using standard HTTP status codes:

| Status | Gossip protocol meaning |
|---|---|
| `202 Accepted` | Delta buffered in epoch accumulation buffer |
| `204 No Content` | Delta suppressed (below `U_FLOOR`); not an error; no retry needed |
| `400 Bad Request` | Envelope malformed or CDL-039/CDL-060 violation detected |
| `409 Conflict` | Delta for an already-committed epoch; too late for this epoch |
| `429 Too Many Requests` | Fanout bound exceeded; sender must not retry this peer this epoch |
| `503 Service Unavailable` | Node mid-epoch crash recovery; buffer lost; sender may re-gossip |

No custom status codes. Standard HTTP monitoring and alerting tooling understands all of these.

### Peer discovery (v1)

Static configuration: each node is provisioned with a list of peer HTTPS endpoints at startup. No DHT or dynamic peer discovery in v1. This is sufficient for the three-machine / seven-agent test milestone and defers dynamic peer discovery to a future CDL track.

### Payload encoding

CBOR (`application/cbor`) is the required payload encoding for all ILC gossip messages. JSON (`application/json`) is permitted as a debug/development fallback but MUST NOT be used in production nodes.

---

## Relationship to ADR-0011

ADR-0011 states: "HTTP request/response payment flows and centralized brokers are not suitable as core transport for hot-path graph operations."

This ADR does not contradict ADR-0011:

1. The gossip layer is not a "hot-path graph operation." It operates at 1-minute validation epoch cadence with bounded fanout=3. Latency requirements are on the order of seconds, not milliseconds.
2. The concern about "centralized brokers" does not apply to direct peer-to-peer HTTP/3 POST requests between ILC nodes. No broker is introduced.
3. The concern about "HTTP request/response payment flows" applies to the x402 / external payment integration question (a separate track), not to gossip message transport.
4. HTTP/3 IS QUIC. HTTP/3 uses QUIC encrypted streams at the transport layer. ADR-0011's "QUIC-based encrypted streams" requirement is satisfied by HTTP/3.

If the gossip layer were required to operate at sub-second hot-path latency, raw QUIC streams without HTTP framing would be the right choice. At validation-epoch cadence, HTTP/3 framing overhead is negligible and the operational benefits dominate.

---

## CDL-024 transport-kind canonical representation

CDL-024 lists allowed kinds as `("http", "libp2p", "quic")`. HTTP/3 spans both `http` and `quic`. The canonical representation for each binding is:

| Binding | CDL-024 `kind` | Rationale |
|---|---|---|
| HTTP/3 over QUIC (production) | `kind=quic` | CDL-024 governs the wire transport layer; at the wire level, HTTP/3 IS QUIC encrypted streams |
| HTTP/2 over TLS/TCP (fallback) | `kind=http` | HTTP/2 over TCP is the classical `http` transport; no QUIC involved |

This means `kind=http` under CDL-024 refers to HTTP/1.1 or HTTP/2 over TCP, and `kind=quic` covers HTTP/3. Both are already authorized. No CDL amendment is required; this classification note is the definitive interpretation for Window 555-564 implementation.

---

## Consequences

**Positive:**
- `kind=quic` is already in CDL-024's allowed transport kinds; no CDL amendment required for the wire transport spec
- HTTP/3 satisfies ADR-0011's (Accepted) QUIC requirement
- HTTPS/QUIC encryption satisfies CDL-039's channel opacity requirement without additional machinery
- Standard infrastructure (Cloudflare, AWS, load balancers, monitoring stacks) understands the transport natively
- HTTP status codes provide a clean, zero-custom-code protocol state signaling layer
- HTTP/2 fallback is available for test environments where UDP/QUIC may be blocked
- The gossip envelope header design is identical across HTTP/2 and HTTP/3; migration is a transport-layer swap

**Costs:**
- HTTP/3 requires UDP port 443 to be open; some test environments may require HTTP/2 fallback
- CBOR encoding requires a CBOR library dependency (minor)
- A new CDL is required to constitutionally lock the gossip HTTP envelope contract (header field set, CDL-039 exclusions, status code semantics)

**Non-goals:**
- This ADR does not cover x402 external payment integration (separate ADR/CDL track)
- This ADR does not cover dynamic peer discovery (deferred to a future CDL)
- This ADR does not govern the content dissemination layer (CDL-036 pull-fetch remains unchanged)
- This ADR does not authorize multi-hop gossip (CDL-060 ratified single-hop lane is unchanged)

---

## Follow-on status

### Completed follow-ons

1. **ADR status closure**: ADR-0025 is Accepted and ADR-0011 is Accepted concurrently.
2. **Phase 555 sequence lock**: Window 555-564 referenced ADR-0025 and locked `kind=quic` (HTTP/3) as the production transport binding with `kind=http` (HTTP/2) as the fallback.
3. **CDL-061 governance lane**: Phase 557 opened CDL-061, Phase 561 ratified it, and the decision log now records the gossip HTTP envelope contract as ratified canon.
4. **Transport envelope runtime**: Phase 558 implemented `ilc_core/network/d2d/gossip_transport.py`, Phase 559 hardened the adapter surface, and Phase 560 extended the mutation canary to protect the transport constants and forbidden-header invariants.
5. **Pause A carry-forwards**: The Phase 548 gossip runtime now documents the one-epoch attribution lag and logs zeroed epoch buffers on crash recovery.
6. **Static peer registry v1**: Phase 562 added `ilc_core/network/d2d/gossip_peer_registry.py` with static-v1 scope and no DHT or dynamic discovery.

### Remaining follow-ons

1. **Window 565-574 transport operationalization**: Wrap the ratified envelope contract in actual multi-machine HTTP/3 or HTTP/2 client/server I/O, including deployment packaging and observability.
2. **Static peer configuration**: Define the file or environment format that initializes `GossipPeerRegistry`, including normalization, deduplication, and operator-facing validation guidance.
3. **HTTP/2 fallback activation path**: Document and test the environments where UDP or QUIC is blocked, and define how nodes intentionally downgrade to the permitted HTTP/2 fallback.
4. **Production JSON policy**: Keep `application/json` as debug-only and add an explicit production-mode enforcement path when the operational runtime is introduced.
5. **Window 575-584 agent behavioral loop**: Add x402 as an MCP skill candidate for outbound agent payments to external services. This remains an ADR-level decision, not a gossip-transport governance action.
6. **Window 595+ planning**: Treat inbound x402 task submission as a separate treasury-governed lane requiring stablecoin-to-ECU conversion rules under CDL-047. Do not merge it into the gossip transport stack.
