# ILC MemPalace Internal Retrieval Adoption and Boundary 606 v0.1

Status: internal tooling adoption packet
Date: 2026-04-10
Classification: bounded internal retrieval standardization; not protocol law

## 1. Purpose and boundary

`mempalace_is_retrieval_only_not_canonical_authority`.

This packet adopts MemPalace as an optional local retrieval and memory-recovery
layer for ILC internal development work.

`approved_context_pack_and_repo_canon_remain_authoritative`.

MemPalace may help agents or operators find relevant historical discussions,
walkthrough evidence, prior prompts, and planning lineage. It does not become a
source of constitutional truth, ratified law, or execution authority. Canonical
answers remain anchored to the repo's ratified and accepted artifacts,
especially the approved planning pack, current handoff stack, accepted ADRs,
and current phase specs.

`external_payment_and_wallet_boundaries_remain_unchanged`.

This packet does not authorize any change to current wallet authority,
payment-ingress semantics, native escrow, public release posture, or `ilc_core/`
runtime scope.

## 2. Suitability assessment

MemPalace is suitable for ILC internal use because the project now produces a
large volume of:
- specs,
- walkthroughs,
- planning prompts,
- audit notes,
- research notes,
- and long conversation histories.

That makes semantic retrieval useful for provenance and history questions such
as:
- where a boundary was first discussed,
- which handoff carried a defer forward,
- which walkthrough recorded a fix,
- or which research note framed a later decision.

MemPalace is not adopted here as a replacement for:
- `docs/phases/STATUS.md`,
- handoff specs,
- context capsules,
- the approved planning pack,
- ratified specs,
- or accepted ADRs.

The retrieval layer is therefore adopted for memory recovery and provenance
assistance, not for truth arbitration.

## 3. Authority-tier retrieval model

`tier_a_canonical_sources_default_for_answers`.

The MemPalace corpus must be split into four authority tiers:

1. `tier_a_canonical`
   - current ratified or accepted source-of-truth material
   - default basis for direct answers
2. `tier_b_planning`
   - approved planning packs, active candidate groupings, current planning docs
   - only used when the question is explicitly about planning or open lanes
3. `tier_c_evidence`
   - walkthroughs, phase evidence, tool outputs, integration proof docs
   - used for execution provenance and historical verification
4. `tier_d_historical`
   - research notes, dredge outputs, chats, draft supplements, old context packs
   - used only as labeled provenance support, never as default authority

Answering policy:
- direct answers default to `tier_a_canonical`
- planning questions may cite `tier_b_planning` after identifying them as
  planning-only surfaces
- provenance questions may use `tier_c_evidence`
- historical rationale may use `tier_d_historical`, but only with explicit
  labeling that the source is historical, draft, or non-normative when
  applicable

## 4. Internal developer adoption plan

Recommended bounded rollout:

1. Pilot corpus
   - ingest `docs/specs/`, `docs/adr/`, `docs/phases/`, and selected current
     `docs/research/` materials into the tiered corpus
2. Historical expansion
   - ingest recovered conversation exports and dredge outputs as Tier D only
3. Shared-query discipline
   - require agents to cite retrieved source paths and then verify against the
     authoritative tier before making a strong claim
4. Prompt discipline
   - future prompts may permit MemPalace as an optional retrieval tool, but must
     explicitly preserve repo canon as authoritative
5. Maintenance
   - refresh the corpus after major handoffs, capsule updates, or new closure
     windows so retrieval remains synchronized with the current state

This plan intentionally avoids a repo dependency on MemPalace itself. Adoption
here is documentation, corpus policy, and operator guidance only.

## 5. Future local FAQ/oracle boundary

`public_faq_oracle_must_not_answer_from_unvetted_historical_corpus`.

A future post-RC local FAQ/oracle tool may use MemPalace or a similar retrieval
layer, but only under these rules:
- default answer basis must remain `tier_a_canonical`
- planning or historical material must be explicitly labeled as non-canonical
  when used
- draft, research, and historical-chat corpora must never silently answer as if
  they were ratified protocol law
- any public-facing tool must preserve current payment, wallet, and release
  boundaries rather than infer new ones from historical discussion

## 6. Non-goals and deferred items

This packet does not:
- install MemPalace into the repo or CI,
- add ChromaDB or other runtime dependencies to ILC,
- define a public oracle implementation,
- widen wallet authority,
- authorize native ledger escrow,
- authorize inbound payment ingress,
- authorize market-liquidity or node-market protocol work,
- or reopen any frozen 585-605 closure.

Deferred items:
- any future local FAQ/oracle runtime
- any explicit MCP integration for MemPalace use by agents
- any automated corpus refresh tooling
- any public-release or product-surface integration
