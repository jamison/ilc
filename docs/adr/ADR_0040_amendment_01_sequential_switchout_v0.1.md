# ADR-0040 Amendment 01: Sequential Switch-Out Jury Design

**Status:** DRAFT — candidate amendment; not ratified; requires human GO and CDL authority before implementation.
**Phase:** 1568-Fix2i
**Date:** 2026-06-29

## Purpose

This draft amends ADR-0040 with a sequential switch-out model for jury panels.
It does not activate runtime behavior. It records design decisions, invariants,
SIM evidence, and non-authorizations that must be reviewed before any ratified
implementation.

## Relationship to ADR-0040

ADR-0040 remains the governing accepted ADR for jury eligibility and assignment.
This document is a draft amendment only. The current additive 7+1 model remains
canon until this amendment or a successor CDL is ratified.

## Phase 1429 Guard Boundary

`PRODUCTION_ASSIGNMENT_NOT_ACTIVATED = False` in
`ilc_core/epistemic/jury_assignment_runtime.py` is authorized by Phase 1429.
The name is a double negative: `False` means the assignment quote/execution
machinery is active inside the already authorized boundary.

Phase 1429 covers assignment quote execution and deterministic epoch-hash
selection. It does not cover public RC, reviewer payment, ECU settlement,
production VRF assignment, public serving, or J-008 public gate conditions.

## Resolved Design Decisions

### 1. Switch-Out Non-Response

**Decision:** Option B, one retry with a fresh draw from the same committed
lane-specific `eligible_set_root`; then fallback to escalation policy.

Rationale: one retry avoids silent anti-capture degradation while bounding
liveness cost. The same root keeps the assignment replayable and avoids a
second eligibility snapshot dependency. If the retry also fails:

- ordinary lanes record `diversity_fail_escalated` or `switchout_nonresponse_degraded_evidence`;
- high-stakes lanes escalate to Tier 2 review;
- no settlement effect follows without CDL authority.

No indefinite redraw loop is authorized.

### 2. Switch-Out Time Window

**Decision:** the switch-out window is expressed in validation epochs, not
wall-clock time.

- Trigger: sealed-vote commitment of the last original-7 reviewer.
- Minimum: 1 validation epoch.
- Maximum: 3 validation epochs for the first switch-out attempt.
- Retry: at most 3 additional validation epochs.

If the switch-out or retry does not commit within the bounded window, the
panel must follow the non-response route above. Finality must not wait
indefinitely.

### 3. Switch-Out Pool Source

**Decision:** use the same lane-specific `eligible_set_root` committed for the
initial panel, filtered before commitment by:

- reputation threshold;
- specialization or capability credential;
- conflict and operator-domain constraints;
- CDL-V3 diversity constraints.

The switch-out is not drawn from "any eligible agent in the network." It is
drawn from the same lane-qualified snapshot, excluding the original 7 and any
conflicted agents.

### 4. Random Slot Removal Seed

**Decision:** the removed original slot is computed from:

```text
slot_seed = SHA-384(
  "ILC_JURY_SWITCHOUT_SLOT_V1" ||
  assignment_context_hash ||
  switchout_vote_commit_hash ||
  epoch_finalization_randomness
)
slot_index = slot_seed mod 7
```

The seed must not include revealed vote contents from the original 7.

### 5. Economic Treatment

Economic treatment remains unauthorized:

```text
discarded_reviewer_economic_treatment: requires_cdl_authority
switchout_accuracy_bonus_treatment: requires_cdl_authority
switchout_base_fee_treatment: requires_cdl_authority
```

This amendment draft does not define reviewer payment, penalty, burn, slash,
wallet debit, treasury event, or settlement effect.

### 6. Runtime-Memory-Substrate Independence

The following boundary tokens are recorded for later CDL/ADR work:

```text
same_cxl_pool_operator_not_independent_for_substrate_purposes
runtime_memory_substrate_custody_requires_attestation
weight_hash_or_model_family_alone_is_not_sufficient_independence_evidence
substrate_custody_settlement_effect_requires_cdl_authority
```

These are not active runtime checks. They are design constraints for later
substrate-custody and representational-independence work.

## Critical Invariants

### INVARIANT-1: Vote-Blind Isolation

The switch-out agent must not observe original-7 revealed votes before
committing its own sealed vote. The switch-out may only see the review payload,
assignment context, and any permitted public metadata.

### INVARIANT-2: Finality Gate Over Final Counted 7

Quorum `k=5` is evaluated only over the final counted 7: the 6 original slots
remaining after random removal plus the switch-out. A quorum of the original 7
alone must not finalize the result before switch-out commit or bounded failure
resolution.

### INVARIANT-3: Post-Replacement Diversity

CDL-V3 diversity and independence checks must be validated over the final
counted 7. If the final counted 7 fails the diversity floor, the result is not
settlement-final and must be escalated or retried under ratified rules.

## Assignment Context Hash

The switch-out extension binds the existing assignment context to the selected
eligible set and algorithm version:

```text
assignment_context_hash = SHA-384(
  "ILC_JURY_ASSIGNMENT_CONTEXT_V2" ||
  review_lane ||
  node_commitment ||
  eligible_set_root ||
  formation_epoch ||
  assignment_algorithm_id ||
  diversity_policy_id
)
```

`node_commitment` must not reveal `node_cid` before the privacy conditions for
the review lane are satisfied.

## SIM Summary

The accompanying SIM report is
`docs/specs/ilc_phase_1568_fix2i_sequential_switchout_sim_v0.1.md`.

Key result: a random switch-out does not reduce unconditional static capture
probability under an IID attacker-control model; exchangeability makes the
final random 7 have the same compromised-count distribution. Its value is
privacy and anti-adaptive-capture: attackers cannot know the final counted
panel during the original voting window if switch-out entropy remains unknown.

## Remaining Open Questions

No open design question from the Fix2i prompt remains unresolved for draft
purposes. Runtime implementation still requires:

- CDL authority for economic treatment;
- CDL or ADR authority for substrate-custody settlement effects;
- final choice on whether blind-jury CDL work blocks public RC or routes
  post-RC;
- implementation-specific tests after any ratification.

## Required CDL Authority Before Implementation

Implementation of the sequential switch-out as canonical jury behavior requires
separate authority. This draft does not ratify:

- switch-out runtime behavior;
- reviewer payment;
- economic treatment of discarded reviewers;
- blind jury assignment;
- substrate-custody gates;
- public jury notification;
- VRF assignment.

## Non-Claims

This draft does not activate production jury assignment beyond the already
authorized Phase 1429 boundary, does not flip any production guard, does not
authorize reviewer payment, does not authorize ECU or ILC settlement, does not
open or ratify any CDL, and does not authorize public RC.
