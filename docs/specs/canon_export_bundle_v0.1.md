# Canon Export Bundle v0.1 Specification

**Version:** v0.1  
**Status:** Draft  
**Last Updated:** 2026-02-05

## Purpose
Defines a directory-based package structure for distributing canon exports along with their validation reports and integrity manifests. This format ensures that consumers can verify the integrity of the export file and its associated validation metadata.

## Directory Layout
A valid bundle is a directory containing exactly these three files:

```
<bundle_root>/
├── export.json      # The canon export payload (v0.1 export format)
├── validate.json    # The validation result ({ok, errors, warnings})
└── manifest.json    # Integrity metadata linking the above files
```

## File Formats

### 1. `export.json`
*   **Format:** Single-line JSON (recommended), newline-terminated.
*   **Schema:** Must conform to [Canon Export Format v0.1](./canon_export_format_v0.1.md).

### 2. `validate.json`
*   **Format:** Single-line JSON, newline-terminated.
*   **Schema:**
    ```json
    {
      "ok": boolean,
      "errors": [string],
      "warnings": [string]
    }
    ```

### 3. `manifest.json`
*   **Format:** Single-line JSON, newline-terminated.
*   **Fields:**

| Field | Type | Description |
|---|---|---|
| `bundle_format` | string | Fixed `"v0.1"` |
| `export_format` | string | The version from `export.json` (e.g., `"v0.1"`) |
| `hash_alg` | string | Hash algorithm used (e.g., `"sha256"`) |
| `created_at` | string | ISO-8601 UTC timestamp of bundle creation |
| `export_hash` | string | Hex digest of `export.json` content (excluding terminal newline) |
| `validate_hash` | string | Hex digest of `validate.json` content (excluding terminal newline) |
| `canon_hash` | string | Promoting `canon_hash` from export for easy indexing |
| `export_path` | string | Relative path to export file (`"export.json"`) |
| `validate_path` | string | Relative path to validate file (`"validate.json"`) |

## Integrity Verification
To verify a bundle:
1.  Read `manifest.json`.
2.  Read `export.json` (strip trailing newline if calculating strict content hash intended by signer, though v0.1 writer implementation hashes bytes *before* writing newline. *Clarification: The v0.1 python implementation computes SHA-256 of the JSON bytes **before** the terminating newline is appended.*).
3.  Compute hash of `export.json` content.
4.  Assert `computed_hash == manifest.export_hash`.
5.  Repeat for `validate.json`.

> **Note:** This bundle format provides **integrity**, not authenticity. It proves the files match the manifest, but does not prove who created the manifest (unless distributed via a signed channel).
