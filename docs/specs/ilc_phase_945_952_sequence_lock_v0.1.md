# ILC Phase 945–950, 1100–1101 Sequence Lock

**Window:** 945–950, 1100–1101
**Locked at:** Phase 945
**Date:** 2026-04-28
**Status:** LOCKED
**Reference:** `docs/specs/ilc_window_945_952_candidate_phase_grouping_v0.1.md`

**Phase numbering correction (applied at Phase 1100):** Phases originally planned as 951 and
952 collide with the Cluster-A G8 reserved range (0951–1014, permanently reserved per Phase 944
§4). Corrected: Phase 951 → Phase 1100, Phase 952 → Phase 1101. Window identity corrected
to 945–1101. All other phase numbers (945–950) are unaffected.

`window_945_952_sequence_lock_committed_phase_945`
`window_945_1101_phase_numbering_corrected_phase_1100`

---

## Phase Table (corrected)

| Order | Phase | Topic | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 945 | Window sequence lock + capsule v5.32 | Foundation / Constitutional | NON-SENSITIVE |
| 2 | 946 | H-012 settle() runtime + Decimal precision fix (M1) | Runtime | NON-SENSITIVE |
| 3 | 947 | H-012 ratification evidence (31 tests) | Runtime | NON-SENSITIVE |
| 4 | 948 | CDL-082 opening — H-013 threshold amendment | Constitutional | SENSITIVE |
| 5 | 949 | CDL-082 prelock hardening + ratification evidence doc | Constitutional | NON-SENSITIVE |
| 6 | 950 | CDL-082 ratification (two-commit: runtime + CDL) | Constitutional / Runtime | SENSITIVE |
| 7 | **1100** | Coherence report + capsule v5.33 | Synthesis | NON-SENSITIVE |
| 8 | **1101** | Window 945–1101 closure gate | Gate | SENSITIVE |

---

## Sequencing Constraints

1. Phase 945 (seq lock) must precede all other phases — locks the sequence.
2. Phase 946 (runtime) must precede Phase 947 (tests) — tests import the runtime.
3. Phase 948 (CDL-082 open) must precede Phase 949 (prelock hardening).
4. Phase 949 (prelock + evidence) must precede Phase 950 (ratification).
5. Phase 950 Commit 1 (runtime mutation) must precede Phase 950 Commit 2 (CDL mutation).
6. Phases 945–950 must all precede Phase 1100 (coherence report cites all window work).
7. Phase 1100 must precede Phase 1101 (closure gate verifies coherence report).

---

## Sensitive Phase Authorization

| Phase | Env var required | Trigger |
|-------|-----------------|---------|
| 948 | `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=948` | CDL-082 row inserted in constitutional log |
| 950 (Commit 2 only) | `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=950` | CDL-082 spec OPEN → RATIFIED + log row updated |
| 1101 | Human closure verdict required | Structural window boundary |

---

## Window Entry Conditions (confirmed met at Phase 945)

- CDL-081 ratified (Phase 943) — H-012 prerequisite met.
- SIM-BEACON-01 complete (Phase 939) — CDL-082 evidence exists.
- Phase 944 coherence report records capsule v5.32 as forward obligation.
- Phase numbering: normal lane 945–950 available; 951–1014 permanently reserved (Cluster-A);
  990–1099 reserved buffer; normal lane resumes at 1100+.

`window_945_952_sequence_lock_committed_phase_945`
`window_945_1101_phase_numbering_corrected_phase_1100`
