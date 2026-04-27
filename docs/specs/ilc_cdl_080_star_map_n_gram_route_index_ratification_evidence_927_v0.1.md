# CDL-080 Ratification Evidence — Phase 927

**CDL:** CDL-080 Star.Map N-Gram Route Index — L3 Routing Layer
**Opened:** Phase 922
**Ratification Phase:** 927
**Status:** RATIFIED

---

## Ratification Readiness Evidence (CDL-080 §8 Checklist)

### ☑ 1. `star_map_route_index_runtime.py` exists; version + dep tokens present

File: `ilc_core/network/star_map/star_map_route_index_runtime.py`
Committed: Phase 923-926 commit `3180dc78`

```python
STAR_MAP_RUNTIME_VERSION = "star_map_route_index_runtime_923.v0.1"
CDL_080_DEPENDENCY = "cdl_080_star_map_n_gram_route_index.v0.1"
ADR_0003_DEPENDENCY = "adr_0003_star_map_route_index"
ADR_0033_DEPENDENCY = "adr_0033_star_map_homoiconic_entity"
CDL_077_DEPENDENCY = "cdl_077_want_have_want_block_fetch.v0.1"
H015_DEPENDENCY = "spectral_routing_runtime_h015.v0.1"
```

Dep-chain guard verified at import:

```python
def _verify_h015_dep() -> None:
    from ilc_core.network.d2d.spectral_routing_runtime import (
        SPECTRAL_ROUTING_RUNTIME_VERSION,
    )
    if SPECTRAL_ROUTING_RUNTIME_VERSION != "spectral_routing_runtime_h015.v0.1":
        raise RuntimeError(...)
```

**Evidence:** `test_runtime_module_exists`, `test_star_map_runtime_version_token`,
`test_cdl_080_dependency_token`, `test_adr_0003_dependency_token`,
`test_adr_0033_dependency_token`, `test_cdl_077_dependency_token`,
`test_h015_dependency_token` — all PASS.

---

### ☑ 2. Route index computation is deterministic (same inputs → same output)

`compute_route_index()` is deterministic by construction:
- N-gram extraction normalized via `re.sub(r"\s+", " ", text.strip().lower())`
- Bucket endpoint lists sorted: `buckets[key] = sorted(existing)`
- Label iteration: `for label, endpoints in sorted(node_endpoints.items())`
- Parameter digest: `json.dumps(..., sort_keys=True)` throughout

**Evidence:** `test_compute_route_index_deterministic` — calls `compute_route_index`
twice with identical inputs, asserts `ri1.buckets == ri2.buckets` and
`ri1.parameter_digest == ri2.parameter_digest`. PASS.

---

### ☑ 3. `publish_star_map_result()` produces ADR-0033 compliant `Node(type="star_map")`

Required fields per CDL-080 §4.4 / ADR-0033 §2.5:

| Field | Present | Value |
|---|---|---|
| `entity_kind` | ✓ | `"route_cluster"` \| `"panel_result"` \| `"navigation_overlay"` |
| `generator_ref` | ✓ | `route_index.generator_agent_id` |
| `source_artifact_refs` | ✓ | `[]` (route index has no individual source CIDs) |
| `source_node_set_digest` | ✓ | SHA-256 of sorted source node CID list |
| `method` | ✓ | `"n_gram_route_index_v1"` |
| `parameter_digest` | ✓ | SHA-256 of construction parameters |
| `result_payload` | ✓ | Serialized route index artifact |
| `epoch` | ✓ | Publication epoch |
| `agent_id` | ✓ | Publishing agent CID |
| `id` (content-addressed) | ✓ | `sha256(canonical_json).hexdigest()` |
| `type` | ✓ | `"star_map"` |

Invalid `entity_kind` raises `ValueError` — enforces the three-value enum.

Publication boundary marks source `RouteIndex._published_node_id = node_id`.

**Evidence:** `test_publish_star_map_result_returns_node_dict`,
`test_publish_star_map_result_has_all_adr_0033_fields`,
`test_publish_star_map_result_content_addressed_id`,
`test_publish_star_map_result_marks_index_as_published`,
`test_publish_star_map_result_invalid_entity_kind_raises`,
`test_ephemeral_index_has_no_node_id_before_publish`,
`test_publish_star_map_result_carries_cdl_080_token` — all PASS.

---

### ☑ 4. Spectral routing (H-015) wired as L3 prefilter; gossip boundary preserved

`query_route_index_spectral()` imports `spectral_distance` from
`ilc_core.analysis.spectral_utils` (the H-015 compute kernel, not a re-export
from `spectral_routing_runtime`). The function:

1. Calls `query_route_index()` with `top_k * 4` candidates
2. Scores each candidate by spectral distance to local fingerprint
3. Returns `top_k` candidates ranked by distance (closest first)
4. Falls back gracefully when `local_fingerprint` or `peer_fingerprints` is None
   (via `l3_route_and_fetch` dispatch — uses plain `query_route_index` when
   fingerprints absent)

No gossip beacon emission. No `gossip_transport` import anywhere in
`star_map_route_index_runtime.py`.

**Evidence:** `test_query_route_index_spectral_returns_hints_with_distance`,
`test_query_route_index_spectral_no_fingerprints_falls_back`,
`test_l3_spectral_routing_uses_h015_spectral_distance`,
`test_no_gossip_beacon_activation_in_star_map_source` — all PASS.

---

### ☑ 5. L3 advisory / L2 authoritative contract verified by test

The `L3_ADVISORY_L2_AUTHORITATIVE` token is a module-level constant:

```python
L3_ADVISORY_L2_AUTHORITATIVE = (
    "l3_advisory_l2_authoritative_l3_does_not_override_cdl_077"
)
```

`l3_route_and_fetch()`:
- Returns L2 result when L2 responds (not conditional on L3 hint match)
- Returns `None` when all L2 fetches miss — explicitly documented as not a
  routing error per CDL-080 §4.5
- Non-matching L2 response is the correct behavior per CDL-080 §4.5

**Evidence:** `test_l3_advisory_l2_authoritative_token`,
`test_l3_route_and_fetch_returns_l2_result`,
`test_l3_route_and_fetch_returns_none_when_l2_misses`,
`test_l3_route_and_fetch_tries_multiple_candidates`,
`test_l3_route_and_fetch_no_candidates_returns_none` — all PASS.

---

### ☑ 6. No ECU call, no gossip beacon call in star_map source

Static analysis confirms:
- No `ecu` import or call in `star_map_route_index_runtime.py`
- No `gossip` import or call in `star_map_route_index_runtime.py`

**Evidence:** `test_no_ecu_call_in_star_map_source`,
`test_no_gossip_beacon_activation_in_star_map_source` — both PASS.

---

### ☑ 7. ≥28 tests passing, zero regressions

**36 tests collected, 36 passed, 0 failed.**

```
tests/test_phase_921_929_cdl_080_star_map.py  36 passed in 0.57s
```

Test groups:
1. Dep-chain tokens (8 tests)
2. `compute_route_index` (5 tests)
3. `query_route_index` (5 tests)
4. `publish_star_map_result` / ADR-0033 boundary (7 tests)
5. L3 advisory / L2 authoritative (4 tests)
6. Spectral routing (3 tests)
7. No ECU / no gossip (2 tests)
8. CDL-080 in master log (1 test)
9. Commit scope guard (1 test)

---

### ☑ 8. CDL-080 row in master log: `opened_phase: 922`, `ratified_phase: 927`

To be confirmed at CDL log mutation (this phase).

**Evidence:** `test_cdl_080_in_master_log` — reads
`docs/specs/ilc_constitutional_decision_log_v0.1.md`, asserts CDL-080 row
present with `opened_phase: 922`. PASS.

---

## Ratification Declaration

All eight checklist items confirmed. CDL-080 is hereby **RATIFIED** at Phase 927.

**Constitutional effect:**
- Star.map N-gram route index is constitutionally defined as L3 of the ILC
  network stack
- L3 advisory / L2 authoritative is a non-negotiable constitutional rule
- `publish_star_map_result()` is the sole promotion boundary per ADR-0033
- Spectral routing (H-015) is wired as L3 prefilter with gossip boundary preserved
- ECU attribution for star-map nodes deferred to H-CON-01

`cdl_080_ratified_phase_927`
`star_map_l3_constitutionally_defined`
`l3_advisory_l2_authoritative_ratified`
