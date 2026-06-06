# ADR-0035: Homoiconic Type Definition System

**Status:** Accepted — CDL-097 ratified Phase 1528p; implementation authority in place; runtime scaffold is Phase 1529p work; no production activation authorized.
**Date:** 2026-04-28  
**Ratified (direction):** 2026-05-19 (Phase 1387d)  
**Owner lane:** Architecture / ADR lane

`adr_0035_homoiconic_type_definition_system_direction_accepted`
`adr_0035_implementation_deferred_pending_cdl`
`adr_0035_cdl_implementation_authority_in_place_phase_1528p`
`adr_0035_formal_adr_written_phase_1387d`

---

## 1. Context

ILC's knowledge graph has two parallel type systems that are currently expressed
as hardcoded string literals in `ilc_core/types.py`:

**Level 1 — `NodeType` (Literal string):**
```python
NodeType = Literal[
    "genesis", "claim", "refutation", "task", "star_map",
    "proposal", "genesis.schema", "genesis.blob", "hyperedge_entity",
]
```

**Level 2 — `HyperEdge.hyperedge_type` (free string):**
```python
hyperedge_type: str  # "panel" | "co_authorship" | "refutation_coalition" | ...
```

Both levels are defined outside the graph: their rules live in Python source and
prose documentation, not as addressable, claimable graph nodes. This creates a
governance gap:

- Type rules cannot be queried, attributed, or disputed through the graph's own
  machinery
- Amending a type requires a CDL + runtime mutation + deployment
- New `hyperedge_type` values require code changes, not governance actions
- Disputes about whether a hyperedge satisfies its declared type have no formal
  in-system adjudication path

ILC's core thesis is that knowledge and its governance live in the same graph.
Having the type system outside the graph violates that thesis.

A working spec has been maintained at
`docs/specs/ilc_adr_0035_homoiconic_type_definition_system_v0.1.md` since
Window 1102–1109. This ADR records the formal governance verdict on that spec.

---

## 2. Decision

**Accept the homoiconic type definition system as the long-term architectural
target. Implementation is deferred pending a dedicated CDL.**

The target state:

1. Each `hyperedge_type` value becomes a **definition node** in the graph — a
   genesis-class node encoding the rules, attribution behaviour, membership
   requirements, and dispute resolution path for that type.

2. `HyperEdge.hyperedge_type` becomes a **node reference** (ID pointer) rather
   than a string literal, pointing to the definition node for that type.

3. The runtime resolves type semantics by reading the definition node from a
   local cache, not by switching on a string constant.

4. Amendments to what a type means go through the CDL process — the definition
   node is immutable once ratified; amendment requires a new CDL that supersedes it.

5. Disputes about whether a specific hyperedge satisfies its declared type are
   adjudicable by a 7+1 empaneled jury referencing the definition node as the
   authoritative specification.

---

## 3. Three Resolved Questions

Phase 1387b (SIM-GENESIS-COMPILE-02) formally deferred this ADR pending resolution
of three questions. This section records the resolution of each.

### 3.1 Type regress question

**Question:** If type definition nodes are themselves typed, what is the type of
a type definition node? Does this create an infinite regress?

**Resolution:** A small set of **genesis primitives** must remain hardcoded as
the axiomatic floor to stop the regress. The critical primitive is:

| Hardcoded primitive | Rationale |
|---------------------|-----------|
| `type="type_definition"` | Meta-type for all definition nodes; hardcoded to stop the regress |
| `type="genesis"` | Axioms; immutable by definition; cannot be homoiconic |
| `type="claim"` | Fundamental epistemic unit; pre-dates governance machinery |

All other `NodeType` and `hyperedge_type` values are migration candidates. The
type regress stops at `type="type_definition"`, which is itself hardcoded and
not required to reference a definition node.

### 3.2 Relationship to ADR-0030

**Question:** ADR-0030 establishes `content_type` tokens (`"claim"`, `"evidence"`,
`"route_index"`, etc.). Are those tokens the type system, or metadata about it?

**Resolution:** They are different abstractions at different layers and do not
conflict:

- **ADR-0030 `content_type`** is metadata about the semantic category of a node's
  *content* — it governs embedding selection, routing, and future schema validation.
  It operates at the content layer.

- **ADR-0035 type definitions** govern the *behavioral and governance semantics* of
  `hyperedge_type` values — attribution rules, membership requirements, dispute
  adjudication paths. They operate at the graph structure layer.

A definition node itself carries `content_type="type_definition"` (once that token
is added to ADR-0030's accepted list via the relevant CDL). The two systems are
complementary: ADR-0030 handles what content is; ADR-0035 handles how graph
structure behaves.

### 3.3 Popperian claim-form for type-level nodes

**Question:** How do type-level claims (claims about the rules of a type) differ
from instance-level claims (claims about whether a specific hyperedge satisfies
its type) under the Popperian evaluation framework?

**Resolution:** Two distinct claim-form modes apply:

**Type-level claims** target the definition node itself:
- Asserted by: any agent who disputes a type's rules or scope
- Refutation path: CDL amendment process — the only constitutional mechanism for
  changing what a type means
- Jury role: 7+1 empaneled jury adjudicates disputes about whether a CDL amendment
  correctly captures the intended revision
- These are **constitutional** claims, not epistemic claims in the normal sense

**Instance-level claims** target a specific hyperedge instance:
- Asserted by: any agent who disputes whether a specific hyperedge satisfies its
  declared type
- Refutation path: standard Popperian evaluation — submit a refutation node citing
  the definition node as the specification
- Jury role: 7+1 jury empaneled to adjudicate the specific instance, referencing
  the definition node as the authoritative criterion
- These are **epistemic** claims and enter the normal graph evaluation path

Definition nodes are **non-attributable**: they do not participate in REUSE or
CO_AUTHORSHIP attribution. They are infrastructure, not content.

---

## 4. Design Constraints

### 4.1 Bootstrapping floor

The genesis primitives listed in §3.1 remain hardcoded. All other types are
migration candidates.

### 4.2 Definition node properties

A definition node must be:
- `type="type_definition"` (new NodeType, introduced via CDL)
- Genesis-class: declared by a ratified CDL commit; immutable after ratification
- Content-addressed: ID derived from content; silent mutation is detectable
- Non-attributable: does not participate in REUSE or CO_AUTHORSHIP ECU

### 4.3 Compositional primitive basis

Every type definition must be expressible as a composition of the 7 truth
primitives established in ADR-0004:

```
type_semantics = primitive₁ ∘ primitive₂ ∘ ... ∘ primitiveₙ
```

Types that are irreducible (not expressible as compositions) must be flagged
`"irreducible": true`. `commit.epoch` / `EPOCH_BOUNDARY` is the canonical
irreducible type.

Before CDL ratification of any new type:
1. State the `decomposition_recipe` (which primitives, in what order)
2. If the recipe duplicates an existing type, either reject the new type or provide
   a `scope` / `role_schema` parameter formally distinguishing the cases

### 4.4 Retroactivity rule

When a definition node is superseded by amendment:
- Existing hyperedges retain a reference to the definition node valid at their
  creation epoch (snapshot semantics)
- The new definition applies only to hyperedges created after the amendment
  ratification epoch
- No retroactive re-adjudication of settled attribution events

### 4.5 Runtime resolution

- Definition nodes loaded into a local cache at node startup
- Cache invalidated only on CDL ratification events (rare)
- The `settle()` path reads from cache, not from the graph store directly

---

## 5. What This ADR Does Not Govern

- Any runtime implementation — CDL-097 authority is now in place, but the
  default-off runtime scaffold is Phase 1529p work and production activation is
  not authorized
- Initial definition-node instances for specific `hyperedge_type` values
- The ECU formula for type-dispute resolution
- Jury selection procedure for type disputes (separate ADR or CDL annex)
- Production activation of `content_type="type_definition"` beyond the
  CDL-097-governed ADR-0030 token addition

---

## 6. Interaction with Existing ADRs

| ADR | Relationship |
|-----|-------------|
| ADR-0004 | Truth primitives are the compositional basis for all type definitions (§4.3) |
| ADR-0019 | Graph-native governance boundary. ADR-0035 brings type definitions inside that boundary |
| ADR-0021 | Epistemic finality claims. Type-level claims are constitutional; they use the CDL process, not the normal Popperian evaluation path |
| ADR-0029 | Established hypergraph substrate and star expansion. ADR-0035 governs the type of hyperedge, not just its structure |
| ADR-0030 | `content_type` tokens are content-layer metadata. ADR-0035 type definitions are graph-structure-layer governance. Complementary, not conflicting (see §3.2) |
| ADR-0033 | Star-map navigation results as first-class nodes. ADR-0035 may eventually govern the `star_map` NodeType as a definition node once CDL is opened |

---

## 7. Forward Obligations

1. **CDL for `type="type_definition"` introduction** — satisfied by CDL-097
   ratification in Phase 1528p; default-off runtime scaffold remains Phase
   1529p work
2. **Definition node ratification** — existing `hyperedge_type` values must be
   hardened into CDL-ratified definition nodes; prose drafts are in the working spec
3. **`HyperEdge.hyperedge_type` field semantics change** — wire format stays `str`
   (node ID); runtime semantics change; migration guide required
4. **`content_type="type_definition"` token** — satisfied by the CDL-097-governed
   ADR-0030 token addition in Phase 1528p
5. **Jury procedure for type disputes** — procedure spec for §3.3 type-dispute
   adjudication (separate ADR or CDL annex)

---

## 8. Rejected Alternatives

### Option A — Keep hardcoded strings (status quo)
Rejected as long-term target. Hardcoded strings are ungovernable within the
system's own machinery. Every rule change requires code deployment. No in-system
adjudication path for type disputes.

### Option B — Multi-type node fields
Allow `types={"claim", "co_authorship"}` simultaneously. Rejected. Conflates
content identity with ownership mode. Does not solve the governance gap.

### Option C — Ownership as a node attribute flag
Add `is_collectively_owned: bool` to `Node`. Rejected as primary architecture.
Makes ownership implicit rather than governed. Does not extend to non-ownership
hyperedge types.

---

## 9. References

- `docs/specs/ilc_adr_0035_homoiconic_type_definition_system_v0.1.md` — working spec
- `docs/adr/ADR_0004_Truth_Primitives.md`
- `docs/adr/ADR_0019_Graph_Native_Governance_Boundary.md`
- `docs/adr/ADR_0029_Hypergraph_Substrate.md`
- `docs/adr/ADR_0030_Node_Embedding_Substrate_and_Content_Typing.md`
- `docs/adr/ADR_0033_Star_Map_Homoiconic_Epistemiological_Entity.md`
- `ilc_core/types.py`
