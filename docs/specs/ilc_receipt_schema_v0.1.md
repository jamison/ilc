# ILC Receipt Schema v0.1 Specification

**Version:** v0.1  
**Status:** Draft  
**Date:** 2026-02-09  

## Overview

This specification defines the canonical schema for **Receipts** in the ILC Protocol. A receipt is an immutable record of a claim's final outcome, including the consensus decision and any resulting economic transfers (payouts or slashes).

## Schema

The normative schema is defined in [ilc_receipt_schema_v0.1.json](./ilc_receipt_schema_v0.1.json).

### Fields

| Field | Type | Requirement | Description |
|---|---|---|---|
| `protocol_version` | `string` | Required | Must be `"v0.1"`. |
| `receipt_id` | `string` | Required | SHA-256 hash uniquely identifying this receipt. |
| `timestamp` | `string` | Required | ISO-8601 UTC timestamp. |
| `related_claim_id` | `string` | Required | The `event_id` of the claim being resolved. |
| `outcome` | `enum` | Required | One of `"valid"`, `"invalid"`, `"ambiguous"`. |
| `payouts` | `array` | Required | List of economic transfers. Empty if none. |
| `evidence_cids` | `array` | Optional | List of Content Identifiers (CIDs) for evidence used in the decision. |

### Payout Object

| Field | Type | Description |
|---|---|---|
| `recipient_agent_id` | `string` | Identifier of the agent receiving funds. |
| `amount` | `string` | Integer string of atomic units. |
| `currency` | `string` | Token identifier. |

## Examples

### Valid Receipt (Payout)
```json
{
  "protocol_version": "v0.1",
  "receipt_id": "d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5",
  "timestamp": "2026-02-09T15:00:00Z",
  "related_claim_id": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2",
  "outcome": "valid",
  "evidence_cids": ["QmHash1", "QmHash2"],
  "payouts": [
    {
      "recipient_agent_id": "agent-007",
      "amount": "500",
      "currency": "ILC"
    },
    {
      "recipient_agent_id": "verifier-9000",
      "amount": "50",
      "currency": "ILC"
    }
  ]
}
```

### Invalid Receipt (Negative Amount)
```json
{
  "protocol_version": "v0.1",
  "receipt_id": "...",
  "timestamp": "...",
  "related_claim_id": "...",
  "outcome": "valid",
  "payouts": [
    {
      "recipient_agent_id": "agent-007",
      "amount": "-500",
      "currency": "ILC"
    }
  ]
}
```
**Error:** `schema_violation:invalid_format:amount` (Pattern mismatch `^[0-9]+$`).
