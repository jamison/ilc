# ILC CDL-075 — Truth Primitive Graph Persistence — Opening Phase 878

Status: open
Date: 2026-04-27
Phase: 878
Owner lane: Window 877–886

`cdl_075_truth_primitive_graph_persistence_opened_878`

---

## 1. Motivation

CDL-074 (Phase 870) deployed the truth primitive submission runtime, which
validates a CDL-073 wire-format submission and returns a `TruthPrimitiveResult`
(graph-output contract) but does NOT persist anything.  CDL-075 closes this
gap by defining the durable write contract for truth primitive submissions.

---

## 2. Proposed Scope (Option B — Runtime Contract Only)

CDL-075 governs the write path only.  It does NOT govern the read path, query
integration, network delivery, or compaction.

### 2.1 Canonical Node Record

A deterministic Python dict that encodes the submitted truth primitive for
durable storage and CIDv1 derivation.  Minimum required fields:

| Field | Type | Semantics |
|-------|------|-----------|
| `cdl_version` | str | `"cdl_075.v0.1"` — protocol version tag |
| `primitive` | str | e.g. `"assert.truth"` |
| `agent_id` | str | submitting agent's canonical agent_id |
| `epoch` | int | submission epoch (non-negative integer) |
| `payload` | dict | verbatim payload from the CDL-073 envelope |
| `primitive_type` | str \| null | `node_primitive_type` from `TruthPrimitiveResult`; null for edge-only primitives |

All keys must be str (required by `node_id_from_obj`).  All values must be
DAG-CBOR encodable.  Keys are sorted deterministically for encoding.

### 2.2 CIDv1 Derivation Rule

```python
from ilc_core.encoding.cidv1 import node_id_from_obj

node_id = node_id_from_obj(canonical_node_record)
```

This rule is final and MUST NOT be altered without a CDL amendment.  The
idempotency guarantee follows directly: identical content → identical CIDv1.

Only primitives where `result.creates_node is True` derive a node_id.
Edge-only primitives (`validate.claim`, `contradict.assert`, `link.claim`,
`refute.claim`) produce edge writes only.

### 2.3 LMDB Database Layout

Two named databases within a single LMDB environment:

| DB name (bytes) | Key format | Value format |
|-----------------|------------|--------------|
| `b"nodes"` | CIDv1 string (UTF-8) | JSON-encoded canonical node record |
| `b"edges"` | `"{source}:{edge_type}:{target}"` (UTF-8) | JSON-encoded edge record |

Edge record fields: `edge_type`, `source`, `target`, `agent_id`, `epoch`.

The `source` and `target` fields in edge records use the semantic labels from
`EdgeSpec` (e.g. `"new_node_id"`, `"agent_id"`, `"parent_node_id"`).  For
persisted edges the resolved form carries the actual CIDv1 or agent_id value.

### 2.4 Idempotency Contract

`write_truth_primitive_result` uses `put_if_absent` semantics for nodes: if
a node with the computed CIDv1 already exists in the `nodes` db, the write is
skipped and the existing CIDv1 is returned.  Edges use the same pattern.

### 2.5 Epoch Tagging

All node and edge records carry the submission `epoch` for audit purposes.

---

## 3. Evidence Checklist (10 items)

The following must be satisfied for CDL-075 ratification:

1. `ilc_core/epistemic/truth_primitive_graph_store.py` exists and imports cleanly.
2. `TRUTH_PRIMITIVE_GRAPH_STORE_VERSION` token present.
3. `CDL_075_DEPENDENCY` token present and validated at import.
4. `node_record_from_submission(envelope, result)` returns a deterministic dict
   matching the canonical node record schema (§2.1).
5. `node_id_from_submission(envelope, result)` returns a CIDv1 string for
   node-creating primitives; raises for edge-only primitives.
6. `TruthPrimitiveGraphStore` wraps `_LmdbRuntimeBase` with `b"nodes"` and
   `b"edges"` named databases.
7. `write_truth_primitive_result(store, envelope, result)` persists correctly
   for all six primitives (4 edge-only, 2 node-creating: assert.truth and
   revise.assert).
8. Idempotency: calling `write_truth_primitive_result` twice with identical
   input returns the same CIDv1 without raising or duplicating.
9. `d2e_submit_cli.py` calls `write_truth_primitive_result` and returns
   `node_id` when `ILC_TRUTH_GRAPH_STORE_PATH` is set.
10. Tests cover all six primitives, CIDv1 determinism, idempotency, edge-only
    path, and CLI integration.

---

## 4. Exclusions

- No read-path / query integration.
- No network delivery.
- No cross-epoch compaction or snapshot export.
- No modification to CDL-074 runtime or CDL-052 (both intact).
- No modification to `node_submission_runtime.py`.

---

## 5. Status

Open — Phase 878.  Ratification target: Phase 884.

`cdl_075_open_at_phase_878`
