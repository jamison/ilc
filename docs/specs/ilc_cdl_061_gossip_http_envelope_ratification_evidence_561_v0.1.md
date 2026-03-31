# ILC CDL-061 Gossip HTTP Envelope Ratification Evidence v0.1

## 1. CDL-061 ratification summary

CDL-061 is ready for ratification as the ILC gossip HTTP envelope contract.
The prelock surface from Phase 557 was implemented directly in
`ilc_core/network/d2d/gossip_transport.py` during Phases 558-560, with
boundary hardening and canary coverage added before ratification.

## 2. Candidate form selected

Selected: `http3_envelope_cbor` with `http2_fallback_envelope_cbor` as the
permitted fallback (per ADR-0025). The gossip envelope header design is
identical across HTTP/2 and HTTP/3; migration between transports is a
transport-layer swap only.

## 3. Implementation evidence

- `ilc_core/network/d2d/gossip_transport.py` implements `build_gossip_headers`
  and `validate_gossip_headers` per the prelock header field set.
- `GOSSIP_TRANSPORT_RUNTIME_VERSION = "gossip_transport_runtime_558.v0.1"`
- `CDL_061_DEPENDENCY = "cdl_061_ratified_561.v0.1"` (updated from prelock at ratification)
- Phase 558: 12 tests passing
- Phase 559: 8 tests passing (boundary hardening)
- Phase 560: 6 tests passing (canary coverage confirmed, 7 probes all killed)

## 4. CDL-039 enforcement evidence

- `FORBIDDEN_HEADER_KEYS` locks the four disallowed header keys.
- `validate_gossip_headers()` rejects forbidden keys at the envelope layer,
  not by downstream runtime discretion.
- `ILC-Channel` opacity is validated through the existing CDL-039 channel
  validation path and normalized to the ratified transport token on failure.

## 5. CDL-060 hop-count enforcement evidence

- `build_gossip_headers()` rejects any `hop_count` other than `1`.
- `validate_gossip_headers()` rejects missing `ILC-Hop-Count` and any value
  other than `1`.
- This preserves the ratified single-hop boundary from CDL-060.

## 6. Status code semantics evidence

The transport module publishes named constants for all ratified envelope
semantics:

- `HTTP_STATUS_BUFFERED = 202`
- `HTTP_STATUS_SUPPRESSED = 204`
- `HTTP_STATUS_ENVELOPE_ERROR = 400`
- `HTTP_STATUS_EPOCH_CONFLICT = 409`
- `HTTP_STATUS_FANOUT_EXCEEDED = 429`
- `HTTP_STATUS_CRASH_RECOVERY = 503`

## 7. Ratification readiness evidence checklist satisfaction

- header field set implemented and tested
- CDL-039 exclusions enforced at envelope layer (not runtime discretion)
- CDL-060 hop-count header enforcement (`ILC-Hop-Count: 1` only)
- HTTP status code semantics table implemented as named constants
- CBOR required encoding; JSON debug-fallback permitted

`cdl_061_ratification_evidence_complete`
