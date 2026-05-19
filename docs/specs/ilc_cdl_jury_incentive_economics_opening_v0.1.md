# ILC CDL Jury Incentive Economics Opening v0.1

**Phase:** 1394 / J-004
**Date:** 2026-05-19
**Status:** CDL economics lane opened; not ratified
**Owner lane:** G8 jury / epoch-work canonicalization

```text
jury_incentive_economics_cdl_opened_phase_j004
approval_volume_bias_risk_recorded
fixed_plus_accuracy_weighted_panel_compensation_recommended
reviewer_payment_not_activated_phase_j004
```

## 1. Purpose

This document opens the explicit CDL economics lane for jury, reviewer, and
panel compensation. It does not ratify payment amounts, activate reviewer
payments, mutate ledger state, or implement runtime settlement.

The design question is how to compensate review work without creating a direct
incentive to approve marginal work for fee flow. The recommended opening
position is:

```text
fixed_base_plus_delayed_accuracy_bonus_recommended
```

Reviewers should receive a fixed base fee for completed valid review work plus
a delayed accuracy-weighted component tied to later survival, appeal outcome,
refutation outcome, or other ratified long-run quality metrics. They should not
be paid solely per approval.

## 2. Claim Verification Table

| Claim | File or symbol checked | Result |
|-------|------------------------|--------|
| General jury compensation is not implemented or ratified | `docs/specs/ilc_jury_epoch_work_canon_map_v0.1.md`; `docs/research/ilc_jury_deliberation_research_memo_791_v0.1.md`; `docs/research/ilc_inverted_ecu_model_precanon_v0.1.md` | confirmed |
| J-003 taxonomy requires review lanes for reward-bearing public objective nodes | `docs/specs/ilc_public_node_review_taxonomy_v0.1.md` | confirmed |
| ADR-0040 makes jury eligibility opt-in and routes non-response economics to J-004 | `docs/adr/ADR_0040_Jury_Eligibility_Assignment.md` | confirmed |
| ADR-0041 defines T0.5 quarantine and does not activate public economics | `docs/adr/ADR_0041_Agent_INIT_and_Ingestion_Protocol.md`; `docs/specs/ilc_public_node_review_taxonomy_v0.1.md` | confirmed |
| CDL-054 validator reward routing is a default-off validator reward surface, not reviewer compensation | `docs/specs/ilc_cdl_054_validator_economic_incentive_framework_ratification_evidence_491_v0.1.md`; `ilc_core/epoch/validator_reward_pool_routing_runtime.py` | confirmed |
| CDL-047 treasury governance is default-off and does not activate a reviewer budget | `docs/specs/ilc_cdl_047_treasury_governance_ratification_evidence_418_v0.1.md`; `ilc_core/epoch/treasury_governance_runtime.py` | confirmed |
| CDL-083 covers ejected-stake quorum and upheld REFUTATION attribution, not a general reviewer-payment system | `docs/specs/ilc_cdl_083_h_con_02_panel_quorum_ejected_stake_opening_1103_v0.1.md`; `ilc_core/economics/epoch_attribution_settle_runtime.py` | confirmed |
| Public economic event construction requires public graph admission evidence and no private carry-forward | `docs/specs/ilc_public_economics_admission_firewall_1387a_v0.1.md`; `ilc_core/ledger/public_economics_admission_firewall.py` | confirmed |
| Approval-volume bias is an already identified mechanism-design risk | `docs/research/ilc_inverted_ecu_model_precanon_v0.1.md`; `docs/research/ilc_opus_inverted_ecu_model_review_v0.1.md`; MemPalace planning retrieval | confirmed |

## 3. Current Canon Boundaries

### 3.1 Reviewer service remains opt-in

Jury participation is not obligatory for every graph-connected agent. ADR-0040
defines reviewer eligibility as lane-specific opt-in availability. Non-opt-in
agents are not penalized for review non-response.

Opted-in reviewers may later be subject to lane-specific non-response policy
after assignment or seat acceptance, but this phase does not activate any
slashing, fee forfeiture, cooldown, or reputation decay. J-004 does not
activate any slashing.

Stable slashing phrase: J-004 does not activate any slashing.

```text
non_response_consequences_deferred_to_later_ratification
```

### 3.2 Reviewer payment remains inactive

No current runtime path constructs a general jury-review payment. CDL-054 is
validator reward routing. CDL-047 is treasury governance. CDL-083 is a narrow
upheld-refutation and ejected-stake quorum lane. None is a general reviewer
compensation system.

```text
validator_rewards_not_reviewer_rewards_without_cdl_bridge
treasury_governance_not_reviewer_budget_without_cdl_bridge
cdl_083_refutation_attribution_not_general_reviewer_compensation
```

### 3.3 Public economics firewall applies

Any future reviewer payment that creates protocol ECU, public reputation,
public settlement, public corroboration, or public claimability is a public
economic event. It must pass the Phase 1387a public-economics admission
firewall and cannot be constructed from private, local, or T0.5-only material.

```text
public_only_economics_firewall_preserved_for_reviewer_payment
```

Stable firewall phrase: Phase 1387a public-economics admission firewall.

## 4. Options Considered

| Option | Benefits | Risks | J-004 disposition |
|--------|----------|-------|-------------------|
| Fixed review fee for completed valid review work | Pays effort without depending on approval outcome; predictable reviewer income; helps opt-in participation | Can reward low-effort reviews unless paired with quality controls | Accepted as base component |
| Petition-bond funded review | Filters spam; gives challengers skin in the game; matches Phase 791 petition-bond research | Can deter legitimate low-resource challenges; needs bond sizing and refund/burn rules | Candidate funding source, not ratified |
| Delayed accuracy-weighted bonus | Rewards long-run correctness instead of immediate approval; aligns with survival, appeal, and refutation outcomes | Requires outcome tracking, escrow, and delayed settlement | Accepted as bonus component |
| Split fixed fee plus delayed accuracy bonus | Covers review effort while rewarding quality; reduces approval-volume bias | More complex than single fee | Recommended default |
| Approval-only reviewer payment | Simple to measure | Directly rewards rubber-stamping and marginal approvals | Rejected |
| Validator reward carveout | Existing validator economics precedent | Validator reward pool is not reviewer compensation and remains default-off | Rejected unless a later CDL bridge exists |
| Treasury-funded reviewer budget | Possible public reserve source | Treasury remains default-off; requires public economics and governance controls | Deferred funding candidate |
| Non-response slash / decay after opt-in | Protects panel liveness | Must distinguish non-opt-in, pre-decline, conflict recusal, and accepted assignment failure | Deferred to ratification policy |

## 5. Recommended Opening Design

The recommended reviewer compensation design is:

```text
fixed_plus_accuracy_weighted_panel_compensation_recommended
```

Mechanically, a future ratified runtime should separate:

1. **Base review fee:** paid for completed, valid, timely review work regardless
   of approve/reject outcome.
2. **Delayed accuracy-weighted bonus:** released later according to ratified
   quality signals such as appeal survival, later refutation, consensus with
   independent reviewers, long-run graph survival, or downstream contradiction
   detection.
3. **Anti-rubber-stamp controls:** approval-only payment is rejected, reviewer
   approval rates must be monitored, and persistent outlier approval behavior
   should reduce delayed bonuses or future assignment priority after due process.
4. **Opt-in non-response policy:** no penalty for non-opt-in agents; possible
   cooldown, lost fee, bond forfeiture, or availability-score decay only for
   opted-in reviewers who accept assignment and then fail to respond.

```text
approval_only_panel_payment_rejected
anti_rubber_stamp_controls_required_before_payment_activation
```

## 6. Funding Source Opening

J-004 does not choose a funding source. It records candidates and boundaries:

| Funding source | Opening status |
|----------------|----------------|
| Petition bond | Candidate source for contested or escalated cases; needs bond sizing, refund, burn, and challenge rules. |
| Fixed pooled budget | Candidate source for ordinary panel work; needs budget cap and public economics firewall integration. |
| Treasury | Candidate only after a later CDL bridge and treasury activation authority. |
| Validator reward fraction | Not appropriate by default; validator rewards are not reviewer rewards without explicit CDL bridge. |
| Refutation/stake paths | Specialized T5 lanes only; CDL-083 and CDL-084 do not authorize generic reviewer payment. |

```text
petition_bond_candidate_funding_source_recorded
fixed_pooled_review_budget_candidate_recorded
reviewer_payment_activation_requires_later_ratification
```

## 7. Simulation Requirements

Before ratification, a simulation or shadow harness should evaluate:

| Scenario | Required measurement |
|----------|----------------------|
| Approval-only baseline | Approval rate inflation, false-positive admission rate, rubber-stamp concentration. |
| Fixed base fee only | Review completion rate, low-effort review rate, backlog behavior. |
| Fixed plus delayed accuracy bonus | Long-run quality, appeal/refutation survival, reviewer income variance. |
| Petition-bond funding | Legitimate challenge deterrence, spam suppression, bond sizing sensitivity. |
| Non-response policy | Reviewer opt-in rate, assignment completion, unfair punishment of conflict recusals. |
| Public economics firewall | Whether all payment candidates require public admission evidence before settlement. |

Simulation must use exact numeric types for economic state and must not introduce
float-based reward, stake, or settlement logic.

## 8. Non-Authorizations

Phase 1394 / J-004 does not:

- ratify reviewer payment economics;
- activate reviewer payments;
- activate slashing, fee forfeiture, cooldown, or reputation decay;
- mutate `ilc_core/`;
- mutate ledger state;
- mutate any CDL register row;
- activate public graph admission;
- activate public economics, public reputation, public settlement, public
  corroboration, or public claimability;
- authorize production jury assignment;
- authorize public RC claims;
- authorize counsel conclusions.

Stable non-authorization phrase:

```text
No runtime mutation, CDL register mutation, ledger mutation, reviewer payment activation, public economics activation, production jury activation, public graph admission activation, public RC claim, counsel approval, or legal conclusion occurred.
```

## 9. Open Questions for Later Ratification

| Question | Routed to |
|----------|-----------|
| What is the base review fee formula and unit? | J-008 or later CDL ratification |
| How long should delayed accuracy bonuses vest? | Simulation / J-007 shadow harness / later CDL |
| Which quality signals count for bonus release? | J-007 shadow harness and later CDL |
| What bond sizes are acceptable for petitions and refutations? | Mode-2 carry-forward, J-004/J-008 |
| Can treasury fund a reviewer budget? | Later CDL bridge to CDL-047 |
| Can validator rewards fund reviewer work? | Later CDL bridge to CDL-054 |
| What non-response penalties apply after accepted assignment? | Later CDL ratification |

## 10. Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/specs/ilc_cdl_jury_incentive_economics_opening_v0.1.md -> jury_epoch_work_canon
```
