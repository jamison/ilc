# Phase 1237 - L3 Sidecar Query Runtime Expansion Plan

**Phase:** 1237 planning addendum
**Window:** 1233-1240
**Date:** 2026-05-07
**Status:** Planning / prompt-hardening artifact; no runtime executed
**Token:** `phase_1237_sidecar_query_runtime_expansion_plan_committed`

---

## 1. Purpose

The original Phase 1237 prompt is spec-only. That matches the active Window
1233-1240 sequence lock, but it underuses the already-implemented Phase 1229
projection runtime:

```text
agent_graph_projection_runtime_1229.v0.1
```

This addendum records the corrected, code-accurate implementation path for an
L3 sidecar query runtime. It does not execute runtime work. It defines Fix
prompts that can be run after the base Phase 1237 spec if the human reviewer
authorizes the expanded implementation lane.

---

## 2. Code-Trace Corrections to Sonnet Draft

The implementation plan must follow the actual code in
`ilc_core/graph/agent_graph_projection_runtime.py`, not only the prose specs.

| Sonnet draft point | Code-accurate correction |
|--------------------|--------------------------|
| Use `project_graph(filters=...)` to slice ego neighborhoods | Do not do this. `_matches_applicable_filters()` ignores filters for keys absent from an item, so it is not an exact canonical-ID subgraph selector. Ego graph filtering must be manual. |
| Centrality can be recomputed directly from edges | Prefer the already-computed `projection["metrics"]["degree_by_node"]`. It is deterministic and counts both edge endpoints as undirected degree. |
| `path_to_genesis()` may fail for Genesis itself | It does not. `path_to_genesis(projection, "genesis:root")` returns `["genesis:root"]`, so provenance depth for Genesis is `0`. |
| Hyperedge member order needs special handling | Phase 1229 already normalizes hyperedge `members` to sorted tuples. Sidecar filtering should preserve existing projection order. |
| Version token should never bump during fixes | Not a universal rule. If Fix1 declares the complete v0.1 query contract, later additive fixes can keep `sidecar_query_runtime_1237.v0.1`. A breaking interface change must bump the version. |
| Runtime implementation is automatically non-sensitive | It is non-sensitive only because the scoped module is read-only graph-query code under `ilc_core/graph/` and has no mutation authority. If a fix adds protocol writes, consensus/finality behavior, CDL mutation, or sidecar network serving, it becomes sensitive. |

---

## 3. Architectural Boundary

The sidecar query runtime is:

- read-only;
- deterministic;
- pure Python;
- local/in-process by default;
- built on Phase 1229 projection dictionaries;
- not an ILC node;
- not a serving peer;
- not a gossip participant;
- not a mutation authority;
- not a consensus participant;
- not a privacy/anonymity layer; and
- not a human visualization app.

It provides query functions that agent-native or human-facing sidecars can call
after a canonical projection has already been built.

---

## 4. Fix Sequence

| Fix | Topic | Runtime mutation? | Sensitivity |
|-----|-------|-------------------|-------------|
| Base 1237 | L3 sidecar infrastructure spec + this expansion plan | No | NON-SENSITIVE |
| Fix1 | `sidecar_query_runtime.py` skeleton, bounds, dispatcher stubs | Yes, read-only graph module | NON-SENSITIVE; explicit GO recommended because sequence lock base is spec-only |
| Fix2 | Ego graph query | Yes, read-only graph module | NON-SENSITIVE |
| Fix3 | Centrality metrics | Yes, read-only graph module | NON-SENSITIVE |
| Fix4 | Convergence trace | Yes, read-only graph module | NON-SENSITIVE |
| Fix5 | Unified dispatcher + `SidecarQuery` dataclass + integration | Yes, read-only graph module | NON-SENSITIVE |
| Fix6 | Canonical sidecar query export and bundle envelope | Yes, read-only graph module | NON-SENSITIVE |
| Fix7 | Local dev/test smoke harness | Test/tool-only | NON-SENSITIVE |

Do not collapse Fix1-Fix7 into one large implementation commit unless a prompt
explicitly authorizes that larger scope.

---

## 5. Implementation Rules

All fixes must preserve:

- no filesystem I/O in `ilc_core/graph/sidecar_query_runtime.py`;
- no network I/O;
- no wall-clock protocol fields;
- no random or PRNG usage;
- no `assert` runtime enforcement;
- no Python `float` output in query results;
- deterministic ordering for nodes, edges, hyperedges, and ranked metrics;
- `json.dumps(..., sort_keys=True, allow_nan=False, separators=(",", ":"))`
  for canonical sidecar exports; and
- no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md`.

The legacy `EpistemicGraph` class in `ilc_core/graph/__init__.py` is not part of
this implementation lane. Phase 1237 sidecar queries operate on Phase 1229
projection dictionaries.

---

## 6. Additional Fixes Beyond Sonnet Draft

Sonnet's Fix1-Fix4 plan is a good start, but two more implementation fixes are
useful and safe at this stage:

### Fix6 - Canonical Sidecar Query Export

Add:

```python
export_sidecar_query_json(result: Mapping[str, Any], *, max_bytes: int = 10_000_000) -> str
export_sidecar_query_ndjson(results: Sequence[Mapping[str, Any]], *, max_bytes: int = 10_000_000) -> str
build_sidecar_query_bundle(*, projection: Mapping[str, Any], query_results: Sequence[Mapping[str, Any]]) -> dict[str, Any]
```

Why: if Phase 1237 stops at in-memory dicts, it has not actually provided a
usable sidecar consumption surface. Exporting canonical JSON/NDJSON is the
smallest practical external boundary.

### Fix7 - Local Dev/Test Smoke Harness

Add a test-only or tool-only smoke path that builds a sample projection, runs
all query types, exports the bundle, and verifies stable output. No server, no
HTTP endpoint, no filesystem writes in runtime.

Why: this proves the sidecar runtime is usable as a local component without
crossing into L3 app or visualization implementation.

---

## 7. Open Boundaries After Fix7

Even after Fix1-Fix7, these remain open:

```text
l3_visualization_sidecar_app_deferred
sidecar_network_service_deferred
sidecar_authentication_policy_deferred
sidecar_human_ui_deferred
```

The sidecar query runtime is the machine-native query substrate. It is not the
full human-facing visualization sidecar.

---

`phase_1237_sidecar_query_runtime_expansion_plan_committed`
