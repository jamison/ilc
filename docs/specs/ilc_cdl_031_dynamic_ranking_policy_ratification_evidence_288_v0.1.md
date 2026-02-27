# ILC CDL-031 Dynamic Ranking Policy Ratification Evidence 288 v0.1

Status: Phase-288 ratification evidence artifact  
Date: 2026-02-24  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

Record ratification evidence for `CDL-031` using the Phase-287 closure package.

Scope boundary:
- mutate only `CDL-031` ratification fields,
- do not mutate other decision-log rows,
- do not modify `ilc_core/` runtime behavior.

## 2. Evidence chain summary

Evidence chain:
1. `docs/specs/ilc_cdl_031_ranking_policy_evidence_closure_287_v0.1.md`
2. `docs/specs/ilc_epistemic_type_and_subjective_objective_payout_boundary_prelock_280_pre1_v0.1.md`
3. `docs/specs/ilc_reuse_diversity_anti_sybil_contract_v0.1.md`
4. `docs/specs/ilc_phase_286_295_sequence_lock_v0.1.md`

## 3. CDL-031 policy selection statement

Selected policy:
- admit dynamic ranking multiplier policy with explicit guardrails,
- keep bounded multiplier envelopes per epistemic lane,
- keep governance override pathway for emergency containment.

## 4. Ratified policy table and guardrail trace

| Field | Value |
| --- | --- |
| decision_id | `CDL-031` |
| status | `ratified` |
| ratified_phase | `288` |
| ratified_date | `2026-02-24` |
| evidence_document | `docs/specs/ilc_cdl_031_dynamic_ranking_policy_ratification_evidence_288_v0.1.md` |

Guardrail trace:
- anti-Sybil anchors inherited from reuse-diversity contract,
- lane-specific boundaries inherited from 280-pre1 artifact,
- non-target row protections enforced by mutation-scope tests.

## 5. Mutation protocol confirmation

Mutation protocol confirmation:
- only `status`, `ratified_phase`, `ratified_date`, and `evidence_document` were changed for `CDL-031`,
- no other `CDL-*` row was mutated,
- no runtime files in `ilc_core/` were changed.

## 6. Non-goals

This phase does not:
- ratify any CDL other than `CDL-031`,
- alter issuance constants,
- implement ranking runtime logic.

## 7. Canonical anchors

- `docs/specs/ilc_cdl_031_ranking_policy_evidence_closure_287_v0.1.md`
- `docs/specs/ilc_phase_286_295_sequence_lock_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_ratification_mutation_scope_guardrail_261_v0.1.md`
