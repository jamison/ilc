# ILC Phase 1110–1117 Sequence Lock

**Window:** 1110–1117
**Topic:** CDL-084 PROVENANCE Chain Attribution
**Locked:** Phase 1110 (2026-04-29)
**Author:** Claude Sonnet 4.6 (local architectural reviewer)
**Baseline:** Window 1102–1109 CLOSED (Phase 1109, commit 9ede8c79). CDL-083 ratified
             (Phase 1105). Capsule v5.34. CDL-084 Q1–Q10 human-authorized (2026-04-29).
             Guidance doc: `docs/specs/ilc_window_1110_1117_candidate_phase_grouping_v0.1.md`
             (commit 55c0fb70).

`window_1110_1117_sequence_lock_committed_phase_1110`

---

## Phase Table (Locked)

| Order | Phase | Topic | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 1110 | Window sequence lock (this document) | Foundation | NON-SENSITIVE |
| 2 | 1111 | CDL-084 opening + ratification evidence spec | Constitutional | **SENSITIVE** |
| 3 | 1112 | CDL-084 prelock hardening | Constitutional | NON-SENSITIVE |
| 4 | 1113 | CDL-084 ratification (two commits: runtime/float-kill + CDL) | Constitutional / Runtime | **SENSITIVE** |
| 5 | 1114 | PROVENANCE settlement runtime implementation | Runtime | NON-SENSITIVE |
| 6 | 1115 | PROVENANCE evidence tests | Runtime | NON-SENSITIVE |
| 7 | 1116 | Coherence report + capsule v5.35 + planning alignment | Synthesis | NON-SENSITIVE |
| 8 | 1117 | Window 1110–1117 closure gate | Gate | **SENSITIVE** |

---

## Sequencing Constraints (Locked)

1. Phase 1110 (seq lock) must precede all other phases — **this document**.
2. Phase 1111 (CDL open) must precede Phase 1112 (prelock asserts open state).
3. Phase 1112 must precede Phase 1113 (ratification cites evidence doc and prelock commit).
4. Phase 1113 Commit 1 (`ilc_core/` runtime + `ilc_core/types.py` float fix, no CDL env var)
   must precede Phase 1113 Commit 2 (CDL docs only, CDL env var, no `ilc_core/` changes).
5. Phase 1113 must precede Phase 1114 (runtime builds on ratified constants and event shape).
6. Phase 1114 must precede Phase 1115 (tests import the PROVENANCE path).
7. Phases 1110–1115 must all precede Phase 1116 (coherence cites all window work).
8. Phase 1116 must precede Phase 1117 (closure gate cites coherence report + capsule).

---

## CDL-084 Scope (Locked)

**Title:** PROVENANCE Chain Attribution

**Primary obligation:** Constitutionalise ECU attribution for PROVENANCE edges —
derivation credit flowing back along the ancestor chain up to `PROVENANCE_MAX_DEPTH` hops.

**Prerequisite satisfied:** CDL-083 ratified (Phase 1105). PROVENANCE was silently ignored
pending CDL-084 under CDL-081 §4.3 + CDL-083 §5.4. Window 1110 lifts that silence
constitutionally.

**Decisions locked (Q1–Q10, all human-authorized 2026-04-29):**

| Q | Token |
|---|-------|
| Q1 — PROVENANCE triggers ECU; caller-only contract | `q1_provenance_triggers_ecu_caller_only_contract` |
| Q2 — Geometric decay; `PROVENANCE_DECAY_ALPHA = Decimal("0.5")` | `q2_geometric_decay_alpha_decimal_0_5_provisional` |
| Q3 — `PROVENANCE_MAX_DEPTH = 3`; immediate parent = hop 1 | `q3_max_depth_3_hop_1_is_immediate_parent` |
| Q4 — Creator of each ancestor node receives ECU | `q4_ancestor_creator_receives_ecu` |
| Q5 — Fresh `visited_set` per event; `visited_creators` nearest hop wins | `q5_fresh_per_event_visited_creators_nearest_hop_wins` |
| Q6 — Explicit chain payload; pure settle function; no graph queries | `q6_explicit_chain_payload_nearest_first_pure_settle` |
| Q7 — Duplicate node_id raises; duplicate creator_id → nearest wins | `q7_duplicate_node_id_raises_nearest_creator_wins` |
| Q8 — Epoch mint source; SIM-PROVENANCE-01 required before alpha locked | `q8_epoch_mint_source_sim_provenance_01_required` |
| Q9 — Float kill: `PROVENANCE_DECAY_ALPHA: float` → `Decimal("0.5")` | `q9_float_kill_decimal_literal_0_5` |
| Q10 — None chain raises missing; empty chain raises empty | `q10_none_raises_missing_empty_raises_empty` |

**Out of scope (confirmed deferred):**
- SIM-PROVENANCE-01 execution (separate SIM window)
- SIM-HYPEREDGE-01 execution (planning review only in Phase 1116)
- Star expansion implementation
- ATTESTATION or EPOCH_BOUNDARY handling changes (remain silently ignored)
- Werner φ-bound CDL (CDL-085 candidate)
- ADR-0035 implementation CDL

---

## Phase 1113 Two-Commit Structure (Locked)

**Commit 1** — `ilc_core/` runtime + types float fix (no CDL env var):
- `ilc_core/types.py`: `PROVENANCE_DECAY_ALPHA: float = 0.5` → `Decimal("0.5")` + `CDL_084_TYPES_DEPENDENCY`
- `ilc_core/economics/epoch_attribution_settle_runtime.py`: `provenance_chain` field on `AttributionEvent`, new constants, new version token
- No `ILC_CDL_MUTATION_AUTHORIZED` env var on this commit

**Commit 2** — CDL docs only (CDL env var required):
- CDL-084 spec: OPEN → RATIFIED
- CDL log: insert ratification row
- `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1113`
- No `ilc_core/` changes (pre-commit hook enforces this)

---

## Sensitivity Classification

**SENSITIVE — requires human GO token before execution:**
- Phase 1111 — CDL-084 opening inserts new CDL log row (`ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1111`)
- Phase 1113 Commit 2 — CDL-084 OPEN → RATIFIED + log row update (`ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1113`)
- Phase 1117 — Closure gate; requires human GO token

**NON-SENSITIVE:** All other phases may proceed after prompt approval.
