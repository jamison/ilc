# ILC Phase 717-722 Sequence Lock v0.1

**Phase:** 717  
**Window:** 717-722  
**Date:** 2026-04-18  
**Author:** Codex

`window_717_722_sequence_lock_active`

## 1. Baseline

Window `713-716` is closed. Capsule v4.7 is the live main-lane frontier at
sequence-lock time. `CDL-066` and `CDL-067` are already ratified, `CDL-017` remains open and unratified, and rows `5` and `7` remain
`spec_closed_runtime_pending`.

Track B state is moving independently and must be verified from
`docs/phases/STATUS.md` tail at execution time rather than copied from memory.
At sequence-lock time, the live tail shows `M-015` complete and the next planned M-phase as `M-016`. `track_b_status_must_be_verified_from_status_tail`

## 2. Inherited gates and constraints

This window inherits the existing constitutional and architectural baselines and
does not reopen them:

- `CDL-047` treasury ECU-governor framework,
- `CDL-048` mandatory ECU conversion deadline,
- `CDL-051` epoch-state and quorum-record contract,
- `CDL-059` aesthetic panel,
- `CDL-060` and `CDL-061` as the active gossip law,
- `CDL-066` sender authorization,
- `CDL-067` settlement-state governance vehicle,
- `ADR-0028` Option D active posture.

The inherited hard constraints are:

- no pre-window conversation gate applies,
- no CDL ratification is planned in this window,
- no new CDL opening may be treated as automatic or silently presumed,
- no mutation of `ilc_core/` or `ilc_consensus/` in this docs-only packet,
- no claim that row `5` or row `7` is runtime-closed,
- no claim that true multi-machine validator proof already exists.

## 3. Window meaning

Window `717-722` is the ADR-0015 family closure lane. Its job is to close the
historically important but still ungoverned family of:

- transfer tax,
- cooling period,
- commons dedication / public-goods routing,
- leasehold / reversion timing.

This window is not a license to constitutionalize economic metaphors because
they are historically resonant. It must explicitly decide for each mechanism
whether the honest outcome is `launch_bound`, `post_launch_bound`, or
`deferred`.

`adr_0015_family_closure_window_active`

There is no pre-window conversation gate and no planned CDL ratification here.
The family must close by explicit written disposition rather than by drift.
`no_pre_window_conversation_required_for_717_722`
`no_cdl_ratification_planned_in_window_717_722`

## 4. Phase table and sequencing

| Order | Phase | Topic | Character |
|---|---:|---|---|
| 1 | 717 | sequence lock | gate / planning |
| 2 | 718 | ADR-0015 family inventory and scoping | research / planning |
| 3 | 719 | node transfer economics and cooling period governance package | governance / spec |
| 4 | 720 | commons dedication and leasehold / reversion calibration | governance / spec |
| 5 | 721 | ADR-0015 disposition and simulation / replay contract | research / handoff |
| 6 | 722 | closure | gate / handoff |

Phase `718` inventories the family without making final verdicts. Phase `719`
handles transfer tax and cooling period. Phase `720` handles commons dedication
and leasehold / reversion. Phase `721` publishes the final family disposition,
the commissioning contract for later evidence, and any explicit CDL opening
recommendation or deferment. Closure phase is Phase `722`.

## 5. Explicit disposition obligation

Every ADR-0015 mechanism must receive an explicit written disposition before the
window can close:

- accepted,
- amended,
- rejected,
- or deferred,

and separately:

- `launch_bound`,
- `post_launch_bound`,
- or `deferred`.

This applies at minimum to:

- transfer tax,
- cooling period,
- commons dedication,
- leasehold / reversion timing.

The family may not remain implicitly relied upon while still labeled proposed.
`explicit_per_mechanism_disposition_required_before_window_close`

The evidence-bearing obligations are:

- a simulation or replay commissioning contract for transfer tax, cooling
  period, and leasehold duration questions,
- a written routing boundary for commons dedication under the existing
  `CDL-047` treasury lane,
- an explicit statement on whether a new CDL opening is recommended or deferred.

## 6. Non-goals

This window does not include:

- any decision-log mutation by default,
- any CDL ratification,
- any automatic opening of a new transfer-economics CDL,
- any runtime mutation in `ilc_core/` or `ilc_consensus/`,
- any claim that row `5` or row `7` is runtime-closed,
- any claim that the M-series local loopback work already constitutes true
  multi-machine validator proof.

There is no ratification of `CDL-017`, no opening of `CDL-062`, and no final
Option B production selection in this window.

## 7. Source inputs

The authoritative source set for the window is:

- `docs/PLANNING_INDEX.md`
- `docs/specs/ilc_window_717_722_guidance_v0.1.md`
- `docs/specs/ilc_window_717_722_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md`
- `docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md`
- `docs/specs/ilc_window_713_716_closure_gate_716_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v4.7.md`
- `docs/phases/STATUS.md`
- `docs/adr/ADR_0015_Node_Transfer_Economics.md`
- `docs/adr/ADR_0017_Post_Issuance_Economic_Transition.md`
- `docs/specs/ilc_economic_architecture_comprehensive_v0.1.md`
- `docs/specs/ilc_cdl_047_treasury_governance_ratification_evidence_418_v0.1.md`
- `docs/specs/ilc_cdl_048_ecu_mandatory_conversion_deadline_ratification_evidence_419_v0.1.md`
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.3.md`

This sequence lock remains active until Phase `722` closes the window.
