# ILC CDL-025 Terminal Issuance Model Ratification Evidence 267 v0.1

Status: Phase-267 ratification artifact
Date: 2026-02-22
Lane: Constitution Cluster A

## 1. Purpose and scope

This artifact provides the evidence chain and formal ratification statement for `CDL-025`.

Scope is limited to terminal issuance model ratification for `CDL-025`.

## 2. Evidence chain summary

Minimum evidence chain used for this ratification:
- Phase-233 issuance planning: `docs/specs/ilc_issuance_governance_plan_233_v0.1.md`
- Phase-247 issuance activation survey: `docs/specs/ilc_issuance_governance_activation_survey_247_v0.1.md`
- Phase-256 issuance readiness analysis: `docs/specs/ilc_issuance_parameter_analysis_256_v0.1.md`
- Phase-266 issuance evidence closure package: `docs/specs/ilc_issuance_evidence_closure_a_266_v0.1.md`
- Phase-266 reconciliation note: `docs/specs/ilc_genesis_accrual_reconciliation_8pct_vs_theta_hard_266_v0.1.md`
- Ceremony mutation guardrail: `docs/specs/ilc_ratification_mutation_scope_guardrail_261_v0.1.md`

## 3. CDL-025 option selection statement

`CDL-025` options recorded in the decision log:
- asymptotic cap (Model A),
- fee-funded tail (Model B),
- burn-offset tail (Model C).

Selected option for ratification in Phase 267:
- **fee-funded tail (Model B)**.

Formal declaration:
- `CDL-025` is ratified in Phase 267 with the selected terminal issuance model option above, with decision-log mutation bounded to ceremony-allowed fields only.

## 4. Mutation protocol confirmation

Decision-log row mutation constraints enforced:
- allowed fields only: `status`, `ratified_phase`, `ratified_date`, `evidence_document`,
- no change to non-target CDL rows,
- no runtime code changes in this ratification lane.

## 5. Non-goals

This phase does not:
- ratify `CDL-019`,
- ratify `CDL-026` through `CDL-031`,
- implement runtime issuance mechanics,
- alter D2e command surface behavior.

## 6. Canonical anchors

- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_cdl_ratification_and_d2e_activation_sequence_250_259_v0.1.md`
- `docs/specs/ilc_phase_260_269_sequence_lock_v0.1.md`
- `docs/specs/ilc_issuance_governance_plan_233_v0.1.md`
- `docs/specs/ilc_issuance_governance_activation_survey_247_v0.1.md`
- `docs/specs/ilc_issuance_parameter_analysis_256_v0.1.md`
- `docs/specs/ilc_issuance_evidence_closure_a_266_v0.1.md`
- `docs/specs/ilc_genesis_accrual_reconciliation_8pct_vs_theta_hard_266_v0.1.md`
- `docs/specs/ilc_ratification_mutation_scope_guardrail_261_v0.1.md`
