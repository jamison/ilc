# ILC Reputation Gap Audit GAP-REPUTATION-00 v0.1

Status: source-grounded audit
Phase: 1589a / GAP-REPUTATION-00
Date: 2026-07-29
Sensitivity: NON-SENSITIVE

Output token: `reputation_canon_audit_complete_GAP_REPUTATION_00`

## 1. Current runtime inventory

| Surface | File | Current behavior | Production guard state | Committed evidence artifact |
|---|---|---|---|---|
| Decimal reputation voting/atrophy | `ilc_core/consensus/reputation.py` | Computes `calculate_voting_power(stake, trust_vector)` and `apply_atrophy(agent_state, current_epoch)` with Decimal-only arithmetic. | `require_production_reputation_scoring_activation()` always raises `production_reputation_scoring_not_activated_phase_1357`. | None. It returns Decimal/dict values only. |
| CDL-V1 temporal decay | `ilc_core/reputation/temporal_decay_runtime.py` | Computes issuance-epoch-scoped decay with Decimal inputs and twelve-place quantization. | No production reputation activation guard in this module; it is a helper. | None. It returns Decimal values only. |
| CDL-V2 sybil heuristics | `ilc_core/identity/sybil_resistance_runtime.py` | Computes bounded cluster, burst-write, diversity, and aggregate sybil penalty signals. | No reputation activation guard in this module; the code comments classify outputs as advisory anti-sybil heuristics, not settlement or quorum weights. | None. It returns bounded score values only. |
| CDL-055 staking/liveness | `ilc_core/validator/staking_liveness_runtime.py` | Defines `GENESIS_STAKE_AMOUNT = Decimal("400")`, liveness miss threshold `8`, full equivocation slash, and liveness penalty fraction. | No guard in helper; production admission remains guarded in `admission_ejection_runtime.py`. | None. It returns a status dict. |
| CDL-056 trust-tier | `ilc_core/validator/trust_tier_runtime.py` | `is_trust_tier_eligible()` checks only missed epochs and equivocation state. | No guard in helper; production admission remains guarded in `admission_ejection_runtime.py`. | None. It returns booleans or selected candidates. |
| CDL-017 admission/ejection quote runtime | `ilc_core/validator/admission_ejection_runtime.py` | Builds default-off `ValidatorAdmissionDecision` and `ValidatorEjectionDecision` quote objects. | `require_production_validator_admission_activation()` does not activate production admission; it raises unless exact token supplied and then raises not-implemented. | Quote object only; no live ValidatorSet mutation. |

## 2. Guard state inventory

- `PRODUCTION_REPUTATION_SCORING_NOT_ACTIVATED_TOKEN = "production_reputation_scoring_not_activated_phase_1357"` is live in `ilc_core/consensus/reputation.py`.
- `require_production_reputation_scoring_activation()` unconditionally raises that token. There is no bypass token in the current function.
- `PRODUCTION_VALIDATOR_ADMISSION_NOT_ACTIVATED_TOKEN = "production_validator_admission_not_activated_phase_1353"` remains the validator-admission guard token in `ilc_core/validator/admission_ejection_runtime.py`.
- `PRODUCTION_VALIDATOR_ADMISSION_ACTIVATION_TOKEN = "first_non_genesis_validator_deployment_requires_later_human_gate"` exists, but the guard function still raises `production_validator_admission_activation_not_implemented_phase_1353` after the token check.
- `trust_tier_runtime.py`, `staking_liveness_runtime.py`, `temporal_decay_runtime.py`, and `sybil_resistance_runtime.py` are helper surfaces. They do not themselves activate production reputation scoring, produce roots, or mutate validator membership.

## 3. Gap enumeration

### 3.1 No AgentReputationRecord

Repo search found no `class AgentReputationRecord` in `ilc_core/`. Current code has reputation calculations and validator admission quote objects, but no epoch-bound, immutable, content-addressed per-agent reputation record.

### 3.2 No extractor

Repo search found no production `reputation_extractor` module in `ilc_core/`. There is no runtime that constructs an agent reputation record from graph snapshot evidence, lifecycle evidence, attribution evidence, liveness, equivocation, and sybil signals.

### 3.3 No AgentReputationRoot

Repo search found no `AgentReputationRoot` or `reputation_evidence_root` in `ilc_core/`. No root is computed over sorted reputation records, and no such root is available for epoch-state commitments or validator admission.

### 3.4 No binding to validator admission

`ValidatorAdmissionDecision` has fields for `validator_id`, `agent_id`, `stake_ecu`, `minimum_stake_ecu`, `trust_tier_requested`, `trust_tier_eligible`, and activation tokens. It has no `reputation_evidence_root`, no `earned_ecu_work_score_root`, no `liveness_state_root`, and no role-state model distinguishing candidate/provisional/official validators.

Phase 1589 now requires reputation evidence for validator admission, but the current runtime does not produce it. This is a real pre-RC gap.

## 4. CDL canon constraints

| Authority | Status | Constraint for reputation lane |
|---|---|---|
| Phase 345 reputation adjoint contract | Canonical spec artifact | Reputation is derived from lifecycle outputs and graph history, not stored as mutable inline node state. Mutable inline reputation is forbidden. |
| CDL-017 | Ratified Phase 765 | Provides the validator-governance framework, bootstrap transition criteria, Genesis sunset trigger design, and dynamic validator-set activation boundary. It does not silently supersede CDL-055 or CDL-056. |
| CDL-055 | Ratified Phase 496 | Validator participation stake, liveness penalties, equivocation slash, and re-admission boundary remain under CDL-055. |
| CDL-056 | Ratified Phase 501 | Trust-tier is a non-inheritable validator flag with liveness/equivocation coupling and bounded consensus-dispute tiebreaker. It is not the same as reputation. |
| CDL-V1 | Ratified Phase 330 | Temporal decay is ratified as a governance parameter; current runtime exposes Decimal helper functions. |
| CDL-V2 | Ratified Phase 331 | Sybil-resistance heuristics are ratified as participant-identity and reuse-validation safeguards. Current runtime returns advisory bounded signals, not settlement roots. |
| CDL-081 | Ratified Phase 943 | REUSE and CO_AUTHORSHIP ECU attribution are ratified; `REUSE_ATTRIBUTION_RATE=0.20` is ECU payout authority, not an agent reputation weight. |
| CDL-084 | Ratified Phase 1113, amended Phase 1126 | PROVENANCE chain ECU attribution is ratified; `PROVENANCE_DECAY_ALPHA=Decimal("0.45")` and `PROVENANCE_MAX_DEPTH=3` govern ECU flow, not a reputation formula by themselves. |

## 5. Historical research canon-status table

| Item | Source | Classification | Disposition |
|---|---|---|---|
| Derived-not-inline reputation boundary | `docs/specs/ilc_reputation_and_agent_profile_adjoint_contract_345_v0.1.md` | `tier_a_canonical` | Binding design constraint for all future reputation records. |
| CDL-017 validator-as-governed-role law | CDL-017 decision-log row and Phase 765 evidence | `tier_a_canonical` | Ratified governance home for validator admission/ejection boundaries. |
| CDL-055/056 liveness and trust-tier surfaces | CDL-055 and CDL-056 ratification evidence | `tier_a_canonical` | Required inputs or constraints, but not full reputation. |
| CDL-V1 temporal decay | Decision log and runtime | `tier_a_canonical` | Decay support signal; not a full reputation record. |
| CDL-V2 sybil resistance | Decision log and runtime | `tier_a_canonical` | Anti-sybil support signal; not a full reputation record. |
| SIM-REUSE-01 result via CDL-081 | CDL-081 decision-log row | `tier_a_canonical` for the ratified rate | `REUSE_ATTRIBUTION_RATE=0.20` is ECU attribution, not a reputation component by itself. |
| SIM-PROVENANCE-01 result via CDL-084 amendment | CDL-084 decision-log row | `tier_a_canonical` for the ratified alpha/depth | `PROVENANCE_DECAY_ALPHA=0.45` and max depth 3 are ECU attribution parameters, not a reputation formula by themselves. |
| Validator-as-agent identity design doc | `docs/research/ilc_validator_agent_identity_system_v0.1.md` | `tier_b_planning` | Strong design reference: validators are agents with validator roles. Exact role-record implementation still needs current phases. |
| Pressure-flow reputation model | `docs/research/ilc_pressure_flow_reputation_and_entropy_intelligence_research_note_v0.2.md` | `tier_c_evidence` | Pre-canon research. It explicitly requires SIM-F before replacing BAL/CDL-052 quality-derived legitimacy. Do not use as public-RC formula yet. |
| BAL four-component node scoring / `node_value_kernel.py` | `ilc_core/analysis/node_value_kernel.py` and pressure-flow context | `tier_c_evidence` for reputation formula use | Analysis-grade node-quality kernel, not settlement-grade or validator-admission-grade reputation. |
| Bipartite coupling `R_agent * avg(R_node)` | pressure-flow research note | `tier_c_evidence` | Candidate research mechanism. Requires SIM and CDL authority before use in admission. |
| SIM-F adversarial pressure-reputation farming | pressure-flow research note and context | `tier_c_evidence` / missing execution evidence | Planning gap. No source read in this phase establishes SIM-F as complete. |

## 6. Design constraints for CDL-106 and CDL-107

### CDL-106: AgentReputationRecord schema

CDL-106 should define a first-class, immutable, epoch-bound `AgentReputationRecord` and `AgentReputationRoot`. It should not lock the scoring formula unless the CDL process explicitly does so. Minimum schema constraints:

- `agent_id` must be the accountable identity.
- `epoch` must bind the record to a closed epoch.
- `graph_snapshot_root`, `lifecycle_event_root`, `liveness_root`, `equivocation_root`, and `sybil_risk_root` should be independent evidence commitments.
- `attribution_root` may be optional until the GAP-ECU backward-attribution lane produces a committed root.
- `previous_reputation_record_root` should hash-chain per-agent reputation history.
- Canonical JSON must use deterministic key ordering and exact Decimal strings.

### CDL-107: reputation/ECU boundary and validator eligibility

CDL-107 should decide the scoring semantics, thresholds, and public-RC eligibility tiers. Required decisions:

- Reputation gates validator eligibility; it is not ECU and not a transferable balance.
- Earned ECU work score may be an eligibility evidence root, but transient current ECU balance should not be confused with a slashable bond or reputation.
- Trust-tier is a liveness/equivocation flag and may contribute to eligibility, but it is not full reputation.
- Candidate and provisional validators must have zero BFT quorum weight.
- Official validators require non-null reputation evidence, earned-work evidence, and liveness evidence unless covered by a time-bounded Genesis bootstrap authority certificate.
- Genesis/bootstrap authority must be a sunsetted exemption, not hard-coded maximum reputation.
- Pressure-flow/BAL formula choices require explicit authority and anti-gaming evidence. The pressure-flow research note must not become a runtime formula by accident.

## 7. Non-claims

This phase does not open CDL-106 or CDL-107, does not mutate the constitutional decision log, does not create `AgentReputationRecord`, does not create an extractor, does not compute or commit an `AgentReputationRoot`, does not bind reputation to validator admission, does not clear production reputation scoring, does not clear production validator admission, does not admit a validator, does not mint ECU or ILC, does not write settlement or wallet state, does not mutate Rust consensus, does not regenerate or push a public mirror, and does not activate public RC.
