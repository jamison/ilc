# ILC Window 631-636 Candidate Phase Grouping v0.1

Status: candidate grouping
Date: 2026-04-13
Owner lane: G8 tier-0 economic numeric determinism strike force
Classification: planning surface — not canonical law until sequence lock is committed

`window_631_636_candidate_grouping_v0_1`

## 1. Window identity and basis

Window 631-636 is the Tier-0 Economic Numeric Determinism strike-force window.
Its purpose is to:
- inventory and classify exact-numeric risk in runtime-critical economic and
  staking surfaces,
- open and ratify a narrow constitutional vehicle for exact numeric
  representation,
- migrate the Tier-0 runtime surfaces away from float-based accounting,
- harden that migration before returning priority to the broader public runtime
  lane.

This window is recommended as a bounded precondition lane before broader
participant-facing runtime widening proceeds. It does not select `Option B`,
does not open `CDL-062`, and does not replace the long-run sovereign-substrate
work.

**Authorization basis:**
- Human direction 2026-04-13: repo-wide float usage in economic, ledger, and
  staking runtime is treated as an active architectural defect rather than
  distant cleanup.
- Post-630 audit finding: the active-layer runtime defect was fixable locally,
  but the deeper numeric problem is repo-wide and affects Tier-0 runtime
  surfaces beyond Phase 628.
- Window 624-630 closed the bounded internal economic-agency lane successfully,
  but left broader runtime-critical float usage intact.
- Phase 619 and capsule v3.4 still keep Window 623+ as the named highest-
  priority continuation; this packet proposes a narrow, explicit reprioritizing
  strike-force lane to remove an exact-arithmetic blocker before that broader
  runtime closure is attempted.

`window_631_636_reprioritization_requires_human_lock`

## 2. Tier-0 scope

This window targets Tier-0 runtime-critical numeric surfaces only:
- `ilc_core/ledger/`
- `ilc_core/rc/economic_cycle_runtime.py`
- `ilc_core/validator/staking_liveness_runtime.py`
- `ilc_core/types.py`
- directly coupled DTO/export/runtime files required to keep those surfaces
  coherent

This window does **not** attempt full repo-wide float removal. The following are
explicitly out of initial strike-force scope unless required for direct Tier-0
coherence:
- simulation suites
- analytics and KPI helpers
- research utilities
- public runtime/interface closure beyond the exact-numeric boundary itself

## 3. Phase map

### Phase 631 — Window 631-636 Sequence Lock (SENSITIVE)

**Type:** SENSITIVE — sequence lock  
**Primary output:** `docs/specs/ilc_phase_631_636_sequence_lock_v0.1.md`

**Mission:** Lock the numeric-determinism strike-force lane, define Tier-0
scope, confirm that float-retention is not an acceptable outcome for these
runtime surfaces, and declare the new constitutional vehicle.

---

### Phase 632 — Tier-0 Numeric Surface Inventory + CDL-064 Opening Stub

**Type:** Non-sensitive  
**Primary outputs:**
- `docs/specs/ilc_tier0_numeric_surface_inventory_and_risk_classification_632_v0.1.md`
- CDL-064 opening stub row in `docs/specs/ilc_constitutional_decision_log_v0.1.md`

**Mission:** Produce a complete Tier-0 inventory of float-bearing runtime
surfaces, classify them by risk, and open CDL-064 as the constitutional vehicle
for exact economic numeric representation.

---

### Phase 633 — CDL-064 Prelock + SIM-NUMERIC-01

**Type:** Non-sensitive  
**Primary outputs:**
- `docs/specs/ilc_cdl_064_exact_numeric_representation_prelock_633_v0.1.md`
- `docs/specs/ilc_sim_numeric_01_representation_evaluation_633_v0.1.md`
- `tests/test_phase_633_cdl_064_exact_numeric_representation_prelock.py`

**Mission:** Evaluate representation options, harden the selected direction into
prelock form, and define migration invariants for Tier-0 runtime.

---

### Phase 634 — CDL-064 Ratification Evidence

**Type:** Non-sensitive  
**Primary outputs:**
- `docs/specs/ilc_cdl_064_exact_numeric_representation_ratification_evidence_634_v0.1.md`
- `tests/test_phase_634_cdl_064_exact_numeric_representation_ratification.py`
- CDL-064 row updated from `status: open` to `status: ratified`

**Mission:** Ratify the exact-numeric contract for Tier-0 economic and staking
surfaces.

---

### Phase 635 — Tier-0 Runtime Migration Implementation

**Type:** Runtime strike-force implementation  
**Primary outputs:**
- `docs/specs/ilc_tier0_exact_numeric_runtime_migration_635_v0.1.md`
- `tests/test_phase_635_tier0_exact_numeric_runtime_migration.py`
- implementation changes under the Tier-0 runtime-critical surface set

**Mission:** Implement the ratified exact-numeric contract across Tier-0
runtime-bearing ledger, settlement, RC economic-cycle, staking, and direct type
surfaces.

---

### Phase 636 — Tier-0 Numeric Hardening Gate + Window Closure

**Type:** Runtime hardening / coherence / closure  
**Primary outputs:**
- `docs/specs/ilc_tier0_numeric_hardening_and_window_631_636_closure_636_v0.1.md`
- `tests/test_phase_636_tier0_numeric_hardening_and_closure.py`
- `tests/test_tier0_numeric_hardening.py`
- `tools/run_window_631_636_numeric_determinism_gate_phase_636.sh`
- `docs/specs/ilc_antigravity_context_capsule_v3.5.md`
- `docs/specs/ilc_window_631_636_handoff_636_v0.1.md`

**Mission:** Run the hardening gate, confirm exact-arithmetic invariants across
the migrated Tier-0 runtime, record the carry-forward, and close the window.

## 4. Window-level constraints

All phases share:
- No `CDL-062` opening
- No `Option B` selection claim
- No wallet-write widening or ILC transferability
- No generalized ECU transfer widening beyond already-ratified bounded active
  layer semantics
- No simulation/analysis-wide float cleanup in this window unless directly
  required for Tier-0 runtime coherence
- Decision-log mutation limited to the `CDL-064` row only

## 5. CDL-064 constitutional scope boundary

**Proposed CDL-064 scope:**
- exact numeric representation for Tier-0 economic, ledger, staking, and direct
  settlement-bearing runtime surfaces
- exact arithmetic and replay invariants
- canonical serialization rule for exact numeric values
- migration compatibility requirements

**Explicitly out of scope for CDL-064:**
- sovereign substrate selection
- `Option B` graduation
- wallet widening
- external purchasing power
- generalized ECU transfer
- public runtime/interface closure outside the exact-numeric boundary

## 6. AG-gate preview

| Gate | Preview | Notes |
|---|---|---|
| AG-1 Co-flourishing mission | advance | Exact arithmetic reduces the risk of silently invalid economic treatment of agents and humans. |
| AG-2 W_e increase | neutral | This is enabling infrastructure rather than direct productivity expansion. |
| AG-3 Epistemic integrity | pass | No Popperian bypass or settled-graph mutation introduced. |
| AG-4 ECU-ILC separation | pass (critical) | The window tightens numeric exactness without collapsing ECU into ILC. |
| AG-5 Harness-agnostic | pass | Numeric representation is protocol/runtime-side, not harness-owned. |
| AG-6 Near-infinite scale | pass | Deterministic exact arithmetic is a prerequisite for scale-safe economic runtime. |
| AG-7 Machine-legible first | advance | Canonical exact serialization should improve machine replay and auditability. |
| AG-8 Outbound economic loop | neutral | The loop remains active from Window 624-630; this window hardens its numeric foundation rather than widening semantics. |

## 7. Relationship to Window 623+

Current canon still records Window 623+ as the named highest-priority
continuation. This packet does not rewrite that canon by itself.

Instead, Window 631-636 is proposed as a bounded corrective strike-force lane:
- if activated by human lock, it should run before or immediately adjacent to
  the broader MVP public runtime/interface closure,
- once closed, the MVP runtime lane should resume on an exact-numeric Tier-0
  foundation rather than on float-based settlement primitives.
