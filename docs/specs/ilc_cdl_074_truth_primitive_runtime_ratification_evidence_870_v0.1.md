# ILC CDL-074 Truth Primitive Runtime Ratification Evidence 870 v0.1

Status: Phase-870 ratification evidence artifact
Date: 2026-04-27
Phase: 870
Owner lane: Window 863–872 — truth primitive runtime

`cdl_074_ratified_phase_870`

---

## 1. Purpose and Scope

Record ratification evidence for CDL-074 using the locked sequence:
- Phase 863: sequence lock
- Phase 864: CDL-074 opening
- Phase 865: `assert.truth` + `validate.claim` runtime
- Phase 866: `contradict.assert` + `link.claim` runtime
- Phase 867: `refute.claim` + `commit.epoch` rejection
- Phase 868: `revise.assert` (module complete)
- Phase 869: integration tests + historical hardening
- Phase 870: ratification evidence (this document)

Scope boundary:
- Mutate only CDL-074 ratification fields in constitutional decision log.
- Do not mutate other CDL-* rows.
- No graph persistence, CID generation, or network delivery implemented.

---

## 2. Evidence Chain Summary

1. `docs/specs/ilc_phase_863_872_sequence_lock_v0.1.md`
2. `docs/specs/ilc_cdl_074_truth_primitive_runtime_opening_864_v0.1.md`
3. `ilc_core/epistemic/truth_primitive_submission_runtime.py` (Phases 865–868)
4. `tests/test_phase_865_872_cdl_074_truth_primitive_runtime.py` (Phase 869)
5. `docs/specs/ilc_layer_0_bundle_schema_section_v0.1.json` (CDL-073 schema)
6. `docs/specs/ilc_constitutional_decision_log_v0.1.md`

---

## 3. CDL-074 Option Inventory and Selection Statement

Option inventory:
- `defer` (Option A)
- `runtime contract only — six-primitive submission validator and graph-output contract` (Option B, proposed)
- `partial lock — assert.truth only` (Option C)

Selection statement:
- Selected option: `runtime contract only` (Option B)
- Rejected options: `defer` (Option A), `partial lock` (Option C)
- Rationale: Wire format is locked (CDL-073). Agents need a validated submission
  layer before graph persistence is wired up. All six agent-issuable primitives
  share the same outer envelope and dependency chain; splitting produces a
  dependency chain without benefit. Option B closes CDL-074 in one
  evidence-checkable CDL.

---

## 4. Evidence Checklist Satisfaction

### Evidence 1 — Runtime module exists (Phase 865)

File: `ilc_core/epistemic/truth_primitive_submission_runtime.py`

Present: ✓

### Evidence 2 — CDL_074_DEPENDENCY token present

`CDL_074_DEPENDENCY = "cdl_074_truth_primitive_runtime_ratified.v0.1"` ✓

Present in: `ilc_core/epistemic/truth_primitive_submission_runtime.py` ✓

### Evidence 3 — AGENT_ISSUABLE_PRIMITIVES contains all six

```python
AGENT_ISSUABLE_PRIMITIVES = frozenset({
    "assert.truth", "validate.claim", "contradict.assert",
    "refute.claim", "revise.assert", "link.claim",
})
```
✓ — `commit.epoch` is NOT in this set.

### Evidence 4 — validate_truth_primitive_submission present

`validate_truth_primitive_submission(submission: Any) -> TruthPrimitiveResult` ✓

### Evidence 5 — commit.epoch rejected

Token: `commit_epoch_agent_submission_rejected` ✓

Test: `test_commit_epoch_agent_submission_rejected` ✓

### Evidence 6 — All six primitives validated

| Primitive | Payload validation | Graph-output contract | Test |
|-----------|-------------------|----------------------|------|
| `assert.truth` | ✓ | creates_node=True, asserted_by + extends edges | ✓ |
| `validate.claim` | ✓ | creates_node=False, validated_by edge | ✓ |
| `contradict.assert` | ✓ | creates_node=False, contradicts edge | ✓ |
| `link.claim` | ✓ | creates_node=False, typed link edge | ✓ |
| `refute.claim` | ✓ | creates_node=False, refuted_by + supported_by edges | ✓ |
| `revise.assert` | ✓ | creates_node=True, asserted_by + revision_of + revised_by edges | ✓ |

### Evidence 7 — refute.claim CDL-052 integration

`has_falsifiable_test` checked before delegating to `_cdl_052_validate_criterion`.
Raises `refute_claim_has_falsifiable_test_required` when False.

Test: `test_refute_claim_has_falsifiable_test_false_rejected` ✓

### Evidence 8 — Graph-output contract consistent with CDL-073 schema

All six primitives cross-checked against `ilc_layer_0_bundle_schema_section_v0.1.json`:
- `creates_node` flag matches schema `graph_output.creates_node` for each ✓
- Edge types consistent with schema `graph_output.edges_produced` for each ✓

Tests: `test_*_graph_output_matches_schema` (6 tests) ✓

### Evidence 9 — CDL-052 node_submission_runtime unchanged

`EPISTEMIC_RUNTIME_PART1_VERSION = "epistemic_node_submission_runtime_477.v0.1"` ✓

`node_submission_runtime.py` was NOT modified in this window.

Test: `test_cdl_052_node_submission_runtime_version_unchanged` ✓
Test: `test_both_runtimes_importable_without_collision` ✓

### Evidence 10 — Historical hardening

| Test file | Tests | Result |
|-----------|-------|--------|
| `test_phase_858_hb_001_genesis_assertion_schema.py` | 35 | PASS ✓ |
| `test_phase_859_hb_003_layer_0_bundle_schema_section.py` | 16 | PASS ✓ |
| `test_cdl_034_ratification_349.py` | (included) | PASS ✓ |
| `test_node_schema_core_runtime_360.py` | (included) | PASS ✓ |
| `test_cdl_022_ratification_320.py` | (included) | PASS ✓ |
| `test_genesis_state_bundle_runtime_312.py` | (included) | PASS ✓ |
| `test_phase_838c_epoch_endorsement_runtime.py` | 75 | PASS ✓ |

Total: 162 historical tests, 162 passed. No regression. ✓

CDL-074 window total: 229 tests, 229 passed. ✓

---

## 5. Ratification Record

| Field | Value |
|-------|-------|
| decision_id | `CDL-074` |
| status | `ratified` |
| ratified_phase | `870` |
| ratified_date | `2026-04-27` |
| evidence_document | `docs/specs/ilc_cdl_074_truth_primitive_runtime_ratification_evidence_870_v0.1.md` |
| selected_option | `runtime contract only — six-primitive submission validator and graph-output contract` |
| dependency_token | `cdl_074_truth_primitive_runtime_ratified.v0.1` |

---

## 6. Mutation Protocol Confirmation

- Only `CDL-074` ratification fields mutated in constitutional decision log.
- No other `CDL-*` rows mutated.
- Runtime file changed: `ilc_core/epistemic/truth_primitive_submission_runtime.py` (new).
- `ilc_core/epistemic/node_submission_runtime.py` (CDL-052) — unchanged.
- No Rust files changed.
- No graph persistence, CID generation, or network delivery implemented.

---

## 7. Non-Goals Confirmed

This ratification does NOT:
- Implement graph persistence, CIDv1 generation, or LMDB storage for truth
  primitive nodes and edges.
- Implement network-layer delivery of truth primitive bundles.
- Deploy `commit.epoch` agent submission under any path.
- Extend `ALLOWED_PRIMITIVE_TYPES` (CDL-034 set unchanged).
- Modify `node_submission_runtime.py` (CDL-052 intact).
- Advance HB-002 or CDL-070.
- Change the live M-009 network in any way.
