# ILC CDL-030 ECU Price Clamp Ratification Evidence 277 v0.1

Status: Phase-277 ratification evidence artifact
Date: 2026-02-23
Owner lane: G8 Constitution Cluster A
Target decision: `CDL-030`

## 1. Purpose and scope

This artifact records ratification evidence for `CDL-030` only.
It locks ECU price clamp bounds (`P_min`, `P_max`) using the deterministic Phase-277-pre1 candidate lock under already-ratified issuance anchors.

This artifact does not ratify `CDL-031`.

## 2. Evidence chain summary

Minimum chain used in this ratification lane:
- Phase-233 governance plan: `docs/specs/ilc_issuance_governance_plan_233_v0.1.md`
- Phase-247 activation survey: `docs/specs/ilc_issuance_governance_activation_survey_247_v0.1.md`
- Phase-256 issuance analysis: `docs/specs/ilc_issuance_parameter_analysis_256_v0.1.md`
- Phase-271 closure-B: `docs/specs/ilc_issuance_evidence_closure_b_271_v0.1.md`
- Phase-273 `C_max` continuity: `docs/specs/ilc_cdl_026_cmax_lock_ratification_evidence_273_v0.1.md`
- Phase-274 `CDL-028` continuity: `docs/specs/ilc_cdl_028_fee_burn_split_ratification_evidence_274_v0.1.md`
- Phase-275 CDL-030 methodology: `docs/specs/ilc_issuance_evidence_closure_c_275_v0.1.md`
- Phase-276 ratified schedule constants: `docs/specs/ilc_cdl_027_decay_formulation_ratification_evidence_276_v0.1.md`
- Phase-277-pre1 simulation lock: `docs/specs/ilc_cdl_030_ecu_price_clamp_candidate_lock_277_pre1_v0.1.md`

## 3. CDL-030 bound selection statement

`CDL-030` selected bounds for ratification in Phase 277:
- selected `P_min = 0.75`
- selected `P_max = 1.30`

Derivation dependency statement:
- selected clamp bounds are copied unchanged from the deterministic Phase-277-pre1 candidate lock,
- Phase-277-pre1 is anchored to ratified Phase-276 schedule constants (`halving`, `H=48`, `1 month`).

Continuity statement:
- this lock remains aligned with ratified `CDL-026` finite `C_max` and ratified `CDL-028` fee-burn split continuity.

Formal declaration:
- `CDL-030` is ratified in Phase 277 with explicit bounds `P_min = 0.75` and `P_max = 1.30`.

## 4. Ratified bound table and derivation trace

| Parameter | Ratified value | Source |
| --- | --- | --- |
| `P_min` | `0.75` | `docs/specs/ilc_cdl_030_ecu_price_clamp_candidate_lock_277_pre1_v0.1.md` |
| `P_max` | `1.30` | `docs/specs/ilc_cdl_030_ecu_price_clamp_candidate_lock_277_pre1_v0.1.md` |
| schedule dependency | `halving`, `H=48`, `1 month` | `docs/specs/ilc_cdl_027_decay_formulation_ratification_evidence_276_v0.1.md` |

Trace summary:
1. Phase 275 defines CDL-030 derivation methodology and volatility/stability criteria.
2. Phase 276 ratifies schedule constants used by downstream clamp derivation.
3. Phase 277-pre1 runs deterministic 2D clamp sweep and candidate lock.
4. Phase 277 ratifies only the prelocked candidate values.

## 5. Mutation protocol confirmation

This ratification lane mutates only `CDL-030` and only the allowed ceremony fields:
- `status: open -> ratified`
- `ratified_phase: 277`
- `ratified_date: 2026-02-23`
- `evidence_document: docs/specs/ilc_cdl_030_ecu_price_clamp_ratification_evidence_277_v0.1.md`

No other `CDL-030` fields are changed.
No other decision-log rows are changed in this lane.

## 6. Non-goals

This phase does not:
- ratify `CDL-031`,
- mutate `options`, `current_candidate`, or `required_artifacts` fields for any row,
- alter runtime behavior in `ilc_core/`,
- alter D2e command-surface contracts.

## 7. Canonical anchors

- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_issuance_governance_plan_233_v0.1.md`
- `docs/specs/ilc_issuance_governance_activation_survey_247_v0.1.md`
- `docs/specs/ilc_issuance_parameter_analysis_256_v0.1.md`
- `docs/specs/ilc_issuance_evidence_closure_b_271_v0.1.md`
- `docs/specs/ilc_issuance_evidence_closure_c_275_v0.1.md`
- `docs/specs/ilc_cdl_026_cmax_lock_ratification_evidence_273_v0.1.md`
- `docs/specs/ilc_cdl_028_fee_burn_split_ratification_evidence_274_v0.1.md`
- `docs/specs/ilc_cdl_027_decay_formulation_ratification_evidence_276_v0.1.md`
- `docs/specs/ilc_cdl_030_ecu_price_clamp_candidate_lock_277_pre1_v0.1.md`
