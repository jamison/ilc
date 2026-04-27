# ILC CDL-074 Truth Primitive Runtime Opening 864 v0.1

Status: open
Date: 2026-04-27
Phase: 864
Owner lane: Window 863–872 — truth primitive runtime

`cdl_074_opened_phase_864`
`truth_primitive_runtime_cdl_opened`

---

## 1. Decision Identity

| Field | Value |
|-------|-------|
| decision_id | `CDL-074` |
| status | `open` |
| opened_phase | `864` |
| opened_date | `2026-04-27` |
| dependencies | CDL-073, CDL-052, CDL-034, CDL-069 |

---

## 2. Problem Statement

CDL-073 (Phase 860) ratified the wire format and schema for all seven ILC truth
primitives. The Python runtime currently has no code that validates a CDL-073
wire format submission (`{v, primitive, agent_id, epoch, payload, sig}`) or that
specifies which graph nodes and edges a given primitive produces.

Without CDL-074, no agent submission pipeline can:
- Route a `validate.claim` submission and know it creates a `validated_by` edge.
- Reject a `contradict.assert` where `node_a_id == node_b_id`.
- Enforce `has_falsifiable_test must be true` for `refute.claim` at the wire
  format layer.
- Block an agent-submitted `commit.epoch` with a machine-readable error token.

CDL-074 constitutionally locks the runtime extension and declares the graph-output
contract for each of the six agent-issuable primitives.

---

## 3. Scope

CDL-074 covers:

1. **Six agent-issuable primitives:** `assert.truth`, `validate.claim`,
   `contradict.assert`, `refute.claim`, `revise.assert`, `link.claim`.
2. **`commit.epoch` rejection:** Permanent constitutional declaration that
   `commit.epoch` is consensus-layer only; agent submission is rejected with
   `token="commit_epoch_agent_submission_rejected"`.
3. **Graph-output contract:** For each primitive, the constitutional lock on
   which nodes are created, which edges are produced, and what their
   source/target semantics are — consistent with CDL-073
   `ilc_layer_0_bundle_schema_section_v0.1.json`.
4. **CDL-052 integration boundary:** `refute.claim` must call the existing
   CDL-052 refutation criterion validator. CDL-074 does not modify CDL-052.
5. **`ALLOWED_PRIMITIVE_TYPES` boundary:** CDL-074 does not extend
   `ALLOWED_PRIMITIVE_TYPES` (CDL-034). The truth primitive verb set and the
   node primitive type set remain distinct by design.

CDL-074 does NOT cover:
- Graph persistence, CIDv1 generation, or LMDB storage.
- Network-layer delivery of truth primitive bundles.
- `commit.epoch` consensus implementation.
- Migration of CDL-052 `node_submission_runtime.py`.
- Rust `config.rs` genesis loading migration.
- HB-002 (P2P bootstrap distribution).

---

## 4. Option Inventory

| Option | Description |
|--------|-------------|
| A — defer | Delay truth primitive runtime until graph persistence is also ready. |
| B — runtime contract only (proposed) | Implement and constitutionally lock the six-primitive submission validator and graph-output contract now. Graph persistence is a subsequent window. |
| C — partial lock (assert.truth only) | Lock only `assert.truth` runtime; defer the remaining five verbs. |

**Proposed option:** B — runtime contract only.

**Rationale:** The wire format is locked (CDL-073). Agents need a validated
submission layer before graph persistence is wired up — the contract must be
constitutionally locked so both the Python implementation and future Rust
runtime can depend on a stable interface. Option A creates unnecessary lag.
Option C produces a dependency chain with five open edges that must be resolved
by additional CDLs — the scopes are cleanly separable within one document.

---

## 5. Evidence Checklist for Ratification

The following items must be satisfied before CDL-074 is ratified:

| # | Evidence item | File |
|---|---------------|------|
| 1 | `truth_primitive_submission_runtime.py` exists | `ilc_core/epistemic/truth_primitive_submission_runtime.py` |
| 2 | `CDL_074_DEPENDENCY` token present in runtime | same file |
| 3 | `AGENT_ISSUABLE_PRIMITIVES` frozenset contains all six | same file |
| 4 | `validate_truth_primitive_submission()` present | same file |
| 5 | `commit.epoch` rejected with `commit_epoch_agent_submission_rejected` | same file + test |
| 6 | All six primitives validated — payload fields + graph-output consistent with CDL-073 schema | same file + tests |
| 7 | `refute.claim` integrates CDL-052 `has_falsifiable_test` enforcement | same file + test |
| 8 | CDL-073 schema section cross-check: each primitive's graph output matches `ilc_layer_0_bundle_schema_section_v0.1.json` | test |
| 9 | `node_submission_runtime.py` (CDL-052) unchanged — coexistence confirmed | test reads Phase 477 version constant |
| 10 | Historical hardening: CDL-034, CDL-052, CDL-073 guard tests all pass without modification | test suite |

---

## 6. Forward Obligations After CDL-074

After CDL-074 ratification, the following remain open:

| Item | Priority |
|------|----------|
| Graph persistence for truth primitive nodes/edges (CIDv1 + LMDB) | Phase 873+ |
| Network-layer delivery of truth primitive bundles | Phase 873+ |
| `commit.epoch` consensus implementation | Separate CDL |
| HB-002 P2P bootstrap distribution | RC2+ |
| CDL-070 PQ migration ceremony | Deferred (SIM-MONETARY-01) |

---

## 7. Non-Goals Confirmation

`no_commit_epoch_agent_submission_in_window_863_872`
`no_graph_persistence_in_window_863_872`
`no_cid_generation_in_window_863_872`
`no_network_delivery_in_window_863_872`
`no_cdl_052_mutation_in_window_863_872`
