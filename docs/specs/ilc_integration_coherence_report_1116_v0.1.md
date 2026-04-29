# ILC Integration Coherence Report — Phase 1116

**Window:** 1110-1117
**Phase:** 1116
**Date:** 2026-04-30
**Verdict:** `coherence_report_1116_verdict=pass`

---

## 1. Purpose

Window 1110-1117 ratified CDL-084 (PROVENANCE chain attribution), activated the geometric
decay ECU payout path in `settle_attribution_batch()`, and replaced the prior PROVENANCE
silent-ignore stub. This report audits that all window deliverables are internally consistent
and ready for the Phase 1117 closure gate.

---

## 2. CDL-084 Coverage Table

| CDL-084 section | Content | Implemented | Tested |
|-----------------|---------|-------------|--------|
| §2 Q1 | PROVENANCE triggers ECU; caller-only contract; one traversal emits PROVENANCE or REUSE, not both | Caller-filter contract; no runtime cross-event detector | G9 |
| §2 Q2 | Geometric decay; `PROVENANCE_DECAY_ALPHA = Decimal("0.5")`; provisional pending SIM-PROVENANCE-01 | `PROVENANCE_DECAY_ALPHA: Decimal` in `types.py` | G1, G12 |
| §2 Q3 | `PROVENANCE_MAX_DEPTH = 3`; hop 1 = immediate parent | `PROVENANCE_MAX_DEPTH: int = 3` in `types.py` | G1, G7, G13 |
| §2 Q4 | Ancestor creator receives ECU | `creator_id` from chain payload is payout recipient | G6, G7 |
| §2 Q5 | Fresh per-event state; `visited_creators` nearest-hop-wins | Per-event `visited_creators` set in PROVENANCE path | G8 |
| §2 Q6 | Explicit nearest-first chain payload; pure settle, no graph queries | `AttributionEvent.provenance_chain`; settle path consumes caller payload only | G3, G6, G7 |
| §2 Q7 | Duplicate `node_id` raises; duplicate `creator_id` nearest-hop-wins | `seen_node_ids` validation plus `visited_creators` skip | G5, G8 |
| §2 Q8 | Epoch mint source; SIM-PROVENANCE-01 required before alpha locks | Alpha remains provisional; forward obligation recorded | G2 plus §5 of this report |
| §2 Q9 | Float kill: `PROVENANCE_DECAY_ALPHA: float -> Decimal("0.5")` | Phase 1113 Commit 1 (`3d943f32`) | G1, G12 |
| §2 Q10 | `None` chain -> `provenance_event_missing_chain`; `()` chain -> `provenance_event_empty_chain` | Validation in PROVENANCE `elif` path | G4 |

---

## 3. Dependency Token Chain

| Token | Value | Location |
|-------|-------|----------|
| `EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION` | `"epoch_attribution_settle_runtime_1114.v0.3"` | `epoch_attribution_settle_runtime.py` |
| `CDL_084_DEPENDENCY` | `"cdl_084_provenance_chain_attribution_ratified_1113.v0.1"` | `epoch_attribution_settle_runtime.py` |
| `CDL_084_TYPES_DEPENDENCY` | `"cdl_084_provenance_chain_attribution_ratified_1113.v0.1"` | `ilc_core/types.py` |
| `PROVENANCE_DECAY_ALPHA` | `Decimal("0.5")` — provisional pending SIM-PROVENANCE-01 | `ilc_core/types.py` |
| `PROVENANCE_MAX_DEPTH` | `3` (`int`) | `ilc_core/types.py` |

---

## 4. Audit Findings

| Finding | Disposition |
|---------|-------------|
| `PROVENANCE_DECAY_ALPHA` is `Decimal`, not `float` | Confirmed — Phase 1113 Commit 1 (`3d943f32`); G1 and G12 verify |
| `AttributionEvent.provenance_chain` field present | Confirmed — Phase 1113 Commit 1; G3 verifies |
| PROVENANCE silent-ignore stub replaced with active ECU path | Confirmed — Phase 1114; G6, G7, G8 verify payout behavior |
| `Decimal ** int` arithmetic used for decay | Confirmed — Phase 1115 payout tests return Decimal amounts |
| G1-G14 evidence tests pass; >=30 tests | Confirmed — Phase 1115 has 31 tests |
| CDL-084 spec shows `**Status:** RATIFIED` | Confirmed — Phase 1113 Commit 2 |
| CDL log row shows `ratified_phase: 1113` | Confirmed — G10 verifies |
| G11 historical assertion: Phase 1111 commit shows `**Status:** OPEN` | Confirmed — git show `2066f75d:...opening_1111...` |
| Hypergraph planning doc aligned to CDL-084 ratified state | Done Phase 1116 |
| Runtime version bumped to `v0.3` at PROVENANCE settlement activation | Confirmed — Phase 1114; G2 verifies |

---

## 5. Forward Obligations

| Item | Status | Next action |
|------|--------|-------------|
| SIM-PROVENANCE-01: alpha calibration | Obligated — alpha provisional pending simulation | Commissioning spec must test inflation/gaming pressure and log per-node PROVENANCE descendant counts as a time series for SIM-SPECTRAL-02 |
| SIM-SPECTRAL-02: Popperian durability / Epistemic Reach correlation | Deferred — non-canonical research direction pending SIM-PROVENANCE-01 data | Sequence after SIM-PROVENANCE-01; test PROVENANCE reach against falsification-resistance, reuse, and validation durability |
| Werner phi-bound CDL | Deferred — SIM evidence required before this CDL can open | Carry forward from Window 1109 handoff |
| ADR-0035 implementation CDL | Deferred — direction accepted at Phase 1100; planning/authorization gate remains | Carry forward from Window 1109 handoff |
| Star expansion implementation | Deferred — constitutional prerequisites appear satisfied, but implementation remains blocked on patent/planning review and explicit human authorization | Planning review before implementation CDL |
| Phase 1117 closure gate | Next — SENSITIVE | Requires human GO token |

---

## 6. Evidence Summary

| Phase | Evidence |
|-------|----------|
| 1110 | Window guidance and sequence lock published |
| 1111 | CDL-084 opened (SENSITIVE); ratification evidence spec published |
| 1112 | CDL-084 prelock hardening; 8 invariants confirmed |
| 1113 | CDL-084 ratified: Commit 1 (`3d943f32`) float kill + event shape; Commit 2 (`275bdd14`) OPEN -> RATIFIED |
| 1114 | PROVENANCE settlement path active; `epoch_attribution_settle_runtime_1114.v0.3` |
| 1115 | `tests/test_phase_1115_cdl_084_provenance_chain_attribution.py` — 31 tests, G1-G14 |
| 1116 | Coherence report, capsule v5.35, hypergraph planning alignment, forward pointers |

`coherence_report_1116_verdict=pass`

