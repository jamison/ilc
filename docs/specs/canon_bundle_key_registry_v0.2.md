# Canon Bundle Key Registry Format v0.2 (Signing Addendum)

## Overview

This addendum describes the detached signature file used to attest integrity of a canon bundle key registry file. The registry JSON format remains **v0.1**; signing metadata is stored separately in a `.sig` file.

## Detached Signature File

For a registry file at:

```
canon_key_registry_v0.1.json
```

the detached signature file is:

```
canon_key_registry_v0.1.json.sig
```

### Signature JSON Fields (required)

| Field | Type | Description |
|-------|------|-------------|
| `sig_alg` | string | Must be `"hmac-sha256"` |
| `key_id` | string | Signing key ID (16‑char lowercase hex) |
| `signed_at` | string | Strict ISO‑8601 timestamp with timezone |
| `registry_hash` | string | SHA‑256 hex of canonical registry bytes |
| `signature_hex` | string | HMAC‑SHA256 hex of canonical registry bytes |

### Canonical Registry Bytes

Canonical bytes are computed from the registry JSON (v0.1) using:

```python
json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
```

No trailing newline is permitted.

## Verification Rules

1. Registry JSON loads and validates per v0.1 schema.
2. Signature JSON loads and contains all required fields.
3. `signed_at` must be strict ISO‑8601 with timezone (`Z` or `±HH:MM`).
4. `registry_hash` must match SHA‑256 of canonical registry bytes.
5. `signature_hex` must match HMAC‑SHA256 over canonical bytes using the provided key.
6. `key_id` should match the derived key ID for the signing key.

## Error Codes

- `signature_missing`
- `signature_invalid`
- `signature_mismatch`
- `signature_key_unknown`
- `key_missing_for_verify`

## Notes

This is a policy attestation (shared‑secret HMAC), not a public trust anchor. Future revisions may add asymmetric signatures or registry signing with public verification.
