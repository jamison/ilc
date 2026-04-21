# ILC CDL-017 Interaction Synthesis and Activation Boundary Record 764 v0.1

**Phase:** 764  
**Window:** 763-766  
**Date:** 2026-04-21  
**Author:** Codex

`cdl_017_interaction_synthesis_764_complete`
`cdl_055_carry_forward_verdict_unchanged_under_cdl_017`
`cdl_056_carry_forward_verdict_unchanged_under_cdl_017`
`cdl_068_adjacent_lane_carry_forward_unchanged_under_cdl_017`
`sec_004_post_ratification_activation_scope_reaffirmed`
`activation_boundary_record_764_complete`
`state_at_ratification_genesis_only_hooks_unimplemented_no_non_genesis_validators`
`ratification_opens_validator_governance_lane_only`
`hooks_remain_disabled_until_separate_activation_work`
`first_non_genesis_deployment_requires_human_gate_after_ratification`
`phase_755_dossier_questions_consumed_not_rederived`
`bootstrap_transition_criteria_scope_named_from_opening_and_dossier`
`genesis_sunset_trigger_scope_named_from_opening_and_dossier`
`dynamic_validator_set_activation_boundary_named_from_dossier_and_m_series_lane`
`no_decision_log_mutation_in_phase_764`

## 1. Purpose and authority order

This Phase `764` artifact discharges the specific obligations reserved by the
Phase `763` sequence lock:

1. publish the explicit `CDL-055` / `CDL-056` carry-forward-versus-amendment
   matrix in writing,
2. publish the activation-boundary record that states what changes and does not
   change when `CDL-017` later ratifies,
3. consume the Phase `755` dossier and the committed Q1-Q6 / prelock evidence
   surfaces as evidence inputs rather than re-deriving them from memory.

This is not a ratification artifact. It does not mutate the constitutional
decision log. It does not authorize runtime hook activation. It does not
authorize first non-Genesis validator deployment.

Authority order for this record is:

1. `docs/specs/ilc_phase_763_766_sequence_lock_v0.1.md`
2. `docs/specs/ilc_cdl_017_ratification_readiness_dossier_v0.1.md`
3. `docs/specs/ilc_cdl_017_opening_stub_695_v0.1.md`
4. `docs/specs/ilc_constitutional_decision_log_v0.1.md`
5. `docs/specs/ilc_cdl_055_validator_staking_and_liveness_enforcement_ratification_evidence_496_v0.1.md`
6. `docs/specs/ilc_cdl_056_validator_trust_tier_elevation_ratification_evidence_501_v0.1.md`
7. `docs/specs/ilc_cdl_068_topology_shuffle_authorization_ratification_evidence_743_v0.1.md`
8. `docs/research/ilc_validator_agent_q1_q6_prewindow_resolution_v0.1.md`
9. `docs/research/ilc_validator_agent_design_evidence_v0.1.md`
10. `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`

## 2. Explicit interaction matrix

The required carry-forward / amendment matrix is:

| Surface | Phase 764 verdict | Exact statement | Evidence consumed |
|---|---|---|---|
| `CDL-055` | **carried forward unchanged** | `CDL-017` does not alter validator participation stake, liveness penalties, equivocation slash boundary, or the separate re-admission boundary. These remain governed by ratified `CDL-055`. | `CDL-055` ratification evidence §4-§5; Phase `763` sequence lock §4.3 |
| `CDL-056` | **carried forward unchanged** | `CDL-017` does not alter the non-inheritable trust-tier flag, its liveness-threshold tie to `CDL-055`, or the bounded consensus-dispute tiebreaker. These remain governed by ratified `CDL-056`. | `CDL-056` ratification evidence §4-§5; Phase `763` sequence lock §4.3 |
| `CDL-068` | **carried forward unchanged as adjacent constitutional lane** | `CDL-068` continues to govern topology-shuffle authorization, diversity thresholds, and randomness-source boundary. `CDL-017` consumes this as an adjacent constitutional neighbor rather than amending it. | Phase `755` dossier §2; `CDL-068` ratification evidence; validator-agent design evidence §6-§7 |
| `SEC-004` | **not ratified here; remains post-ratification activation work** | `SEC-004` remains an implementation obligation that begins only after `CDL-017` ratifies. `TransferCertificate` epoch binding and historical validator-set resolution are not solved by this phase or by ratification rhetoric alone. | Phase `755` dossier §3 and §5; M-series lane `SEC-004` section; Phase `763` sequence lock §4.2 |

The expected answer for `CDL-055` and `CDL-056` is therefore explicit and
complete: both are carried forward unchanged in this window. No amendment text
is proposed in Phase `764`.

## 3. Activation-boundary record

### 3.1 State at the moment of ratification

The inherited system state that Phase `765` will ratify against is:

- Genesis-only validator authority remains operative for the near-term testnet,
- `CDL-017` is still open at Phase `764`,
- no non-Genesis validator has been admitted by constitutional act alone,
- M-007 governance hooks exist but remain disabled:
  - `admit_validator` is `unimplemented!`,
  - `eject_validator` is `unimplemented!`,
- `SEC-004` is not yet implemented,
- first non-Genesis validator deployment remains unauthorized,
- row `7` is already `runtime_closed`, row `5` remains honest-fail
  `spec_closed_runtime_pending`, and row `8` remains inherited with no
  candidate evaluation; those convergence outcomes are inherited evidence, not
  things ratification will rewrite.

### 3.2 What changes constitutionally when CDL-017 ratifies

When `CDL-017` ratifies, the constitutional change is narrow and explicit:

- validator admission and ejection become a ratified governed protocol action,
- the constitutional lane for bootstrap transition criteria is opened,
- the constitutional lane for Genesis-sunset triggers as validator-authority
  design is opened,
- the constitutional activation boundary for dynamic validator-set operation is
  named,
- later post-ratification activation work becomes constitutionally grounded
  rather than extra-constitutional.

This is the constitutional opening of the validator-governance lane only.

### 3.3 What does not change automatically on ratification

Ratification does **not** automatically do any of the following:

- activate the M-007 `admit_validator` / `eject_validator` hooks,
- implement `SEC-004`,
- authorize the first non-Genesis validator deployment without a later human
  gate,
- rewrite `CDL-055`,
- rewrite `CDL-056`,
- rewrite `CDL-068`,
- close row `5`,
- change row `8` from its inherited candidate-evaluation-pending posture.

The first non-Genesis validator remains a later operator decision after
ratification and after the required post-ratification activation work is ready.

## 4. Consumed evidence inputs and dossier-question dispositions

### 4.1 Q1-Q6 and prelock evidence consumption record

Phase `764` consumes the committed prelock block rather than re-deriving it:

| Input | Consumed ratification-relevant conclusion | Evidence source |
|---|---|---|
| Q1 | Validator identity linkage remains derived-sub-key with provable linkage, not same-key identity | Q1-Q6 resolution Q1; validator-agent design evidence §2 and §4 |
| Q2 | Validator minimum stake remains evidence-backed and simulation-derived rather than conversation-fixed | Q1-Q6 resolution Q2; validator-agent design evidence §4 and §7 |
| Q3 | Admission semantics remain threshold-gated eligibility, not proportional seat weighting | Q1-Q6 resolution Q3; validator-agent design evidence §4 |
| Q4 | Validation pools remain outside `CDL-017` core and require a later separate constitutional lane | Q1-Q6 resolution Q4; validator-agent design evidence §4-§5 |
| Q5 | Epoch-hash posture and the named VRF-upgrade trigger are already explicit; Phase `764` consumes them as inherited constraints, not as fresh design work | Q1-Q6 resolution Q5; validator-agent design evidence §6-§7 |
| Q6 | Validator composition remains governed by explicit `validator_cluster_id` diversity language and the committed full-pass `SIM-TOPOLOGY-01` thresholds | validator-agent design evidence §6-§7; Phase `755` dossier §2 |

The practical Phase `764` consequence is narrow: these items are already
specified enough to support ratification and the activation-boundary record.
They are consumed here, not re-negotiated here.

### 4.2 Phase 755 dossier questions closed for Phase 765 foundation

The outstanding ratification-foundation questions named by the Phase `755`
dossier are closed at the constitutional-boundary level as follows:

| Dossier question | Phase 764 disposition | Evidence consumed |
|---|---|---|
| Bootstrap-transition criteria | **Resolved in scope.** Bootstrap transition is a governed validator-admission / validator-ejection constitutional surface, with threshold-gated eligibility and no automatic deployment implied. | Phase `755` dossier §1 and §4; opening stub §1 / §3 / §5; validator-agent design evidence §4 |
| Genesis-sunset trigger scope | **Resolved in scope.** Genesis sunset is part of the validator-authority design lane in `CDL-017`; this phase fixes the scope as constitutional trigger design, not a self-executing runtime cutoff. | Phase `755` dossier §1 and §4; opening stub §1 / §3 / §5; Phase `763` sequence lock §4.1 |
| Dynamic validator-set activation boundary | **Named explicitly.** Ratification opens the constitutional lane only; hooks remain `unimplemented!`, `SEC-004` remains post-ratification work, and first non-Genesis deployment remains a later human gate. | Phase `755` dossier §3-§5; M-series lane `SEC-004`; Phase `763` sequence lock §4.2 / §4.4 |

This closes the loop on the dossier without pretending that runtime activation
has happened. The questions are answered at the law-and-boundary level, which
is exactly what Phase `764` is supposed to produce for Phase `765`.

## 5. Phase 765 handoff constraints

Phase `765` must consume this record as factual foundation and must preserve
all of the following:

- restate the `CDL-055` / `CDL-056` carry-forward-unchanged verdicts,
- restate that `CDL-068` remains adjacent and unchanged,
- restate that `SEC-004` is post-ratification implementation work,
- state explicitly that ratification opens validator-governance law only,
- preserve the separate human gate for first non-Genesis validator deployment,
- preserve the non-claim that M-007 hooks are already active,
- follow the Phase `763` two-commit discipline with a single-row decision-log
  mutation only in commit 2.

No decision-log mutation occurs in Phase `764`.

## 6. Source inputs

- `docs/specs/ilc_phase_763_766_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_017_ratification_readiness_dossier_v0.1.md`
- `docs/specs/ilc_cdl_017_opening_stub_695_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_cdl_055_validator_staking_and_liveness_enforcement_ratification_evidence_496_v0.1.md`
- `docs/specs/ilc_cdl_056_validator_trust_tier_elevation_ratification_evidence_501_v0.1.md`
- `docs/specs/ilc_cdl_068_topology_shuffle_authorization_ratification_evidence_743_v0.1.md`
- `docs/research/ilc_validator_agent_q1_q6_prewindow_resolution_v0.1.md`
- `docs/research/ilc_validator_agent_design_evidence_v0.1.md`
- `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`
- `docs/research/ilc_mysticeti_gemini_lane_handoff_M022_v0.1.md`
- `docs/specs/ilc_master_completion_roadmap_v0.1.md`
