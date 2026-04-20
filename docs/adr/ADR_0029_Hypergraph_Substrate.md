# ADR-0029: Hypergraph Substrate

**Status:** Proposed  
**Date:** 2026-04-19

---

## 1. Context

ILC's current epistemic graph uses binary edges only: every `LinkRecord` connects exactly one source node to one target node. This is adequate for pairwise relationships (A supports B, A refutes B) but loses group structure:

- A **panel** evaluating a claim involves one claim node, N evidence nodes, and M judge agents — this is one relationship with N+M+1 participants, not N+M separate binary relationships
- A **co-authored node** has multiple agents as joint creators — currently modeled as N separate creator links
- A **refutation coalition** — multiple agents jointly challenging a claim — has no natural binary representation
- An **epoch boundary event** ties multiple validators to multiple settled claims simultaneously

Collapsing these into binary edges destroys the group structure and makes it impossible to recover the original relationship from the stored data.

ILC's long-term architectural characterization is a trustless morphogenetic distributed hypergraph (Glossary §5). This ADR establishes the substrate that makes that characterization true in code, without requiring immediate migration of existing binary edges.

The key mathematical primitives required are:

- **Vertices (V)**: existing `Node` objects
- **Hyperedges (E)**: subsets of V with |E| ≥ 2, connecting any number of nodes
- **Weighted hyperedges (W)**: weight per hyperedge (dynamic, epoch-stamped)
- **Incidence structure (H)**: H(v,e) = 1 if v ∈ e — stored as two sparse dicts, not as an explicit matrix
- **Directed hyperedges**: head set (source) and tail set (target) for directional group relationships
- **Temporal stamping**: hyperedges are epoch-stamped for temporal hypergraph analysis
- **Star expansion**: each hyperedge can be unfolded into a bipartite structure (the star node representing the hyperedge becomes a first-class Node) — this is the mechanism by which hyperedges become epistemiological entities with their own provenance, refutation criteria, and signatures

---

## 2. Decision

### 2.1 HyperEdge type

Add to `ilc_core/types.py`:

```python
from dataclasses import dataclass, field
from typing import List, Optional, Set
from decimal import Decimal

@dataclass(frozen=True)
class HyperEdge:
    """
    An n-ary relationship connecting any subset of graph nodes.
    Replaces N binary edges when the relationship is fundamentally group-structured.
    
    Directed hyperedges use head_ids (source set) and tail_ids (target set).
    Undirected hyperedges populate member_ids only; head_ids and tail_ids are empty.
    
    weight is dynamic — callers must apply temporal decay (CDL-V1) before use.
    epoch stamps when this hyperedge was declared, enabling temporal hypergraph analysis.
    
    Star expansion: to obtain the homoiconic form, create a Node of type 'hyperedge_entity'
    with id=self.id and link each member_id to it via binary edges. This makes the hyperedge
    an addressable epistemiological entity (see ADR-0029 §2.3).
    """
    id: str                                    # content-addressed ID (hash of canonical fields)
    hyperedge_type: str                        # "panel" | "co_authorship" | "refutation_coalition" | "epoch_boundary"
    member_ids: List[str]                      # all members (undirected); or union of head+tail (directed)
    head_ids: List[str]                        # directed source set; empty list if undirected
    tail_ids: List[str]                        # directed target set; empty list if undirected
    weight: Decimal                            # W(e) — caller responsible for decay via CDL-V1
    epoch: int                                 # temporal stamp
    agent_id: str                              # declaring agent
    signature: str                             # attribution
```

### 2.2 Sparse incidence index in EpistemicGraph

Add to `EpistemicGraph.__init__()` in `ilc_core/graph.py`:

```python
# Hypergraph structures — parallel to binary edges, not replacing them
self.hyperedges: Dict[str, HyperEdge] = {}
self.vertex_membership: Dict[str, Set[str]] = {}   # node_id  → set of hyperedge_ids  (sparse H^T row)
self.hyperedge_members: Dict[str, Set[str]] = {}   # hyperedge_id → set of node_ids   (sparse H column)
```

These two dicts together are the sparse representation of the incidence matrix H. Derived quantities:
- **Vertex degree**: `len(vertex_membership[node_id])` — O(1)
- **Hyperedge degree**: `len(hyperedge_members[hyperedge_id])` — O(1)
- **H row for vertex v**: `vertex_membership[v]` — the set of hyperedges containing v
- **H column for hyperedge e**: `hyperedge_members[e]` — the set of nodes in e

The explicit incidence matrix H (|V| × |E|) is NEVER stored. It is computed on demand by analytics layers.

### 2.3 Star expansion — hyperedges as epistemiological entities

The star expansion of hyperedge e creates a `Node` of `type="hyperedge_entity"` with `id=e.id`, and binary `LinkRecord` edges from each member node to this star node. This is NOT automatic — it is an explicit operation called when a hyperedge is to be promoted to a first-class epistemiological entity (able to receive claims, refutations, provenance).

Star expansion is the mechanism that fulfills the homoiconic star map requirement: navigational relationships (e.g., a route cluster, a panel result) become graph nodes subject to epistemic evaluation.

### 2.4 Laplacian computation (analytics layer, not substrate)

The normalized hypergraph Laplacian:

```
Δ = D_V^{-1/2} · H · W · D_E^{-1} · H^T · D_V^{-1/2}
```

is computed on demand from the sparse dicts. It is NEVER stored (too large at scale). The analytics layer computes it from `vertex_membership`, `hyperedge_members`, and `HyperEdge.weight` values.

Epoch KPIs derived from Δ that ARE stored (per epoch, in the KPI store):
- `lambda_2`: algebraic connectivity (Fiedler value) — proxy for graph partition risk
- `spectral_hash`: SHA256 of the sorted top-k eigenvalue vector — structural fingerprint
- `perturbation_norm`: ||Δ(t) - Δ(t-1)||_F — magnitude of structural change this epoch

Incremental update: Δ(t) = Δ(t-1) + ΔΔ where ΔΔ affects only rows/columns of nodes involved in new/removed hyperedges in epoch t. Full recomputation is not required each epoch.

---

## 3. What this does NOT do

- Does not remove or deprecate existing binary `LinkRecord` or `GraphEdge` — hyperedges are additive
- Does not require any existing code to change — `vertex_membership` and `hyperedge_members` start empty and grow only when `HyperEdge` objects are added
- Does not implement any query, classification, or learning algorithm — those are analytics layers built over this substrate
- Does not specify hyperedge ECU attribution (deferred to CDL — see §4)

---

## 4. Deferred to CDL

The following require governance decisions before implementation:

- **Hyperedge ECU attribution**: how is ECU credited across co-authors in a `co_authorship` hyperedge? (split equally? stake-weighted? order-weighted?) — requires a CDL
- **Panel hyperedge quorum rules**: what constitutes a valid `panel` hyperedge — minimum degree, agent diversity requirements? — likely extends CDL-V3 diversity floor
- **Spectral hash as epoch commitment**: including `spectral_hash` in the epoch consensus record is a protocol change — requires a CDL

---

## 5. SIM required before activation

- **SIM-HYPEREDGE-01**: calibrate hyperedge weight function W(e) — stake-sum vs. stake-product vs. stake-harmonic-mean — for stability of Laplacian spectrum
- **SIM-SPECTRAL-01**: validate that λ₂ provides useful partition-risk signal on simulated ILC graph topologies; determine noise floor and false-positive rate

---

## 6. Consequences

### Accepted
- `HyperEdge` dataclass added to `ilc_core/types.py` — zero behavioral change, purely additive
- Two sparse dicts added to `EpistemicGraph` — start empty, grow when hyperedges are added
- All n-ary group relationships in ILC now have a natural storage surface
- Laplacian analytics, spectral clustering, random walks become possible without further substrate changes

### Rejected alternatives
- **Model all group relations as binary**: rejected because group structure is lost and unrecoverable; the mathematical properties (Laplacian, spectral analysis) require the actual hyperedge structure
- **Use a hyperedge-specific database**: rejected because it would fragment the graph store; LMDB is adequate at testnet scale and the sparse dict approach scales cleanly

---

## 7. Related
- ADR-0030: Node Embedding Substrate (embeddings are the query interface over this substrate)
- ADR-0031: Subgraph Homomorphism Query Contract (HyperEdgeRecord extends gRPC response)
- CDL (TBD): Hyperedge ECU Attribution
- CDL (TBD): Spectral Hash Epoch Commitment
- SIM-HYPEREDGE-01, SIM-SPECTRAL-01
- Glossary: Hypergraph / Simplicial Complex, Epistemiological Holon, Subgraph Homomorphism Invariant (docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md §5)
