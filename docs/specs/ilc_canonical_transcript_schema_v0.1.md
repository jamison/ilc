# ILC Canonical Transcript Schema v0.1 Specification

**Version:** v0.1  
**Status:** Draft  
**Date:** 2026-02-09  

## Overview

This specification defines the **Canonical Transcript**, a deterministic, append-only log of all events and receipts in a given time window (epoch). The transcript serves as the authoritative history of the protocol state.

## Schema

The normative schema is defined in [ilc_canonical_transcript_schema_v0.1.json](./ilc_canonical_transcript_schema_v0.1.json).

### Fields

| Field | Type | Requirement | Description |
|---|---|---|---|
| `protocol_version` | `string` | Required | Must be `"v0.1"`. |
| `transcript_id` | `string` | Required | SHA-256 hash of the transcript content (canonical JSON form). |
| `previous_transcript_id` | `string` | Required | Pointer to previous transcript. All zeros for genesis. |
| `timestamp_start` | `string` | Required | ISO-8601 UTC start time. |
| `timestamp_end` | `string` | Required | ISO-8601 UTC end time. |
| `records` | `array` | Required | List of events/receipts. |

### Ordering Rules

Records MUST be sorted deterministically by the tuple:
1. `timestamp` (ascending)
2. `event_kind` (lexicographical: `claim` < `receipt` < `refute` < `stake` ...)
3. `event_id` (lexicographical ascending)

Any deviation from this order is an `ordering_violation`.

## Examples

### Valid Transcript
```json
{
  "protocol_version": "v0.1",
  "transcript_id": "a1b2...",
  "previous_transcript_id": "0000000000000000000000000000000000000000000000000000000000000000",
  "timestamp_start": "2026-02-09T14:00:00Z",
  "timestamp_end": "2026-02-09T15:00:00Z",
  "records": [
    {
      "protocol_version": "v0.1",
      "event_id": "111...",
      "timestamp": "2026-02-09T14:01:00Z",
      "event_kind": "claim",
      "agent_id": "agent-A",
      "content_hash": "..."
    },
    {
      "protocol_version": "v0.1",
      "event_id": "222...",
      "timestamp": "2026-02-09T14:02:00Z",
      "event_kind": "claim",
      "agent_id": "agent-B",
      "content_hash": "..."
    }
  ]
}
```

### Invalid Transcript (Unsorted)
```json
{
  "records": [
    { "timestamp": "2026-02-09T14:02:00Z", ... },
    { "timestamp": "2026-02-09T14:01:00Z", ... }
  ]
}
```
**Error:** `ordering_violation` (Records not sorted by timestamp).
