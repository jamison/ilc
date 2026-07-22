# ILC CCSS PrivacyChartManifest and Productive Cover Design 1576b v0.1

**Phase:** 1576b
**Window:** 1576+
**Date:** 2026-07-22
**Status:** committed
**Sensitivity:** NON-SENSITIVE

## 1. Purpose and Scope

This document defines the PrivacyChartManifest schema and the productive cover
taxonomy for graph-native CCSS cohort routing. A PrivacyChart assigns agents to
coarse relay-visible routing cells so that relay-visible operations are
attributed to a cohort of size `k_min >= 128`, not to an individual. Productive
cover fills unused batch capacity with real ILC graph operations rather than
empty synthetic waste.

This design is consistent with the Phase 1573r profile:

| Parameter | Value |
| --- | --- |
| Release batch window | 120 seconds |
| Minimum batch anonymity set | 128 indistinguishable bundles |
| Fixed bundle size | 65,536 bytes |
| Minimum cover ratio | 8 cover envelopes per real envelope when traffic is sparse |
| Required cover provenance for this design | `sender_generated` |

This document does not activate any runtime, does not assert formal anonymity,
does not claim GPO resistance, and does not open or mutate any CDL.

## 2. PrivacyChartManifest Schema

```json
{
  "privacy_chart_id": "<sha256 over epoch_root and chart_version>",
  "chart_version": "v0.1",
  "epoch_root": "<epoch boundary hash>",
  "batch_window_s": 120,
  "fixed_bundle_size_bytes": 65536,
  "k_min": 128,
  "cover_ratio_min": 8,
  "cells": [
    {
      "cell_id": "<deterministic hash of cell parameters>",
      "coarse_geometry_descriptor": "<opaque quantized bucket label>",
      "member_count": 128,
      "cover_provenance": "sender_generated",
      "productive_cover_classes": [
        "atlas_slice_availability_check",
        "star_map_refresh",
        "mailbox_poll"
      ]
    }
  ]
}
```

| Field | Type | Constraint |
| --- | --- | --- |
| `privacy_chart_id` | string | Deterministic SHA-256-derived handle from `epoch_root` and `chart_version`. |
| `chart_version` | string | Current value: `v0.1`. |
| `epoch_root` | string | Epoch-boundary commitment anchoring the chart. |
| `batch_window_s` | integer | Must equal `120` for the current profile. |
| `fixed_bundle_size_bytes` | integer | Must equal `65536` for the current profile. |
| `k_min` | integer | Must equal or exceed `128`; current profile locks `128`. |
| `cover_ratio_min` | integer | Must equal or exceed `8` while traffic is sparse. |
| `cells` | array | Non-empty list of usable cohort cells. |
| `cell_id` | string | Deterministic hash of cell parameters; must not encode agent identity. |
| `coarse_geometry_descriptor` | string | Opaque bucket label; must not expose exact spectral coordinates or `agent_id`. |
| `member_count` | integer | Must be `>= k_min` before the cell is usable. |
| `cover_provenance` | string | Must be `sender_generated` for relay-indistinguishable cover. |
| `productive_cover_classes` | array | At least one allowed class from Section 4. |

Output token: `privacy_chart_manifest_schema_defined_phase_1576b`.

## 3. Cell Assignment and k_min Invariant

Cell assignment is derived from the epoch's PrivacyChart, not from live network
topology revealed to relays.

1. Compute each agent's local spectral fingerprint using a coarse quantized
   bucket. Do not publish exact eigenvalue arrays, raw spectral coordinates, or
   stable agent identifiers.
2. Group agents into cells by bucket.
3. Merge cells below `k_min` into nearest compatible neighbor cells until every
   usable cell satisfies the floor.
4. Publish the PrivacyChartManifest as a signed graph node under the relevant
   graph authority lane.
5. Agents cache their assigned `cell_id`; relays see `cell_id` and fixed-size
   encrypted envelopes, not `agent_id`.

Hard invariant: a cell with `member_count < k_min` MUST NOT be used for routing.
The relay-visible batch must contain only cells meeting this floor.

Output token: `privacy_chart_k_min_invariant_defined_phase_1576b`.

## 4. Productive Cover Taxonomy

Valid `productive_cover_class` values:

| Class | Operation | Graph value |
| --- | --- | --- |
| `atlas_slice_availability_check` | Request or confirm availability of a named Atlas slice. | Slice replication health. |
| `star_map_refresh` | Fetch updated star-map routing index material. | Route-table freshness. |
| `mailbox_poll` | Poll relay mailbox for pending CCSS envelopes. | Delivery reliability. |
| `relay_health_receipt` | Emit a signed health attestation for a relay. | Network health monitoring. |
| `sidecar_sync` | Sync a sidecar recipe or profile to a relay. | Sidecar distribution. |
| `folded_proof_step` | Emit one folding step for a recursive proof in a future HyperNova lane. | Proof-compression amortization. |

Output token: `productive_cover_class_taxonomy_defined_phase_1576b`.

## 5. Anti-Distinguishability Requirement

Productive cover envelopes MUST have the same fixed size, relay-visible metadata
profile, and batch timing distribution as real CCSS envelopes. For the current
profile, that means `65536` bytes, `120` second batch windows, and the same
relay-visible envelope class.

Relays MUST NOT be able to identify which envelopes are productive cover versus
real CCSS messages based on size, metadata, or timing alone. If any cover class
produces a distinguishable envelope, it must be excluded until the distinguisher
is eliminated.

If a cover class requires relay knowledge to execute, it is not valid
sender-generated cover. It must be classified separately as `relay_initiated`
and cannot support the 1576a sender-generated-cover privacy result.

## 6. Batch Composition Model

A usable relay batch for one cohort cell contains:

| Component | Rule |
| --- | --- |
| Real CCSS envelopes | Encrypted envelopes from agents assigned to the current cell. |
| Productive cover envelopes | Sender-generated real graph operations from the same cell. |
| Minimum batch size | `B = k_min = 128` before release. |
| Release timing | Fixed 120 second window boundary; never adaptive to sender timing. |
| Sparse-traffic cover ratio | Maintain at least 8 productive cover envelopes per real envelope while real traffic is below the batch floor. |

Relay-visible surface: fixed-size encrypted envelopes, shuffled release order,
epoch/window metadata, and cell id.

Relay-hidden surface: real versus cover status, agent identity, exact spectral
coordinates, bucket parameters, recipient identity, plaintext, and route purpose.

## 7. Non-Claims and Future Gates

This document does not prove formal anonymity, differential privacy, or GPO
resistance. It defines a schema and design target that must be implemented and
tested before any public claim is strengthened.

Future runtime work must remain guarded behind a future token equivalent to:

```text
CCSS_PRIVACY_CHART_NOT_ACTIVATED = True
```

Guard clearance must require implementation evidence, envelope-format tests,
cover-provenance tests, relay-visible metadata tests, and the Phase 1576d
threshold diffusion SIM evidence.

## 8. Compatibility Notes

Phase 1576a showed that sender-generated cover is the load-bearing assumption
for the modeled relay-level intersection result. Relay-labelable cover does not
support that claim. This spec therefore requires `cover_provenance:
sender_generated` for PrivacyChart cells used in CCSS privacy routing.

The Phase 1573o public-RC boundary remains unchanged: no formal DP claim, no
network anonymity claim, no GPO-resistance claim, no cover/batching activation
claim, and no relay-path hiding claim are authorized by this document.
