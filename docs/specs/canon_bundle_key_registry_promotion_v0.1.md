# Canon Bundle Key Registry Promotion v0.1

## Overview

Promotion workflow enables controlled rollout of registry bundles between channels (e.g., `experimental → test → main`).

---

## Promotion Flow

1. Verify source bundle
2. Check channel order (if configured)
3. Atomic copy bundle to destination
4. Update `last_promotion` in channel file
5. Optionally update `current_channel` with `--switch`

---

## Channel File Extensions

```json
{
  "last_promotion": {
    "from": "test",
    "to": "main",
    "timestamp": "2026-02-07T10:00:00Z",
    "bundle_hash": "abc123...",
    "key_id": "a1b2c3..."
  },
  "channel_order": ["experimental", "test", "main"]
}
```

---

## CLI Usage

```bash
# Promote test to main
python3 -m ilc_core.cli.canon_bundle_key_registry_promotion \
  --src /path/to/test --dest /path/to/main \
  --channel-file channel.json --from test --to main --key-file key.txt

# Dry run
python3 -m ilc_core.cli.canon_bundle_key_registry_promotion \
  --src /path/to/test --dest /path/to/main \
  --channel-file channel.json --from test --to main --key-file key.txt --dry-run

# Promote and switch current channel
python3 -m ilc_core.cli.canon_bundle_key_registry_promotion \
  --src /path/to/test --dest /path/to/main \
  --channel-file channel.json --from test --to main --key-file key.txt --switch
```

---

## Exit Codes

- 0: ok
- 1: validation/policy error
- 2: IO error
