# ILC Agent Graph Projection Interface Spec 1222 v0.1

**Phase:** 1222
**Window:** 1218-1224
**Date:** 2026-05-06
**Status:** DESIGN SPEC ONLY - no runtime implementation

`agent_graph_projection_interface_spec_committed_phase_1222`

---

## 1. Purpose

Digital agents need machine-native access to ILC graph and hypergraph slices before human
visualization sidecars can be meaningful. This spec defines the read-only projection
interface agents should consume.

Human 3D star-map visualization is an L3 sidecar concern. It must not reshape canonical ILC
semantics, schemas, graph identifiers, or hypergraph rules.

---

## 2. Layer Separation

| Layer | Scope | Phase 1222 status |
|-------|-------|-------------------|
| Canonical artifacts | Signed Genesis manifests, CDL/ADR docs, runtime outputs, graph JSON | Existing inputs |
| Agent graph projection interface | Deterministic read-only filtered exports, metrics, traces, stable IDs | Specified here |
| L3 sidecar infrastructure | External app contracts, auth model, data-consumption guarantees, UI attachment | Deferred to Window 1225+ |
| Human visualization | 2D/3D star maps, focus/zoom, overlays, navigation | Future sidecar app |

---

## 3. Required Projection Types

The first projection interface should support:

- `authority_graph`: Genesis lineage, signer authority, release-key lineage, fork boundary.
- `claim_composition_graph`: claim derivation and primitive invocation.
- `provenance_graph`: creator, reuse, attribution, PROVENANCE paths, phi-bound evidence.
- `runtime_binding_graph`: runtime modules, dependency tokens, CDL/ADR bindings.
- `economic_flow_graph`: ECU attribution, settlement edges, mint pressure, decay.
- `branchial_convergence_graph`: derivation-state paths, merge/divergence traces.
- `repo_hypergraph`: file, symbol, doc, test, phase, and artifact hyperedges.

---

## 4. Query Primitives

Minimum machine-native query shapes:

- ego graph: node/hyperedge plus radius `N`;
- path to Genesis: derivation or authority path back to Node 0 / root envelope;
- filtered projection: by phase, CDL, ADR, node class, edge type, artifact type, creator,
  ratification state, runtime token, or lineage domain;
- convergence trace: where paths merge, diverge, or fail to merge;
- centrality metrics: degree, betweenness, hyperedge order, merge depth, provenance depth,
  branchial convergence score;
- export: deterministic JSON and NDJSON.

---

## 5. Stable IDs and Source References

Every projected node, edge, and hyperedge must carry:

- canonical ID;
- projection-local ID;
- source artifact path or artifact hash;
- source line or source object pointer when available;
- generating projection version;
- Genesis lineage domain when applicable.

Agents must be able to cite and verify every projection claim.

---

## 6. Bounds

No unbounded graph dump by default.

Required bounds:

```text
max_nodes
max_edges
max_hyperedges
max_depth
max_paths
max_bytes
```

Default first-pass caps:

```text
max_nodes = 500
max_edges = 1500
max_hyperedges = 500
max_depth = 4
max_paths = 100
max_bytes = 10_000_000
```

Large exports require explicit operator configuration.

---

## 7. Determinism

Projection export must use deterministic ordering:

- sort nodes by canonical ID;
- sort edges by `(source, target, edge_type, canonical_id)`;
- sort hyperedges by canonical hyperedge ID;
- serialize canonical JSON with sorted keys and no NaN;
- never include wall-clock timestamps in hashed projection payloads.

---

## 8. Visualization Boundary

EVE-style star maps are useful visual inspiration only:

- floating spatial layout;
- focus/zoom;
- selectable nodes;
- route overlays;
- color and size encodings.

They are not an ILC semantic model. No ILC artifact should be adapted to an EVE schema.
Visualization consumes projections; it does not define them.

---

## 9. Future Work

Carry-forward:

```text
l3_sidecar_infrastructure_spec_required_window_1225_plus
agent_graph_projection_interface_implementation_required_window_1225_plus
```

The sidecar spec must define app attachment, authorization, versioning, data-consumption
guarantees, and failure behavior before a first human visualization sidecar is built.

---

## 10. Non-Claims

This phase does not:

- implement projection tooling;
- introduce an L3 sidecar runtime;
- create visualization UI;
- mutate canonical graph schemas;
- mutate `ilc_core/`;
- authorize public release or public repository publication.

