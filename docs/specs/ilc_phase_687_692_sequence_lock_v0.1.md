# ILC Phase 687-692 Sequence Lock v0.1

Status: sequence lock
Date: 2026-04-16
Phase: 687
Owner lane: G8 sovereign-substrate research

`phase_687_692_sequence_lock_active`
`cdl_062_opens_as_bounded_research_lane_only`
`settlement_state_enumeration_is_687_prerequisite_for_690_691`

---

## 1. Baseline

Window 677-682 is closed. Capsule v4.3 is current.

Inherited row state:
- rows 1-4: `runtime_closed`
- row 5: `partial`
- rows 6-9: `closed`
- `CDL-062`: unopened
- Option D: active

This window opens `CDL-062` as a bounded sovereign-substrate research lane.
It does not select the final Option-B substrate winner.

---

## 2. Inherited constitutional gates carried forward

All of the following remain live constraints on this window and every phase
within it.

`row_6_upstream_downstream_boundary_active_in_this_window`
- CDL-065: the backend may carry already-legitimate protocol state; it may not
  author legitimacy. This is not a preference. It is locked constitutional law.

`row_7_censorship_resistance_and_exitability_gates_active_in_this_window`
- Rows 7-8 selection criteria lock (Phase 675): every candidate substrate must
  satisfy strong exitability and replayability proof obligations and must not
  rely on a single operator, dashboard, or provider shell as the ordinary
  public legitimacy surface.

`row_8_external_constitutional_center_exclusion_active_in_this_window`
- Phase 673 exclusion matrix is binding. Any outside system with de facto or
  formal legitimacy veto over ILC protocol state is presumptively inadmissible.
  Popular public L1s with governance bodies are the inadmissible bucket, not
  the comparison set.

`row_5_partial_compatibility_filter_active_in_this_window`
- Row 5 is partial, not closed. Candidate substrate families must not foreclose
  the near-term tractable mechanism families from Phase 680 (timing smoothing,
  relay/indirection, commitment/selective-disclosure). Substrate choices that
  make all three families technically implausible fail this filter.

`cdl_062_opening_admissibility_gates_inherited_from_662`
- Phase 662 opening admissibility gates are all satisfied as of this window
  opening (row 6 closed, rows 7-8 locked, row 9 material evidence present,
  row 5 narrowed).
- The legal memo is not a formal opening gate.
- The explicit human authorization boundary from Phase 662 remains real. This
  sequence lock is the exercise of that authorization.

`683_686_does_not_block_this_window`
- The legal positioning lane (683-686) is carry-forward, not a blocking
  checkpoint for this lane.

---

## 3. What CDL-062 means in this window

`cdl_062_opening_means_bounded_research_lane_not_final_selection`

Opening CDL-062 here means:
- the project is authorized to begin disciplined sovereign-substrate research
- the project is authorized to produce a narrowed candidate set
- the project is authorized to define benchmark methodology against real ILC
  settlement-state semantics

Opening CDL-062 here does not mean:
- final Option-B substrate is selected
- any candidate is authorized for production deployment
- row 5 is further closed by implication
- rows 6-9 are reopened, relaxed, or reinterpreted

---

## 4. Settlement-state enumeration requirement

`settlement_state_enumeration_required_in_phase_687`
`phase_690_and_691_are_preliminary_only_if_enumeration_slips`

The Phase 687 deliverable
`ilc_settlement_state_enumeration_and_submission_model_687_v0.1.md`
must be produced in this phase.

If it slips to Phase 688, that phase must absorb it before any family
comparison claims to be testing real ILC settlement behavior.

If it is not complete by the end of Phase 688, Phases 690 and 691 are
constrained to preliminary scoping and methodology notes only — they may not
publish authoritative benchmark or survivor analysis against an undefined
settlement target.

---

## 5. BAL-profile weight disclaimer

`bal_profile_weights_are_unratified_planning_inputs_in_this_window`

The BAL-profile ECU kernel weights (reuse 0.35, contradiction-resilience 0.25,
validation-integrity 0.20, path-uplift 0.20) are used as planning inputs in
this window's benchmark and comparison work.

They are not ratified constitutional law. They are planning assumptions pending
calibration work in Window 701-706.

Every benchmark or comparison artifact in this window that relies on ECU kernel
assumptions must state this explicitly. Results must not be presented as if the
underlying economic model is settled canon.

---

## 6. Bounded-spike scope limit

`spike_work_in_this_window_is_bounded`

Any implementation-shape or harness work in this window is bounded as follows:
- no production key generation
- no live validator deployment
- no runtime that persists state beyond local test environments
- no claim of protocol-production readiness for any candidate family

---

## 7. Phase table and sequencing

| Phase | Topic | Character | Gate |
|---:|---|---|---|
| 687 | Sequence lock + CDL-062 opening stub + settlement-state enumeration | Gate / Planning | **SENSITIVE** |
| 688 | Sovereign substrate-family prefilter and exclusion packet | Research / Criteria | **SENSITIVE** |
| 689 | Sovereign BFT / finality-family research packet | Research / Design | planning |
| 690 | Benchmark harnesses and evaluation protocol | Bench / Methodology | planning |
| 691 | Admissible-family comparison analysis | Analysis / Adversarial | **SENSITIVE** |
| 692 | Narrowed survivor set, remaining gaps, and handoff | Gate / Handoff | **SENSITIVE** |

Phases execute in order. Phase 688 may not begin family comparison work until
Phase 687 settlement-state enumeration is published or absorbed. Phase 690
harnesses must be anchored to the enumerated settlement-state model.

---

## 8. Non-goals for the full window

`no_final_option_b_selection_in_this_window`
`no_row_5_closure_by_implication`
`no_row_6_7_8_relaxation`
`no_production_deployment_authorization`
`no_chain_choice_by_ecosystem_momentum`

This window does not:
- select the final Option-B substrate winner
- close row 5 by implication or convenience
- relax or reopen rows 6, 7, or 8
- authorize production validator deployment
- authorize public launch claims
- choose a substrate by ecosystem popularity, tooling comfort, or brand
  familiarity

---

## 9. Source inputs this sequence lock is bound by

Required source inputs inherited by this lock:
- `docs/specs/ilc_window_687_692_candidate_phase_grouping_v0.1.md`
- `docs/research/ilc_window_687_692_cdl_062_sovereign_substrate_conversation_frame_2026_04_15_v0.1.md`
- `docs/specs/ilc_cdl_062_opening_admissibility_matrix_662_v0.1.md`
- `docs/specs/ilc_coupling_invariants_governance_lock_663_v0.1.md`
- `docs/specs/ilc_rows_7_8_selection_criteria_lock_675_v0.1.md`
- `docs/specs/ilc_row_5_prework_narrowing_decision_682_v0.1.md`
- `docs/specs/ilc_row_5_mechanism_family_matrix_680_v0.1.md`
- `docs/specs/ilc_public_ledger_substrate_options_and_rejection_matrix_610_v0.1.md`
- `docs/research/ilc_foundational_principles_and_window_687_692_context_2026_04_15_v0.1.md`
- `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md`
