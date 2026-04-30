# ILC Phase 1124–1129 Sequence Lock

Window: 1124–1129
Topic: CDL-084 Q2 Alpha Amendment — PROVENANCE_DECAY_ALPHA Lock
Locked: Phase 1124 (2026-04-30)
Author: Claude Sonnet 4.6 (local architectural reviewer)
Baseline: Window 1118–1123 CLOSED (Phase 1123, commit `2b8b05b9`). CDL-084 ratified
          (Phase 1113). SIM-PROVENANCE-01 complete (Phases 1120–1121); α=0.45
          recommended; Q8 satisfied; Q2 active. Capsule v5.36. 247 tests.
          Guidance doc: `docs/specs/ilc_window_1124_1129_candidate_phase_grouping_v0.1.md`.

`window_1124_1129_sequence_lock_committed_phase_1124`

---

## Phase Table (Locked)

| Order | Phase | Topic | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 1124 | Window sequence lock (this document) | Foundation | NON-SENSITIVE |
| 2 | 1125 | CDL-084 Q2 amendment prelock hardening | Constitutional | NON-SENSITIVE |
| 3 | 1126 | CDL-084 Q2 ratification: `PROVENANCE_DECAY_ALPHA` -> `Decimal("0.45")` | Constitutional / Runtime | **SENSITIVE** |
| 4 | 1127 | Amendment evidence tests | Constitutional | NON-SENSITIVE |
| 5 | 1128 | Coherence report + capsule v5.37 | Synthesis | NON-SENSITIVE |
| 6 | 1129 | Window 1124–1129 closure gate | Gate | **SENSITIVE** |

---

## Sequencing Constraints (Locked)

1. Phase 1124 (seq lock) must precede all other phases — this document.
2. Phase 1125 (prelock) must precede Phase 1126 (ratification). The prelock grep must
   document all hardcoded-value test sites before any mutation executes.
3. Phase 1126 Commit 1 (runtime: `ilc_core/types.py` + version bump + test updates) must
   precede Phase 1126 Commit 2 (CDL doc: CDL-084 Q2 row + CDL log). The pre-commit hook
   enforces no `ilc_core/` changes in Commit 2.
4. Phase 1127 (evidence tests) must follow Phase 1126 (ratification complete).
5. Phases 1124–1128 must all precede Phase 1129 (closure gate).

---

## CDL-084 Q2 Amendment Scope (Locked)

| Item | Locked value |
|------|--------------|
| Old constant | `PROVENANCE_DECAY_ALPHA: Decimal = Decimal("0.5")` (provisional) |
| New constant | `PROVENANCE_DECAY_ALPHA: Decimal = Decimal("0.45")` (locked Phase 1126) |
| Old Q2 token | `q2_geometric_decay_alpha_decimal_0_5_provisional` |
| New Q2 token | `q2_geometric_decay_alpha_decimal_0_45_locked` |
| Runtime version | `epoch_attribution_settle_runtime_1126.v0.4` |
| SIM evidence | Run 01 (Phase 1120): α=0.45 keep; α=0.50 fail (drift 0.2065). Run 02 (Phase 1121): α=0.45 keep rate 3/3; α=0.50 keep rate 2/3. |
| Amendment target | CDL-084 Q2 row in `docs/specs/ilc_cdl_084_provenance_chain_attribution_opening_1111_v0.1.md` |
| CDL log target | `docs/specs/ilc_constitutional_decision_log_v0.1.md` CDL-084 row |
| `PROVENANCE_MAX_DEPTH` | Unchanged — remains `3` |
| `REUSE_ATTRIBUTION_RATE` | Unchanged — remains `Decimal("0.20")` |

---

## Phantom Edit Risk (Locked)

The constant change from `Decimal("0.5")` to `Decimal("0.45")` alters live PROVENANCE
payout arithmetic. Any test asserting payout values computed from the live constant will
break. The three-hop payout changes are:

| Hop | Old (α=0.50) | New (α=0.45) |
|-----|--------------|--------------|
| 1 | `Decimal("0.10")` | `Decimal("0.09")` |
| 2 | `Decimal("0.05")` | `Decimal("0.0405")` |
| 3 | `Decimal("0.025")` | `Decimal("0.018225")` |

Phase 1125 prelock grep must identify all affected test sites before Phase 1126 executes.
Phase 1126 Commit 1 must update all affected tests in the same commit as the constant
change.

---

## Sensitivity Classification

**SENSITIVE — requires human GO token:**

- Phase 1126 — CDL-084 Q2 ratification and runtime constant mutation.
- Phase 1129 — closure gate.

**NON-SENSITIVE:**

- Phase 1124 — sequence lock.
- Phase 1125 — prelock hardening and grep audit.
- Phase 1127 — amendment evidence tests.
- Phase 1128 — coherence report + capsule v5.37.

No new CDL opens in this window. CDL-085 remains unassigned.

---

## What This Window Does Not Do

- Does not change `PROVENANCE_MAX_DEPTH`.
- Does not change `REUSE_ATTRIBUTION_RATE`.
- Does not alter the PROVENANCE settlement algorithm beyond the alpha constant and runtime
  version bump.
- Does not authorize SIM-SPECTRAL-02, SIM-ECU-STABILITY-01, Conley research, star expansion,
  ADR-0035 implementation CDL, or Werner phi-bound CDL.

---

`window_1124_1129_sequence_lock_committed_phase_1124`
`cdl_084_q2_amendment_prelock_precedes_ratification`
`cdl_084_q2_alpha_0_45_locked_pending_phase_1126`
