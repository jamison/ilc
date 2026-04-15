# ILC Window 677-682: Candidate Phase Grouping

**Author:** Codex
**Date:** 2026-04-15
**Baseline:** Window 671-676 CLOSED. Capsule v4.2 is current. Rows 1-4 remain `runtime_closed`; row 5 remains `not_started`; row 6 remains `closed`; rows 7-8 remain `closed` as criteria-first governance locks; row 9 remains `closed`. The next planned target is row 5 as privacy-preserving public-legitimacy prework, not final mechanism closure.
**Planning note:** This is a candidate grouping, not a locked sequence. The purpose of this packet is to define the likely phase shape, scope discipline, core conversation questions, and recommended posture for the row-5 privacy lane before sequence lock.

## 1. Window identity and scope

Window 677-682 is the first major post-rows-7-and-8 lane. Its purpose is to
attack checklist row 5 directly, but only in the pre-substrate sense:

1. define the narrowed privacy problem as correlation minimization and
   unlinkability for public submissions rather than "hide all private work";
2. define the leak surfaces and adversary classes that matter for public
   legitimacy participation;
3. define the minimum observability and auditability budget that privacy work
   may not violate;
4. narrow candidate mechanism families and reject bad ones before substrate
   implementation work begins; and
5. either advance row 5 from `not_started` to a sharply bounded `partial`
   posture or prove that even prework cannot honestly reduce the ambiguity.

This window is not the final row-5 closure lane. It is not a sovereign
substrate implementation lane. It is not a `CDL-062` opening lane. It is a
privacy threat-model, observability-budget, and mechanism-family narrowing
lane.

## 2. Baseline and inheritance

Inherited canon and carry-forward:
- `docs/specs/ilc_settlement_substrate_governance_vehicle_selection_611_v0.1.md`
  already fixes row 5 as a real graduation blocker and explicitly leaves the
  mechanism unresolved.
- `docs/specs/ilc_option_b_remaining_rows_closure_criteria_661_v0.1.md`
  already sharpens the row-5 closure surfaces.
- `docs/specs/ilc_window_671_676_handoff_676_v0.1.md` already routes the next
  planned lane to row-5 privacy-preserving public-legitimacy prework.
- `docs/specs/ilc_antigravity_context_capsule_v4.2.md` already records row 5
  as the sole remaining undefined checklist row.
- `docs/research/ilc_option_b_architecture_memo_and_remaining_gates_v0.1.md`
  is non-canonical but directionally useful in narrowing the privacy problem to
  correlation minimization and unlinkability for public submissions.

Inherited rule set:
- Option D remains active.
- `CDL-062` remains unopened.
- rows 6-9 should not be silently reopened here.
- row 5 remains open and is the only checklist row still at `not_started`.
- the public-work-only model narrows the privacy target, but does not close row
  5.

## 3. Operationally obligated versus deferred

### 3.1 Obligated in this window

- a row-5 privacy threat model centered on public submission correlation and
  linkability
- a leak-surface inventory
- a minimum observability and auditability budget
- a candidate mechanism-family matrix and rejection packet
- simulation or red-team evidence on realistic linkability leakage patterns
- a decision record on whether row 5 can honestly move from `not_started` to
  `partial`

### 3.2 Explicitly deferred

- final row-5 closure over a chosen settlement architecture
- `CDL-062` opening
- sovereign substrate implementation
- production runtime implementation of a privacy mechanism
- claims of full anonymity or global passive-adversary immunity
- reopening rows 6-9

## 4. Window design lemma

The governing lemma for this window should be:

- public-legitimacy work must remain machine-legible, challengeable, and
  auditable; and
- privacy work must minimize correlation and linkability for public submissions
  without destroying receipt lineage, bounded human auditability, or protocol
  contestability.

This means the window should distinguish:
- privacy for public submission correlation,
- privacy for private off-graph work, which is already outside the protocol
  reward surface,
- and overbuilt privacy that breaks observability or turns legitimacy into an
  opaque black box.

## 5. Candidate phase table

| Order | Phase | Topic | Character | Sensitivity |
|---|---:|---|---|---|
| 1 | 677 | Sequence lock, canon inventory, and row-5 problem framing | Foundation / Planning | **SENSITIVE** |
| 2 | 678 | Privacy threat model and leak-surface inventory | Research / Criteria | planning |
| 3 | 679 | Observability budget and auditability floor | Criteria / Governance | planning |
| 4 | 680 | Candidate mechanism-family matrix and rejection packet | Research / Design narrowing | planning |
| 5 | 681 | Correlation / unlinkability simulation and red-team packet | Simulation / Adversarial review | planning |
| 6 | 682 | Narrowing decision, checklist delta, capsule, and handoff | Gate | **SENSITIVE** |

## 6. Scope notes for candidate phases

### Phase 677 — sequence lock and canon inventory

Deliverables:
- `docs/specs/ilc_phase_677_682_sequence_lock_v0.1.md`
- `docs/research/ilc_row_5_canon_inventory_and_issue_register_677_v0.1.md`

Required content spec:
- fix the row-5 mission
- lock non-goals
- classify inherited canon versus supporting context
- fix the public-work-only narrowing as the starting point
- classify which questions are normative and which are simulation-heavy

### Phase 678 — privacy threat model and leak-surface inventory

Deliverables:
- `docs/specs/ilc_privacy_public_legitimacy_threat_model_678_v0.1.md`

Required content spec:
- adversary classes
- correlation and linkability surfaces
- receipt, settlement, namespace, timing, and operator-metadata leak surfaces
- hosted-query-surface aggregation as its own practical surveillance class
- participant classes harmed by overexposure
- explicit distinction between public-submission privacy and private-work
  privacy

### Phase 679 — observability budget and auditability floor

Deliverables:
- `docs/specs/ilc_public_legitimacy_observability_budget_679_v0.1.md`

Required content spec:
- what must remain machine-legible
- what bounded human auditability requires
- what receipt lineage may not lose
- what contestability and challengeability require
- what forms of opacity are disqualifying even if they improve unlinkability
- explicit hard constraints:
  - machine-legible receipts
  - receipt lineage intact
  - challengeability preserved
  - bounded human auditability preserved
- explicit inadmissibility for default designs that require specialized tooling
  to verify public legitimacy claims

### Phase 680 — mechanism-family matrix and rejection packet

Deliverables:
- `docs/specs/ilc_row_5_mechanism_family_matrix_680_v0.1.md`

Required content spec:
- candidate mechanism families at the architectural level
- compatibility with public auditability and receipt lineage
- interaction with later substrate choice
- rejected families with reasons
- three-bucket classification:
  - near-term tractable
  - later-stage tractable
  - presumptively inadmissible
- shortlist or narrowed candidate set for later lanes

### Phase 681 — simulation and red-team packet

Deliverables:
- `docs/specs/ilc_row_5_correlation_unlinkability_simulation_packet_681_v0.1.md`
- optional structured metrics or scenario JSON if useful

Required content spec:
- realistic public-participation correlation scenarios
- ordinary-observer and operator-path leakage analysis
- observability-versus-unlinkability tradeoff evidence
- red-team or adversarial reasoning on linkage recovery
- explicit statement of what the candidate families do not protect against
- concrete definition of "materially harder" using a degradation metric rather
  than narrative-only judgment
- phase sequencing note: this phase scopes to the surviving shortlist from
  Phase 680 and may force a controlled iterate-back if the Phase 680 matrix is
  still too wide for realistic simulation

### Phase 682 — narrowing decision and handoff

Deliverables:
- `docs/specs/ilc_row_5_prework_narrowing_decision_682_v0.1.md`
- updated checklist state JSON
- updated capsule
- handoff note

Required content spec:
- whether row 5 advances from `not_started` to `partial`
- whether a dedicated CDL vehicle is likely required before final mechanism
  closure
- exact carry-forward into later substrate and privacy mechanism work
- next-lane routing
- explicit statement of the remaining row-5 gap after this window closes

## 7. Main conversation questions for this window

The phase work is downstream of these human decisions:

1. What exactly is the protected thing: contributor identity, submission
   linkage, settlement linkage, timing correlation, operator metadata, or some
   bounded subset?
2. Which adversaries matter for row 5: ordinary public observers, protocol
   operators, hosting providers, outside indexers, hosted-query surfaces, or
   stronger observers?
3. What is the non-negotiable observability floor for receipts, auditability,
   and contestability?
4. How much unlinkability is enough for this lane to count as meaningful
   progress, and by what metric is "materially harder" measured?
5. Can row 5 close before a concrete substrate is chosen, or only advance to a
   bounded `partial` state?
6. Which mechanism families are worth narrowing now versus explicitly deferring?
7. How much UX, debuggability, and operational burden is acceptable in exchange
   for privacy gains?

## 8. Current recommendation

My current recommendation for sequence lock is:
- treat row 5 as the hardest remaining checklist row
- do not promise row-5 closure in this window
- do promise that row 5 should stop being `not_started`
- keep the target narrow: correlation minimization and unlinkability for public
  submissions
- protect identity, cross-submission linkage, and receipt/settlement linkage as
  the minimum row-5 privacy target while keeping receipts themselves
  machine-legible and auditable
- treat public observers, indexers, hosted-query surfaces, and operator/query
  paths as the minimum adversary set
- explicitly reject any privacy approach that destroys machine-legible
  participation, bounded human auditability, or receipt lineage
- treat Phase 679 observability budget work as a standalone hard-constraint
  artifact rather than an inherited preference
- assume this lane is likely to require iterative simulation and red-team
  passes, especially in Phases 678, 680, and 681
- assume a later dedicated CDL vehicle is plausible, but do not pre-open one in
  this window

## 9. What this candidate grouping does not claim

This artifact does not claim:
- row 5 is already narrowed enough for closure
- the exact privacy mechanism family is already known
- a later sovereign substrate has already been selected
- a ZK-heavy design is required
- `CDL-062` is openable now
