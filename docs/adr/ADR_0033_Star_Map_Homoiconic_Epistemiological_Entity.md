# ADR-0033: Star Map Homoiconic Epistemiological Entity

**Status:** Accepted  
**Date:** 2026-04-21  
**Owner lane:** Codex research / ADR lane

`run_h003_star_map_homoiconic_adr_verdict=accepted`

---

## 1. Context

ILC already has two accepted star-map surfaces:

- ADR-0003 defines the signed, versioned n-gram route index as a low-cost
  routing prefilter.
- ADR-0005 defines observational star-map feeds as append-only event surfaces.

ILC also now has the accepted hypergraph substrate in ADR-0029, including the
idea that a relationship can become addressable and claimable when it is lifted
into a first-class graph entity.

What remained unset was the specific star-map question:

When a star-map expansion produces a navigation result such as a route cluster,
panel result, or other publishable navigation overlay, is that result merely an
ephemeral view, or is it itself a graph node that can receive claims,
refutations, provenance, Popperian review, and later ECU attribution?

This ADR answers that question directly.

---

## 2. Decision

### 2.1 Published star-map navigation results are first-class nodes

Published star-map navigation results are first-class nodes.
For avoidance of doubt: published star-map navigation results are first-class nodes.

When a star-map computation produces a navigation result that is:

- published,
- shared across agents,
- relied upon for downstream routing or evaluation, or
- referenced by later claims,

that result SHALL exist as a first-class graph node rather than as an
untracked transient view.

Private, purely local scratch overlays may remain ephemeral. The conversion to a
graph node occurs at the publication / reliance boundary.

### 2.2 Node type and payload posture

Star-map navigation results use the already-existing runtime node type:

- `Node.type = "star_map"`

This ADR does **not** create a new `NodeType`.

This ADR also does **not** amend ADR-0030's accepted semantic
`content_type` token list. A star-map result may carry:

- `content_type="route_index"` when it is specifically a route-index artifact
- `content_type=None` until a later ADR expands the semantic token set

The architectural point is addressability and claimability, not a new token
surface.

### 2.3 Star-map entity kinds

This ADR authorizes the following star-map result kinds as node-addressable
entities:

- `route_cluster`
- `panel_result`
- `navigation_overlay`

Future star-map result kinds may be added if they preserve the same identity and
claim-form contract.

### 2.4 Identity scheme

The node id for a published star-map entity SHALL be content-addressed from a
canonical payload containing at least:

- `entity_kind`
- `generator_ref`
- `source_artifact_refs`
- `source_node_set_digest`
- `method`
- `parameter_digest`
- `result_payload`
- `epoch`
- `agent_id`

This makes the result reproducible, challengeable, and stable under later
reference. The identity is the navigation result as published, not merely the
underlying source set.

### 2.5 Claim-form contract

A published star-map node SHALL carry enough structure that another agent can:

- identify what was computed,
- identify which sources were used,
- reproduce or contest the computation,
- attach supporting or refuting claims to the result itself.

At minimum the published payload must expose:

- the generator or method reference,
- the source references or source-set digest,
- the result kind,
- the result summary,
- the parameter digest,
- the publication epoch.

This is the minimum claim form that allows the result to enter the normal graph
evaluation path instead of remaining an opaque UI artifact.

### 2.6 Attribution chain

This ADR authorizes star-map results to sit on an attribution chain, but it
does **not** define the ECU formula for them.

The attribution chain is:

`source nodes / source artifacts -> published star_map node -> later claims, refutations, or governance review`

What this ADR grants:

- star-map results can be addressed,
- star-map results can receive claims and refutations,
- star-map results can be reviewed under the Popperian evaluation apparatus,
- star-map results can later participate in ECU attribution once the relevant
  downstream CDL opens.

What this ADR defers:

- the ECU split rule,
- economic weighting across co-authors or panels,
- any new constitutional attribution formula.

The downstream economic lane remains H-CON-01 and adjacent later CDLs.

---

## 3. Interaction Matrix

### 3.1 ADR-0003 remains unchanged

ADR-0003 governs the **route-index artifact**:

- hashed n-gram buckets,
- advisory routing hints,
- low-cost prefilter behavior.

ADR-0033 does not replace or deprecate ADR-0003. It states that when a
navigation result derived from route-index work is itself published as a
reviewable result, that result may become a `star_map` node.

ADR-0003 governs the prefilter artifact. ADR-0033 governs the published
navigation result as an entity.

### 3.2 ADR-0005 remains unchanged

ADR-0005 governs **observational feeds**:

- append-only NDJSON event surfaces,
- topic feeds,
- observation infrastructure.

ADR-0033 does not convert feeds themselves into star-map nodes automatically.
Instead, observational feeds may be one source input to a published star-map
entity. The feed remains a feed; the published navigation result is the node.

### 3.3 ADR-0029 remains unchanged

ADR-0029 governs the **hypergraph substrate** and the star-expansion of a
hyperedge into a `hyperedge_entity`.

ADR-0033 is adjacent but distinct:

- `hyperedge_entity` is a promoted group relationship
- `star_map` is a published navigational result

A star-map node may reference hyperedges or hyperedge entities, but it is not
the same thing as ADR-0029 star expansion and does not amend that substrate.

---

## 4. What This ADR Governs

This ADR governs:

- whether published star-map results are graph nodes
- the node type used for those results
- the minimum identity scheme
- the minimum claim-form contract
- the fact that such nodes may enter the later attribution chain

---

## 5. What This ADR Does Not Govern

This ADR does **not** govern:

- hyperedge ECU attribution mechanics
- panel quorum or diversity law
- gossip or sealed-sender transport
- route-index hashing details from ADR-0003
- observational feed transport from ADR-0005
- any constitutional mutation in the decision log
- any runtime implementation work

Those remain downstream tasks.

---

## 6. Consequences

### Accepted

- Published star-map navigation results are no longer architecturally invisible
- A route cluster or panel result can itself be challenged, cited, and audited
- The graph can represent navigational knowledge as knowledge, not only as a UI
  side effect

### Rejected alternatives

- **Ephemeral-only star maps**: rejected because untracked navigation results
  cannot be challenged or cited
- **Treat every star-map result as a hyperedge entity**: rejected because a
  navigational result is not always a group relationship
- **Defer addressability until ECU law exists**: rejected because provenance and
  challengeability are needed before the economic formula is finalized

---

## 7. Downstream Implications

- H-CON-01 remains the downstream economic lane for attribution mechanics
- H-012 remains blocked on H-CON-01 even though ADR-0033 is now accepted
- Future implementation may publish `star_map` nodes directly from route-cluster
  or panel-result generation once the relevant activation work is authorized

---

## 8. References

- `docs/adr/ADR_0003_Star_Map_Ngram_Route_Index.md`
- `docs/adr/ADR_0005_Star_Map_Observational_Feeds.md`
- `docs/adr/ADR_0029_Hypergraph_Substrate.md`
- `docs/adr/ADR_0030_Node_Embedding_Substrate_and_Content_Typing.md`
- `ilc_core/types.py`
