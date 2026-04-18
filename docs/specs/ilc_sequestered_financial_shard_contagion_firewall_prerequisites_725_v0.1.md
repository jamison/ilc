# ILC Sequestered Financial Shard Contagion Firewall Prerequisites 725 v0.1

**Phase:** 725  
**Window:** 723-726  
**Date:** 2026-04-18  
**Author:** Codex

`contagion_firewall_prerequisites_explicit`

## 1. Baseline

The sequestered financial-shard concept only remains coherent if its risk
surface can be isolated from the base epistemic graph, from L1 treasury
governance, and from the public knowledge-economy budget lane.

This artifact defines those minimum isolation requirements without activating
the lane.

## 2. Required isolation surfaces

The required isolation surfaces are:

- separate governance review from ordinary shard lifecycle,
- explicit separation from `CDL-062` sovereign-substrate work,
- explicit separation from ADR-0022/private-gated rights and access hardening,
- explicit market-microstructure isolation from the base epistemic graph,
- explicit L1/L2 separation for failure containment.

`l1_l2_firewall_required`
`market_microstructure_must_remain_sequestered`

## 3. Budget and firewall prerequisites

The budget and firewall prerequisites are:

- a dedicated `B_hft` surface must remain separate from `B_e`,
- Treasury / L1 logic must not read or react to the market lane directly,
- failure in the market lane must not contaminate the base knowledge-economy
  route,
- opening-side review must name the exact firewall surfaces before any later
  activation proposal is considered.

`b_hft_must_be_separate_from_b_e`

## 4. Auditability and failure containment

The minimum auditability and failure-containment expectations are:

- identifiable boundaries between L1 and the later financial lane,
- observable evidence for demand and later opening justification,
- explicit spillover and contagion failure cases,
- a rollback or containment story if the lane later proves unsafe,
- a later-window decision on whether constitutional action is even needed.

## 5. Non-goals

This artifact does not:

- activate the lane,
- implement `B_hft`,
- authorize any new CDL opening,
- reopen private/gated access hardening,
- reopen ordinary shard-lifecycle law,
- mutate `ilc_core/` or `ilc_consensus/`.
