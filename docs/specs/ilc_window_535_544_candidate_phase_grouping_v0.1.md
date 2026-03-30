# ILC Window 535-544 Candidate Phase Grouping v0.1

Status: candidate phase grouping — awaiting sequence lock
Date: 2026-03-30
Owner lane: G8 Constitution Cluster A

This document supersedes any informal carry-forward notes from Window 525-534.
The Phase 535 sequence lock will canonicalize and may amend this grouping.

---

## 1. Window purpose

Window 535-544 advances two carry-forward lanes from Window 525-534:

**Primary lane**: CDL-036 gossip schema extension via a new CDL-060 row governing the
`centrality_delta` gossip message type for single-hop direct-use centrality propagation.
CDL-060 cites CDL-036 and CDL-039 as related clauses and must preserve CDL-039 topology
privacy constraints throughout its design, prelock, and ratification.

**Secondary lane**: CDL-052 Mode 3 reuse-centrality runtime advancement — replacing the
`reuse_centrality_runtime.py` stub with an algorithm implementing Phase 527 calibration
constants (u_floor=0.05, alpha=0.60, beta=0.40, gamma=0.15) for single-hop direct-use
centrality computation.

**Evidence lanes**: SIM-CENTRALITY-02 (Phase 538) calibrates gossip propagation parameters
required before CDL-060 can be opened. SIM-PASSIVE-ECU-01 (Phase 542) calibrates the
passive ECU attribution formula (ADR-0023 §Layer 3 economic model), which is a Window 535+
carry-forward independent of CDL-060 ratification.

Three deliverables remain out of window scope:
1. CDL-060 gossip runtime (`ilc_core/network/` extension for centrality_delta message type)
   — Window 545+ carry-forward.
2. Multi-hop centrality (SIM-MULTI-HOP-01) — Window 545+ carry-forward.
3. CDL-053 remains reserved and unopened throughout this window.

---

## 2. Carry-forward inputs (from Window 525-534)

| Item | Source | Window 535-544 action |
|---|---|---|
| CDL-036 gossip schema amendment (centrality_delta) | Phase 534 handoff | CDL-060 lifecycle Phases 538-541 |
| Passive ECU attribution formula | Phase 534 handoff | SIM-PASSIVE-ECU-01 Phase 542 |
| Multi-hop centrality (SIM-MULTI-HOP-01) | Phase 534 handoff | Window 545+ carry-forward |
| CDL-052 reuse-centrality runtime stub | `ilc_core/epistemic/reuse_centrality_runtime.py` | Phase 537 stub→algorithm |
| Phase 527 calibration constants | `ilc_sim_centrality_01_and_novelty_01_calibration_527_v0.1.md` | consumed by Phase 537 |
| CDL-039 topology privacy | CDL-039 ratified (Phase 379) | CDL-060 design must preserve |
| CDL-053 reserved and separate | Capsule v2.6 | protected throughout window |

---

## 3. CDL status at window entry

| CDL | Status | Action |
|---|---|---|
| CDL-036 | ratified (Phase 351) | CDL-060 cites this as related_clause |
| CDL-039 | ratified (Phase 379) | CDL-060 must preserve topology privacy |
| CDL-052 | ratified (Phase 466) | Mode 3 runtime advanced in Phase 537 |
| CDL-059 | ratified (Phase 531) | consumed by Phase 537 dep chain |
| CDL-060 (centrality_delta gossip) | not yet opened | CDL-036 scoping Phase 536 → open Phase 539 only after SIM-CENTRALITY-02 |
| CDL-053 | reserved (unopened) | protected throughout window |

---

## 4. Phase map

### Phase 535 — Sequence lock and carry-forward intake (NON-SENSITIVE)

Deliverables:
- `docs/specs/ilc_phase_535_544_sequence_lock_v0.1.md`

Scope:
- Freeze 10-phase program for Window 535-544.
- Authorize CDL-036 gossip scoping analysis and CDL-039 privacy analysis in Phase 536.
- State that CDL-060 opening requires SIM-CENTRALITY-02 completion with
  `sim_centrality_02_sufficient` in Phase 538.
- State Phase 537 reuse centrality runtime advancement is authorized.
- State CDL-053 reserved throughout window.
- State CDL-060 gossip runtime is a Window 545+ carry-forward.
- No CDL mutation. No ilc_core/ mutation.

Required tokens in sequence lock:
- `SIM-CENTRALITY-02 is required before CDL-060 can be opened.`
- `CDL-060 opening requires Phase 538 simulation calibration gate.`
- `CDL-053 remains reserved and unopened throughout Window 535-544.`
- `CDL-060 gossip runtime is a Window 545+ carry-forward.`
- `Phase 544 is the closure gate.`
- `multi_hop_centrality_deferred`

---

### Phase 536 — CDL-060 gossip extension scoping and CDL-039 privacy analysis (NON-SENSITIVE)

Deliverables:
- `docs/specs/ilc_cdl_060_gossip_centrality_extension_scoping_536_v0.1.md`

Scope:
- Analyze the CDL-036 gossip schema amendment requirement for `centrality_delta` message type.
- Analyze CDL-039 topology privacy constraints as they apply to gossip-propagated centrality
  scores (cluster membership must not be inferrable from centrality_delta messages).
- Produce design requirements for CDL-060 (gossip message type, fanout bounds, opaque channel
  compliance, single-hop scope).
- Output must contain `cdl_060_scoping_complete` token (Phase 538 entry criterion).
- Output must contain `cdl_039_privacy_analysis_complete` token.
- No CDL mutation. No ilc_core/ mutation.
- Test count: 7 tests.

---

### Phase 537 — Reuse centrality runtime stub→algorithm (SENSITIVE — ilc_core/)

Deliverables:
- `ilc_core/epistemic/reuse_centrality_runtime.py` (stub→algorithm, additive and backward-compatible)
- `tests/test_phase_537_reuse_centrality_runtime_algorithm.py`

Scope:
- Replace `computation_backend="stub_deferred"` with `computation_backend="incremental_direct_use_v1"`.
- Add exports: `REUSE_CENTRALITY_RUNTIME_VERSION = "reuse_centrality_runtime_537.v0.1"`,
  `CDL_052_DEPENDENCY = "cdl_052_ratified_466.v0.1"`, `U_FLOOR = 0.05`,
  `COMPUTATION_BACKEND_V1 = "incremental_direct_use_v1"`.
- Implement direct-use centrality computation: `query` dict may contain optional `usage_data`
  key `{"direct_use_count": int, "total_pool_size": int}`; apply u_floor clamp.
- Patch Phase 478 test `test_reuse_centrality_query_returns_stub_backend` to historicalize
  the `stub_deferred` assertion.
- `ilc_core/epistemic/reuse_centrality_runtime.py` mutations only; `__init__.py` unchanged.
- CRITICAL: backward-compatible query signature; queries without `usage_data` return
  `centrality_score=0.0`.
- Test count: 12 tests (10+2 commit-anchored).
- Phase 537 commit touches exactly `{runtime_path, phase_478_test, test_path}` (3 paths).

---

### Phase 538 — SIM-CENTRALITY-02: gossip propagation calibration (NON-SENSITIVE)

Deliverables:
- `docs/specs/ilc_sim_centrality_02_gossip_propagation_calibration_538_v0.1.md`
- `tests/test_phase_538_sim_centrality_02_gossip_propagation.py`

Scope:
- Calibrates gossip propagation parameters for the `centrality_delta` message type:
  `recommended_fanout`, `recommended_convergence_epochs`, CDL-039 privacy budget compliance.
- Evidence base: gossip convergence theory, CDL-039 topology privacy constraints, single-hop
  scope from Phase 527.
- Output must contain `sim_centrality_02_sufficient` (Phase 539 entry criterion, CDL-060 gate).
- No CDL mutation. No ilc_core/ mutation.
- Test count: 7 tests.

---

### Phase 539 — CDL-060 gossip centrality extension opening (SENSITIVE — CDL mutation)

Deliverables:
- `docs/specs/ilc_cdl_060_gossip_centrality_extension_opening_stub_539_v0.1.md`
- `tests/test_phase_539_cdl_060_opening_stub.py`
- historicalization patches to `tests/test_phase_535_sequence_lock_and_carry_forward_intake.py`,
  `tests/test_phase_536_cdl_060_gossip_extension_scoping.py`, and
  `tests/test_phase_538_sim_centrality_02_gossip_propagation.py`
- CDL log mutation (additive CDL-060 row only)

Scope:
- Opens CDL-060 (gossip centrality extension) using Phase 538 calibration.
- Entry criteria require `sim_centrality_02_sufficient` in Phase 538 document.
- Selected option: centrality_delta gossip message type with CDL-039-compliant opaque channel
  and bounded fanout, single-hop scope.
- Must patch Phase 535, Phase 536, and Phase 538 tests to historicalize CDL-060 absent assertions.
- Pre-commit split: 5 passed / 2 failed. Post-commit: 7 passed.

---

### Phase 540 — CDL-060 prelock hardening (NON-SENSITIVE)

Deliverables:
- `docs/specs/ilc_cdl_060_gossip_centrality_extension_prelock_hardening_540_v0.1.md`
- `tests/test_phase_540_cdl_060_prelock_hardening.py`

Scope:
- Hardens CDL-060 lane against scope creep.
- Patches Phase 539 opening test to historicalize CDL-060 open-state read.
- Locks: single-hop scope, CDL-039 topology privacy compliance, bounded fanout, Layer 3
  (reuse centrality) orthogonality.
- Rejected scope expansions: multi-hop centrality, direct modification of CDL-036 row,
  CDL-039 topology relaxation, gossip runtime implementation (deferred to Window 545+).
- No CDL mutation in Phase 540.
- Pre-commit split: 5 passed / 2 failed. Post-commit: 7 passed.

---

### Phase 541 — CDL-060 ratification (SENSITIVE — CDL mutation)

Deliverables:
- `docs/specs/ilc_cdl_060_gossip_centrality_extension_ratification_evidence_541_v0.1.md`
- `tests/test_phase_541_cdl_060_ratification_evidence.py`
- historicalization patch to `tests/test_phase_540_cdl_060_prelock_hardening.py`
- CDL log mutation (CDL-060 only: open → ratified)

Scope:
- Ratifies CDL-060 per evidence ladder anchored to SIM-CENTRALITY-02 and Phase 536 scoping.
- CDL-060 moves `open → ratified`.
- Evidence section 6 heading: `## 6. Section-5 ratification readiness evidence checklist satisfaction`
- Governance tokens: `cdl_060_governs_centrality_delta_gossip`, `cdl_039_privacy_preserved`,
  `single_hop_scope_locked`, `cdl_036_related_clause`, `sim_centrality_02_evidence_anchored`.
- CDL mutation: `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=541`.
- Pre-commit split: 5 passed / 2 failed. Post-commit: 7 passed.

---

### Phase 542 — SIM-PASSIVE-ECU-01: passive ECU attribution formula calibration (NON-SENSITIVE)

Deliverables:
- `docs/specs/ilc_sim_passive_ecu_01_attribution_formula_calibration_542_v0.1.md`
- `tests/test_phase_542_sim_passive_ecu_01_attribution_formula.py`

Scope:
- Calibrates the passive ECU attribution formula for content re-use (ADR-0023 §Layer 3
  economic model).
- Produces `recommended_passive_attribution_rate`, `recommended_decay_floor`, and
  `recommended_attribution_cap` constants.
- Uses Phase 527 gamma=0.15 quality-factor map as an upstream input.
- Output must contain `sim_passive_ecu_01_sufficient` token (Window 545+ carry-forward anchor).
- No CDL mutation. No ilc_core/ mutation.
- Test count: 7 tests.

---

### Phase 543 — Integration coherence report and capsule v2.7 (NON-SENSITIVE)

Deliverables:
- `docs/specs/ilc_integration_coherence_report_543_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v2.7.md`
- `tests/test_phase_543_coherence_report_and_capsule_v2_7.py`

Scope:
- Covers CDL-060 full lifecycle (scoping → ratification), reuse centrality runtime
  advancement, SIM-CENTRALITY-02 evidence chain, SIM-PASSIVE-ECU-01 calibration,
  and Window 545+ carry-forwards.
- Capsule v2.7 supersedes v2.6.
- §1 required text: "Window 535-544 remains active at Phase 543."
- CDL-060 state must reflect `ratified` status.
- No CDL mutation. No ilc_core/ mutation.

---

### Phase 544 — Closure gate and handoff (SENSITIVE — gate + tests)

Deliverables:
- `tools/check_window_535_544_closure_gate_phase_544.sh`
- `docs/specs/ilc_window_535_544_handoff_544_v0.1.md`
- `tests/test_window_535_544_closure_gate_544.py`

Scope:
- 6-category gate: prompt_contract_validation, lane_contract_tests, cross_window_regression,
  mutation_canary, closure_gate_cli_contract, walkthrough_hygiene.
- Lane contract tests: all 9 phases (535-543) must pass.
- Cross-window regression: all prior closure gate tests from 307 through 534.
- Selftest chain must include `ILC_PHASE_534_GATE_SELFTEST=1` and all prior confirmed
  guards; verify by reading each prior gate test file.
- Snapshot isolation: `ILC_PHASE_544_SNAPSHOT_PATH` override; no canonical `out/monitoring/`
  mutation.

---

## 5. CDL mutation summary for Window 535-544

| Phase | CDL action |
|---|---|
| 535 | None |
| 536 | None |
| 537 | None |
| 538 | None |
| 539 | add new CDL-060 row (status: open) |
| 540 | None |
| 541 | CDL-060 status: open → ratified |
| 542 | None |
| 543 | None |
| 544 | None |

---

## 6. ilc_core/ mutation summary for Window 535-544

| Phase | ilc_core/ action |
|---|---|
| 535–536 | None |
| 537 | `ilc_core/epistemic/reuse_centrality_runtime.py` (stub→algorithm, existing file modified) |
| 538–544 | None |

---

## 7. Protected boundaries

The following boundaries must remain intact throughout Window 535-544:

- CDL-053 reserved and unopened.
- CDL-039 topology privacy: cluster membership must not be inferrable from any gossip message
  produced or described in this window.
- CDL-036 row must not be modified (CDL-060 is a new row that cites CDL-036 in related_clause).
- Multi-hop centrality deferred to Window 545+ (v1 explicit out-of-scope).
- CDL-060 gossip runtime (`ilc_core/network/` extension) deferred to Window 545+.
- `ilc_core/epistemic/__init__.py` must not be modified in Phase 537.
- No other `ilc_core/epistemic/` files may be modified in Phase 537.
- Passive ECU attribution formula implementation deferred to Window 545+ (SIM-PASSIVE-ECU-01
  calibration is evidence; runtime implementation is a separate future phase).
- CDL-V3 diversity floor protections unchanged.
- 7+1 quorum ladder unchanged (CDL-V7 + ADM-001 unmodified).
- Aesthetic panel runtime (`ilc_core/epistemic/aesthetic_panel_runtime.py`) must not be
  modified.

---

## 8. Predecessor references

- `docs/specs/ilc_window_525_534_handoff_534_v0.1.md` — Window 525-534 closure
- `docs/specs/ilc_antigravity_context_capsule_v2.6.md` — current capsule (superseded by v2.7 at Phase 543)
- `docs/specs/ilc_sim_centrality_01_and_novelty_01_calibration_527_v0.1.md` — Phase 527 calibration (u_floor=0.05, alpha=0.60, beta=0.40, gamma=0.15)
- `docs/adr/ADR_0023_Multi_Layer_Quality_Signal_Architecture.md` — ADR-0023 (design input for SIM-PASSIVE-ECU-01)
- `ilc_core/epistemic/reuse_centrality_runtime.py` — stub to be advanced in Phase 537
- `tests/test_phase_478_cdl_052_epistemic_runtime_part_2.py` — contains stub_deferred assertion requiring Phase 537 historicalization patch
- `docs/specs/ilc_constitutional_decision_log_v0.1.md` — CDL log (CDL-036, CDL-039, CDL-052, CDL-059 ratified; CDL-060 absent at entry)
