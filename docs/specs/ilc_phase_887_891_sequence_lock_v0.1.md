# ILC Phase 887–891 Sequence Lock v0.1

Status: locked
Date: 2026-04-27
Phase: 887
Owner lane: Truth primitive read-path query integration — CDL-042 extension

`window_887_891_sequence_lock`
`truth_primitive_query_window_commissioned`
`cdl_075_write_path_precedes_read_path_query`

---

## 1. Window Purpose

Window 887–891 closes the submit→persist→query loop by extending the ILC CLI
`query` command to read persisted truth primitive nodes and edges from the
CDL-075 LMDB graph store.

This window does NOT require a new CDL — it is an implementation extension of
the CDL-042 CLI framework (Phase 420) using the CDL-075 graph store (Phase 884).

New subcommands added under `ilc query`:
- `ilc query truth-node --node-id <cid>` — retrieve a persisted truth primitive
  node record by its CIDv1 identifier
- `ilc query truth-edges --node-id <cid>` — list all edges whose source or
  target matches the given node identifier

Both subcommands activate the CDL-075 LMDB graph store via
`ILC_TRUTH_GRAPH_STORE_PATH` and fall back to a `not_found` error when the
env var is absent or the node does not exist.

---

## 2. Prerequisite State

| Item | Status at Window Open |
|------|-----------------------|
| CDL-042 | Ratified (Phase 407) — CLI framework |
| CDL-075 | Ratified (Phase 884) — LMDB graph store write path |
| `truth_primitive_graph_store.py` | Deployed (Phase 880) |
| `main.py` query subcommand | Deployed (Phase 420) — JSON backend |
| Network delivery | Not yet — Phase 892+ separate CDL |

---

## 3. Hard Pass Condition

Window 887–891 passes only if ALL of the following are true:

1. A new `ilc_core/cli/d2e_query_truth_cli.py` module exists.
2. `D2E_QUERY_TRUTH_CLI_VERSION` and `CDL_075_DEPENDENCY` tokens present.
3. `handle_query_truth_node(node_id, store_path)` returns the canonical node
   record for a known CIDv1, raises a typed error for unknown CIDv1.
4. `handle_query_truth_edges(node_id, store_path)` returns all edges where
   source or target matches the given node identifier.
5. `main.py` registers `truth-node` and `truth-edges` as subcommands of
   `query` and routes to the new module.
6. The existing JSON-backed `query node`, `query epoch`, and `query claim`
   subcommands are untouched.
7. Both subcommands return a typed error (not a crash) when
   `ILC_TRUTH_GRAPH_STORE_PATH` is absent.
8. Tests cover: node lookup hit/miss, edges lookup, absent store path,
   main.py wiring, and dependency token presence.
9. The window does NOT implement network delivery, compaction, or mutation
   of the LMDB store via the query path.

`window_887_891_hard_pass_condition`

---

## 4. Phase Map

| Phase | Topic | Deliverable |
|-------|-------|-------------|
| 887 | Sequence lock | This document |
| 888 | `d2e_query_truth_cli.py` | Query handlers + typed errors |
| 889 | `main.py` wiring | `truth-node` and `truth-edges` subcommands |
| 890 | Tests + coherence report + capsule v5.26 | `test_phase_888_891_query_truth_cli.py`; coherence report; capsule |
| 891 | Closure gate | Gate document; window closed |

---

## 5. Scope Boundaries

This window DOES:
- Add `ilc_core/cli/d2e_query_truth_cli.py`.
- Add `truth-node` and `truth-edges` as `query` subcommands in `main.py`.

This window does NOT:
- Add a write path via the query command.
- Implement network delivery or P2P propagation of query results.
- Modify the existing JSON-backed `query node/epoch/claim` handlers.
- Modify `truth_primitive_graph_store.py` (CDL-075 intact).
- Open a new CDL.
- Change M-009.

---

## 6. Exclusion Tokens

```
no_write_path_via_query_in_window_887_891
no_network_delivery_in_window_887_891
no_json_query_handler_mutation_in_window_887_891
no_new_cdl_in_window_887_891
no_m009_change_in_window_887_891
```
