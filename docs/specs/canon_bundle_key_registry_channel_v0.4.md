# Canon Bundle Key Registry Channel Format v0.4

Version `v0.4` introduces mandatory rollback protection fields.

## Changes from v0.3
- **Required**: `channel_seq` (integer, >= 0). Strictly monotonic.
- **Required**: `published_at` (ISO-8601 UTC string).
- **Optional**: `prev_channel_hash` (hex sha256 of previous canonical JSON).

## Schema

```json
{
  "channel_version": "v0.4",
  "updated_at": "<ISO-8601>",
  "published_at": "<ISO-8601>",
  "channel_seq": <int>,
  "prev_channel_hash": "<hex-sha256-optional>",
  "current_channel": "<string>",
  "channels": ["<string>", ...],
  "sources": {
    "<channel_name>": ["<source_uri>", ...]
  },
  "channel_order": ["<channel_name>", ...]
}
```

## Validation Rules
1. `channel_seq` must be non-negative integer.
2. `published_at` must be valid ISO-8601 UTC.
3. `prev_channel_hash` must be valid 64-char hex string if present.

## Version Policy Note
In production environments (`prod=True`), version `v0.4` is mandatory. Legacy versions (`v0.3`, `v0.2`, `v0.1`) are rejected by default to enforce rollback protection. Non-production environments may allow legacy versions via explicit compatibility flags (`--allow-legacy-channel-v03`), but these modes operate with reduced security semantics (no rollback protection).

