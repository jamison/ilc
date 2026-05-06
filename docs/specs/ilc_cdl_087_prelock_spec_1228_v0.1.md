# ILC CDL-087 Prelock Spec 1228 v0.1

**CDL number:** CDL-087
**Title:** Canonical Fetch Distribution Policy
**Status after this phase:** OPEN / PRELOCKED
**Phase:** 1228
**Date:** 2026-05-06
**Prelock token:** `cdl_087_prelock_committed_phase_1228`
**Non-ratification token:** `cdl_087_not_ratified_phase_1228`
**Basis:** `cdl_087_canonical_fetch_distribution_policy_opened_phase_1227`

---

## 1. Prelock Statement

Phase 1228 prelocks CDL-087 by resolving the Q1-Q5 deliberation agenda opened
in Phase 1227. CDL-087 remains open. This phase does not ratify CDL-087, does
not mutate the CDL register, does not amend CDL-077, does not implement runtime
code, and does not authorize public launch, public repository publication,
public release artifact distribution, v0.2 signing, or release-key generation.

CDL-087 ratification remains gated behind SIM-FETCH-01 and the ratification
conditions in Section 9.

```text
cdl_087_prelock_committed_phase_1228
cdl_087_not_ratified_phase_1228
```

---

## 2. Terminology Lock

CDL-087 uses the existing ILC node-disambiguation canon.

| Term | Meaning |
|------|---------|
| **Graph Node** or **artifact node** | A content-addressed epistemic object in the ILC hypergraph, for example a truth primitive, CDL, ADR, lineage receipt, or checkpoint artifact. This follows `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md`, where unqualified "Node" means Graph Node. |
| **Serving peer**, **host**, or **operator instance** | Network software that may store, mirror, or serve artifact content. This is not a Graph Node. |
| **Artifact CID** | The content identifier for the requested Graph Node or artifact. |

Bare "node" must not be used for serving infrastructure in CDL-087 artifacts.
The policy governs how serving peers handle artifact availability; it does not
place obligations on Graph Nodes themselves.

---

## 3. Q1 Resolution: High-Centrality Tier Definition

CDL-087 prelocks a three-tier artifact structure.

| Tier | Artifacts | Service expectation |
|------|-----------|---------------------|
| **Tier A** - canonical public infrastructure | Genesis root artifacts; ADR-0004 truth primitives; accepted CDLs and ADRs; signed manifests; lineage receipts; CDL-086 release artifacts; bootstrap bundles; epoch/checkpoint roots | Must be eligible for caching, mirroring, and snapshot distribution as Tier A infrastructure. A serving peer or operator instance that advertises Tier A artifact availability must either serve verifiable content, return a bounded circuit-breaker response, or provide a verifiable fresher-peer/snapshot hint when such hinting is implemented. No universal service obligation is created for every serving peer, and Graph Nodes do not advertise themselves. |
| **Tier B** - hot operational content | Recent epoch deltas; projection snapshots; agent bootstrap indexes | Cache-opportunistic; expected to be widely available but not guaranteed at every serving peer. |
| **Tier C** - tail content | All other fetchable content not in Tier A or B | Fetchable if available from serving peers; no infrastructure-grade service expectation. |

Tier A must include the exact artifact list above. Additional Tier A inclusions
require a future CDL amendment, not operator discretion.

Serving Tier A content is intended to route through CDL-078 routing reputation
and CDL-060 centrality paths. That operator incentive loop is not claimed as
fully implemented here: current serve-event code credits the served `node_id`
(the CID of the served Graph Node), not clearly the serving operator or agent
identity. That ambiguity is routed to Phase 1229 through the incentive
projection requirement in Section 7.

---

## 4. Q2 Resolution: Caching and Staleness Guarantees

Staleness is verified by lineage and epoch proof, not wall-clock freshness.

| Artifact class | Caching rule |
|----------------|--------------|
| Content-addressed immutable Tier A artifacts | Cache indefinitely once hash and lineage verify. No expiry is required. Eviction is operator-local resource management only. |
| Mutable indexes and manifests at the Tier A/B boundary | Cache is valid for the current epoch sequence number. A served index is stale if the epoch counter has advanced without the serving peer receiving the update. |
| Tier C tail content | No mandatory caching; opportunistic only. |

A served artifact is fresh if its lineage proof chain resolves back to the
immutable Genesis domain anchor and the epoch sequence number in the artifact is
less than or equal to the serving peer's current epoch head. Wall-clock TTLs are
not a constitutional staleness criterion.

The following numeric values are provisional candidate defaults until
SIM-FETCH-01 and must not be ratified as constitutional policy in this prelock:

| Candidate default | Value |
|-------------------|-------|
| Minimum propagation window for Tier A updates | `provisional: 2 validation epochs` |
| Maximum serve-lag before a serving peer should route to a fresher peer | `provisional: 4 validation epochs` |

---

## 5. Q3 Resolution: Minimum Bootstrap Snapshot Format

A conforming bootstrap snapshot is a Genesis-rooted pull artifact with a
verifiable lineage chain. It must contain all fields below.

| Field | Type | Notes |
|-------|------|-------|
| `snapshot_manifest` | object | Top-level envelope. |
| `genesis_domain_hash` | hex string | Genesis v0.1 root envelope hash; must match the immutable Genesis domain anchor. |
| `snapshot_epoch` | integer | Epoch sequence number at which the snapshot was produced. |
| `artifact_list` | array | Each entry has `{cid, sha256, tier, artifact_kind}`. |
| `lineage_proof_chain` | array | Ordered hash references from snapshot root back to the Genesis domain anchor. |
| `epoch_checkpoint_range` | object | `{from_epoch, to_epoch}` range covered by this snapshot. |
| `authority_refs` | array | CDL/ADR references establishing the authority chain for included artifacts. |
| `graph_projection_export` | object or null | Optional agent graph projection export for the snapshot epoch range. |

Verification rule: any serving peer receiving a bootstrap snapshot must
recompute the SHA-256 of each artifact and verify that the lineage proof chain
resolves to the immutable Genesis domain anchor. A snapshot that fails
verification must be rejected. The serving peer is not penalized unless it
repeatedly serves invalid snapshots, which remains circuit-breaker territory.

Bootstrap snapshots are pull artifacts. Any mirror may serve them. No trusted
push or signed delivery from a specific authority is required because the
lineage proof chain provides content-addressed verifiability.

---

## 6. Q4 Resolution: Required Observability Signals

Observability is aggregate and privacy-minimized. Per-requester behavioral
dossiers are not required and must not be produced as mandatory CDL-087 output.
Reputation must remain derived from useful graph/network behavior, not become
surveillance infrastructure.

Serving peers must expose the following signals before any future fetch
admission CDL ratification is permitted.

| Signal | Unit | Notes |
|--------|------|-------|
| `fetch_requests_by_tier` | count/epoch | Bucketed by Tier A/B/C; no per-requester breakdown. |
| `want_have_hit_rate` | ratio | WANT-HAVE probe hits vs. total probes. |
| `want_have_miss_rate` | ratio | WANT-HAVE probe misses. |
| `want_block_success_count` | count/epoch | Successful WANT-BLOCK fetches served. |
| `want_block_error_404` | count/epoch | Not-found responses. |
| `want_block_error_429` | count/epoch | Rate-limit circuit breaker activations. |
| `want_block_error_400` | count/epoch | Malformed request rejections. |
| `cache_hit_rate_tier_a` | ratio | Tier A cache hits vs. Tier A fetch attempts served. |
| `bytes_served_by_tier` | bytes/epoch | Bucketed by Tier A/B/C. |
| `non_cacheable_request_volume` | count/epoch | Requests for non-cacheable content. |
| `circuit_breaker_activations` | count/epoch | CDL-077 rate-limit triggers. |
| `serve_events_credited_cdl_078` | count/epoch | Serve events that fed CDL-078 reputation/CDL-060 centrality. |

Collection interval is one validation epoch. Output format is JSON with
`sort_keys=True`; epoch sequence number is the protocol-time axis. Wall-clock
timestamps are not protocol signals.

These signals are per-serving-peer aggregates. Individual requester identities
must not appear in mandatory observability output. If a future CDL requires
per-requester metrics for abuse detection, it must open separately and justify
the privacy trade-off.

---

## 7. Incentive Hypergraph Slice

CDL-087 is being prelocked against an incentive architecture that is partially
present in the constitutional canon but not yet cleanly projected as a named
machine-native slice.

### Present in Genesis candidate graph

| Graph Node / artifact | Incentive role |
|-----------------------|----------------|
| `policy:genesis_accrual_governor` | L3 economic policy - governs ECU accrual rate. |
| `policy:genesis_theta_hard_0_05` / `policy:genesis_theta_soft_exp_minus_3` | L3 economic policy - provenance decay thresholds. |
| `policy:provenance_decay_alpha_0_45` | L3 provenance decay alpha from CDL-084. |
| ADR-0008, ADR-0012, ADR-0023, ADR-0028, ADR-0031 | L2 governance/economics spine. |
| CDL-081, CDL-083, CDL-084 | L4 hyperedge ECU attribution, panel quorum, provenance decay. |
| ADR-0029, ADR-0030, ADR-0032, ADR-0033, ADR-0035 | L4 morphogenic/economic overlay. |

### Not yet promoted or cleanly projected in the current Genesis incentive slice

These surfaces exist in the constitutional canon or codebase but are not yet
cleanly projected as a named incentive slice in the Genesis graph.

| Surface | Why it matters for CDL-087 |
|---------|----------------------------|
| CDL-060 centrality-delta gossip | Carry mechanism for serve-event centrality credit. |
| CDL-077 WANT-HAVE/WANT-BLOCK pull fetch | Pull protocol CDL-087 supplements. |
| CDL-078 relay incentive | Routing reputation path CDL-087 organic incentives depend on. |
| CDL-079 bootstrap bundle fetch | Tier A bootstrap artifact delivery mechanism. |
| CDL-087 | Opened in this window; prelocked here; not yet ratified. |
| Reputation adjunct contract (Phase 345) | Lifecycle/graph-history reputation basis. |
| CDL-V1 temporal decay | Reputation/centrality damping surface. |
| Serving-peer vs. served-Graph-Node centrality edge | Distinct edge type needed to encode "serving peer delivered artifact X" vs. "Graph Node X is central"; currently conflated in runtime. |

Required carry-forward token:

```text
fetch_incentive_hypergraph_slice_projection_required_phase_1229
```

Phase 1229 must expose this fetch/incentive subgraph as a named projection
slice adjacent to `economic_flow_graph` and `runtime_binding_graph`, or
explicitly record why the projection is safely deferred. CDL-087 ratification
cannot claim organic incentive coverage until that slice is resolved or
explicitly deferred with evidence.

---

## 8. Advertisement and Privacy Mechanics

CDL-087 preserves the pull-dominant dissemination architecture.

1. **Pull-dominant with soft push-signals:** CDL-076 allows lightweight
   announcement gossip only: Graph Node `node_id`, primitive type, agent, epoch,
   and CDL version. It excludes full-payload push. Content fetch is deferred to
   CDL-077.
2. **CID-specific WANT-HAVE/WANT-BLOCK:** a requesting agent asks a specific
   serving peer whether it has CID X, then asks for CID X via WANT-BLOCK. Under
   current CDL-077, the requester knows which serving peer it asked and the
   serving peer sees the `requester_id`. Per-CID, per-peer visibility exists at
   the direct fetch layer.
3. **No mandatory public inventory:** serving peers are not required to publish
   a global map from artifact CID to serving peer identity. CDL-060/CDL-039
   constraints preserve opaque channels, bounded fanout, and non-inferrable
   cluster membership.
4. **Tier A advertisement is class-level or CID-specific:** a serving peer may
   advertise that it mirrors Tier A content as a class-level capability, or
   respond to a CID-specific WANT-HAVE probe. CDL-087 does not require
   broadcasting a full Tier A inventory.
5. **Unlinkability deferred:** stronger unlinkability, meaning hiding which
   serving peer served which artifact to which requesting agent, belongs to
   future L4 onion routing / SURB work. CDL-087 does not claim to provide
   unlinkability.

The correct CDL-087 privacy statement is: no global public inventory or
universal service mandate now; direct fetch peers remain visible at the CDL-077
layer until L4 privacy routing exists.

---

## 9. Ratification Conditions

CDL-087 may not ratify until all six conditions below are satisfied or an
explicit future CDL records a narrower safe deferral.

1. SIM-FETCH-01 passes, demonstrating actual fetch pressure distribution by
   tier, cache hit rates under realistic agent behavior, and high-centrality
   serve profiles consistent with the Tier A/B/C classification.
2. Tier A/B/C artifact classification is implemented and observable in at least
   one production-candidate serving peer.
3. Bootstrap snapshot format is implemented and verifiable against the
   immutable Genesis domain anchor.
4. Required observability signals from Section 6 are emitted by at least one
   production-candidate serving peer and collected for at least one SIM window.
5. CDL-077 static rate limiter remains active and unmodified throughout the
   parallel operation window; no unlimited fetch path exists in regression
   tests.
6. `fetch_incentive_hypergraph_slice_projection_required_phase_1229` is either
   resolved, with the incentive slice machine-visible in the agent graph
   projection runtime and audited against the serving-peer vs.
   served-Graph-Node edge distinction, or explicitly deferred with recorded
   evidence of why projection coverage is not required for safe CDL-087
   ratification.

---

## 10. Q5 Resolution: CDL-077 Relationship and Non-Bypass Rule

CDL-087 supplements CDL-077 without amendment.

- CDL-077 remains the narrow pull protocol and circuit breaker: WANT-HAVE probe,
  WANT-BLOCK fetch, and rate limiting.
- CDL-087 defines the caching, mirroring, snapshot, advertisement, privacy, and
  observability layer that reduces legitimate Tier A fetch pressure and routes
  it to caches rather than live peers.
- CDL-087 does not create a new incentive structure. It records the intended
  organic path through CDL-078 and CDL-060 and routes the unresolved
  serving-peer credit ambiguity to Phase 1229.
- A future admission/reputation CDL may be opened only after SIM-FETCH-01
  demonstrates that the CDL-087 distribution layer is insufficient and the
  structural objections in Phase 1222 Section 8 are resolved.

```text
transport_abuse_circuit_breaker_not_final_scaling_policy
```

CDL-077's WANT-BLOCK rate limiter must remain active until all six ratification
conditions are satisfied and a separate ratification phase is executed. CDL-087
prelock does not supersede or weaken the circuit breaker.

---

## 11. Core Framing Lock

```text
cdl_087_pull_first_availability_not_service_mandate
```

CDL-087 establishes pull-first, verifiable canonical availability for Graph
Nodes (content-addressed epistemic objects). It does not constitutionalize a
top-down universal service mandate for serving peers, hosts, or operator
instances. Serving useful canonical content is intended to route through
CDL-078 routing reputation and CDL-060 centrality score paths; however, whether
the serving peer (not the served Graph Node) receives that credit is an open
runtime ambiguity recorded in the prelock and routed to Phase 1229. CDL-077
static circuit breakers remain active as the abuse floor. CDL-087 supplements
the fetch layer by defining the caching, mirroring, and snapshot infrastructure
layer that makes Tier A content cheap and verifiable to access without creating
unpriced service obligations. Availability advertisement is class-level or
CID-specific; no global artifact-to-peer inventory is required. Direct fetch
peer visibility at the CDL-077 layer is acknowledged; stronger unlinkability is
deferred to future L4 privacy routing work.

---

## 12. Non-Claims

This prelock does not:

- ratify CDL-087;
- mutate the CDL register;
- amend CDL-077;
- implement runtime code;
- deprecate or weaken static rate limiting;
- open a reciprocal scoring CDL;
- authorize public launch;
- authorize public repository publication;
- authorize public release artifact distribution;
- authorize external contributor onboarding;
- authorize v0.2 signing or release-key generation.

