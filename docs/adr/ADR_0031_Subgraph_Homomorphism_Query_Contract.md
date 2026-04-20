# ADR-0031: Subgraph Homomorphism Query Contract

**Status:** Proposed  
**Date:** 2026-04-19  
**Urgency:** Pre-M-018 gate — the gRPC surface added in M-018 Workload F must not be locked before this contract is in the proto schema.

---

## 1. Context

M-018 (Workload F) will activate the ILC gRPC public query surface, starting with `GetBalance` and `GetEpoch`. Future RPC methods will return epoch records, node summaries, and eventually richer graph data. If those responses return flat lists of records without edge metadata, we lock in flat-list query semantics. Retrofitting edge metadata into an existing proto schema is a breaking change requiring client migration.

ILC's long-term architecture is a morphogenetic distributed hypergraph where agents query semantic subgraphs of each other's graph state. The mathematical basis for this is graph homomorphism: a subgraph query should return a structure-preserving subset — if node A and node B are both in the response and an edge A→B exists in the source graph, that edge must be in the response. A flat list of matched node records violates this invariant silently.

This ADR establishes the query contract before the gRPC surface locks. It does not require implementation of subgraph queries in M-018 — only that the proto schema is forward-compatible with them.

---

## 2. Decision

### 2.1 Wire format: EdgeRecord added to proto

Add `EdgeRecord` to `ilc_consensus/proto/ilc_app.proto`:

```proto
message EdgeRecord {
    string source_id = 1;
    string target_id = 2;
    string link_type = 3;   // e.g., "supports", "refutes", "depends_on", "derives_from"
    float  weight    = 4;   // optional; 0.0 = unweighted
}
```

All future RPC response messages that return multiple nodes MUST include a `repeated EdgeRecord edges` field, populated when the caller sets `include_edges = true` on the request.

All future RPC request messages that return multiple nodes MUST include a `bool include_edges` field, defaulting to `false`.

### 2.2 The homomorphism invariant

This invariant is the normative contract for any ILC subgraph query implementation:

> **Homomorphism invariant:** If a query response includes node A and node B, and an edge A→B exists in the queried subgraph, then that edge MUST appear in `edges`. Omitting edges between returned nodes is a protocol violation.

This invariant is enforced at query time by the serving validator. It is verifiable by the requesting agent by cross-checking `edges` against the returned node set.

### 2.3 Hyperedge extension (forward reservation)

When HyperEdge types are activated (per ADR-0029), the response schema extends to:

```proto
message HyperEdgeRecord {
    string          id            = 1;
    string          hyperedge_type = 2;
    repeated string member_ids    = 3;
    repeated string head_ids      = 4;   // directed: source set; empty if undirected
    repeated string tail_ids      = 5;   // directed: target set; empty if undirected
    float           weight        = 6;
    uint64          epoch         = 7;
}
```

Response messages MUST reserve a field number for `repeated HyperEdgeRecord hyperedges` even if unpopulated in early implementations.

### 2.4 Proto comment as normative gate

The following comment MUST appear in `ilc_app.proto` adjacent to any query response message containing edges:

```
// Subgraph Homomorphism Invariant (ADR-0031): when include_edges=true,
// if both source_id and target_id of an edge are present in the returned
// node set, that edge MUST be included in edges[]. Partial edge sets
// that omit intra-response edges are a protocol violation.
```

---

## 3. Consequences

### Accepted
- All M-018+ gRPC query responses carry the `include_edges` field and `repeated EdgeRecord edges` field, even when empty
- Agents that don't need edges set `include_edges = false` (default) with zero overhead
- Future subgraph query implementations are backwards-compatible with M-018 clients

### Rejected alternatives
- **Add edges later when needed**: rejected because proto field addition to existing messages requires client migration and creates version fragmentation
- **Use a sidecar edges endpoint**: rejected because it breaks the atomicity of the subgraph response — caller cannot trust that edges and nodes are consistent if fetched separately

---

## 4. Related
- ADR-0029: Hypergraph Substrate (HyperEdge type; HyperEdgeRecord extends this contract)
- ADR-0030: Node Embedding Substrate (embedding fields on node responses follow the same forward-reservation pattern)
- M-018 Workload F: the gRPC surface this ADR gates
- Glossary entry: Subgraph Homomorphism Invariant (docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md §5)
