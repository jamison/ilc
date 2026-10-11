# ADR-0045: ILC Native QUIC Submit Frame Format

**Status:** Accepted
**Date:** 2026-10-04
**Phase:** GAP-NATIVE-QUIC-RECEIVER-FRAME-SPEC-00
**Author:** Jamison and Codex
**Dependencies:** CDL-073, CDL-074, CDL-075, CDL-117, CDL-118, ADR-0025, ADR-0039, `docs/specs/ilc_native_quic_receiver_design_guidance_GAP_NATIVE_QUIC_RECEIVER_v0.1.md`

`native_quic_frame_spec_adr_complete_GAP_NATIVE_QUIC_RECEIVER_FRAME_SPEC_00`

---

## Context

The public submit ingress lane already has constitutional authority and local
runtime semantics:

- CDL-117 ratifies graph-rooted public submit endpoint assertions, TLS
  fingerprint binding, and the unsigned-submission rejection contract.
- CDL-118 ratifies `native_submit_sig_profile.v0.1`: the submitter AgentID is
  the compressed BLS G1 public key, `key_ref == agent_id`, and the BLS G2
  signature is over canonical envelope bytes with the `sig` key excluded.
- CDL-073 defines the outer submission envelope shape used by the Python
  runtime.
- CDL-074 governs truth primitive validation.
- CDL-075 governs canonical graph node records, CIDv1 derivation, and graph
  persistence.

Rev 223 proved that the live VPS environment had no HTTP/3-capable public
submit receiver. Rev 224 rejected Hypercorn/aioquic HTTP/3 as the production
public-submit receiver core and selected a native Rust QUIC receiver instead.
The existing Rust workspace already carries `quinn = "0.11"`, `blst =
"0.3.11"`, and `rustls`.

ADR-0025 remains accepted authority for the D2D gossip HTTP/3-over-QUIC
binding. It does not govern the public submit receiver. Public submit ingress is
a signed graph-ingress operation, not a D2D gossip envelope, and does not need
HTTP request/response semantics or QPACK headers.

## Decision

ILC defines a native public submit transport frame over QUIC streams.

The receiver and client use QUIC/TLS for transport, and carry the existing
CDL-073/CDL-118 JSON envelope unchanged as the frame payload. This ADR defines
only the transport frame. It does not redefine the envelope, the signature
profile, validation, CIDv1 derivation, replay semantics, endpoint assertion
schema, or persistence.

Non-claims are explicit below: this ADR does not authorize HTTP/3 as the public
submit receiver core, does not touch D2D gossip, and does not mutate runtime or
VPS state.

The canonical ALPN string is:

```text
ilc-native-submit-v1
```

The canonical public-RC native submit network ID remains:

```text
ilc-public-rc-01-testnet-harness
```

The canonical CDL-118 BLS DST remains:

```text
ILC_NATIVE_TRUTH_SUBMIT_V1:ilc-public-rc-01-testnet-harness
```

## Request Frame

Each submission is sent on one bidirectional QUIC stream. The client sends
exactly one request frame, then waits for exactly one receipt frame.

```text
[1 byte]  frame_type = 0x01  (NATIVE_SUBMIT_REQUEST)
[4 bytes] payload_length     (big-endian uint32)
[N bytes] payload            (UTF-8 JSON; exact CDL-073 outer envelope)
```

`payload_length` is the number of payload bytes after UTF-8 encoding. The
maximum allowed value is `1,048,576` bytes. A receiver MUST reject larger
payloads before allocating or reading the body.

The payload is the existing outer envelope:

```json
{
  "v": 1,
  "primitive": "assert.truth",
  "agent_id": "<96 lowercase hex compressed BLS G1 public key>",
  "epoch": 0,
  "payload": {},
  "sig": {
    "schema_version": "native_submit_sig.v0.1",
    "verifier_profile": "native_submit_sig_profile.v0.1",
    "dst": "ILC_NATIVE_TRUTH_SUBMIT_V1:ilc-public-rc-01-testnet-harness",
    "payload_sha256": "<64 lowercase hex>",
    "signature_hex": "<192 lowercase hex compressed BLS G2 signature>",
    "key_ref": "<96 lowercase hex; must equal agent_id>"
  }
}
```

The `sig` field is a nested object. It is not a string and not a flat top-level
signature structure.

## Receipt Frame

The receiver responds on the same bidirectional QUIC stream with exactly one
receipt frame:

```text
[1 byte]  frame_type = 0x81  (NATIVE_SUBMIT_RECEIPT_OK)
                  or = 0xFF  (NATIVE_SUBMIT_RECEIPT_REJECT)
[4 bytes] body_length        (big-endian uint32)
[N bytes] body               (UTF-8 JSON)
```

Successful receipt body:

```json
{
  "ok": true,
  "node_id": "<CIDv1>",
  "epoch": 0
}
```

Rejected receipt body:

```json
{
  "ok": false,
  "error": "<machine-readable token>"
}
```

The receiver MUST close the stream after writing the receipt. The connection
may remain open for subsequent streams according to normal QUIC connection
lifecycle behavior.

## Error Tokens

This ADR reserves these transport-layer error tokens:

| Token | Meaning |
|-------|---------|
| `native_submit_unknown_frame_type` | `frame_type` is not `0x01` for a client request |
| `native_submit_payload_too_large` | `payload_length` exceeds `1,048,576` bytes |
| `native_submit_invalid_utf8` | payload or receipt body is not valid UTF-8 |
| `native_submit_incomplete_frame` | stream ended before the declared frame body was read |
| `native_submit_receipt_body_too_large` | receipt body exceeds the implementation's configured receipt cap |

Validation-layer and signature-layer tokens remain governed by CDL-073,
CDL-074, CDL-075, CDL-117, and CDL-118. Implementations MUST preserve those
tokens rather than remapping them to transport-generic errors.

## TLS and Endpoint Binding

QUIC uses TLS 1.3. The receiver MUST present a certificate whose DER SHA-256
fingerprint matches the active graph-rooted public submit endpoint assertion for
the selected `(serving_agent_id, network_id)` pair.

The client MUST verify the server certificate fingerprint against that endpoint
assertion before sending the request payload. Disabling certificate or
fingerprint verification is not permitted in public-RC or production public
submit ingress.

This requirement is the QUIC transport expression of CDL-117's TLS fingerprint
binding. No WebPKI or DNS authority replaces graph-rooted endpoint assertion
authority.

## Relationship To CDL-117

This ADR is subordinate to CDL-117. It does not amend CDL-117.

CDL-117 is transport-neutral. It requires graph-rooted endpoint assertions,
purpose-scoped endpoint signing, TLS DER SHA-256 fingerprint binding, and the
native signed submission envelope. This ADR defines one concrete transport
framing for that already-ratified authority.

## Relationship To CDL-118

This ADR does not change the signing preimage or verifier policy.

The BLS signature is over the canonical JSON bytes of the envelope with the
`sig` key excluded. `payload_sha256` is the SHA-256 commitment and replay
fingerprint for those canonical bytes. A native QUIC implementation MUST pass
the payload bytes to the same semantic verifier used by other native submit
paths, and MUST NOT sign, verify, or hash a different envelope representation.

## Relationship To CDL-075

This ADR does not define graph node IDs.

CIDv1 derivation remains the CDL-075 rule: derive from the canonical node record
produced from a validated submission and validation result. It is not derived
from raw QUIC frame bytes and not derived from raw envelope bytes alone.

## Relationship To ADR-0025 And D2D Gossip

ADR-0025 governs D2D gossip transport. It selects HTTP/3-over-QUIC for the D2D
gossip envelope and permits HTTP/2/TCP fallback for development/test contexts.

This ADR governs public submit ingress only. It intentionally does not use
HTTP/3 request/response framing. The native submit receiver carries a compact
ILC frame over QUIC streams because public submit ingress already has its own
signed envelope, graph endpoint assertion, and receipt semantics.

This ADR does not clear or alter any D2D gossip guard such as
`transport_kind_quic_not_operationalized`.

## Security Requirements

Implementations MUST:

1. Enforce the `1,048,576` byte payload cap before allocating the payload body.
2. Reject unknown request frame types with `native_submit_unknown_frame_type`.
3. Reject invalid UTF-8 with `native_submit_invalid_utf8`.
4. Verify TLS certificate DER SHA-256 fingerprint against the graph endpoint
   assertion before accepting public-RC traffic.
5. Preserve validation and signature error tokens from the semantic verifier.
6. Avoid per-request process spawning in bridge mode; bridge mode must use a
   bounded long-lived local worker boundary.
7. Treat bridge mode as interim only. The production target remains full Rust
   validation and persistence after parity vectors pass.

## Claim Verification Table

| Claim | Source checked | Result |
|-------|----------------|--------|
| Rust QUIC foundation exists | `ilc_consensus/Cargo.toml` | `quinn = "0.11"` present |
| Rust BLS foundation exists | `ilc_consensus/Cargo.toml` | `blst = "0.3.11"` present |
| Rust TLS foundation exists | `ilc_consensus/Cargo.toml` | `rustls` present |
| CDL-117 is transport-neutral and requires TLS fingerprint binding | CDL-117 register row | `tls_binding_required: true`; no HTTP/3 mandate |
| CDL-118 DST is fixed | CDL-118 register row | `ILC_NATIVE_TRUTH_SUBMIT_V1:ilc-public-rc-01-testnet-harness` |
| Envelope shape is canonical | `truth_primitive_submission_runtime.py` | `v`, `primitive`, `agent_id`, `epoch`, `payload`, `sig` |
| `sig` is nested | `d2e_submit_cli.py` | `_build_native_submit_sig_object()` returns nested sig fields |
| D2D gossip QUIC is separate | ADR-0025 and `http_gossip_transport_runtime.py` | ADR-0025 governs D2D; public submit receiver is separate |

## Non-claims

- This ADR does not mutate, open, or ratify any CDL.
- This ADR does not implement the receiver, client, CLI, BLS verifier, CIDv1
  derivation, LMDB persistence, or endpoint assertion writer.
- This ADR does not deploy to VPS and does not bind any public port.
- This ADR does not clear any runtime guard.
- This ADR does not activate public RC, mainnet, settlement, minting, wallet
  mutation, validator admission, or epoch transition.
- This ADR does not govern D2D gossip or replace ADR-0025.
- This ADR does not authorize HTTP/3 as the public submit receiver core.

## Follow-On Phases

1. `GAP-NATIVE-QUIC-RECEIVER-PARITY-VECTORS-00`
2. `GAP-NATIVE-QUIC-RECEIVER-RUST-BRIDGE-AND-CLIENT-00`
3. `GAP-NATIVE-QUIC-RECEIVER-CLI-00`
4. `GAP-NATIVE-QUIC-RECEIVER-BRIDGE-VPS-00`
5. `GAP-PUBLIC-RC-NATIVE-INGRESS-VPS-SMOKE-00`
6. `GAP-NATIVE-QUIC-RECEIVER-RUST-VALIDATION-00`
7. `GAP-NATIVE-QUIC-RECEIVER-RUST-PERSISTENCE-00`
8. `GAP-NATIVE-QUIC-RECEIVER-RUST-SWITCHOVER-00`
