# ILC Edge and Link Boundary Contract v0.1

## Status
Accepted for implementation boundary hardening in Phase 1007.

## Purpose
Clarify the role split between `edge` and `link` graph relation paths so relation semantics are deterministic and migration-safe.

## Boundary

### Edge path (compatibility lineage surface)
- Data model: `GraphEdge`
- Storage/indexes: `outgoing_edges`, `incoming_edges`
- Allowed relation types: `derives_from` only
- Intended usage: claim lineage compatibility in legacy call paths

### Link path (semantic relation surface)
- Data model: `LinkRecord`
- Storage/indexes: `links`, `outgoing_links`, `incoming_links`
- Allowed relation types:
  - `supports`
  - `refutes`
  - `equivalent`
  - `depends_on`
- Intended usage: semantic graph reasoning and protocol-level relation semantics

## Enforced invariants
1. Any non-`derives_from` relation sent through edge APIs is rejected.
2. Link APIs continue to validate semantic link types via `validate_link_type`.
3. Boundary hardening does not remove the compatibility edge APIs in this phase.

## Non-goals
- Full edge API removal.
- Automatic edge-to-link migration of historical records.
- Expansion of semantic link type vocabulary.
