# ILC CDL-028 Fee-Burn Split Ratification Evidence 274 v0.1

Status: Phase-274 ratification evidence artifact
Date: 2026-02-23
Owner lane: G8 Constitution Cluster A
Target decision: `CDL-028`

## 1. Purpose and scope

This artifact records ratification evidence for `CDL-028` only.
It locks the fee-burn split ratio after continuity checks with ratified `CDL-025`, `CDL-029`, and `CDL-026`.

This artifact does not ratify `CDL-027`, `CDL-030`, or `CDL-031`.

## 2. Evidence chain summary

Minimum chain used in this ratification lane:
- Phase-233 governance plan: `docs/specs/ilc_issuance_governance_plan_233_v0.1.md`
- Phase-247 activation survey: `docs/specs/ilc_issuance_governance_activation_survey_247_v0.1.md`
- Phase-256 issuance analysis: `docs/specs/ilc_issuance_parameter_analysis_256_v0.1.md`
- Phase-266 closure/reconciliation: `docs/specs/ilc_issuance_evidence_closure_a_266_v0.1.md`, `docs/specs/ilc_genesis_accrual_reconciliation_8pct_vs_theta_hard_266_v0.1.md`
- Phase-271 closure-B: `docs/specs/ilc_issuance_evidence_closure_b_271_v0.1.md`
- Phase-267 terminal model ratification continuity: `docs/specs/ilc_cdl_025_terminal_issuance_model_ratification_evidence_267_v0.1.md`
- Phase-272 allocation ratification continuity: `docs/specs/ilc_cdl_029_allocation_split_ratification_evidence_272_v0.1.md`
- Phase-273 `C_max` continuity: `docs/specs/ilc_cdl_026_cmax_lock_ratification_evidence_273_v0.1.md`
- Epoch-duration policy matrix (context only): `docs/specs/ilc_epoch_duration_candidate_matrix_and_policy_options_274_fix2_v0.1.md`
- Phase-274-fix1 deterministic candidate lock: `docs/specs/ilc_cdl_028_fee_burn_split_candidate_lock_274_fix1_v0.1.md`

## 3. CDL-028 option selection statement

`CDL-028` selected option for ratification in Phase 274:
- `other percentages`.

Selected split value:
- fee-burn ratio = `10%`.

Carry-forward rule confirmation:
- selected value is copied unchanged from:
  - `docs/specs/ilc_cdl_028_fee_burn_split_candidate_lock_274_fix1_v0.1.md`.

Continuity statement:
- this lock remains aligned to ratified `CDL-025` Model B terminal issuance framing and ratified `CDL-029`/`CDL-026` continuity.

Deferred-schedule statement:
- decay schedule and epoch-duration selection are explicitly deferred to Phase 275/276 (`CDL-027` lane).

Formal declaration:
- `CDL-028` is ratified in Phase 274 as `other percentages` with explicit `10%` fee-burn split.

## 4. Mutation protocol confirmation

This ratification lane mutates only `CDL-028` and only the allowed ceremony fields:
- `status: open -> ratified`
- `ratified_phase: 274`
- `ratified_date: 2026-02-23`
- `evidence_document: docs/specs/ilc_cdl_028_fee_burn_split_ratification_evidence_274_v0.1.md`

No other `CDL-028` fields are changed.
No other decision-log rows are changed in this lane.

## 5. Non-goals

This phase does not:
- ratify `CDL-027`, `CDL-030`, or `CDL-031`,
- mutate `options`, `current_candidate`, or `required_artifacts` fields for any row,
- ratify epoch-duration or decay constants,
- change runtime behavior in `ilc_core/`.

## 6. Canonical anchors

- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_issuance_governance_plan_233_v0.1.md`
- `docs/specs/ilc_issuance_governance_activation_survey_247_v0.1.md`
- `docs/specs/ilc_issuance_parameter_analysis_256_v0.1.md`
- `docs/specs/ilc_epoch_duration_candidate_matrix_and_policy_options_274_fix2_v0.1.md`
- `docs/specs/ilc_issuance_evidence_closure_a_266_v0.1.md`
- `docs/specs/ilc_genesis_accrual_reconciliation_8pct_vs_theta_hard_266_v0.1.md`
- `docs/specs/ilc_issuance_evidence_closure_b_271_v0.1.md`
- `docs/specs/ilc_cdl_025_terminal_issuance_model_ratification_evidence_267_v0.1.md`
- `docs/specs/ilc_cdl_029_allocation_split_ratification_evidence_272_v0.1.md`
- `docs/specs/ilc_cdl_026_cmax_lock_ratification_evidence_273_v0.1.md`
- `docs/specs/ilc_cdl_028_fee_burn_split_candidate_lock_274_fix1_v0.1.md`
