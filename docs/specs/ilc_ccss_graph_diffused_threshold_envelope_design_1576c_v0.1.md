# ILC CCSS Graph-Diffused Threshold Envelope Design 1576c v0.1

**Phase:** 1576c
**Window:** 1576+
**Date:** 2026-07-22
**Status:** committed
**Sensitivity:** NON-SENSITIVE

## 1. Purpose and Non-Claims

This document defines a graph-diffused threshold-envelope design for future
CCSS routing. A logical CCSS message `M` is split into `n` encrypted shares,
each share is routed through a distinct PrivacyChart cell, and the recipient
can reconstruct `M` from any `m` successfully delivered shares.

This design extends the Phase 1576b `PrivacyChartManifest` schema and the Phase
1573r cover/batching profile. It does not implement runtime code, mutate a CDL
or ADR, clear any activation guard, write to LMDB, claim formal anonymity,
claim formal differential privacy, or claim global passive observer resistance.

Discovery note: the prompt expected a runtime
`CCSS_COVER_BATCHING_NOT_ACTIVATED` symbol under `ilc_core/sidecars/`, but the
live repository currently contains that token as a future-runtime guard
requirement in the Phase 1573r design spec, not as an `ilc_core` constant. This
phase records that source truth and does not create a runtime guard in a
spec-only lane.

Output token: `threshold_envelope_scheme_defined_phase_1576c`.

## 2. Source Alignment

| Source | Finding Used Here |
| --- | --- |
| `docs/specs/ilc_ccss_privacy_chart_manifest_and_productive_cover_design_1576b_v0.1.md` | Defines `PrivacyChartManifest`, `cell_id`, `member_count >= k_min`, `cover_provenance=sender_generated`, `fixed_bundle_size_bytes=65536`, `batch_window_s=120`, and `cover_ratio_min=8`. |
| `docs/specs/ilc_ccss_cover_batching_design_1573r_v0.1.md` | Defines candidate profile `ccss_pre_rc_cover_batch_profile_v1_candidate`, 120-second windows, 128-bundle minimum batches, 65,536-byte bundles, cover ratio 8, TTL/drop receipts, and future guard requirement. |
| `docs/specs/ilc_ccss_public_rc_privacy_claim_boundary_1573o_v0.1.md` | Preserves non-claims: no formal DP, no network anonymity, no Signal-equivalent claim, no GPO unlinkability, no cover/batching/mixing activation claim. |
| `ilc_core/network/d2d/spectral_route_token.py` | Current hybrid key constants are X25519 32 bytes, ML-KEM-768 public key 1184 bytes, and hybrid public key 1216 bytes. Existing hiding commitment pattern uses `CCSS_SPECTRAL_HIDING_COMMIT_PREFIX` and SHA-256 over canonical JSON. |
| `ilc_core/network/d2d/gossip_transport.py` | Current D2D gossip exposes and enforces single-hop `ILC-Hop-Count`; future CCSS route-depth padding is therefore not a current runtime claim. |

The direct search found no CCSS threshold-sharing implementation in `ilc_core`.
Historical Shamir tooling exists outside the active CCSS runtime surface, but no
current `ilc_core` CCSS module implements graph-diffused threshold envelopes.

## 3. Core Math and Target Profile

Current target profile:

| Parameter | Value | Source |
| --- | ---: | --- |
| `k_min` | 128 | Phase 1576b PrivacyChart cell floor |
| `m` | 3 | 1576c target reconstruction threshold |
| `n` | 7 | 1576c target emitted shares |
| `B` | 65536 bytes | Phase 1573r fixed bundle size |
| `window` | 120 seconds | Phase 1573r release window |
| `cover_r` | 8 | Phase 1573r sparse-traffic cover ratio |

Delivery probability is modeled as independent Bernoulli path success with
per-share success probability `p`:

```python
from math import comb


def p_delivery(n: int, m: int, p: float) -> float:
    return sum(comb(n, i) * (p**i) * ((1 - p) ** (n - i)) for i in range(m, n + 1))
```

For `m=3,n=7`:

| Per-path success `p` | `P(deliver >= 3 of 7)` |
| ---: | ---: |
| 0.5 | 0.773437500000 |
| 0.7 | 0.971204500000 |
| 0.8 | 0.995328000000 |
| 0.9 | 0.999823500000 |

The prompt's inline comment `p_delivery(7, 3, 0.8) ~= 0.967` was arithmetic
drift. The correct value from the stated formula is `0.995328`.

Bandwidth multiplier:

```text
n * (1 + cover_r) = 7 * 9 = 63
```

Each logical message therefore produces 63 fixed-size relay-visible envelopes
under the target sparse-traffic profile.

Per-envelope relay-level guessing advantage under a usable PrivacyChart cell is
bounded by the configured cohort floor:

```text
1 / k_min = 1 / 128 = 0.0078125
```

This is a design target, not a formal anonymity theorem.

## 4. Share Construction

Each logical message `M` is transformed into shares as follows:

1. Split `M` using Shamir-style threshold sharing over GF(2^256) or an
   equivalent ratified field. Shares are `(i, f(i))`, where `f` is a degree
   `m-1` polynomial and `f(0)` encodes `M`.
2. Encapsulate each share independently to the recipient's hybrid capability
   public key. The hybrid key family must remain consistent with
   `spectral_route_token.py`: X25519 plus ML-KEM-768.
3. Use fresh ephemeral material for every share. No ephemeral key, nonce,
   commitment salt, or KEM ciphertext component may be reused across shares of
   the same logical message.
4. Pad every resulting envelope to exactly 65,536 bytes before relay exposure.
5. Assign each share to a distinct usable PrivacyChart cell from the current
   `PrivacyChartManifest`.

Implementation of Shamir splitting is explicitly out of scope for this phase.

## 5. Share Unlinkability Requirements

| Rule | Requirement | Rationale |
| --- | --- | --- |
| Independent encapsulations | Each share uses a fresh KEM encapsulation and fresh ephemeral material. | Prevents direct ciphertext linkage. |
| No shared ephemeral | No share may reuse another share's ephemeral key, nonce, salt, or commitment seed. | Prevents cryptographic and metadata joins. |
| No relay-visible share index | `share_index` must be encrypted inside the envelope. | Relays must not see `i` or infer share ordering. |
| No relay-visible `m/n/count` | Threshold parameters and total share count must not appear in relay-visible fields. | Relays must not group envelopes by logical-message structure. |

Shares of the same logical message must be assigned to distinct PrivacyChart
cells. Assigning two shares to the same cell is forbidden for this profile
because it increases relay-output linkability.

Output token: `share_unlinkability_requirement_defined_phase_1576c`.

## 6. Route Depth and Path-Length Padding

The current D2D gossip runtime exposes and validates a single-hop
`ILC-Hop-Count` header. That runtime behavior is not modified here and cannot
support a relay-path hiding claim.

For future CCSS threshold envelopes, relay-visible route depth must be either:

1. fixed at one canonical depth class for all envelopes in a PrivacyChart cell;
   or
2. padded to the maximum selected depth class so relay-visible hop counts do not
   reveal message type, share index, or reconstruction role.

Hard rule: variable visible route depth is forbidden unless all envelopes in
the same batch are padded to the same relay-visible depth.

Candidate route-depth classes for later simulation:

| Class | Visible Hops | Use Case |
| --- | ---: | --- |
| `depth_1` | 1 | Bootstrap network or low relay density |
| `depth_3` | 3 | Standard production routing target |
| `depth_5` | 5 | High-sensitivity envelopes |

Padding from `depth_1` to `depth_3` would require two onion-encrypted
re-encryption hops with ephemeral material, but that is future runtime work and
requires separate testing.

Output token: `route_depth_padding_defined_phase_1576c`.

## 7. Recipient Scan Model and Cost Bound

The recipient scans only envelopes in cells for which it holds a relevant
recipient capability or trapdoor. Relays see `cell_id` and fixed-size encrypted
envelopes; they do not see recipient identity or plaintext.

Recipient scan bound for this profile:

| Quantity | Bound |
| --- | ---: |
| Minimum usable cell size | `k_min = 128` |
| Envelopes per release window per sparse cell target | `B = 128` |
| Decapsulation attempts per envelope | `O(1)` |
| Recipient scan cost per epoch/window | `O(k_min) = O(128)` |

Once the recipient successfully decapsulates at least `m=3` shares for the same
logical message, it reconstructs `M` by threshold interpolation over the
ratified field.

Relay cheap-check boundary: relays may validate fixed size, envelope class,
batch-window membership, and cell-id membership against a committed
PrivacyChartManifest. Relays must not perform KEM decapsulation, inspect
threshold metadata, infer share groupings, or validate plaintext contents.

Output token: `recipient_scan_cost_bound_defined_phase_1576c`.

## 8. Relation to Phase 1573r

This design is additive to the Phase 1573r profile:

| Phase 1573r Parameter | Status in 1576c |
| --- | --- |
| `ccss_pre_rc_cover_batch_profile_v1_candidate` | Preserved |
| 120-second release window | Preserved |
| 128-bundle minimum batch | Preserved |
| Fixed 65,536-byte bundle class | Preserved |
| 8:1 sparse-traffic cover ratio | Preserved |
| TTL/drop receipt requirement | Preserved |
| Offline recipient bounded mailbox requirement | Preserved |
| No formal anonymity or GPO claim | Preserved |

The only new design elements are threshold sharing, distinct-cell share
routing, share unlinkability requirements, route-depth padding targets, and the
recipient scan-cost bound.

## 9. Future Gates

Future implementation must introduce a default-off runtime guard equivalent to:

```text
CCSS_THRESHOLD_ENVELOPE_NOT_ACTIVATED = True
```

Clearing that guard must require, at minimum:

- a ratified finite-field construction and test vectors for share generation and
  reconstruction;
- fixed-size envelope serialization tests;
- relay-visible metadata tests proving no share index, `m`, `n`, sender id,
  recipient id, route purpose, raw capability id, or spectral coordinate leaks;
- PrivacyChart cell assignment tests proving distinct-cell routing and
  `member_count >= k_min`;
- route-depth padding tests;
- recipient scan-cost tests;
- Phase 1576d threshold diffusion SIM evidence;
- explicit authority for any public relay-serving claim.

## 10. Canonical Boundary Sentence

Threshold envelope diffusion gives a logical CCSS message delivery redundancy
and relay-output ambiguity without requiring GPO resistance. GPO resistance
requires L6 mix/shuffle (Phase 1576a, not yet designed).

## 11. Completion Tokens

```text
threshold_envelope_scheme_defined_phase_1576c
share_unlinkability_requirement_defined_phase_1576c
route_depth_padding_defined_phase_1576c
recipient_scan_cost_bound_defined_phase_1576c
ccss_threshold_envelope_design_complete_phase_1576c
```
