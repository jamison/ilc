# Canon Bundle Key Registry Bundle Format v0.1

## Overview

A **registry bundle** is a distribution artifact containing a signed key registry.

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
