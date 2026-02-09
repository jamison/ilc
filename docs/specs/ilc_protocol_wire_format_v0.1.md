# ILC Protocol Wire Format v0.1 Specification

**Version:** v0.1  
**Status:** Draft  
**Date:** 2026-02-09  

## Overview

This specification defines the canonical wire format for ILC Protocol events. It enforces a strict, deterministic schema for the three primary atomic actions in the protocol: `claim`, `refute`, and `stake`.

This format is designed to be:
- **Deterministic:** No ambiguous fields; strict ordering and types.
- **Machine-Readable:** strictly validated by JSON Schema.
- **Minimal:** Encodes only the necessary logical data for consensus, leaving rich content to sidecars.

## Schema

The normative schema is defined in [ilc_protocol_wire_format_v0.1.json](./ilc_protocol_wire_format_v0.1.json).

### Common Fields

All events MUST include:

| Field | Type | Description |
|---|---|---|
| `protocol_version` | `string` | Must be `"v0.1"`. |
| `event_id` | `string` | SHA-256 hash (64 hex chars) uniquely identifying this event. |
| `timestamp` | `string` | ISO-8601 UTC timestamp ending in `Z` (e.g., `2026-02-09T12:00:00Z`). |
| `agent_id` | `string` | Identifier of the agent creating the event. |
| `event_kind` | `enum` | One of `"claim"`, `"refute"`, `"stake"`. |

### Event Types

#### 1. Claim
Asserts a fact or unit of work.

| Field | Type | Requirement | Description |
|---|---|---|---|
| `content_hash` | `string` | Required | SHA-256 hash of the content/payload being claimed. |
| `content_url` | `string` | Optional | URI pointing to the content payload. |
| `context_ids` | `array<string>` | Optional | IDs of parent/context events. |

#### 2. Refute
Challenges an existing claim.

| Field | Type | Requirement | Description |
|---|---|---|---|
| `target_claim_id` | `string` | Required | ID of the claim being challenged. |
| `reason` | `string` | Required | Human or machine-readable reason code. |
| `evidence_hash` | `string` | Optional | SHA-256 hash of evidence supporting the refutation. |

#### 3. Stake
Allocates economic weight to an event.

| Field | Type | Requirement | Description |
|---|---|---|---|
| `target_event_id` | `string` | Required | ID of the event (claim or refute) being staked. |
| `amount` | `string` | Required | Integer string representing the stake amount (e.g., `"100"`). |
| `currency` | `string` | Required | Identifier for the token/currency (e.g., `"ILC"`). |

## Examples

### Valid Claim
```json
{
  "protocol_version": "v0.1",
  "event_id": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2",
  "timestamp": "2026-02-09T14:30:00Z",
  "agent_id": "agent-007",
  "event_kind": "claim",
  "content_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "context_ids": ["parent-123"]
}
```

### Valid Refute
```json
{
  "protocol_version": "v0.1",
  "event_id": "b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3",
  "timestamp": "2026-02-09T14:35:00Z",
  "agent_id": "verifier-9000",
  "event_kind": "refute",
  "target_claim_id": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2",
  "reason": "signature_invalid"
}
```

### Invalid (Missing Discriminator)
```json
{
  "protocol_version": "v0.1",
  "event_id": "c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4",
  "timestamp": "2026-02-09T14:40:00Z",
  "agent_id": "agent-007",
  "content_hash": "..."
}
```
**Error:** `schema_violation:missing_field:event_kind`
