# ILC CDL-027 Decay Formulation Ratification Evidence 276 v0.1

Status: Phase-276 ratification evidence artifact
Date: 2026-02-23
Owner lane: G8 Constitution Cluster A
Target decision: `CDL-027`

## 1. Purpose and scope

This artifact records ratification evidence for `CDL-027` only.
It locks the decay formulation and schedule constants using the Phase-275 carry-forward recommendation.

This artifact does not ratify `CDL-030` or `CDL-031`.

## 2. Evidence chain summary

Minimum chain used in this ratification lane:
- Phase-233 governance plan: `docs/specs/ilc_issuance_governance_plan_233_v0.1.md`
- Phase-247 activation survey: `docs/specs/ilc_issuance_governance_activation_survey_247_v0.1.md`
- Phase-256 issuance analysis: `docs/specs/ilc_issuance_parameter_analysis_256_v0.1.md`
- Phase-271 closure-B: `docs/specs/ilc_issuance_evidence_closure_b_271_v0.1.md`
- Phase-273 `C_max` continuity: `docs/specs/ilc_cdl_026_cmax_lock_ratification_evidence_273_v0.1.md`
- Phase-274 `CDL-028` continuity: `docs/specs/ilc_cdl_028_fee_burn_split_ratification_evidence_274_v0.1.md`
- Phase-275 closure-C carry-forward lock: `docs/specs/ilc_issuance_evidence_closure_c_275_v0.1.md`

## 3. CDL-027 formulation selection statement

`CDL-027` selected formulation for ratification in Phase 276:
- selected formulation: `halving`
- selected schedule constant: `H = 48`
- selected epoch duration: `1 month`

Carry-forward continuity statement:
- selected values are copied unchanged from the Phase-275 carry-forward candidate in `docs/specs/ilc_issuance_evidence_closure_c_275_v0.1.md`.

Dependency continuity statement:
- this lock remains aligned to ratified `CDL-026` finite `C_max` continuity and ratified `CDL-028` fee-burn split continuity.

Formal declaration:
- `CDL-027` is ratified in Phase 276 as `halving` with schedule constant `H = 48` under monthly epochs.

## 4. Ratified constants and schedule table

| Parameter | Ratified value | Source |
| --- | --- | --- |
| Formulation family | `halving` | Phase-275 carry-forward |
| Schedule constant | `H = 48` | Phase-275 carry-forward |
| Epoch duration candidate | `1 month` | Phase-275 carry-forward |

Derived interpretation for downstream lanes:
- clamp derivation in `CDL-030` uses this ratified schedule set as fixed input.

## 5. Mutation protocol confirmation

This ratification lane mutates only `CDL-027` and only the allowed ceremony fields:
- `status: open -> ratified`
- `ratified_phase: 276`
- `ratified_date: 2026-02-23`
- `evidence_document: docs/specs/ilc_cdl_027_decay_formulation_ratification_evidence_276_v0.1.md`

No other `CDL-027` fields are changed.
No other decision-log rows are changed in this lane.

## 6. Non-goals

This phase does not:
- ratify `CDL-030` or `CDL-031`,
- mutate `options`, `current_candidate`, or `required_artifacts` fields for any row,
- alter runtime behavior in `ilc_core/`,
- alter D2e command-surface contracts.

## 7. Canonical anchors

- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_issuance_governance_plan_233_v0.1.md`
- `docs/specs/ilc_issuance_governance_activation_survey_247_v0.1.md`
- `docs/specs/ilc_issuance_parameter_analysis_256_v0.1.md`
- `docs/specs/ilc_issuance_evidence_closure_b_271_v0.1.md`
- `docs/specs/ilc_cdl_026_cmax_lock_ratification_evidence_273_v0.1.md`
- `docs/specs/ilc_cdl_028_fee_burn_split_ratification_evidence_274_v0.1.md`
- `docs/specs/ilc_issuance_evidence_closure_c_275_v0.1.md`
