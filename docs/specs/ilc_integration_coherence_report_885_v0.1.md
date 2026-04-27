# ILC Integration Coherence Report — Phase 885

Status: final
Date: 2026-04-27
Window: 877–886
Phase: 885

---

## 1. Purpose

This report verifies that Window 877–886 is internally coherent and that
CDL-075 (truth primitive graph persistence) integrates cleanly with the
existing CDL-074 runtime, CDL-052 Popperian gate, CDL-042 CLI framework,
and the LMDB infrastructure.

---

## 2. Scope of Changes

| File | Role |
|------|------|
| `docs/specs/ilc_phase_877_886_sequence_lock_v0.1.md` | Window sequence lock (Phase 877) |
| `docs/specs/ilc_cdl_075_truth_primitive_graph_persistence_opening_878_v0.1.md` | CDL-075 opening (Phase 878) |
| `ilc_core/epistemic/truth_primitive_graph_store.py` | Graph store runtime (Phases 879–881) |
| `ilc_core/cli/d2e_submit_cli.py` | CLI extension for CDL-075 (Phase 882) |
| `tests/test_phase_879_886_truth_primitive_graph_store.py` | 31 tests (Phase 882) |
| `docs/specs/ilc_cdl_075_truth_primitive_graph_persistence_ratification_evidence_883_v0.1.md` | Ratification evidence (Phase 883) |
| `docs/specs/ilc_constitutional_decision_log_v0.1.md` | CDL-074 backfill + CDL-075 ratification (Phase 884) |

---

## 3. Coherence Checks

### 3.1 CDL-074 runtime untouched

`truth_primitive_submission_runtime.py` is unchanged in this window.
The `validate_truth_primitive_submission` function is the authority for
envelope validation; the graph store receives its `TruthPrimitiveResult`
only after CDL-074 has accepted the submission.

Token: `no_cdl_074_mutation_in_window_877_886` satisfied.

### 3.2 CDL-052 untouched

`node_submission_runtime.py` (CDL-052) is unchanged.

Token: `no_cdl_052_mutation_in_window_877_886` satisfied.

### 3.3 CIDv1 derivation uses existing infrastructure

`node_id_from_obj` from `ilc_core/encoding/cidv1.py` is used without
modification.  The canonical node record is a deterministic DAG-CBOR-
encodable dict satisfying all `node_id_from_obj` invariants (str keys,
no float values, sorted).

### 3.4 LMDB infrastructure pattern followed

`TruthPrimitiveGraphStore` extends `_LmdbRuntimeBase` from
`ilc_core/storage/lmdb_public_runtime.py` exactly as `LmdbGraphStore`,
`LmdbWalletStore`, and `LmdbPublicReceiptStore` do.  No new LMDB
infrastructure was introduced.

### 3.5 CLI extension is backward compatible

`d2e_submit_cli.py` is modified to check `ILC_TRUTH_GRAPH_STORE_PATH`.
When the env var is absent (the default), behaviour is identical to Phase 874:
`node_id = null`, `graph_persistence = "deferred — CDL-075 graph store path
not configured"`.  The 20 Phase 874 pre-commit tests continue to pass.

`node_id` is now included in the result dict (previously absent) — this is
a non-breaking addition since the field is `null` when no store is configured.

### 3.6 Idempotency guarantee closes the duplicate-write risk

`put_node_if_absent` and `put_edge_if_absent` perform the read-and-write in
a single LMDB write transaction, providing atomic idempotency without a
separate lock.  Test `test_write_twice_returns_same_node_id` verifies the
guarantee end-to-end.

### 3.7 Edge-only writes correctly handle all four non-creating primitives

`validate.claim`, `contradict.assert`, `link.claim`, and `refute.claim` all
reach `result.creates_node = False`.  The write path skips node derivation
and writes only to the `b"edges"` database.  Verified by six primitive-
specific tests plus `test_edge_only_writes_no_node_db_entry`.

### 3.8 Test coverage

31 tests in `test_phase_879_886_truth_primitive_graph_store.py` — all pass.
Phase 874 tests: 22 still pass (no regressions).
CDL-074 runtime tests: 67 still pass.

---

## 4. Forward Obligations Closed

| Obligation | Status |
|------------|--------|
| Truth primitive graph persistence (CDL-075) | CLOSED — Phase 884 |

---

## 5. Open Forward Obligations Carried Forward

| Obligation | Next window |
|------------|-------------|
| Network-layer delivery of persisted truth primitive records | Phase 887+ |
| Read-path query integration (ilc query → LMDB graph store) | Phase 887+ |
| Cross-epoch compaction / snapshot export | Deferred |
| HB-002 (P2P bootstrap distribution) | RC2+ |
| CDL-070 (PQ migration ceremony) | Deferred |

---

## 6. Coherence Verdict

Window 877–886 is coherent.  All scope boundaries observed.  All exclusion
tokens satisfied.  31 new tests pass.  No regressions.

`window_877_886_coherence_verified`
