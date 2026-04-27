# ILC Phase 877–886 Sequence Lock v0.1

Status: locked
Date: 2026-04-27
Phase: 877
Owner lane: Truth primitive graph persistence — CDL-075

`window_877_886_sequence_lock`
`truth_primitive_graph_persistence_window_commissioned`
`cdl_074_runtime_precedes_graph_persistence_write_path`

---

## 1. Window Purpose

Window 877–886 implements truth primitive graph persistence: the write path
that takes a validated `TruthPrimitiveResult` from the CDL-074 runtime, derives
a deterministic CIDv1 node identifier, and durably stores the canonical node
record and its edges in an LMDB-backed graph store.

This window requires a new CDL (CDL-075) to govern the canonical node record
schema, CIDv1 derivation rule, LMDB database layout, and idempotency contract.

After this window the `submit` CLI command will optionally persist validated
truth primitives when `ILC_TRUTH_GRAPH_STORE_PATH` is set in the environment.

---

## 2. Prerequisite State

| Item | Status at Window Open |
|------|-----------------------|
| CDL-042 | Ratified (Phase 407) — CLI framework |
| CDL-052 | Ratified (Phase 466) — Popperian gate (coexists) |
| CDL-073 | Ratified (Phase 860) — wire format + genesis schema |
| CDL-074 | Ratified (Phase 870) — truth primitive submission runtime |
| `truth_primitive_submission_runtime.py` | Deployed (Phase 868) |
| `d2e_submit_cli.py` | Deployed (Phase 874) |
| `ilc_core/encoding/cidv1.py` | Deployed — `node_id_from_obj` available |
| `ilc_core/storage/lmdb_public_runtime.py` | Deployed — `_LmdbRuntimeBase` available |
| Network delivery | Not yet — Phase 887+ separate CDL |

---

## 3. Hard Pass Condition

Window 877–886 passes only if ALL of the following are true:

1. A new `ilc_core/epistemic/truth_primitive_graph_store.py` module exists.
2. `TRUTH_PRIMITIVE_GRAPH_STORE_VERSION` and `CDL_075_DEPENDENCY` tokens present.
3. `node_id_from_submission(envelope, result)` produces a deterministic CIDv1
   string from the canonical node record; same content always yields same CIDv1.
4. `write_truth_primitive_result(store, envelope, result)` persists nodes and
   edges to LMDB; `validate.claim`, `contradict.assert`, `link.claim`, and
   `refute.claim` (which do not create nodes) produce edge-only writes.
5. The canonical node record is a deterministic dict encodable to DAG-CBOR with
   sorted string keys (consistent with `node_id_from_obj` invariants).
6. Idempotency: writing the same submission twice does not duplicate the record;
   the same CIDv1 is returned on both calls.
7. `d2e_submit_cli.py` calls `write_truth_primitive_result` and returns
   `node_id` in the result when `ILC_TRUTH_GRAPH_STORE_PATH` env var is set.
   When the env var is absent, behaviour is unchanged from Window 873–876.
8. Tests cover: CIDv1 determinism, write + read-back for all six primitives,
   idempotency, edge-only path for non-creating primitives, and CLI integration
   with and without store path.
9. The window does NOT implement network-layer delivery, read-path query
   integration, or cross-epoch compaction.
10. CDL-075 ratification evidence satisfies all 10 evidence checklist items.

`window_877_886_hard_pass_condition`

---

## 4. Phase Map

| Phase | Topic | Deliverable |
|-------|-------|-------------|
| 877 | Sequence lock | This document |
| 878 | CDL-075 opening | CDL-075 opened; Option B proposed; evidence checklist |
| 879 | Canonical node record schema + CIDv1 derivation | `node_record_from_submission()`, `node_id_from_submission()` |
| 880 | LMDB write path | `TruthPrimitiveGraphStore`, `write_truth_primitive_result()` |
| 881 | Idempotency + edge-only writes | Edge records; idempotency guard; read-back helpers |
| 882 | CLI wiring + tests | `d2e_submit_cli.py` extended; `test_phase_879_886_truth_primitive_graph_store.py` |
| 883 | Integration regression | Full regression pass; CDL-075 ratification evidence |
| 884 | CDL-075 ratification | CDL master log updated; Option B ratified |
| 885 | Coherence report + capsule v5.25 | Coherence report 885; capsule v5.25 |
| 886 | Closure gate | Gate document; window closed |

---

## 5. Scope Boundaries

This window DOES:
- Add `ilc_core/epistemic/truth_primitive_graph_store.py`.
- Extend `ilc_core/cli/d2e_submit_cli.py` to call the graph store when
  `ILC_TRUTH_GRAPH_STORE_PATH` is set.
- Open and ratify CDL-075 (canonical node record + LMDB write contract).

This window does NOT:
- Implement network-layer delivery of persisted records.
- Integrate the write path with `ilc query` read commands.
- Implement cross-epoch compaction or snapshot export.
- Modify `truth_primitive_submission_runtime.py` (CDL-074 intact).
- Modify `node_submission_runtime.py` (CDL-052 intact).
- Change M-009.

---

## 6. CDL-075 Scope Preview

CDL-075 will lock:

1. **Canonical node record fields** — the deterministic dict written to LMDB
   and used to derive the CIDv1. Minimum fields: `primitive`, `agent_id`,
   `epoch`, `payload`, `primitive_type` (or `null`), `cdl_version`.
2. **CIDv1 derivation rule** — `node_id = node_id_from_obj(canonical_record)`
   using the existing `ilc_core/encoding/cidv1.py` implementation.
3. **LMDB database layout** — named dbs: `nodes` (key=CIDv1), `edges`
   (key=`{source_cid}:{edge_type}:{target}`).
4. **Idempotency contract** — `put_if_absent` semantics; no overwrite on
   duplicate CIDv1.
5. **Epoch tagging** — all writes carry the submission epoch for audit.

---

## 7. Exclusion Tokens

```
no_network_delivery_in_window_877_886
no_query_read_path_in_window_877_886
no_cross_epoch_compaction_in_window_877_886
no_cdl_074_mutation_in_window_877_886
no_cdl_052_mutation_in_window_877_886
no_m009_change_in_window_877_886
```
