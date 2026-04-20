# ILC Phase 749-752 Sequence Lock v0.1

**Phase:** 749  
**Window:** 749-752  
**Date:** 2026-04-20  
**Author:** Codex

`window_749_752_sequence_lock_active`
`track_b_m021_complete_m022_next`
`planning_consolidation_window_active`
`master_completion_roadmap_authorized_in_window_749_752`
`stale_planning_doc_retirement_authorized_in_window_749_752`
`m_series_lane_update_authorized_in_window_749_752`
`no_convergence_window_open_in_window_749_752`
`no_cdl_017_ratification_in_window_749_752`
`no_option_b_graduation_in_window_749_752`
`rows_5_and_7_remain_spec_closed_runtime_pending_at_window_open`
`row_8_remains_inherited_at_window_open`
`uncommitted_m_track_drafts_do_not_satisfy_convergence_entry`

## 1. Baseline

Window `745-748` is closed. Capsule `v5.3` is the latest closed-window capsule.
The later Mysticeti convergence window is commissioned but not open.

At live execution time, the authoritative Track B line is taken from
`docs/phases/STATUS.md` tail rather than from the frozen `v5.3` capsule:

- `**Current:** M-021 (SIM-LEAKAGE-01 execution / audit remediation) complete. sim_leakage_01_verdict=fail accurately documented and remediation fixes cleanly verified.`
- `**Next planned phase:** M-022 (Gemini Lane Handoff Package)`

That Track B line supersedes the older `M-019` / `M-020` wording frozen in
Window `745-748` planning surfaces.

## 2. Inherited gates and constraints

The inherited constitutional and runtime posture at Window `749-752` open is:

- `CDL-017` remains open and unratified.
- `CDL-066`, `CDL-067`, and `CDL-068` remain ratified.
- row `5` remains `spec_closed_runtime_pending`.
- row `7` remains `spec_closed_runtime_pending`.
- row `8` remains inherited and unchanged.
- ADR-0028 Option D remains the active posture.
- the later convergence window remains commissioned but not open.

This window does not reopen any settled lane. It consolidates planning surfaces
only.

## 3. Window meaning

Window `749-752` is a planning-consolidation lane with three linked outputs:

1. a single human-readable master completion roadmap from the current frontier
   through RC candidate,
2. an in-place M-series lane update that preserves the current Gemini / Claude
   execution pattern and aligns the lane text with the live frontier, and
3. archival headers on historically overtaken planning docs whose load-bearing
   forward content is explicitly carried into the new roadmap.

No runtime evidence is produced in this window. No constitutional ratification
occurs in this window.

## 4. Convergence-window posture at open

The later convergence window remains bounded by the commissioned artifact-entry
rules from Phase `746`.

This sequence lock therefore fixes two simultaneous truths:

1. the live Track B current/next line now reads `M-021` complete and `M-022`
   next, and
2. neither local worktree drafts nor planning-surface text are sufficient to
   satisfy any convergence entry condition by themselves.

Convergence entry still requires committed artifact-class re-verification at
the later convergence sequence lock. In particular:

- the row-7 censorship bundle must be re-verified against the Phase `741`
  contract,
- the row-5 leakage-results carrier must be committed and re-verified against
  the Phase `740` commissioning contract,
- the strong-exitability drill results must be committed and re-verified
  against the Phase `741` contract.

Uncommitted Gemini worktree drafts remain below that authority threshold and
therefore do not satisfy convergence entry.

## 5. Planning-consolidation posture at open

This window is authorized to:

- create `docs/specs/ilc_master_completion_roadmap_v0.1.md`,
- update `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`,
- add archival or superseded headers to designated older planning docs,
- advance `docs/PLANNING_INDEX.md`,
- close with a coherence report and closure gate.

This window is not authorized to:

- open the later convergence window,
- move row `5` to `runtime_closed`,
- move row `7` to `runtime_closed`,
- advance row `8`,
- ratify `CDL-017`,
- graduate Option B,
- mutate `ilc_core/` or `ilc_consensus/`.

## 6. Phase table and sequencing

| Order | Phase | Purpose | Class |
|---|---|---|---|
| 1 | 749 | sequence lock | gate / planning |
| 2 | 750 | master completion roadmap + M-series lane update | planning |
| 3 | 751 | archival headers + planning-index advance | planning / archival |
| 4 | 752 | coherence report + closure gate | gate / handoff |

Phase `752` is the closure gate for the window.

## 7. Explicit separation obligations

The following boundaries remain mandatory throughout the window:

- Track B current/next wording comes from `STATUS.md` tail, not from frozen
  capsules or older roadmaps.
- Convergence entry remains artifact-gated even if Track B current/next wording
  has moved.
- The master roadmap may summarize future windows and convergence sequencing,
  but it may not claim that any row, CDL, or Option B gate has already crossed.
- Archival headers may retire stale planning docs, but only after the new
  master roadmap explicitly covers the forward-looking content those docs used
  to carry.

## 8. Non-goals

This window does not perform:

- any ratification of `CDL-017`,
- any move of row `5` to `runtime_closed`,
- any move of row `7` to `runtime_closed`,
- any advancement of row `8`,
- any Option B graduation claim,
- any reopening of the legal positioning technical facts annex,
- any mutation of `ilc_core/` or `ilc_consensus/`,
- any use of uncommitted M-track worktree drafts as convergence authority.

## 9. Source inputs

- `docs/PLANNING_INDEX.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.3.md`
- `docs/phases/STATUS.md`
- `docs/specs/ilc_window_745_748_closure_gate_748_v0.1.md`
- `docs/specs/ilc_window_749_752_guidance_v0.1.md`
- `docs/specs/ilc_mysticeti_convergence_window_commissioning_spec_746_v0.1.md`
- `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.4.md`
- `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md`
- `docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md`
