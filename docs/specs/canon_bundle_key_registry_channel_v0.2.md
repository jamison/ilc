# Canon Bundle Key Registry Channel Format v0.2

> **Supersedes:** v0.1

## Overview

A **channel file** tracks available registry sources and the currently active channel. v0.2 adds per-channel source URLs and sync metadata.

---

## File Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `channel_version` | string | yes | Must be `"v0.2"` |
| `updated_at` | string | yes | ISO-8601 with timezone |
| `current_channel` | string | yes | Active channel name |
| `channels` | array | yes | Available channel names (sorted, unique) |
| `channel_order` | array | no | Promotion order |
| `sources` | object | no | Map channel → list of source URLs |
| `last_sync` | object | no | Last sync metadata |
| `notes` | string | no | Optional notes |

---

## Sources Schema

```json
{
  "sources": {
    "experimental": ["file:///tmp/registry/experimental.bundle"],
    "test": ["https://example.com/registry/test.bundle"],
    "main": ["/var/ilc/registry/main.bundle", "https://mirror.example.com/main.bundle"]
  }
}
```

- Each channel in `channels` must have a non-empty sources list if `sources` is present.
- Sources can be: local path, `file://` URL, or `https://` URL.

---

## Last Sync Schema

```json
{
  "last_sync": {
    "channel": "main",
    "source": "https://mirror.example.com/main.bundle",
    "timestamp": "2026-02-07T12:00:00Z",
    "bundle_hash": "abc123...",
    "key_id": "a1b2c3d4e5f6a7b8",
    "ok": true,
    "selected_source_reason": "first_success",
    "source_attempts": [
      {
        "index": 0,
        "source": "/var/ilc/registry/main.bundle",
        "ok": false,
        "errors": ["source_not_found"],
        "attempt_duration_ms": 12
      },
      {
        "index": 1,
        "source": "https://mirror.example.com/main.bundle",
        "ok": true,
        "errors": [],
        "attempt_duration_ms": 450
      }
    ],
    "warnings": [],
    "errors": []
  }
}
```

---

## CLI Usage

```bash
# Sync current channel
python3 -m ilc_core.cli.canon_bundle_key_registry_sync \
  --channel-file channel.json --key-file key.txt --dest /var/ilc/registry

# Sync specific channel
python3 -m ilc_core.cli.canon_bundle_key_registry_sync \
  --channel-file channel.json --key-file key.txt --dest /var/ilc/registry --channel main

# Use alternate source
python3 -m ilc_core.cli.canon_bundle_key_registry_sync \
  --channel-file channel.json --key-file key.txt --dest /var/ilc/registry --source-index 1
```

---

## Exit Codes

- 0: ok
- 1: validation error
- 2: IO error
