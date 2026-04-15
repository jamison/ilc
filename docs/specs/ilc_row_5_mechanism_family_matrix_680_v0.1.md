# ILC Row-5 Mechanism Family Matrix 680 v0.1

Status: mechanism-family matrix artifact
Date: 2026-04-15
Phase: 680
Owner lane: G8 row-5 privacy-preserving public-legitimacy prework

## 1. Purpose

This artifact classifies row-5 mechanism families into:
- near-term tractable
- later-stage tractable
- presumptively inadmissible

`three_bucket_mechanism_family_matrix_complete`

The point is not to pick the final winner. The point is to narrow the design
space and reject families that would break the observability budget or create
new constitutional choke points.

## 2. Near-term tractable families

Near-term tractable means:
- plausibly compatible with the current public-work-only model
- preserves receipt lineage and machine-legible public legitimacy
- can be evaluated before final substrate selection

`near_term_tractable_families_preserve_receipt_lineage_and_auditability`

The near-term tractable shortlist is:

| Family | Why it survives | Main risk |
|---|---|---|
| timing smoothing / bounded batching | reduces naive timing linkage while keeping receipts public | timing windows may hurt freshness or debuggability |
| relay / submission indirection with non-custodial multi-relay support | weakens direct submitter-path linkage without making one relay sovereign | relay concentration can drift into operator dependence |
| commitment / selective-disclosure envelope with public receipt core | keeps public receipt/query path intact while weakening contributor linkage | challenge path can become too complex if disclosure rules are underspecified |

These three families form the survivor set for Phase 681.

## 3. Later-stage tractable families

Later-stage tractable means:
- plausibly valuable
- probably substrate-dependent or heavier-weight
- not honest as the default current-lane answer

`later_stage_tractable_families_include_nullifier_and_heavier_zk_variants`

The later-stage tractable bucket includes:
- nullifier-style submission unlinkability
- heavier ZK or proof-carrying privacy overlays
- more ambitious anonymity-set constructions that depend on later substrate or
  proving ergonomics

These are not rejected. They are deferred out of the near-term default lane.

## 4. Presumptively inadmissible families

Presumptively inadmissible means:
- they break queryability, challengeability, or bounded human auditability
- or they require trusted third-party operators as a structural dependency

`presumptively_inadmissible_families_break_queryability_challengeability_or_operator_independence`

The inadmissible bucket includes:

| Family | Why rejected |
|---|---|
| opaque receipt pooling that removes public queryability | violates machine-legible receipts and receipt lineage |
| trusted privacy broker or mandatory portal | creates a new external choke point and violates anti-bottleneck constraints |
| custodial aggregator that becomes the default submission authority | introduces operator dependence and weakens contestability |
| privacy scheme that requires expert-only verification as the normal path | violates bounded human auditability |

`phase_680_rejection_list_is_more_important_than_premature_family_selection`

The rejections matter more than premature winner selection because they prevent
future scope drift into privacy theater or hidden centralization.

## 5. Phase-681 scoping consequence

Phase 681 should simulate against the near-term tractable survivor set rather
than the full family universe.

If Phase 681 shows that all near-term tractable survivors fail the degradation
metric or observability budget, the lane must iterate back into Phase 680
narrowing or explicitly elevate later-stage dependence in the 682 decision.
