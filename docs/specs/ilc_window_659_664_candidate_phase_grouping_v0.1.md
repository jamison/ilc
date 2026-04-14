# ILC Window 659-664: Candidate Phase Grouping

**Author:** Codex
**Date:** 2026-04-14
**Baseline:** Window 655-658 CLOSED (bounded signing/export reproducibility lane). Capsule v3.9 is current. Rows 1-4 are `runtime_closed`; row 5 is `not_started`; row 6 is `partial`; rows 7-9 remain open-state checklist items. The next constitutional target is the row-6 coupling-invariants governance lock.
**Planning note:** This is a candidate grouping, not a locked sequence. Phases 659-664 are the hard minimum lane and there are no conditional tail slots. The window closes row 6 if and only if the governance lock is opened, ratified, and the closure gate passes. Rows 5 and 7-9 are sharpened here but are not closed here.

## 1. Window identity and scope

Window 659-664 is the first post-658 constitutional lane. Its purpose is to do
two things at the same time without confusing them:

1. close Phase 611 checklist row 6 by locking the coupling invariants that keep
   protocol truth and public legitimacy upstream of later settlement backend
   choice; and
2. formally split "`CDL-062` opening admissibility" from final "`Option B`
   selection" so the roadmap stops treating those as the same event.

This window is not a substrate-selection lane. It does not choose the final
public settlement backend. It does not close rows 5 or 7-9. It creates the
constitutional grammar that makes those later lanes cleaner and less ambiguous.

Tail-slot policy statement:
- no conditional tail slots are authorized in this window
- every phase from 659 through 664 is firm
- later-row sharpening is in scope only where it helps future windows without
  overclaiming closure

## 2. Baseline and inheritance

Inherited canon and carry-forward:
- Phase 611 locked the Option-B checklist and blocker matrix
- Phase 612 kept `CDL-062` unopened and unauthorized
- Window 649-654 closed checklist rows 1-4 in runtime form
- Window 655-658 removed bounded signing/export reproducibility debt but did
  not alter the constitutional frontier
- the current machine-legible checklist artifact is
  `docs/specs/ilc_option_b_graduation_checklist_state_654_v0.1.json`
- the practical row-6 evidence base already includes the Phase 652 read-only
  coupling diagnostic and the cryptographic-economic coupling memo

Inherited rule set:
- `Option D` remains active
- `Option B` remains legitimate later posture, but is not selected here
- `CDL-062` remains unopened throughout this window
- legal positioning remains real carry-forward, but is not treated here as a
  formal admissibility gate for opening `CDL-062`

Next fresh CDL number:
- `CDL-065`

## 3. Track inventory

### 3.1 Constitutionally obligated

- row-6 governance lock over admission, namespace, quorum authority,
  settlement legitimacy, and reputation continuity
- formal split between "`CDL-062` may open" and "`Option B` may be selected"
- constitutional vehicle for the row-6 lock (`CDL-065`)
- closure artifact that records row 6 as `closed` using a governance-closure
  label if and only if this lane passes

### 3.2 Deferred governance

- row 5 privacy-preserving public legitimacy mechanism
- row 7 censorship-resistance mechanism closure
- row 8 final independence proof over a chosen substrate/governance stack
- row 9 operational maturity closure
- legal positioning memo and other pre-RC material
- sovereign substrate selection, BFT/L1 engineering, and final `CDL-062` work
- final `Option B` selection

### 3.3 Simulation-conditional

- light adversarial counterexample testing is required in this window
- no simulation-conditional phase slots are opened
- heavier transport, privacy, or substrate simulation remains later-lane work

## 4. CDL-065 coupling-invariants governance lock scope

`CDL-065` is the constitutional vehicle for the row-6 lock.

Practical meaning of the lock:
- "backend" means a later sovereign settlement substrate family, such as a
  custom minimal L1, an external rollup/L2, or another later chain-backed
  settlement substrate that might eventually be opened by `CDL-062`
- "upstream" means the source of canonical legitimacy or authority
- "downstream" means a later backend may record, order, anchor, finalize, or
  settle what the protocol already made legitimate, but it may not create or
  override that legitimacy

The lock must say, in durable language, that later backend choice may not
author or overwrite:
- public admission legitimacy
- canonical namespace and handle authority
- canonical quorum and evaluation authority
- public settlement legitimacy
- public reputation continuity

The lock must also say what later backend choice is allowed to do:
- carry receipt-linked settlement forward
- anchor already legitimate protocol state
- provide later durability, ordering, settlement, or finalization services

Rejected scope inside `CDL-065`:
- selecting the final backend
- deciding Tendermint vs HotStuff vs another BFT variant
- implementing a privacy-preserving mechanism for row 5
- closing rows 7-9

## 5. Pre-opening admissibility and later-row sharpening sidecar

This window also carries a bounded sidecar whose purpose is to make later work
easier without pretending to finish it now.

The sidecar must produce:
- a `CDL-062` opening admissibility matrix that lists what must be true before
  the sovereign-substrate lane may open
- an explicit statement that opening admissibility is not the same as final
  `Option B` selection
- a remaining-row closure-criteria artifact for rows 5, 7, 8, and 9
- a bounded derived gate set for agent-suitability / machine use that keeps the
  later substrate lane from opening into a human-only or dashboard-only vacuum
- a row-9 maturity evidence starter pack that fixes the required evidence
  families now while deferring exact thresholds to Window 665-670

The sidecar must not:
- mark rows 5, 7, 8, or 9 closed
- treat the legal memo as a formal `CDL-062` opening gate
- smuggle in substrate selection criteria that amount to selecting the
  substrate itself

## 6. CDL number assignments

| CDL | Title (candidate) | Decision digest anchor | Opening phase | Ratification phase |
|-----|-------------------|------------------------|---------------|-------------------|
| CDL-065 | Coupling invariants governance lock and `CDL-062` admissibility split | `protocol_truth_and_public_legitimacy_remain_upstream_of_later_backend_choice` | Phase 662 | Phase 663 |

Pre-authorization note:
- `CDL-065` is the only constitutional vehicle in this window
- `CDL-062` is not opened in this window; it is only discussed through an
  admissibility matrix

## 7. Candidate phase table

| Order | Phase | Topic | Character | Sensitivity |
|---|---:|---|---|---|
| 1 | 659 | Sequence lock and constitutional lane freeze | Foundation / Constitutional | **SENSITIVE** |
| 2 | 660 | Coupling surface inventory and invariant matrix | Constitutional | constitutional |
| 3 | 661 | Counterexample sweep and later-row criteria sharpening | Governance review | constitutional |
| 4 | 662 | `CDL-065` opening and `CDL-062` admissibility matrix | Constitutional | **SENSITIVE** |
| 5 | 663 | `CDL-065` ratification and row-6 closure candidate | Constitutional | **SENSITIVE** |
| 6 | 664 | Closure gate, checklist delta, capsule, and handoff | Gate | **SENSITIVE** |

### Conditional note on Phases 659-664

There are no conditional tail slots in this window. All six phases are firm.

### Note on Phase 661 non-ratifying boundary

Phase 661 sharpens rows 5, 7, 8, and 9 by writing closure criteria and
counterexample analysis. It does not claim those rows closed or partially
closed beyond what the checklist already records.

For row 9 specifically, Phase 661 should be semi-prescriptive rather than
purely abstract: it should name the minimum evidence families now and defer the
exact topology, run-count, and pass-threshold work to Window 665-670.

### Note on Phase 663 doc-only constitutional mutation pattern

Phase 663 is a constitutional ratification phase, but it remains doc-only:
- decision-log mutation is authorized
- ratification evidence and governance-lock artifacts are authorized
- `ilc_core/` mutation is not authorized

## 8. Sensitivity classification

### SENSITIVE phases list

- Phase 659: structural sequence lock for the next constitutional lane; an
  incorrect lock could overclaim closure or route `CDL-062` work improperly
- Phase 662: opens `CDL-065` and therefore mutates the constitutional decision
  log
- Phase 663: ratifies `CDL-065` and therefore mutates the constitutional
  decision log
- Phase 664: closure boundary phase; it sets the official row-6 status and
  routes the next constitutional work

### NON-SENSITIVE phases list

- Phase 660: constitutional prelock inventory and matrix work only; no
  decision-log mutation
- Phase 661: governance review and sharpening artifacts only; no decision-log
  mutation

### Conditional phases rule

There are no conditional phases in Window 659-664. Every phase is fixed in
advance. Human GO remains required for every SENSITIVE phase.

### Pre-commit hook block

Use the literal hook syntax for CDL mutation phases only:

```text
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=<phase>
```

Phases requiring the hook:
- Phase 662
- Phase 663

Phases 659 and 664 are SENSITIVE but do not authorize decision-log mutation, so
they require explicit human GO but not the CDL-mutation hook.

## 9. Scope notes for fixed phases

### Phase 659 — sequence lock and lane freeze

Sensitivity: **SENSITIVE**. Explicit human GO required before commit. No
decision-log mutation authorized.

Deliverables:
- `docs/specs/ilc_phase_659_664_sequence_lock_v0.1.md`
- `tests/test_phase_659_window_659_664_sequence_lock.py`

Required content spec:
- row-6 practical target
- `CDL-065` as the lane vehicle
- `CDL-062` admissibility versus `Option B` selection split
- preserved non-goals and later-row discipline

Test structure:
- phase test only before main commit
- no decision-log or `ilc_core/` path changes allowed

Commit subject:
- `docs(g8): phase 659 window 659-664 sequence lock`

### Phase 660 — coupling surface inventory and invariant matrix

Sensitivity: NON-SENSITIVE constitutional prelock. No GO token beyond normal
window authorization.

Deliverables:
- `docs/specs/ilc_coupling_surface_inventory_and_invariant_matrix_660_v0.1.md`
- `docs/specs/ilc_coupling_surface_inventory_and_invariant_matrix_660_v0.1.json`
- `tests/test_phase_660_coupling_surface_inventory_and_invariant_matrix.py`

Required content spec:
- one row per coupling surface
- authority source, allowed downstream action, forbidden backend action,
  lineage requirement, evidence basis
- human-readable examples of allowed and forbidden backend behavior

Test structure:
- phase test asserts doc headings, tokens, JSON shape, and no decision-log
  mutation

Commit subject:
- `docs(g8): phase 660 coupling surface inventory and invariant matrix`

### Phase 661 — counterexample sweep and later-row sharpening

Sensitivity: NON-SENSITIVE constitutional review. No CDL mutation.

Deliverables:
- `docs/specs/ilc_coupling_counterexample_sweep_661_v0.1.md`
- `docs/specs/ilc_option_b_remaining_rows_closure_criteria_661_v0.1.md`
- `tests/test_phase_661_coupling_counterexample_and_row_sharpening.py`

Required content spec:
- adversarial cases showing what the backend may not do
- rows 5, 7, 8, and 9 closure criteria sharpened into future-lane inputs
- no closure claims for rows 5 or 7-9

Test structure:
- phase test asserts later-row sharpening without status inflation

Commit subject:
- `docs(g8): phase 661 counterexample sweep and row sharpening`

### Phase 662 — `CDL-065` opening and admissibility split

Sensitivity: **SENSITIVE**. Explicit human GO and the CDL-mutation hook
required.

Deliverables:
- `docs/specs/ilc_cdl_065_coupling_invariants_governance_lock_opening_662_v0.1.md`
- `docs/specs/ilc_cdl_062_opening_admissibility_matrix_662_v0.1.md`
- `tests/test_phase_662_cdl_065_opening_and_admissibility_matrix.py`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

Required content spec:
- open `CDL-065` only
- define opening-side gates for `CDL-062` without opening `CDL-062`
- record agent-suitability gates as opening-side criteria
- record that the legal memo is not a formal opening gate

Test structure:
- pre-commit split for opening doc, admissibility matrix, test, and decision
  log row mutation

Pre-commit hook:
- `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=662`

Commit subject:
- `docs(g8): phase 662 cdl 065 opening and admissibility split`

### Phase 663 — `CDL-065` ratification and row-6 closure candidate

Sensitivity: **SENSITIVE**. Explicit human GO and the CDL-mutation hook
required.

Deliverables:
- `docs/specs/ilc_coupling_invariants_governance_lock_663_v0.1.md`
- `docs/specs/ilc_cdl_065_coupling_invariants_governance_lock_ratification_evidence_663_v0.1.md`
- `tests/test_phase_663_cdl_065_ratification_and_row6_closure_candidate.py`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

Required content spec:
- ratified governance-lock text for row 6
- evidence basis tying the ratification to Phases 660-662
- explicit statement that rows 5 and 7-9 remain open

Test structure:
- phase test must harden the historical opening state and the new ratified
  state

Pre-commit hook:
- `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=663`

Commit subject:
- `docs(g8): phase 663 cdl 065 ratification and row 6 closure candidate`

### Phase 664 — closure gate, checklist delta, capsule, and handoff

Sensitivity: **SENSITIVE**. Explicit human GO required before commit. No
decision-log mutation authorized.

Deliverables:
- `docs/specs/ilc_window_659_664_handoff_664_v0.1.md`
- `docs/specs/ilc_option_b_graduation_checklist_state_664_v0.1.json`
- `docs/specs/ilc_antigravity_context_capsule_v4.0.md`
- `tools/run_window_659_664_constitutional_closure_gate_phase_664.sh`
- `tests/test_phase_664_window_659_664_closure_and_handoff.py`

Required content spec:
- row 6 becomes `closed` if and only if the window passed and `CDL-065` is
  ratified
- row 6 uses `closed` as a governance-closure label, while rows 1-4 remain
  `runtime_closed`
- rows 5 and 7-9 remain open
- the next lanes are sharpened, not pre-closed
- routing after closure remains honest

Test structure:
- closure gate must run phases 659-664 test surfaces and fail closed

Commit subject:
- `docs(g8): phase 664 window 659-664 closure and handoff`

## 10. Key dependencies and open questions

### Must-resolve at entry

- confirm that `CDL-065` is the next fresh constitutional number
- confirm current capsule baseline is v3.9 at entry
- confirm row-6 closure target is governance lock only, not substrate selection

### Sequencing constraints

- Phase 660 depends on Phase 659 sequence lock
- Phase 661 depends on the surface map from Phase 660
- Phase 662 depends on Phases 660 and 661 because the opening doc should not be
  written in a vacuum
- Phase 663 depends on `CDL-065` opening in Phase 662
- Phase 664 depends on Phases 659-663 and the closure gate

### Open questions

- which exact agent-suitability gates should be named in the admissibility
  matrix beyond the bounded derived set required here
- which exact numeric thresholds Window 665-670 should impose on the row-9
  evidence starter pack

### Permanently deferred

- `CDL-062` opening
- sovereign substrate selection
- BFT/L1 engineering choice
- row 5 closure
- row 7 closure
- row 8 final proof over a chosen substrate
- row 9 closure

## 11. Known patterns and technical constraints

### Novel patterns introduced this window

- first constitutional lane whose primary objective is to separate
  `CDL-062` opening admissibility from final `Option B` selection
- first row-closure lane that uses runtime evidence but does not authorize any
  runtime mutation
- first lane that deliberately sharpens rows 5 and 7-9 while refusing to claim
  they are closed

### Historical prelock hardening

If Phase 663 ratifies `CDL-065`, its test must also assert that the opening
state remained `open` at the historical opening commit reference. Do not ratify
without hardening the historical-opening assertion.

### Phantom edit guard

No `ilc_core/` runtime mutation is expected anywhere in Window 659-664. If an
`ilc_core/` diff appears, treat it as a phantom edit or scope breach until
proven otherwise.

Detection command:
- `git diff --name-only -- ilc_core/`

Expected fix rule:
- remove the stray runtime mutation from the phase or stop and re-scope

### Pre-commit hook `ilc_core/` clean-state guard

Because this is a doc-only constitutional lane, every phase should verify that
`ilc_core/` remains clean before commit.

### Closure gate selftest guard chain

Phase 664 must read every prior phase test file directly and wire the closure
gate from those specific files. Do not reason by analogy from earlier window
gate scripts.

## 12. Non-goals and explicitly deferred items

- opening `CDL-062`
- selecting `Option B`
- choosing a sovereign settlement substrate
- choosing a BFT or L1 implementation stack
- implementing the row-5 privacy mechanism
- closing rows 7, 8, or 9
- widening wallet authority or altering claimability
- mutating `ilc_core/` in this window

## 13. Key canonical anchors for prompt drafting

- `docs/specs/ilc_antigravity_context_capsule_v3.9.md` (PRIMARY)
- `docs/specs/ilc_window_655_658_handoff_658_v0.1.md`
- `docs/specs/ilc_window_655_658_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/phases/STATUS.md`
- `docs/specs/ilc_settlement_substrate_governance_vehicle_selection_611_v0.1.md`
- `docs/specs/ilc_settlement_substrate_closure_and_mvp_gated_replan_612_v0.1.md`
- `docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md`
- `docs/specs/ilc_option_b_graduation_checklist_state_654_v0.1.json`
- `docs/specs/ilc_ecu_ilc_lifecycle_runtime_652_v0.1.md`
- `docs/research/ilc_cryptographic_economic_coupling_memo_v0.1.md`
- `docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md`
- `docs/research/ilc_option_b_historical_recovery_dossier_2026_04_14_v0.1.md`
- `docs/specs/ilc_agent_utility_logic_gates_v0.1.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.2.md`

For closure gate (Phase 664): all Phase 659-663 test files and artifacts.

Optional MemPalace retrieval appendix:
- default active working-set descriptor:
  `docs/tools/mempalace/ilc_mempalace_active_working_set_v0.1.json`
- logic-gate profile:
  `docs/tools/mempalace/ilc_mempalace_logic_gate_profile_v0.1.md`
- retrieval use in this planning pass should remain advisory only and never
  override direct repo reads

## 14. Rationale for single-window scope

1. Row 6 is the next constitutional blocker and is tight enough to support a
   focused single-window lane.
2. The `CDL-062 admissibility` versus `Option B selection` split is the
   smallest move that unties the current sequencing knot.
3. Rows 5 and 7-9 benefit from sharpening now, but closing them here would be
   dishonest and would contaminate later windows.
4. A doc-only constitutional lane minimizes risk while still producing durable
   carry-forward artifacts.
