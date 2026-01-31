# Star Map Geometry Overlay Placeholders

## Purpose

This file tracks future geometry overlay ideas for star.map without implementing them yet. It keeps the intent visible while the current workstream focuses on route_index tooling and transport.

---

## Placeholder: Route Descriptor Node Schema (Future)

Goal: define a route descriptor node that can carry geometric metadata about a route or cluster.

Draft fields (placeholder only):
- schema: "ilc.star.map.route_descriptor@v1"
- route_id: string (CIDv1 or registry label)
- geometry_type: string (e.g., simplicial_complex, hypergraph, polytope)
- geometry_payload_ref: CIDv1 (content-addressed geometry data)
- bounds: optional summary stats (node_count, edge_count, dimension)
- provenance: producer, created_at

Status: Not implemented.

---

## Placeholder: Multi-Route Coherence Representation (Future)

Goal: represent coherence or alignment across multiple routes.

Draft approaches (placeholder only):
- Shared simplex sets for route overlap
- Hyperedge bundles for multi-route constraints
- Weighted coherence score over shared claims/evidence

Status: Not implemented.

---

## Placeholder: Incremental Update Strategy (Future)

Goal: enable efficient incremental updates to route_index artifacts without full rebuilds.

Notes:
- Consider compacted de Bruijn update methods (e.g., Cdbgtricks-style index-assisted updates)
- Potential L2 approach: maintain an update index plus periodic full compaction
- Keep determinism and auditability as first-class constraints

Status: Not implemented.

---

## Placeholder: Minimizer-Space Compression (Future)

Goal: explore minimizer-space style compression to reduce route_index size while preserving routing signal.

Notes:
- Minimizer-space de Bruijn graphs use ordered minimizers instead of raw k-mers to reduce graph size.
- Potential L2 approach: define a deterministic minimizer scheme over tokens and build a route_index on the minimizer stream.
- Trade-off: compression introduces sampling bias; must be evaluated against routing accuracy.

Status: Not implemented.
