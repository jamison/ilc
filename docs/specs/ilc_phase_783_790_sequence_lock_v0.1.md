# ILC Phase 783-790 Sequence Lock v0.1

**Phase:** 783  
**Window:** 783-790  
**Date:** 2026-04-22  
**Author:** Local architectural reviewer (Sonnet)

`window_783_790_sequence_lock_active`
`row_8_substrate_evaluation_and_cdl_062_admissibility_window`
`mysticeti_sovereign_is_named_candidate_for_classification`
`phase_673_exclusion_matrix_is_binding_evaluation_surface`
`phase_675_criteria_lock_is_binding_evaluation_surface`
`cdl_062_admissibility_determination_required`
`human_gate_required_for_option_b_selection_not_discharged_by_this_window`
`no_cdl_mutation_in_window_783_790`
`window_783_790_parallel_to_775_782_and_791_800`
`window_767_774_closed_capsule_v5_6_current_at_sequence_lock_time`

## 1. Baseline and authority order

Window 767-774 is closed. Capsule `v5.6` is the current frontier. CDL-017 is
ratified (Phase 765). Row 7 is `runtime_closed`. Row 5 is
`spec_closed_runtime_pending` with active remediation running in Window 775-782.
CDL-062 is open as a research lane (Phase 687). Mysticeti has been elevated to
Tier 1 primary in the Phase 693 survivor set addendum.

Window 783-790 is parallel to Window 775-782 (Row 5 remediation) and Window
791-800 (Hypergraph research). It does not depend on either window's outcome.
Row 5 does not need to close before this window can produce a CDL-062
admissibility determination — the Phase 662 admissibility matrix requires row 5
to be *narrowed*, not closed. Row 5 is in active remediation; that satisfies
the narrowing requirement.

Authority order for this window:

1. live `STATUS.md` tail and `docs/PLANNING_INDEX.md`
2. capsule `v5.6` (or whichever is current at execution time)
3. `docs/research/ilc_post_766_continuation_program_guide_2026_04_22_v0.1.md`
   (Window 3 section)
4. `docs/specs/ilc_cdl_062_mysticeti_survivor_set_addendum_693_v0.1.md`
   (Phase 693 — Mysticeti elevated to Tier 1 primary; row-8 independence pass
   issued; ECU owned/shared object split defined; TLA+ requirement stated)
5. `docs/specs/ilc_external_constitutional_center_and_exclusion_matrix_673_v0.1.md`
   (Phase 673 — binding exclusion matrix for row-8 classification)
6. `docs/specs/ilc_rows_7_8_selection_criteria_lock_675_v0.1.md`
   (Phase 675 — locked row-7 and row-8 rules)
7. `docs/specs/ilc_cdl_062_opening_admissibility_matrix_662_v0.1.md`
   (Phase 662 — formal opening-side CDL-062 admissibility gates)
8. `docs/specs/ilc_row_8_disposition_and_option_b_gate_synthesis_cw5_v0.1.md`
   (Phase 761 — most recent Option B gate synthesis; blockers explicitly stated)
9. `docs/specs/ilc_cdl_062_research_lane_handoff_692_v0.1.md`
   (Phase 692 — window 687-692 handoff; prior survivor set before Phase 693
   correction)
10. live constitutional decision log

## 2. Pre-window state and resolved questions

The following questions were treated as open in the program guide. All three
are resolved by prior work and are locked here before execution begins.

**Q1 — Mysticeti independence criterion: RESOLVED — pass**

Phase 693 §4 issued an explicit row-8 independence verdict against the Mysticeti
sovereign configuration: *"Row-8 independence: pass — ILC governs its own
validator set; the Mysticeti protocol is sovereign; the Sui network and Sui
Foundation are not involved."*

The Phase 675 independence criterion tests *governance independence* — no
external party may veto ILC protocol legitimacy decisions. The `mysticeti-core`
crate is used as a library under MIT license. ILC replaces the application layer
entirely. The Sui Foundation has no veto authority over ILC's validator set,
protocol rules, or legitimacy decisions. Upstream code dependency is not a
disqualifying dependency under Phase 673; only de facto governance authority
over ILC legitimacy is disqualifying. This question does not reopen in Window
783-790. The Phase 693 pass verdict is the authoritative record.

**Q2 — Row 5 partial-state and CDL-062 admissibility: RESOLVED — no wait required**

The Phase 662 admissibility matrix states `row_5_must_be_narrowed_before_cdl_062_admissible`.
It does not require row 5 to be closed. Row 5 is currently
`spec_closed_runtime_pending` with a defined attacker model, a defined
two-layer mechanism family (Layer-1 log hygiene, Layer-2 batching + multi-relay),
defined closure bands, and active SIM-LEAKAGE-01 remediation running in Window
775-782. This is substantially more than "narrowed" — it is in active remediation
with a commissioning spec. Window 783-790 does not wait on Window 775-782's
outcome before opening or before issuing a CDL-062 admissibility determination.

**Q3 — Replayability evidence for row-8: RESOLVED — existing evidence sufficient**

Row 7 is `runtime_closed`: `row_7_censorship_resistance_runtime_closure_verdict=pass`
and `row_7_strong_exitability_runtime_closure_verdict=pass` are both committed.
The Phase 675 exitability and replayability proof obligations are already
discharged by that runtime closure. Window 783-790 evaluates Mysticeti
sovereign against the Phase 673 *independence* exclusion matrix — not against
row-7 censorship or finality claims, which are already closed. No new benchmark
packet is required.

**CDL-062 status note:** CDL-062 is already open as a research lane (Phase 687).
The Phase 662 admissibility matrix governed whether CDL-062 *could open*. That
threshold was crossed when CDL-062 opened at Phase 687. What this window produces
is not a second admissibility determination on whether CDL-062 may open — it is
an *evaluation artifact* classifying Mysticeti sovereign against the row-8 criteria
and recording the current Option B gate state honestly.

## 3. Window meaning

Window 783-790 is the Row 8 substrate evaluation window.

`mysticeti_sovereign_classified_against_phase_673_exclusion_matrix`
`mysticeti_sovereign_classified_against_phase_675_criteria_lock`
`option_b_gate_re_synthesized_against_current_blocker_state`
`cdl_062_admissibility_evaluation_artifact_required`
`honest_human_gate_record_required`
`no_option_b_selection_claim_permitted`
`no_cdl_mutation_permitted`
`tla_plus_status_recorded_honestly`
`capsule_v5_9_required_at_closure`

This window exists to:

1. classify Mysticeti sovereign configuration against every criterion in the
   Phase 673 exclusion matrix and the Phase 675 criteria lock
2. produce a CDL-062 evaluation artifact: pass, conditional, or not-yet —
   with the exact conditions named if conditional or not-yet
3. re-synthesize the Option B gate against the current committed evidence:
   CDL-017 now ratified (discharged); row-8 evaluation produced by this window
4. record the human gate honestly: CDL-062 admissibility is not Option B
   selection; the human decision boundary is named and preserved
5. record the TLA+ formal verification status honestly: Phase 693 mandated TLA+
   for both the shared-object DAG path and the owned-object fast path before any
   Rust implementation lane opens
6. update coherence report and capsule to v5.9
7. close the window at Phase 790 gate

This window does not select Option B. It does not implement Mysticeti. It does
not open any new CDL. It does not mutate the constitutional decision log. It
does not close row 5 or interact with Window 775-782. It does not advance
the hypergraph lane.

## 4. Evaluation scope

### 4.1 Mysticeti sovereign — Phase 673 exclusion matrix classification

The Phase 673 exclusion matrix defines six disqualifying dependency patterns.
Each must be evaluated explicitly for the Mysticeti sovereign configuration.

**Disqualifying pattern 1 — Protocol legitimacy can be overridden or nullified
by an outside governance body:**

Mysticeti sovereign: ILC governs its own validator set via CDL-017. The Sui
Foundation has no authority over ILC's validator admission, ejection, or
protocol rules. The `mysticeti-core` crate is MIT-licensed library code. No
outside governance body has a veto over ILC legitimacy decisions.
**Classification: DOES NOT APPLY.**

**Disqualifying pattern 2 — Admission or namespace authority can be created
outside protocol lineage:**

Mysticeti sovereign: validator admission is governed exclusively by CDL-017
(now ratified). No external party can admit a validator to the ILC network.
AgentID namespace is derived from BLS key material under CDL-042 — no external
namespace authority.
**Classification: DOES NOT APPLY.**

**Disqualifying pattern 3 — Public settlement legitimacy can be declared without
protocol receipt basis:**

Mysticeti sovereign: settlement legitimacy flows from the ILC epoch settlement
record (DAG-CBOR + CIDv1 state root), submitted to the Mysticeti consensus
layer. The Mysticeti layer does not author ILC legitimacy — it finalizes
ILC-authored state. No outside party can declare settlement legitimacy that
ILC did not produce.
**Classification: DOES NOT APPLY.**

**Disqualifying pattern 4 — Public reputation continuity depends on outside
operator or vendor approval:**

Mysticeti sovereign: reputation scores and ECU attribution are computed by the
ILC epistemic engine. No external operator or vendor approval is required for
reputation continuity. The Sui Foundation cannot freeze or modify ILC reputation
state.
**Classification: DOES NOT APPLY.**

**Disqualifying pattern 5 — The only practical audit or exit path runs through
one hosted control plane:**

Mysticeti sovereign: the DAG commit structure is verifiable via graph traversal
from any archive node. ILC must build a one-time verification CLI (Phase 693
§4 audit note). This is a tooling investment, not a structural dependency. No
single hosted control plane is the only exit path.
**Classification: DOES NOT APPLY — conditional on tooling delivery noted in §4.3.**

**Disqualifying pattern 6 — Migration requires privileged consent from the
original operator or provider:**

Mysticeti sovereign: full DAG history is reconstructible from public archive
nodes. There is no privileged migration consent requirement. An ILC operator
can stand up an independent archive node from public data.
**Classification: DOES NOT APPLY.**

**Phase 673 matrix verdict for Mysticeti sovereign:**
`mysticeti_sovereign_phase_673_exclusion_matrix_verdict=pass`

No disqualifying dependency pattern applies. The Mysticeti sovereign
configuration falls into the Phase 673 "presumptively admissible" family:
"sovereign minimal L1 / BFT network where protocol legitimacy stays upstream
and exit is credible."

### 4.2 Mysticeti sovereign — Phase 675 criteria lock classification

The Phase 675 locked row-8 rule has three components:

**Component 1 — Later substrate families may not make protocol legitimacy
subordinate to an outside veto authority:**

Mysticeti sovereign: ILC legitimacy is authored by the ILC epistemic engine and
validator set. The Mysticeti consensus layer finalizes ILC-authored state; it
does not author legitimacy. The Sui Foundation is not in the write path for
ILC legitimacy. **SATISFIED.**

**Component 2 — Outside systems may carry or settle already-legitimate protocol
state, but may not become the constitutional center that authors legitimacy:**

Mysticeti sovereign: the Mysticeti DAG carries ILC epoch settlement records
that ILC authored. Mysticeti does not determine what counts as a valid ILC
submission, what the epoch state root should be, or which validators are
legitimate. **SATISFIED.**

**Component 3 — The Phase 673 exclusion matrix is binding for later substrate
admissibility:**

Classified in §4.1 above: all six exclusion patterns — DOES NOT APPLY.
**SATISFIED.**

**Phase 675 criteria lock verdict for Mysticeti sovereign:**
`mysticeti_sovereign_phase_675_criteria_lock_verdict=pass`

### 4.3 Conditional notes and carry-forward obligations

Two honest conditional notes apply to the pass verdicts above:

**Note A — Verification tooling obligation (Phase 673 pattern 5):**
Phase 693 §4 flagged: "ILC must build a one-time verification CLI abstracting
DAG graph traversal for non-expert operators (satisfies Phase 679 observability
budget with tooling investment)." This tooling does not exist yet. The pass
verdict on pattern 5 is conditioned on this tooling being delivered before any
public-facing deployment claim. It does not block the row-8 classification or
the CDL-062 evaluation artifact; it is a named pre-deployment obligation.

**Note B — TLA+ formal verification (Phase 693 mandatory prerequisite):**
Phase 693 §6 mandated TLA+ formal verification of both:
1. Shared-object DAG commit path (`docs/specs/tla/ilc_dag_censorship_bounds.tla`)
2. Owned-object Byzantine Consistent Broadcast fast path
   (`docs/specs/tla/ilc_ecu_fast_path_bcast.tla`)

TLC model check must pass before any Rust implementation lane opens. This
window records the current TLA+ status honestly. If the specs exist and TLC
passes, record the positive result. If the specs exist but TLC has not been run,
record that explicitly. If the specs do not exist, record the gap — it is a gate
for the implementation lane (Window 803+), not for this evaluation window.

Check: `docs/specs/tla/ilc_dag_censorship_bounds.tla` and
`docs/specs/tla/ilc_ecu_fast_path_bcast.tla` — read what exists at execution
time and record status honestly.

### 4.4 CDL-062 evaluation artifact

CDL-062 is already open as a research lane. This window produces an evaluation
artifact recording the current CDL-062 state against the Phase 662 formal
opening-side gates — not to re-adjudicate whether CDL-062 may open, but to
record the honest current status for the Option B gate synthesis.

Phase 662 opening-side gates — status at Window 783-790:

| Gate | Status | Evidence |
|---|---|---|
| Row 6 closed via CDL-065 | Record current status | Read CDL log at execution time |
| Rows 7 and 8 locked as selection criteria | SATISFIED | Phase 675 criteria lock; Phase 673 matrix |
| Row 9 material transport/discovery maturity | Record current status | Read H-series and transport status |
| Row 5 narrowed | SATISFIED | Active remediation in Window 775-782; mechanism family defined |
| Machine-legible participation | Record current status | gRPC surfaces; CLI access |
| Harness-agnostic access | Record current status | CLI, file, JSON surfaces |
| Agent-participant parity | Record current status | Phase 680 compatibility |
| Human-auditability co-preservation | Record current status | Phase 679 observability budget |
| Bounded agent economic participation | Record current status | ECU transfer path |

For each gate with "Record current status": read the authoritative source at
execution time and record the honest verdict. Do not assume a gate is satisfied
without evidence. Do not assume a gate is failed without evidence.

**CDL-062 evaluation verdict format:**
- `cdl_062_evaluation_verdict=pass` — all gates satisfied (CDL-062 is open and
  the lane is well-founded)
- `cdl_062_evaluation_verdict=conditional` — all formally required gates
  satisfied; named conditional obligations remain (list them explicitly)
- `cdl_062_evaluation_verdict=not_yet` — one or more formal gates not yet met
  (name which, and what satisfies them)

### 4.5 Option B gate re-synthesis

The Phase 761 gate synthesis recorded:
- Row-7 proof obligations: PASS
- Row-8 candidate evaluation: PENDING (the blocker this window discharges)
- CDL-017 ratification: PENDING (discharged — Phase 765)

After this window completes the row-8 classification, re-synthesize the gate:

| Gate condition | Status at Phase 790 | Evidence |
|---|---|---|
| Row-7 proof obligations satisfied | PASS | Phase 761 — unchanged |
| CDL-017 ratified | PASS | Phase 765 |
| Row-8 exclusion matrix evaluation | Result of §4.1 | This window |
| Row-8 criteria lock classification | Result of §4.2 | This window |

If both row-8 items return pass: the formal blocker list is discharged.
The remaining gate is the **human decision boundary** — Option B selection
requires explicit human authorization. That boundary must be named explicitly
and honestly in the gate synthesis. The synthesis artifact must not imply that
a pass verdict automatically activates Option B.

**Option B gate synthesis verdict format:**
- `option_b_gate_synthesis_verdict=go_pending_human_authorization` — all formal
  blockers discharged; human decision is the only remaining gate
- `option_b_gate_synthesis_verdict=no_go` — one or more formal blockers remain
  (name which)

## 5. Phase table and sequencing

| Order | Phase | Topic | Character |
|---|---:|---|---|
| 1 | 783 | Sequence lock (this document) | gate |
| 2 | 784 | TLA+ status audit | audit |
| 3 | 785 | Phase 673 exclusion matrix classification artifact | evaluation |
| 4 | 786 | Phase 675 criteria lock classification artifact | evaluation |
| 5 | 787 | CDL-062 evaluation artifact | evaluation |
| 6 | 788 | Option B gate re-synthesis | evaluation |
| 7 | 789 | Coherence report + capsule v5.9 | coherence |
| 8 | 790 | Closure gate + handoff | gate |

Sequencing rules:

- Phase 784 (TLA+ audit) may execute first; its output informs Phase 788 (Option B
  synthesis) but does not block Phase 785 or 786
- Phases 785 and 786 are independent of each other and may execute in parallel
  or in either order
- Phase 787 reads Phases 785 and 786 outputs; it must follow both
- Phase 788 reads Phases 784, 785, 786, and 787; it must follow all four
- Phase 789 reads all prior outputs; it must be last before Phase 790
- Phase 790 is the closure gate; it must be last

## 6. Pass conditions for closure gate (Phase 790)

The closure gate must assert:

- Phase 673 exclusion matrix classification artifact exists with an explicit
  verdict for each of the six disqualifying patterns
- Phase 675 criteria lock classification artifact exists with a verdict on all
  three components
- Mysticeti sovereign row-8 combined verdict recorded:
  `mysticeti_sovereign_phase_673_exclusion_matrix_verdict=pass|fail`
  and `mysticeti_sovereign_phase_675_criteria_lock_verdict=pass|fail`
- TLA+ status recorded honestly — existing specs and TLC run status noted;
  gap flagged if specs do not exist
- Conditional notes recorded (verification tooling obligation; TLA+ gate for
  implementation lane)
- CDL-062 evaluation artifact exists with verdict:
  `cdl_062_evaluation_verdict=pass|conditional|not_yet`
  If conditional or not-yet: named conditions listed explicitly
- Option B gate synthesis artifact exists with verdict:
  `option_b_gate_synthesis_verdict=go_pending_human_authorization|no_go`
  If no-go: remaining blockers named explicitly
- Human decision boundary recorded explicitly: Option B selection requires
  human authorization regardless of gate synthesis verdict
- No CDL rows mutated anywhere in Window 783-790
- No Option B selection claim made
- Capsule v5.9 exists and supersedes the capsule current at window open time
- Handoff names the pre-deployment obligations (verification tooling, TLA+ if
  not yet done) and the human gate for Option B selection

## 7. Non-goals

This window does not include:

- Option B selection
- Mysticeti implementation or spike work
- TLA+ specification authoring (if specs don't exist, the gap is recorded;
  spec authoring is a separate window)
- Any CDL mutation, opening, or prelocking
- Row 5 remediation work or SIM-LEAKAGE-01 execution
- Hypergraph lane work
- Jolteon/HotStuff fallback analysis (Gap 6 from Phase 692 — fallback-only,
  not needed unless Mysticeti extraction proves infeasible)
- Legal memo (Window 797-802 scope)
- CDL-017 re-evaluation (already ratified)
- Any `ilc_core/` Python runtime mutation
- Any Rust consensus implementation work

## 8. Pre-window state corrections (locked before execution)

The following are locked and must not be re-opened as design questions:

- **Mysticeti is the named candidate.** Jolteon/HotStuff remains the named
  fallback only. No other candidate is evaluated in this window.
- **Row 5 partial-state does not block this window.** The Phase 662 narrowing
  requirement is satisfied by active remediation. This is decided.
- **Row-8 independence criterion is about governance, not code provenance.**
  MIT license + ILC validator sovereignty = pass on independence. This is decided
  by Phase 693. Do not re-litigate.
- **CDL-062 is already open.** This window evaluates and records; it does not
  re-open or re-adjudicate CDL-062 admissibility.
- **The human gate is real and must be named.** No prose in this window may
  imply that a formal-blockers-cleared verdict means Option B is selected or
  imminent without explicit human authorization.

## 9. Source inputs

- `docs/PLANNING_INDEX.md`
- `docs/phases/STATUS.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.6.md`
- `docs/specs/ilc_window_767_774_closure_gate_774_v0.1.md`
- `docs/research/ilc_post_766_continuation_program_guide_2026_04_22_v0.1.md`
- `docs/specs/ilc_cdl_062_mysticeti_survivor_set_addendum_693_v0.1.md`
- `docs/specs/ilc_external_constitutional_center_and_exclusion_matrix_673_v0.1.md`
- `docs/specs/ilc_rows_7_8_selection_criteria_lock_675_v0.1.md`
- `docs/specs/ilc_cdl_062_opening_admissibility_matrix_662_v0.1.md`
- `docs/specs/ilc_row_8_disposition_and_option_b_gate_synthesis_cw5_v0.1.md`
- `docs/specs/ilc_cdl_062_research_lane_handoff_692_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/tla/ilc_dag_censorship_bounds.tla` (read if exists; record gap if not)
- `docs/specs/tla/ilc_ecu_fast_path_bcast.tla` (read if exists; record gap if not)

This sequence lock remains active until Phase `790` closes Window `783-790`.
