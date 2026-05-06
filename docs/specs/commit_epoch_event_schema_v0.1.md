> **SUPERSEDED — HISTORICAL ARCHIVE ONLY.**
> This G4-era draft (Phase 69a, 2026-02-01) pre-dates CDL-051, the ADR-0004
> revision, and the no-wall-clock / no-float / consensus-only-issuer rules.
> It contains `created_at` (ISO 8601 wall-clock timestamp) and other fields
> that are **prohibited** under current protocol rules.
> **It is not a governing source.** Canonical authority: ADR-0004, CDL-051,
> `ilc_consensus/src/epoch_settlement.rs`, and CLAUDE.md §ILC Coding Security Standards.
> The Phase 1226 spec (`docs/specs/ilc_commit_epoch_causal_frontier_mapping_spec_1226_v0.1.md`)
> is the current authoritative mapping document.
> Do not use field definitions, examples, or parameters from this file
> without verifying they are consistent with the superseding authorities above.

# Commit.Epoch Event Schema v0.1

**Version:** 0.1  
**Status:** DRAFT (SUPERSEDED — see tombstone above)
**Date:** 2026-02-01

## Purpose and Scope

The `commit.epoch` event is the definitive signal of epoch finalization within the ILC protocol. It marks a point in time where a set of logical operations (tasks, agent actions) are sealed, summarized, and cryptographically anchored.

This schema defines the structure of the `commit.epoch` event payload found in the ILC Event Log (NDJSON).

## Goals

- Provide a stable, parseable signal for epoch transitions.
- Anchor the state of the protocol at a specific point in time.
- Summarize economic activity for the epoch (rewards, stakes).
- Link to cryptographic proofs (CIDs) of the detailed event log and state snapshot.

## Non-Goals

- Encoding complex economic logic or formulas (this is just the log output).
- Replacing the detailed ledger or transaction history (summary only).

## Schema Definition

### Top-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `event_kind` | String | Yes | Must be `commit.epoch`. |
| `epoch_index` | Integer | Yes | Monotonically increasing epoch number (>= 0). |
| `epoch_id` | String | Yes | Unique, stable identifier for this specific epoch instance. |
| `namespace_id` | String | Yes | NodeID or CID of the entity emitting this epoch. |
| `created_at` | String | Yes | ISO 8601 timestamp (UTC, Z suffix). |
| `finalization_state` | String | Yes | Enum: `committed`, `rolled_back`, `superseded`. |
| `summary` | Object | Yes | Economic and operational summary. |
| `checksums` | Object | Yes | Cryptographic anchors. |

### Summary Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `task_count` | Integer | Yes | Number of tasks processed in this epoch (>= 0). |
| `agent_count` | Integer | Yes | Number of active agents in this epoch (>= 0). |
| `reward_total` | Number | Yes | Total rewards distributed (>= 0). |
| `stake_total` | Number | Yes | Total active stake (>= 0). |

### Checksums Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `epoch_events_cid` | String | Yes | CID of the full event log segment for this epoch. |
| `epoch_state_cid` | String | Yes | CID of the state snapshot at epoch end. |

## Example Payload

```json
{
  "event_kind": "commit.epoch",
  "epoch_index": 42,
  "epoch_id": "epoch_42_QmNodeID...",
  "namespace_id": "QmNodeID...",
  "created_at": "2026-02-01T12:00:00Z",
  "finalization_state": "committed",
  "summary": {
    "task_count": 150,
    "agent_count": 5,
    "reward_total": 100.5,
    "stake_total": 5000.0
  },
  "checksums": {
    "epoch_events_cid": "bafkq...",
    "epoch_state_cid": "bafkq..."
  }
}
```

## Constraints

- **Time:** `created_at` must be strictly ordered relative to previous epochs.
- **Sequence:** `epoch_index` must be exactly `previous_epoch_index + 1`.
- **Immutability:** Once `finalization_state` is `committed`, the epoch is immutable unless explicitly `rolled_back` by a later consensus event (rare).
