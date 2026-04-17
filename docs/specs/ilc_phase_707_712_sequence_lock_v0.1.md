# ILC Phase 707-712 Sequence Lock v0.1

Status: sequence lock
Date: 2026-04-17
Phase: 707
Owner lane: G8 governance minimization and validator-agent identity

`window_707_712_sequence_lock_active`
`cdl_066_and_cdl_067_ratification_routed_in_window_707_712`
`cdl_017_prelock_only_not_ratified_in_window_707_712`
`q1_q6_answers_required_before_phase_710_execution`
`cdl_062_option_b_selection_not_in_scope_707_712`
`track_b_status_must_be_verified_from_status_tail`

## 1. Baseline

Window `701-706` is closed. The inherited baseline at Window `707-712` entry is:

- capsule v4.5 is published
- row `5 = spec_closed_runtime_pending`
- row `7 = spec_closed_runtime_pending`
- row `8 = closed / reconfirmed`
- `CDL-066`, `CDL-017`, and `CDL-067` remain open and unratified
- Track B has advanced beyond the old `M-009` gate language and must be read
  from `docs/phases/STATUS.md` tail, not from memory

This window is the governance-minimization and validator-agent identity lane. It
is a constitutional preparation and narrow ratification window, not a final
Option B selection window.

## 2. Inherited gates and constraints

Inherited from the Window `701-706` closure gate, the carry-forward program,
and the approved `707-712` packet:

- only `CDL-066` and `CDL-067` are in-window ratification targets
- `CDL-017` remains prelock-only and must not be ratified in this window
- `CDL-062` remains unauthorized and may not be opened here
- final Option B production configuration is not selected here
- rows `5` and `7` remain runtime-pending and are not closed by rhetoric
- validation pools remain outside `CDL-017` core and outside this window
- docs-only phases in this window may not mutate `ilc_core/` or
  `ilc_consensus/`
- any statement about Track B current state must be verified from `STATUS.md`
  tail at execution time

## 3. Window meaning

Window `707-712` exists to narrow constitutional ambiguity before the later
Mysticeti convergence window.

It is authorized to:

1. lock the sequence and scope of the governance-minimization lane,
2. publish a governance-minimization inventory and ADR-0019 disposition,
3. ratify `CDL-066` narrowly as the sender-authorization constitutional lane,
4. publish the graph-native algorithm-governance contract and a bounded
   local-influence example,
5. ratify `CDL-067` narrowly as the settlement-state governance vehicle,
6. record validator-agent design evidence and the resolved Q1-Q6 answer set for
   `CDL-017` prelock,
7. commission validator simulations and publish the `CDL-039` topology
   authorization scope note,
8. close the window with coherence, capsule v4.6, and an explicit carry-forward
   gate.

This window does not authorize final validator-set activation, final topology
seed law for production, or ratification of the broader validation-pool
economics lane.

## 4. Phase table and sequencing

| Order | Phase | Topic | Deliverable focus |
|---|---:|---|---|
| 1 | 707 | sequence lock | lock the window scope, ratification boundary, and prerequisites |
| 2 | 708 | governance minimization + `CDL-066` | taxonomy, ADR-0019 disposition, narrow sender-auth ratification |
| 3 | 709 | algorithm governance + `CDL-067` | contract, local-influence example, narrow settlement-governance ratification |
| 4 | 710 | validator-agent design evidence | Q1-Q6 record and `CDL-017` prelock mapping |
| 5 | 711 | simulation commissioning + `CDL-039` | `SIM-VALIDATOR-01`, `SIM-TOPOLOGY-01`, topology-shuffling authorization path |
| 6 | 712 | closure | coherence report, capsule v4.6, and closure gate |

Sequencing rule:

- only Phases `708-709` may mutate the constitutional decision log
- Phase `710` may begin only after Q1-Q6 answers exist from conversation
- Phase `711` may commission evidence but must not overclaim final production
  topology law if the evidence is not yet complete
- Phase `712` may summarize only what Phases `708-711` actually establish

## 5. Phase-specific prerequisites

Phase `708` prerequisite:
- Phase `707` sequence lock is active

Phase `709` prerequisite:
- Phase `708` is complete and `CDL-066` status is no longer ambiguous

Phase `710` prerequisite:
- Q1-Q6 answers must already exist from conversation with the local reviewer
- that prerequisite is now satisfied by
  `docs/research/ilc_validator_agent_q1_q6_prewindow_resolution_v0.1.md`
- if the answer record were absent, Phase `710` would be blocked rather than
  improvised

Phase `711` prerequisite:
- Phase `710` has recorded the validator-agent design evidence and explicit
  Q1-Q6 answers

Phase `712` prerequisite:
- ratification results from Phases `708-709` and the prelock/simulation outputs
  from Phases `710-711` are in place
- Track B status must be rechecked from `STATUS.md` tail before the capsule is
  written

## 6. Non-goals

- no ratification of `CDL-017`
- no opening of `CDL-062`
- no final Option B production selection
- no claim that row `5` or row `7` runtime work is complete
- no ratification of validation pools as part of `CDL-017`
- no mutation of `ilc_core/` or `ilc_consensus/` in the docs-only phases of
  this window
- no silent conversion of governance philosophy into executable runtime law

## 7. Source inputs

- `docs/specs/ilc_window_701_706_closure_gate_706_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v4.5.md`
- `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md`
- `docs/specs/ilc_window_707_712_guidance_v0.1.md`
- `docs/specs/ilc_window_707_712_candidate_phase_grouping_v0.1.md`
- `docs/research/ilc_validator_agent_q1_q6_prewindow_resolution_v0.1.md`
- `docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md`
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.3.md`
- `docs/phases/STATUS.md`
