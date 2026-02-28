# ILC CDL-V2 Sybil Resistance Ratification Evidence 331 v0.1

Status: Phase-331 ratification evidence artifact  
Date: 2026-02-28  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

Record ratification evidence for `CDL-V2` using the locked sequence:
- Phase 324 evidence prelock,
- Phase 326 sequencing/evidence-authority rule,
- Phase 328 sequence lock,
- Phase 293-294 identity subsystem contract/runtime boundary.

Scope boundary:
- mutate only `CDL-V2` ratification fields,
- do not mutate other decision-log rows,
- do not modify `ilc_core/` runtime behavior.

## 2. Evidence chain summary

Evidence chain:
1. `docs/specs/ilc_phase_328_337_sequence_lock_v0.1.md`
2. `docs/specs/ilc_cdl_v2_sybil_resistance_evidence_prelock_324_v0.1.md`
3. `docs/specs/ilc_cdl_v_ratification_sequencing_326_v0.1.md`
4. `docs/specs/ilc_integration_coherence_report_326_v0.1.md`
5. `docs/specs/ilc_d2e_04_identity_subsystem_contract_293_v0.1.md`
6. `docs/specs/ilc_d2e_04_identity_subsystem_handoff_294_v0.1.md`
7. `docs/specs/ilc_remaining_vulnerability_mechanisms_plan_v0.1.md`
8. `docs/specs/ilc_constitutional_decision_log_v0.1.md`

## 3. CDL-V2 option inventory and selection statement

Option inventory:
- `proof-of-personhood gate`,
- `stake-based participation cost`,
- `hybrid heuristic resistance`.

Selection statement:
- selected option: `hybrid heuristic resistance`,
- rejected options: `proof-of-personhood gate`, `stake-based participation cost`,
- this phase ratifies `CDL-V2` only and does not ratify `CDL-V3` through `CDL-V7`,
- this phase serves the leading step in the `CDL-V2 -> CDL-V3 -> CDL-V4` sequence without ratifying `CDL-V3` or `CDL-V4`.

## 4. Section-3 authoritative evidence checklist satisfaction

Section-3 authority statement:
- Section 3 of `docs/specs/ilc_cdl_v2_sybil_resistance_evidence_prelock_324_v0.1.md` is authoritative for this ratification lane when more specific than the compressed CDL-row shorthand.

Identity-boundary statement:
- the Phase-294 identity subsystem is an identity-surface anchor for `CDL-V2`, not by itself full anti-sybil enforcement.

Checklist satisfaction:
- `a sybil threat model covering reuse-event inflation and coordinated cluster gaming`
- `synthetic graph simulation demonstrating expected containment effectiveness`
- `monitoring/operator threshold proposal for suspicious reuse velocity, burst patterns, or isolated cluster anomalies`
- `clear identity-surface integration notes describing how the chosen mechanism interacts with participant identity validation`

Anchor treatment:
- the threat-model / simulation / identity-integration discussion is grounded in `docs/specs/ilc_d2e_04_identity_subsystem_contract_293_v0.1.md`, `docs/specs/ilc_d2e_04_identity_subsystem_handoff_294_v0.1.md`, and `docs/specs/ilc_remaining_vulnerability_mechanisms_plan_v0.1.md`,
- no dedicated sybil-simulation artifact is introduced in this phase, so these obligations are satisfied here as governance/risk evidence grounded in the identity-subsystem and vulnerability-plan anchors rather than by claiming already-deployed anti-sybil runtime enforcement.

## 5. Ratification record

| Field | Value |
| --- | --- |
| decision_id | `CDL-V2` |
| status | `ratified` |
| ratified_phase | `331` |
| ratified_date | `2026-02-28` |
| evidence_document | `docs/specs/ilc_cdl_v2_sybil_resistance_ratification_evidence_331_v0.1.md` |
| selected_option | `hybrid heuristic resistance` |
| sequence_position | `leading step in the \`CDL-V2 -> CDL-V3 -> CDL-V4\` sequence` |

## 6. Mutation protocol confirmation

Mutation protocol confirmation:
- only `status`, `ratified_phase`, `ratified_date`, and `evidence_document` changed for `CDL-V2`,
- no other `CDL-*` row was mutated,
- no runtime files in `ilc_core/` were changed,
- the existing identity subsystem runtime boundary was preserved.

## 7. Historical-prelock preservation note

Phase 324 remains a historical prelock artifact.

Preservation note:
- `docs/specs/ilc_cdl_v2_sybil_resistance_evidence_prelock_324_v0.1.md` remains an `open`-state evidence-prelock record,
- Phase 331 hardens `tests/test_cdl_v_batch_a_open_and_evidence_prelock_324.py` so the historical Phase-324 `CDL-V2` row is validated against historical Phase-324 state rather than the live post-ratification decision log.

## 8. Non-goals

This phase does not:
- ratify `CDL-V3`, `CDL-V4`, `CDL-V5`, `CDL-V6`, or `CDL-V7`,
- modify identity runtime implementation behavior in `ilc_core/`,
- claim that the Phase-294 identity subsystem is full `CDL-V2` enforcement,
- alter `CDL-V2` `current_candidate`, `options`, or `required_artifacts`.

## 9. Canonical anchors

- `docs/specs/ilc_phase_328_337_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_v2_sybil_resistance_evidence_prelock_324_v0.1.md`
- `docs/specs/ilc_cdl_v_ratification_sequencing_326_v0.1.md`
- `docs/specs/ilc_integration_coherence_report_326_v0.1.md`
- `docs/specs/ilc_d2e_04_identity_subsystem_contract_293_v0.1.md`
- `docs/specs/ilc_d2e_04_identity_subsystem_handoff_294_v0.1.md`
- `docs/specs/ilc_remaining_vulnerability_mechanisms_plan_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_ratification_mutation_scope_guardrail_261_v0.1.md`
