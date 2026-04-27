# ILC Phase 863–872 Sequence Lock v0.1

Status: locked
Date: 2026-04-27
Phase: 863
Owner lane: RC1 truth primitive runtime — CDL-074

`window_863_872_sequence_lock`
`truth_primitive_runtime_window_commissioned`
`cdl_073_schema_precedes_cdl_074_runtime`
`cdl_052_mode_routing_precedes_truth_primitive_verb_routing`

---

## 1. Window Purpose

Window 863–872 delivers the CDL-074 runtime extension that allows the epistemic
graph to process all six agent-issuable truth primitive submission verbs defined
by CDL-073:

- `assert.truth` — agent asserts a new truth claim; creates node + provenance edges
- `validate.claim` — agent endorses an existing node; creates validated_by edge
- `contradict.assert` — agent signals two nodes contradict; creates contradicts edge
- `refute.claim` — agent formally refutes a node (CDL-052 criterion required)
- `revise.assert` — agent proposes revision of existing node; creates revision edges
- `link.claim` — agent asserts typed semantic relationship; creates typed edge

`commit.epoch` is consensus-layer only and remains outside the agent submission
pipeline. It is NOT implemented in this window.

The CDL-073 wire format (`{v, primitive, agent_id, epoch, payload, sig}`) is the
authoritative submission envelope for this window. The existing CDL-052
`node_submission_runtime.py` (Phase 477, mode-1/2/3 routing) is a parallel
track that remains intact and unmodified.

---

## 2. Prerequisite State

| Item | Status at Window Open |
|------|-----------------------|
| CDL-073 | Ratified (Phase 860) — wire format + schema locked |
| CDL-052 | Ratified (Phase 466) — epistemic mode routing intact |
| CDL-034 | Ratified (Phase 349) — `ALLOWED_PRIMITIVE_TYPES` stable |
| `SYSTEM_PRIMITIVE_TYPES` | Deployed (Phase 858) — disjoint from agent-issuable set |
| `ilc_core/genesis/assertion_schema.py` | Deployed (Phase 858) |
| `ilc_layer_0_bundle_schema_section_v0.1.json` | Deployed (Phase 859) |
| `node_submission_runtime.py` (CDL-052) | Phase 477 — mode-1/2/3 routing; unchanged by this window |
| Full seven primitive runtime | Not yet deployed — this window's deliverable |
| `commit.epoch` agent submission | Permanently excluded (consensus-layer only) |

---

## 3. Hard Pass Condition

Window 863–872 passes only if ALL of the following are true:

1. CDL-074 is opened with scope, option inventory, and evidence checklist.
2. CDL-074 is ratified with all evidence items satisfied.
3. A new Python runtime module (`ilc_core/epistemic/truth_primitive_submission_runtime.py`)
   implements payload validation and graph-output specification for all six
   agent-issuable truth primitives (`assert.truth`, `validate.claim`,
   `contradict.assert`, `refute.claim`, `revise.assert`, `link.claim`).
4. `commit.epoch` is explicitly rejected by the agent submission pipeline
   with a machine-readable error token.
5. `refute.claim` correctly enforces the CDL-052 refutation criterion
   (`has_falsifiable_test must be true`).
6. The existing CDL-052 `node_submission_runtime.py` is NOT modified. Both
   runtimes coexist in the same package without collision.
7. All six primitives produce correct graph-output specifications (node creation
   flag, edge type list, source/target semantics) consistent with CDL-073 §4
   (`ilc_layer_0_bundle_schema_section_v0.1.json`).
8. Test coverage for all six primitives: valid paths, invalid paths, and CDL-073
   dependency token present.
9. The window does NOT deploy `commit.epoch` agent submission.
10. The window does NOT claim that graph persistence, CID generation, or
    network-layer delivery of truth primitive bundles is implemented — the
    runtime module specifies and validates the submission shape and graph output
    contract only.

`window_863_872_hard_pass_condition`

---

## 4. Sequencing Constraints

```
cdl_073_ratified_precedes_cdl_074_opening
cdl_074_opening_precedes_truth_primitive_runtime_implementation
assert_truth_and_validate_claim_precede_contradict_and_link
refute_claim_precedes_revise_assert
refute_claim_integrates_cdl_052_criterion
historical_hardening_precedes_ratification
coherence_report_precedes_closure_gate
```

`assert.truth` and `validate.claim` are implemented first because they are the
canonical base cases (one creates a node, one creates an edge on an existing
node). `contradict.assert` and `link.claim` follow (both edge-only, no new
nodes). `refute.claim` follows (edge-only, but requires CDL-052 criterion
integration). `revise.assert` is last (creates a new node with multi-edge
revision linkage — most complex).

---

## 5. Phase Map

| Phase | Topic | Deliverable |
|-------|-------|-------------|
| 863 | Sequence lock | This document |
| 864 | CDL-074 opening | CDL document opened; scope, option inventory, evidence checklist |
| 865 | `assert.truth` + `validate.claim` runtime | `truth_primitive_submission_runtime.py` (partial); tests |
| 866 | `contradict.assert` + `link.claim` runtime | Module extended; tests |
| 867 | `refute.claim` runtime | CDL-052 criterion integration; `commit.epoch` rejection; tests |
| 868 | `revise.assert` runtime | Module complete; full six-primitive coverage; tests |
| 869 | Integration tests + historical hardening | Cross-CDL regression; 073/052/034 all pass |
| 870 | CDL-074 ratification | Evidence checklist satisfied; CDL master log updated |
| 871 | Coherence report + capsule v5.23 | Coherence report 871; capsule v5.23 |
| 872 | Closure gate | Gate document; window closed |

---

## 6. Scope Boundaries

This window DOES:
- Implement payload validation for all six agent-issuable truth primitives.
- Implement the graph-output contract specification for each primitive (what
  nodes and edges are produced, with source/target semantics).
- Enforce `commit.epoch` rejection from the agent submission pipeline.
- Integrate `refute.claim` with the existing CDL-052 refutation criterion.
- Ratify CDL-074 to constitutionally lock the runtime extension.

This window does NOT:
- Implement graph persistence, CIDv1 generation, or LMDB storage for
  truth primitive graph nodes and edges.
- Implement network-layer delivery of truth primitive bundles (HTTP transport,
  gossip dissemination).
- Deploy `commit.epoch` agent submission under any path.
- Modify `node_submission_runtime.py` (CDL-052 mode-1/2/3 routing).
- Migrate Rust `config.rs` genesis loading to truth-primitive objects.
- Advance HB-002 (P2P bootstrap distribution).
- Advance CDL-070.
- Change the live M-009 network in any way.

---

## 7. Module Architecture

**New module:** `ilc_core/epistemic/truth_primitive_submission_runtime.py`

```
CDL_074_DEPENDENCY = "cdl_074_truth_primitive_runtime_ratified.v0.1"
CDL_073_DEPENDENCY = "cdl_073_homoiconic_bootstrap_schema_ratified.v0.1"
CDL_052_DEPENDENCY = "cdl_052_ratified_466.v0.1"

TRUTH_PRIMITIVE_RUNTIME_VERSION = "truth_primitive_submission_runtime_868.v0.1"

AGENT_ISSUABLE_PRIMITIVES = frozenset({
    "assert.truth", "validate.claim", "contradict.assert",
    "refute.claim", "revise.assert", "link.claim",
})
# commit.epoch excluded — consensus layer only
```

**Key functions:**
- `validate_truth_primitive_submission(envelope: dict) -> TruthPrimitiveResult`
  Routes to per-primitive validator; rejects `commit.epoch` with
  `token="commit_epoch_agent_submission_rejected"`.
- Per-primitive validators: `_validate_assert_truth`, `_validate_validate_claim`,
  `_validate_contradict_assert`, `_validate_refute_claim`, `_validate_revise_assert`,
  `_validate_link_claim`.
- `TruthPrimitiveResult` dataclass: `primitive`, `creates_node`, `edges` (list of
  `EdgeSpec`), `node_primitive_type` (None if no node created).
- `EdgeSpec` dataclass: `edge_type`, `source`, `target`.

**Coexistence rule:** Both `truth_primitive_submission_runtime.py` and
`node_submission_runtime.py` live in `ilc_core/epistemic/`. They share
`EpistemicSubmissionError` from `node_submission_runtime.py` (imported, not
redefined). No circular imports.

---

## 8. CDL-074 Scope Preview

CDL-074 will constitute:
- Authorization to deploy the six agent-issuable truth primitive submission
  handlers in the Python runtime layer.
- The `commit.epoch` permanent exclusion from agent submission (consensus-only
  declaration).
- The graph-output contract for all six primitives as a constitutional lock.

Dependencies: CDL-073 (wire format), CDL-052 (refutation criterion),
CDL-034 (ALLOWED_PRIMITIVE_TYPES boundary — not extended by CDL-074).

---

## 9. Exclusion Tokens

```
no_commit_epoch_agent_submission_in_window_863_872
no_graph_persistence_in_window_863_872
no_cid_generation_in_window_863_872
no_network_delivery_in_window_863_872
no_cdl_052_mutation_in_window_863_872
no_hb_002_in_window_863_872
no_cdl_070_in_window_863_872
no_m009_change_in_window_863_872
no_rust_config_migration_in_window_863_872
```

---

## 10. Dependency Bundle

Every Phase 863–872 artifact must carry or reference:

- `docs/specs/ilc_phase_853_862_sequence_lock_v0.1.md` (prior window)
- `docs/specs/ilc_layer_0_bundle_schema_section_v0.1.json` (CDL-073 schema)
- `ilc_core/genesis/assertion_schema.py` (CDL-073 runtime)
- `docs/specs/ilc_antigravity_context_capsule_v5.22.md`
