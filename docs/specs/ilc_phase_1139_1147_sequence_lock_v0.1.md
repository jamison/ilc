# ILC Phase 1139-1147 Sequence Lock

Window: 1139-1147
Phase: 1139
Date: 2026-05-02

`window_1139_1147_sequence_lock_committed_phase_1139`

---

## 1. Purpose

Window 1139-1147 opens as a three-lane simulation and atlas window:

1. SIM-SPECTRAL-02 Run 02 Fix2 corrected baseline
2. Genesis Atlas Tier-1, Genesis node attestation signing, and GENESIS-COMPILE-01 checkpoint #1
3. SIM-SPECTRAL-03 with the patched Genesis star-map topology, ending in a CDL-085 authorization recommendation

The window does not open or ratify any CDL. It does not mutate `ilc_core/`, settlement,
QATPS, validator slashing, or runtime economic rules. CDL-085 remains SIM-gated and unopened.

---

## 2. Baseline

| Item | Value |
|------|-------|
| Prior window | 1130-1138 CLOSED Phase 1138 `961319bb` |
| Runtime version | `epoch_attribution_settle_runtime_1129_fix1.v0.5` |
| `PROVENANCE_DECAY_ALPHA` | `Decimal("0.45")` - locked Phase 1126 |
| Capsule | v5.38 |
| Scoped test baseline | 358 after Phase 1138 |
| Next fresh CDL | CDL-085, SIM-gated and not opened this window |
| Run 02 baseline status | Phase 1136 Scenario B Advisory is provisional pending corrected baseline |

The corrected Run 02 baseline is required because the original Run 02 matrix used
combinatorial λ₂ for structural impedance, while the fixed harness at `58c4687f` uses
normalized λ₂ bounded to `[0, 2]`. These metrics are not directly comparable. Phase 1140
isolates the formula correction; SIM-SPECTRAL-03 then isolates the topology change.

---

## 3. Phase Table

| Order | Phase | Topic | Character | Sensitivity | Batch |
|-------|-------|-------|-----------|-------------|-------|
| 1 | 1139 | Window 1139-1147 sequence lock | Foundation | NON-SENSITIVE | A |
| 2 | 1140 | SIM-SPECTRAL-02 Run 02 Fix2 corrected baseline | Simulation | NON-SENSITIVE | A |
| 3 | 1141 | Corrected Run 02 disposition addendum | Synthesis | NON-SENSITIVE | B |
| 4 | 1142 | Atlas Tier-1 genesis attestation node + diagnostic restructure | Atlas/Simulation | NON-SENSITIVE | C |
| 4S | 1142s | Genesis node attestation signing ceremony | Signing | **SENSITIVE** | C-S |
| 5 | 1143 | GENESIS-COMPILE-01 checkpoint #1 | Simulation | NON-SENSITIVE | D |
| 6 | 1144 | SIM-SPECTRAL-03 harness update + program spec | Simulation | NON-SENSITIVE | E |
| 7 | 1145 | SIM-SPECTRAL-03 Run 01 | Simulation | NON-SENSITIVE | F |
| 8 | 1146 | SIM-SPECTRAL-03 disposition + CDL-085 recommendation | Synthesis | NON-SENSITIVE | G |
| 9 | 1147 | Window 1139-1147 closure gate + capsule v5.39 | Gate | **SENSITIVE** | H |

---

## 4. Constraints

1. No CDL opening, prelock, ratification, or mutation occurs in this window.
2. `ILC_CDL_MUTATION_AUTHORIZED` is not required for any phase in this window.
3. No `ilc_core/` runtime mutation occurs in this window.
4. Phase 1140 must complete before Phase 1141.
5. Phase 1141 corrected baseline is the comparison baseline for SIM-SPECTRAL-03; Phase 1136 Run 02 numeric values are superseded for comparison purposes.
6. Phase 1142 must complete and the 32-node star-map output must be reviewed before Phase 1142s.
7. Phase 1142s is SENSITIVE and requires a separate explicit human GO token. Agents must not handle private key material.
8. Phase 1143 must confirm `authority_traceable_core_nodes >= 28/32` before Phase 1144.
9. Phase 1144 must complete before Phase 1145.
10. Phase 1146 must complete and be reviewed by the human before Phase 1147.
11. Phase 1147 is SENSITIVE and requires an explicit human GO token.

`no_cdl_mutation_this_window`
`ilc_core_read_only_this_window`
`genesis_signing_requires_human_go_phase_1142s`

---

## 5. Batch Strike Force Plan

| Batch | Phases | Notes |
|-------|--------|-------|
| A | 1139 + 1140 | Sequence lock and corrected rerun may run together after this lock is committed |
| B | 1141 alone | Disposition addendum must be reviewed before atlas changes proceed |
| C | 1142 alone | Atlas node/edge/diagnostic work; human reviews generated graph before signing |
| C-S | 1142s alone | SENSITIVE signing ceremony; separate human GO token required |
| D | 1143 alone | Checkpoint depends on Phase 1142s signature artifact |
| E | 1144 alone | Harness update depends on checkpoint passing |
| F | 1145 alone | Computational SIM-SPECTRAL-03 run |
| G | 1146 alone | Disposition may drive CDL-085 authorization recommendation |
| H | 1147 alone | SENSITIVE closure gate; human GO token required |

---

## 6. Canonical Anchors

- Window guidance doc: `docs/specs/ilc_window_1139_1147_candidate_phase_grouping_v0.1.md`
- Capsule v5.38: `docs/specs/ilc_antigravity_context_capsule_v5.38.md`
- Window 1130-1138 handoff: `docs/specs/ilc_window_1130_1138_handoff_1138_v0.1.md`
- RC planning bridge: `docs/specs/ilc_window_1130_1138_to_rc_planning_bridge_v0.1.md`
- SIM-SPECTRAL-02 harness: `tools/sim_spectral_02.py`
- SIM-SPECTRAL-02 Run 02 provisional disposition: `docs/sims/sim_spectral_02/run02_disposition_1136_v0.1.md`
- Genesis curated seed: `docs/sims/sim_spectral_02/genesis_core_star_map_curated_seed_v0.1.json`
- GENESIS-COMPILE-01 diagnostic: `tools/genesis_compile_coverage_diagnostic.py`
- Genesis Agent 1 public key record: `docs/genesis/genesis_agent1_pubkey_record_838a.txt`

---

## 7. Closing Tokens

`window_1139_1147_sequence_lock_committed_phase_1139`
`run02_fix2_corrected_baseline_phase_1140`
`atlas_tier1_patch_phase_1142`
`genesis_node_attestation_signing_phase_1142s_sensitive`
`genesis_compile_checkpoint_1_phase_1143`
`sim_spectral_03_phases_1144_1146`
`window_1139_1147_closure_gate_phase_1147_sensitive`
`no_cdl_mutation_this_window`
`ilc_core_read_only_this_window`
`genesis_signing_requires_human_go_phase_1142s`
