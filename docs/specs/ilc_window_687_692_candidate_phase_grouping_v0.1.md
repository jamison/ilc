# ILC Window 687-692: Candidate Phase Grouping

**Author:** Codex
**Date:** 2026-04-15
**Baseline:** Window 677-682 CLOSED. Capsule v4.3 is current. Rows 1-4 remain `runtime_closed`; row 5 remains `partial`; rows 6-9 remain `closed`; `CDL-062` remains unopened; Option D remains active.
**Planning note:** This is a candidate grouping, not a locked sequence. It is meant to restate the `687-692` lane in project-native terms after context recovery from the March 2026 Werner/economic-architecture conversations, the December 2025 off-chain/on-chain architecture discussions, the row-5 narrowing packet, and the row-6/7/8/9 closure work.

## 1. Window identity and corrected scope

Window 687-692 is not a generic blockchain-shopping lane.

It is the first bounded research lane for the question:

- what kind of sovereign finality substrate could make already-legitimate ILC
  protocol state durable, replayable, and publicly auditable without becoming
  the constitutional center itself?

That framing matters because the inherited project spine is not:

- “find a chain for the token,” or
- “move ILC onto an ecosystem with good tooling.”

The inherited project spine is:

- the epistemic graph is the real machine;
- ECU is productive protocol credit created by verified epistemic work;
- ILC is the hard settlement asset;
- the settlement substrate is downstream durability/finality infrastructure for
  protocol legitimacy that already exists upstream in the graph.

This window therefore exists to:

1. open `CDL-062` only as a bounded sovereign-substrate research lane;
2. dispose quickly of families that fail the closed constitutional gates from
   rows 6-8 or materially conflict with the row-5 partial packet;
3. focus serious effort on sovereign BFT/finality families and minimal-L1
   implementation shapes;
4. define honest benchmark and comparison discipline centered on admissibility,
   finality, censorship resistance, exitability, auditability, and operability;
   and
5. narrow the candidate field without pretending that the final winner must be
   selected in the same window.

This window is not:

- final Option-B selection,
- final row-5 closure,
- production implementation authorization,
- or a reopening of rows 6-9.

## 2. Baseline and inheritance

Inherited constitutional and architectural anchors:
- `docs/specs/ilc_cdl_062_opening_admissibility_matrix_662_v0.1.md`
- `docs/specs/ilc_coupling_invariants_governance_lock_663_v0.1.md`
- `docs/specs/ilc_rows_7_8_selection_criteria_lock_675_v0.1.md`
- `docs/specs/ilc_row_5_prework_narrowing_decision_682_v0.1.md`
- `docs/specs/ilc_public_ledger_substrate_options_and_rejection_matrix_610_v0.1.md`
- `docs/specs/ilc_economic_architecture_comprehensive_v0.1.md`
- `docs/whitepaper/ilc_whitepaper_working_draft_v6_0.md`

Inherited project principles that matter directly here:
- protocol legitimacy is upstream; later settlement backends may carry that
  legitimacy downstream, but may not author it;
- row 6 already locks the upstream/downstream boundary;
- row 7 already locks censorship resistance and exitability as later-substrate
  gates;
- row 8 already locks independence from external constitutional centers;
- row 5 is still live as a compatibility filter because privacy-preserving
  public legitimacy is only narrowed, not finally closed;
- Option D remains the honest near-term architecture until a later substrate is
  chosen and implemented.

Inherited practical rules:
- `CDL-062` remains unopened;
- explicit human authorization from Phase 662 remains real;
- 683-686 is not a blocker or checkpoint for this window;
- rows 6-9 may not be silently softened or reopened here.

## 3. Research-boundary clarification

The opening boundary should be read in the narrowest honest way:

- planning for this lane may proceed now;
- no 683-686 completion event is required before sequence lock or opening-side
  work in this lane;
- the legal memo remains carry-forward, not a formal opening gate;
- the explicit human authorization boundary from Phase 662 still exists.

Therefore this candidate grouping does not itself claim that `CDL-062` is
already open. It only defines what the first honest opening lane should contain.

## 4. Operationally obligated versus deferred

### 4.1 Obligated in this window

- a bounded `CDL-062` opening stub or opening-side research authorization
- a sovereign substrate-family prefilter
- a BFT/finality research packet
- an implementation-shape research packet for a minimal sovereign L1 line
- benchmark harness definitions and bounded comparison methodology
- analysis of finality, censorship, exitability, replayability, public
  auditability, operability, and validator-cost structure
- a narrowed candidate set or explicit ranked survivor set for the next lane

### 4.2 Explicitly deferred

- final Option-B winner selection
- final row-5 closure
- production validator deployment
- public launch claims
- wallet or payment-lane widening
- chain choice by ecosystem popularity, tooling comfort, or branding affinity

## 5. Governing lemma

The governing lemma for 687-692 should be:

- the substrate is not the protocol;
- the substrate exists to finalize and carry already-legitimate protocol state;
- therefore candidate families must be judged first on constitutional
  admissibility and only then on engineering attractiveness.

This requires the window to keep separate:
- constitutional admissibility,
- finality semantics,
- censorship resistance and exitability,
- public auditability and bounded human inspectability,
- participant operability,
- implementation tractability,
- and only then performance or operational cost.

## 6. Candidate phase table

| Order | Phase | Topic | Character | Sensitivity |
|---|---:|---|---|---|
| 1 | 687 | Sequence lock and bounded `CDL-062` opening stub | Gate / Planning | **SENSITIVE** |
| 2 | 688 | Sovereign substrate-family prefilter and exclusion packet | Research / Criteria | **SENSITIVE** |
| 3 | 689 | Sovereign BFT / finality-family research packet | Research / Design | planning |
| 4 | 690 | Benchmark harnesses and evaluation protocol | Bench / Methodology | planning |
| 5 | 691 | Admissible-family comparison: finality, censorship, exitability, auditability, operability | Analysis / Adversarial review | **SENSITIVE** |
| 6 | 692 | Narrowed survivor set, remaining gaps, and handoff | Gate / Handoff | **SENSITIVE** |

## 7. Scope notes for candidate phases

### Phase 687 — sequence lock and bounded `CDL-062` opening stub

Deliverables:
- `docs/specs/ilc_phase_687_692_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_062_opening_stub_687_v0.1.md`
- `docs/specs/ilc_settlement_state_enumeration_and_submission_model_687_v0.1.md`

Required content:
- explicitly inherit the 662 admissibility matrix and the row-6/7/8/5 carry-
  forward constraints
- define `CDL-062` opening as bounded research-lane authorization, not final
  substrate choice
- enumerate what counts as settlement-layer epoch state for this lane, so later
  benchmark work is not testing against an undefined target
- state that 683-686 does not block this lane
- preserve the explicit human authorization boundary from Phase 662
- state whether any benchmark or comparison work in this window uses BAL-profile
  ECU kernel weights as planning inputs, and if so label them explicitly as
  unratified planning assumptions pending later calibration work
- state explicitly that if the settlement-state enumeration is not published in
  Phase 687, Phase 690 and Phase 691 may publish only scoping or preliminary
  methodology notes rather than authoritative benchmark or survivor analysis
- lock non-goals:
  - no final winner
  - no row-5 closure by implication
  - no row-6/7/8 relaxation

### Phase 688 — sovereign substrate-family prefilter and exclusion packet

Deliverables:
- `docs/specs/ilc_sovereign_substrate_family_prefilter_688_v0.1.md`

Required content:
- candidate family inventory framed around sovereign finality architectures
- explicit mapping against row 6, row 7, row 8, and row 5 compatibility
- classification of families as:
  - primary sovereign candidates
  - control or exclusion surfaces
  - presumptively inadmissible families
- explicit rejection reasons where outside constitutional centers, weak
  exitability, poor privacy compatibility, or dashboard/provider choke points
  dominate

Important note:
- external-chain families are not the main line here
- they may appear only as exclusion/control surfaces or, at most, as highly
  conditional edge cases that must clear the closed constitutional gates
- if the settlement-state enumeration slipped from Phase 687, Phase 688 must
  absorb that enumeration work before family comparison can claim to be testing
  real ILC settlement behavior

### Phase 689 — sovereign BFT / finality-family research packet

Deliverables:
- `docs/specs/ilc_sovereign_bft_and_finality_research_packet_689_v0.1.md`

Required content:
- comparison among admissible sovereign BFT/finality families
- deterministic-finality and fork-resolution semantics
- validator-client and network-shape assumptions
- implementation-stack tradeoffs
- complexity, auditability, and participant-operability notes
- explicit separation between constitutional questions, engineering questions,
  and benchmark questions

### Phase 690 — benchmark harnesses and evaluation protocol

Deliverables:
- `docs/specs/ilc_sovereign_substrate_benchmark_harnesses_690_v0.1.md`
- optional harness config/schema files if they clarify the lane

Required content:
- bounded workload definitions tied to the enumerated ILC settlement-state model
  from Phase 687
- finality measurement methodology
- censorship, failure, recovery, and replayability scenario catalog
- public-auditability and bounded-human-inspectability checks
- validator-operability and participant-access assumptions
- operational-cost measurement methodology
- explicit declaration of which economic/kernel assumptions are ratified versus
  planning-only inputs
- explicit statement that bounded harnesses are not public-production proof

### Phase 691 — admissible-family comparison analysis

Deliverables:
- `docs/specs/ilc_sovereign_substrate_comparison_analysis_691_v0.1.md`

Required content:
- finality semantics and rollback-risk surfaces
- censorship and veto surfaces
- exitability and replayability surfaces
- public-auditability surfaces
- validator-operability and implementation-burden surfaces
- operational-cost structure
- explicit statement of where a family is constitutionally strong but difficult,
  versus attractive-looking but constitutionally weak

### Phase 692 — narrowed survivor set and handoff

Deliverables:
- `docs/specs/ilc_cdl_062_research_lane_handoff_692_v0.1.md`
- updated capsule
- optional survivor-set artifact if separated

Required content:
- what `CDL-062` opening accomplished in this window
- narrowed candidate set or ranked survivor set
- exact remaining gaps before any final substrate choice
- exact carry-forward into the next implementation or deeper-selection lane
- explicit statement that final Option-B selection remains later unless the
  evidence truly compels a stronger claim

## 8. Main conversation questions for this window

The phase work is downstream of these human decisions:

1. What should opening `CDL-062` mean here:
   start disciplined research, narrow to a survivor set, or pick a winner now?
2. Which families belong in the actual live matrix:
   only sovereign families, or sovereign families plus exclusion/control
   surfaces?
3. How hard should the sovereignty requirement be in practical terms?
4. What evaluation hierarchy should govern disagreements:
   admissibility, finality, censorship resistance, exitability, auditability,
   operability, implementation tractability, performance, cost?
5. What must the first benchmark wave prove to count as meaningful?
6. How should the row-5 partial packet constrain candidate families now?
7. How should the explicit human authorization boundary be exercised?
8. What exactly should Phase 692 authorize and what must remain deferred?

## 9. Current recommendation

My current recommendation for sequence lock is:
- retain the explicit human authorization boundary from Phase 662
- treat `CDL-062` opening as bounded research-lane authorization, not final
  substrate selection
- focus the live candidate lane on sovereign BFT/finality families and minimal
  L1 implementation shapes
- treat external or delegated-security families primarily as exclusion/control
  surfaces, not as equal default candidates
- force every candidate through row-6, row-7, row-8, and row-5 filters before
  performance or operational-cost arguments matter
- require Phase 690 and 691 to test finality, censorship, exitability,
  replayability, auditability, and operability rather than collapsing the lane
  into throughput theater
- aim for a narrowed survivor set by Phase 692, not a final winner

## 10. What this candidate grouping does not claim

This artifact does not claim:
- `CDL-062` is already open
- the final sovereign substrate winner is already known
- row 5 can be ignored now that it is `partial`
- external-chain convenience is sufficient to outweigh constitutional locks
- performance leadership alone is enough to justify a substrate choice
