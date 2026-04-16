# ILC CDL-062 Research Lane Handoff 692 v0.1

Status: gate artifact — window closure and handoff
Date: 2026-04-16
Phase: 692
Owner lane: G8 sovereign-substrate research

`window_687_692_cdl_062_research_lane_closed`
`narrowed_survivor_set_produced`
`final_option_b_selection_remains_later`
`window_687_692_handoff_692_closed`

---

## 1. What CDL-062 opening accomplished in this window

Window 687-692 opened CDL-062 as a bounded sovereign-substrate research lane
and executed the following:

| Phase | Deliverable | Status |
|---|---|---|
| 687 | Sequence lock | Complete |
| 687 | CDL-062 opening stub | Complete |
| 687 | Settlement-state enumeration and submission model | Complete |
| 688 | Sovereign substrate-family prefilter and exclusion packet | Complete |
| 689 | Sovereign BFT / finality-family research packet | Complete |
| 690 | Benchmark harnesses and evaluation protocol | Complete |
| 691 | Admissible-family comparison analysis | Complete |
| 692 | This handoff artifact | Complete |

The window closed the following questions that were previously open:

- **What exactly does ILC need a settlement substrate to do?** Now answered
  precisely: the Phase 687 settlement-state enumeration defines the epoch
  settlement record, on-chain vs. off-chain boundary, submission model, and
  row-5 compatibility constraints.

- **Which substrate families are constitutionally admissible?** Now answered:
  external public L1s, external L2 rollups, shared sequencers, appchains with
  external security delegation — all excluded on row-6 and/or row-8 grounds.
  The primary live candidate is the custom minimal sovereign L1 family.

- **Which BFT protocol variants within that family are the serious candidates?**
  Now answered: CometBFT (standalone) and HotStuff/Jolteon are Tier 1 survivors.
  Narwhal-Bullshark is Tier 2 (conditional, pending DAG censorship analysis).
  Avalanche-native is excluded on row-7 grounds.

---

## 2. Narrowed survivor set

### Tier 1 — Primary implementation investigation targets

**CometBFT (standalone, no ICS dependency)**
- Deterministic finality: confirmed
- Row-7 censorship resistance: conditional pass — requires ILC validator
  governance to prevent >1/3 concentration
- Row-7 exitability: strong — full state reconstructible from public chain data
- Row-8 independence: pass — no external constitutional center
- Row-5 compatibility: pass — no structural incompatibility with Phase 680
  near-term mechanism families
- Bounded public auditability: strong — standard RPC/JSON interface
- Participant operability: strong — commodity hardware, mature tooling
- Implementation tractability: strongest among candidates — MIT licensed,
  well-audited ABCI boundary, extractable from Cosmos SDK without ICS

**HotStuff / Jolteon**
- Deterministic finality: confirmed
- Row-7 censorship resistance: conditional pass — same validator-governance
  dependency as CometBFT; threshold signature withholding is a secondary
  censorship surface that must be analyzed
- Row-7 exitability: strong
- Row-8 independence: pass
- Row-5 compatibility: pass
- Bounded public auditability: moderate — BLS threshold signature verification
  requires more sophisticated tooling than CometBFT's individual signatures
- Participant operability: moderate — threshold signature infrastructure
  adds operational complexity
- Implementation tractability: moderate — smaller audit surface than CometBFT;
  stronger scaling trajectory for later validator set growth

### Tier 2 — Conditional carry-forward for later investigation

**Narwhal-Bullshark**
- Deterministic finality: achievable but architecturally more complex
- Row-7 censorship: CONDITIONAL — DAG withholding attack surface not yet
  formally bounded; cannot claim row-7 compliance until this is resolved
- All other dimensions: comparable to Tier 1
- Status: carry forward as a deeper-investigation target for a post-selection
  implementation lane after DAG censorship analysis is complete

### Excluded families (confirmed in this window)

| Family | Exclusion ground | Phase confirmed |
|---|---|---|
| External public L1 (ETH, SOL, AVAX, ATOM) | Row-6 + Row-8 | 688 |
| External L2 rollups | Row-6 + Row-8 | 688 |
| Shared sequencer / managed settlement | Row-6 + Row-7 + Row-8 | 688 |
| Appchain with external security (ICS, DOT subnet) | Row-8 (standard config) | 688 |
| Internal-ledger-final | Phase 610 rejection | 688 |
| Avalanche-native probabilistic | Row-7 (probabilistic finality) | 691 |

---

## 3. Remaining gaps before final substrate choice

The following gaps must be resolved in a later lane before any final Option-B
substrate selection is authorized:

### Gap 1: Validator governance CDL

The most critical near-term gap. Both Tier 1 families require ILC's CDL
process to govern validator admission, ejection, and concentration limits to
prevent >1/3 validator-set capture. CDL-017 (Bootstrap transition criteria and
Genesis sunset triggers) is the relevant existing vehicle. It must open before
any lane that authorizes first non-Genesis validator deployment.

`cdl_017_must_open_before_first_validator_deployment_authorization`

### Gap 2: Settlement-state formal CDL

The Phase 687 settlement-state enumeration is an authoritative spec artifact
but not itself a ratified CDL. The on-chain/off-chain boundary, epoch record
format, and submission model need formal constitutional status before any
implementation lane commits to implementing them.

`settlement_state_enumeration_needs_cdl_vehicle_in_later_lane`

### Gap 3: BAL-weight calibration (Window 701-706)

Any benchmark results in this window that used BAL profile weights (unratified
planning inputs) for ECU kernel sizing must be re-evaluated after Window
701-706 calibration. The economic model assumptions underlying the workload
sizing in Phase 690 are planning-level only.

`bal_calibration_required_before_benchmark_results_are_authoritative`

### Gap 4: Row-5 mechanism proof over a concrete substrate

Row 5 remains partial. The Phase 682 remaining gap is explicit: choose or
narrow further against a concrete later settlement architecture, then prove
that a specific mechanism family satisfies the row-5 observability floor in
real implementation terms. That proof is now one step closer — the substrate
candidates are narrowed — but the mechanism proof itself is not done.

`row_5_mechanism_proof_still_required_over_concrete_substrate`

### Gap 5: Narwhal-Bullshark DAG censorship formal analysis

Before Narwhal-Bullshark can be elevated to Tier 1 in any later lane, the
DAG withholding attack surface must be formally bounded against the row-7
practical-exclusion standard.

`narwhal_bullshark_dag_censorship_analysis_required_for_tier_1_elevation`

### Gap 6: HotStuff threshold signature threshold-withholding analysis

The secondary censorship surface in HotStuff/Jolteon (threshold signature
share withholding) must be analyzed before this family's row-7 compliance
claim can be fully confirmed.

`hotstuff_threshold_withholding_analysis_required_for_row_7_closure`

---

## 4. 701+ carry-forward program items that are prerequisites for the next implementation lane

The following items from the 701+ carry-forward program are direct
prerequisites or active dependencies for the next sovereign implementation
lane — not only for final Option-B selection:

| Item | Window routed | Why it matters for the next lane |
|---|---|---|
| BAL-weight calibration | 701-706 | Benchmark results in 690/691 are unratified until calibration completes |
| Settlement-state formal CDL | 701-706 or later | Implementation lane must build to ratified spec, not planning doc |
| Governance-minimization / CDL-017 | 707-712 (early-start) | Validator governance must be locked before first validator deployment |
| ADR-0019 acceptance and algorithm governance | 707-712 | Not a blocker for implementation start but should precede first governance parameter changes |

`701_plus_items_with_implementation_lane_dependencies_named`

---

## 5. Carry-forward into the next implementation or deeper-selection lane

The next lane after this handoff should:

1. Start with CometBFT (standalone) as the primary implementation
   investigation target
2. Run bounded spike work: ILC ABCI application layer prototype, scoped to the
   Phase 687 settlement-state submission model
3. Define the validator governance CDL (CDL-017 / Bootstrap transition
   criteria) as an early-start deliverable, not a later-lane afterthought
4. Produce a formal row-5 mechanism proof candidate over the CometBFT substrate
   model — the first concrete substrate-specific privacy mechanism test
5. Evaluate HotStuff/Jolteon as the scaling-path alternative in parallel with
   the CometBFT spike
6. Carry Narwhal-Bullshark as a Tier 2 investigation item pending DAG
   censorship formal analysis

The next lane must not:
- Declare a final Option-B winner without completing the remaining gap items
- Begin production validator deployment before CDL-017 is ratified
- Treat the Phase 690 benchmark harnesses as production-proof rather than
  research instruments

---

## 6. Explicit statement on final Option-B selection

`final_option_b_selection_remains_later`

Final Option-B substrate selection is not authorized by this window.

The evidence in this window — prefilter, BFT research, benchmark harness
definitions, comparison analysis — is research-grade. It is necessary but not
sufficient for final selection.

Final Option-B selection requires, in a later lane:
- Completed bounded spike work demonstrating the Tier 1 family is
  implementable at production quality
- Row-5 mechanism proof over the concrete substrate
- Validator governance CDL ratified
- Settlement-state formal CDL ratified
- BAL calibration completed (or explicit deferral statement)
- Explicit human authorization for the selection

---

## 7. Window row state after 692

Row state is unchanged by this window. CDL-062 is now open as a research lane
but its ratification remains later.

| Row | Status after 692 |
|---|---|
| Rows 1-4 | `runtime_closed` (unchanged) |
| Row 5 | `partial` (unchanged) |
| Row 6 | `closed` (unchanged) |
| Rows 7-9 | `closed` (unchanged) |
| CDL-062 | `open (research lane)` — was `unopened` |
| Option D | `active` (unchanged) |

---

## 8. Minimum acceptable result assessment

This window meets the minimum acceptable result from the candidate grouping:

- Admissible and inadmissible families are clearly separated: YES
- Benchmark and comparison methodology are real: YES — anchored to Phase 687
  settlement-state enumeration
- The next sovereign implementation or deeper-selection lane receives a
  disciplined handoff rather than "research substrate later": YES — Tier 1
  survivor set named, remaining gaps explicit, next-lane obligations stated

The best-case result is also met:
- CDL-062 opens as a bounded research lane under explicit human GO: YES
- The live lane is narrowed to a serious sovereign survivor set: YES
  (CometBFT + HotStuff/Jolteon Tier 1)
- Benchmark discipline is real: YES
- The project has a serious BFT/finality implementation-spec artifact: YES
  (Phase 689 research packet)
