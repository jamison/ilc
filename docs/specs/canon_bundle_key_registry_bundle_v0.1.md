# Canon Bundle Key Registry Bundle Format v0.1

## Overview

A **registry bundle** is a distribution artifact containing a signed key registry.

This format defines the **canonical artifact** that nodes can verify deterministically.
Transport mechanisms (streaming, subscription feeds, pub/sub) are intentionally
out of scope for v0.1 so we can stabilize integrity rules first. In future phases,
streams can deliver *the same canonical bundle content* as chunked, content-addressed
deltas, but the bundle remains the final source of truth for settlement.

---

## Bundle Structure

```
canon_key_registry_bundle_v0.1/
├── canon_key_registry_v0.1.json       # Registry file
├── canon_key_registry_v0.1.json.sig   # Detached signature
└── registry_manifest.json             # Bundle metadata
```

---

## Manifest Schema

| Field | Type | Description |
|-------|------|-------------|
| `bundle_version` | string | Must be `"v0.1"` |
| `created_at` | string | ISO-8601 with timezone |
| `registry_path` | string | Basename of registry file |
| `registry_hash` | string | SHA-256 of canonical JSON bytes |
| `registry_size_bytes` | integer | File size in bytes |
| `sig_path` | string | Basename of signature file |
| `sig_alg` | string | Signature algorithm |
| `key_id` | string | Signing key ID (16 hex chars) |
| `registry_version` | string | Registry version from JSON |
| `sig_hash` | string | SHA-256 of signature file |

---

## Security

- Registry hash computed from canonical JSON (sorted keys, compact)
- Signature hash provides integrity check on signature file
- Path fields must be basenames only (no path traversal)

---

## Future Transport Layer (Context)

The bundle is a **canonical snapshot**. A streaming or subscription layer is a
transport mechanism, not the truth source. When we add streaming, the expectation
is that streams will carry **content-addressed chunks** (Merkle-style or NDJSON
deltas) that reconstruct a bundle on disk. Verification still happens against the
bundle manifest + signature, so streaming can be added without changing settlement
semantics.

In short: **bundles remain canonical artifacts; streams deliver chunked, signed
deltas that rehydrate into a bundle**.

This maps to the earlier “star map” intuition: broadcast is a **pointer**, not the
payload. Agents can signal that *something exists* (like a star in the sky), but
anyone who wants to know **what** it is must pull and verify the canonical bundle.
That keeps discovery scalable while preserving local verification.

Practically, this means:
- **Pull-first** is the default (fetch/verify/settle).
- **Broadcast** is metadata only (announcements, hints, indices).
- **Bundles** are the final truth objects and the basis for settlement.

**Source note:** See `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt`
for the original “star map / pull discovery” discussion (Oct 8, 2025).

---

## Auditor Panels by Layer (Context)

We anticipate *multiple auditor panels* operating at different layers of the stack:

- **Settlement / Canonical panel**: verifies bundle integrity (hashes, signatures,
  schema, epoch linkage). This panel decides accept/reject for settlement.
- **Transport / Streaming panel**: verifies delivery correctness (chunk completeness,
  replay safety, path traversal, DOS anomalies). Produces reliability metrics and
  triggers re-fetch but does not override canonical acceptance.
- **Semantic / Agent panel**: evaluates epistemic quality, contradictions, and
  relevance of the underlying claims/updates. Produces *quality weights* that can
  influence rewards, but does not change the canonical bundle hash.

This layered model keeps **truth, reliability, and meaning** separated while still
allowing each to influence downstream incentives.

---

## CLI Usage

```bash
# Build bundle
python3 -m ilc_core.cli.canon_bundle_key_registry_bundle \
  --build --registry registry.json --key-file key.txt --out-dir ./bundles

# Verify bundle
python3 -m ilc_core.cli.canon_bundle_key_registry_bundle \
  --verify --bundle ./bundles/canon_key_registry_bundle_v0.1 --key-file key.txt
```

---

## Size Limit

Bundles over 5 MB emit a `bundle_too_large` warning.
