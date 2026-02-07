# Canon Bundle Key Registry Channel Format v0.1

> **Note:** v0.2 supersedes this version. See `canon_bundle_key_registry_channel_v0.2.md`.

## Overview

A **channel file** tracks available registry sources (e.g., main, test, experimental) and the currently active channel.

---

## File Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `channel_version` | string | yes | Must be `"v0.1"` |
| `updated_at` | string | yes | ISO-8601 with timezone |
| `current_channel` | string | yes | Active channel name |
| `channels` | array | yes | Available channel names (sorted, unique) |
| `notes` | string | no | Optional notes |

---

## Channel Name Constraints

- Lowercase letters, numbers, and dashes only
- Maximum 32 characters
- Pattern: `^[a-z0-9-]{1,32}$`

---

## CLI Usage

```bash
# Validate
python3 -m ilc_core.cli.canon_bundle_key_registry_channel --file channel.json --validate

# List channels
python3 -m ilc_core.cli.canon_bundle_key_registry_channel --file channel.json --list

# Set current channel
python3 -m ilc_core.cli.canon_bundle_key_registry_channel --file channel.json --set main

# Create file with initial channel
python3 -m ilc_core.cli.canon_bundle_key_registry_channel --file channel.json --set main --create

# Force add missing channel
python3 -m ilc_core.cli.canon_bundle_key_registry_channel --file channel.json --set experimental --force
```

---

## Exit Codes

- 0: ok
- 1: validation error
- 2: IO error
