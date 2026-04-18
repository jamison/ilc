# ILC Phase 727-732 Sequence Lock v0.1

**Phase:** 727  
**Window:** 727-732  
**Date:** 2026-04-18  
**Author:** Codex

`window_727_732_sequence_lock_active`

## 1. Baseline

Window `723-726` is closed. Capsule `v4.9` is the live main-lane frontier at
sequence-lock time. The financial-shard concept remains a real later-lane
candidate, but activation remains explicitly deferred and not yet eligible.
`CDL-017` remains open and unratified. `CDL-062` remains open as the bounded
sovereign-substrate research lane rather than the active lane for this window.

Track B must still be verified from `docs/phases/STATUS.md` tail at execution
time rather than copied from memory or older capsules. At sequence-lock time,
the live tail shows `M-016` complete and the next
planned M-phase as `M-017`.
`track_b_m016_complete_m017_next`

## 2. Inherited gates and constraints

This window inherits the existing constitutional and architectural baselines
and does not reopen them:

- `CDL-017` remains open but not ratifiable in this window,
- `CDL-062` remains the sovereign-substrate research lane,
- `CDL-066` and `CDL-067` remain ratified,
- ADR-0022 remains the private/public and gated-use boundary anchor,
- the financial-shard deferment posture from Window `723-726` remains in
  force.

The inherited hard constraints are:

- no pre-window conversation gate applies,
- no CDL ratification is planned in this window,
- no financial-shard activation may be claimed in-window,
- no new CDL opening may be silently presumed,
- no mutation of `ilc_core/` or `ilc_consensus/` in this docs-only packet,
- no claim that rights/licensing has already become a ratified native contract
  surface.

## 3. Window meaning

Window `727-732` is the adjacent gated-economy hardening lane.

`adjacent_gated_economy_hardening_window_active`
`no_pre_window_conversation_required_for_727_732`
`no_financial_shard_activation_in_window_727_732`
`no_cdl_ratification_planned_in_window_727_732`
`cdl_017_text_review_permitted_but_not_ratifiable_in_window_727_732`

The window exists to make six things explicit:

- which non-financial carry-forward lane is honest after `723-726`,
- how rights and licensing sit relative to epistemic adjudication,
- what minimal public/private contract surfaces should exist for gated shards,
- how private/gated continuity should remain aligned with `CDL-038` and
  `CDL-041`,
- what remains deferred to later constitutional or runtime work,
- how the next handoff should carry the gated-economy boundary forward without
  reopening financial-shard activation.

This is a hardening and boundary window, not an activation, ratification, or
runtime-implementation window.

## 4. Phase table and sequencing

| Order | Phase | Topic | Character |
|---|---:|---|---|
| 1 | 727 | sequence lock | gate / planning |
| 2 | 728 | carry-forward selection and boundary lock | research / planning |
| 3 | 729 | rights / licensing / gated-access disposition | research / spec |
| 4 | 730 | private/gated header and capability-token hardening | research / spec |
| 5 | 731 | coherence report | gate / handoff |
| 6 | 732 | capsule v5.0 and closure gate | gate / handoff |

Phase `728` selects the adjacent carry-forward lane without opening a new CDL.
Phase `729` records the rights/licensing and layer-assignment disposition.
Phase `730` hardens the minimal public/private contract boundary for
private/gated shards. Closure phase is Phase `732`.

## 5. Explicit separation obligations

This window must preserve four non-conflation boundaries:

1. `CDL-062` remains the sovereign-substrate research lane and is not merged
   into this gated-economy hardening work.
2. ADR-0022 remains the architectural boundary anchor rather than a phase
   target for hidden ratification or implementation.
3. Financial-shard activation work remains separate and deferred after
   `723-726`.
4. Rights/licensing and access-surface hardening must not be collapsed into
   ordinary epistemic refutation rules.

The window must also preserve the layered split:

- public anchor and provenance surfaces at L1,
- bounded gated/private shard contract surfaces at the shard layer,
- richer billing, delivery, enterprise permissions, and market microstructure
  at L2/L3.

## 6. Non-goals

This window does not include:

- financial-shard activation,
- any new CDL ratification,
- any default new CDL opening,
- any reopening of the `723-726` trigger-matrix question,
- any runtime implementation of capability tokens or gated shard logic,
- any mutation of `ilc_core/` or `ilc_consensus/`.

This window does not claim that `M-016` solved the stronger public-substrate
replayability question. It only inherits the live Track B status that `M-016`
is complete and `M-017` is next.

## 7. Source inputs

The authoritative source set for the window is:

- `docs/PLANNING_INDEX.md`
- `docs/specs/ilc_window_723_726_closure_gate_726_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v4.9.md`
- `docs/specs/ilc_window_727_732_codex_guidance_and_audit_brief_v0.1.md`
- `docs/specs/ilc_window_727_732_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md`
- `docs/research/ilc_rights_licenses_and_gated_access_surfaces_memo_v0.1.md`
- `docs/specs/ilc_private_gated_shard_header_and_capability_token_contract_candidate_v0.1.md`
- `docs/adr/ADR_0022_Local_First_Private_Use_and_Publication_Bound_Economics.md`
- `docs/specs/ilc_cdl_038_private_to_public_promotion_and_promotion_receipt_ratification_evidence_353_v0.1.md`
- `docs/specs/ilc_cdl_041_shard_lifecycle_ratification_evidence_394_v0.1.md`
- `docs/phases/STATUS.md`

This sequence lock remains active until Phase `732` closes the window.
