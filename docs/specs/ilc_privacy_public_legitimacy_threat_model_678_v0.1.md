# ILC Privacy / Public-Legitimacy Threat Model 678 v0.1

Status: threat-model artifact
Date: 2026-04-15
Phase: 678
Owner lane: G8 row-5 privacy-preserving public-legitimacy prework

## 1. Purpose and boundary

This artifact narrows checklist row 5 into a concrete threat model for public
submissions.

`phase_678_threat_model_scopes_row_5_to_correlation_minimization_and_unlinkability`
`public_submission_privacy_not_private_work_privacy`

This phase is not about hiding all private work. It is about reducing
correlation and linkage across public submissions while preserving machine
legibility, receipt lineage, contestability, and bounded human auditability.

Out of scope:
- private off-graph work that never enters the public legitimacy surface
- final mechanism-family selection
- final sovereign substrate selection
- perfect anonymity against all possible observers

## 2. Protected thing

The minimum protected thing in this lane is:
- contributor identity
- cross-submission linkage
- receipt and settlement linkage

The receipt itself remains public.

`receipt_exists_but_contributor_linkage_is_target_of_protection`

The row-5 target is not to hide that a receipt exists. The target is to make it
materially harder to infer who submitted it and whether multiple public
submissions came from the same contributor over time.

Stress-test surfaces beyond the minimum target include:
- timing correlation
- operator-metadata correlation
- query-pattern correlation

## 3. Adversary classes

The minimum adversary set for this window is:
- ordinary public observers
- explorers and indexers
- hosted-query surfaces that aggregate receipt metadata over time
- operator-path and gateway surfaces that see submission or query metadata

`hosted_query_surface_aggregation_is_primary_public_scale_surveillance_vector`
`operator_path_metadata_and_timing_correlation_are_realistic_secondary_surfaces`

Red-team scope beyond the minimum closure set includes:
- hosting-provider observers
- stronger path observers
- colluding explorer plus gateway surfaces

This phase does not require a global-passive-adversary solution as its minimum
closure standard.

## 4. Leak surfaces

The main leak surfaces for row 5 are:

1. admission and namespace linkage
2. receipt publication and receipt queryability
3. settlement and delayed-settlement continuity
4. timing and publication-window metadata
5. hosted-query aggregation
6. operator-path metadata
7. repeated query-pattern or explorer-access correlation

`namespace_receipt_timing_and_query_pattern_leakage_must_be_modeled_together`

These surfaces are coupled. A candidate family that reduces one surface but
leaves the others trivially linkable does not meaningfully solve the row-5
problem.

## 5. Realistic public participation model

For this window, a realistic public submitter means:
- a contributor who emits repeated public receipts over time
- a contributor whose work is visible through ordinary explorer or query
  surfaces
- a contributor who may interact through more than one relay, gateway, or
  client path
- a contributor who is not trying to run a full anonymity-ops program

This matters because row 5 is not judged against heroic user behavior. It is
judged against ordinary public participation patterns.

## 6. Threat statements that later phases must preserve

The following statements are fixed by this threat model:

- row 5 is a correlation problem, not a "hide all work" problem
- receipts remain public and machine-legible
- receipt existence is not the protected surface; contributor and linkage
  inference is
- hosted-query aggregation is the most likely public-scale surveillance vector
- operator-path metadata and timing remain real secondary leakage surfaces
- any plausible mechanism family must be evaluated against the coupled
  namespace, receipt, timing, and query-pattern surfaces rather than one
  surface in isolation

## 7. Carry-forward into later phases

Phase 679 must treat the following as hard observability constraints:
- receipt lineage intact
- challengeability intact
- machine-legible participation intact
- bounded human auditability intact

Phase 680 must reject families that only create cosmetic privacy by shifting
linkage from one surface to another.

Phase 681 must evaluate correlation recovery under realistic repeated public
participation rather than single-submission toy cases.
