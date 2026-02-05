# Canon Export Format v0.1 Specification

**Version:** v0.1  
**Status:** Draft  
**Last Updated:** 2026-02-05

## Purpose

This specification defines a **machine-readable interchange format** for exporting `canon_state` artifacts from the ILC protocol. The goal is to provide a stable, consistent structure for downstream consumers (indexers, graph builders, analytics tools) to ingest ledger state without relying on internal memory representations.

## Design Principles

1.  **Machine-Friendly:** Strict JSON structure with explicit types.
2.  **Forward-Compatible:** Unknown keys in data sections (`epochs`, `snapshots`) are allowed to facilitate protocol evolution without breaking parsers.
3.  **Self-Describing:** Includes metadata, versioning, and hashes for verification.
4.  **Flat Top-Level:** Key metadata is lifted to the root for O(1) access.

## Schema Definition

### Top-Level Object

The root object MUST contain the following fields:

| Field | Type | Required | Description |
|---|---|---|---|
| `canon_export_format` | string | Yes | Fixed value: `"v0.1"` |
| `canon_hash` | string | Yes | The canonical SHA-256 hash of the state content. |
| `computed_hash` | string | No | The hash computed during export (for verification). |
| `exported_at` | string | Yes | ISO-8601 UTC timestamp of export generation. |
| `meta` | object | Yes | Summary counts and export version. |
| `epochs` | list | Yes | List of epoch records. |
| `snapshots` | list | Yes | List of stake snapshots. |
| `kpis` | object | No | Optional KPI summary (matches `meta` counts). |

### Meta Object

| Field | Type | Required | Description |
|---|---|---|---|
| `canon_export_version` | string | Yes | The version string from the source `canon_state`. |
| `epoch_count` | integer | Yes | Number of epoch records. |
| `snapshot_count` | integer | Yes | Number of stake snapshots. |
| `balance_count` | integer | Yes | Number of agent balances (if balances map exists). |

### Epoch Record

Minimum shape:

```json
{
  "epoch_id": "<string>",
  "epoch_index": <integer>,
  "summary": { ... }
}
```

### Snapshot Record

Minimum shape:

```json
{
  "epoch_id": "<string>",
  "balances": { "<agent_id>": <float> }
}
```

## Example Payload

```json
{
  "canon_export_format": "v0.1",
  "canon_hash": "a1b2c3d4e5f6",
  "computed_hash": "a1b2c3d4e5f6",
  "exported_at": "2026-02-05T12:00:00+00:00",
  "meta": {
    "canon_export_version": "v0.1",
    "epoch_count": 1,
    "snapshot_count": 1,
    "balance_count": 1
  },
  "epochs": [
    {
      "epoch_id": "epoch_1",
      "epoch_index": 1,
      "summary": {
        "task_count": 10,
        "agent_count": 5,
        "reward_total": 100.0,
        "stake_total": 5000.0
      }
    }
  ],
  "snapshots": [
    {
      "epoch_id": "epoch_1",
      "balances": {
        "agent_alice": 1000.0
      }
    }
  ],
  "kpis": {
    "epoch_count": 1,
    "snapshot_count": 1,
    "balance_count": 1
  }
}
```

## Versioning

*   **Format Version (`canon_export_format`):** Incremented for breaking schema changes.
*   **Content Version (`canon_export_version`):** Reflects the version of the *source* `canon_state` production logic.

Parsers SHOULD check `canon_export_format` first.
