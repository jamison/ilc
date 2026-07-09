# ILC CCSS Cover and Batching Design 1573r v0.1

**Phase:** 1573r
**Window:** 1565-1575
**Date:** 2026-07-09
**Status:** committed
**Sensitivity:** NON-SENSITIVE

## 1. Purpose

This document specifies the pre-public-RC cover, batching, fixed-bundle,
relay-queue, TTL, and offline-recipient design required before ILC may make a
stronger CCSS traffic-analysis-resistance claim than the narrow Phase 1573o
route-token non-disclosure claim.

This phase does not activate public relay serving, public RC, formal anonymity,
formal differential privacy, wallet writes, minting, settlement, or any guard.

## 2. Source Evidence

| Source | Finding |
| --- | --- |
| `docs/specs/ilc_ccss_public_rc_privacy_claim_boundary_1573o_v0.1.md` | Public RC may claim only route-token non-disclosure unless later evidence clears side-channel gaps |
| `docs/specs/ilc_ccss_metadata_leakage_audit_1573p_v0.1.md` | Relay-visible payload/log surfaces omit spectral coordinates and identity internals, but transport metadata remains visible |
| `docs/sims/ilc_ccss_side_channel_sim_1573q_v0.1.json` | Recommended candidate: `ccss_pre_rc_cover_batch_profile_v1_candidate` |
| `docs/specs/ilc_epoch_boundary_commit_semantics_decision_546_v0.1.md` | Epoch-boundary accumulation reduces message-level timing surfaces |
| `docs/adr/ADR_0025_D2d_HTTP_Gossip_Transport_Binding.md` | D2D gossip uses bounded HTTP/3/HTTP fallback envelope; no dynamic peer discovery in v1 |
| `ilc_core/network/d2d/http_gossip_transport_runtime.py` | Runtime remains transport-focused and does not implement public relay cover/batching |
| `ilc_core/network/d2d/spectral_route_token.py` | CCSS-SPECTRAL remains guard-closed |

## 3. Selected Design Profile

Canonical profile token:

```text
ccss_pre_rc_cover_batch_profile_v1_candidate
```

Required parameters:

| Parameter | Value |
| --- | --- |
| Release batch window | 120 seconds |
| Minimum batch anonymity set | 128 indistinguishable bundles |
| Cover ratio | 8 cover bundles per real bundle when natural traffic is below the minimum batch target |
| Bundle sizing | fixed-size bundle classes; public-RC profile uses one fixed class until a later size-class proof exists |
| Route purpose | concealed from relay-visible fields; relay sees only generic relay/bundle handling |
| Relay path | rotate per bundle or per epoch; stable route reuse is forbidden for stronger claims |
| TTL | required |
| Offline recipient policy | required |
| Claim shape | configured anonymity-set and metadata-minimization claim only |

The 1573q SIM modeled this profile with worst modeled linking probability
`0.01` under the tested `N` grid, bounded by the configured anonymity set. This
does not prove global anonymity.

## 4. Fixed Bundle Shape

The public-RC candidate uses a single fixed relay bundle shape:

```json
{
  "bundle_version": "ccss_cover_bundle_v1",
  "profile": "ccss_pre_rc_cover_batch_profile_v1_candidate",
  "bundle_size_bytes": 65536,
  "ciphertext": "<fixed-length bytes>",
  "epoch": 0,
  "release_window_seconds": 120,
  "route_purpose_visible_to_relay": false
}
```

Rules:

- Real and cover bundles are indistinguishable by size.
- Route purpose is sealed inside the recipient-readable payload, not exposed as
  a relay-visible classifier.
- The relay may observe fixed bundle size, epoch, release window, and queue
  timing. It must not observe route purpose, recipient identity, raw capability
  identifiers, spectral coordinates, or plaintext.
- Future multi-class size support requires a separate proof or SIM showing the
  class does not create unacceptable cohort leakage.

## 5. Batch Release Rules

For each release window:

1. Collect real bundles for the window.
2. Add cover bundles until the release set has at least 128 bundles.
3. If natural traffic plus configured cover cannot reach 128 within the window,
   hold until the next 120-second window unless the bundle TTL would expire.
4. Shuffle release order with secure randomness in the future runtime
   implementation.
5. Emit all bundles at the batch boundary, not immediately on receipt.

This design follows the Phase 546 epoch-boundary principle: reduce
message-level timing surfaces by materializing relay-visible effects at coarse
boundaries.

## 6. Relay Queue Behavior

Relay queue state is local and non-authority-bearing. A future runtime must
maintain these logical queues:

| Queue | Purpose |
| --- | --- |
| `pending_real` | encrypted real bundles awaiting batch release |
| `pending_cover` | locally generated cover bundles awaiting batch release |
| `ready_batch` | fixed-size bundles ready for shuffled release |
| `expired_drop_receipts` | local audit receipts for TTL drops |

Relays must not persist raw recipient capability IDs, route purpose, plaintext,
or spectral data in queue records.

## 7. TTL and Drop Policy

Required public-RC candidate TTL:

| Field | Value |
| --- | --- |
| `bundle_ttl_windows` | 5 |
| `bundle_ttl_seconds` | 600 |
| `drop_receipt_required` | true |
| `drop_receipt_public` | false |

If a bundle cannot be released before TTL expiry, the relay drops it and records
a local non-public drop receipt containing only:

```json
{
  "receipt_version": "ccss_bundle_drop_receipt_v1",
  "bundle_commitment": "<sha256 of ciphertext bundle>",
  "drop_reason": "ttl_expired",
  "epoch": 0,
  "window_index": 0
}
```

## 8. Offline Recipient Policy

Offline recipients are handled by bounded mailbox retention, not permanent
circulation.

| Field | Value |
| --- | --- |
| `offline_mailbox_retention_windows` | 20 |
| `offline_mailbox_retention_seconds` | 2400 |
| `recipient_pull_required` | true |
| `public_delivery_claim` | false |

The relay may retain fixed-size encrypted bundles for offline recipients within
the retention window. It must drop expired bundles with local drop receipts.
The design does not guarantee delivery to offline recipients.

## 9. Replay and Duplicate Handling

Each bundle must carry or derive a sealed nonce/nullifier inside the encrypted
payload. Relay-visible duplicate handling uses only a bundle commitment:

```json
{
  "receipt_version": "ccss_relay_batch_receipt_v1",
  "profile": "ccss_pre_rc_cover_batch_profile_v1_candidate",
  "batch_commitment": "<merkle-root-or-sha256-list-root>",
  "bundle_count": 128,
  "release_window_seconds": 120,
  "fixed_bundle_size_bytes": 65536,
  "route_purpose_visible_to_relay": false
}
```

The relay may de-duplicate identical ciphertext commitments. It must not inspect
or log recipient identity, plaintext, route purpose, or spectral metadata.

## 10. Future Runtime Guard Requirements

Any future runtime implementation must remain guarded until explicit authority
clears it. Required guard token:

```text
CCSS_COVER_BATCHING_NOT_ACTIVATED = True
```

Guard clearance must require:

- implementation of fixed bundles;
- implementation of 120-second batching;
- implementation of cover generation at ratio 8 when traffic is sparse;
- relay-path rotation;
- TTL/drop receipts;
- offline mailbox retention bounds;
- tests proving route purpose is not relay-visible;
- Phase 1574 activation-matrix authorization;
- Phase 1575 public-RC gate authorization if public serving is involved.

## 11. Phase 1574 Claim Wording

Allowed if and only if this design remains unchanged or is strengthened by
implementation evidence:

```text
ILC has a pre-public-RC CCSS cover/batching design that targets configured
anonymity-set traffic-analysis resistance using fixed-size bundles,
batch-boundary release, cover bundles, route-purpose concealment, and relay-path
rotation. This is a design and SIM-supported target, not a formal anonymity or
differential privacy proof.
```

Forbidden:

```text
ILC proves network anonymity.
ILC provides formal differential privacy for CCSS traffic.
ILC is Signal-equivalent.
ILC hides timing, size, and relay-path metadata against global observers.
```

## 12. Verdict

Phase 1573r closes the design gap identified by 1573q by selecting a concrete
cover/batching profile for future implementation.

This phase does not activate the profile.

This phase does not authorize stronger public claims until implementation and
activation evidence exists.
