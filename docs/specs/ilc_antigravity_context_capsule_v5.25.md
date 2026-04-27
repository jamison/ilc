# ILC Antigravity Context Capsule v5.25

Supersedes: docs/specs/ilc_antigravity_context_capsule_v5.24.md
Date: 2026-04-27
Owner lane: Window 877–886 — CDL-075 truth primitive graph persistence

`capsule_v5_25_supersedes_v5_24`
`window_877_886_closed_recorded_in_capsule_v5_25`
`cdl_075_ratified_recorded_in_capsule_v5_25`

This capsule is self-contained.

---

## 1. Current Frontier State

**Window 877–886 — COMPLETE.**

| Phase | Topic | Key outcome |
|-------|-------|-------------|
| 877 | Sequence lock | Window 877–886 commissioned |
| 878 | CDL-075 opening | Write path only; Option B proposed |
| 879–881 | `truth_primitive_graph_store.py` | Node schema + CIDv1 + LMDB write + idempotency |
| 882 | CLI wiring + tests | `d2e_submit_cli.py` extended; 31 tests |
| 883 | CDL-075 ratification evidence | All 10 items satisfied |
| 884 | CDL-075 ratification | CDL master log updated |
| 885 | Coherence report + capsule v5.25 | This phase |
| 886 | Closure gate | Gate document; window closed |

**Previous windows:**
- Window 873–876 COMPLETE. CLI `submit` command wired. 251 tests.
- Window 863–872 COMPLETE. CDL-074 ratified (Phase 870). 229 tests.

---

## 2. Option B Status (unchanged)

`option_b_selected_by_human_authorization_2026_04_23`
`adr_0028_posture=option_b`

---

## 3. CDL Status

| CDL | Status | Phase | Note |
|-----|--------|-------|------|
| CDL-001 | Open (genesis_blocker) | — | Packaging track |
| CDL-017 | Ratified | 765 | — |
| CDL-042 | Ratified | 407 | CLI framework |
| CDL-043 | Ratified | 395 | **Tier 2 (CDL-071)** |
| CDL-044 | Ratified | 399 | **Tier 2 (CDL-071)** |
| CDL-052 | Ratified | 466 | Popperian gate — intact |
| CDL-068 | Ratified | 743 | — |
| CDL-069 | Ratified | 838j | — |
| CDL-070 | Deferred | — | PQ migration |
| CDL-071 | Ratified | 851 | Temporal tier reconciliation |
| CDL-072 | Ratified | 846 | Bound B formula amendment |
| CDL-073 | Ratified | 860 | RC1 homoiconic bootstrap schema |
| CDL-074 | Ratified | 870 | Truth primitive runtime |
| CDL-075 | **Ratified** | 884 | Truth primitive graph persistence |
| CDL-V1 | Ratified | 330 | **Tier 2 (CDL-071)** |

---

## 4. CDL-075 Deliverable

**New module:** `ilc_core/epistemic/truth_primitive_graph_store.py`

```python
TRUTH_PRIMITIVE_GRAPH_STORE_VERSION = "truth_primitive_graph_store_880.v0.1"
CDL_075_DEPENDENCY = "cdl_075_truth_primitive_graph_persistence.v0.1"

def node_record_from_submission(envelope, result) -> dict:
    # Canonical node record: agent_id, cdl_version, epoch, payload,
    # primitive, primitive_type — DAG-CBOR encodable, sorted keys

def node_id_from_submission(envelope, result) -> str:
    # CIDv1 = node_id_from_obj(canonical_node_record)

class TruthPrimitiveGraphStore(_LmdbRuntimeBase):
    # b"nodes": CIDv1 → JSON node record (put_if_absent)
    # b"edges": "{src}:{type}:{tgt}" → JSON edge record (put_if_absent)

def write_truth_primitive_result(store, envelope, result) -> dict:
    # Persists node + edges; returns {node_id, nodes_written, edges_written}
```

**CLI extension:** `ILC_TRUTH_GRAPH_STORE_PATH` env var activates persistence.
Without it, Phase 874 deferred behaviour is unchanged.

**Test coverage:** 31 tests in `tests/test_phase_879_886_truth_primitive_graph_store.py`

---

## 5. Test Count

| Scope | Tests |
|-------|-------|
| Window 877–886 (CDL-075) | 31 |
| Window 873–876 (CLI submit) | 22 |
| Window 863–872 (CDL-074 runtime) | 67 |
| Prior windows | 162 |
| **Total** | **282** |

---

## 6. HB Obligation Status (unchanged)

| Obligation | Status |
|------------|--------|
| HB-001 | **CLOSED** (CDL-073, Phase 860) |
| HB-002 | RC2+ — enabled |
| HB-003 | **CLOSED** (CDL-073, Phase 860) |

---

## 7. Forward Obligations

| Item | Priority | Status |
|------|----------|--------|
| Network-layer delivery of persisted truth primitive records | Phase 887+ | CDL-076 required |
| Read-path query integration (ilc query → LMDB graph store) | Phase 887+ | — |
| Cross-epoch compaction / snapshot export | Deferred | — |
| HB-002 (P2P bootstrap distribution) | RC2+ | Enabled after CDL-073 |
| CDL-070 (PQ migration ceremony) | Deferred | SIM-MONETARY-01 prerequisite |
