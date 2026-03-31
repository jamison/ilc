# ILC Window 545-554 Candidate Phase Grouping v0.1

Status: candidate phase grouping — awaiting sequence lock
Date: 2026-03-31
Owner lane: G8 Constitution Cluster A

This document supersedes the informal carry-forward notes in the Window 535-544 handoff.
The Phase 545 sequence lock will canonicalize and may amend this grouping.

---

## 1. Window purpose

Window 545-554 delivers the first runtime implementation tranche for the reuse-centrality
economic lane ratified in Window 535-544.

**Primary lane A**: CDL-060 gossip runtime — extends `ilc_core/network/d2d/` with a
`centrality_delta` message handler implementing the CDL-060-ratified single-hop bounded-fanout
gossip protocol. This runtime requires an epoch-boundary commit semantics decision before
implementation begins (see Phase 546).

**Primary lane B**: Passive ECU attribution runtime — implements the formula calibrated in
Phase 542 (`passive_attribution_rate=0.20`, `decay_floor=0.05`, `attribution_cap=0.15`).
Depends on CDL-060 gossip runtime being in place to supply `centrality_score` inputs.
Requires `attribution_cap` formula application semantics resolved at Phase 545 scoping.

**Research lane**: SIM-MULTI-HOP-01 — parallel evidence-gathering simulation for multi-hop
centrality. No CDL opening. Results feed Window 555+ planning only.

**Baseline verification obligation**: Phase 542 exact-value assertions are already present on
mainline. Phase 545 must verify and bind that baseline state rather than re-repair it.

---

## 2. Carry-forward inputs (from Window 535-544)

| Item | Source | Window 545-554 action |
|---|---|---|
| CDL-060 gossip runtime (`centrality_delta` over D2d) | Phase 544 handoff | Phases 548-549 implementation |
| Passive ECU attribution runtime | Phase 544 handoff | Phase 550 implementation |
| Epoch-boundary commit semantics | Phase 543 coherence report | Phase 546 scoping decision required FIRST |
| `attribution_cap` formula application semantics | Phase 542 audit | Phase 545 scoping obligation |
| Direct authorship reward baseline (authorship primacy proof) | Phase 542 audit | Phase 545 scoping obligation |
| `decay_floor >= u_floor` invariant documentation | Phase 544 handoff | Phase 545 scoping obligation |
| Signal-floor policy consistency | Phase 543 carry-forward | Phase 547 scoping (may produce ADR/CDL) |
| Multi-hop centrality (SIM-MULTI-HOP-01) | Phase 544 handoff | Phase 552 simulation (research only) |
| CDL-053 reserved and separate | Window 535-544 protected boundary | Preserved throughout |
| Phase 542 exact-value assertions present in baseline | `0ceb88c` / current mainline | Verify in Phase 545; no repair required |

---

## 3. CDL status at window entry

| CDL | Status | Window 545-554 action |
|---|---|---|
| CDL-036 | ratified (Phase 351) | No mutation; CDL-060 runtime cites this |
| CDL-039 | ratified (Phase 379) | No mutation; D2d gossip runtime must preserve |
| CDL-052 | ratified (Phase 466) | No mutation; dep chain consumed by reuse centrality runtime |
| CDL-059 | ratified (Phase 531) | No mutation; dep chain upstream |
| CDL-060 | ratified (Phase 541) | Gossip runtime authorized; no row mutation needed |
| CDL-053 | reserved (unopened) | Protected throughout window |
| CDL-061 | absent | No opening in Window 545-554 (no CDL-opening phase planned) |

Note: no new CDL rows are opened in this window. All runtime work proceeds under the existing
ratified CDL chain.

---

## 4. Phase map

### Phase 545 — Sequence lock, scoping obligations, and baseline verification (NON-SENSITIVE)

Deliverables:
- `docs/specs/ilc_phase_545_554_sequence_lock_v0.1.md`
- `tests/test_phase_545_sequence_lock_and_carry_forward_intake.py`

Scope:
- Freeze 10-phase program for Window 545-554.
- Document and bind the three Phase 542 scoping obligations carried forward:
  (a) `attribution_cap` formula application mechanism defined;
  (b) direct authorship reward baseline stated (authorship primacy proof made verifiable);
  (c) `decay_floor >= u_floor` invariant formally documented;
- Verify that Phase 542 exact-value assertions are already active in baseline.
- Authorize Phase 546 epoch-boundary commit semantics scoping.
- State CDL-060 gossip runtime implementation requires Phase 546 decision document first.
- State CDL-053 reserved throughout window.
- State SIM-MULTI-HOP-01 is Phase 552 research-only (no CDL opening from this simulation).
- No CDL mutation in Phase 545.

Phase 545 commit: single main commit touching the sequence lock and its new test only.

Required tokens in sequence lock:
- `epoch_boundary_commit_semantics_required_before_cdl_060_gossip_runtime`
- `passive_ecu_runtime_depends_on_cdl_060_gossip_runtime`
- `CDL-053 remains reserved and unopened throughout Window 545-554.`
- `Phase 554 is the closure gate.`
- `sim_multi_hop_01_deferred`
- `phase_542_exact_value_assertions_confirmed`

---

### Phase 546 — Epoch-boundary commit semantics decision (NON-SENSITIVE)

Deliverables:
- `docs/specs/ilc_epoch_boundary_commit_semantics_decision_546_v0.1.md`
- `tests/test_phase_546_epoch_boundary_commit_semantics.py`

Scope:
- Decide between two accumulation models for `centrality_delta` gossip messages:
  **Model A (write-through)**: each received message immediately updates the centrality score
  (simpler, more granular attribution, slightly more CDL-039 traffic correlation surface).
  **Model B (epoch-boundary atomic)**: messages accumulate in-memory per validation epoch;
  committed atomically at epoch boundary (XLA operator-fusion analog; better CDL-039 traffic
  privacy; more complex failure-recovery path).
- Analyze CDL-039 privacy implications of each model (topology correlation surface).
- Analyze failure-recovery semantics for each model under CDL-046 timed_out_lifecycle context.
- Produce `epoch_boundary_commit_semantics_decision` governance token with rationale.
- Output must state which model is selected and why.
- Produce `cdl_060_gossip_runtime_design_unblocked` token (Phase 548 entry criterion).
- No CDL mutation. No ilc_core/ mutation.
- Test count: 7 tests.

---

### Phase 547 — Signal-floor policy consistency scoping (NON-SENSITIVE)

Deliverables:
- `docs/specs/ilc_signal_floor_policy_consistency_scoping_547_v0.1.md`
- `tests/test_phase_547_signal_floor_policy_scoping.py`

Scope:
- Document all current ILC signal floors: `U_FLOOR=0.05` (reuse centrality), `recommended_decay_floor=0.05` (passive ECU), CDL-V1 temporal decay floor, CDL-V2 sybil resistance threshold.
- Determine whether a unified cross-metric floor governance framework is required (ADR or CDL),
  or whether per-domain documentation of the `decay_floor >= u_floor` invariant is sufficient.
- Produce one of two dispositions:
  (a) `signal_floor_governance_adm_only` — ADM-001 or ADR-0023 update sufficient; no new CDL.
  (b) `signal_floor_cdl_warranted` — opens a planning track for Window 555+ CDL opening.
- Produce `signal_floor_policy_scoped` token (closes dredge Idea C carry-forward).
- No CDL mutation. No ilc_core/ mutation.
- Test count: 7 tests.

---

### Phase 548 — CDL-060 gossip runtime implementation (SENSITIVE — ilc_core/)

Deliverables:
- `ilc_core/network/d2d/centrality_delta_gossip_runtime.py`
- `tests/test_phase_548_centrality_delta_gossip_runtime.py`

Entry criteria:
- `cdl_060_gossip_runtime_design_unblocked` in Phase 546 document.
- `epoch_boundary_commit_semantics_decision` governance token present in Phase 546 document.

Scope:
- Implement `centrality_delta` gossip message type under CDL-060 ratified lane.
- Extend `ilc_core/network/d2d/` — new file; must not modify `gossip.py`, `peer.py`, or `interface.py`.
- Constants required:
  `CDL_060_GOSSIP_RUNTIME_VERSION = "cdl_060_gossip_runtime_548.v0.1"`
  `CDL_060_DEPENDENCY = "cdl_060_ratified_541.v0.1"`
  `D2D_GOSSIP_DEPENDENCY = "d2d_gossip_382.v0.1"` (links to existing D2d dep chain)
- Runtime must enforce:
  (a) single-hop only (`hop_count` must equal 1);
  (b) bounded fanout (fanout <= `recommended_fanout=3` from Phase 538);
  (c) CDL-039 opaque channel (message must not expose cluster membership);
  (d) epoch-boundary accumulation model as decided in Phase 546.
- U_FLOOR enforcement: centrality scores below 0.05 must not propagate.
- Must import CDL-052 dep token from `reuse_centrality_runtime.py`.
- No CDL mutation. Forbidden ilc_core/ paths: `gossip.py`, `peer.py`, `interface.py`, and all
  non-D2d ilc_core/ packages (consensus/, security/, ledger/, issuance/, schema/, genesis/,
  epoch/, identity/, cli/).
- Test count: 12 tests (10+2 commit-anchored).
- Phase 548 commit touches exactly `{runtime_path, test_path}` (2 paths).

---

### Phase 549 — CDL-060 gossip runtime hardening and canary integration (SENSITIVE — ilc_core/)

Deliverables:
- `ilc_core/network/d2d/centrality_delta_gossip_runtime.py` (hardening patches)
- `tools/run_mutation_canary_phase_297.py` (new centrality-delta probes)
- `tests/test_phase_549_centrality_delta_gossip_runtime_hardening.py`

Scope:
- Add edge-case coverage: zero-centrality message suppression, fanout=3 exactly (boundary),
  hop_count=2 rejection, channel opacity enforcement, epoch-boundary rollover.
- Add canary integration: `tools/run_mutation_canary_phase_297.py` must catch mutations to
  CDL-060 version constant and D2d dependency constant.
- No CDL mutation. Same forbidden ilc_core/ paths as Phase 548; tools mutation limited to the
  mutation canary script.
- Test count: 8 tests.

---

### Phase 550 — Passive ECU attribution runtime implementation (SENSITIVE — ilc_core/)

Deliverables:
- `ilc_core/economics/passive_ecu_attribution_runtime.py`
- `tests/test_phase_550_passive_ecu_attribution_runtime.py`

Entry criteria:
- Phase 548 runtime passing (CDL-060 gossip runtime in place).
- `attribution_cap` formula application semantics confirmed in Phase 545 sequence lock.

Scope:
- Implement formula: `passive_ecu = min(base_reward * passive_attribution_rate * centrality_score * m_i, base_reward * attribution_cap)`
  where `m_i = 1 + gamma * (2*q_i - 1)`, `gamma=0.15`.
- Constants:
  `PASSIVE_ECU_ATTRIBUTION_RUNTIME_VERSION = "passive_ecu_attribution_runtime_550.v0.1"`
  `CDL_060_DEPENDENCY = "cdl_060_ratified_541.v0.1"`
  `PASSIVE_ATTRIBUTION_RATE = 0.20`
  `DECAY_FLOOR = 0.05`
  `ATTRIBUTION_CAP = 0.15`
  `GAMMA = 0.15`
- Must enforce zero-attribution for `centrality_score < DECAY_FLOOR`.
- Must enforce `passive_ecu <= base_reward * ATTRIBUTION_CAP` (cap applied at output layer).
- Must consume `CDL_060_GOSSIP_RUNTIME_VERSION` from Phase 548 as a dep token.
- No CDL mutation. Forbidden ilc_core/ paths: all non-economics packages plus CDL log.
- Test count: 12 tests (10+2 commit-anchored).

---

### Phase 551 — Passive ECU attribution runtime hardening (SENSITIVE — ilc_core/)

Deliverables:
- `ilc_core/economics/passive_ecu_attribution_runtime.py` (hardening)
- `tests/test_phase_551_passive_ecu_attribution_hardening.py`

Scope:
- Edge-case coverage: cap binding (highly-reused node capped at attribution_cap fraction),
  quality-factor extremes (q_i=0 and q_i=1), base_reward=0 case, authorship primacy proof
  (assert `passive_ecu < base_reward` for all valid inputs).
- No CDL mutation.
- Test count: 7 tests.

---

### Phase 552 — SIM-MULTI-HOP-01: multi-hop centrality simulation (NON-SENSITIVE)

Deliverables:
- `docs/specs/ilc_sim_multi_hop_01_centrality_calibration_552_v0.1.md`
- `tests/test_phase_552_sim_multi_hop_01_centrality.py`

Scope:
- Evidence-gathering simulation for multi-hop centrality propagation.
- Research track only: does not open a CDL, does not amend CDL-060.
- Key question: at what hop-depth does centrality signal become indistinguishable from noise
  (signal-to-noise ratio below 1.0)?
- Must produce `sim_multi_hop_01_sufficient` or `sim_multi_hop_01_insufficient` disposition.
- Output must state whether multi-hop CDL opening is warranted in Window 555+.
- No CDL mutation. No ilc_core/ mutation.
- Test count: 7 tests.

---

### Phase 553 — Integration coherence report and capsule v2.8 (NON-SENSITIVE)

Deliverables:
- `docs/specs/ilc_integration_coherence_report_553_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v2.8.md`
- `tests/test_phase_553_coherence_report_and_capsule_v2_8.py`

Scope:
- Covers CDL-060 gossip runtime, passive ECU attribution runtime, SIM-MULTI-HOP-01 disposition,
  signal-floor policy decision, and Window 555+ carry-forwards.
- Capsule v2.8 supersedes v2.7.
- No CDL mutation. No ilc_core/ mutation.

---

### Phase 554 — Closure gate and handoff (SENSITIVE — gate + tests)

Deliverables:
- `tools/check_window_545_554_closure_gate_phase_554.sh`
- `docs/specs/ilc_window_545_554_handoff_554_v0.1.md`
- `tests/test_window_545_554_closure_gate_554.py`

Scope:
- 6-category gate: prompt_contract_validation, lane_contract_tests, cross_window_regression,
  mutation_canary, closure_gate_cli_contract, walkthrough_hygiene.
- Lane contract tests: all 9 phases (545-553) must pass.
- Cross-window regression: all prior closure gate tests from 307 through 544.
- Selftest chain must include `ILC_PHASE_544_GATE_SELFTEST=1` and all prior confirmed guards.
- Snapshot isolation: `ILC_PHASE_554_SNAPSHOT_PATH` override; no canonical `out/monitoring/` mutation.

---

## 5. CDL mutation summary for Window 545-554

| Phase | CDL action |
|---|---|
| 545 | None (sequence lock + baseline verification only) |
| 546-554 | None (all runtime work proceeds under ratified CDL chain) |

No new CDL rows open in Window 545-554.

---

## 6. ilc_core/ mutation summary for Window 545-554

| Phase | ilc_core/ action |
|---|---|
| 545-547 | None |
| 548 | `ilc_core/network/d2d/centrality_delta_gossip_runtime.py` (new file) |
| 549 | `ilc_core/network/d2d/centrality_delta_gossip_runtime.py` (hardening) |
| 550 | `ilc_core/economics/passive_ecu_attribution_runtime.py` (new file) |
| 551 | `ilc_core/economics/passive_ecu_attribution_runtime.py` (hardening) |
| 552-554 | None |

---

## 7. Protected boundaries

The following boundaries must remain intact throughout Window 545-554:

- CDL-053 reserved and unopened.
- CDL-039 topology privacy: cluster membership must not be inferrable from `centrality_delta` messages.
- CDL-036 row must not be modified.
- CDL-060 row must not be modified (already ratified; no amendment needed).
- Multi-hop centrality: SIM-MULTI-HOP-01 is research only; no CDL opening within this window.
- `ilc_core/network/d2d/gossip.py`, `peer.py`, `interface.py` must not be modified.
- `ilc_core/epistemic/reuse_centrality_runtime.py` must not be modified (advanced in Phase 537).
- `ilc_core/epistemic/aesthetic_panel_runtime.py` must not be modified.
- CDL-V3 diversity floor protections unchanged.
- 7+1 quorum ladder unchanged.

---

## 8. Predecessor references

- `docs/specs/ilc_window_535_544_handoff_544_v0.1.md` — Window 535-544 closure
- `docs/specs/ilc_antigravity_context_capsule_v2.7.md` — current capsule at window entry
- `docs/specs/ilc_sim_passive_ecu_01_attribution_formula_calibration_542_v0.1.md` — calibrated constants
- `docs/specs/ilc_sim_centrality_02_gossip_propagation_calibration_538_v0.1.md` — gossip propagation calibration
- `docs/specs/ilc_cdl_060_gossip_centrality_extension_ratification_evidence_541_v0.1.md` — CDL-060 ratification
- `ilc_core/network/d2d/gossip.py` — D2d gossip surface (must not modify)
- `ilc_core/epistemic/reuse_centrality_runtime.py` — Phase 537 advanced runtime (must not modify)
- `tests/test_phase_542_sim_passive_ecu_01_attribution_formula.py` — baseline exact-value assertion reference
- `docs/adr/ADR_0023_Multi_Layer_Quality_Signal_Architecture.md` — Layer 3 economics basis
