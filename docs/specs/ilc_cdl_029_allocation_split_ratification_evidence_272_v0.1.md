# ILC CDL-029 Allocation Split Ratification Evidence 272 v0.1

Status: Phase-272 ratification evidence artifact
Date: 2026-02-23
Owner lane: G8 Constitution Cluster A
Target decision: `CDL-029`

## 1. Purpose and scope

This artifact records the ratification evidence for `CDL-029` only.
It formalizes selection of the allocation split and confirms dependency continuity with prior issuance-governance artifacts.

This artifact does not ratify `CDL-026`, `CDL-027`, `CDL-028`, `CDL-030`, or `CDL-031`.

## 2. Evidence chain summary

Minimum chain used in this ratification lane:
- Phase-233 governance plan: `docs/specs/ilc_issuance_governance_plan_233_v0.1.md`
- Phase-247 activation survey: `docs/specs/ilc_issuance_governance_activation_survey_247_v0.1.md`
- Phase-256 issuance analysis: `docs/specs/ilc_issuance_parameter_analysis_256_v0.1.md`
- Phase-266 closure/reconciliation: `docs/specs/ilc_issuance_evidence_closure_a_266_v0.1.md`, `docs/specs/ilc_genesis_accrual_reconciliation_8pct_vs_theta_hard_266_v0.1.md`
- Phase-271 closure-B: `docs/specs/ilc_issuance_evidence_closure_b_271_v0.1.md`
- Phase-267 terminal model ratification continuity: `docs/specs/ilc_cdl_025_terminal_issuance_model_ratification_evidence_267_v0.1.md`

This chain preserves allocation-surface continuity from planning through closure artifacts and into ratification.

## 3. CDL-029 option selection statement

`CDL-029` selected option for ratification in Phase 272:
- performer / auditor / genesis split = `80 / 15 / 5`

Validation continuity statement:
- this ratification preserves `theta_hard = 1/20` continuity from prior closure artifacts and does not alter previously ratified terminal issuance model constraints.

Formal declaration:
- `CDL-029` is ratified in Phase 272 with the `80/15/5` split and associated `theta_hard = 1/20` continuity assumptions as documented in the evidence chain.

## 4. Mutation protocol confirmation

This ratification lane mutates only `CDL-029` and only the allowed ceremony fields:
- `status: open -> ratified`
- `ratified_phase: 272`
- `ratified_date: 2026-02-23`
- `evidence_document: docs/specs/ilc_cdl_029_allocation_split_ratification_evidence_272_v0.1.md`

No other `CDL-029` fields are changed.
No other decision-log rows are changed in this lane.

## 5. Non-goals

This phase does not:
- ratify `CDL-026`, `CDL-027`, `CDL-028`, `CDL-030`, or `CDL-031`,
- mutate `options`, `current_candidate`, or `required_artifacts` fields,
- change runtime behavior in `ilc_core/`,
- alter D2e command-surface contracts.

## 6. Canonical anchors

- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_issuance_governance_plan_233_v0.1.md`
- `docs/specs/ilc_issuance_governance_activation_survey_247_v0.1.md`
- `docs/specs/ilc_issuance_parameter_analysis_256_v0.1.md`
- `docs/specs/ilc_issuance_evidence_closure_a_266_v0.1.md`
- `docs/specs/ilc_genesis_accrual_reconciliation_8pct_vs_theta_hard_266_v0.1.md`
- `docs/specs/ilc_issuance_evidence_closure_b_271_v0.1.md`
- `docs/specs/ilc_cdl_025_terminal_issuance_model_ratification_evidence_267_v0.1.md`
