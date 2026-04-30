# ILC Window 1110–1117: Candidate Phase Grouping

**Author:** Claude Sonnet 4.6 (local architectural reviewer)
**Date:** 2026-04-29
**Baseline:** Window 1102–1109 CLOSED (Phase 1109, commit 9ede8c79). CDL-083 ratified
             (Phase 1105). Capsule v5.34. CDL-084 Q1–Q10 human-authorized (2026-04-29).

---

## 1. Window Identity and Scope

**Window:** 1110–1117
**Topic:** CDL-084 PROVENANCE Chain Attribution
**Primary obligation:** Constitutionalise ECU attribution for PROVENANCE edges —
derivation credit flowing back along the ancestor chain up to `PROVENANCE_MAX_DEPTH` hops.

**Prerequisite satisfied:** CDL-083 ratified (Phase 1105). PROVENANCE was silently ignored
pending CDL-084. That silence is now CDL-licensed (CDL-081 §4.3 + CDL-083 §5.4 confirm
PROVENANCE is ignored until CDL-084). Window 1110 lifts that silence constitutionally.

---

## 2. Baseline and Inheritance

| Artifact | Path | Role |
|----------|------|------|
| Prior window handoff | `docs/specs/ilc_window_1102_1109_handoff_1109_v0.1.md` | Incoming state |
| Capsule | `docs/specs/ilc_antigravity_context_capsule_v5.34.md` | Current context |
| Settle runtime | `ilc_core/economics/epoch_attribution_settle_runtime.py` | File under change |
| Types | `ilc_core/types.py` | PROVENANCE_MAX_DEPTH, PROVENANCE_DECAY_ALPHA (float — to be fixed) |
| CDL-083 spec | `docs/specs/ilc_cdl_083_h_con_02_panel_quorum_ejected_stake_opening_1103_v0.1.md` | CDL-083 §4.3 confirms PROVENANCE ignored until CDL-084 |
| CDL log | `docs/specs/ilc_constitutional_decision_log_v0.1.md` | Insert CDL-084 row at Phase 1111 |
| Hypergraph planning | `docs/research/ilc_morphogenetic_hypergraph_planning_classification_v0.1.md` | Planning alignment (Phase 1116) |

**Active runtime stub:** In `settle_attribution_batch()`:
```python
# §4.3 ATTESTATION, PROVENANCE, EPOCH_BOUNDARY — silently ignored.
```
CDL-084 ratification replaces the silent-ignore for PROVENANCE with an active settlement path.
ATTESTATION and EPOCH_BOUNDARY remain silently ignored.

**Provisional float to fix:** `ilc_core/types.py` line 83:
```python
PROVENANCE_DECAY_ALPHA: float = 0.5   # must become Decimal("0.5") at Phase 1113 Commit 1
```

---

## 3. Track Inventory

| Track | Phases | Character |
|-------|--------|-----------|
| Constitutional | 1110 (seq lock), 1111 (CDL open + evidence spec), 1112 (prelock), 1113 (ratification) | SENSITIVE: 1111 open, 1113 Commit 2 |
| Runtime | 1114 (PROVENANCE settlement), 1115 (evidence tests) | NON-SENSITIVE |
| Synthesis | 1116 (coherence + capsule v5.35 + planning alignment), 1117 (closure gate) | SENSITIVE: 1117 |

---

## 4. CDL Number Assignments

| CDL | Title | Status | Opening phase | Ratification phase |
|-----|-------|--------|--------------|-------------------|
| CDL-084 | PROVENANCE chain attribution | pre-open | 1111 | 1113 |

Next fresh CDL after CDL-084: CDL-085 (Werner φ-bound or ADR-0035 CDL — TBD).

---

## 5. Candidate Phase Table

| Order | Phase | Topic | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 1110 | Window sequence lock (this guidance doc ratified) | Foundation | NON-SENSITIVE |
| 2 | 1111 | CDL-084 opening + ratification evidence spec | Constitutional | **SENSITIVE** |
| 3 | 1112 | CDL-084 prelock hardening | Constitutional | NON-SENSITIVE |
| 4 | 1113 | CDL-084 ratification (two commits) | Constitutional/Runtime | **SENSITIVE** |
| 5 | 1114 | PROVENANCE settlement runtime implementation | Runtime | NON-SENSITIVE |
| 6 | 1115 | PROVENANCE evidence tests | Runtime | NON-SENSITIVE |
| 7 | 1116 | Coherence report + capsule v5.35 + planning alignment | Synthesis | NON-SENSITIVE |
| 8 | 1117 | Window 1110–1117 closure gate + handoff | Gate | **SENSITIVE** |

---

## 6. Sensitivity Classification

**SENSITIVE:**
- Phase 1111 — CDL-084 opening inserts a new CDL log row
  (`ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1111`)
- Phase 1113 Commit 2 — CDL-084 OPEN → RATIFIED + log row update
  (`ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1113`)
- Phase 1117 — Closure gate; requires human GO token

**NON-SENSITIVE:** All other phases may proceed after prompt approval.

**Pre-commit hook:** CDL-authorized commits must not touch `ilc_core/`. Phase 1113 must
be two separate commits (Commit 1: `ilc_core/` runtime + `ilc_core/types.py` float fix,
no CDL env var; Commit 2: CDL docs only, with CDL env var).

---

## 7. CDL-084 Q1–Q10 Decisions (All Human-Authorized 2026-04-29)

| Q | Decision | Token |
|---|----------|-------|
| Q1 | PROVENANCE triggers ECU; caller-only contract — one traversal emits PROVENANCE or REUSE, not both | `q1_provenance_triggers_ecu_caller_only_contract` |
| Q2 | Geometric decay; `PROVENANCE_DECAY_ALPHA = Decimal("0.5")`; provisional pending SIM-PROVENANCE-01 | `q2_geometric_decay_alpha_decimal_0_5_provisional` |
| Q3 | `PROVENANCE_MAX_DEPTH = 3`; immediate parent = hop 1; max included hop = 3 | `q3_max_depth_3_hop_1_is_immediate_parent` |
| Q4 | Creator of each ancestor node receives ECU (consistent with CDL-081 Q5 originator-credit) | `q4_ancestor_creator_receives_ecu` |
| Q5 | Fresh `visited_set` per event per CDL-081 §4.1; `visited_creators` set deduplicates within event chain; nearest hop wins | `q5_fresh_per_event_visited_creators_nearest_hop_wins` |
| Q6 | Event shape: `provenance_chain: Optional[tuple[tuple[str, str], ...]]` ordered nearest-ancestor-first; len ≤ `PROVENANCE_MAX_DEPTH`; settle makes no graph queries (pure function) | `q6_explicit_chain_payload_nearest_first_pure_settle` |
| Q7 | Repeated `node_id` in chain → `ValueError("provenance_chain_contains_duplicate_node_id")`; repeated `creator_id` → nearest hop wins (first occurrence, skip later) | `q7_duplicate_node_id_raises_nearest_creator_wins` |
| Q8 | Epoch mint source (consistent with REUSE/REFUTATION); SIM-PROVENANCE-01 must test inflation surface before alpha is locked | `q8_epoch_mint_source_sim_provenance_01_required` |
| Q9 | `PROVENANCE_DECAY_ALPHA: float = 0.5` in `ilc_core/types.py` must be replaced with `Decimal("0.5")` before any economic runtime use; fix in Phase 1113 Commit 1 | `q9_float_kill_decimal_literal_0_5` |
| Q10 | `provenance_chain=None` → `ValueError("provenance_event_missing_chain")`; `provenance_chain=()` → `ValueError("provenance_event_empty_chain")` | `q10_none_raises_missing_empty_raises_empty` |

---

## 8. Implementation Targets (Locked for Phase 1113/1114)

### 8.1 `ilc_core/types.py` changes (Phase 1113 Commit 1)

Replace:
```python
PROVENANCE_DECAY_ALPHA: float = 0.5
```
With:
```python
PROVENANCE_DECAY_ALPHA: Decimal = Decimal("0.5")   # Q9: CDL-084 locks mechanism; SIM-PROVENANCE-01 refines value
CDL_084_TYPES_DEPENDENCY = "cdl_084_provenance_chain_attribution_ratified_1113.v0.1"
```

`PROVENANCE_MAX_DEPTH: int = 3` is already correct type — no change needed.

### 8.2 `AttributionEvent` extension (Phase 1113 Commit 1)

Add field to `AttributionEvent` dataclass in `epoch_attribution_settle_runtime.py`:
```python
provenance_chain: Optional[tuple[tuple[str, str], ...]] = None
# Q6: ((node_id, creator_id), ...) ordered nearest-ancestor-first
# len must be > 0 and ≤ PROVENANCE_MAX_DEPTH for PROVENANCE events
# None is valid for non-PROVENANCE events
```

### 8.3 New constants (Phase 1113 Commit 1)

In `epoch_attribution_settle_runtime.py`:
```python
EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION = "epoch_attribution_settle_runtime_1114.v0.3"
CDL_084_DEPENDENCY = "cdl_084_provenance_chain_attribution_ratified_1113.v0.1"
```

### 8.4 PROVENANCE settlement path (Phase 1114)

Replace the silent-ignore for PROVENANCE in `settle_attribution_batch()`:
```python
elif attr_event.edge_type == EdgeType.PROVENANCE:
    # CDL-084 §X: PROVENANCE chain attribution.
    # Q10: None/empty chain is malformed.
    chain = attr_event.provenance_chain
    if chain is None:
        raise ValueError("provenance_event_missing_chain")
    if len(chain) == 0:
        raise ValueError("provenance_event_empty_chain")
    # Q7: reject duplicate node_ids in chain
    seen_node_ids: set[str] = set()
    for node_id, _ in chain:
        if node_id in seen_node_ids:
            raise ValueError("provenance_chain_contains_duplicate_node_id")
        seen_node_ids.add(node_id)
    # Q5/Q7: pay each creator at most once; nearest hop wins
    visited_creators: set[str] = set()
    for hop_index, (node_id, creator_id) in enumerate(chain):
        if hop_index >= PROVENANCE_MAX_DEPTH:
            break  # Q3: max depth enforced
        if creator_id in visited_creators:
            continue  # Q7: nearest hop wins; skip duplicate creators
        visited_creators.add(creator_id)
        # Q2: geometric decay — alpha^(hop+1) where hop_index 0 = immediate parent (hop 1)
        decay = PROVENANCE_DECAY_ALPHA ** (hop_index + 1)
        payout = REUSE_ATTRIBUTION_RATE * decay
        payouts.append((creator_id, payout))
```

Note: `PROVENANCE_DECAY_ALPHA` must be `Decimal` before this path is activated (Q9).
`Decimal ** int` is exact in Python's decimal module.

---

## 9. Sequencing Constraints (Locked)

1. Phase 1110 (seq lock) must precede all other phases.
2. Phase 1111 (CDL open) must precede Phase 1112 (prelock asserts open state).
3. Phase 1112 must precede Phase 1113 (ratification cites evidence doc and prelock commit).
4. Phase 1113 Commit 1 (`ilc_core/` + `ilc_core/types.py`, no CDL env var) must precede Phase 1113 Commit 2 (CDL mutation, CDL env var, no `ilc_core/` changes).
5. Phase 1113 must precede Phase 1114 (runtime builds on ratified constants and event shape).
6. Phase 1114 must precede Phase 1115 (tests import the PROVENANCE path).
7. Phases 1110–1115 must all precede Phase 1116 (coherence cites all window work).
8. Phase 1116 must precede Phase 1117 (closure gate cites coherence report + capsule).

---

## 10. Key Dependencies and Open Questions

### Dependencies satisfied at window entry
- CDL-083 ratified (Phase 1105) — PROVENANCE silence is CDL-licensed
- `PROVENANCE_MAX_DEPTH = 3` already in `ilc_core/types.py` (correct type)
- `EdgeType.PROVENANCE = "provenance"` already in `ilc_core/types.py`
- Q1–Q10 all human-authorized (2026-04-29)

### Open questions deferred to later windows
- SIM-PROVENANCE-01: inflation/gaming pressure test for `PROVENANCE_DECAY_ALPHA`
  (alpha is provisional pending SIM — CDL-084 locks the *mechanism*, not the final value)
- Werner φ-bound CDL (CDL-085 candidate): needs SIM before opening
- Star expansion implementation: gate now clear (CDL-081 ✓, CDL-083 ✓, SIM-REUSE-01 ✓);
  planning review in Phase 1116

---

## 11. Non-Goals for This Window

- No SIM-PROVENANCE-01 execution (that requires a separate SIM window)
- No SIM-HYPEREDGE-01 execution (planning review only in Phase 1116)
- No star expansion implementation
- No changes to ATTESTATION or EPOCH_BOUNDARY handling (remain silently ignored)
- No Werner φ-bound CDL
- No ADR-0035 implementation CDL
- No changes to CDL-081 or CDL-083

---

## 12. Key Canonical Anchors for Prompt Drafting

| Artifact | Path |
|----------|------|
| This guidance doc | `docs/specs/ilc_window_1110_1117_candidate_phase_grouping_v0.1.md` |
| Prior window handoff | `docs/specs/ilc_window_1102_1109_handoff_1109_v0.1.md` |
| Settle runtime | `ilc_core/economics/epoch_attribution_settle_runtime.py` |
| Types (float to fix) | `ilc_core/types.py` |
| CDL log | `docs/specs/ilc_constitutional_decision_log_v0.1.md` |
| CDL-083 spec (scope ref) | `docs/specs/ilc_cdl_083_h_con_02_panel_quorum_ejected_stake_opening_1103_v0.1.md` |
| Capsule v5.34 | `docs/specs/ilc_antigravity_context_capsule_v5.34.md` |
| H-012 evidence tests (format ref) | `tests/test_phase_0947_h012_epoch_attribution_settle.py` |
| CDL-083 evidence tests (format ref) | `tests/test_phase_1107_h_con_02_panel_quorum_settle.py` |

`window_1110_1117_guidance_doc_published`
`cdl_084_q1_q10_all_human_authorized_2026_04_29`
`provenance_decimal_float_kill_required_phase_1113_commit_1`

**Status:** CLOSED — Phase 1117 closure gate passed. `window_1110_1117_closed_phase_1117`
