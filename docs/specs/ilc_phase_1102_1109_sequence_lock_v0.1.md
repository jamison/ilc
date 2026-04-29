# ILC Phase 1102–1109 Sequence Lock

**Window:** 1102–1109
**Topic:** H-CON-02 Panel Quorum Rules for Ejected Stake Treasury Distribution (CDL-083)
**Locked:** Phase 1102 (2026-04-28)
**Author:** Claude Sonnet 4.6 (local architectural reviewer)
**Baseline:** Window 945–950, 1100–1101 CLOSED (Phase 1101, commit f523e918).
             CDL-082 ratified (Phase 950). CDL-083 Q1–Q5 human-authorized (2026-04-28).
             Capsule v5.33. Next fresh CDL: CDL-083.

`window_1102_1109_sequence_lock_committed_phase_1102`

---

## Phase Table (Locked)

| Order | Phase | Topic | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 1102 | Window sequence lock (this document) | Foundation | NON-SENSITIVE |
| 2 | 1103 | CDL-083 opening — H-CON-02 panel quorum + REFUTATION attribution | Constitutional | **SENSITIVE** |
| 3 | 1104 | CDL-083 prelock hardening + ratification evidence doc | Constitutional | NON-SENSITIVE |
| 4 | 1105 | CDL-083 ratification (two commits: runtime + CDL) | Constitutional / Runtime | **SENSITIVE** |
| 5 | 1106 | H-CON-02 runtime — REFUTATION path implementation | Runtime | NON-SENSITIVE |
| 6 | 1107 | H-CON-02 ratification evidence tests | Runtime | NON-SENSITIVE |
| 7 | 1108 | Coherence report + capsule v5.34 | Synthesis | NON-SENSITIVE |
| 8 | 1109 | Window 1102–1109 closure gate | Gate | **SENSITIVE** |

---

## Sequencing Constraints (Locked)

1. Phase 1102 (seq lock) must precede all other phases — **this document**.
2. Phase 1103 (CDL open) must precede Phase 1104 (prelock asserts open state).
3. Phase 1104 must precede Phase 1105 (ratification cites evidence doc and prelock commit).
4. Phase 1105 Commit 1 (runtime mutation, no CDL env var) must precede Phase 1105 Commit 2 (CDL mutation).
5. Phase 1105 must precede Phase 1106 (ratification-enabling runtime mutation lands first; Phase 1106 hardens and tests the ratified runtime surface without re-opening CDL-083 semantics).
6. Phase 1106 must precede Phase 1107 (tests import the runtime).
7. Phases 1102–1107 must all precede Phase 1108 (coherence cites all window work).
8. Phase 1108 must precede Phase 1109 (closure gate cites coherence report).

---

## CDL-083 Scope (Locked)

**Title:** H-CON-02 Panel Quorum Rules for Ejected Stake Treasury Distribution and REFUTATION Attribution

**Two sub-scopes:**

### Sub-scope 1 — Ejected stake treasury distribution
CDL-081 §4.5 established that ejected member stake accumulates in the star node treasury.
H-CON-02 (CDL-083) defines the panel quorum rules for distribution.

### Sub-scope 2 — REFUTATION edge attribution
CDL-081 Q1 declared REFUTATION attribution "conditional on CDL-V7 Popperian gate upholding
the refutation" and deferred the ECU flow definition to H-CON-02. CDL-083 defines that flow.

**Out of scope (confirmed deferred):**
- PROVENANCE chain attribution (CDL-084, Window 1110+)
- ADR-0035 homoiconic type system implementation
- Werner φ-bound CDL
- ATTESTATION / EPOCH_BOUNDARY attribution changes

---

## CDL-083 Human-Gate Decisions (Pre-Authorized)

Q1–Q5 were presented to the human and authorized 2026-04-28. The following values are
locked for CDL-083 opening at Phase 1103:

| Q | Decision | Value |
|---|----------|-------|
| Q1 | Quorum participation floor | ≥0.50 of remaining members; hard minimum 2 voters |
| Q2 | Vote threshold | Exact 2/3 supermajority of participating voters, evaluated by integer arithmetic (`approve_votes * 3 >= participating_voters * 2`) |
| Q3 | Distribution formula | Proportional to current stake of all remaining members at distribution epoch |
| Q4 | REFUTATION ECU flow | Upheld REFUTATION → `REUSE_ATTRIBUTION_RATE` (0.20) to refuting agent, epoch mint source; caller-filters upheld events before batch entry |
| Q5 | Ejected stake recovery | Irrevocable — readmission starts with zero stake; no retroactive recovery |

Canon anchors for Q1–Q5: `epoch_state_runtime.py` (`quorum_threshold: {2, 3}`);
CDL-081 §4.2 stake-proportional split; CDL-058 re-admission boundary; CDL-046 ejection.

---

## CDL Number Assignments (Locked)

| CDL | Title | Status | Opening phase | Ratification phase |
|-----|-------|--------|--------------|-------------------|
| CDL-083 | H-CON-02 panel quorum rules + REFUTATION attribution | pre-open | 1103 | 1105 |

Next fresh CDL after CDL-083: CDL-084 (PROVENANCE, Window 1110+).

---

## Pre-Commit Hook Requirements

```
# Phase 1103 (CDL-083 log insert — opening only, no ilc_core/ changes):
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1103

# Phase 1105 Commit 1 (runtime mutation — NO CDL env var, NO CDL doc changes):
# (no env var required — ilc_core/ only)

# Phase 1105 Commit 2 (CDL mutation — NO ilc_core/ changes):
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1105
```

The pre-commit hook enforces that CDL-authorized commits must not touch `ilc_core/`.
Phase 1105 must be two separate commits for this reason.

---

## Canonical Anchors for Prompt Drafting

| Artifact | Path |
|----------|------|
| Window guidance doc | `docs/specs/ilc_window_1102_1109_candidate_phase_grouping_v0.1.md` |
| Prior window handoff | `docs/specs/ilc_window_945_1101_handoff_1101_v0.1.md` |
| Settle runtime (active stub) | `ilc_core/economics/epoch_attribution_settle_runtime.py` |
| CDL-081 spec | `docs/specs/ilc_cdl_081_hyperedge_ecu_attribution_opening_929_v0.1.md` |
| Constitutional decision log | `docs/specs/ilc_constitutional_decision_log_v0.1.md` |
| Capsule v5.33 | `docs/specs/ilc_antigravity_context_capsule_v5.33.md` |

---

## Non-Goals for This Window

- No PROVENANCE attribution implementation (CDL-084 scope)
- No ADR-0035 runtime changes (CDL required first)
- No changes to CDL-V7 Popperian gate implementation (CDL-052 scope)
- No treasury governance changes (CDL-047 scope)
- No star node adoption rule changes (CDL-081 scope)
- No Werner φ-bound (SIM required)

`window_1102_1109_sequence_lock_committed_phase_1102`
`cdl_083_q1_q5_pre_authorized_human_gate_complete`
`cdl_083_scope_locked_ejected_stake_refutation_attribution`
`provenance_deferred_cdl_084_window_1110_plus`
