# ILC CDL-075 Ratification Evidence — Phase 883

Status: ratification_ready
Date: 2026-04-27
Phase: 883
CDL: CDL-075 — Truth Primitive Graph Persistence

`cdl_075_ratification_evidence_883`

---

## 1. Evidence Checklist Satisfaction

### Evidence Item 1 — Module exists and imports cleanly

File: `ilc_core/epistemic/truth_primitive_graph_store.py`

Exists: ✅  
Imports cleanly (verified by test `test_graph_store_module_imports_cleanly`): ✅

### Evidence Item 2 — TRUTH_PRIMITIVE_GRAPH_STORE_VERSION token

```python
TRUTH_PRIMITIVE_GRAPH_STORE_VERSION = "truth_primitive_graph_store_880.v0.1"
```

Token present (verified by test `test_graph_store_version_token_correct`): ✅

### Evidence Item 3 — CDL_075_DEPENDENCY and CDL_074_DEPENDENCY tokens

```python
CDL_075_DEPENDENCY = "cdl_075_truth_primitive_graph_persistence.v0.1"
CDL_074_DEPENDENCY = "cdl_074_truth_primitive_runtime_ratified.v0.1"
```

Both tokens present (verified by tests `test_cdl_075_dependency_token_correct`,
`test_cdl_074_dependency_token_correct`): ✅

### Evidence Item 4 — node_record_from_submission deterministic schema

`node_record_from_submission(envelope, result)` returns a dict with exactly
these keys: `agent_id`, `cdl_version`, `epoch`, `payload`, `primitive`,
`primitive_type`.

- `cdl_version` = `"cdl_075.v0.1"`
- All keys are strings (required for `node_id_from_obj`)
- Deterministic: identical inputs always produce identical output
- Raises `ValueError` for edge-only primitives

Tests: `test_node_record_assert_truth_has_required_fields`,
`test_node_record_revise_assert_has_required_fields`,
`test_node_record_rejects_edge_only_primitive`,
`test_node_record_is_deterministic` ✅

### Evidence Item 5 — node_id_from_submission CIDv1 derivation

CIDv1 derivation rule (CDL-075 §2.2):
```python
node_id = node_id_from_obj(canonical_node_record)
```

- Returns a `"b"`-prefixed base32 lowercase CIDv1 string
- Deterministic: same submission → same CIDv1
- Different content → different CIDv1
- Raises for edge-only primitives

Tests: `test_node_id_assert_truth_is_cidv1_string`,
`test_node_id_is_deterministic`,
`test_node_id_different_for_different_content`,
`test_node_id_rejects_edge_only_primitive` ✅

### Evidence Item 6 — TruthPrimitiveGraphStore LMDB layout

`TruthPrimitiveGraphStore` extends `_LmdbRuntimeBase` with:
- `b"nodes"` — CIDv1 key → JSON canonical node record
- `b"edges"` — `"{source}:{edge_type}:{target}"` key → JSON edge record

`put_node_if_absent` and `put_edge_if_absent` use LMDB read-within-write-txn
to enforce put-if-absent semantics atomically.

Tests: `test_graph_store_opens_and_closes`,
`test_graph_store_put_and_get_node`,
`test_graph_store_put_and_get_edge` ✅

### Evidence Item 7 — write_truth_primitive_result for all six primitives

| Primitive | creates_node | nodes_written | edges_written |
|-----------|-------------|---------------|---------------|
| assert.truth | True | 1 | ≥1 |
| validate.claim | False | 0 | 1 |
| contradict.assert | False | 0 | 1 |
| link.claim | False | 0 | 1 |
| refute.claim | False | 0 | 3 (refuted_by + 2×supported_by) |
| revise.assert | True | 1 | 3 (asserted_by + revision_of + revised_by) |

Tests: `test_write_assert_truth_creates_node_and_edges`,
`test_write_validate_claim_edge_only`,
`test_write_contradict_assert_edge_only`,
`test_write_link_claim_edge_only`,
`test_write_refute_claim_edge_only_with_evidence`,
`test_write_revise_assert_creates_node_and_edges` ✅

### Evidence Item 8 — Idempotency

Calling `write_truth_primitive_result` twice with identical input:
- Returns the same `node_id` both times
- `nodes_written = 0` on second call (record already present)
- `edges_written = 0` on second call (edges already present)

Tests: `test_write_twice_returns_same_node_id`,
`test_put_node_if_absent_idempotent` ✅

### Evidence Item 9 — CLI integration with ILC_TRUTH_GRAPH_STORE_PATH

When `ILC_TRUTH_GRAPH_STORE_PATH` is set:
- `handle_submit` opens `TruthPrimitiveGraphStore` at that path
- Calls `write_truth_primitive_result`
- Returns `node_id` (CIDv1) and `graph_persistence: "persisted"` in result

When `ILC_TRUTH_GRAPH_STORE_PATH` is absent:
- `node_id` is `null`
- `graph_persistence` contains `"deferred"`
- Behaviour identical to Phase 874

Persisted nodes are readable back from the LMDB store.

Tests: `test_submit_cli_with_store_path_returns_node_id`,
`test_submit_cli_without_store_path_defers_persistence`,
`test_submit_cli_store_path_persisted_node_readable` ✅

### Evidence Item 10 — Edge-only path for non-creating primitives

For `validate.claim`, `contradict.assert`, `link.claim`, `refute.claim`:
- `node_id = None`
- `nodes` LMDB database remains empty
- Only `edges` LMDB database receives writes

Tests: `test_edge_only_writes_no_node_db_entry`,
`test_edge_key_format_correct` ✅

---

## 2. Test Count

31 tests in `tests/test_phase_879_886_truth_primitive_graph_store.py` — all pass.

---

## 3. Option B Selection

CDL-075 implements Option B: runtime contract only (write path).  No read-path
query integration, no network delivery, no cross-epoch compaction.

---

## 4. Ratification Readiness

All 10 evidence items satisfied.  CDL-075 is ready for ratification at Phase 884.

`cdl_075_ratification_evidence_satisfied_883`
