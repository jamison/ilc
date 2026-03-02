# ILC CDL-V7 Agent Decomposition Criteria Ratification Evidence 335 v0.1

Status: Phase-335 ratification evidence artifact  
Date: 2026-03-02  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

Record ratification evidence for `CDL-V7` using the locked evidence-prelock boundary from Phase 325, the sequencing and evidence-authority rules from Phase 326, the sequence lock from Phase 328, and the completed `CDL-V5 -> CDL-V7` prerequisite from Phase 333.

Scope boundary:
- mutate only `CDL-V7` ratification fields,
- do not mutate any non-target decision-log row,
- do not modify runtime behavior in `ilc_core/`.

## 2. Evidence chain summary

Evidence chain:
1. `docs/specs/ilc_phase_328_337_sequence_lock_v0.1.md`
2. `docs/specs/ilc_cdl_v7_agent_decomposition_criteria_evidence_prelock_325_v0.1.md`
3. `docs/specs/ilc_cdl_v5_schema_epoch_translation_ratification_evidence_333_v0.1.md`
4. `docs/specs/ilc_cdl_v_ratification_sequencing_326_v0.1.md`
5. `docs/specs/ilc_integration_coherence_report_326_v0.1.md`
6. `docs/specs/ilc_antigravity_context_capsule_v0.7.md`
7. `docs/specs/ilc_remaining_vulnerability_mechanisms_plan_v0.1.md`
8. `docs/specs/ilc_popper_ilc_analysis_v0.1.md`
9. `docs/specs/ilc_epistemological_foundations_canonical_v0.1.md`
10. `docs/specs/ilc_constitutional_decision_log_v0.1.md`

## 3. CDL-V7 option inventory and selection statement

Option inventory:
- `utility-only acceptance`,
- `operator discretionary decomposition`,
- `Popperian basic-statement gate for agent decomposition`.

Selection statement:
- selected option: `Popperian basic-statement gate for agent decomposition`,
- rejected options: `utility-only acceptance`, `operator discretionary decomposition`,
- this phase is the downstream step in the `CDL-V5 -> CDL-V7` sequence,
- this phase ratifies `CDL-V7` only.

## 4. Section-3 authoritative evidence checklist satisfaction

Section-3 authority statement:
- Section 3 of the Phase-325 `CDL-V7` prelock artifact is authoritative for this ratification lane.

Checklist satisfaction:
- `decomposition test corpus covering singular, existential, and falsifiable claim forms`
- `admissibility counterexamples demonstrating what must be rejected and why`
- `cross-agent reproducibility rubric showing that decomposition outcomes are intersubjectively stable`
- `explicit tie-back to graph-entry rules and reuse-value admissibility`

Prerequisite statement:
- Phase-333 `CDL-V5` ratification supplies the schema-epoch comparability prerequisite consumed by the cross-agent reproducibility rubric.

## 5. Cross-agent reproducibility protocol

This evidence artifact treats the reproducibility rubric as a concrete tolerance-bound evaluation protocol rather than abstract agreement language.

Protocol tokens:
- `minimum of three independent agent decomposition runs`
- `benchmark corpus partitions: singular, existential, falsifiable-positive, inadmissible-counterexample`
- `admissibility-decision agreement threshold: >= 0.85 across the full corpus`
- `counterexample rejection threshold: 1.00 on the inadmissible-counterexample set`
- `any candidate failing these thresholds is non-ratifiable`

Operational interpretation:
- the benchmark corpus must include representative singular, existential, falsifiable-positive, and inadmissible-counterexample cases,
- agreement must be measured on admissibility decisions across all three or more independent runs,
- failure on the inadmissible-counterexample set is disqualifying even when broader utility appears favorable.

## 6. Graph-entry and reuse-value admissibility tie-back

Tie-back statements:
- `graph-entry eligibility is limited to knowledge units that satisfy the ratified Popperian basic-statement gate`
- `reuse-value admissibility is denied to decomposition outputs that fail the gate even if utility appears high`

Boundary note:
- the Popperian admissibility gate governs both entry into the knowledge graph and downstream reuse-value eligibility,
- apparent usefulness cannot override inadmissibility.

## 7. Ratification record

| Field | Value |
| --- | --- |
| decision_id | `CDL-V7` |
| status | `ratified` |
| ratified_phase | `335` |
| ratified_date | `2026-03-02` |
| evidence_document | `docs/specs/ilc_cdl_v7_agent_decomposition_criteria_ratification_evidence_335_v0.1.md` |
| selected_option | `Popperian basic-statement gate for agent decomposition` |
| sequence_position | downstream step in the `CDL-V5 -> CDL-V7` sequence |

## 8. Mutation protocol confirmation

Mutation protocol confirmation:
- only `status`, `ratified_phase`, `ratified_date`, and `evidence_document` changed for `CDL-V7`,
- no other `CDL-*` row was mutated,
- this phase preserves runtime boundaries and does not modify `ilc_core/`.

## 9. Historical-prelock preservation note

Phase 325 remains a historical prelock artifact.

Preservation note:
- `docs/specs/ilc_cdl_v7_agent_decomposition_criteria_evidence_prelock_325_v0.1.md` remains an `open`-state evidence-prelock record,
- Phase 335 hardens `tests/test_cdl_v_batch_b_open_and_evidence_prelock_325.py`, `tests/test_cdl_v5_ratification_333.py`, and `tests/test_cdl_v4_v6_dual_ratification_334.py` so the historical Phase-325 `CDL-V7` row is validated against historical Phase-325 state rather than the live post-ratification decision log.

## 10. Non-goals

This phase does not:
- reopen the already-ratified `CDL-V4` / `CDL-V6` coupled boundary,
- revise the completed `CDL-V5 -> CDL-V7` ordering rule,
- claim runtime enforcement in `ilc_core/`,
- alter `CDL-V7` `current_candidate`, `options`, or `required_artifacts`.

## 11. Canonical anchors

- `docs/specs/ilc_phase_328_337_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_v7_agent_decomposition_criteria_evidence_prelock_325_v0.1.md`
- `docs/specs/ilc_cdl_v5_schema_epoch_translation_ratification_evidence_333_v0.1.md`
- `docs/specs/ilc_cdl_v_ratification_sequencing_326_v0.1.md`
- `docs/specs/ilc_integration_coherence_report_326_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v0.7.md`
- `docs/specs/ilc_remaining_vulnerability_mechanisms_plan_v0.1.md`
- `docs/specs/ilc_popper_ilc_analysis_v0.1.md`
- `docs/specs/ilc_epistemological_foundations_canonical_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_ratification_mutation_scope_guardrail_261_v0.1.md`
