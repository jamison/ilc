# ILC ADR Stale Reconciliation Strike Force 1156 v0.1

Status: planning reconciliation; non-canonical; no ADR acceptance
Phase context: Window 1156-1165 pre-sequence planning
Date: 2026-05-04

`adr_stale_reconciliation_strike_force_1156`

---

## 1. Purpose

This memo fills the forward-planning gap identified after Window 1148-1156:
several high-authority ADRs remain `Proposed` even though later MemPalace
history may have resolved their original uncertainty. The goal is to route the
next ADR acceptance work cleanly before Atlas v0.2 grows further.

This document does not accept any ADR, mutate the signed Genesis v0.1 artifacts,
open a CDL, or authorize v0.2 signing. It provides evidence-backed routing for
the Window 1156-1165 candidate guidance.

---

## 2. Current Frontier

Window 1148-1156 closed with:

- signed Genesis v0.1 unchanged at 32 nodes and 55 edges;
- unsigned Atlas v0.2 candidate at 36 nodes and 63 edges;
- accepted ADR nodes already added: ADR-0019, ADR-0026, ADR-0028, ADR-0031;
- proposed ADRs blocked from Tier-2 promotion until acceptance review;
- ADR-0008 reconciled in commit `b6e9e7a8`.

Active carry-forward from the Phase 1155 handoff:

- ADR-0020 acceptance review priority before Tier-3 embedding linkage;
- ADR acceptance review batch for ADR-0012, ADR-0022, ADR-0023, and ADR-0008;
- formal Genesis Canonical Lineage Contract ADR;
- operational release-key ADR;
- SIM-SPECTRAL-04 execution planning.

---

## 3. Acceptance Criteria Applied

This memo uses the same three criteria recorded in the Window 1156-1165
candidate guidance:

1. The ADR describes a decision that has been substantively implemented or is
   durable governance that will not be reversed.
2. The ADR has no open blocking objections in the governance record.
3. The ADR content correctly describes the protocol's current or intended state.

If an ADR only partially satisfies these criteria, the correct result is scoped
acceptance review or explicit deferral, not blind promotion.

---

## 4. Priority Disposition

| ADR | Current status | Strike Force disposition | Routing |
|-----|----------------|--------------------------|---------|
| ADR-0020 | Proposed | Highest-priority acceptance candidate | Phase 1157 |
| ADR-0012 | Proposed | Likely acceptance candidate after settlement/coupling reconciliation | Phase 1158 |
| ADR-0022 | Proposed | Likely scoped acceptance candidate for local/private boundary | Phase 1158 |
| ADR-0023 | Proposed | Narrow acceptance candidate; full architecture still partly staged | Phase 1158 |
| ADR-0008 | Proposed | Acceptance-ready for architectural boundary claim after reconciliation | Phase 1158 |
| ADR-0009/0010 | Proposed | Stale but not current-window blockers | Window 1166+ or later |
| ADR-0015/0016/0017 | Proposed | Larger economics rewrite/review, not quick stale cleanup | Later economics lane |

---

## 5. ADR-0020 Finding

`adr_0020_acceptance_review_ready_priority`

ADR-0020 is the strongest immediate candidate for acceptance review.

Reasoning:

- ADR-0019 is already Accepted and establishes graph-native governance
  compilation boundary logic.
- ADR-0033 is already Accepted and establishes the star map as a homoiconic
  epistemological entity.
- GENESIS-COMPILE-01 and the Atlas v0.1/v0.2 work now operationalize the idea
  that governance artifacts, graph nodes, and runtime explanation surfaces
  compile through the same substrate.
- SIM-SPECTRAL-04 now explicitly depends on claim-composition projection, which
  is an application of knowledge-node-first reasoning.
- Tier-3 runtime linkage for `embedding_pipeline.py` and
  `node_value_governance_conformance.py` is blocked until ADR-0020 is accepted
  or explicitly deferred.

Known caution:

- ADR-0020 contains migration-language about governance constants and
  documentation. Acceptance should be scoped to the design principle and
  migration discipline, not interpreted as immediate runtime migration of every
  governance constant.

Recommended Phase 1157 result if review confirms no hidden blocker:

- update ADR-0020 status to `Accepted`;
- add `adr:0020_knowledge_node_first_design_principle` to the unsigned v0.2
  candidate;
- emit `adr_0020_accepted_phase_1157`.

---

## 6. ADR-0012 Finding

`adr_0012_acceptance_review_likely_ready`

ADR-0012 is likely acceptance-ready after a focused MemPalace review.

Reasoning:

- Later settlement-substrate reconciliation treated ADR-0012 as a lower-authority
  proposed input, not as rejected.
- CDL-084 and the provenance settlement runtime now provide concrete evidence
  for graph activity producing ECU through ratified rules.
- Settlement/wallet boundary locks separate hot-path messaging from settlement
  authority, matching ADR-0012's directional coupling.
- Genesis economics Phases 597-600 and the Phase 1129 runtime chain reinforce
  anti-reflexivity and bounded issuance behavior.

Known caution:

- ADR-0012 should not be accepted as locking new ECU settlement windows,
  issuance constants, or public minting terms. Its acceptance surface is the
  coupling and anti-reflexivity contract only.

Recommended Phase 1158 review posture:

- accept if scoped to directional coupling and anti-reflexivity;
- defer only if the review discovers wording that incorrectly implies final
  settlement substrate closure.

---

## 7. ADR-0022 Finding

`adr_0022_acceptance_review_likely_ready_with_boundary_scope`

ADR-0022 is likely acceptance-ready as a local/private/public boundary ADR.

Reasoning:

- CDL-038 ratified private-to-public promotion continuity, successor-node
  promotion, promotion receipts, disclosed lineage, and no automatic public
  corroboration or reuse carry-forward.
- Private/gated shard hardening in Phase 730 defined minimum public header
  surface and access-right reference boundaries without collapsing private
  interiors into public legitimacy.
- Multiple coherence reports preserve ADR-0022 as the separate private/gated
  boundary rather than merging it into Werner, validator, or financial-shard
  lanes.

Known caution:

- Acceptance should not constitutionalize all private/gated business logic,
  licensing, subscriptions, payment execution, or revocation mechanics. Those
  remain future lane work.

Recommended Phase 1158 review posture:

- accept ADR-0022 for the local-first invariant, explicit promotion boundary,
  public anchor/private interior model, and publication-bound economics
  principle;
- keep implementation mechanics deferred.

---

## 8. ADR-0023 Finding

`adr_0023_acceptance_review_scope_narrow_not_full_architecture`

ADR-0023 is stale in a useful way: much of the later evidence now exists, but
full acceptance still requires careful scoping.

Evidence now present:

- Phase 522 originally kept ADR-0023 as research guidance.
- Phase 526 established SIM-AESTHETIC-01 sufficiency.
- Phase 527 established SIM-CENTRALITY-01 and SIM-NOVELTY-01 sufficiency.
- Phase 528 authorized CDL-059 opening for the narrow Layer 2 lane.
- CDL-059 was opened, ratified, and implemented through Phases 529-532.
- CDL-060 and the centrality-gossip lane were later opened, ratified, and
  implemented.
- Phase 542 calibrated passive ECU attribution formula inputs.
- Phase 547 scoped the cross-module signal-floor invariant and identified ADR
  documentation as the right place for that invariant.

Known caution:

- ADR-0023 started as pre-constitutional research. Full acceptance could
  overstate finality for multi-hop centrality, passive ECU long-horizon tuning,
  or future aesthetic re-evaluation rules.

Recommended Phase 1158 review posture:

- accept only a narrowed "architecture now has sufficient evidence for Layer 2
  aesthetic panel, direct-use centrality, and bounded signal/factor separation"
  surface if the ADR text is amended accordingly;
- otherwise defer with a precise gap token requiring a scoped ADR-0023 amendment.

---

## 9. ADR-0008 Finding

`adr_0008_acceptance_review_complete_boundary_ready`

ADR-0008's previous default-defer posture is stale after commit `b6e9e7a8`.

The reconciliation commit resolved the previously-listed blockers at the
architectural-boundary level:

- coefficients and calibration are deferred but no longer block acceptance of
  the boundary separation;
- Genesis ordinary-governance baseline/floor/bonus is closed by Phase 597;
- freshness/reuse boundary is closed by Phase 598;
- Genesis economic tranche is distinguished from governance weight by
  Phases 599-600.

Recommended Phase 1158 review posture:

- include ADR-0008 as an acceptance candidate;
- keep acceptance scoped to epistemic weight, utility flow, governance weight,
  Genesis dilution, and Genesis economic/governance separation;
- do not accept final coefficients or runtime retuning as part of ADR-0008.

---

## 10. Deferred ADRs

`adr_0009_0010_deferred_transport_distribution_reconciliation`

ADR-0009 and ADR-0010 are likely stale because bundle distribution, D2d,
transport, gossip, and packaging work have advanced substantially. They are not
current blockers for Atlas v0.2 or SIM-SPECTRAL-04. Route them to a later
transport/distribution reconciliation window.

`adr_0015_0016_0017_deferred_economic_rewrite_not_quick_cleanup`

ADR-0015, ADR-0016, and ADR-0017 are not good quick-cleanup candidates.
They require larger economics rewrite/review work:

- ADR-0015 has explicit simulation/open economics questions and a dedicated
  family disposition history.
- ADR-0016 and ADR-0017 are tied to treasury, productive ECU expansion, and
  post-issuance economic transition design.
- These surfaces may require rewrite, partial rejection, or replacement rather
  than an ADR-0008-style stale issue cleanup.

---

## 11. Window 1156-1165 Planning Changes

The Window 1156-1165 candidate guidance should inherit this memo as the
Phase 1156 reconciliation basis:

1. Preserve ADR-0020 as Phase 1157 priority.
2. Keep Phase 1158 as independent per-ADR review for ADR-0012, ADR-0022,
   ADR-0023, and ADR-0008.
3. Remove ADR-0008 default-defer language and replace it with
   boundary-acceptance-ready language.
4. Add explicit caution that ADR-0023 is the highest-risk Phase 1158 review
   because full acceptance may overclaim.
5. Keep ADR-0009/0010 and ADR-0015/0016/0017 out of the current window.

---

## 12. Non-Claims

This memo does not:

- accept any ADR;
- mutate the signed v0.1 Genesis star map;
- mutate the unsigned v0.2 candidate;
- open or ratify a CDL;
- authorize Phase 1156 signing;
- modify runtime semantics;
- resolve counsel-track obligations.

`adr_stale_reconciliation_strike_force_1156`
