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
| `sig_alg` | `enum` | `"ed25519"`. |
| `signature` | `string` | Hex-encoded signature. |
| `signed_at` | `string` | ISO-8601 UTC timestamp. |

## Runtime Acceptance Semantics (Cluster A)

Schema validation alone is not sufficient for governance acceptance. Runtime ingest/conformance enforces the following rules:

### 1) Record Identity Binding Mode

- `record_digest_v1` is the canonical mode: identity checks bind `gov_record_id` to the SHA-256 digest of the entire record (excluding `signatures`).
- `payload_hash_v0` is legacy compatibility mode and must be explicitly set in policy state.
- Fail-closed rule: if `known_records` is non-empty and `known_records_hash_mode` is missing or unknown, acceptance must fail with `context_violation:known_records_hash_mode_required`.
- Safe default: if `known_records` is empty and mode is missing/unknown, runtime defaults to `record_digest_v1`.

### 2) Pure Apply Contract

`apply_governance_record` is a pure function over inputs:

- It must not mutate `current_policy_state`.
- On success it returns a deterministic state delta at `data.policy_state_delta`:
  - `proposals`: proposal state transition update.
  - `known_records`: identity binding update for `gov_record_id`.
  - `known_records_hash_mode`: effective mode used for this acceptance.

### 3) Strict Governance Binding in Conformance

Conformance policy checks (Phase 136/137) are strict for governance records:

- Governance records require full policy binding (`policy_hash`, `policy_epoch`, `policy_window`).
- If expected policy context is supplied and binding is missing, it is a hard failure (`context_violation:missing_policy_binding`).
- Unchecked-binding warning (`policy_binding_absent_unchecked`) applies only when no expectations are provided.

Implementation references:
- `ilc_core/protocol/ilc_cluster_a_ingest.py`
- `ilc_core/protocol/ilc_cluster_a_conformance.py`

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
