# ILC Antigravity Context Capsule v5.36

Supersedes: docs/specs/ilc_antigravity_context_capsule_v5.35.md
Date: 2026-04-30
Owner lane: Window 1118–1123 — FLOAT-KILL-01 + SIM-PROVENANCE-01

`capsule_v5_36_supersedes_v5_35`
`window_1118_1123_phases_1118_1122_complete_pending_gate_1123`
`float_kill_01_complete_phase_1119`
`sim_provenance_01_complete_phase_1120_1121`
`provenance_decay_alpha_sim_recommendation_0_45_cdl_amendment_pending`

This capsule is self-contained.

---

## 1. Current Frontier State

Window 1118–1123 phases 1118–1122 are complete. Phase 1123 is the SENSITIVE closure gate
and requires an explicit human GO token.

| Phase | Key work |
|-------|----------|
| 1118 | Window 1118–1123 sequence lock: FLOAT-KILL-01 before SIM-PROVENANCE-01 |
| 1119 | FLOAT-KILL-01 runtime hardening: PRNG kill, Decimal ECU path, interface cleanup |
| 1120 | SIM-PROVENANCE-01 commissioning, Run 01, time-series output |
| 1121 | SIM-PROVENANCE-01 Run 02 fine sweep and alpha disposition evidence |
| 1122 | Coherence report + capsule v5.36 |

Current position: Phase 1122 complete, Phase 1123 closure gate next.

---

## 2. CDL Chain Status

No new CDL ratifications occurred in Window 1118–1123.

| CDL | Status | Phase | Note |
|-----|--------|-------|------|
| CDL-001 | Open (genesis_blocker) | — | Packaging track |
| CDL-042 | Ratified | 407 | CLI framework |
| CDL-052 | Ratified | 466 | Popperian gate |
| CDL-060 | Ratified | 541 | Centrality delta gossip |
| CDL-073 | Ratified | 860 | RC1 homoiconic bootstrap schema |
| CDL-074 | Ratified | 870 | Truth primitive runtime |
| CDL-075 | Ratified | 884 | Truth primitive graph persistence |
| CDL-076 | Ratified | 897 | Truth primitive announcement gossip (L1) |
| CDL-077 | Ratified | 904 | WANT-HAVE/WANT-BLOCK fetch (L2) |
| CDL-078 | Ratified | 911 | Relay incentive constitutional lock (L5) |
| CDL-079 | Ratified | 918 | HB-002 P2P bootstrap distribution protocol |
| CDL-080 | Ratified | 927 | star.map N-gram route index (L3) |
| CDL-081 | Ratified | 943 | Hyperedge ECU attribution (`REUSE_ATTRIBUTION_RATE = Decimal("0.20")`) |
| CDL-082 | Ratified | 950 | H-013 gossip beacon emission threshold amendment |
| CDL-083 | Ratified | 1105 | H-CON-02 panel quorum + REFUTATION attribution |
| CDL-084 | Ratified | 1113 | PROVENANCE chain attribution; SIM-PROVENANCE-01 complete; Q8 satisfied; Q2 active pending CDL amendment; SIM recommendation `α=0.45` |
| CDL-070 | Deferred | — | PQ migration |

Next fresh CDL number remains **CDL-085**. Werner phi-bound remains SIM-gated. ADR-0035
implementation CDL remains planning/authorization-gated.

---

## 3. Attribution Settlement Runtime Status

| Constant | Value | Phase |
|----------|-------|-------|
| `EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION` | `"epoch_attribution_settle_runtime_1114.v0.3"` | 1114 |
| `CDL_084_DEPENDENCY` | `"cdl_084_provenance_chain_attribution_ratified_1113.v0.1"` | 1113 |
| `CDL_084_TYPES_DEPENDENCY` | `"cdl_084_provenance_chain_attribution_ratified_1113.v0.1"` | 1113 |
| `PROVENANCE_DECAY_ALPHA` | `Decimal("0.5")` — provisional; SIM recommendation `α=0.45`; CDL amendment pending | 1113, unchanged |
| `PROVENANCE_MAX_DEPTH` | `3` (`int`) | pre-existing |

PROVENANCE attribution path remains active as of Phase 1114. ATTESTATION and EPOCH_BOUNDARY
remain silently ignored. REFUTATION attribution remains governed by CDL-083.

---

## 4. CDL-084 Decision Record

| Q | Decision | Token |
|---|----------|-------|
| Q1 | PROVENANCE triggers ECU; caller-only contract | `q1_provenance_triggers_ecu_caller_only_contract` |
| Q2 | Geometric decay; `PROVENANCE_DECAY_ALPHA = Decimal("0.5")`; provisional. SIM recommendation: `α=0.45`; CDL amendment required before lock. | `q2_geometric_decay_alpha_decimal_0_5_provisional` |
| Q3 | `PROVENANCE_MAX_DEPTH = 3`; hop 1 = immediate parent | `q3_max_depth_3_hop_1_is_immediate_parent` |
| Q4 | Ancestor creator receives ECU | `q4_ancestor_creator_receives_ecu` |
| Q5 | Fresh per-event state; `visited_creators` nearest-hop-wins | `q5_fresh_per_event_visited_creators_nearest_hop_wins` |
| Q6 | Explicit nearest-first chain payload; pure settle, no graph queries | `q6_explicit_chain_payload_nearest_first_pure_settle` |
| Q7 | Duplicate `node_id` raises; duplicate `creator_id` nearest-hop-wins | `q7_duplicate_node_id_raises_nearest_creator_wins` |
| Q8 | Epoch mint source; SIM-PROVENANCE-01 required before alpha locks. SATISFIED Phase 1121: Run 01 + Run 02 complete. | `q8_epoch_mint_source_sim_provenance_01_required` |
| Q9 | Float kill: `PROVENANCE_DECAY_ALPHA: float -> Decimal("0.5")` | `q9_float_kill_decimal_literal_0_5` |
| Q10 | `None` chain -> missing error; `()` chain -> empty error | `q10_none_raises_missing_empty_raises_empty` |

---

## 5. Forward Obligations and Deferred Items

| Item | Status | Gate / sequencing |
|------|--------|-------------------|
| **FLOAT-KILL-01** | **COMPLETE — Phase 1119** | 3 commits; FLOAT-KILL-02 not triggered; active runtime PRNG/Decimal hardening complete |
| **SIM-PROVENANCE-01** | **COMPLETE — Phases 1120–1121** | Run 01 coarse sweep + Run 02 fine sweep; `α=0.45` SIM recommendation; Q8 satisfied; Q2 remains active pending CDL amendment |
| **CDL-084 Q2 alpha amendment** | **Obligated — future window** | SENSITIVE phase required; human GO token; decide whether to adopt `α=0.45` SIM recommendation |
| **SIM-SPECTRAL-02** | Deferred — non-canonical research direction | Time-series data dependency satisfied (Phase 1120). Tests whether PROVENANCE reach correlates with Popperian durability. Not scheduled. |
| **SIM-ECU-STABILITY-01** | Candidate — not authorized | Carry forward unchanged; no current-window authorization |
| Werner phi-bound CDL (CDL-085 candidate) | Deferred — SIM evidence required before CDL can open | Carry forward |
| ADR-0035 implementation CDL | Deferred — direction accepted Phase 1100; no CDL vehicle yet | Planning/authorization gate remains |
| star expansion implementation | Deferred — CDL prerequisites satisfied (CDL-081, CDL-083) and SIM-REUSE-01 complete; implementation blocked on H-011 patent assessment, planning review, and explicit human authorization | Planning review before implementation CDL |
| SIM-HYPEREDGE-01 gate | CDL-083 ratified; SIM can now be planned | Next planning window |
| Conley Index research | Deferred — pre-RC1.0 | Prompt archived at `docs/antigravity_tasks/antigravity_prompt__conley_index_framing_review_v0.1.md`; not scheduled before RC1.0 |
| Phase 1123 closure gate | **Next** | SENSITIVE — requires human GO token |
| Capsule v5.37 | Next coherence after Phase 1123 | Window 1124+ |

---

## 6. Test Inventory Snapshot

| Test file | Tests | Phase | Coverage |
|-----------|-------|-------|----------|
| `tests/test_phase_0947_h012_epoch_attribution_settle.py` | 31 | 947 | H-012 regression |
| `tests/test_phase_1101_window_945_1101_closure_gate.py` | 25 | 1101 | Window 945–1101 closure regression |
| `tests/test_phase_1107_h_con_02_panel_quorum_settle.py` | 30 | 1107 | CDL-083 H-CON-02 evidence |
| `tests/test_phase_1109_window_1102_1109_closure_gate.py` | 25 | 1109 | Window 1102–1109 closure regression |
| `tests/test_phase_1115_cdl_084_provenance_chain_attribution.py` | 31 | 1115 | CDL-084 PROVENANCE chain attribution |
| `tests/test_sensitive_runtime_coding_taboos.py` | 1 | 1119 | PRNG/float guardrail |
| `tests/test_phase_1117_window_1110_1117_closure_gate.py` | 37 | 1117 | Window 1110–1117 closure gate |
| `tests/test_phase_1120_sim_provenance_01_commissioning.py` | 22 | 1120 | SIM-PROVENANCE-01 commissioning evidence |
| `tests/test_phase_1121_sim_provenance_01_run02_disposition.py` | 10 | 1121 | Run 02 fine sweep + alpha disposition |

Combined scoped regression as of Phase 1121: **212 tests**.

---

## 7. Phase Numbering

| Range | Status |
|-------|--------|
| 0055–0950 | Normal constitutional lane (used through Phase 950) |
| 0951–1014 | **PERMANENTLY RESERVED** — Cluster-A G8 parallel track (CLOSED) |
| 0990–1099 | **SKIP** — reserved buffer |
| 1100+ | Normal lane resumes (current position: 1122) |

`phase_numbering_remediation_normal_lane_945_989_then_1100_plus`

---

## 8. Historical Anchors

- Prior capsule: `docs/specs/ilc_antigravity_context_capsule_v5.35.md`
- Phase 1119 walkthrough: `docs/phases/phase_1119_float_kill_01_ilc_core_float_prng_hardening_walkthrough.md`
- SIM-PROVENANCE-01 program spec: `docs/sims/sim_provenance_01/program.md`
- SIM-PROVENANCE-01 Run 01 results: `docs/sims/sim_provenance_01/results_phase_1120_run_01.md`
- SIM-PROVENANCE-01 Run 02 results: `docs/sims/sim_provenance_01/results_phase_1121_run_02.md`
- Alpha disposition record: `docs/sims/sim_provenance_01/alpha_disposition_phase_1121.md`
- Phase 1122 coherence report: `docs/specs/ilc_integration_coherence_report_1122_v0.1.md`
- Conley research prompt (deferred): `docs/antigravity_tasks/antigravity_prompt__conley_index_framing_review_v0.1.md`

`capsule_v5_36_supersedes_v5_35`
`float_kill_01_complete_phase_1119`
`sim_provenance_01_complete_phase_1120_1121`
`q8_satisfied_sim_provenance_01_complete`
`q2_active_cdl_amendment_pending_alpha_0_45`
`sim_spectral_02_data_dependency_satisfied`
