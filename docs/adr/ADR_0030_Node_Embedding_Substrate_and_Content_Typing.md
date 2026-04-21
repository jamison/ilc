# ADR-0030: Node Embedding Substrate and Content Typing

**Status:** Accepted  
**Date:** 2026-04-19  
**Accepted:** 2026-04-21 — Node embedding fields live (commit `1c027054`)

---

## 1. Context

ILC will eventually be queried by near-infinite digital agents operating at semantic rather than lexical resolution. Agents don't retrieve by node ID — they retrieve by meaning: "what is related to this concept?" This is fundamentally a vector similarity query, not a key-value lookup.

Two substrate gaps currently block this:

**1. Content is untyped.** `Node.content` is `Union[str, Dict[str, Any]]` with no type annotation on what the dict contains. Without a declared content type, it is impossible to:
- Select the appropriate embedding model (a claim and a route index should embed differently)
- Validate content shape
- Enable partial field projection ("give me only the `refutation_criterion` of these nodes")
- Route query-side filtering by semantic category

**2. Embeddings have no home.** There is no field on `Node` for a semantic embedding vector. Embedding generation is therefore entirely external with no way to record that an embedding exists, which model generated it, or when it was computed relative to node content.

This ADR adds both fields as optional, additive, non-breaking additions. No existing code changes. No migration required.

---

## 2. Decision

### 2.1 Content typing

Add to `Node` in `ilc_core/types.py`:

```python
content_type: Optional[str] = None
```

Defined content type tokens (extensible):
- `"claim"` — a falsifiable epistemic assertion
- `"evidence"` — supporting or weakening data for a claim
- `"task"` — a work specification
- `"task_result"` — output of a completed task
- `"route_index"` — star.map navigational entry
- `"hyperedge_entity"` — a star-expanded hyperedge node (see ADR-0029 §2.3)
- `"genesis"` — axiomatic core node (immutable)

`content_type=None` on existing nodes is valid — it means untyped (legacy). New nodes SHOULD declare a content type.

Content type does not constrain `content` structure at the Python level in this phase — it is metadata for routing, embedding selection, and future schema validation. A separate validation layer (CDL-deferred) will enforce shape per type.

### 2.2 Embedding substrate

Add to `Node` in `ilc_core/types.py`:

```python
embedding: Optional[List[float]] = None
embedding_model: Optional[str] = None    # e.g., "text-embedding-3-small", "ilc-epistemic-v1"
embedding_epoch: Optional[int] = None    # the epoch at which embedding was computed
```

All three fields are `Optional` and default to `None`. A node without an embedding is valid — it simply cannot participate in vector similarity queries until an embedding is generated.

**Embedding staleness:** if `embedding_epoch < current_epoch` by more than a threshold, analytics layers SHOULD treat the embedding as potentially stale and regenerate before use in clustering or retrieval. The threshold is not fixed by this ADR — it is a parameter for SIM-EMBED-01.

**Scale posture:**
- Testnet (thousands of nodes): store embedding directly in LMDB alongside node record. 6 KB per node at 1536 dims × 10K nodes = 60 MB — acceptable.
- Mainnet (millions of nodes): embedding store separates from LMDB. Node carries `embedding_model` and `embedding_epoch` as cache-invalidation metadata; actual vectors live in a FAISS-backed sidecar. The Node fields remain the same — the storage backend changes, not the interface.

### 2.3 Typed content enables type-appropriate embedding

The correct pipeline is:

```
Node.content_type → select embedding model → embed Node.content → Node.embedding
```

A `"claim"` node should be embedded by a model trained on or fine-tuned for epistemic claim structure. A `"route_index"` node should be embedded by a model that captures navigational proximity. Without `content_type`, all nodes are embedded by the same undifferentiated model, degrading retrieval quality.

This ADR establishes the field. SIM-EMBED-01 will determine which embedding models produce meaningful proximity for each content type.

### 2.4 Partial field projection (forward declaration)

`content_type` enables a future partial-projection query pattern:
```
"give me only the refutation_criterion field from claim nodes matching embedding distance < θ"
```

This is NOT implemented in this ADR. The field is declared now so that future query implementations can rely on `content_type` being present. Without it, field projection would require content inspection (fragile) rather than type dispatch (clean).

---

## 3. What this does NOT do

- Does not change how existing nodes are stored or retrieved — all fields are Optional with None defaults
- Does not require any existing node creation path to supply content_type or embedding
- Does not implement embedding generation — that is a separate analytics service
- Does not specify which embedding model to use — deferred to SIM-EMBED-01

---

## 4. SIM required before activation of embedding pipeline

- **SIM-EMBED-01**: for each content_type, evaluate candidate embedding models on ILC-specific retrieval tasks (find-related-claim, find-conflicting-evidence, find-similar-task). Determine model selection per type and acceptable staleness threshold.

---

## 5. Consequences

### Accepted
- `content_type`, `embedding`, `embedding_model`, `embedding_epoch` added to `Node` — all Optional, zero behavioral change
- All future node creation paths encouraged (not required) to declare `content_type`
- Embedding-based semantic retrieval becomes possible without further schema changes
- Type-appropriate embedding model selection becomes possible

### Rejected alternatives
- **Store embeddings in a separate table only**: rejected because decoupling embedding from node breaks the atomic view needed for gossip — a peer receiving a node should be able to cache its embedding alongside it without a second lookup
- **Use content inspection to infer type**: rejected because it is fragile, slow, and produces incorrect results for multi-purpose content fields

---

## 6. Related
- ADR-0029: Hypergraph Substrate (hyperedge_entity is a content_type; embedding applies to star-expanded hyperedge nodes)
- ADR-0031: Subgraph Homomorphism Query Contract (node responses in gRPC SHOULD include content_type; embedding is omitted from wire format by default for bandwidth reasons)
- SIM-EMBED-01: embedding model calibration per content type
- Glossary: Morphogenetic Distributed Hypergraph (docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md §5)
