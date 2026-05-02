# ILC Antigravity Context Capsule v5.38

Supersedes: docs/specs/ilc_antigravity_context_capsule_v5.37.md
Date: 2026-05-02
Owner lane: Window 1130–1138 — SIM-SPECTRAL-02 + Genesis Atlas

`capsule_v5_38_supersedes_v5_37`
`window_1130_1138_sim_spectral_02_complete`
`sim_spectral_02_disposition_phase_1136`
`sim_spectral_02_scenario_b_advisory_phase_1136`
`genesis_morphogenic_hypergraph_atlas_complete_phase_1136a`
`genesis_compile_coverage_diagnostic_complete_v0_1`

This capsule is self-contained.

---

## 1. Current Frontier State

Window 1130–1138 phases 1130–1137 are complete. Phase 1138 is the SENSITIVE closure gate
and requires an explicit human GO token.

| Phase | Key work |
|-------|----------|
| 1130 | Window 1130–1138 sequence lock — SIM-SPECTRAL-02 lane |
| 1131 | SIM-SPECTRAL-02 data audit + signal definition |
| 1132 | SIM-SPECTRAL-02 harness build + program.md |
| 1133 | SIM-SPECTRAL-02 Run 01 coarse sweep (+ Fix1, Fix2, Fix3) |
| 1134 | Run 01 disposition — Scenario A declared |
| 1135 | SIM-SPECTRAL-02 Run 02 (+ Fix1 homoiconic rerun) |
| 1136A | Genesis morphogenic hypergraph atlas (curated seed, 31-node star map, GENESIS-COMPILE-01) |
| 1136 | Run 02 disposition — Scenario B advisory; β probe; ADR recommendation PROPOSED |
| 1137 | Coherence report + capsule v5.38 |

Current position: Phase 1137 complete, Phase 1138 closure gate next (SENSITIVE).

---

## 2. CDL Chain Status

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
| CDL-084 | Ratified | 1113 | PROVENANCE chain attribution; `PROVENANCE_DECAY_ALPHA = Decimal("0.45")` locked Phase 1126; Q2 token `q2_geometric_decay_alpha_decimal_0_45_locked`; all Q1–Q10 resolved and locked |
| CDL-070 | Deferred | — | PQ migration |

Next fresh CDL number remains **CDL-085**.

---

## 3. Attribution Settlement Runtime Status

| Constant | Value | Phase |
|----------|-------|-------|
| `EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION` | `"epoch_attribution_settle_runtime_1129_fix1.v0.5"` | 1129 Fix1 |
| `CDL_084_DEPENDENCY` | `"cdl_084_provenance_chain_attribution_ratified_1113.v0.1"` | 1113 (unchanged) |
| `CDL_084_TYPES_DEPENDENCY` | `"cdl_084_provenance_chain_attribution_ratified_1113.v0.1"` | 1113 (unchanged) |
| `PROVENANCE_DECAY_ALPHA` | `Decimal("0.45")` — **locked Phase 1126** | 1126 |
| `PROVENANCE_MAX_DEPTH` | `3` (`int`) | pre-existing (unchanged) |

No `ilc_core/` files were modified in Window 1130–1138. PROVENANCE attribution path remains
active. ATTESTATION and EPOCH_BOUNDARY remain silently ignored. REFUTATION attribution
remains governed by CDL-083.

---

## 4. CDL-084 Decision Record

| Q | Decision | Token |
|---|----------|-------|
| Q1 | PROVENANCE triggers ECU; caller-only contract | `q1_provenance_triggers_ecu_caller_only_contract` |
| Q2 | Geometric decay; `PROVENANCE_DECAY_ALPHA = Decimal("0.45")`; locked Phase 1126. SIM-PROVENANCE-01 Run 02: alpha `0.45` keep rate `3/3`. | `q2_geometric_decay_alpha_decimal_0_45_locked` |
| Q3 | `PROVENANCE_MAX_DEPTH = 3`; hop 1 = immediate parent | `q3_max_depth_3_hop_1_is_immediate_parent` |
| Q4 | Ancestor creator receives ECU | `q4_ancestor_creator_receives_ecu` |
| Q5 | Fresh per-event state; `visited_creators` nearest-hop-wins | `q5_fresh_per_event_visited_creators_nearest_hop_wins` |
| Q6 | Explicit nearest-first chain payload; pure settle, no graph queries | `q6_explicit_chain_payload_nearest_first_pure_settle` |
| Q7 | Duplicate `node_id` raises; duplicate `creator_id` nearest-hop-wins | `q7_duplicate_node_id_raises_nearest_creator_wins` |
| Q8 | Epoch mint source; SIM-PROVENANCE-01 satisfied Phase 1121. Q2 now locked. | `q8_epoch_mint_source_sim_provenance_01_required` (SATISFIED) |
| Q9 | Float kill: `PROVENANCE_DECAY_ALPHA: float -> Decimal("0.5")` | `q9_float_kill_decimal_literal_0_5` |
| Q10 | `None` chain -> missing error; `()` chain -> empty error | `q10_none_raises_missing_empty_raises_empty` |

---

## 5. Forward Obligations and Deferred Items

| Item | Status | Gate / sequencing |
|------|--------|-------------------|
| **SIM-SPECTRAL-02** | **COMPLETE — Phase 1136** | Scenario B advisory. Three advance conditions: (1) gaming resistance fix (S3 Sybil unresolved); (2) SIM-SPECTRAL-03 with 31-node Genesis seed; (3) λ₂ > 0 spectral connectivity confirmed. |
| **SIM-SPECTRAL-03** | Recommended — not yet authorized | Re-run Track A using 31-node Genesis core star map as S1 topology seed. Prerequisite for CDL-085 authorization. Must follow Atlas Tier-1 patch (Window 1139+). |
| **Werner φ-bound CDL (CDL-085)** | Deferred — SIM-gated | Scenario B advisory not sufficient to open; requires SIM-SPECTRAL-03 positive result + human authorization |
| **Genesis Atlas Tier-1** | Next atlas iteration (Window 1139) | Add ~10 authority-chain edges to curated seed to close L2 basis-reachability gap (17/31 → ≥28/31). Must precede SIM-SPECTRAL-03. |
| **Genesis Atlas Tier-2** | Window 1148+ | Promote ADR-0019 (graph-native governance compilation boundary) and ADR-0020 (knowledge-node-first) to core star-map nodes |
| **Genesis Atlas Tier-3** | Future window (dedicated design phase) | `schema:*` / `runtime:*` node class linking CDL/ADR governance nodes to `ilc_core/` implementation modules. Required for "compiler-like" coverage. Do not rush into current closure. |
| **GENESIS-COMPILE-01 checkpoints** | Ongoing at Windows 1139, 1148, 1166, 1175 | Iterative diagnostic; current baseline: PARTIAL_WITH_STRUCTURAL_GAPS (17/31 basis-reachable, 31% observed coverage). Gap is graph-construction (missing edges), not primitive-basis failure. |
| **SIM-ECU-STABILITY-01** | Candidate — not authorized | Carry forward unchanged |
| **Conley Index research** | Deferred — pre-RC1.0 | Prompt archived; not scheduled before RC1.0 |
| **ADR-0035 implementation CDL** | Deferred — direction accepted Phase 1100; §9 compositional primitive basis amendment added Phase 1136A | CDL number TBD (CDL-086 candidate); planning/authorization gate remains |
| **star expansion implementation** | Deferred — CDL prerequisites satisfied; blocked on H-011 patent assessment | Planning review before implementation CDL |
| **SIM-HYPEREDGE-01** | CDL-083 ratified ✓; planning authorization needed | Next planning window after CDL-085 |
| **Phase 1138 closure gate** | **Next** | SENSITIVE — requires human GO token; review scope includes Scenario B Advisory conditions AND GENESIS-COMPILE-01 gap |
| **Capsule v5.39** | Next coherence | Window 1139+ |
| **RC planning bridge** | Non-binding dependency map committed (`0e8920a6`) | See `docs/specs/ilc_window_1130_1138_to_rc_planning_bridge_v0.1.md`; requires formal guidance doc drafting before Window 1139+ executes |

---

## 6. Test Inventory Snapshot

### Inherited from capsule v5.37

| Test file | Tests | Phase | Coverage |
|-----------|-------|-------|----------|
| `tests/test_phase_0947_h012_epoch_attribution_settle.py` | 31 | 947 | H-012 regression |
| `tests/test_phase_1101_window_945_1101_closure_gate.py` | 25 | 1101 | Window 945–1101 closure regression |
| `tests/test_phase_1107_h_con_02_panel_quorum_settle.py` | 30 | 1107 | CDL-083 H-CON-02 evidence |
| `tests/test_phase_1109_window_1102_1109_closure_gate.py` | 25 | 1109 | Window 1102–1109 closure regression |
| `tests/test_phase_1115_cdl_084_provenance_chain_attribution.py` | 31 | 1115 | CDL-084 PROVENANCE chain attribution |
| `tests/test_phase_1117_window_1110_1117_closure_gate.py` | 37 | 1117 | Window 1110–1117 closure gate |
| `tests/test_sensitive_runtime_coding_taboos.py` | 1 | 1119 | PRNG/float guardrail |
| `tests/test_phase_1120_sim_provenance_01_commissioning.py` | 22 | 1120 | SIM-PROVENANCE-01 commissioning evidence |
| `tests/test_phase_1121_sim_provenance_01_run02_disposition.py` | 10 | 1121 | Run 02 fine sweep + alpha disposition |
| `tests/test_phase_1122_coherence_capsule_v5_36.py` | 10 | 1122 | Coherence/capsule v5.36 |
| `tests/test_phase_1123_window_1118_1123_closure_gate.py` | 25 | 1123 | Window 1118–1123 closure gate |
| `tests/test_phase_1127_cdl_084_q2_amendment.py` | 8 | 1127 | CDL-084 Q2 amendment evidence |

Subtotal (v5.37 inherited): **255 tests**

### Added in Window 1130–1138

| Test file | Tests | Phase | Coverage |
|-----------|-------|-------|----------|
| `tests/test_phase_1130_window_1130_1138_sequence_lock.py` | 5 | 1130 | Window 1130–1138 sequence lock |
| `tests/test_phase_1131_sim_spectral_02_signal_definition.py` | 5 | 1131 | SIM-SPECTRAL-02 signal definition |
| `tests/test_phase_1132_sim_spectral_02_harness.py` | 6 | 1132 | SIM-SPECTRAL-02 harness |
| `tests/test_phase_1133_sim_spectral_02_run01.py` | 5 | 1133 | Run 01 results |
| `tests/test_phase_1133_sim_spectral_02_fix2.py` | 8 | 1133 Fix2 | Ancestor-edge topology diagnostic |
| `tests/test_phase_1133_sim_spectral_02_fix3.py` | 6 | 1133 Fix3 | Homoiconic Genesis seed diagnostic |
| `tests/test_phase_1134_sim_spectral_02_run01_disposition.py` | 5 | 1134 | Run 01 disposition |
| `tests/test_phase_1135_sim_spectral_02_run02.py` | 7 | 1135 | Run 02 results (333 entries) |
| `tests/test_phase_1135_fix1_sim_spectral_02_run02_homoiconic.py` | 6 | 1135 Fix1 | Homoiconic Run 02 |
| `tests/test_phase_1136_sim_spectral_02_run02_disposition.py` | 5 | 1136 | Run 02 disposition (D01–D05) |
| `tests/test_phase_1136a_genesis_morphogenic_hypergraph_atlas.py` | 8 | 1136A | Atlas evidence (A01–A08) |
| `tests/test_genesis_node_candidate_crawl.py` | 11 | 1136A | Genesis crawl evidence |
| `tests/test_genesis_star_map_gap_analysis.py` | 5 | 1136A | Gap analysis evidence |
| `tests/test_genesis_compile_coverage_diagnostic.py` | 5 | 1136A | GENESIS-COMPILE-01 evidence |

Subtotal (Window 1130–1138 new): **87 tests**

**Combined total as of Phase 1137: 342 tests**

---

## 7. Phase Numbering

| Range | Status |
|-------|--------|
| 0055–0950 | Normal constitutional lane (used through Phase 950) |
| 0951–1014 | **PERMANENTLY RESERVED** — Cluster-A G8 parallel track (CLOSED) |
| 0990–1099 | **SKIP** — reserved buffer |
| 1100+ | Normal lane resumes (current position: 1137) |

`phase_numbering_remediation_normal_lane_945_989_then_1100_plus`

---

## 8. Historical Anchors

- Prior capsule: `docs/specs/ilc_antigravity_context_capsule_v5.37.md`
- Window 1130–1138 sequence lock: `docs/specs/ilc_phase_1130_1138_sequence_lock_v0.1.md`
- Phase 1136 disposition: `docs/sims/sim_spectral_02/run02_disposition_1136_v0.1.md`
- Phase 1136A curated seed: `docs/sims/sim_spectral_02/genesis_core_star_map_curated_seed_v0.1.json`
- Genesis core star map: `out/genesis_core_star_map_v0.1.json` (31 nodes, 35 edges)
- GENESIS-COMPILE-01 output: `out/genesis_compile_coverage_diagnostic_v0.1.json`
- RC planning bridge (non-binding): `docs/specs/ilc_window_1130_1138_to_rc_planning_bridge_v0.1.md`
- Phase 1137 coherence report: `docs/specs/ilc_integration_coherence_report_1137_v0.1.md`
- SIM-PROVENANCE-01 Run 02 disposition: `docs/sims/sim_provenance_01/alpha_disposition_phase_1121.md`

`capsule_v5_38_supersedes_v5_37`
`window_1130_1138_sim_spectral_02_complete`
`sim_spectral_02_disposition_phase_1136`
`sim_spectral_02_scenario_b_advisory_phase_1136`
`genesis_morphogenic_hypergraph_atlas_complete_phase_1136a`
`genesis_compile_coverage_diagnostic_complete_v0_1`
`cdl_084_q2_alpha_locked_decimal_0_45_phase_1126`
`q2_geometric_decay_alpha_decimal_0_45_locked`
`q8_satisfied_sim_provenance_01_complete`
