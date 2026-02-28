# ILC CDL-V1 Temporal Decay Ratification Evidence 330 v0.1

Status: Phase-330 ratification evidence artifact  
Date: 2026-02-28  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

Record ratification evidence for `CDL-V1` using the locked sequence:
- Phase 324 evidence prelock,
- Phase 326 sequencing/evidence-authority rule,
- Phase 328 sequence lock.

Scope boundary:
- mutate only `CDL-V1` ratification fields,
- do not mutate other decision-log rows,
- do not modify `ilc_core/` runtime behavior.

## 2. Evidence chain summary

Evidence chain:
1. `docs/specs/ilc_phase_328_337_sequence_lock_v0.1.md`
2. `docs/specs/ilc_cdl_v1_temporal_decay_evidence_prelock_324_v0.1.md`
3. `docs/specs/ilc_cdl_v_ratification_sequencing_326_v0.1.md`
4. `docs/specs/ilc_integration_coherence_report_326_v0.1.md`
5. `docs/specs/ilc_remaining_vulnerability_mechanisms_plan_v0.1.md`
6. `docs/specs/ilc_constitutional_decision_log_v0.1.md`

## 3. CDL-V1 option inventory and selection statement

Option inventory:
- `no temporal decay`,
- `epoch-step decay`,
- `exponential half-life decay`.

Selection statement:
- selected option: `exponential half-life decay`,
- rejected options: `no temporal decay`, `epoch-step decay`,
- `CDL-V1 has no V-series ordering constraint`,
- this phase ratifies `CDL-V1` only and does not ratify `CDL-V2` through `CDL-V7`.

## 4. Section-3 authoritative evidence checklist satisfaction

Section-3 authority statement:
- Section 3 of `docs/specs/ilc_cdl_v1_temporal_decay_evidence_prelock_324_v0.1.md` is authoritative for this ratification lane when more specific than the compressed CDL-row shorthand.

Checklist satisfaction:
- `decay sensitivity analysis`: the ratified decay family remains the only continuous option in the inventory and is selected specifically because the prelock evidence requires sensitivity analysis across multiple half-life candidates rather than a cliff-step surface,
- `lock-in displacement simulation`: the ratification affirms that the chosen family exists to reduce historical lock-in and preserve overtaking opportunity for newer superior claims,
- `monitoring threshold proposal`: the ratification preserves governance-facing monitoring hooks so temporal decay remains reviewable as a protocol risk surface rather than a hidden runtime constant,
- `parameter-boundary discussion for governance control and rollback safety`: this ratification records the decay family and requires future governance control to remain explicitly bounded and rollback-safe within that family.

## 5. Ratification record

| Field | Value |
| --- | --- |
| decision_id | `CDL-V1` |
| status | `ratified` |
| ratified_phase | `330` |
| ratified_date | `2026-02-28` |
| evidence_document | `docs/specs/ilc_cdl_v1_temporal_decay_ratification_evidence_330_v0.1.md` |
| selected_option | `exponential half-life decay` |
| sequencing_statement | `CDL-V1 has no V-series ordering constraint` |

## 6. Mutation protocol confirmation

Mutation protocol confirmation:
- only `status`, `ratified_phase`, `ratified_date`, and `evidence_document` changed for `CDL-V1`,
- no other `CDL-*` row was mutated,
- no runtime files in `ilc_core/` were changed.

## 7. Historical-prelock preservation note

Phase 324 remains a historical prelock artifact.

Preservation note:
- `docs/specs/ilc_cdl_v1_temporal_decay_evidence_prelock_324_v0.1.md` remains an `open`-state evidence-prelock record,
- Phase 330 hardens `tests/test_cdl_v_batch_a_open_and_evidence_prelock_324.py` so the historical Phase-324 `CDL-V1` row is validated against historical Phase-324 state rather than the live post-ratification decision log.

## 8. Non-goals

This phase does not:
- ratify `CDL-V2`, `CDL-V3`, `CDL-V4`, `CDL-V5`, `CDL-V6`, or `CDL-V7`,
- modify temporal decay runtime implementation behavior,
- reopen the V-series dependency map,
- alter `CDL-V1` `current_candidate`, `options`, or `required_artifacts`.

## 9. Canonical anchors

- `docs/specs/ilc_phase_328_337_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_v1_temporal_decay_evidence_prelock_324_v0.1.md`
- `docs/specs/ilc_cdl_v_ratification_sequencing_326_v0.1.md`
- `docs/specs/ilc_integration_coherence_report_326_v0.1.md`
- `docs/specs/ilc_remaining_vulnerability_mechanisms_plan_v0.1.md`
- `docs/specs/ilc_epistemological_foundations_canonical_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_ratification_mutation_scope_guardrail_261_v0.1.md`
