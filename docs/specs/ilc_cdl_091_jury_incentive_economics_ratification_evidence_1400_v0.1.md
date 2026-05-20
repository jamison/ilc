# ILC CDL-091 Jury Incentive Economics Ratification Evidence 1400 v0.1

**Phase:** 1400
**Date:** 2026-05-20
**Status:** ratification evidence committed; CDL register mutation performed in Phase 1400 C2
**Owner lane:** G8 Jury Economy / Launch Readiness

```text
cdl_091_ratified_phase_1400
cdl_091_jury_incentive_economics_ratification_evidence_committed
cdl_091_historical_hardening_phase_1399_ref_asserted
reviewer_payment_not_activated_phase_1400
```

## 1. Purpose

This document records the evidence and scope constants for ratifying CDL-091,
Jury Incentive Economics. It consumes the Phase 1399 prelock and authorizes the
constitutional decision that ordinary jury-review work uses fixed-base-plus-
delayed-accuracy-weighted compensation with anti-approval-volume controls.

Ratification does not activate reviewer payments, distribute ECU, mutate ledger
state, implement the Phase 1401 runtime stub, activate treasury budgets, or
change the J-008 production jury activation gate verdict.

## 2. Claim Verification Table

| Claim | File or symbol checked | Result |
|-------|------------------------|--------|
| CDL-091 is open before Phase 1400 ratification | `docs/specs/ilc_constitutional_decision_log_v0.1.md` before C2 | confirmed |
| Phase 1399 prelock scope constants exist | `docs/specs/ilc_cdl_091_jury_incentive_economics_prelock_1399_v0.1.md` | confirmed |
| Phase 1399 register-opening commit can be read with `git show` | `git show 06993864:docs/specs/ilc_constitutional_decision_log_v0.1.md` | confirmed |
| Historical CDL-091 state at Phase 1399 C1 was open | same `git show` command | confirmed |
| No reviewer-payment runtime exists before Phase 1401 | filesystem search for `ilc_core/epistemic/jury_incentive_runtime.py` | confirmed |
| Phase 1400 prompt had stale `ratified_date: 2026-05-19` wording | `docs/antigravity_tasks/antigravity_prompt__phase_1400_g8_cdl_091_jury_incentive_economics_ratification.md` | confirmed and corrected to 2026-05-20 |

## 3. Historical Hardening

Phase 1400 uses the Phase 1399 formal register-opening commit, not the Phase
1394 J-004 lane-opening artifact, as the historical hardening reference.

```bash
git show 06993864:docs/specs/ilc_constitutional_decision_log_v0.1.md | rg -n "^\\| CDL-091 \\|"
```

Result: the historical row contains `| open |`, `opened_phase: 1399`, and
`opening_token: cdl_091_jury_incentive_economics_opened_phase_1399`.

```text
cdl_091_historical_hardening_phase_1399_ref_asserted
```

## 4. Ratified Scope Constants

The following Phase 1399 prelock constants are ratified by CDL-091:

| Constant | Ratified value |
|----------|----------------|
| `PRIMARY_REVIEW_FUNDING_SOURCE` | `fixed_pooled_review_budget` |
| `SECONDARY_CONTESTED_FUNDING_SOURCE` | `petition_bond_for_contested_or_escalated_cases` |
| `BASE_REVIEW_FEE_ECU` | `Decimal("0.05")` |
| `PANEL_PAYMENT_MODEL` | `per_reviewer_flat_plus_delayed_accuracy_bonus` |
| `REGULAR_PANEL_SIZE` | `7` |
| `OUTSIDER_SEATS` | `1` |
| `MAX_COMPENSATED_REVIEWERS` | `8` |
| `REVIEWER_QUORUM_K` | `5` |
| `ACCURACY_BONUS_MAX_MULTIPLIER` | `Decimal("1.00")` |
| `ACCURACY_BONUS_VESTING_EPOCHS` | `4` |
| `APPEAL_SURVIVAL_WEIGHT` | `Decimal("0.35")` |
| `REFUTATION_SURVIVAL_WEIGHT` | `Decimal("0.35")` |
| `INDEPENDENT_REVIEWER_CONSENSUS_WEIGHT` | `Decimal("0.20")` |
| `LONG_RUN_GRAPH_SURVIVAL_WEIGHT` | `Decimal("0.10")` |
| `APPROVAL_BIAS_MIN_REVIEWS` | `20` |
| `APPROVAL_BIAS_Z_THRESHOLD` | `Decimal("2.50")` |
| `OUTLIER_BONUS_ATTENUATION` | `Decimal("0.50")` |
| `APPROVAL_ONLY_PAYMENT_REJECTED` | `true` |
| `REVIEWER_PAYMENT_NOT_ACTIVATED` | `true` |

All economic values remain Decimal strings. No float value is ratified for ECU,
reward, stake, bond, or budget arithmetic.

## 5. Ratified Economic Posture

CDL-091 ratifies the following posture:

1. Ordinary review work uses a fixed pooled review budget as the preferred
   funding source.
2. Contested, escalated, appeal, or refutation-driven work uses petition-bond
   funding as the preferred secondary source.
3. The base fee compensates completed valid review work, not approval outcome.
4. Delayed accuracy-weighted bonus depends on later survival, appeal,
   refutation, independent reviewer agreement, and long-run graph survival
   signals.
5. Approval-only payment is rejected because it creates approval-volume bias.
6. Sustained high-side approval-rate outliers may have delayed bonuses
   attenuated after due-process checks.

## 6. Non-Activation

```text
reviewer_payment_not_activated_phase_1400
```

Phase 1400 ratification does not:

- activate reviewer payment;
- distribute ECU;
- mutate ledger state;
- activate treasury budgets;
- implement `ilc_core/epistemic/jury_incentive_runtime.py`;
- flip any J-008 gate condition;
- authorize production jury assignment;
- activate public graph admission;
- publish public RC;
- create a legal conclusion.

Phase 1401 remains responsible for the default-off runtime stub. Later review
lane wiring and gate re-run phases remain responsible for any production
activation path.

## 7. CDL Register Mutation

The Phase 1400 C2 register mutation records:

```text
ratified_phase: 1400
ratified_date: 2026-05-20
ratification_token: cdl_091_ratified_phase_1400
evidence_document: docs/specs/ilc_cdl_091_jury_incentive_economics_ratification_evidence_1400_v0.1.md
```

## 8. Graph Delta

```text
graph_delta=load_bearing_artifact_changed:docs/specs/ilc_constitutional_decision_log_v0.1.md -> constitutional/cdl
```
