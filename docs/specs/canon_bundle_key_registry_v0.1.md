# Canon Bundle Key Registry Format v0.1

## Overview

This document defines the canonical on-disk format for the ILC canon bundle key registry. The registry tracks signing keys across their lifecycle (current, previous, deprecated) to support key rotation.

## Format

The registry file is a JSON object with the following structure:

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `registry_version` | string | Must be `"v0.1"` |
| `updated_at` | string | Strict ISO-8601 timestamp (e.g., `"2026-02-06T21:30:00Z"`) |
| `current_keys` | array of strings | Active signing keys |
| `previous_keys` | array of strings | Accepted but deprecated keys (warning) |
| `deprecated_keys` | array of strings | Rejected keys |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `notes` | string | Human-readable notes |

### Key ID Format

Key IDs must be lowercase hexadecimal strings of exactly 16 characters, matching the output of `derive_key_id()` (SHA-256 prefix).

Pattern: `^[0-9a-f]{16}$`

## Validation Rules

1. JSON must be valid
2. All required fields must be present
3. Key IDs must match the pattern `^[0-9a-f]{16}$`
4. No duplicates within any list
5. No overlaps between current/previous/deprecated lists
6. `updated_at` must be strict ISO-8601 format
7. Lists should be sorted for determinism (warning if unsorted)
8. `current_keys` should not be empty in production (warning)
9. Maximum 10,000 keys per list (warning if exceeded)

## Example

```json
{
  "registry_version": "v0.1",
  "updated_at": "2026-02-06T21:30:00Z",
  "current_keys": ["a1b2c3d4e5f6a7b8"],
  "previous_keys": ["0011223344556677"],
  "deprecated_keys": ["deadbeefdeadbeef"],
  "notes": "Rotated after key compromise"
}
```

## File Discovery

The registry file is discovered via:
1. Explicit path passed to loader
2. `ILC_KEY_REGISTRY_PATH` environment variable
3. Default file `config/canon_key_registry_v0.1.json`

## Security Considerations

The registry is a policy file that controls which signing keys are accepted. It is **not** a trust anchor itself. Future versions may add cryptographic signing of the registry to prevent tampering.

For production deployments:
- Store the registry in a protected location
- Use version control for audit trail
- Validate registry integrity before deployment
