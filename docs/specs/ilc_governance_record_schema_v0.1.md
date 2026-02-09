# ILC Governance Record Schema v0.1 Specification

**Version:** v0.1  
**Status:** Draft  
**Date:** 2026-02-09  

## Overview

This specification defines the canonical schema for **Governance Records**. These records track the lifecycle of protocol governance, from proposal to finalization or rejection. Crucially, they serve as the container for cryptographic signatures from governance keys, authorizing changes to the protocol.

## Schema

The normative schema is defined in [ilc_governance_record_schema_v0.1.json](./ilc_governance_record_schema_v0.1.json).

### Fields

| Field | Type | Requirement | Description |
|---|---|---|---|
| `protocol_version` | `string` | Required | Must be `"v0.1"`. |
| `gov_record_id` | `string` | Required | SHA-256 hash unique to this record. |
| `timestamp` | `string` | Required | ISO-8601 UTC timestamp. |
| `proposal_id` | `string` | Required | Unique ID of the proposal. |
| `state` | `enum` | Required | `"proposed"`, `"finalized"`, `"rejected"`. |
| `payload` | `object` | Required | The content of the proposal (e.g., parameter dict). |
| `signatures` | `array` | Required | List of signer objects. |

### Signature Object

| Field | Type | Description |
|---|---|---|
| `key_id` | `string` | ID of the signing key (referenced in Key Registry). |
| `sig_alg` | `enum` | `"ed25519"` or `"secp256k1"`. |
| `signature` | `string` | Hex-encoded signature. |
| `signed_at` | `string` | ISO-8601 UTC timestamp. |

## Examples

### Valid Finalized Record
```json
{
  "protocol_version": "v0.1",
  "gov_record_id": "aaabbb...",
  "timestamp": "2026-02-09T16:00:00Z",
  "proposal_id": "prop-123",
  "state": "finalized",
  "payload": {
    "min_stake_amt": "1000",
    "epoch_duration": "3600"
  },
  "signatures": [
    {
      "key_id": "key-admin-01",
      "sig_alg": "ed25519",
      "signature": "deadbeef...",
      "signed_at": "2026-02-09T15:55:00Z"
    }
  ]
}
```

### Invalid (Missing Signatures)
```json
{
  "protocol_version": "v0.1",
  "state": "finalized",
  "signatures": []
}
```
**Error:** `schema_violation:minItems:signatures` (Must have at least 1 signature).
