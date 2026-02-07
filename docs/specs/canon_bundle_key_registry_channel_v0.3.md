# Canon Bundle Key Registry Channel Format v0.3

> **Supersedes:** v0.2

## Overview

A **channel file** tracks available registry sources and the currently active channel. v0.3 adds support for detached signatures.

---

## File Schema (Same as v0.2)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `channel_version` | string | yes | Must be `"v0.3"` |
| `updated_at` | string | yes | ISO-8601 with timezone |
| `current_channel` | string | yes | Active channel name |
| `channels` | array | yes | Available channel names (sorted, unique) |
| `channel_order` | array | no | Promotion order |
| `sources` | object | no | Map channel → list of source URLs |
| `last_sync` | object | no | Last sync metadata |
| `notes` | string | no | Optional notes |

---

## Detached Signature Sidecar

- **Path:** `<channel_file>.sig`
- **Format:** JSON

```json
{
  "sig_alg": "hmac-sha256",
  "key_id": "a1b2c3d4e5f6a7b8",
  "signed_at": "2026-02-07T16:10:00Z",
  "channel_hash": "<sha256 canonical channel bytes>",
  "signature_hex": "<hmac sha256 hex over canonical channel bytes>"
}
```

- **Canonicalization:**
  - JSON dump with `sort_keys=True`, `separators=(',', ':')`, UTF-8 encoding.
  - Sidecar contents are NOT included in the channel JSON payload.

---

## Policy

- **Invalid Signature:** Always hard fail.
- **Missing Signature:**
  - Default: Warning (unenforced).
  - Required mode: Hard fail.

---

## Exit Codes

- 0: ok
- 1: validation/policy error
- 2: IO error
