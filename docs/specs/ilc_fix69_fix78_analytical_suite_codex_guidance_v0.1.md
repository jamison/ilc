# Combined Codex Guidance: Fix69 → Fix78 + Post-Repair Analytical Suite

**PUBLIC_RC_EXCLUDE: local Atlas graph repair completion, gap hardening, and diagnostic re-run suite**

**Version:** v0.4 — revised per Codex review (phase naming, traversal semantics, Fix45-R scope, sequence reorder, output-manifest discipline, Fix72a safe-writer semantic allowlist)

---

## Preamble — Current State

Fix71 is closed at `29127a5e` and its gap report is committed at `d3219fd2`. The Fix69 antigravity prompt already exists at `docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix69_g10_orphaned_policy_target_sim_rewiring.md` and validates. After gap-report file registration, the unified LMDB is:

| Metric | Value |
|---|---|
| LMDB path | `out/genesis_base_graph_v0.4_unified.lmdb` |
| Nodes | 16,894 |
| Edges | 94,167 |
| Dangling edges | 0 |
| Missing edge IDs | 0 |
| Phase orphans | 0 |
| CLASSIFIED_BY public-path fan-in | 1 |

**What changed since the last analytical passes (Fix43/Fix56):**

| Fix | Change | Scale |
|---|---|---|
| Fix67 | Removed per-file public-path CLASSIFIED_BY spokes | −199 edges |
| Fix68 | Wired orphaned phase nodes into lineage chain | +528 edges |
| Fix70 | Established CDL↔ADR cross-family authority lattice | +significant cross-family GOVERNS/REFERENCES_AUTHORITY links |
| Fix71 | Classified all `ilc_core/` source files with semantic edges | +4,044 IMPLEMENTS/EVIDENCES/REFERENCES_AUTHORITY edges |

Fix56 (the last spectral measurement) saw the authority-only projection at λ₂ = 0.0 with 1,224 isolated nodes in a projection of only 1,515 nodes / 318 edges. Fix71 added 4,044 semantic edges, the majority connecting `ilc_core/` runtime modules into the CDL/phase/authority lattice via `IMPLEMENTS`. Those runtime nodes are not necessarily inside the strict `genesis_core_star_map` authority-only projection, so Fix71 should be evaluated with an additional authority-binding projection that includes authority nodes plus runtime nodes that implement or reference them.

Fix71 also produced a gap report (`docs/specs/ilc_fix71_manual_read_gap_report_v0.1.md`, ledger: `docs/specs/ilc_fix71_manual_read_gap_ledger_v0.1.json`) capturing 899 gap-note rows across 587 source paths. These are integrated into the execution sequence below.

**API rule (applies to every step in this document):**
- Use `writer.store.iter_nodes()` and `writer.store.iter_edges()` for all data access
- Do not call `writer.inspect()` expecting node/edge lists — it returns count summaries only
- Node ID field: use `n.get("candidate_id") or n.get("node_id")` — bare `n["node_id"]` will silently undercount or raise
- Edge fields: prefer helpers that read `source`/`target` first and fall back to `src`/`tgt`; several historical rows carry both forms
- All LMDB counts are measured at execution time — never rely on counts quoted in planning docs

**Required clauses for every phase in this sequence:**
1. Live LMDB counts are measured at execution time via `iter_nodes()`/`iter_edges()`
2. `out/` artifacts are not committed unless explicitly small and policy-approved; every uncommitted `out/` artifact must be represented by a committed digest/manifest row
3. Committed `docs/specs/`, `docs/phases/`, and `tests/` files are registered in LMDB before phase closure
4. Manual-read evidence is required wherever semantic edges are added — no speculative edges

---

## Overall Execution Sequence

```
Fix71 closed (29127a5e) + gap report committed (d3219fd2)
  ↓
Fix69    ← patch existing prompt; structural orphan repair (policy/target/sim)
  ↓
Fix72    ← read-only measurement suite: Fiedler, baseline, spectral/PageRank,
           percolation analysis, authority SIM battery (NO edge writes except
           registering output docs)
  ↓
Fix72a   ← safe-writer edge-type semantic allowlist (central write-path hardening;
           no LMDB graph-content mutation)
  ↓
Fix73    ← runtime-to-governance trace study (read-only)
  ↓
Fix74    ← P1+P1b: pre-public-RC code hardening + doc cleanup (18 items)
  ↓
Fix75    ← P2: numeric/determinism classification sweep (149 rows)
  ↓
Fix76    ← P3: package/build/content-hash audit (66 rows)
  ↓
Fix77    ← P4: crypto-boundary map (48 rows)
  ↓
Fix78    ← P7: LMDB lifecycle/alias cleanup (14 rows)
```

**Sequencing rationale:** Fix72 measurement runs immediately after Fix69 (the last structural repair) before any code/doc phases (Fix74+) add new support nodes and perturb counts. Fix72a lands immediately after Fix72 because it is central write-path hardening: Fix72's own closeout registration is the last acceptable safe-writer invocation before the semantic allowlist is installed. Every analytical report in Fix72 and Fix73 must state: "post-Fix69 LMDB state." If P1 urgency requires Fix74 to run before Fix72, every analytical report must instead state "post-Fix74 LMDB state" — the two states must not be conflated.

**P5/P6 rows (452 total):** Not a work queue. Confirmed working default-off guards archived in the ledger as permanent release-gate assertions. No Fix phase.

**P8 (task queue durability, 2 rows):** Deferred to a future product planning window. No Fix phase.

---

## Fix69 — Patch Existing Prompt, Then Execute

**The Fix69 prompt already exists and validates.** Do not draft a replacement. Apply the following patches to `docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix69_g10_orphaned_policy_target_sim_rewiring.md` before execution:

### Required patches

**1. §0a input tokens — add `fix71_complete`:**

Current:
```
fix68_complete
```

Patch to:
```
fix68_complete
fix71_complete
```

**2. Required Inputs — add gap report:**

Add to the direct-read list:
```
- `docs/specs/ilc_fix71_manual_read_gap_report_v0.1.md` — Fix71 gap report;
  Track B and Track C nodes in the gap ledger may already be partially addressed
  or newly surfaced here; cross-reference before computing the live queue
```

**3. Track B — remove SOURCE_TREE_MEMBER as a fallback:**

Current Track B language includes `SOURCE_TREE_MEMBER` as a valid edge type for `target:*` nodes. Remove it. Approved edges for target nodes are:
- `CARRIES_FORWARD → phase`
- `EVIDENCES → invariant/phase/CDL`
- `TESTS → phase/module`
- `IMPLEMENTS → CDL`
- If no semantic relationship is determinable: flag as `support_leaf_no_wiring_required` in the audit report — do not write a speculative edge

**4. Pre-execution claim table — replace hardcoded counts with live-measure instruction:**

Current table has hardcoded Fix66 queue of 10 entries. The live queues are larger now. Replace the count rows with:

| Claim | Check | Expected |
|---|---|---|
| Live policy orphan count | LMDB scan at execution time | ~235 (recompute live) |
| Live target orphan count | LMDB scan at execution time | ~668 (recompute live) |
| Live sim/non-repo orphan count | LMDB scan at execution time | ~116 (recompute live) |
| Fix66 residual queue exists | `ilc_fix66_residual_audit_queue_v0.1.json` | present |
| Fix71 gap report exists | `ilc_fix71_manual_read_gap_report_v0.1.md` | present |

All counts must be confirmed live — do not assume prior estimates are current.

**5. Node field access — update all Python examples:**

Replace any bare `n["node_id"]` with `n.get("candidate_id") or n.get("node_id")` to avoid silent undercounting or key errors.

### Fix69 execution notes (unchanged from existing prompt, confirmed)

Work in batches of 10–15. Dry-run (`dry_run=True`) before every live write. Audit report at `docs/specs/ilc_fix69_orphan_rewiring_audit_v0.1.json`. Register all output files in LMDB before closure. One commit.

```
fix(atlas): Fix69 orphan rewiring — wire policy/target/sim orphans to authority lattice
```

---

## Fix72 — Read-Only Post-Repair Measurement Suite

**Required token:** `fix69_complete`

**This phase is entirely read-only against LMDB edge/node data.** The only LMDB mutations permitted are registering committed output documents (walkthroughs, JSON reports) as phase nodes. No `put_nodes()`, no `put_edges()`, no `remove_edges_by_semantic()` against graph content.

**Output tokens to emit:**
```
fix72_fiedler_rebaseline_complete
fix72_whole_graph_baseline_complete
fix72_spectral_pagerank_complete
fix72_percolation_analysis_complete
fix72_authority_sim_battery_complete
fix72_complete
```

All five passes run against the same LMDB snapshot. Load once at the start of Fix72:

```python
from ilc_core.storage.genesis_atlas_lmdb_writer import AtlasLmdbSafeWriter

writer = AtlasLmdbSafeWriter("out/genesis_base_graph_v0.4_unified.lmdb")
all_nodes = list(writer.store.iter_nodes())
all_edges = list(writer.store.iter_edges())

# Safe ID accessor — use throughout all Fix72 passes
def node_id(n):
    return n.get("candidate_id") or n.get("node_id", "")

def edge_source(e):
    return e.get("source") or e.get("src", "")

def edge_target(e):
    return e.get("target") or e.get("tgt", "")

node_by_id = {node_id(n): n for n in all_nodes}
```

Record the live node/edge counts at the top of the Fix72 walkthrough. Every result in Fix72 must be labelled "post-Fix69 LMDB state."

### Pass 1 — Projection-Aware Fiedler Rebaseline (lineage: Fix56)

**Why:** Fix56 saw the authority-only projection at λ₂ = 0.0 with 1,224 isolated nodes. Strict authority-only may still be sparse because it excludes runtime modules. Add a fourth `authority_binding_surface` projection to measure whether Fix71's `IMPLEMENTS` and `REFERENCES_AUTHORITY` edges connect runtime modules to the governance spine.

**Prior baselines (Fix56, against 15,677 nodes / 74,981 edges):**

| Projection | Nodes | Edges | Components | λ₂ |
|---|---|---|---|---|
| all_local | 15,677 | 74,981 | 1 | 0.009638 |
| public_eligible | 15,195 | 70,823 | 1 | 0.014181 |
| authority_only | 1,515 | 318 | 1,225 | 0.0 |

**Method:** Build four filtered node sets and construct undirected graphs for each:

```python
AUTHORITY_PROJECTIONS = {"genesis_core_star_map"}
PUBLIC_ELIGIBLE = {"genesis_core_star_map", "public_protocol_graph", "support_candidate_graph"}

authority_ids = {node_id(n) for n in all_nodes
                 if n.get("graph_projection") in AUTHORITY_PROJECTIONS}
public_ids = {node_id(n) for n in all_nodes
              if n.get("graph_projection") in PUBLIC_ELIGIBLE}
all_ids = {node_id(n) for n in all_nodes}

authority_binding_ids = set(authority_ids)
for e in all_edges:
    if e.get("edge_type") in {"IMPLEMENTS", "REFERENCES_AUTHORITY"}:
        s, t = edge_source(e), edge_target(e)
        if t in authority_ids:
            source_node = node_by_id.get(s)
            if source_node and "ilc_core" in (source_node.get("source_path") or ""):
                authority_binding_ids.add(s)

def build_undirected(node_set, edge_list):
    import networkx as nx
    G = nx.Graph()
    G.add_nodes_from(node_set)
    for e in edge_list:
        s, t = edge_source(e), edge_target(e)
        if s in node_set and t in node_set:
            G.add_edge(s, t)
    return G

# Compute lambda2 with scipy.sparse.linalg.eigsh or nx.algebraic_connectivity
# Treat all edges as undirected (same as Fix56)
```

Expected direction, not a pass/fail rule: all_local and public_eligible λ₂ may increase because edge density is higher, but λ₂ can also fall when many low-degree support nodes are added. For strict `authority_only`, do not assume Fix71 runtime edges can change connectivity because runtime nodes may be outside that projection. The key Fix71 diagnostic is whether the new `authority_binding_surface` projection shows a connected or substantially larger governance/runtime component.

If authority_only remains disconnected: enumerate isolated node IDs — these are candidates for a follow-on Fix (flag for human review, not part of this sequence).

**Output artifacts:**
- `out/genesis_atlas_fix72_fiedler_all_local_v0.1.json`
- `out/genesis_atlas_fix72_fiedler_authority_only_minority_v0.1.json` (isolated nodes if any)
- `out/genesis_atlas_fix72_fiedler_authority_binding_surface_v0.1.json`
- SHA-256 and byte-size entries for each `out/` artifact in `docs/specs/ilc_fix72_measurement_suite_manifest_v0.1.json`
- Section in `docs/phases/phase_1545p_fix72_measurement_suite_walkthrough.md`

### Pass 2 — Whole-Graph Baseline Diagnostic (lineage: Fix25)

**Why:** Fix25 measured authority-forward trace coverage at 0.5% (0.005484) over 10,029 nodes / 27,668 edges. A new baseline records the post-repair state.

**Traversal semantics (corrected):** `IMPLEMENTS` edges point FROM runtime/support nodes TOWARD CDL/phase authority nodes — they are not edges that flow outward from genesis. Run **three separate traversals**, not one combined BFS:

**Traversal 1 — Authority-control forward:** Walk `GOVERNS` and `CARRIES_FORWARD` edges outward from genesis root. This measures how much of the graph is under direct governance authority.

```python
from collections import deque

GENESIS_ROOT_CANDIDATES = [
    "artifact:genesis_intent_attestation_init_authority_map",
    "artifact:genesis_package_merkle_root_v0.4",
    "artifact:full_repo_genesis_atlas_candidate_root_1545p_fix22",
]
genesis_root = next((candidate for candidate in GENESIS_ROOT_CANDIDATES if candidate in node_by_id), None)
if genesis_root is None:
    genesis_root = next((node_id(n) for n in all_nodes if n.get("node_kind") == "genesis_root_node"), None)
if genesis_root is None:
    raise RuntimeError("No Genesis root candidate found in LMDB")

AUTHORITY_CONTROL_EDGES = {"GOVERNS", "CARRIES_FORWARD"}
forward_adj = {}
for e in all_edges:
    if e.get("edge_type") in AUTHORITY_CONTROL_EDGES:
        forward_adj.setdefault(edge_source(e), []).append(edge_target(e))

visited_forward = set()
queue = deque([genesis_root])
while queue:
    node = queue.popleft()
    if node in visited_forward:
        continue
    visited_forward.add(node)
    for neighbor in forward_adj.get(node, []):
        if neighbor not in visited_forward:
            queue.append(neighbor)

print(f"Authority-control forward coverage: {len(visited_forward)}/{len(all_nodes)}")
```

**Traversal 2 — Implementation reverse reach:** Walk `IMPLEMENTS` edges in reverse (from CDL/ADR toward runtime modules). This measures how many runtime modules are bound to governance nodes by implementation edges.

```python
IMPL_EDGE_TYPES = {"IMPLEMENTS"}
reverse_adj = {}
for e in all_edges:
    if e.get("edge_type") in IMPL_EDGE_TYPES:
        # Reverse direction: target -> source
        reverse_adj.setdefault(edge_target(e), []).append(edge_source(e))

# BFS from each CDL/ADR node backward to runtime nodes
cdl_adr_nodes = {node_id(n) for n in all_nodes
                 if node_id(n).startswith("cdl:") or node_id(n).startswith("adr:")}
visited_reverse = set()
queue = deque(cdl_adr_nodes)
while queue:
    node = queue.popleft()
    if node in visited_reverse:
        continue
    visited_reverse.add(node)
    for neighbor in reverse_adj.get(node, []):
        if neighbor not in visited_reverse:
            queue.append(neighbor)

ilc_core_nodes = {node_id(n) for n in all_nodes
                  if "ilc_core" in (n.get("source_path", "") or "")}
ilc_core_reachable = ilc_core_nodes & visited_reverse
print(f"ilc_core/ nodes reachable from CDL/ADR via reverse IMPLEMENTS: "
      f"{len(ilc_core_reachable)}/{len(ilc_core_nodes)}")
```

**Traversal 2b — Authority-reference reverse reach:** Optionally run the same reverse traversal over `REFERENCES_AUTHORITY` only. Report this separately because it captures evidence/support references, not direct implementation binding.

**Traversal 3 — Undirected connectivity:** Count connected components in the undirected full graph. This is the same as the all_local projection in Pass 1 — confirm giant component fraction is 1.0.

Also report: top-10 highest in-degree nodes by `GOVERNS`/`REFERENCES_AUTHORITY` edge type (most-referenced CDLs and ADRs).

**Output artifacts:**
- `docs/specs/ilc_fix72_whole_graph_baseline_diagnostic_v0.1.json`
- Section in walkthrough

### Pass 3 — Spectral and PageRank Analysis (lineage: Fix43)

**Prior baseline (Fix43, against JSON candidate — 15,676 nodes / 65,693 edges):**

| Metric | Fix43 result |
|---|---|
| λ₂ | 0.034323 |
| Bridge count | 6,175 |
| Giant component fraction | 1.0 |
| Protocol-relevant node count | 5,550 |

**Method:** Replicate `tools/evaluators/sim_genesis_base_graph_spectral_pagerank_1545p_fix43.py` but reading from live LMDB via the pre-loaded `all_nodes` / `all_edges` lists (not the JSON candidate file). Key metrics:

1. **λ₂ (Fiedler):** Full undirected graph, `scipy.sparse.linalg.eigsh`
2. **Bridge count:** `networkx.bridges`
3. **Giant component fraction:** Largest component / total nodes
4. **PageRank:** `networkx.pagerank`, same parameters as Fix43
5. **Bottom-PageRank analysis queue:** 500 protocol-relevant nodes (exclude `out/`, `.git/`, private material) sorted by lowest PageRank — used in Pass 4 and Fix73

Use `k=128` for approximate betweenness (Fix43 used `k=64`). Record `k` value in output.

Record delta table against Fix43 baseline in the walkthrough.

**Output artifacts:**
- `out/genesis_base_graph_spectral_post_fix69.json`
- `out/genesis_base_graph_pagerank_post_fix69.json`
- `out/genesis_base_graph_fix72_low_pagerank_queue.json` (bottom-500, used in Pass 4 and Fix73)
- SHA-256 and byte-size entries for each `out/` artifact in `docs/specs/ilc_fix72_measurement_suite_manifest_v0.1.json`
- Section in walkthrough

### Pass 4 — Percolation Analysis (lineage: Fix45) — ANALYSIS ONLY, NO EDGE WRITES

**Why analysis-only:** Fix45 left 382 of 500 low-PageRank nodes as "deferred to manual semantic review." This pass measures how many of those have since been resolved by Fix71 annotation. It does NOT write new edges — if annotation is warranted based on findings, that becomes a separate structural phase (Fix79 or similar) requiring the same manual-read discipline as Fix71.

**Method:**

1. Load the bottom-500 queue from Pass 3 (`out/genesis_base_graph_fix72_low_pagerank_queue.json`)
2. Cross-reference against the original Fix45 deferred list (locate in Fix45 walkthrough or ledger artifact)
3. For each of the original 382 deferred nodes: check current semantic in-degree from `all_edges`. Count how many now have non-zero semantic in-degree (resolved by Fix71 or Fix68/Fix70)
4. For nodes still in the low-PageRank set with in-degree 0: record as `still_unresolved` with node ID, node_kind, and source_path. Do not write edges.
5. Output the resolved/unresolved counts and the still-unresolved node list for human review

**Output artifacts:**
- `docs/specs/ilc_fix72_percolation_analysis_v0.1.json` — resolved count, still_unresolved list
- Section in walkthrough

If the still-unresolved list is non-empty and annotation edges can be deterministically inferred (node metadata directly implies the relationship without semantic judgment), flag for a follow-on structural phase. Annotation requiring direct-read of source content is not deterministic and must not be inferred.

### Pass 5 — Authority SIM Battery (lineage: Fix52)

**Why:** Fix52 ran without CDL↔ADR cross-family authority links (Fix70 added them). Adding new Suite D — first runtime binding coverage test.

**Prior baseline (Fix52):**
- Suite A: 0 unresolved epistemic_gap nodes (PASS)
- Suite B: 0 GOVERNS cycles (PASS)
- Suite C: gap node had no candidate targets (BLOCKED)

**Four suites:**

**Suite A — Authority exclusion:** For each CDL node, verify reachability from genesis root via `GOVERNS` path (Traversal 1 above). Count unreachable CDLs. Expected: near-zero after Fix70.

**Suite B — GOVERNS cycle detection:** Build directed `GOVERNS`-only subgraph. Run `networkx.simple_cycles`. Expected: 0.

**Suite C — Gap closure simulation:** Find all `node_kind == "epistemic_gap_node"` entries. For each, check if any candidate authority target now exists reachable via the cross-family lattice (Fix70). Record `resolvable_gap` candidates for human review. Do not write edges.

**Suite D (new) — Runtime binding coverage:** For each ratified CDL node, count `ilc_core/` nodes carrying `IMPLEMENTS → <that CDL>`. CDLs with zero IMPLEMENTS edges are "implementation-dark." List all implementation-dark CDLs — this feeds directly into Fix73.

**Output artifacts:**
- `docs/specs/ilc_fix72_authority_sim_battery_v0.1.json` (all four suites)
- `docs/specs/ilc_fix72_measurement_suite_manifest_v0.1.json` (manifest over all committed and uncommitted Fix72 outputs)
- Section in walkthrough

### Fix72 walkthrough and commit

One walkthrough file: `docs/phases/phase_1545p_fix72_measurement_suite_walkthrough.md`

All five passes documented in order. Every result must be labelled with the live LMDB node/edge counts recorded at the start of Fix72.

Register all committed output artifacts in LMDB before committing. Do not commit or register large `out/` files directly unless they are explicitly approved; register the committed measurement manifest that records their SHA-256, byte size, and purpose.

Commit message:
```
analysis(atlas): Fix72 post-repair measurement suite — Fiedler, baseline, spectral, SIM battery
```

---

## Fix72a — Safe-Writer Edge-Type Semantic Allowlist

**Required token:** `fix72_complete`

**Purpose:** Install central semantic edge validation in
`ilc_core/storage/genesis_atlas_lmdb_writer.py` before Fix73 and later phases
perform any further safe-writer registrations or semantic graph writes. The
existing safe writer enforces baseline structural integrity (no dangling edges,
edge IDs, duplicate controls, payload/index consistency). Fix72a adds semantic
edge-shape validation so structurally valid but semantically invalid edges are
rejected before write.

**Non-claims:**
- Does not mutate existing LMDB graph content.
- Does not rewrite historical edges.
- Does not sign or promote Genesis material.
- Does not claim all existing historical edges satisfy the new policy.
- Does not replace manual-read evidence requirements for future semantic edges.

**Output tokens:**
```
fix72a_safe_writer_edge_type_allowlist_committed
fix72a_unknown_edge_types_default_denied
fix72a_authority_edge_gates_enforced
fix72a_complete
```

### Implementation Requirements

Add an edge-type policy layer inside `AtlasLmdbSafeWriter` and call it from
`validate_plan()` before an edge can be accepted. The validator must inspect:

- edge type
- source candidate ID
- target candidate ID
- source node record, when present
- target node record, when present
- write-plan metadata, for explicitly documented historical migration overrides

Default behavior:

- Unknown edge types are rejected by default.
- Missing source/target nodes remain rejected by existing dangling-edge checks.
- Existing accepted Fix69/Fix71-style support edges must continue to pass.
- Historical migration overrides must be explicit and auditable; they must not
  become a general bypass.

Minimum policy table:

| Edge type | Allow rule |
|---|---|
| `GOVERNS` | Source must be genesis/CDL/ADR authority-like. Runtime, repo, policy-support, target, sim, and file-ref sources are rejected. Live write requires explicit authority env gate already used by the Atlas write CLI where applicable. |
| `SAME_SOURCE` | Source must be `repo:file_ref:*`; target must be `repo:file:*`. |
| `REFERENCES_AUTHORITY` | Target must be authority-like (`cdl:*`, `adr:*`, trusted `artifact:*`, or explicitly allowlisted authority-policy nodes). Target must not be `repo:*`. |
| `IMPLEMENTS` | Source must be runtime/source/test/tool/support implementation material; target must be CDL/ADR/phase/invariant authority or implementation target. Reject authority-to-runtime `IMPLEMENTS`. |
| `TESTS` | Source must be test file/test node or accepted test harness material; target may be phase, module, invariant, runtime/source node, CDL/ADR, or security/doc artifact under direct evidence. |
| `EVIDENCES` | Source must be file/doc/test/sim/invariant/support material; target must be phase, invariant, CDL/ADR, policy, artifact, or other evidence-bearing support endpoint. |
| `CARRIES_FORWARD` | Source and target must be phase/support/doc/policy/artifact endpoints or file-registration support nodes. Reject runtime module to authority misuse. |
| `CLASSIFIED_BY` | Reject writes that would create target fan-in above `100` unless the target is explicitly allowlisted in plan metadata. Never use as a public-path routine file tag. |
| `SOURCE_TREE_MEMBER` | Not a generic fallback. Allow only for actual source-tree containment semantics where source and target node kinds/prefixes are source-tree/file/group endpoints. |
| `CONTAINS_FILE`, `CONTAINS_GROUP`, `CONTAINS_PARTITION` | Allow only from repo/source-tree group or manifest nodes to repo/file/group/partition endpoints. |
| `OPENED_FOR`, `PRELOCK_FOR`, `RATIFICATION_EVIDENCE_FOR`, `PROPOSES_CHANGE_TO`, `RESOLVED_BY`, `SAME_AUTHORITY`, `DERIVED_FROM` | Allow lifecycle/identity/provenance edges only between CDL/ADR/lifecycle/support authority endpoints. Reject repo-file sources unless explicitly backed by a lifecycle document node. |

Authority-like source/target checks must be helper functions, not repeated inline
string fragments. Use candidate-ID prefixes and node metadata (`node_kind`,
`graph_projection`, `tier`) conservatively. A false reject is preferable to a
false accept; migration phases can add a documented override with human review.

### Historical Migration Override

Add a narrow override path for historical repair phases. It must require all of:

- `plan.metadata["allowlist_override"] is True`
- `plan.metadata["migration_phase"]` is a non-empty string
- every overridden edge receives an `allowlist_override_reason`
- the receipt reports overridden edge count and edge semantics

Overrides must not be permitted for `GOVERNS` unless the authority environment
gate is also satisfied.

### Tests

Add or extend tests under `tests/` with at least:

- Reject `repo:file:* --GOVERNS--> cdl:*`
- Reject `policy:* --GOVERNS--> invariant:*` unless the policy is explicitly
  authority-like and env-gated
- Reject unknown edge types by default
- Accept `repo:file_ref:* --SAME_SOURCE--> repo:file:*`
- Reject `repo:file:* --SAME_SOURCE--> repo:file_ref:*`
- Accept `repo:file:* --REFERENCES_AUTHORITY--> cdl:*`
- Reject `repo:file:* --REFERENCES_AUTHORITY--> repo:file:*`
- Accept valid `CARRIES_FORWARD`, `EVIDENCES`, and `TESTS` phase-file
  registration edges
- Reject routine `CLASSIFIED_BY` writes that would recreate a high-fan-in
  public-path or support-policy hub
- Preserve existing Fix69/Fix71-style support-edge plans under the new policy

Also add one regression test that constructs an otherwise structurally valid
edge with invalid semantics and proves `validate_plan()` rejects it before
`apply_plan(dry_run=False)` can mutate LMDB.

### Fix72a Commit

Register modified committed files in LMDB before closure. The closeout
registration itself must pass the new allowlist.

Commit message:
```
fix(atlas): Fix72a enforce safe-writer edge-type semantic allowlist
```

---

## Fix73 — Runtime-to-Governance Trace Study (New — First-Ever)

**Required token:** `fix72a_complete`

**This phase is read-only against graph content.** No semantic node/edge mutations are permitted. The only LMDB writes allowed are support-only registrations for committed report/walkthrough artifacts.

**Why this study is now possible:** Before Fix71, no path existed from `ilc_core/` source code into the CDL/governance lattice. Fix71 added `IMPLEMENTS → CDL/phase` edges from runtime modules. This is the first time a graph-native implementation coverage audit is possible. Fix72 measurement has already established the baseline; Fix73 does the deeper cross-referencing.

**Output tokens:**
```
fix73_runtime_governance_trace_complete
fix73_complete
```

### H1 — CDL implementation coverage

For each CDL node, compute `implements_count` and `evidences_count`. Classify each CDL:

| Classification | Condition |
|---|---|
| `implemented_and_tested` | >0 IMPLEMENTS, >0 EVIDENCES |
| `implemented` | >0 IMPLEMENTS, 0 EVIDENCES |
| `spec_only` | 0 IMPLEMENTS, >0 EVIDENCES |
| `dark` | 0 IMPLEMENTS, 0 EVIDENCES |

```python
cdl_nodes = [n for n in all_nodes if node_id(n).startswith("cdl:")
             or n.get("node_kind") == "cdl_node"]

cdl_coverage = {}
for cdl in cdl_nodes:
    cid = node_id(cdl)
    impl_sources = [edge_source(e) for e in all_edges
                    if e.get("edge_type") == "IMPLEMENTS"
                    and edge_target(e) == cid
                    and "ilc_core" in edge_source(e)]
    test_sources = [edge_source(e) for e in all_edges
                    if e.get("edge_type") == "EVIDENCES"
                    and edge_target(e) == cid]
    cdl_coverage[cid] = {
        "implements_count": len(impl_sources),
        "evidences_count": len(test_sources),
        "implementing_modules": impl_sources,
        "classification": (
            "implemented_and_tested" if impl_sources and test_sources
            else "implemented" if impl_sources
            else "spec_only" if test_sources
            else "dark"
        )
    }
```

Cross-reference with Fix72 Suite D (implementation-dark CDL list) to confirm consistency.

### H2 — Runtime module authority reach

For each `ilc_core/` module node, compute:
- `implements_count`: number of CDLs directly IMPLEMENTS-linked
- `authority_reach`: set of CDL/ADR nodes reachable at depth ≤ 3 via `IMPLEMENTS → CDL → GOVERNS → ...`

Identify modules with zero IMPLEMENTS edges (should be none after Fix71 — any found are a gap).

### H3 — Test coverage by governance node

For each CDL, list `EVIDENCES` sources. Sort by evidence count. Bottom = zero-evidence CDLs — candidates for new test coverage. A CDL that is both implementation-dark (from H1) and test-dark is the highest-priority gap.

### H4 — Write study report

`docs/specs/ilc_fix73_runtime_governance_trace_study_v0.1.json`:

```json
{
  "study": "runtime_to_governance_trace",
  "lmdb_state_at_execution": {"nodes": 16894, "edges": 94167},
  "cdl_coverage_summary": {
    "total_cdls": 0,
    "implemented_and_tested": 0,
    "implemented_only": 0,
    "spec_only": 0,
    "dark": 0
  },
  "dark_cdls": ["cdl:...", "..."],
  "top_implemented_cdls": [{"cdl_id": "...", "implements_count": 0}],
  "implementation_orphan_ilc_core_modules": ["..."],
  "test_dark_cdls": ["..."],
  "highest_priority_gaps": ["..."]
}
```

Use live numeric values in the final report; the values above are schema examples,
not expected counts.

Also write `docs/phases/phase_1545p_fix73_runtime_governance_trace_walkthrough.md`.

Register both output files in LMDB before committing.

Commit message:
```
analysis(atlas): Fix73 runtime-to-governance trace — CDL implementation and test coverage map
```

---

## Fix74 — Pre-Public-RC Gap Fixes (P1 + P1b)

**Required tokens:** `fix73_runtime_governance_trace_complete`, `fix73_complete`

**Why after the measurement suite:** Fix74 adds new support nodes (doc files, updated source files) to the LMDB and perturbs the edge/node counts. Measurement passes Fix72 and Fix73 must reflect the clean post-Fix69 state. Fix74's trace output in Fix73 may reveal which P1 modules are implementation-dark — that informs triage priority within Fix74.

**Output tokens:**
```
fix74_p1_pre_rc_code_fixes_complete
fix74_p1b_cleanup_complete
fix74_complete
```

### P1: 13 Pre-Public-RC Code and Config Fixes

Fix them in priority order:

**Group 1 — Canonical JSON non-finite rejection (fix first — confirmed exploit vector):**

Files: `ilc_core/network/wire_transport_runtime.py`, `ilc_core/protocol/ilc_cluster_a_acceptance_evidence.py`

Add `allow_nan=False` to every `json.dumps()` call whose output may become a canonical public preimage. Direct-read each file's call path before adding the flag to confirm which calls touch canonical outputs. Covered by ILC Coding Security Standard §1 and §3.

**Group 2 — Float inputs at protocol boundaries:**

- `ilc_core/cli/ep_task_cli.py`: Replace float literals in demo payloads with string or `Decimal`-compatible examples
- `ilc_core/consensus/governance.py`: Add docstring/type stub clarifying `List[float]` inputs are not valid protocol inputs; caller must supply canonical string or `Decimal` form
- `ilc_core/privacy/metrics.py`: Add module-level comment confirming float telemetry must never enter economic or settlement state — no code change to computation

**Group 3 — Build-time resource loading:**

- `ilc_core/crypto/__init__.py`: Treat this as the evidence pointer for the crypto dependency gap, but apply version pins in the actual package metadata file (`pyproject.toml`, setup config, or equivalent) after direct-reading the current packaging surface
- `ilc_core/genesis/schema.py`: Replace root-path schema loading with `importlib.resources` or graph-addressed content lookup. Direct-read current loading code before patching.

**Wire format timestamp — requires explicit adjudication:**

`ilc_core/protocol/schemas/ilc_protocol_wire_format_v0.1.json`: Timestamp field is ambiguous. Adjudicate before patching:
- If diagnostic only: add `"semantic": "diagnostic_only"` to the field and a comment that it must not be used as a protocol input
- If protocol input: conflicts with ILC Coding Security Standard §7 (no wall-clock in protocol timing); raise to human review before patching

Do not leave without explicit classification.

### P1b: 5 Doc, Docstring, and Index Cleanup Items

- **ADR-0036, ADR-0037**: Remove stale "Proposed" status wording where accepted header or LMDB authority is already established
- **`ilc_core/cli/atlas_lmdb_cli.py`**: Docstring says read-only but guarded writes exist — add "read-first, guarded-write" clarification
- **`tools/evaluators/sim_genesis_base_graph_lmdb_rematerialization_1545p_fix41.py`**: Add file-level comment: "Historical evaluator from Fix41. Future writes must use `AtlasLmdbSafeWriter`."
- **`docs/adr/README.md`**: Regenerate or correct stale ADR status index before public documentation freeze
- **`ilc_core/config.py`**: Docstring references `governance_mvp.yaml`; actual default is `governance_mvp.json` — fix docstring

### Fix74 commit structure

Two commits preferred: P1 code changes (auditable diff) + P1b doc/docstring cleanup. Do not mix code and doc changes in the same diff hunk.

Register all modified files in LMDB before closing.

Commit message (P1):
```
fix(ilc_core): Fix74-P1 pre-RC hardening — allow_nan, float boundary, build resource loading
```
Commit message (P1b):
```
docs: Fix74-P1b cleanup — stale ADR prose, CLI docstring, config mismatch
```

---

## Fix75 — Numeric, Determinism, and Serialization Sweep (P2)

**Required token:** `fix74_complete`

**Scope:** 149 rows from the Fix71 gap ledger (`category = determinism_numeric_or_serialization_hardening`).

**Why after Fix73:** Fix73 may have identified float-heavy modules as implementation-dark or high-authority-coupling — use those findings to prioritize which P2 rows are `protocol-forbidden` vs `simulation-only`.

**Output tokens:**
```
fix75_p2_numeric_determinism_sweep_complete
fix75_complete
```

### Step 1 — Classification pass (document-only, no code changes first)

Label each of the 149 rows:

| Label | Meaning | Action |
|---|---|---|
| `protocol-forbidden` | Float/non-determinism in settlement, ECU, or canonical hash path | Code change required |
| `exact-runtime` | Already uses `Decimal` or epoch sequence correctly | Record in classification JSON; add code comments only where the boundary is otherwise ambiguous |
| `simulation-only` | Float/randomness in SIM/devnet path, correctly isolated | Record in classification JSON; add `sim-only` comments only where needed |
| `telemetry-only` | Float in monitoring/logging, never enters protocol state | Record in classification JSON; add `telemetry-only` comments only where needed |

Write the table to `docs/specs/ilc_fix75_numeric_determinism_classification_v0.1.json` before touching code.

### Step 2 — Code changes for protocol-forbidden instances only

**Highest-risk items (direct-read call path first):**

- `ilc_core/consensus/engine.py`: float formulas for age/tax/bounty — if they flow into settlement or ECU: `protocol-forbidden` → convert to `Decimal`, add `if not d.is_finite(): raise ValueError(...)` at ledger input boundaries
- `ilc_core/genesis/work_task.py`: `difficulty_factor` is `Optional[float]` — `protocol-forbidden` if used in ECU computation; `simulation-only` if SIM scaffolding only
- `ilc_core/analysis/node_value_input_canon.py`: reward/stake/age fields accept `int/float` before normalization — check if normalization produces `Decimal` or stays float downstream
- `ilc_core/types.py`: `WeightParams` float-like fields — classify per field (analysis surface vs protocol input)
- Export/report paths writing `datetime.now()`: add explicit timestamp override parameter for reproducible signing contexts

SIM and devnet paths: comments only, no code changes.

### Step 3 — Commit structure

Two commits: classification document first, then code changes for `protocol-forbidden` instances only.

```
docs(ilc_core): Fix75-P2 numeric classification — label all float/timestamp/randomness rows
fix(ilc_core): Fix75-P2 numeric hardening — Decimal conversion for protocol-forbidden paths
```

---

## Fix76 — Package, Build, and Content-Hash Audit (P3)

**Required tokens:** `fix75_p2_numeric_determinism_sweep_complete`, `fix75_complete`

**Scope:** 66 rows (`category = package_content_identity_or_build_gap`).

**Output tokens:**
```
fix76_p3_package_build_audit_complete
fix76_complete
```

Continues the Fix64/Fix65 lineage. Deliverable: build-critical file manifest verifying five properties for every public protocol file:

| Property | Check |
|---|---|
| Content hash | Present in LMDB `file_ref` node |
| Source path | Resolves from both repo root and package root |
| Package membership | Declared in package manifest |
| Dependency membership | Required transitive deps listed with versions |
| Verifier/test relation | At least one `TESTS` or `EVIDENCES` edge from a test node |

Write to `docs/specs/ilc_fix76_build_critical_file_audit_v0.1.json`.

Priority items: confirm `genesis/schema.py` resource loading was addressed in Fix74; verify `crypto/__init__.py` version pins are complete; add `"signed": false` to any pre-signing-ceremony manifest to prevent confusion with signed Genesis package roots.

```
docs(build): Fix76-P3 build-critical file audit — content hash, package membership, dep closure
```

---

## Fix77 — Crypto-Boundary Audit (P4)

**Required tokens:** `fix76_p3_package_build_audit_complete`, `fix76_complete`

**Scope:** 48 rows (`category = cryptography_signature_or_keying_gap`).

**Output tokens:**
```
fix77_p4_crypto_boundary_audit_complete
fix77_complete
```

Deliverable: crypto-boundary map assigning one of three labels per module:

| Label | Meaning |
|---|---|
| `schema_validation_only` | Validates shape/structure; no cryptographic signature verification |
| `signature_verification` | Performs actual signature verification against a public key |
| `key_custody_required` | Requires external signing ceremony input; never holds private keys |

Starting points: `ilc_core/crypto/cose_sign1.py` → `key_custody_required`; `ilc_core/genesis/assertion_schema.py` → `schema_validation_only`; `ilc_core/protocol/ilc_governance_record_validate.py` → `schema_validation_only`.

Do not treat schemas with HMAC compatibility records or example values as authoritative signing artifacts. Add clarifying comments to any such file.

Write map to `docs/specs/ilc_fix77_crypto_boundary_map_v0.1.json`.

```
docs(crypto): Fix77-P4 crypto-boundary map — classify schema/verify/key-custody surfaces
```

---

## Fix78 — LMDB Lifecycle and Alias Cleanup (P7)

**Required tokens:** `fix77_p4_crypto_boundary_audit_complete`, `fix77_complete`

**Scope:** 14 rows (`category = authority_lifecycle_or_alias_cleanup`).

**Output tokens:**
```
fix78_p7_lifecycle_alias_cleanup_complete
fix78_complete
```

For each lifecycle/alias node, direct-read to confirm a canonical authority node exists. Apply the appropriate edge:

| Situation | Edge to add |
|---|---|
| Alias of ratified CDL/ADR | `SAME_AUTHORITY → <canonical node>` |
| Lifecycle record for open CDL/ADR | `OPENED_FOR → <target>` or `PRELOCK_FOR → <target>` |
| Evidence for ratification event | `RATIFICATION_EVIDENCE_FOR → <ratified node>` |
| Proposal for change | `PROPOSES_CHANGE_TO → <existing authority>` |
| Superseded | `RESOLVED_BY → <successor node>` |

**Hard rule:** Do not create a new independent authority node for a lifecycle/alias record. If no canonical node exists, flag for human decision. Dry-run each batch before applying.

```
fix(atlas): Fix78-P7 lifecycle alias cleanup — wire lifecycle nodes to canonical authority records
```

---

## Gap Categories Requiring No Fix Phase

**P5/P6 (452 rows — economic activation and public RC gates):** Not bugs. Confirmed working default-off guards. Use the Fix71 gap ledger as a living release-gate checklist. At each future activation GO decision, query the ledger and confirm guards are intact before opening the gate.

**P8 (2 rows — task queue durability):** `ilc_core/work/task_queue.py` is intentionally in-memory. Not a public RC blocker. Deferred to a future product planning window.

---

## Commit and Artifact Summary

| Phase | Type | Commit message prefix | Key output artifact |
|---|---|---|---|
| Fix69 | Structural repair | `fix(atlas): Fix69 orphan rewiring` | `ilc_fix69_orphan_rewiring_audit_v0.1.json` |
| Fix72 | Read-only analysis | `analysis(atlas): Fix72 measurement suite` | 5 JSON reports + walkthrough |
| Fix73 | Read-only analysis | `analysis(atlas): Fix73 runtime-governance trace` | `ilc_fix73_runtime_governance_trace_study_v0.1.json` |
| Fix74-P1 | Code hardening | `fix(ilc_core): Fix74-P1 pre-RC hardening` | code changes in ~5 files |
| Fix74-P1b | Doc cleanup | `docs: Fix74-P1b cleanup` | doc/docstring changes in 5 files |
| Fix75-P2 | Classification + code | `fix(ilc_core): Fix75-P2 numeric hardening` | `ilc_fix75_numeric_determinism_classification_v0.1.json` |
| Fix76-P3 | Audit doc | `docs(build): Fix76-P3 build-critical audit` | `ilc_fix76_build_critical_file_audit_v0.1.json` |
| Fix77-P4 | Audit doc | `docs(crypto): Fix77-P4 crypto-boundary map` | `ilc_fix77_crypto_boundary_map_v0.1.json` |
| Fix78-P7 | LMDB graph surgery | `fix(atlas): Fix78-P7 lifecycle alias cleanup` | LMDB edge additions |

Each phase: own commit, own walkthrough in `docs/phases/`, own STATUS.md token(s), LMDB registration of all output files before closure.
