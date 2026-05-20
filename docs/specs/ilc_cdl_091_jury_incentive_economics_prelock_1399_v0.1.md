# ILC CDL-091 Jury Incentive Economics Prelock 1399 v0.1

**Phase:** 1399
**Date:** 2026-05-20
**Status:** prelock committed; CDL-091 open and not ratified
**Owner lane:** G8 Jury Economy / Launch Readiness

```text
cdl_091_prelock_committed_phase_1399
cdl_091_not_ratified_phase_1399
cdl_091_scope_constants_locked_phase_1399
```

## 1. Purpose

Phase 1394 / J-004 opened the jury incentive economics lane as a spec artifact.
Phase 1399 first registered CDL-091 in the constitutional decision log as open,
then prelocks the scope constants that Phase 1400 may ratify.

This phase does not ratify CDL-091, activate reviewer payments, distribute ECU,
mutate ledger state, implement a runtime path, or authorize production jury
activation.

## 2. Claim Verification Table

| Claim | File or symbol checked | Result |
|-------|------------------------|--------|
| Phase 1394 opened the jury incentive lane but did not mutate the CDL register | `docs/specs/ilc_cdl_jury_incentive_economics_opening_v0.1.md`; `docs/phases/phase_1394_jury_incentive_economics_cdl_opening_walkthrough.md`; pre-Phase-1399 CDL register read | confirmed |
| CDL-091 is now registered as open | `docs/specs/ilc_constitutional_decision_log_v0.1.md`; commit `06993864` | confirmed |
| J-008 still records `JURY_INCENTIVE_CDL_RATIFIED` as NOT_MET | `docs/specs/ilc_production_jury_activation_gate_j008_v0.1.md`; `ilc_core/epistemic/jury_activation_gate.py` | confirmed |
| No jury incentive runtime stub exists in Phase 1399 | filesystem search for `ilc_core/epistemic/jury_incentive_runtime.py` | confirmed |
| J-004 left funding source unresolved | `docs/specs/ilc_cdl_jury_incentive_economics_opening_v0.1.md` sections 6 and 9 | confirmed |

## 3. Prelock Decision

The prelocked funding posture is:

```text
ordinary_review_funding_source_prelocked=fixed_pooled_review_budget
contested_review_funding_source_prelocked=petition_bond_for_contested_or_escalated_cases
```

Fixed pooled review budget is the preferred ordinary-review funding source.
It compensates valid review work without requiring every submitter or challenger
to post a dispute bond. Petition bonds remain the preferred funding source for
contested, escalated, appeal, or refutation-driven work where spam resistance
and skin-in-the-game are material.

This is a governance prelock, not a live treasury or ledger allocation. Any
future public reviewer payment remains subject to the Phase 1387a public
economics admission firewall and later runtime activation authority.

## 4. Scope Constants

All ECU-denominated and weight-like values are Decimal strings for Phase 1400
ratification and Phase 1401 stub wiring. No Python float value is authorized.

| Constant | Prelocked value | Meaning |
|----------|-----------------|---------|
| `PRIMARY_REVIEW_FUNDING_SOURCE` | `fixed_pooled_review_budget` | Ordinary public review work draws from a fixed review budget candidate. |
| `SECONDARY_CONTESTED_FUNDING_SOURCE` | `petition_bond_for_contested_or_escalated_cases` | Contested, appealed, or escalated review may use petition-bond funding. |
| `BASE_REVIEW_FEE_ECU` | `Decimal("0.05")` | Candidate base fee for completed valid review work. |
| `PANEL_PAYMENT_MODEL` | `per_reviewer_flat_plus_delayed_accuracy_bonus` | Base fee is per valid reviewer, not per approval. |
| `REGULAR_PANEL_SIZE` | `7` | Regular reviewer seats inherited from the 7+1 panel structure. |
| `OUTSIDER_SEATS` | `1` | One outsider seat is preserved for anti-capture review. |
| `MAX_COMPENSATED_REVIEWERS` | `8` | Compensation cap for one full 7+1 panel. |
| `REVIEWER_QUORUM_K` | `5` | Candidate quorum count for normal objective-lane review. |
| `ACCURACY_BONUS_MAX_MULTIPLIER` | `Decimal("1.00")` | Delayed bonus may not exceed one base fee per review without later ratification. |
| `ACCURACY_BONUS_VESTING_EPOCHS` | `4` | Candidate minimum delay before accuracy bonus release. |
| `APPEAL_SURVIVAL_WEIGHT` | `Decimal("0.35")` | Weight for review surviving appeal. |
| `REFUTATION_SURVIVAL_WEIGHT` | `Decimal("0.35")` | Weight for review not being overturned by later refutation. |
| `INDEPENDENT_REVIEWER_CONSENSUS_WEIGHT` | `Decimal("0.20")` | Weight for agreement with independent reviewers. |
| `LONG_RUN_GRAPH_SURVIVAL_WEIGHT` | `Decimal("0.10")` | Weight for longer-run non-ejection and non-contradiction. |
| `APPROVAL_BIAS_MIN_REVIEWS` | `20` | Minimum review count before approval-volume bias attenuation applies. |
| `APPROVAL_BIAS_Z_THRESHOLD` | `Decimal("2.50")` | Candidate outlier threshold for approval-rate deviation review. |
| `OUTLIER_BONUS_ATTENUATION` | `Decimal("0.50")` | Candidate delayed-bonus attenuation for sustained outlier approval behavior after due process. |
| `APPROVAL_ONLY_PAYMENT_REJECTED` | `true` | Approval outcome alone must not trigger reviewer payment. |
| `REVIEWER_PAYMENT_NOT_ACTIVATED` | `true` | No payment path is active after Phase 1399. |

## 5. Candidate Bonus Formula

The prelocked bonus candidate is:

```text
accuracy_score =
  appeal_survival * Decimal("0.35")
  + refutation_survival * Decimal("0.35")
  + independent_reviewer_consensus * Decimal("0.20")
  + long_run_graph_survival * Decimal("0.10")

delayed_accuracy_bonus =
  BASE_REVIEW_FEE_ECU
  * min(ACCURACY_BONUS_MAX_MULTIPLIER, max(Decimal("0"), accuracy_score))
```

The formula is intentionally conservative. The base fee pays completed valid
review work; the delayed bonus rewards later correctness signals. A reviewer
whose approval pattern is a sustained high-side outlier may have the delayed
bonus attenuated after ratified due-process checks. Immediate approval volume
does not increase compensation.

## 6. Approval-Volume Bias Mitigation

The following controls are prelocked for Phase 1400 ratification:

1. Payment is tied to valid review completion, not approve/reject outcome.
2. Approval-only payment is rejected.
3. Delayed accuracy bonus depends on later survival and independent signals.
4. Sustained approval-rate outliers are eligible for delayed-bonus attenuation
   only after the minimum review count and due-process review.
5. Future implementation must expose approval-rate telemetry without activating
   public reviewer payment before runtime authority exists.

## 7. Non-Ratification and Non-Activation

CDL-091 remains open and unratified after Phase 1399.

```text
cdl_091_not_ratified_phase_1399
```

Phase 1399 does not:

- ratify CDL-091;
- activate reviewer payments;
- implement `ilc_core/epistemic/jury_incentive_runtime.py`;
- distribute ECU;
- mutate ledger state;
- activate treasury reviewer budgets;
- activate public graph admission;
- activate production jury assignment;
- change the J-008 gate verdict;
- authorize public RC publication;
- create any legal conclusion.

## 8. Phase 1400 Carry-Forward

Phase 1400 must consume this prelock and either ratify or explicitly reject the
prelocked constants. It must reference the Phase 1399 register-opening commit:

```text
phase_1399_register_opening_commit=06993864
```

Phase 1401 remains responsible for any runtime stub after ratification.

## 9. Graph Delta

```text
graph_delta=load_bearing_artifact_changed:docs/specs/ilc_constitutional_decision_log_v0.1.md -> constitutional/cdl
```
