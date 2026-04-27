# ILC Integration Coherence Report — Phase 890

Status: final
Date: 2026-04-27
Window: 887–891
Phase: 890

---

## 1. Purpose

This report verifies that Window 887–891 is internally coherent and that the
truth primitive read-path query integration connects cleanly to the CDL-075
LMDB graph store without disturbing the existing JSON-backed query handlers.

---

## 2. Scope of Changes

| File | Role |
|------|------|
| `docs/specs/ilc_phase_887_891_sequence_lock_v0.1.md` | Window sequence lock (Phase 887) |
| `ilc_core/cli/d2e_query_truth_cli.py` | Query handlers (Phase 888) |
| `ilc_core/cli/main.py` | truth-node/truth-edges subcommands (Phase 889) |
| `tests/test_phase_888_891_query_truth_cli.py` | 23 tests (Phase 890) |

---

## 3. Coherence Checks

### 3.1 CDL-075 graph store untouched

`truth_primitive_graph_store.py` is unchanged in this window.  The query
handlers call `store.get_node()` and `store.iter_edges()` — read-only
operations — and never call any write method.

Token: `no_write_path_via_query_in_window_887_891` satisfied.

### 3.2 Existing JSON-backed query handlers untouched

`_run_query_subcommand` now dispatches truth-node/truth-edges before loading
the JSON graph state, so the existing `node`, `epoch`, and `claim` branches
are unreachable from truth query paths.  The original handlers are called
only for their own subcommands.  All existing query tests continue to pass.

Token: `no_json_query_handler_mutation_in_window_887_891` satisfied.

### 3.3 Absent store path is graceful

Both handlers call `_require_store_path()`, which raises `QueryTruthCommandError`
with token `query_truth_store_path_not_configured` before opening any file.
The CLI dispatch translates this to a `QueryCommandError`, producing a
JSON error response with exit code 1 — no crash, no stack trace.

### 3.4 No new CDL

This window is a CDL-042 framework extension.  No new CDL was opened.

Token: `no_new_cdl_in_window_887_891` satisfied.

### 3.5 Test coverage

23 tests in `test_phase_888_891_query_truth_cli.py` — all pass.

---

## 4. Forward Obligations Closed

| Obligation | Status |
|------------|--------|
| Read-path query integration (ilc query → LMDB graph store) | CLOSED — Phase 890 |

---

## 5. Open Forward Obligations Carried Forward

| Obligation | Next window |
|------------|-------------|
| Network-layer delivery of persisted truth primitive records | Phase 892+ — CDL-076 required |
| Cross-epoch compaction / snapshot export | Deferred |
| HB-002 (P2P bootstrap distribution) | RC2+ |
| CDL-070 (PQ migration ceremony) | Deferred |

---

## 6. Coherence Verdict

Window 887–891 is coherent.  All scope boundaries observed.  All exclusion
tokens satisfied.  23 new tests pass.  No regressions.

`window_887_891_coherence_verified`
