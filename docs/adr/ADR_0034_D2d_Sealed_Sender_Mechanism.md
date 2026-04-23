# ADR-0034: D2d Sealed-Sender Mechanism

**Status:** Accepted
**Date:** 2026-04-23
**Window:** 791-800

`run_h013_d2d_sealed_sender_adr_verdict=accepted`

---

## 1. Context

H-013 requires sealed spectral beacon emission over the D2d layer.  A
`SpectralBeacon` carries privacy-noised local spectral coordinates.  If the
transport path exposes the originating peer or agent identity to relay nodes,
then the beacon becomes a topology-fingerprinting surface rather than a
privacy-preserving routing hint.

Current D2d surfaces already enforce several boundaries:

- `ilc_core/network/d2d/gossip.py` rejects `creator_agent_id` in transport headers.
- `build_transport_envelope()` emits `sender_peer_id`, `channel_id`,
  `payload_cid`, and normalized transport headers.
- `build_observer_metadata_trace()` exposes only relay peer id, channel tag, and
  epoch slot to a passive observer.
- `ilc_core/network/d2d/spectral_beacon.py` is a stub and is not transmitted.

The gap is sealed sender: the existing envelope can hide creator-agent metadata
from headers, but it does not define how a spectral beacon payload is sealed so
relay nodes cannot read or link the originator.

---

## 2. Mechanism Decision

Three mechanism families were evaluated.

| Option | Summary | Decision |
|---|---|---|
| Option A: one-hop relay concealment | Submitter sends to a relay and the relay forwards an opaque payload. | Rejected as insufficient alone. The first relay still observes the immediate network sender unless additional sealing and relay-origin separation are defined. |
| Option B: fixed-size Sphinx-style onion envelope | Sender builds a fixed-size layered encrypted envelope. Each relay peels only its layer and learns only the next hop plus opaque payload. | **Accepted** for H-013 design. It provides sender concealment from relay nodes and keeps payload size uniform. |
| Option C: SURB reply block | Sender supplies single-use reply blocks for anonymous return traffic. | Deferred. Useful for replies, but H-013 spectral beacon emission is one-way and does not need an anonymous return channel. |

Decision: ADR-0034 accepts **Option B: fixed-size Sphinx-style sealed envelope**
for the spectral beacon path.

The accepted form for testnet scope is a bounded one-relay Sphinx-style envelope:

1. Sender chooses a relay selected by the H-015 routing layer.
2. Sender creates a fixed-size sealed payload containing the noised spectral
   beacon and terminal delivery instruction.
3. Relay peels one layer, learns only the next-hop delivery instruction, and
   forwards the sealed inner payload.
4. Relay never receives `creator_agent_id` or unsealed spectral content.

This ADR does not choose concrete cryptographic libraries.  H-013 implementation
must choose authenticated public-key encryption primitives in a later phase.

---

## 3. CDL-060 Compatibility Surface

CDL-060 ratified bounded centrality gossip with opaque channel and single-hop
scope.  The accepted sealed-sender mechanism must not convert D2d gossip into
unbounded multi-hop dissemination.

Compatibility resolution:

- H-013 may use one bounded relay leg plus one terminal delivery leg for a sealed
  spectral beacon.
- H-013 may not recursively re-gossip the beacon.
- The relay selection fanout remains bounded by the existing D2d peer registry
  ceiling.
- A relay cannot expand the recipient set beyond the sender-selected terminal
  instruction.

This is not a CDL-060 amendment because it does not alter fanout, channel
opacity, or centrality gossip semantics.  It defines the payload-sealing method
for the separate spectral beacon path.

---

## 4. CDL-061 Compatibility Surface

CDL-061 ratified the HTTP/3 CBOR outer envelope contract.  ADR-0034 places the
sealed sender layer **inside** that envelope.

Outer envelope fields remain unchanged:

- `message_id`
- `payload_cid`
- `channel_id`
- `sender_peer_id`
- `transport_headers`

The sealed spectral beacon is addressed as an opaque payload object referenced
by `payload_cid`.  The outer envelope continues to carry only the relay peer id
visible for the current hop.  It must not add `creator_agent_id`,
`source_agent_id`, raw spectral coordinates, cluster membership, or route
history to transport headers.

---

## 5. H-015 Wiring Boundary

H-015 and H-013 are adjacent but separate.

H-015 owns:

- choosing a next-hop relay candidate from known peers
- scoring peers using `spectral_distance()` against target spectral coordinates
- applying the greedy-descent plus random-walk fallback routing policy
- returning a next-hop or bounded failure result

H-013 owns:

- constructing the fixed-size Sphinx-style sealed payload
- hiding the sender from relay nodes
- ensuring the relay sees only the next-hop instruction and opaque ciphertext
- preserving CDL-061 outer-envelope compatibility

H-015 must not inspect sealed payload internals.  H-013 must not make routing
decisions from raw graph topology.  The interface between them is:

`selected_relay_peer_id + sealed_payload_cid + opaque_channel_id`

---

## 6. Decision Verdict

`run_h013_d2d_sealed_sender_adr_verdict=accepted`

ADR-0034 is accepted as the prerequisite ADR for later H-013 implementation.
It clears the design boundary needed for H-015 initial routing work, but it does
not itself implement sealed sender.

---

## 7. Non-Authorizations

This ADR does not authorize:

- implementation of H-013 sealed beacon emission
- mutation, opening, or prelocking of any CDL row
- amendment of CDL-060 or CDL-061
- publication of patent-sensitive spectral-routing material
- unbounded multi-hop gossip
- exposure of `creator_agent_id` or raw spectral coordinates in D2d headers
- activation of Tier 3
