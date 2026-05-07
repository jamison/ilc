# ILC L3 Sidecar Infrastructure Spec 1237 v0.1

**Phase:** 1237
**Status:** Spec-level boundary committed; runtime implementation pending Fix1 authorization
**Date:** 2026-05-07

```text
l3_sidecar_infrastructure_spec_committed_phase_1237
l3_sidecar_runtime_implementation_pending_fix1_authorization
```

This specification resolves `l3_sidecar_infrastructure_spec_required_window_1225_plus`
at spec level. It defines the read-only L3 sidecar boundary for consuming Phase
1229 graph projections. It does not authorize runtime implementation, sidecar
network serving, UI implementation, ILC protocol participation, CDL mutation, or
any write path into an ILC node.

The implementation expansion plan is recorded separately at:

```text
docs/specs/ilc_phase_1237_sidecar_query_runtime_expansion_plan_v0.1.md
phase_1237_sidecar_query_runtime_expansion_plan_committed
```

## 1. Boundary definition

The L3 sidecar is a read-only external consumer of canonical graph projection
output. It is not an ILC node, not a serving peer, not a gossip participant, not
a CDL authority, and not a consensus participant. It has no stake, no AgentID,
no ECU balance, and no authority to affect finality, settlement, routing, fetch
admission, validator eligibility, or governance outcomes.

The sidecar does not participate in the ILC protocol. It may compute local views
over already-produced projection artifacts, but those views are derived
observability products, not protocol state. A sidecar failure, omission, or local
display disagreement must not affect any canonical ledger, graph, epoch,
consensus, or economic result.

## 2. Consumption interface

The primary source is the Phase 1229 graph projection runtime:

```text
agent_graph_projection_runtime_1229.v0.1
```

The sidecar consumes output from:

```text
project_graph
export_projection_json
export_projection_ndjson
```

The sidecar consumes canonical JSON or NDJSON projection output. It does not read
raw ledger records, raw gossip messages, consensus internals, validator stores,
CDL registers, or mutable node state directly. The ILC node and its canonical
projection runtime remain the source of truth.

The sidecar consumption contract is projection-shaped:

- `metadata` identifies projection type and runtime version;
- `nodes` contains normalized canonical graph node records;
- `edges` contains normalized directed graph edges;
- `hyperedges` contains normalized hyperedge records with sorted members;
- `metrics` contains deterministic projection metrics, including
  `degree_by_node`, `node_count`, and `hyperedge_order_by_id`;
- `bounds` records the `ProjectionBounds` applied during projection; and
- `filters` records the projection filters supplied by the caller.

Future sidecar runtime phases must consume this projection contract rather than
inventing a parallel raw-graph read path.

## 3. Privacy constraints

The sidecar may expose only information already present in public projection
artifacts. It must not infer, enrich, deanonymize, or display individual agent
identity beyond what the projection explicitly makes public.

Serving-peer identity nodes must be aggregated or anonymized before external UI
exposure. Aggregate observability signals are acceptable. Per-agent serving
pressure, hidden serving-peer identity, validator identity, and consensus quorum
membership are not acceptable external display fields.

The sidecar must not expose CDL-039 opaque channel fields. It must not convert
opaque-channel metadata, fetch traces, transport metadata, operator-local logs,
or network timing artifacts into public identity claims. Privacy-preserving
projection boundaries are inherited from the projection producer; the sidecar is
not allowed to weaken them.

## 4. Visualisation posture

Agent-facing views over canonical graph structures are permitted when they
remain faithful to the projection artifact. Suitable agent-facing views include
epistemic graph neighborhoods, node provenance, CDL lineage, runtime binding
relationships, economic-flow projections, branchial convergence summaries, and
fetch-incentive hypergraph slices.

Human-facing visualization is allowed only if it preserves the privacy
constraints in Section 3. A human UI must not imply authority, finality,
validator identity, serving-peer identity, or quorum membership that is not
public in the projection. It must not present local sidecar query results as
canonical protocol decisions.

The sidecar must not infer or display consensus quorum membership or validator
identity. Any quorum, finality, or validator information visible in a sidecar
view must come from an explicitly public projection artifact and must remain
read-only.

## 5. Mutation prohibition

The sidecar has no mutation authority and no write path to any ILC runtime. A
sidecar API, if implemented later, must be read-only by construction.

The sidecar must not write claims, refutations, votes, governance actions,
settlement records, fetch records, routing reputations, graph nodes, graph
edges, hyperedges, ledger records, event-log entries, consensus messages, or CDL
entries. It must not submit material to a node on behalf of a user. It must not
trigger finality, epoch closure, validator admission, fetch admission, or
economic settlement.

User feedback collected by a sidecar is external to ILC. It is not a claim, not
a refutation, not a governance action, not a quorum input, and not an ILC
protocol message unless it is separately submitted through a canonical ILC
runtime path in a future authorized phase.

## 6. Deployment model

The sidecar may be deployed in any of these read-only shapes:

- subprocess consuming projection NDJSON via stdout or pipe;
- in-process module called by local test/dev tooling;
- separate service polling a read-only projection endpoint; or
- local visualization process loading a bounded projection artifact.

In all deployment shapes, the ILC node remains the source of truth. The sidecar
does not become a node, serving peer, or protocol actor by being co-located with
one. If a future deployment uses a network service, that service must be scoped
as a read-only projection consumer and must receive separate authorization for
authentication, rate limits, privacy boundaries, and operational exposure.

The base Phase 1237 spec does not authorize network serving, service discovery,
authentication policy, UI publication, public release distribution, or
production sidecar claims.

## 7. Future runtime phase inputs

Future sidecar runtime phases should consume these projection types by default:

```text
authority_graph
claim_composition_graph
provenance_graph
runtime_binding_graph
economic_flow_graph
branchial_convergence_graph
repo_hypergraph
fetch_incentive_hypergraph_slice
```

Those values are inherited from `PROJECTION_TYPES` in
`agent_graph_projection_runtime_1229.v0.1`.

Refresh cadence should be caller-selected and bounded:

- per validation epoch for epoch-linked observability;
- per N epochs for lower-cost monitoring;
- on-demand for local developer and audit workflows; and
- never based on sidecar-local wall-clock authority for protocol state.

Future sidecar query runtimes should start from the Phase 1229 defaults:

```text
DEFAULT_MAX_NODES = 500
DEFAULT_MAX_EDGES = 1500
DEFAULT_MAX_HYPEREDGES = 500
DEFAULT_MAX_DEPTH = 4
DEFAULT_MAX_PATHS = 100
DEFAULT_MAX_BYTES = 10000000
```

The staged runtime prompts are:

```text
docs/antigravity_tasks/antigravity_prompt__phase_1237_fix1_g8_sidecar_query_runtime_skeleton.md
docs/antigravity_tasks/antigravity_prompt__phase_1237_fix2_g8_sidecar_ego_graph_query.md
docs/antigravity_tasks/antigravity_prompt__phase_1237_fix3_g8_sidecar_centrality_metrics.md
docs/antigravity_tasks/antigravity_prompt__phase_1237_fix4_g8_sidecar_convergence_trace.md
docs/antigravity_tasks/antigravity_prompt__phase_1237_fix5_g8_sidecar_dispatcher_integration.md
docs/antigravity_tasks/antigravity_prompt__phase_1237_fix6_g8_sidecar_canonical_export_bundle.md
docs/antigravity_tasks/antigravity_prompt__phase_1237_fix7_g8_sidecar_local_smoke_harness.md
```

Runtime implementation remains pending explicit Fix1 authorization:

```text
l3_sidecar_runtime_implementation_pending_fix1_authorization
```

Until that authorization is issued, this spec is the authoritative Phase 1237
deliverable and no `ilc_core/graph/sidecar_query_runtime.py` runtime is claimed
as present.
