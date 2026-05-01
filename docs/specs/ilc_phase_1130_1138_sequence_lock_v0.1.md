# ILC Phase 1130-1138 Sequence Lock

Window: 1130-1138
Phase: 1130
Date: 2026-05-01

`window_1130_1138_sequence_lock_committed_phase_1130`

---

## 1. Purpose

Window 1130-1138 executes a single simulation research lane: SIM-SPECTRAL-02. The window
tests whether the ILC hypergraph can serve as a relative directional epistemic efficiency
meter. No CDL mutations, no `ilc_core/` changes, and no settlement rule changes occur. An
ADR draft is authorized in Phase 1136 if simulation evidence is positive; it does not take
effect this window.

---

## 2. Baseline

| Item | Value |
|------|-------|
| Prior window | 1124-1129 CLOSED Phase 1129 `b84e0c72`; Fix1 `2562012b` |
| Runtime version | `epoch_attribution_settle_runtime_1129_fix1.v0.5` |
| `PROVENANCE_DECAY_ALPHA` | `Decimal("0.45")` - locked Phase 1126 |
| Capsule | v5.37 |
| Scoped tests passing | 289 (post-Fix1) |
| Next fresh CDL | CDL-085 (SIM-gated; not this window) |

---

## 3. Phase Table

| Order | Phase | Topic | Character | Sensitivity | Batch |
|-------|-------|-------|-----------|-------------|-------|
| 1 | 1130 | Window 1130-1138 sequence lock | Foundation | NON-SENSITIVE | A |
| 2 | 1131 | SIM-SPECTRAL-02 data audit + signal definition | Simulation | NON-SENSITIVE | A |
| 3 | 1132 | SIM-SPECTRAL-02 harness build + program.md | Simulation | NON-SENSITIVE | A |
| 4 | 1133 | SIM-SPECTRAL-02 Run 01 - coarse sweep | Simulation | NON-SENSITIVE | B |
| 5 | 1134 | Run 01 disposition - parameter narrowing | Simulation | NON-SENSITIVE | C |
| 6 | 1135 | SIM-SPECTRAL-02 Run 02 - fine sweep + gaming resistance | Simulation | NON-SENSITIVE | D |
| 7 | 1136 | Run 02 disposition + ADR recommendation draft | Synthesis | NON-SENSITIVE | E |
| 8 | 1137 | Coherence report + capsule v5.38 | Synthesis | NON-SENSITIVE | E |
| 9 | 1138 | Window 1130-1138 closure gate | Gate | **SENSITIVE** | F |

---

## 4. Constraints

1. No CDL opening or ratification in this window - `ILC_CDL_MUTATION_AUTHORIZED` is not
   required at any phase.
2. No `ilc_core/` runtime mutations in this window - spectral substrate files
   (`laplacian_analytics.py`, `spectral_trajectory.py`, `local_spectral_analytics.py`,
   `spectral_utils.py`) are read-only references.
3. SIM-SPECTRAL-02 is a research simulation only - disposition does not constitute a CDL
   amendment or settlement change.
4. Phase 1135 scope is conditional on Phase 1134 disposition (Scenario A, B, or C). Phase
   numbers are fixed; scope determination requires reading the Phase 1134 disposition
   document before executing Phase 1135.
5. Phase 1138 (closure gate) is SENSITIVE and requires explicit human GO token before
   execution.

`no_cdl_mutation_this_window`
`ilc_core_read_only_this_window`

---

## 5. Batch Strike Force Plan

| Batch | Phases | Notes |
|-------|--------|-------|
| A | 1130 + 1131 + 1132 | All NON-SENSITIVE; may Strike Force together |
| B | 1133 alone | Computational; results require human review before disposition |
| C | 1134 alone | Disposition declares Scenario A/B/C; must complete before Phase 1135 |
| D | 1135 alone | Scope is disposition-dependent |
| E | 1136 + 1137 | Tightly coupled; both NON-SENSITIVE |
| F | 1138 alone | SENSITIVE - human GO token required |

---

## 6. Key Canonical Anchors

- Window guidance doc: `docs/specs/ilc_window_1130_1138_candidate_phase_grouping_v0.1.md`
- Capsule v5.37 (PRIMARY): `docs/specs/ilc_antigravity_context_capsule_v5.37.md`
- SIM-SPECTRAL-02 research plan: `docs/research/ilc_relative_directional_energy_meter_and_epistemic_efficiency_plan_v0.1.md`
- SIM-PROVENANCE-01 time-series: `out/sim_provenance_01_time_series.json`
- Laplacian analytics (read-only): `ilc_core/analysis/laplacian_analytics.py`

---

## 7. Closing Tokens

`window_1130_1138_sequence_lock_committed_phase_1130`
`sim_spectral_02_commissioned_phase_1131_1135`
`sim_spectral_02_disposition_phase_1136`
`capsule_v5_38_phase_1137`
`window_1130_1138_closure_gate_phase_1138_sensitive`
`no_cdl_mutation_this_window`
`ilc_core_read_only_this_window`
