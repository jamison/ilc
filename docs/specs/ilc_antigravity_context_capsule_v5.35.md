# ILC Antigravity Context Capsule v5.35

Supersedes: docs/specs/ilc_antigravity_context_capsule_v5.34.md
Date: 2026-04-30
Owner lane: Window 1110-1117 — CDL-084 PROVENANCE Chain Attribution

`capsule_v5_35_supersedes_v5_34`
`window_1110_1117_complete_pending_gate_1117`
`cdl_084_ratified_phase_1113`
`provenance_settlement_active_phase_1114`
`provenance_evidence_tests_31_pass_phase_1115`

This capsule is self-contained.

---

## 1. Current Frontier State

**Window 1110-1117 complete pending closure gate Phase 1117.**

| Phase | Key work |
|-------|----------|
| 1110 | Window guidance and sequence lock for CDL-084 PROVENANCE chain attribution |
| 1111 | CDL-084 OPEN — PROVENANCE chain attribution (SENSITIVE) |
| 1112 | CDL-084 prelock hardening — 8 invariants confirmed |
| 1113 | CDL-084 RATIFIED — runtime/type Commit 1 (`3d943f32`), CDL Commit 2 (`275bdd14`) |
| 1114 | PROVENANCE settlement path activated; runtime version `epoch_attribution_settle_runtime_1114.v0.3` |
| 1115 | 31 CDL-084 evidence tests (G1-G14) — all pass |
| 1116 | Coherence report + capsule v5.35 + planning alignment |

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
| CDL-084 | **Ratified** | **1113** | **PROVENANCE chain attribution; geometric decay Decimal("0.5"); Q1-Q10 all resolved; float kill; explicit chain payload; pure settle** |
| CDL-070 | Deferred | — | PQ migration |

Next fresh CDL number: **CDL-085**. Werner phi-bound is SIM-gated. ADR-0035 implementation
CDL is planning/authorization-gated. The next CDL vehicle is TBD.

---

## 3. Attribution Settlement Runtime Status

| Constant | Value | Phase |
|----------|-------|-------|
| `EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION` | `"epoch_attribution_settle_runtime_1114.v0.3"` | 1114 |
| `CDL_084_DEPENDENCY` | `"cdl_084_provenance_chain_attribution_ratified_1113.v0.1"` | 1113 |
| `CDL_084_TYPES_DEPENDENCY` | `"cdl_084_provenance_chain_attribution_ratified_1113.v0.1"` | 1113 |
| `PROVENANCE_DECAY_ALPHA` | `Decimal("0.5")` — provisional pending SIM-PROVENANCE-01 | 1113 |
| `PROVENANCE_MAX_DEPTH` | `3` (`int`) | pre-existing |

PROVENANCE attribution path: **active as of Phase 1114**. ATTESTATION and EPOCH_BOUNDARY
remain silently ignored. REFUTATION attribution remains governed by CDL-083.

---

## 4. CDL-084 Decision Record

| Q | Decision | Token |
|---|----------|-------|
| Q1 | PROVENANCE triggers ECU; caller-only contract | `q1_provenance_triggers_ecu_caller_only_contract` |
| Q2 | Geometric decay; `PROVENANCE_DECAY_ALPHA = Decimal("0.5")`; provisional pending SIM-PROVENANCE-01 | `q2_geometric_decay_alpha_decimal_0_5_provisional` |
| Q3 | `PROVENANCE_MAX_DEPTH = 3`; hop 1 = immediate parent | `q3_max_depth_3_hop_1_is_immediate_parent` |
| Q4 | Ancestor creator receives ECU | `q4_ancestor_creator_receives_ecu` |
| Q5 | Fresh per-event state; `visited_creators` nearest-hop-wins | `q5_fresh_per_event_visited_creators_nearest_hop_wins` |
| Q6 | Explicit nearest-first chain payload; pure settle, no graph queries | `q6_explicit_chain_payload_nearest_first_pure_settle` |
| Q7 | Duplicate `node_id` raises; duplicate `creator_id` nearest-hop-wins | `q7_duplicate_node_id_raises_nearest_creator_wins` |
| Q8 | Epoch mint source; SIM-PROVENANCE-01 required before alpha locks | `q8_epoch_mint_source_sim_provenance_01_required` |
| Q9 | Float kill: `PROVENANCE_DECAY_ALPHA: float -> Decimal("0.5")` | `q9_float_kill_decimal_literal_0_5` |
| Q10 | `None` chain -> missing error; `()` chain -> empty error | `q10_none_raises_missing_empty_raises_empty` |

---

## 5. Forward Obligations and Deferred Items

This is the active forward-pointer register. Preserve these rows into v5.36+ until closed.

| Item | Status | Gate / sequencing |
|------|--------|-------------------|
| **SIM-PROVENANCE-01** | **Obligated** — alpha provisional; must execute before alpha locks | CDL-084 Q2 + Q8. Commissioning spec must require per-node PROVENANCE descendant count logging as a time series, not epoch snapshots, for SIM-SPECTRAL-02 correlation testing. |
| **SIM-SPECTRAL-02** | **Deferred** — non-canonical research direction | Sequence: CDL-084 done -> SIM-PROVENANCE-01 -> SIM-SPECTRAL-02. Tests whether PROVENANCE reach correlates with Popperian durability (falsification-resistance, not objective truth). Plan: `docs/research/ilc_relative_directional_energy_meter_and_epistemic_efficiency_plan_v0.1.md`. |
| Werner phi-bound CDL (CDL-085 candidate) | Deferred — SIM evidence required before CDL can open | Carried from Window 1109 handoff |
| ADR-0035 implementation CDL | Deferred — direction accepted Phase 1100; no CDL vehicle yet | Planning/authorization gate remains |
| star expansion implementation | Deferred — constitutional prerequisites appear satisfied; implementation blocked on patent/planning review and explicit human authorization | Planning review before implementation CDL |
| SIM-HYPEREDGE-01 gate | CDL-083 ratified; SIM can now be planned | Next planning window |
| Phase 1117 closure gate | Next | SENSITIVE — requires human GO token |
| Capsule v5.36 | Next coherence | Window 1118+ |

---

## 6. Test Inventory Snapshot

| Test file | Tests | Phase | Coverage |
|-----------|-------|-------|----------|
| `tests/test_phase_0947_h012_epoch_attribution_settle.py` | 31 | 947 | H-012 regression |
| `tests/test_phase_1101_window_945_1101_closure_gate.py` | 25 | 1101 | Window 945-1101 closure regression |
| `tests/test_phase_1107_h_con_02_panel_quorum_settle.py` | 30 | 1107 | CDL-083 H-CON-02 evidence |
| `tests/test_phase_1109_window_1102_1109_closure_gate.py` | 25 | 1109 | Window 1102-1109 closure regression |
| `tests/test_phase_1115_cdl_084_provenance_chain_attribution.py` | 31 | 1115 | CDL-084 PROVENANCE chain attribution |

Combined scoped regression: 142 tests.

---

## 7. Phase Numbering

| Range | Status |
|-------|--------|
| 0055-0950 | Normal constitutional lane (used through Phase 950) |
| 0951-1014 | **PERMANENTLY RESERVED** — Cluster-A G8 parallel track (CLOSED) |
| 0990-1099 | **SKIP** — reserved buffer |
| 1100+ | Normal lane resumes (current position: 1116) |

`phase_numbering_remediation_normal_lane_945_989_then_1100_plus`

---

## 8. Historical Anchors

- Prior capsule: `docs/specs/ilc_antigravity_context_capsule_v5.34.md`
- Phase 1116 coherence report: `docs/specs/ilc_integration_coherence_report_1116_v0.1.md`
- CDL-084 spec: `docs/specs/ilc_cdl_084_provenance_chain_attribution_opening_1111_v0.1.md`
- CDL-084 evidence tests: `tests/test_phase_1115_cdl_084_provenance_chain_attribution.py`
- Settle runtime: `ilc_core/economics/epoch_attribution_settle_runtime.py`

`capsule_v5_35_supersedes_v5_34`
`window_1110_1117_complete_pending_gate_1117`
`cdl_084_ratified_phase_1113`
`provenance_settlement_active_phase_1114`
`sim_provenance_01_required_before_alpha_locked`
`sim_spectral_02_sequenced_after_sim_provenance_01`
