# ILC Window 671-676: Candidate Phase Grouping

**Author:** Codex
**Date:** 2026-04-15
**Historical note, 2026-04-15:** This is a pre-lock planning artifact. It is superseded for current-frontier decision purposes by [the Phase 671 sequence lock](./ilc_phase_671_676_sequence_lock_v0.1.md) and [the 676 handoff](./ilc_window_671_676_handoff_676_v0.1.md).
**Baseline:** Window 665-670 CLOSED. Capsule v4.1 is current. Rows 1-4 remain `runtime_closed`; row 5 remains `not_started`; row 6 remains `closed`; row 9 is now `closed`; rows 7-8 remain `partial`. The next planned target is rows 7 and 8 as criteria-first closure work, not substrate implementation.
**Planning note:** This is a candidate grouping, not a locked sequence. The purpose of this packet is to define the likely phase shape, scope discipline, core conversation questions, and recommended posture for the censorship-resistance and independence lane before sequence lock.

## 1. Window identity and scope

Window 671-676 is the first major post-row-9 governance lane. Its purpose is to
attack checklist rows 7 and 8 directly as substrate-selection criteria rather
than as substrate code:

1. define what future substrate options must prove about censorship resistance,
   exitability, and replayability;
2. define what counts as an external constitutional center and what forms of
   outside veto are disqualifying;
3. publish a usable exclusion matrix and decision record for later substrate
   selection; and
4. either close rows 7 and 8 honestly or narrow any remaining gap into a hard,
   enforceable carry-forward threshold.

This window is not a privacy-mechanism lane. It is not a substrate
implementation lane. It is not a `CDL-062` opening lane. It is a
criteria-definition and governance-constraint lane.

## 2. Baseline and inheritance

Inherited canon and carry-forward:
- `docs/specs/ilc_settlement_substrate_governance_vehicle_selection_611_v0.1.md`
  already names censorship resistance and independence from external
  constitutional centers as Option-B graduation criteria.
- `docs/specs/ilc_option_b_remaining_rows_closure_criteria_661_v0.1.md`
  already sharpens the required closure surfaces for rows 7 and 8.
- `docs/specs/ilc_window_659_664_handoff_664_v0.1.md` already routes Window
  671-676 to row-7 and row-8 criteria work.
- `docs/specs/ilc_phase_585_genesis_authority_and_sunset_dependency_note_v0.1.md`
  already establishes Genesis as a bounded bootstrap necessity, not indefinite
  founder sovereignty.
- `docs/specs/ilc_cdl_v6_genesis_intervention_protocol_ratification_evidence_334_v0.1.md`
  already ratifies Genesis intervention only as a documented, sunset-bound,
  audited extraordinary path.

Inherited rule set:
- Option D remains active.
- `CDL-062` remains unopened.
- row 9 is closed and should not be silently reopened here.
- rows 7 and 8 are still open and require explicit criteria closure rather than
  intuition.
- Genesis-rooted legitimacy lineage remains canonical.
- Genesis-operated choke points are tolerated only as bounded bootstrap
  exceptions with transfer and sunset semantics.

## 3. Operationally obligated versus deferred

### 3.1 Obligated in this window

- a row-7 censorship and exclusion threat model
- a minimum bar for participant exitability and replayability
- an explicit definition of external constitutional center
- an exclusion matrix for later substrate families
- a clear Genesis bootstrap-exception statement that does not collapse into
  founder bottleneck tolerance
- a decision record saying whether row 8 closes here and whether row 7 closes
  here or remains a bounded threshold

### 3.2 Explicitly deferred

- privacy-preserving public legitimacy mechanism work for row 5
- `CDL-062` opening
- sovereign substrate implementation
- benchmark or throughput comparison of concrete substrate candidates
- runtime integration with any chosen settlement backend
- transport rediscovery or row-9 revalidation

## 4. Window design lemma

The governing lemma for this window should be:

- public legitimacy surfaces must remain contestable, portable, and auditable
  without dependence on one hidden operator choke point; and
- later substrate choices may carry or settle protocol legitimacy, but they may
  not become the source of protocol legitimacy or the sole constitutional center
  for public ILC participation.

This means the window should distinguish:
- tolerated bootstrap exception,
- ordinary operational convenience,
- and constitutionally disqualifying external dependence.

## 5. Genesis exception rule for this lane

Window 671-676 should not accidentally write against existing Genesis canon.

The working rule should be:
- Genesis-rooted artifact lineage remains canonical and non-optional.
- Genesis-sensitive authority may still exist in bounded bootstrap form.
- Genesis may not be treated as a permanent excuse for bottlenecking public
  legitimacy surfaces through one founder, one dashboard, or one provider shell.
- any Genesis bootstrap exception must be documented, auditable, challengeable,
  and sunset-bound.

This preserves:
- canonical continuity,
- bootstrap necessity,
- and the anti-sovereign-bottleneck rule at the same time.

## 6. Candidate phase table

| Order | Phase | Topic | Character | Sensitivity |
|---|---:|---|---|---|
| 1 | 671 | Sequence lock, canon inventory, and issue register | Foundation / Planning | **SENSITIVE** |
| 2 | 672 | Censorship-resistance threat model and legitimacy-surface map | Research / Criteria | planning |
| 3 | 673 | External constitutional center definition and exclusion matrix | Research / Governance | planning |
| 4 | 674 | Exitability and replayability threshold contract | Criteria / Admissibility | planning |
| 5 | 675 | Criteria lock, row-8 decision, and row-7 threshold or closure decision | Review / Ratification prep | **SENSITIVE** |
| 6 | 676 | Closure gate, checklist delta, capsule, and handoff | Gate | **SENSITIVE** |

## 7. Scope notes for candidate phases

### Phase 671 — sequence lock and canon inventory

Deliverables:
- `docs/specs/ilc_phase_671_676_sequence_lock_v0.1.md`
- `docs/research/ilc_rows_7_8_canon_inventory_and_issue_register_671_v0.1.md`

Required content spec:
- fix the rows 7 and 8 mission
- lock non-goals
- classify inherited canon into binding, supporting, and carry-forward
- explicitly include the Genesis bootstrap-exception rule
- classify which questions are normative and which are empirical

### Phase 672 — censorship-resistance threat model

Deliverables:
- `docs/specs/ilc_censorship_resistance_threat_model_672_v0.1.md`

Required content spec:
- public legitimacy surface inventory
- denial, exclusion, throttling, routing, namespace, custody, dashboard, and
  shell-level choke points
- participant classes affected
- minimum anti-bottleneck interpretation for row 7

### Phase 673 — independence and exclusion matrix

Deliverables:
- `docs/specs/ilc_external_constitutional_center_and_exclusion_matrix_673_v0.1.md`

Required content spec:
- definition of external constitutional center
- definition of outside veto authority
- candidate substrate-family matrix
- allowed, risky, and disqualifying dependency patterns
- Genesis bootstrap exception distinguished from ordinary third-party control

### Phase 674 — exitability and replayability threshold

Deliverables:
- `docs/specs/ilc_exitability_and_replayability_threshold_674_v0.1.md`

Required content spec:
- minimum state extractability rule
- portable proof requirements
- replayability and migration minimums
- requirements that do not depend on privileged original-operator consent
- row-7 enforceable threshold wording

### Phase 675 — criteria lock and decision packet

Deliverables:
- `docs/specs/ilc_rows_7_8_selection_criteria_lock_675_v0.1.md`
- `docs/specs/ilc_rows_7_8_ratification_or_threshold_decision_675_v0.1.md`

Required content spec:
- whether row 8 closes now
- whether row 7 closes now or remains an explicit admissibility threshold
- exclusion list for future substrate work
- decision record stating what later lanes may not violate

### Phase 676 — closure gate and handoff

Deliverables:
- `docs/specs/ilc_window_671_676_handoff_676_v0.1.md`
- updated checklist state JSON
- updated capsule

Required content spec:
- final status of rows 7 and 8 after this lane
- routing into row 5 prework and later substrate selection
- exact carry-forward if row 7 is not yet fully closed

## 8. Main conversation questions for this window

The phase work is downstream of these human decisions:

1. How broad is the row-7 censorship model?
2. What exactly counts as an external constitutional center?
3. What dependency patterns are disqualifying versus merely undesirable?
4. What is the minimum acceptable exitability and replayability bar?
5. Can row 8 close on criteria alone?
6. Can row 7 close on criteria alone, or only become a hard pre-opening gate?
7. How should Genesis bootstrap exception language be written so it does not
   collapse into founder bottleneck tolerance?

## 9. Current recommendation

My current recommendation for sequence lock is:
- row 8 should likely close in this window
- row 7 must at minimum become a hard enforceable threshold
- row 7 may also close in this window if the project accepts a
  criteria-first closure standard rather than requiring live substrate proof
- Genesis should be treated as a bounded bootstrap exception, not as an
  anti-bottleneck exemption in general
- no `CDL-062` opening should occur in this window

## 10. What this candidate grouping does not claim

This artifact does not claim:
- rows 7 or 8 are already closed
- the exact row-7 threshold text is already final
- a later sovereign substrate has already been selected
- Genesis has already fully sunset
- `CDL-062` is openable now
