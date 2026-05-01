# ILC Window 1130-1138: Candidate Phase Grouping

**Author:** Claude Sonnet 4.6 (local architectural reviewer)
**Date:** 2026-05-01
**Baseline:** Window 1124-1129 CLOSED (Phase 1129 `b84e0c72`; Fix1 `2562012b`). CDL-084 fully resolved; `PROVENANCE_DECAY_ALPHA = Decimal("0.45")` locked Phase 1126; runtime `epoch_attribution_settle_runtime_1129_fix1.v0.5`; Q2 token `q2_geometric_decay_alpha_decimal_0_45_locked`; all CDL-084 Q1–Q10 locked. 289 scoped tests passing post-Fix1. Capsule v5.37.
**Planning note:** This is a candidate grouping, not a locked sequence. Phases 1130–1137 are the hard minimum lane. Phase 1138 (closure gate) requires human GO token.

---

## §1. Window Identity and Scope

**Window:** 1130–1138
**Primary lane:** SIM-SPECTRAL-02 — Relative Epistemic Energy and Directional Efficiency
**Character:** Single-lane simulation research window. No CDL openings. No `ilc_core/` runtime mutations. No settlement changes. No ADR ratification or adoption — an ADR draft is permitted in Phase 1136 if evidence is positive, but it does not take effect this window.

This window commissions, runs, and disposes of SIM-SPECTRAL-02: the simulation testing whether the hypergraph can serve as a relative directional epistemic efficiency meter. The core question is whether `x_i = exp(-k * Durability_t(node_i))` makes the Dirichlet energy `E_L(x)` a predictive stability signal — and whether the combined V_t formulation `α·E_L(x) + β·mean_i(x_i) + γ·Structural_Impedance_t + δ·Contention_Pressure_t` distinguishes genuine durability from fragile homogeneity under adversarial and healthy-growth conditions alike.

The research is non-canonical. No CDL, ADR, settlement rule, or QATPS change is authorized here. If SIM-SPECTRAL-02 evidence is positive and robust, this window produces a draft ADR for human review in a subsequent window. If the signal is not robust, the window produces an explicit non-recommendation that closes the research direction cleanly.

**Tail-slot policy:** Phase 1138 (closure gate) is SENSITIVE and requires explicit human GO token. Phases 1130–1137 are all NON-SENSITIVE and may be Strike Forced in batches.

---

## §2. Baseline and Inheritance

### Ratified CDL chain (relevant to this window)

| CDL | Status | Key constant |
|-----|--------|--------------|
| CDL-081 | Ratified | Hyperedge ECU attribution — PROVENANCE chain, REUSE, CO_AUTHORSHIP, REFUTATION, MAINTENANCE |
| CDL-083 | Ratified | H-CON-02 panel quorum ejected stake |
| CDL-084 | Ratified | PROVENANCE chain attribution; `PROVENANCE_DECAY_ALPHA = Decimal("0.45")` locked Phase 1126 |

**Next fresh CDL number: CDL-085** — SIM-gated (Werner φ-bound); not opened this window.

### Active runtime chain (relevant to SIM inputs)

| Module | Version | Phase |
|--------|---------|-------|
| `epoch_attribution_settle_runtime.py` | `epoch_attribution_settle_runtime_1129_fix1.v0.5` | 1129 Fix1 (`2562012b`) |
| `laplacian_analytics.py` | SIM-SPECTRAL-01/H-005/H-006a calibrated | pre-existing |
| `spectral_trajectory.py` | H-006b temporal trajectory | pre-existing |
| `local_spectral_analytics.py` | local neighborhood λ₂ | pre-existing |

### Inherited canonical anchors

- Capsule v5.37: `docs/specs/ilc_antigravity_context_capsule_v5.37.md`
- Window 1124-1129 handoff: `docs/specs/ilc_window_1124_1129_handoff_1129_v0.1.md`
- SIM-SPECTRAL-02 research plan: `docs/research/ilc_relative_directional_energy_meter_and_epistemic_efficiency_plan_v0.1.md`
- SIM-PROVENANCE-01 time-series data: `out/sim_provenance_01_time_series.json`
- SIM-PROVENANCE-01 summaries: `out/sim_provenance_01_summary.json`, `out/sim_provenance_01_run02_summary.json`
- Laplacian analytics background: `docs/research/ilc_lyapunov_stability_and_dirichlet_energy_notes_v0.1.md`
- Spectral intelligence memo: `docs/research/ilc_spectral_intelligence_test_research_memo_v0.1.md`

---

## §3. Track Inventory

### Constitutionally obligated

None. CDL-084 fully discharged Window 1124-1129. No outstanding constitutional obligations entering this window.

### Deferred governance

| Item | Status | Gate |
|------|--------|------|
| CDL-085 (Werner φ-bound) | SIM-gated | Requires SIM evidence; not this window |
| ADR-0035 implementation CDL | Planning/authorization gated | Not this window |
| Star expansion | H-011 patent gate + human authorization | Not this window |
| SIM-ECU-STABILITY-01 | Candidate — not authorized | Not this window |
| SIM-HYPEREDGE-01 | Gate clear (CDL-083 ✓) — not scheduled | Not this window |
| Conley Index research | Deferred pre-RC1.0 | Archived Phase 1119 |

### Simulation-conditional

| SIM | Status | CDL downstream |
|-----|--------|----------------|
| **SIM-SPECTRAL-02** | **This window — active** | ADR draft if positive; CDL-085 gated separately |

---

## §4. SIM-SPECTRAL-02 Scope

### 4.1 Research questions (from plan v0.1 §12)

Ten questions drive the simulation design and disposition:

| Q | Question |
|---|----------|
| Q1 | Does `x_i = exp(-k * Durability_t(node_i))` make `E_L(x)` predictive or explanatory? Which Durability components and weight profiles are robust across seeds and workloads? |
| Q2 | Does bounded `Structural_Impedance_t = max(0, θ_floor - λ₂_t) / θ_floor` add signal beyond the existing λ₂ partition-risk alert in `laplacian_analytics.py`? |
| Q3 | Can the combined `α·E_L(x) + β·mean_i(x_i)` distinguish genuinely durable coherence from uniformly fragile homogeneity (same-V_t failure mode)? |
| Q4 | Does `Epistemic_Efficiency_t = Durable_Verified_Work_t / Relative_Cost_Proxy_t` improve under known-good graph growth and degrade under partition, Sybil clustering, duplicate-contention, and contradiction-loop scenarios? |
| Q5 | What rolling-window length and recovery-half-life thresholds avoid false positives during normal discovery bursts? |
| Q6 | Does the metric correlate with downstream REUSE and PROVENANCE reach better than raw claim volume? |
| Q7 | Can the metric be gamed by creating low-value reuse, artificial provenance chains, or staged refutations? |
| Q8 | Should topology appear as `h_topology_t` in QATPS, as a denominator cost proxy, or only as an operator dashboard signal? (Disposition only — no QATPS change authorized here.) |
| Q9 | Do local node-neighborhood `V_t` signals catch stress earlier than global graph metrics? |
| Q10 | Does PROVENANCE descendant count (from `out/sim_provenance_01_time_series.json`) correlate with later durability, reuse, or validation survival? |

### 4.2 Signal and formulation definition targets

**Primary signal:**
```
x_i = exp(-k * Durability_t(node_i))

Durability_t(node_i) =
    a * survived_refutations_i
  + b * reuse_count_i
  + c * provenance_descendant_count_i
  + d * validation_integrity_i
  + e * path_uplift_i
```

`k` and weights `{a, b, c, d, e}` are SIM-SPECTRAL-02 calibration targets. Multiple weight profiles must be swept before any profile is treated as stable.

**Dirichlet energy:**
```
E_L(x) = x^T L x = Σ_edges w_ij * (x_i - x_j)²
```

**V_t candidate (local neighborhood):**
```
V_t(N(node_i)) =
    α * Σ w_ij(x_i - x_j)²    ← epistemic tension across incident edges
  + β * mean_i(x_i)             ← baseline instability penalty (size-invariant)
  + γ * Structural_Impedance_t  ← bounded λ₂ proxy (NOT raw 1/λ₂)
  + δ * Contention_Pressure_t   ← attribution dispute pressure
```

**Epistemic efficiency metric:**
```
Epistemic_Efficiency_t = Durable_Verified_Work_t / Relative_Cost_Proxy_t

rolling_slope(Epistemic_Efficiency_t) > 0  ← the health criterion
```

### 4.3 Input data sources

- `out/sim_provenance_01_time_series.json` — per-node provenance descendant counts over simulated epochs; primary raw material for Q10 and Durability_t calibration
- `ilc_core/analysis/laplacian_analytics.py` — existing λ₂ substrate; calibration constants from SIM-SPECTRAL-01 (`THETA_FLOOR=0.001`, `N_BOOTSTRAP=44`, `EPSILON_TRIGGER=0.3391`); SIM-SPECTRAL-02 must not modify this file
- `ilc_core/analysis/spectral_trajectory.py` — existing temporal trajectory analytics; read-only reference
- `ilc_core/analysis/local_spectral_analytics.py` — local neighborhood λ₂; read-only reference for Q9 baseline comparison

### 4.4 Required scenarios (Run 01 and Run 02)

Four mandatory adversarial/healthy contrast scenarios:

| Scenario | Description | Expected V_t response |
|----------|-------------|----------------------|
| **S1 — Healthy growth** | Agents produce durable verified work; REUSE and PROVENANCE reach expand; no adversarial activity | V_t decreasing; rolling slope positive; Epistemic_Efficiency rising |
| **S2 — Partition stress** | Topology becomes near-disconnected (λ₂ → 0); γ term maxed; structural impedance high | V_t spiking; Structural_Impedance_t dominant; clear alarm |
| **S3 — Sybil cluster** | Coordinated agents produce correlated low-quality claims with artificial REUSE | V_t locally elevated; contention pressure elevated; ideally distinguishable from S1 |
| **S4 — Contradiction loop** | Persistent unresolved contradictions; no upheld REFUTATION events; attribution contention cycles | δ term elevated; Epistemic_Efficiency denominator growing; numerator stalled |

Gaming-resistance probes (Run 02 additional):

| Probe | Description |
|-------|-------------|
| **G1** | Flood low-value REUSE events without durability improvement |
| **G2** | Construct artificial provenance chains (shallow, no downstream reuse) |
| **G3** | Stage refutations that are immediately retracted |

### 4.5 Expected outputs

| Output | File | Condition |
|--------|------|-----------|
| SIM-SPECTRAL-02 program spec | `docs/sims/sim_spectral_02/program.md` | Always |
| Simulation harness | `tools/sim_spectral_02.py` | Always |
| Run 01 results | `out/sim_spectral_02_run01_summary.json` | Always |
| Run 02 results | `out/sim_spectral_02_run02_summary.json` | Always |
| Disposition document | `docs/sims/sim_spectral_02/spectral_02_disposition_phase_1136.md` | Always |
| ADR draft | `docs/adrs/adr_NNNN_relative_epistemic_energy_draft.md` | If evidence positive — Scenario A or B only; not ratified this window |
| Explicit non-recommendation | Inside disposition doc | If signal not robust |
| Coherence report | `docs/specs/ilc_integration_coherence_report_1137_v0.1.md` | Always |
| Capsule v5.38 | `docs/specs/ilc_antigravity_context_capsule_v5.38.md` | Always |

**Harness location convention:** SIM-PROVENANCE-01 harness lives at `tools/sim_provenance_01.py`. SIM-SPECTRAL-02 follows the same convention: `tools/sim_spectral_02.py`. The `docs/sims/sim_spectral_02/` directory holds the program spec and disposition docs only.

### 4.6 Non-goals for this window

- No CDL opening or ratification
- No `ilc_core/` runtime mutations
- No settlement rule changes
- No QATPS changes
- No epoch commitment changes (Merkle-Laplacian dual commitment is research-only, deferred)
- No CDL-085 opening (SIM-gated; disposition from this window informs but does not open it)
- No SIM-HYPEREDGE-01 or SIM-ECU-STABILITY-01 (separate lanes)

---

## §5. CDL Number Assignments

| CDL | Title (candidate) | Decision digest anchor | Opening phase | Ratification phase |
|-----|-------------------|----------------------|---------------|-------------------|
| CDL-085 | Werner φ-bound epistemic efficiency KPI | TBD — SIM-SPECTRAL-02 evidence required | Not this window | Not this window |

**Note:** CDL-085 is SIM-gated. This window's disposition (Phase 1136) may recommend opening CDL-085 if evidence is positive, but the opening itself is not authorized here. Human authorization is required before CDL-085 opens.

No CDL mutations occur in Window 1130-1138. The pre-commit hook (`ILC_CDL_MUTATION_AUTHORIZED`) is not required for any phase.

---

## §6. Candidate Phase Table

| Order | Phase | Topic | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 1130 | Window 1130–1138 sequence lock | Foundation | NON-SENSITIVE |
| 2 | 1131 | SIM-SPECTRAL-02 data audit + signal definition | Simulation | NON-SENSITIVE |
| 3 | 1132 | SIM-SPECTRAL-02 harness build + program.md | Simulation | NON-SENSITIVE |
| 4 | 1133 | SIM-SPECTRAL-02 Run 01 — coarse sweep | Simulation | NON-SENSITIVE |
| 5 | 1134 | Run 01 disposition — parameter narrowing | Simulation | NON-SENSITIVE |
| 6 | 1135 | SIM-SPECTRAL-02 Run 02 — fine sweep + gaming resistance | Simulation | NON-SENSITIVE |
| 7 | 1136 | Run 02 disposition + ADR recommendation draft | Synthesis | NON-SENSITIVE |
| 8 | 1137 | Coherence report + capsule v5.38 | Synthesis | NON-SENSITIVE |
| 9 | 1138 | Window 1130–1138 closure gate | Gate | **SENSITIVE** |

### Strike Force batch groupings

| Batch | Phases | Rationale |
|-------|--------|-----------|
| **Batch A** | 1130 + 1131 + 1132 | All NON-SENSITIVE; seq lock defines phases that data audit and harness immediately build on; no interdependence issues |
| **Batch B** | 1133 alone | Computational phase; may produce results requiring human review before disposition |
| **Batch C** | 1134 alone | Disposition may alter Phase 1135 scope; must be reviewed before Run 02 executes |
| **Batch D** | 1135 alone | Run 02 scope is disposition-dependent |
| **Batch E** | 1136 + 1137 | Disposition and coherence are tightly coupled; both NON-SENSITIVE; ADR draft and capsule are natural pair |
| **Batch F** | 1138 alone | SENSITIVE — human GO token required before execution |

### Conditional note on Run 02 (Phase 1135)

Run 02 scope is conditional on Run 01 disposition:

- **Scenario A (Run 01 ambiguous — signal present but k/weights unstable):** Phase 1135 runs a fine parameter sweep centered on the best-performing Run 01 region, plus all gaming-resistance probes. Phase 1136 produces disposition + ADR draft.
- **Scenario B (Run 01 positive — clear signal, parameter ranges stable):** Phase 1135 runs gaming-resistance probes only (G1–G3) plus a confirmatory fine sweep. Phase 1136 produces disposition + ADR draft with higher confidence.
- **Scenario C (Run 01 negative — no predictive signal):** Phase 1135 is abbreviated: run gaming probes and one additional workload variant to confirm the null result is not a workload artifact. Phase 1136 produces explicit non-recommendation with a clean close of the research direction.

Under all scenarios, Phases 1136 and 1137 remain NON-SENSITIVE (no CDL, no runtime mutation).

---

## §7. Sensitivity Classification

### SENSITIVE phases

- **Phase 1138 — Closure gate:** Structural window boundary. Requires explicit human GO token before execution. Not a CDL mutation, but classified SENSITIVE per standard closure-gate policy.

### NON-SENSITIVE phases

- **Phase 1130 — Sequence lock:** Doc-only. No CDL mutation. No `ilc_core/` changes.
- **Phase 1131 — Data audit + signal definition:** Read-only audit of `out/sim_provenance_01_time_series.json` and existing spectral substrate. Produces a signal definition spec doc. No mutation.
- **Phase 1132 — Harness build:** Creates `docs/sims/sim_spectral_02/program.md` and `tools/sim_spectral_02.py`. No `ilc_core/` changes. No CDL.
- **Phase 1133 — Run 01:** Executes harness. Writes `out/sim_spectral_02_run01_summary.json`. No mutation.
- **Phase 1134 — Run 01 disposition:** Analysis and parameter-narrowing document. No mutation.
- **Phase 1135 — Run 02:** Executes harness with narrowed parameters + gaming probes. Writes `out/sim_spectral_02_run02_summary.json`. No mutation.
- **Phase 1136 — Disposition + ADR draft:** Analysis document + optional ADR draft text (draft only — not ratified here). No `ilc_core/` changes. No CDL env var.
- **Phase 1137 — Coherence + capsule:** Standard coherence report + capsule v5.38. Doc-only. No mutation.

### Conditional phases rule

Phase numbers are fixed (1130–1138); no phase is conditional on a CDL scenario. However, **Phase 1135 scope is conditional on Phase 1134 disposition** (Scenario A, B, or C per §6). Before executing Phase 1135, Codex must read the Phase 1134 disposition document to determine which run scope applies. This is a scope-conditional phase, not a CDL-conditional phase — no GO token is required regardless of scenario.

### Pre-commit hook

The `ILC_CDL_MUTATION_AUTHORIZED` hook is **not required for any phase** in Window 1130-1138. No CDL mutations occur in this window.

---

## §8. Scope Notes for Fixed Phases

### Phase 1130 — Window 1130–1138 Sequence Lock (NON-SENSITIVE)

No GO token required. Doc-only commit.

**Deliverables:**
- `docs/specs/ilc_phase_1130_1138_sequence_lock_v0.1.md`

**Required content tokens:**
```
window_1130_1138_sequence_lock_committed_phase_1130
sim_spectral_02_commissioned_phase_1131_1135
sim_spectral_02_disposition_phase_1136
capsule_v5_38_phase_1137
window_1130_1138_closure_gate_phase_1138_sensitive
```

Phase table (6 columns): Order / Phase / Topic / Character / Sensitivity / Batch.

Constraints to enumerate:
1. No CDL opening in this window
2. No `ilc_core/` runtime mutations in this window
3. SIM-SPECTRAL-02 is research-only; disposition does not constitute a CDL amendment
4. Phase 1135 scope is conditional on Phase 1134 disposition
5. Phase 1138 (closure gate) requires explicit human GO token

**Commit subject:** `docs(seq-lock): window 1130-1138 sequence lock — SIM-SPECTRAL-02`

---

### Phase 1131 — SIM-SPECTRAL-02 Data Audit + Signal Definition (NON-SENSITIVE)

No GO token required.

**Deliverables:**
- `docs/sims/sim_spectral_02/sim_spectral_02_signal_definition_v0.1.md`

**Required content:** Signal definition spec must nail down:
1. Exact form of `x_i = exp(-k * Durability_t(node_i))` with `k` declared as a sweep parameter
2. **Durability_t data inventory (critical):** For each component `{survived_refutations, reuse_count, provenance_descendant_count, validation_integrity, path_uplift}`, explicitly declare whether it is: (a) directly observed in `out/sim_provenance_01_time_series.json`, (b) synthetically generated for the SIM, or (c) unavailable and excluded from this run. Components declared synthetic must be clearly labeled as such throughout the disposition — the SIM must not validate a synthetic metric as if it were a live ILC data surface. If fewer than 3 components are directly observed, Run 01 should prioritize the observed components and treat the rest as sensitivity analysis.
3. V_t formulation with all four terms named and bounded
4. `Structural_Impedance_t` formula (`max(0, θ_floor - λ₂_t) / θ_floor`) — confirm `THETA_FLOOR = 0.001` from `laplacian_analytics.py`
5. Audit of `out/sim_provenance_01_time_series.json` structure: available fields, epoch count, node count, presence of provenance descendant counts per node
6. Declaration of which SIM-SPECTRAL-02 questions (Q1–Q10) are addressable with directly observed data, which require synthetic workloads, and which are deferred pending richer data capture
7. Run 01 parameter sweep plan: k values, weight profiles, seed set

**Test structure:** Minimum 4 tests:
- T1: signal definition doc exists and contains `sim_spectral_02_signal_definition_committed`
- T2: `out/sim_provenance_01_time_series.json` is parseable JSON with expected structure
- T3: `THETA_FLOOR` in `laplacian_analytics.py` is `0.001` (imported, not hardcoded in test)
- T4: signal definition doc declares at least 3 distinct k candidate values for Run 01 sweep

**Commit subject:** `sim(spectral-02): signal definition + data audit phase 1131`

---

### Phase 1132 — SIM-SPECTRAL-02 Harness Build (NON-SENSITIVE)

No GO token required.

**Deliverables:**
- `docs/sims/sim_spectral_02/program.md` — human-readable simulation program spec
- `tools/sim_spectral_02.py` — simulation harness (follows `tools/sim_provenance_01.py` convention)

**Required content for program.md:**
- Hard metrics with pass/fail thresholds for each scenario (S1–S4)
- Explicit definition of "signal viable" vs. "signal not viable" decision rule
- Gaming-resistance probe definitions (G1–G3)
- Output schema for `out/sim_spectral_02_run01_summary.json`

**Harness must:**
- Accept `--k`, `--weights`, `--seed`, `--scenario`, `--epochs` as CLI parameters
- Load `out/sim_provenance_01_time_series.json` as the provenance data source
- Compute `x_i`, `E_L(x)`, V_t per epoch per node
- Compute global `Epistemic_Efficiency_t` and rolling slope
- Write structured JSON output consumable by disposition phase
- Not modify any `ilc_core/` file

**Test structure:** Minimum 5 tests:
- H1: `program.md` exists and contains `sim_spectral_02_program_committed`
- H2: `sim_spectral_02.py` is importable without error
- H3: harness accepts `--k` and `--scenario` arguments
- H4: harness outputs valid JSON to stdout or file
- H5: harness correctly computes `x_i = exp(-k * d)` for a simple hand-verified example

**Commit subject:** `sim(spectral-02): harness build + program.md phase 1132`

---

### Phase 1133 — SIM-SPECTRAL-02 Run 01 (NON-SENSITIVE)

No GO token required. Codex executes the harness.

**Deliverables:**
- `out/sim_spectral_02_run01_summary.json`
- `docs/sims/sim_spectral_02/run01_raw_notes_1133.md` (brief narrative of what was run and what came out)

**Run 01 parameters:** Per signal definition from Phase 1131. Minimum:
- 3+ k values spanning coarse range (e.g., 0.3, 0.7, 1.2 — actual values set in Phase 1131)
- 3+ weight profiles for Durability_t components
- Seeds: 42, 1337, 2026
- All four scenarios: S1–S4
- ≥ 30 simulated epochs per run

**Decision gate at Run 01 output:** Before Phase 1134 disposition, human reviews run01_summary.json. No branch decision is made in Phase 1133 — that is Phase 1134's job.

**Test structure:** Minimum 3 tests:
- R1: `out/sim_spectral_02_run01_summary.json` exists and is valid JSON
- R2: summary contains results for all four scenarios (S1–S4)
- R3: summary contains at least 3 distinct k values in results

**Commit subject:** `sim(spectral-02): Run 01 results phase 1133`

---

### Phase 1134 — Run 01 Disposition (NON-SENSITIVE)

No GO token required. Human reviews before Phase 1135 proceeds.

**Deliverables:**
- `docs/sims/sim_spectral_02/run01_disposition_1134_v0.1.md`

**Required content:**
1. Summary of Run 01 findings per scenario (S1–S4)
2. k and weight profile recommendation for Run 02 (or null if Scenario C)
3. Answer to Q2: does Structural_Impedance add signal beyond existing λ₂ alert?
4. Answer to Q3: can combined terms distinguish durable coherence from fragile homogeneity?
5. Declared scenario for Run 02: A, B, or C (per §6 conditional note)
6. Run 02 parameter plan: narrowed k range, weight profile(s), gaming probe inclusion

**Closing token:** `sim_spectral_02_run01_disposition_committed_phase_1134`

**Test structure:** Minimum 2 tests:
- D1: disposition doc exists and contains closing token
- D2: disposition doc declares a scenario (A, B, or C) explicitly

**Commit subject:** `sim(spectral-02): Run 01 disposition phase 1134`

---

### Phase 1135 — SIM-SPECTRAL-02 Run 02 (NON-SENSITIVE)

No GO token required. Scope is conditional on Phase 1134 disposition.

**Deliverables:**
- `out/sim_spectral_02_run02_summary.json`
- `docs/sims/sim_spectral_02/run02_raw_notes_1135.md`

**All scenarios include gaming-resistance probes G1–G3.**

Per declared scenario:
- **Scenario A or B:** Fine sweep centered on Run 01 best-performing k/weight region. Seeds 42, 1337, 2026. All four scenarios S1–S4 plus gaming probes.
- **Scenario C:** Single k/weight profile (Run 01 best candidate). S1 + S3 only. Gaming probes G1–G3. Purpose: confirm null result is not workload-specific.

**Test structure:** Minimum 3 tests:
- R4: `out/sim_spectral_02_run02_summary.json` exists and is valid JSON
- R5: summary contains gaming probe results (G1–G3)
- R6: summary scenario count matches declared scenario (A/B → 4 scenarios; C → 2 scenarios)

**Commit subject:** `sim(spectral-02): Run 02 results phase 1135`

---

### Phase 1136 — Run 02 Disposition + ADR Draft (NON-SENSITIVE)

No GO token required. No CDL env var.

**Deliverables:**
- `docs/sims/sim_spectral_02/spectral_02_disposition_phase_1136.md` (always)
- `docs/adrs/adr_NNNN_relative_epistemic_energy_draft.md` (if evidence positive — Scenario A or B only)

**Required content for disposition doc:**
1. Final answers to all ten SIM-SPECTRAL-02 questions (Q1–Q10)
2. Recommended parameters: k, Durability_t weights, α/β/γ/δ coefficients — or explicit non-recommendation
3. Gaming-resistance verdict: is the signal gameable? By how much? Mitigation options if applicable
4. Answer to Q8: topology placement recommendation (QATPS multiplier / cost denominator / dashboard only) — advisory only, no rule change here
5. If Scenario A or B: ADR draft text for relative directional energy metrics KPI
6. If Scenario C: explicit research-direction closure statement
7. Closing token: `sim_spectral_02_disposition_complete_phase_1136`

**ADR draft (if produced):** Draft text only. Not ratified here. Must include: motivation, decision, consequences, and explicit gate condition ("this ADR requires human ratification in a subsequent window before any implementation").

**Test structure:** Minimum 4 tests:
- P1: disposition doc exists and contains closing token
- P2: disposition doc contains answers to all ten questions (assert presence of Q1–Q10 markers)
- P3: if ADR file exists, it contains `adr_relative_epistemic_energy_draft_not_ratified`
- P4: disposition doc does not contain `ILC_CDL_MUTATION_AUTHORIZED` (no CDL mutation happened)

**Commit subject:** `sim(spectral-02): Run 02 disposition + ADR recommendation phase 1136`

---

### Phase 1137 — Coherence Report + Capsule v5.38 (NON-SENSITIVE)

No GO token required.

**Deliverables:**
- `docs/specs/ilc_integration_coherence_report_1137_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.38.md`
- `tests/test_phase_1137_coherence_capsule_v5_38.py`

**Coherence report required sections:**
- §1 Purpose: Window 1130–1138 SIM-SPECTRAL-02 lane
- §2 SIM-SPECTRAL-02 outcome summary: declared scenario, key findings, disposition verdict
- §3 CDL chain unchanged: CDL-084 still the frontier; CDL-085 still SIM-gated
- §4 Runtime chain unchanged: `epoch_attribution_settle_runtime_1129_fix1.v0.5` still current (no `ilc_core/` mutations in this window)
- §5 Audit findings (or explicit: no findings — window clean)
- Closing token: `coherence_report_1137_verdict=pass`

**Capsule v5.38** supersedes v5.37. Opening tokens:
```
capsule_v5_38_supersedes_v5_37
window_1130_1138_sim_spectral_02_complete
sim_spectral_02_disposition_phase_1136
```

Capsule updates from v5.37:
- §1 frontier: Window 1130-1138 complete; Phase 1138 (closure gate) next
- §5 forward obligations: add SIM-SPECTRAL-02 disposition row; update CDL-085 row (SIM evidence now available if Scenario A or B)
- §6 test inventory: add Phase 1133/1135/1137 test files
- All other sections carry forward unchanged

**Test structure:** Minimum 6 tests covering capsule existence, opening tokens, coherence report verdict token, CDL-084 constants unchanged, SIM-SPECTRAL-02 disposition file exists.

**Commit subject:** `docs(coherence): phase 1137 coherence report + capsule v5.38`

---

### Phase 1138 — Window 1130–1138 Closure Gate (SENSITIVE)

**Requires explicit human GO token before execution.**

**Deliverables:**
- `tests/test_phase_1138_window_1130_1138_closure_gate.py`
- `docs/specs/ilc_window_1130_1138_handoff_1138_v0.1.md`
- `STATUS.md` update: Window 1130-1138 entry

**Gate tests (minimum 21):**

| Cat | Tests | Content |
|-----|-------|---------|
| 0 | 1 | Selftest guard: `ILC_PHASE_1138_GATE_SELFTEST=1` required |
| 1 | 3 | Sequence lock doc exists; all 9 phases listed; window_1130_1138_sequence_lock token present |
| 2 | 4 | SIM-SPECTRAL-02: program.md exists; run01 and run02 summaries exist; disposition doc exists with closing token |
| 3 | 4 | CDL-084 constants unchanged: `PROVENANCE_DECAY_ALPHA = Decimal("0.45")`; runtime version unchanged; no `ilc_core/` changes in this window |
| 4 | 4 | Capsule v5.38 exists; supersedes v5.37; contains SIM-SPECTRAL-02 disposition row |
| 5 | 3 | Coherence report exists with `coherence_report_1137_verdict=pass`; handoff doc exists |
| 6 | 2 | Scoped regression ≥ 289 (post-Fix1 baseline) + window 1130-1138 new test count; all window test files pass |

**Handoff doc required sections:**
1. Window identity and closure basis
2. SIM-SPECTRAL-02 outcome: scenario declared, key findings, disposition (recommendation or non-recommendation), ADR file path if produced
3. CDL-085 gate status: does SIM-SPECTRAL-02 evidence clear or remain SIM-gated?
4. Carry-forward items: CDL-085, SIM-HYPEREDGE-01, SIM-ECU-STABILITY-01, ADR-0035, star expansion
5. Next-window entry criteria and routing
6. MemPalace refresh disposition

**Commit subject:** `gate(window): phase 1138 window 1130-1138 closure gate`

---

## §9. Key Dependencies and Open Questions

### Must-resolve at window entry

| Dependency | Status |
|------------|--------|
| `out/sim_provenance_01_time_series.json` exists and is parseable | Confirmed — file present |
| `laplacian_analytics.py` calibration constants available | Confirmed — `THETA_FLOOR=0.001`, `N_BOOTSTRAP=44` |
| SIM-SPECTRAL-02 research plan (`ilc_relative_directional_energy_meter_and_epistemic_efficiency_plan_v0.1.md`) | Present at `7b3fb27e` |
| CDL-084 fully resolved | Confirmed — Phase 1129 |

### Sequencing constraints

1. Phase 1134 (disposition) must complete before Phase 1135 (Run 02) — scope is disposition-dependent
2. Phase 1135 must complete before Phase 1136 (final disposition)
3. Phase 1137 (coherence) must complete before Phase 1138 (closure gate)
4. Phase 1138 requires explicit human GO token

### Open questions (resolve during window)

- What fields are actually present in `out/sim_provenance_01_time_series.json`? Phase 1131 data audit resolves this — some Durability_t components may need synthetic proxies if not recorded
- Is `provenance_descendant_count` recorded per-node per-epoch in the time-series file, or only in summary? This determines Q10 addressability directly vs. indirectly
- ~~Harness location~~ **Resolved:** `tools/sim_spectral_02.py` follows `tools/sim_provenance_01.py` convention; `docs/sims/sim_spectral_02/` holds spec and disposition docs

### Permanently deferred (not in scope this window)

- CDL-085 opening (SIM-gated; evidence from this window informs but does not open it)
- Merkle-Laplacian dual commitment (research-only until SIM-SPECTRAL-02 proves signal)
- QATPS changes (advisory disposition only)
- Epoch commitment changes
- Conley Index formalization (pre-RC1.0)

---

## §10. Known Patterns and Technical Constraints

### Novel pattern: SIM-only window with no CDL or runtime mutation

This is the first window where no `ILC_CDL_MUTATION_AUTHORIZED` env var is used at any phase. The pre-commit hook is active but never triggered. Codex should not attempt to set the env var for any commit in this window.

### Structural_Impedance_t bounded transform (critical)

Do NOT use raw `1/λ₂` anywhere in the harness or analytics. Near bootstrap (`N < 44`, i.e., `N_BOOTSTRAP`), λ₂ can be near zero, causing the raw inverse to explode. Always use:
```
Structural_Impedance_t = max(0, THETA_FLOOR - λ₂_t) / THETA_FLOOR
```
This is bounded in `[0, 1]`. Confirmed pattern from SIM-SPECTRAL-01/H-005.

### x_i exponential form required (not linear)

`x_i = exp(-k * Durability_t)` is required, not the earlier linear sketch `1 - Durability_t`. Linear is unsafe: raw durability inputs (reuse count, provenance descendant count) are unbounded; a linear transform produces negative `x_i` in mature networks and causes squared Dirichlet terms to explode. Exponential keeps `x_i ∈ [0, 1]` always.

### Read-only constraint on existing spectral substrate

`laplacian_analytics.py`, `spectral_trajectory.py`, `local_spectral_analytics.py`, and `spectral_utils.py` must NOT be modified in this window. SIM-SPECTRAL-02 builds a new harness that calls or reads these as a reference; it does not extend them in-place. Any extensions to the analytics substrate are gated on positive SIM-SPECTRAL-02 evidence and belong in a follow-on window.

### Durability_t is aspirational — observed vs. synthetic must be labeled

`out/sim_provenance_01_time_series.json` records provenance descendant counts per node per epoch. It does NOT record `survived_refutations`, `validation_integrity`, or `path_uplift` — these are not emitted by the SIM-PROVENANCE-01 harness. Phase 1131 must audit what is actually available and declare each Durability_t component's data class (observed / synthetic / excluded). The SIM must not silently treat synthetic inputs as real ILC data. If the final disposition recommends a Durability_t formulation that relies predominantly on synthetic components, the recommendation must say so explicitly and call out the additional data capture required before the metric could be used operationally.

### Gaming-resistance probe design

G1–G3 probe scenarios are designed to distinguish metric improvement via genuine epistemic quality vs. strategic manipulation. The harness must be able to run gaming probes independently from the main scenarios. If the metric cannot distinguish G1–G3 from S1 (healthy growth), the disposition must note this clearly — it is a finding that bears on the ADR recommendation.

### Closure gate selftest guard chain

Phase 1138 gate must include `ILC_PHASE_1138_GATE_SELFTEST=1` in category 0. Prompt author must read prior closure gate test files directly rather than reasoning by analogy — each gate has distinct category 3 requirements.

---

## §11. Non-Goals and Explicitly Deferred Items

- No CDL opening, prelock, or ratification
- No `ilc_core/` runtime changes
- No settlement rule changes
- No QATPS parameter changes
- No epoch commitment changes
- No Merkle-Laplacian dual commitment work
- No CDL-085 opening (evidence from this window informs future authorization — it does not open the CDL)
- No SIM-HYPEREDGE-01 (separate lane)
- No SIM-ECU-STABILITY-01 (not authorized)
- No Star expansion work (H-011 patent gate)
- No ADR ratification or adoption — ADR draft text is permitted in Phase 1136 if evidence is positive (Scenario A or B), but the draft does not take effect this window; ratification requires a subsequent window with explicit human authorization
- No MemPalace modifications (rebuild runs in parallel outside the phase sequence)
- No Conley Index formalization (deferred pre-RC1.0)

---

## §12. Key Canonical Anchors for Prompt Drafting

Codex must reference these in every phase prompt:

- **(PRIMARY)** Capsule v5.37: `docs/specs/ilc_antigravity_context_capsule_v5.37.md`
- Window 1130-1138 sequence lock: `docs/specs/ilc_phase_1130_1138_sequence_lock_v0.1.md` (produced Phase 1130)
- Window 1124-1129 handoff: `docs/specs/ilc_window_1124_1129_handoff_1129_v0.1.md`
- SIM-SPECTRAL-02 research plan: `docs/research/ilc_relative_directional_energy_meter_and_epistemic_efficiency_plan_v0.1.md`
- SIM-SPECTRAL-02 signal definition: `docs/sims/sim_spectral_02/sim_spectral_02_signal_definition_v0.1.md` (produced Phase 1131)
- SIM-SPECTRAL-02 program: `docs/sims/sim_spectral_02/program.md` (produced Phase 1132)
- SIM-PROVENANCE-01 time-series: `out/sim_provenance_01_time_series.json`
- Laplacian analytics substrate: `ilc_core/analysis/laplacian_analytics.py` (read-only reference)
- CDL register: `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- Phase completion log: `STATUS.md`
- ADM-003 reference agent architecture: carry-forward unchanged (see capsule v5.37 §3)
- For closure gate (Phase 1138): all Phase 1130–1137 test files and artifact paths listed in §8.
