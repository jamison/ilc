# ILC Public-Legitimacy Observability Budget 679 v0.1

Status: observability-budget artifact
Date: 2026-04-15
Phase: 679
Owner lane: G8 row-5 privacy-preserving public-legitimacy prework

## 1. Purpose

This artifact fixes the observability floor that row-5 mechanism work may not
trade away.

`observability_budget_caps_privacy_mechanism_design_space`
`strong_row_5_observability_floor_is_hard_constraint_not_preference`

Row 5 is not allowed to solve privacy by making public legitimacy opaque.

## 2. Non-negotiable constraints

The following four constraints are non-negotiable:

- machine-legible receipts
- receipt lineage intact
- challengeability preserved
- bounded human auditability preserved

`machine_legible_receipts_nonnegotiable`
`receipt_lineage_nonnegotiable`
`challengeability_nonnegotiable`
`bounded_human_auditability_nonnegotiable`

These are hard constraints on later mechanism evaluation, not advisory
preferences.

## 3. What remains publicly visible

The observability floor requires that:
- a receipt can be located and queried
- the receipt can be placed in legitimacy lineage
- a bounded human can inspect what happened without expert-only tooling
- a machine client can query the same public legitimacy surface
- later challenge and contest paths remain coherent

This lane therefore preserves:
- receipt existence
- receipt queryability
- receipt lineage continuity
- public contestability

This lane does not require preserving trivial contributor linkage.

## 4. Inadmissible opacity

The following are disqualifying even if they improve unlinkability:

- receipts that are no longer queryable by ordinary participants
- legitimacy traces that cannot be challenged without privileged infrastructure
- lineage surfaces that become unverifiable without expert-only tooling
- public verification paths that require one privileged portal, one hosted
  dashboard, or one operator-specific shell

`default_specialized_tooling_requirement_is_inadmissible`
`one_privileged_portal_verification_path_is_inadmissible`

Any default design that requires specialized tooling to verify public
legitimacy claims is inadmissible as the default row-5 posture.

## 5. Ordinary participant verification floor

The ordinary participant verification floor means:
- a participant can discover a receipt
- a participant can inspect enough surrounding lineage to understand why it is
  legitimate
- a participant can see how to challenge it
- a participant does not need to run a specialized proving stack merely to
  verify that the public legitimacy surface is coherent

This does not prohibit richer expert tooling. It prohibits expert-only default
verification.

## 6. Budget implication for later phases

The observability budget permits:
- privacy work that weakens contributor linkage
- privacy work that weakens repeated-submission correlation
- privacy work that weakens operator-path or hosted-query inference

The observability budget forbids:
- privacy work that hides the receipt itself
- privacy work that breaks receipt lineage
- privacy work that destroys challengeability
- privacy work that makes public legitimacy unreadable to ordinary humans or
  ordinary machines

`receipt_visibility_yes_contributor_linkability_no`

That is the governing design trade in this lane.
