# ILC Agent Graph Projection Interface — Scope 1222 v0.1

**Phase:** 1222
**Window:** 1218-1224
**Date:** 2026-05-05
**Status:** SCOPE COMMITTED — implementation deferred to Window 1225+

`agent_graph_projection_interface_scope_committed_phase_1222`

---

## 1. Purpose and Priority

ILC is a knowledge graph for digital agents, not a human dashboard. This interface
produces deterministic bounded projections of ILC graph/hypergraph state for agent
consumption. Human 3D star-map visualizations are L3 sidecar consumers of this interface —
not the canonical surface and not a design input.

**Priority:** agent-native JSON/NDJSON output. Every projected item carries its canonical
source reference so agents can cite, verify, and compose projections without additional
round-trips.

**Substrate:** `EpistemicGraph` in `ilc_core/graph.py` already maintains:
- `nodes: Dict[str, Node]` — full node record including type, claim, ratification state
- `outgoing_edges / incoming_edges` — compatibility lineage edges (`derives_from`)
- `links / outgoing_links / incoming_links` — semantic links (supports, refutes,
  equivalent, depends_on)
- `hyperedges: Dict[str, HyperEdge]` — sparse incidence index
- `vertex_membership` — node → hyperedge set (H^T rows)
- `hyperedge_members` — hyperedge → node set (H columns)

The projection interface is a **read-only bounded query layer** on top of this existing
structure. It does not maintain a separate graph. It does not mutate any canonical
artifact.

---

## 2. Projection Types

Six named projection types. Each projection is deterministic given the same query
parameters and graph state. The same projection type produced twice from the same state
must produce byte-identical output.

### 2.1 Authority Graph

Nodes: genesis, claim, refutation, validator class, CDL/ADR ratification records.
Edges: ratifies, supersedes, derives_from, depends_on.

Purpose: trace the ratification chain from any node back to Genesis v0.1. Agents use
this to verify that a given claim or decision is constitutionally grounded.

Required fields per node: `node_id`, `node_type`, `ratification_state`, `cdl_ref` (if
any), `genesis_lineage_depth`, `source_ref` (commit or file path).

### 2.2 Claim-Composition Graph

Nodes: claim, refutation, revision, link endpoints.
Edges: supports, refutes, equivalent, depends_on, revises.
Hyperedges: co-authorship bundles, multi-author claim groups.

Purpose: show the epistemic structure of a claim domain — what supports it, what refutes
it, how contested it is, which claims it depends on.

Required fields per node: `node_id`, `node_type`, `claim_domain`, `net_support`,
`is_controversial`, `hyperedge_memberships`, `source_ref`.

### 2.3 Provenance Graph

Nodes: PROVENANCE chain members — the path from a downstream claim/reuse event back
through its provenance chain to the originating node.
Edges: provenance_hop (hop index, decay_factor per CDL-084 α=0.45).

Purpose: answer "where does this derive from, and what is the ECU attribution chain?"
Provenance depth is bounded by `PROVENANCE_MAX_DEPTH = 3`.

Required fields per edge: `hop_index`, `decay_factor` (Decimal, `α^(hop+1)`),
`cumulative_attribution_fraction`, `source_ref`.

### 2.4 Runtime-Binding Graph

Nodes: runtime modules (version tokens), CDL/ADR ratification events, phase anchors.
Edges: implements, depends_on, supersedes, activated_by.

Purpose: answer "which runtime module is active for a given protocol feature, and what
constitutional path governs it?" Agents and LLMs performing code review use this to
verify that runtime version tokens are live and constitutionally bound.

Required fields per node: `runtime_version_token`, `governing_cdl`, `activation_phase`,
`module_path`, `source_ref`.

### 2.5 Economic-Flow Graph

Nodes: agent/validator IDs, star nodes, treasury.
Edges: attribution_payout (PROVENANCE/REUSE/CO_AUTHORSHIP), stake_route, fee_route,
ejected_stake_treasury_route.

Purpose: project ECU flow through the epoch settlement layer. Answer "what is the
attribution path for ECU awarded to agent X?" without exposing unbounded ledger state.

Bounds: max_agents = configurable (default 50); single epoch window per query.

Required fields per edge: `event_type`, `ecu_amount` (Decimal), `epoch_id`,
`source_ref`.

### 2.6 Branchial/Convergence Graph

Nodes: state snapshots, branchial equivalence classes, merge points.
Edges: branchial_equivalence, diverges_from, converges_to.
Metrics: `merge_depth`, `divergence_count`, `convergence_point_ids`.

Purpose: answer "where do provenance paths merge or fail to merge?" — the core
branchial convergence question that CDL-085 φ-bound is designed to constrain.

Required fields per node: `equivalence_class_id`, `member_count`,
`phi_bound_ratio` (Decimal — provenance events / node mints in epoch),
`phi_bound_exceeded` (bool), `source_ref`.

---

## 3. Query and Filter Modes

All filters are AND-combined unless `mode: "any"` is specified. All inputs are
validated; unknown filter keys raise `ValueError("unknown_filter_key:<key>")`.

| Filter | Type | Description |
|--------|------|-------------|
| `node_id` | str or list[str] | Include only specified node(s) |
| `ego_radius` | int (1–5) | Nodes within N hops of specified `center_id` |
| `phase_range` | [int, int] | Nodes/edges produced in [min_phase, max_phase] |
| `node_class` | str or list[str] | Filter by NodeType (genesis, claim, refutation, task, …) |
| `edge_type` | str or list[str] | Filter by edge/link type |
| `hyperedge_type` | str or list[str] | Filter by HyperEdge.type |
| `cdl_ref` | str or list[str] | Nodes governed by specified CDL(s) |
| `adr_ref` | str or list[str] | Nodes governed by specified ADR(s) |
| `genesis_lineage` | bool | If true, include only nodes with traceable Genesis lineage |
| `ratification_state` | str | Filter by ratification state token |
| `creator_agent` | str or list[str] | Filter by creator/author agent ID |
| `claim_domain` | str | Filter by claim domain tag |

**Ego query:** `center_id` + `ego_radius` returns the subgraph of all nodes within
N hops of `center_id` across the selected projection type's edge set. Max radius: 5.

**Derivation path query:** `derive_path_from: str, derive_path_to: str` — returns the
shortest path(s) from `derive_path_to` back toward `derive_path_from` via provenance or
authority edges. Max path length: `PROVENANCE_MAX_DEPTH` for provenance queries; 20 for
authority queries.

---

## 4. Output Formats

### 4.1 Deterministic JSON

```json
{
  "projection_type": "<type>",
  "query": { ... },
  "generated_phase": <int>,
  "node_count": <int>,
  "edge_count": <int>,
  "hyperedge_count": <int>,
  "bounds_applied": { "max_nodes": <int>, "max_edges": <int>, "max_depth": <int> },
  "truncated": <bool>,
  "nodes": [ { "node_id": "...", "source_ref": "...", ... } ],
  "edges": [ { "source_id": "...", "target_id": "...", "type": "...", "source_ref": "...", ... } ],
  "hyperedges": [ { "hyperedge_id": "...", "member_ids": [...], "cardinality": <int>, "source_ref": "...", ... } ],
  "metrics": { ... }
}
```

Serialization: `json.dumps(sort_keys=True, allow_nan=False, separators=(",", ":"))`.
No float values for any ECU/Decimal field — serialize as canonical decimal strings.
`source_ref` is required on every node, edge, and hyperedge — omission is a test failure.

### 4.2 NDJSON Stream Mode

Same schema per record, one record per line. Header record first:

```json
{"record_type": "header", "projection_type": "...", "query": {...}, "generated_phase": <int>}
{"record_type": "node", "node_id": "...", "source_ref": "...", ...}
{"record_type": "edge", "source_id": "...", "target_id": "...", "source_ref": "...", ...}
{"record_type": "hyperedge", "hyperedge_id": "...", "source_ref": "...", ...}
{"record_type": "metrics", ...}
{"record_type": "footer", "node_count": <int>, "edge_count": <int>, "truncated": <bool>}
```

Footer must be last. Stream consumers can verify completeness by checking for footer.

### 4.3 Summary Metrics (optional, included in both formats)

| Metric | Description |
|--------|-------------|
| `degree_max` | Maximum node degree (edges + links) in projection |
| `degree_mean` | Mean node degree (Decimal string, 2dp) |
| `hyperedge_cardinality_max` | Largest hyperedge member count |
| `hyperedge_cardinality_mean` | Mean hyperedge cardinality (Decimal string, 2dp) |
| `provenance_depth_max` | Deepest provenance chain in projection |
| `convergence_point_count` | Number of branchial merge points (branchial projection only) |
| `divergence_point_count` | Number of branchial split points (branchial projection only) |
| `phi_bound_ratio_max` | Maximum φ-bound ratio observed in epoch window (Decimal string) |
| `betweenness_top5` | Top 5 node IDs by betweenness centrality — only computed if `metrics: "full"` and node_count ≤ 500 (expensive) |

Betweenness is opt-in and bounded. Default metrics mode is `"basic"` (no betweenness).

---

## 5. Safety Constraints

These are **hard invariants** — not configurable defaults:

| Constraint | Value | Rationale |
|------------|-------|-----------|
| Read-only | Enforced | No canonical artifact mutation permitted |
| `max_nodes` | 1000 (default) | Prevent OOM on unbounded graph dumps |
| `max_edges` | 5000 (default) | As above |
| `max_hyperedges` | 500 (default) | As above |
| `max_depth` | 10 (default) | Prevent deep traversal DoS |
| `max_ego_radius` | 5 | Hard ceiling; cannot be overridden by caller |
| Deterministic sort | Required | All output sorted by canonical key before serialization |
| `sort_keys=True` | Required | `json.dumps` and NDJSON records |
| `allow_nan=False` | Required | No NaN/Infinity in output |
| No float for ECU | Required | All Decimal fields serialized as strings |
| Truncation flag | Required | If `max_nodes/edges/depth` causes truncation, `"truncated": true` in output |

Operator may increase `max_nodes`/`max_edges`/`max_depth` via config — but hard ceilings
apply: max_nodes ≤ 10000, max_edges ≤ 50000, max_depth ≤ 25.

---

## 6. Source References

Every projected item must carry a `source_ref` field. This is the canonical anchor that
allows an agent or human reviewer to verify the item against the repository.

`source_ref` format:
- For graph nodes/edges: `"<commit_hash>:<file_path>:<line_or_record_id>"`
- For CDL/ADR items: `"<commit_hash>:docs/specs/<cdl_filename>"`
- For runtime tokens: `"<commit_hash>:ilc_core/<module_path>"`
- For genesis items: `"<genesis_v0.1_hash>:config/genesis.json:<node_id>"`

A projection without `source_ref` on every item is a malformed projection and fails the
completeness test.

---

## 7. Sidecar Boundary

Human 3D visualization is downstream. The canonical interface is the JSON/NDJSON
projection. Any 3D star-map, XGI rendering, HNX visualization, Three.js scene, D3 graph,
or equivalent human-readable visual is an L3 sidecar consumer that reads the projection
output — it has no schema authority and no semantic input into the projection design.

EVE Online-style maps are visual inspiration only. No schema borrowing, no semantic
mapping from EVE concepts to ILC graph primitives.

This boundary must be stated explicitly in the implementation module docstring.

---

## 8. Implementation Deliverables (Window 1225+)

This scope document governs the following artifacts, to be produced in Window 1225+:

| Artifact | Phase |
|----------|-------|
| `tools/export_ilc_graph_projection.py` | Window 1225+ |
| `tests/test_agent_graph_projection_*.py` | Window 1225+ |

**Minimum tests (Window 1225+ implementation):**

1. `test_authority_projection_is_deterministic` — same query twice → byte-identical output
2. `test_provenance_projection_bounded_by_max_depth` — depth > max_depth truncates; `truncated: true`
3. `test_all_nodes_have_source_ref` — projection output fails if any node/edge missing `source_ref`
4. `test_no_nan_in_output` — all projections pass `json.loads` with `allow_nan=False`
5. `test_read_only_no_graph_mutation` — running any projection does not mutate `EpistemicGraph` state
6. `test_ego_radius_bounded` — ego_radius > 5 raises `ValueError("ego_radius_exceeds_maximum")`
7. `test_ndjson_footer_is_last_record` — NDJSON output always ends with `record_type: footer`
8. `test_decimal_fields_are_strings` — no float in ECU/Decimal fields; serialized as strings
9. `test_branchial_projection_records_phi_bound_ratio` — φ-bound ratio present in branchial output
10. `test_truncation_flag_set_when_max_nodes_exceeded` — over-limit projection sets `"truncated": true`

---

## 9. Constitutional Routing

No CDL or ADR mutation required for the projection interface itself — it is read-only
infrastructure. However, if projection outputs are later used as evidence in CDL
deliberations or ratification ceremonies, the projection format and source_ref schema
should be cited in the relevant evidence bundle.

If a CDL is later opened to govern agent-facing API surfaces (e.g., a "canonical export
format" CDL), this scope document should be cited as the design basis.

---

## 10. Open Questions

1. **Betweenness centrality algorithm** — exact algorithm and Decimal-safe implementation.
   Current best candidate: Brandes algorithm adapted for Decimal weights. Requires SIM
   validation before becoming a default metric.

2. **Hyperedge projection geometry** — for branchial/convergence graph, the incidence
   index (H^T rows, H columns) is already maintained. Projection onto a 2-graph (pairwise
   cliques per hyperedge) vs retaining true hyperedge representation in output. Recommend
   retaining hyperedge representation natively — clique expansion loses cardinality signal.

3. **CDL governing export format** — if the projection output format becomes an
   inter-agent protocol surface (agents sending projections to each other), it may require
   a CDL for stability guarantees. Defer until at least one production consumer exists.

---

## Token

`agent_graph_projection_interface_scope_committed_phase_1222`
