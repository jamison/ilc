# ILC CDL-026 Cmax Lock Ratification Evidence 273 v0.1

Status: Phase-273 ratification evidence artifact
Date: 2026-02-23
Owner lane: G8 Constitution Cluster A
Target decision: `CDL-026`

## 1. Purpose and scope

This artifact records ratification evidence for `CDL-026` only.
It locks the `C_max` policy surface after `CDL-025` and `CDL-029` ratification continuity checks.

This artifact does not ratify `CDL-027`, `CDL-028`, `CDL-030`, or `CDL-031`.

## 2. Evidence chain summary

Minimum chain used in this ratification lane:
- Phase-233 governance plan: `docs/specs/ilc_issuance_governance_plan_233_v0.1.md`
- Phase-247 activation survey: `docs/specs/ilc_issuance_governance_activation_survey_247_v0.1.md`
- Phase-256 issuance analysis: `docs/specs/ilc_issuance_parameter_analysis_256_v0.1.md`
- Phase-266 closure/reconciliation: `docs/specs/ilc_issuance_evidence_closure_a_266_v0.1.md`, `docs/specs/ilc_genesis_accrual_reconciliation_8pct_vs_theta_hard_266_v0.1.md`
- Phase-271 closure-B: `docs/specs/ilc_issuance_evidence_closure_b_271_v0.1.md`
- Phase-267 terminal model ratification continuity: `docs/specs/ilc_cdl_025_terminal_issuance_model_ratification_evidence_267_v0.1.md`
- Phase-272 allocation ratification continuity: `docs/specs/ilc_cdl_029_allocation_split_ratification_evidence_272_v0.1.md`

## 3. CDL-026 option selection statement

`CDL-026` selected option for ratification in Phase 273:
- `explicit finite cap` (not `cap-with-tolerance`).

Selected `C_max` lock candidate:
- governance-fixed finite `C_max` constant under Model B terminal issuance assumptions (no tolerance band admitted in this ratification lane).

Continuity statement:
- this lock remains aligned to ratified `CDL-025` Model B framing and ratified `CDL-029` allocation continuity.

Formal declaration:
- `CDL-026` is ratified in Phase 273 as `explicit finite cap` with the selected finite `C_max` lock candidate for downstream issuance schedule derivation lanes.

## 4. Mutation protocol confirmation

This ratification lane mutates only `CDL-026` and only the allowed ceremony fields:
- `status: open -> ratified`
- `ratified_phase: 273`
- `ratified_date: 2026-02-23`
- `evidence_document: docs/specs/ilc_cdl_026_cmax_lock_ratification_evidence_273_v0.1.md`

No other `CDL-026` fields are changed.
No other decision-log rows are changed in this lane.

## 5. Non-goals

This phase does not:
- ratify `CDL-027`, `CDL-028`, `CDL-030`, or `CDL-031`,
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
- `docs/specs/ilc_cdl_029_allocation_split_ratification_evidence_272_v0.1.md`
