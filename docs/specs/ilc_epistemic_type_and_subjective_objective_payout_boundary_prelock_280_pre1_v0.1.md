# ILC Epistemic Type and Subjective/Objective Payout Boundary Prelock 280-pre1 v0.1

Status: Phase-280-pre1 prelock artifact  
Date: 2026-02-24  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and non-ratifying boundary

This prelock artifact defines a candidate epistemic-type schema and payout-boundary matrix for future CDL ratification lanes.

Non-ratifying boundary:
- no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- no mutation of any CDL status field,
- no runtime implementation changes in `ilc_core/`.

## 2. Epistemic type schema candidate

Candidate enum values:
- `objective`
- `subjective`
- `normative`
- `creative_speculative`

Candidate schema fields:
- `epistemic_type` (required enum value),
- `validation_path` (policy-bound lane),
- `payout_boundary` (lane-specific policy gate),
- `promotion_requirements` (if moving toward objective-core treatment).

## 3. Validation-path matrix by type

Matrix statements:
1. `objective` lane uses full contradiction/refute path and full reuse valuation.
2. `subjective` lane uses curation/reuse-resonance path and is not auto-promoted to objective-core without decomposition/reclassification criteria.
3. `normative` lane uses governance-bound challenge path.
4. `creative_speculative` lane remains exploratory by default.

## 4. Payout-boundary matrix by type

Candidate boundaries:
- `objective`: highest contradiction-weighted payout boundary with refute-settlement coupling.
- `subjective`: bounded payout boundary tied to curation quality and reuse resonance, with promotion gate for objective-core admission.
- `normative`: governance-mediated payout boundary, ratification-gated.
- `creative_speculative`: exploratory payout boundary with stricter anti-gaming dampers.

## 5. Sybil and anti-gaming controls (anchor map)

Mandatory anchor statements:
1. reuse-diversity policy remains binding for scoring-boundary integrity.
2. sponsor-root independence is required for quorum independence claims.
3. missing provenance fails closed in scoring path.
4. citation-loop/collusion risk remains explicitly bounded by diversity/cluster controls.

## 6. Ratification-entry criteria and deferred decisions

Entry criteria for future CDL ratification:
- formalize per-type scoring constants and promotion thresholds,
- verify anti-Sybil anchors remain test-covered,
- prove no contradiction between this prelock and existing reuse-diversity policy.

Deferred decisions:
- exact parameter values for type-specific payout scaling,
- promotion threshold constants between subjective and objective lanes,
- governance quorum thresholds for normative lane escalation.

## 7. Canonical source anchors

- `docs/specs/ilc_capability_proof_activation_readiness_gates_v0.1.md`
- `docs/specs/ilc_reuse_diversity_anti_sybil_contract_v0.1.md`
- `docs/specs/ilc_subjective_objective_epistemic_type_and_sybil_guardrails_precanon_v0.1.md`
- `docs/specs/ilc_historical_simulation_recovery_index_subjective_objective_sybil_v0.1.md`
- `docs/specs/ilc_historical_simulation_replay_evidence_20251009_v0.1.md`
