# ILC CCSS Metadata Leakage Audit 1573p v0.1

**Phase:** 1573p
**Window:** 1565-1575
**Date:** 2026-07-09
**Status:** committed
**Sensitivity:** NON-SENSITIVE

## 1. Purpose

This audit traces the actual CCSS/SPECTRAL relay-visible wire and log surfaces
after Phase 1573o. It verifies the narrow public-RC claim boundary: relay
surfaces must not expose raw or noisy spectral coordinates, sigma values, agent
identity fields, raw capability identifiers, recipient public keys, or
commitment salts.

This is not an anonymity proof, formal differential privacy proof, full
unlinkability proof, Signal-equivalent sealed-sender claim, or public transport
activation.

## 2. Sources Read

| Source | Purpose |
| --- | --- |
| `docs/specs/ilc_ccss_public_rc_privacy_claim_boundary_1573o_v0.1.md` | Claim boundary being tested |
| `ilc_core/network/d2d/spectral_route_token.py` | SpectralRouteToken primitive and forbidden field validator |
| `ilc_core/network/d2d/spectral_beacon.py` | H-013 and CCSS-SPECTRAL envelope builders |
| `ilc_core/network/d2d/http_gossip_transport_runtime.py` | HTTP receive path and event log surface |
| `ilc_core/network/d2d/gossip.py` | Generic D2D transport envelope surface |
| `tests/test_phase_1573g_ccss_spectral_01_beacon_emission.py` | Prior beacon-emission guard tests |
| `tests/test_phase_1573h_ccss_spectral_01_full_test_suite.py` | Prior route-token authentication and SIM tests |

## 3. Relay-Visible Field Inventory

### 3.1 SpectralRouteToken Envelope

`build_spectral_route_token_envelope()` is still guarded by
`CCSS_SPECTRAL_01_NOT_ACTIVATED`. When enabled under test-only monkeypatching,
the returned relay-visible fields are:

| Field | Relay-visible meaning |
| --- | --- |
| `ccss_spectral_version` | Envelope version |
| `epoch` | Epoch integer |
| `route_token` | Opaque HKDF-derived route token |
| `sender_ephemeral_pubkey` | Sender X25519 ephemeral public key component of the hybrid KEM ciphertext |
| `kem_ciphertext` | Hybrid X25519 + ML-KEM-768 ciphertext |
| `message_nonce` | Message nonce |
| `route_purpose` | Coarse enum: `bootstrap`, `direct-message`, `query`, or `relay` |
| `hiding_commitment` | One-way commitment over quantized lambda and salt |
| `capability_context_commitment` | One-way epoch/capability context commitment |

The function uses `lambda_local`, `raw_cap_id`, `recipient_pk_bytes`, and
`commitment_salt` internally, but none of those names or values are emitted as
relay-visible fields.

### 3.2 Relay Validator

`validate_relay_envelope()` delegates to
`spectral_route_token.validate_no_forbidden_fields()` and is intentionally
guard-independent. It recursively rejects:

`lambda_local`, `lambda_vector`, `eigenvalue`, `eigenvalues`,
`spectral_fingerprint`, `noise_sigma`, `sigma`, `agent_id`,
`sender_agent_id`, `recipient_agent_id`, `recipient_public_key`,
`raw_contact_capability_id`, and `commitment_salt`.

### 3.3 H-013 Wrapper

`build_h013_gossip_envelope()` wraps sealed beacon metadata in the generic D2D
transport envelope. It calls `_check_no_lambda_in_envelope()` before return.
Custom H-013 transport headers are sanitized by
`_sanitize_h013_transport_headers()`, which rejects aliases for:

`agent_id`, `creator_agent_id`, `h013_emission_id`, `source_agent_id`,
`sender_peer_id`, `schema_ref`, `origin_peer_id`, `lambda_local`,
`noise_sigma`, `raw_spectral_coordinates`, `route_history`,
`cluster_membership`, `cluster_members`, and `topic`.

The wrapper still carries D2D transport metadata: `message_id`, `payload_cid`,
`channel_id`, `sender_peer_id`, and sanitized `transport_headers`.
`sender_peer_id` is a peer transport identifier, not a spectral coordinate or
agent-init identity claim.

### 3.4 HTTP Gossip Transport Logs

`HttpGossipTransportRuntime._record()` writes local in-memory event-log entries.
The audited receive path records status tokens, path, payload byte count,
payload hash, signature hash, and, for signature/key failures, peer/key/epoch
metadata. It does not log lambda values, sigma values, route tokens, raw
capability IDs, recipient public keys, KEM internals, commitment salts, or
sealed payload plaintext.

Residual metadata remains visible to a relay or network observer: IP-layer
connection metadata, path, content length, timing, channel/gossip headers,
coarse route purpose where present, peer IDs used for transport verification,
key IDs, and failure tokens. These are outside the narrow Phase 1573o
non-disclosure claim.

## 4. Test Coverage Added

`tests/test_phase_1573p_ccss_metadata_leakage_audit.py` adds focused regression
coverage for:

| Test area | Boundary pinned |
| --- | --- |
| SRT envelope emission | Only allowlisted cleartext fields are returned |
| Recursive forbidden field search | No forbidden key appears at nested depth |
| Relay validation | Nested forbidden fields fail closed |
| H-013 header sanitizer | Forbidden aliases fail closed before wrapper emission |
| H-013 envelope wrapper | Returned wrapper contains no lambda/sigma/agent forbidden field |
| HTTP log source scan | Forbidden route-token internals are not recorded |
| Status tokens | Phase 1573p completion tokens are present |

## 5. Non-Claims and Residual Work

This phase does not establish:

| Non-claim | Reason |
| --- | --- |
| Formal `(epsilon, delta)` differential privacy | No adjacency relation, sensitivity bound, composition theorem, or DP proof is introduced here |
| Network anonymity | Timing, path, cover traffic, batching, and global observer defenses are not proven here |
| Full unlinkability | The SIM evidence from Phase 1573h is passive-relay evidence, not a complete unlinkability theorem |
| Signal-equivalent sealed sender | Transport peer metadata and operational routing are still visible |
| Public relay activation | `CCSS_SPECTRAL_01_NOT_ACTIVATED` remains true |

The next privacy-strengthening phases should continue with side-channel SIM
work, cover/batching design, ContactGate policy, and pre-1574 coherence gating.

## 6. Verdict

The narrow relay-visible field claim is supported by code trace and regression
tests: CCSS/SPECTRAL relay-visible envelopes and local log surfaces do not emit
lambda coordinates, noisy eigenvalues, sigma values, raw capability IDs,
recipient public keys, commitment salts, or agent identity fields.

Public path remains blocked.
