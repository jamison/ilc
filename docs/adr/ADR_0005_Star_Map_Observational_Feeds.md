# ADR-0005: Star Map Observational Feeds

**Status:** Accepted  
**Date:** 2026-01-31  
**Authors:** ILC Core Team

---

## Context

As the ILC protocol matures and external agents integrate via MCP, there is a need for efficient, audit-friendly mechanisms to observe protocol events without per-call polling. Polling creates unnecessary load and call spam, especially in high-volume environments.

The existing NDJSON append-only event log pattern (used in `ProtocolEventLog`) provides a foundation for observable feeds. This ADR extends that concept into a formal architectural direction for "observational fields" in star.map.

---

## Decision

We adopt the concept of **star.map observational fields**: broadcast feeds that external consumers can selectively pull from, rather than requiring them to poll individual endpoints.

### Feed Design Principles

1. **Append-Only NDJSON Streaming**: Feeds are append-only NDJSON streams, consistent with existing event log patterns.
2. **Topic-Based Organization**: Events are organized into logical topic queues:
   - `events.reuse.v0` - block reuse and caching events
   - `events.ops.v0` - operational/system events
   - `events.evidence.v0` - evidence submission and challenge events
   - `events.contradiction.v0` - contradiction detection and resolution events
3. **Selective Pull**: Consumers subscribe to topics of interest and pull at their own cadence.
4. **Broadcast Model**: Events are emitted once; multiple consumers can observe the same stream.

### Transport

- Local: Direct file reads from NDJSON event logs
- Future: HTTP SSE or WebSocket streaming (out of scope for this phase)

---

## Consequences

### Positive

- Eliminates polling overhead for event-driven consumers
- Maintains full auditability via append-only logs
- Enables efficient multi-consumer observation of protocol state
- Consistent with existing NDJSON patterns

### Negative

- Requires new feed emitter infrastructure
- Consumers must implement pull/filter logic
- Topic schema versioning needs management

---

## Non-Goals

This ADR does **not** cover:

- Network transport implementation (HTTP, WebSocket, pub-sub brokers)
- Message queue or broker infrastructure
- Real-time push notifications
- Cross-node federation of feeds

These may be addressed in future phases.

---

## Alternatives Considered

### 1. Per-Call Polling via MCP

**Rejected.** Creates excessive call volume and does not scale for high-frequency event streams.

### 2. Full Pub-Sub Broker (e.g., Redis, NATS)

**Deferred.** Adds operational complexity. The append-only NDJSON model provides sufficient functionality for initial use cases without external dependencies.

### 3. Database-Backed Event Store

**Considered but not chosen.** Adds database dependency. NDJSON files are simpler, auditable, and sufficient for current scale.

---

## References

- [ADR-0002: NDJSON Bundle Transport](ADR_0002_NDJSON_Bundle_Transport.md)
- `ilc_core/protocol/event_log.py` - existing NDJSON event log implementation
