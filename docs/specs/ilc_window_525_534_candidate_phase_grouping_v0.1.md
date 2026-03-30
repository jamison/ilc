# ILC Window 525-534 Candidate Phase Grouping v0.1

Status: candidate phase grouping — awaiting sequence lock
Date: 2026-03-30
Owner lane: G8 Constitution Cluster A

This document supersedes any informal carry-forward notes from Window 515-524.
The Phase 525 sequence lock will canonicalize and may amend this grouping.

---

## 1. Window purpose

Window 525-534 implements the ADR-0023 quality signal simulation evidence chain and advances
CDL-059 (aesthetic panel governance) to a constitutional opening decision. If Phase 528 produces
`cdl_059_opening_authorized`, the window continues through the CDL-059 full lifecycle
(opening -> prelock -> ratification -> runtime). If Phase 528 produces
`cdl_059_opening_deferred`, the window closes honestly on a blocked carry-forward path without
executing Phases 529-532. Three dedicated simulation phases build the constitutional evidence
base: SIM-AESTHETIC-01 validates diversity-maximizing panel composition, SIM-CENTRALITY-01
validates incremental use centrality convergence and ECU stability, and SIM-NOVELTY-01
calibrates novelty bonus parameters. A synthesis phase (528) combines the simulation evidence
and produces the CDL-059 opening authorization gate.

Two primary deliverables:
1. Three simulation documents establishing the constitutional evidence chain for CDL-059
   (SIM-AESTHETIC-01, SIM-CENTRALITY-01, SIM-NOVELTY-01), and
2. Conditional CDL-059 aesthetic panel governance lifecycle on the authorized path
   (synthesis gate -> opening -> prelock -> ratification -> runtime in `ilc_core/epistemic/`).

CDL-036 gossip schema amendment (centrality_delta message type) and passive ECU attribution
formula are Window 535+ items — they require CDL-059 to be ratified first and are
explicitly deferred from this window.

---

## 2. Carry-forward inputs (from Window 515-524)

| Item | Source | Window 525-534 action |
|---|---|---|
| ADR-0023 quality signal architecture (research guidance) | Phase 522 scoping (`adr_0023_remains_research_guidance`) | simulation evidence chain Phases 526-528 |
| CDL-059 opening: Window 525+ carry-forward | Phase 524 handoff | Phases 528-531 |
| CDL-053 reserved and separate | Capsule v2.5 | protected throughout window |
| CDL-036 gossip schema amendment deferred | Phase 524 handoff + ADR-0023 §4 | Window 535+ |
| Layer 3 reuse-centrality runtime (CDL-052) | `ilc_core/epistemic/reuse_centrality_runtime.py` | unchanged; CDL-059 Layer 2 is additive |

---

## 3. CDL status at window entry

| CDL | Status | Action |
|---|---|---|
| CDL-055 | ratified (Phase 496) | consumed by Phase 532 dep chain |
| CDL-056 | ratified (Phase 501) | unchanged |
| CDL-057 | ratified (Phase 511) | unchanged |
| CDL-058 | ratified (Phase 520) | consumed by Phase 532 dep chain |
| CDL-059 (aesthetic panel governance) | not yet opened | synthesis gate Phase 528 -> open Phase 529 only if authorized |
| CDL-053 | reserved (unopened) | protected throughout window |

---

## 4. Phase map

### Phase 525 — Sequence lock and carry-forward intake (NON-SENSITIVE)

Deliverables:
- `docs/specs/ilc_phase_525_534_sequence_lock_v0.1.md`

Scope:
- Freeze 10-phase program for Window 525-534.
- Authorize SIM-AESTHETIC-01 in Phase 526.
- State CDL-059 opening requires simulation synthesis with `cdl_059_opening_authorized` in Phase 528.
- State CDL-053 reserved throughout window.
- State CDL-036 gossip schema amendment deferred to Window 535+.
- No CDL mutation. No ilc_core/ mutation.

Required tokens in sequence lock:
- `SIM-AESTHETIC-01 is required before CDL-059 can be opened.`
- `CDL-059 opening requires Phase 528 synthesis authorization gate.`
- `CDL-053 remains reserved and unopened throughout Window 525-534.`
- `CDL-036 gossip schema amendment is a Window 535+ carry-forward.`
- `Phase 534 is the closure gate.`

---

### Phase 526 — SIM-AESTHETIC-01: aesthetic panel composition validation (NON-SENSITIVE)

Deliverables:
- `docs/specs/ilc_sim_aesthetic_01_panel_composition_526_v0.1.md`
- `tests/test_phase_526_sim_aesthetic_01_panel_composition.py`

Scope:
- Validates diversity-maximizing panel composition for Register 2 expressive content evaluation.
- Evidence base: Scott Page Diversity Prediction Theorem, preferential vs. veritative aggregation,
  digital-agent ecosystem composition considerations.
- Output must contain `sim_aesthetic_01_sufficient` (Phase 527 entry criterion).
- Output must contain `diversity_prediction_theorem` and `layer_2_informational_only` governance tokens.
- No CDL mutation. No ilc_core/ mutation.
- Test count: 7 tests.

---

### Phase 527 — SIM-CENTRALITY-01 + SIM-NOVELTY-01: convergence and calibration (NON-SENSITIVE)

Deliverables:
- `docs/specs/ilc_sim_centrality_01_and_novelty_01_calibration_527_v0.1.md`
- `tests/test_phase_527_sim_centrality_01_and_novelty_01.py`

Scope:
- SIM-CENTRALITY-01: validates incremental distributed eigenvector centrality convergence and
  ECU stability; produces `recommended_u_floor` constant (use-centrality floor for attribution).
- SIM-NOVELTY-01: calibrates novelty bonus parameters `recommended_alpha` and `recommended_beta`
  (discovery weight formula: `alpha * aesthetic_score + beta * (1 / (1 + centrality))`);
  also produces `recommended_gamma` (quality factor scaling, v1 target ~0.15).
- Output must contain `sim_centrality_01_sufficient` and `sim_novelty_01_sufficient`.
- Entry criteria require `sim_aesthetic_01_sufficient` in Phase 526 document.
- No CDL mutation. No ilc_core/ mutation.
- Test count: 7 tests.

---

### Phase 528 — ADR-0023 simulation synthesis and CDL-059 opening gate (NON-SENSITIVE)

Deliverables:
- `docs/specs/ilc_adr_0023_simulation_synthesis_528_v0.1.md`
- `tests/test_phase_528_adr_0023_simulation_synthesis.py`

Scope:
- Synthesizes SIM-AESTHETIC-01, SIM-CENTRALITY-01, and SIM-NOVELTY-01 into a unified CDL-059
  opening authorization assessment.
- Output: exactly one of `cdl_059_opening_authorized` OR `cdl_059_opening_deferred`.
- If `cdl_059_opening_authorized`: Section 4 must enumerate CDL-059 opening scope and required
  governance tokens for Phase 529.
- If `cdl_059_opening_deferred`: Section 4 must state the blocking criterion and carry-forward plan.
- No CDL mutation. No ilc_core/ mutation.
- Test count: 7 tests.

---

### Phase 529 — CDL-059 aesthetic panel governance opening (SENSITIVE — CDL mutation)

Deliverables:
- `docs/specs/ilc_cdl_059_aesthetic_panel_governance_opening_stub_529_v0.1.md`
- `tests/test_phase_529_cdl_059_opening_stub.py`
- historicalization patches to `tests/test_phase_525_sequence_lock_and_carry_forward_intake.py`,
  `tests/test_phase_522_adr_0023_cdl_scoping_analysis.py`, and
  `tests/test_phase_523_coherence_report_and_capsule_v2_5.py`
- CDL log mutation (additive CDL-059 row only)

Scope:
- Opens CDL-059 (aesthetic panel governance) using Phase 528 synthesis authorization.
- Entry criteria require `cdl_059_opening_authorized` in Phase 528 synthesis document.
- Selected option: diversity-maximizing aesthetic panel for Register 2 expressive content,
  informational only (no blocking authority).
- Must patch Phase 522, Phase 523, and Phase 525 tests to historicalize CDL-059 absent assertions.
- Pre-commit split: 5 passed / 2 failed. Post-commit: 7 passed.
- Skipped entirely if Phase 528 outputs `cdl_059_opening_deferred`.

---

### Phase 530 — CDL-059 prelock hardening (NON-SENSITIVE)

Deliverables:
- `docs/specs/ilc_cdl_059_aesthetic_panel_governance_prelock_hardening_530_v0.1.md`
- `tests/test_phase_530_cdl_059_prelock_hardening.py`

Scope:
- Hardens the CDL-059 lane against scope creep.
- Patches Phase 529 test to use historical CDL-059 open-state read (via commit-anchored git show).
- Locks: diversity-maximizing composition, Layer 2 informational-only status, CDL-V7/ADM-001
  orthogonality, CDL-052 Layer 3 orthogonality.
- Rejected scope expansions: blocking authority, CDL-036 gossip schema amendment, passive ECU
  attribution formula, multi-hop centrality in v1.
- No CDL mutation in Phase 530.
- Pre-commit split: 5 passed / 2 failed. Post-commit: 7 passed.
- Executes only on the authorized path after Phase 529 opens CDL-059.

---

### Phase 531 — CDL-059 ratification (SENSITIVE — CDL mutation)

Deliverables:
- `docs/specs/ilc_cdl_059_aesthetic_panel_governance_ratification_evidence_531_v0.1.md`
- `tests/test_phase_531_cdl_059_ratification_evidence.py`
- historicalization patch to `tests/test_phase_530_cdl_059_prelock_hardening.py`
- CDL log mutation (CDL-059 only: open → ratified)

Scope:
- Ratifies CDL-059 per evidence ladder anchored to SIM-AESTHETIC-01.
- CDL-059 moves `open → ratified`.
- Evidence section 6 heading: `## 6. Section-5 ratification readiness evidence checklist satisfaction`
- Governance tokens: `cdl_059_governs_aesthetic_panel_governance`, `layer_2_informational_only`,
  `cdl_v7_7_plus_1_panel_orthogonal`, `cdl_052_layer_3_orthogonal`, `cdl_053_reserved`,
  `sim_aesthetic_01_evidence_anchored`.
- CDL mutation: `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=531`.
- Pre-commit split: 5 passed / 2 failed. Post-commit: 7 passed.
- Executes only on the authorized path after Phase 530.

---

### Phase 532 — CDL-059 aesthetic panel runtime (SENSITIVE — ilc_core/)

Deliverables:
- `ilc_core/epistemic/aesthetic_panel_runtime.py`
- `tests/test_phase_532_aesthetic_panel_runtime.py`

Scope:
- New module in existing `ilc_core/epistemic/` subpackage (additive only; all existing epistemic
  runtime modules must remain unchanged).
- Runtime module exports:
  - `AESTHETIC_PANEL_RUNTIME_VERSION = "aesthetic_panel_runtime_532.v0.1"`
  - `CDL_059_DEPENDENCY = "cdl_059_ratified_531.v0.1"`
  - `BLOCKING_AUTHORITY_ACTIVE = False` (constitutional boundary: Layer 2 is informational only)
  - `compose_aesthetic_panel(agent_pool, panel_size, seed=None)` → list of agent_ids selected
    by diversity-maximizing algorithm
  - `compute_aesthetic_score(votes)` → normalized float in `[0.0, 1.0]`
  - `format_transparency_label(score)` → dict with `panel_type` and `not_objective_truth: true`
  - `is_blocking_authority_active()` → always False (constitutional boundary assertion)
- `ilc_core/epistemic/` mutations only. No CDL mutation.
- CRITICAL: `is_blocking_authority_active()` must always return False; tested explicitly.
- CRITICAL: `format_transparency_label` must include `not_objective_truth: true` in output.
- Test count: 12 tests.
- Executes only on the authorized path after Phase 531 ratifies CDL-059.

---

### Phase 533 — Integration coherence report and capsule v2.6 (NON-SENSITIVE)

Deliverables:
- `docs/specs/ilc_integration_coherence_report_533_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v2.6.md`
- `tests/test_phase_533_coherence_report_and_capsule_v2_6.py`

Scope:
- Always executes. On the success path it covers ADR-0023 simulation evidence chain, CDL-059
  lifecycle, aesthetic panel runtime integration, CDL-036/passive-attribution deferral, and
  snapshot isolation. On the blocked path it records the Phase 528 deferral outcome, exact
  blocker list, and Window 535+ carry-forward obligations without claiming CDL-059 ratification
  or runtime delivery.
- Capsule v2.6 supersedes v2.5. §1 required text: "Window 525-534 remains active at Phase 533."
- CDL-059 state handling must reflect ratification status at Phase 533: `ratified` on the success
  path, `absent` on the blocked path.
- No CDL mutation. No ilc_core/ mutation.

---

### Phase 534 — Closure gate and handoff (SENSITIVE — gate + tests)

Deliverables:
- `tools/check_window_525_534_closure_gate_phase_534.sh`
- `docs/specs/ilc_window_525_534_handoff_534_v0.1.md`
- `tests/test_window_525_534_closure_gate_534.py`

Scope:
- 6-category gate: prompt_contract_validation, lane_contract_tests, cross_window_regression,
  mutation_canary, closure_gate_cli_contract, walkthrough_hygiene.
- Lane contract tests are scenario-aware:
  - success path: Phases 525-533 (9 tests)
  - blocked path: Phases 525-528 and Phase 533 only (6 tests)
- Cross-window regression: all prior closure gate tests from 307 through 524.
- Selftest chain must include `ILC_PHASE_524_GATE_SELFTEST=1` and `ILC_PHASE_514_GATE_SELFTEST=1`;
  verify by reading actual prior gate test files.
- Window states:
  - success_path: CDL-059 ratified + Phase 532 runtime implemented, CDL-053 absent
  - blocked_path: Phase 528 deferred CDL-059 opening, CDL-059 absent, Phase 532 runtime absent,
    CDL-053 absent
  - invalid: any mismatch between the Phase 528 synthesis disposition and the live CDL/runtime
    state (including `cdl_059_opening_authorized` without ratification/runtime, or deferred path
    with stray CDL-059/runtime artifacts)
- Snapshot isolation: `ILC_PHASE_534_SNAPSHOT_PATH` override; no canonical `out/monitoring/` mutation.

---

## 5. CDL mutation summary for Window 525-534

| Phase | CDL action |
|---|---|
| 525 | None |
| 526 | None |
| 527 | None |
| 528 | None |
| 529 | add new CDL-059 row (status: open) |
| 530 | None |
| 531 | CDL-059 status: open → ratified |
| 532 | None |
| 533 | None |
| 534 | None |

---

## 6. ilc_core/ mutation summary for Window 525-534

| Phase | ilc_core/ action |
|---|---|
| 525–531 | None |
| 532 | `ilc_core/epistemic/aesthetic_panel_runtime.py` (NEW, additive to existing epistemic subpackage) |
| 533–534 | None |

---

## 7. Protected boundaries

The following boundaries must remain intact throughout Window 525-534:

- CDL-053 reserved and unopened.
- CDL-036 gossip schema amendment deferred to Window 535+ (centrality_delta message type).
- Passive ECU attribution formula deferred to Window 535+ (requires CDL-059 ratification first).
- Multi-hop centrality deferred to Window 535+ (v1 explicit out-of-scope per ADR-0023).
- CDL-V3 diversity floor protections unchanged.
- 7+1 quorum ladder unchanged (CDL-V7 + ADM-001 unmodified).
- Layer 3 reuse-centrality runtime (`ilc_core/epistemic/reuse_centrality_runtime.py`) must not
  be modified by Phase 532.
- `ilc_core/epistemic/__init__.py` must not be modified by Phase 532.
- Blocking authority for aesthetic panel (Layer 2) remains inactive: `BLOCKING_AUTHORITY_ACTIVE = False`.
- ADR-0022 private/gated boundary remains separate from quality signal work.

---

## 8. Predecessor references

- `docs/specs/ilc_window_515_524_handoff_524_v0.1.md` — Window 515-524 closure (must exist before Phase 525)
- `docs/specs/ilc_antigravity_context_capsule_v2.5.md` — current capsule (superseded by v2.6 at Phase 533)
- `docs/specs/ilc_adr_0023_cdl_scoping_analysis_522_v0.1.md` — Phase 522 scoping (`adr_0023_remains_research_guidance`)
- `docs/adr/ADR_0023_Multi_Layer_Quality_Signal_Architecture.md` — ADR-0023 (design input for all simulation phases)
- `docs/research/ilc_quality_signal_architecture_design_note_v0.1.md` — ADR-0023 elaboration (SIM input)
- `ilc_core/epistemic/reuse_centrality_runtime.py` — existing Layer 3 implementation (CDL-052; orthogonal to CDL-059)
- `ilc_core/epistemic/novelty_check_runtime.py` — existing novelty infrastructure (informs SIM-NOVELTY-01)
