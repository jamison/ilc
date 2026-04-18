# ILC Phase 723-726 Sequence Lock v0.1

**Phase:** 723  
**Window:** 723-726  
**Date:** 2026-04-18  
**Author:** Codex

`window_723_726_sequence_lock_active`

## 1. Baseline

Window `717-722` is closed. Capsule `v4.8` is the live main-lane frontier at
sequence-lock time. `CDL-066` and `CDL-067` are already ratified, `CDL-017`
remains open and unratified, and `CDL-062` remains open as the bounded
sovereign-substrate research lane rather than a financial-shard governance
vehicle.

Track B remains independently moving and must be verified from
`docs/phases/STATUS.md` tail at execution time rather than copied from memory.
At sequence-lock time, the live tail shows `M-015` complete and the next
planned M-phase as `M-016`. `track_b_status_must_be_verified_from_status_tail`

## 2. Inherited gates and constraints

This window inherits the existing constitutional and architectural baselines
and does not reopen them:

- `CDL-047` treasury governance framework,
- `CDL-048` mandatory ECU conversion discipline,
- `CDL-062` as the sovereign-substrate research lane,
- `CDL-066` sender authorization ratified,
- `CDL-067` settlement-state governance vehicle ratified,
- ADR-0022 as the separate private/public and gated-use boundary,
- ADR-0028 as the active Option D posture.

The inherited hard constraints are:

- no pre-window conversation gate applies,
- no financial-shard activation may be claimed in-window,
- no CDL ratification is planned in this window,
- no new CDL opening may be silently presumed,
- no mutation of `ilc_core/` or `ilc_consensus/` in this docs-only packet,
- no claim that post-launch trigger conditions are already satisfied before
  public launch exists.

## 3. Window meaning

Window `723-726` is the sequestered financial-shard eligibility and
gated-economy prefilter lane. It is an eligibility / trigger window, not an
activation window.

`financial_shard_eligibility_window_active`
`no_pre_window_conversation_required_for_723_726`
`no_financial_shard_activation_in_window_723_726`

The window exists to make four things explicit:

- whether the sequestered financial-shard idea remains a real later-lane
  candidate,
- what would have to become true after public launch before a later lane could
  honestly open,
- how contagion, firewall, and auditability boundaries would have to work,
- how this lane stays separate from ordinary shard lifecycle, from
  ADR-0022/private-gated rights hardening, and from `CDL-062`.

This window does not authorize the shard. It defines the honest boundary for
future eligibility, trigger, and deferment reasoning.

## 4. Phase table and sequencing

| Order | Phase | Topic | Character |
|---|---:|---|---|
| 1 | 723 | sequence lock | gate / planning |
| 2 | 724 | eligibility prefilter and lane separation | research / planning |
| 3 | 725 | trigger matrix and contagion / firewall prerequisites | research / spec |
| 4 | 726 | closure | gate / handoff |

Phase `724` publishes the eligibility prefilter without activating the lane.
Phase `725` publishes the minimum trigger conditions and the required
contagion-firewall prerequisites. Closure phase is Phase `726`.

## 5. Explicit separation obligations

This window must preserve three non-conflation boundaries:

1. `CDL-062` remains the sovereign-substrate research lane and is not the same
   lane as financial-shard eligibility work.
2. ADR-0022 and the private/gated shard header/capability-token lane remain
   separate from this window.
3. Ordinary shard-lifecycle law remains separate from this window.

`gated_economy_lane_must_remain_separate_from_private_gated_rights_hardening`

The later financial-shard concept, if ever opened honestly, must preserve a
separate `B_hft` budget surface from `B_e`, an L1/L2 contagion firewall, and
market-microstructure isolation from the base epistemic graph.

## 6. Non-goals

This window does not include:

- financial-shard activation,
- any new CDL ratification,
- any default new CDL opening,
- any reopening of ordinary shard-lifecycle law,
- any reopening of ADR-0022/private-gated access hardening,
- any mutation of `ilc_core/` or `ilc_consensus/`.

This window does not treat historical “ADR-0018” references as accepted live
ADR law, because there is no accepted ADR artifact for ADR-0018 under
`docs/adr/`.

## 7. Source inputs

The authoritative source set for the window is:

- `docs/PLANNING_INDEX.md`
- `docs/specs/ilc_window_717_722_closure_gate_722_v0.1.md`
- `docs/specs/ilc_window_723_726_guidance_v0.1.md`
- `docs/specs/ilc_window_723_726_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md`
- `docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md`
- `docs/specs/ilc_economic_architecture_comprehensive_v0.1.md`
- `docs/specs/ilc_cdl_050_treasury_blocker_resolution_plan_v0.1.md`
- `docs/research/ilc_rights_licenses_and_gated_access_surfaces_memo_v0.1.md`
- `docs/specs/ilc_private_gated_shard_header_and_capability_token_contract_candidate_v0.1.md`
- `docs/specs/ilc_cdl_062_research_lane_handoff_692_v0.1.md`
- `docs/phases/STATUS.md`

This sequence lock remains active until Phase `726` closes the window.
