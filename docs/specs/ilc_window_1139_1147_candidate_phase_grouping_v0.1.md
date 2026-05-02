# ILC Window 1139-1147: Candidate Phase Grouping

**Author:** Claude Sonnet 4.6 (local architectural reviewer)
**Date:** 2026-05-02
**Baseline:** Window 1130-1138 CLOSED (Phase 1138 `961319bb`). CDL-084 fully resolved;
`PROVENANCE_DECAY_ALPHA = Decimal("0.45")` locked Phase 1126; runtime
`epoch_attribution_settle_runtime_1129_fix1.v0.5`. 358 tests passing. Capsule v5.38.
**Planning note:** This is a candidate grouping, not a locked sequence. Phases 1139–1146
are the hard minimum lane. Phase 1147 (closure gate) requires human GO token.

---

## §1. Window Identity and Scope

**Window:** 1139–1147
**Primary lanes:** (1) SIM-SPECTRAL-02 Run 02 Fix2 corrected baseline; (2) Genesis Atlas
Tier-1 curated seed patch; (3) SIM-SPECTRAL-03
**Character:** Simulation research + atlas patch. No CDL openings. No `ilc_core/` runtime
mutations. No settlement changes. No QATPS changes.

This window has three lanes that must execute in a specific order: the corrected Run 02
baseline first, Atlas Tier-1 second, and SIM-SPECTRAL-03 third. Each depends on the
previous.

**Lane 1 — Corrected baseline (Phases 1140–1141):** The SIM-SPECTRAL-02 Run 02 matrix
(333 entries, `a93da4f9`) was produced before the normalized-λ₂ / Greek-weights fix
(`58c4687f`). Run 02 used the **combinatorial** Laplacian λ₂ (unbounded) for the
structural impedance term; the fixed harness uses the **normalized** Laplacian λ₂
(bounded [0,2]). These are not the same metric — for any connected graph, combinatorial
λ₂ >> THETA_FLOOR (0.001), so the structural impedance term was silently dropped in
Run 02. The Phase 1136 Scenario B advisory is therefore provisional. A corrected Run 02
rerun using the fixed harness is required to establish a valid comparison baseline before
SIM-SPECTRAL-03 changes the seed topology. Slopes from Run 02 and the corrected run are
not directly comparable as quantitative values.

**Lane 2 — Atlas Tier-1 (Phases 1142–1143):** Add the ~10 missing authority-chain edges
to the curated seed to close the L2 basis-reachability gap (17/31 → ≥ 28/31). Run
GENESIS-COMPILE-01 checkpoint #1 to verify improvement. This patched star map becomes the
S1 topology seed for SIM-SPECTRAL-03.

**Lane 3 — SIM-SPECTRAL-03 (Phases 1144–1146):** Re-run SIM-SPECTRAL-02 with the patched
31-node Genesis star map as the S1 seed topology. Compare results against the corrected
Run 02 baseline (Phase 1140/1141) — not the broken Run 02. If the corrected SIM-SPECTRAL-03
shows materially improved S3 Sybil discrimination, Phase 1146 recommends CDL-085
authorization.

**Tail-slot policy:** Phase 1147 (closure gate) is SENSITIVE and requires explicit human
GO token. Phases 1139–1146 are all NON-SENSITIVE and may be Strike Forced in batches
subject to sequencing constraints.

---

## §2. Baseline and Inheritance

### Ratified CDL chain (relevant to this window)

| CDL | Status | Key constant |
|-----|--------|--------------|
| CDL-081 | Ratified | Hyperedge ECU attribution — `REUSE_ATTRIBUTION_RATE = Decimal("0.20")` |
| CDL-083 | Ratified | H-CON-02 panel quorum ejected stake |
| CDL-084 | Ratified | PROVENANCE chain attribution; `PROVENANCE_DECAY_ALPHA = Decimal("0.45")` locked Phase 1126 |

**Next fresh CDL number: CDL-085** — SIM-gated (Werner φ-bound). Requires SIM-SPECTRAL-03
positive result + human GO token. Not opened this window.

### Active runtime chain (no changes this window)

| Module | Version | Phase |
|--------|---------|-------|
| `epoch_attribution_settle_runtime.py` | `epoch_attribution_settle_runtime_1129_fix1.v0.5` | 1129 Fix1 |
| `CDL_084_DEPENDENCY` | `"cdl_084_provenance_chain_attribution_ratified_1113.v0.1"` | 1113 |
| `PROVENANCE_DECAY_ALPHA` | `Decimal("0.45")` — locked Phase 1126 | 1126 |

No `ilc_core/` file is a mutation target in this window. The pre-commit CDL mutation hook
is not triggered at any phase.

### Inherited canonical anchors

- Capsule v5.38: `docs/specs/ilc_antigravity_context_capsule_v5.38.md`
- Window 1130-1138 handoff: `docs/specs/ilc_window_1130_1138_handoff_1138_v0.1.md`
- Window 1130-1138 sequence lock: `docs/specs/ilc_phase_1130_1138_sequence_lock_v0.1.md`
- Planning bridge (§3 gap registry and §4 window sequence): `docs/specs/ilc_window_1130_1138_to_rc_planning_bridge_v0.1.md`
- Run 02 corrected-baseline motivation: `out/sim_spectral_02_run02_summary.json`
  (333 entries; produced with combinatorial λ₂ — structural impedance term was silently
  zero throughout Run 02; see §4.1 for full explanation)
- Fixed harness commit: `58c4687f` — normalized-λ₂ + Greek-weights fix
- SIM-SPECTRAL-02 program spec: `docs/sims/sim_spectral_02/program.md`
- Run 02 disposition (provisional): `docs/sims/sim_spectral_02/run02_disposition_1136_v0.1.md`
- Genesis curated seed (Tier-1 mutation target): `docs/sims/sim_spectral_02/genesis_core_star_map_curated_seed_v0.1.json`
- Genesis core star map (to be regenerated): `out/genesis_core_star_map_v0.1.json`
- GENESIS-COMPILE-01 baseline output: `out/genesis_compile_coverage_diagnostic_v0.1.json`
- GENESIS-COMPILE-01 tool chain: `tools/crawl_genesis_node_candidates.py`,
  `tools/compare_genesis_star_map_to_repo_graph.py`,
  `tools/genesis_compile_coverage_diagnostic.py`
- Gap registry (Bucket 1 — Tier-1 unreachable nodes): planning bridge §3 Bucket 1
- SIM-SPECTRAL-02 signal definition: `docs/sims/sim_spectral_02/sim_spectral_02_signal_definition_v0.1.md`

---

## §3. Track Inventory

### Constitutionally obligated

None. CDL-084 fully discharged Window 1124-1129. No outstanding constitutional obligations
entering this window.

### Deferred governance

| Item | Status | Gate |
|------|--------|------|
| CDL-085 (Werner φ-bound) | SIM-gated | SIM-SPECTRAL-03 + human GO token required |
| ADR-0035 implementation CDL | Planning/authorization gated | Not this window |
| Star expansion | H-011 patent gate + human authorization | Not this window |
| SIM-ECU-STABILITY-01 | Candidate — not authorized | Not this window |
| SIM-HYPEREDGE-01 | Gate clear (CDL-083 ✓) — not scheduled | Window 1148+ |
| Conley Index research | Deferred pre-RC1.0 | Archived |

### Simulation-conditional

| SIM | Status | CDL downstream |
|-----|--------|----------------|
| **SIM-SPECTRAL-02 Run 02 Fix2** | **This window — active (corrected baseline)** | Supersedes broken Run 02 as comparison basis |
| **SIM-SPECTRAL-03** | **This window — active (pending corrected baseline + Atlas Tier-1)** | CDL-085 gate condition |

---

## §4. Run 02 Fix2 Corrected Baseline Scope

### 4.1 Why this is required

The original SIM-SPECTRAL-02 Run 02 (commit `a93da4f9`, 2026-05-01 19:56) ran with two
silent bugs in the harness:

1. **Laplacian type mismatch.** The harness computed a **combinatorial** Laplacian
   λ₂ and passed it to `compute_structural_impedance()`. The combinatorial λ₂ is
   unbounded — for any connected graph it greatly exceeds `THETA_FLOOR` (0.001), so
   `max(0.0, THETA_FLOOR - λ₂)` always returned 0.0. The structural impedance term was
   silently dropped; the V_t formula that ran was effectively
   `V_t = el_x + mean_x + 0 + contention`. The fixed harness computes the **normalized**
   Laplacian λ₂ (bounded [0,2]), which is a different metric. Slopes from Run 02
   and the corrected run are **not directly comparable** as quantitative values.

2. **Greek weights not exposed.** The CLI did not accept `--alpha`, `--beta`, `--gamma`,
   `--delta`. All four calibration weights were hardcoded to 1.0; the β calibration probe
   in Phase 1136 was possible only because the fix (`58c4687f`) landed before the
   disposition was written.

The fix (`58c4687f`, 2026-05-02 07:47) corrected both bugs: `_normalized_lambda2`
computes the symmetric normalized Laplacian (bounded [0, 2]) for structural impedance,
and all four Greek weights are exposed as CLI parameters. All 8 tests in
`tests/test_phase_1133_sim_spectral_02_fix2.py` pass with the fixed harness.

**Consequence for CDL-085 gating:** The slope values from Run 02 (S1=+0.557, S2=+0.214,
S3=+0.358, S4=+0.246, G2=+0.481) and the S3/S1 ratio (0.647) are from a formula missing
one of its four terms. The Scenario B advisory is directionally plausible but is not a
valid quantitative baseline for CDL-085 gate conditions. The corrected rerun establishes
that baseline.

### 4.2 Corrected rerun specification (Phase 1140)

Rerun the same 333-entry matrix using the fixed harness (`58c4687f`) with identical
parameters:

- Same seed topology (3 Genesis axioms + 97 synthetic artifacts — homoiconic model)
- Same seeds: 42, 1337, 2026
- Same k values and weight profiles from the committed Run 02 matrix
- Same scenarios: S1, S2, S3, S4, G1, G2, G3 in same track groupings (A/B/C/D)
- All four Greek weights at defaults (α=β=γ=δ=1.0) for the base comparison matrix
- Output to `out/sim_spectral_02_run02_fix2_summary.json`

The corrected run must NOT change the seed topology, scenario definitions, or k/weight
values from Run 02. The only change is the harness version. This isolates the formula
fix as the single variable.

### 4.3 Corrected disposition addendum (Phase 1141)

Phase 1141 produces a corrected disposition document that:

1. Tabulates old vs. corrected slope values per scenario and track group
2. Re-establishes the S3/S1 ratio from the corrected data
3. Updates the Scenario B/C verdict (or confirms it survives the correction)
4. Declares the corrected S3/S1 ratio as the operative gate number for CDL-085
   (i.e., replaces the 0.647 figure from the broken run)
5. Notes whether the structural impedance term contributed meaningfully to any scenario
   after the fix (i.e., was there any epoch where λ₂ < THETA_FLOOR for connected graphs?)

The corrected disposition becomes the comparison baseline for SIM-SPECTRAL-03.

**Expected finding:** For typical connected graphs in the simulation, the normalized λ₂
will likely remain above THETA_FLOOR (0.001), meaning structural impedance may still be
near zero in most epochs. If so, the corrected disposition should document this as a
calibration finding — the THETA_FLOOR may need tuning for the simulation's graph density
range, or γ may need elevation to amplify the structural impedance signal. This
calibration question is within scope for Phase 1141 commentary but should NOT result in
a new parameter sweep — that belongs in SIM-SPECTRAL-03 if warranted.

---

## §5. Genesis Atlas Tier-1 Scope

### 5.1 What Tier-1 means (Genesis attestation node + diagnostic restructure)

The Genesis core star map (`out/genesis_core_star_map_v0.1.json`, 31 nodes, 35 edges) is
a projection of the governance hypergraph onto a core authority set. GENESIS-COMPILE-01
baseline reports 17/31 `basis_reachable_core_nodes` via single-class forward BFS.

**Key finding (confirmed by Codex):** The 14 unreachable nodes reflect a limitation of
single-class BFS, not an absence of genesis authority. The clean fix is:
1. A **retrospective Genesis attestation document** (`docs/specs/ilc_genesis_intent_attestation_and_init_authority_map_v0.1.md`) that formally records the pre-repo Genesis intent as the root of project authority
2. A new star-map **node-promotion** (`artifact:genesis_intent_attestation_init_authority_map`) sourced from that document
3. **GOVERNS/ATTESTATION edges** from the attestation node to all currently-unreachable governance artifacts
4. **Restructured GENESIS-COMPILE-01** that reports `derivation_reachability` and `authority_traceability` as separate classes

**The graph must model actual authority structure. Do not add edges to satisfy a traversal
metric; add edges because the authority relationship genuinely exists.**

**Genesis attestation document — required properties:**
- `attested_by`: Genesis / Jamison
- `status`: `RETROSPECTIVE_GENESIS_ATTESTATION`
- Purpose: records the Genesis intent that preceded repo concretization; formalizes
  the pre-existing authority relationships for atlas/RC compilation
- `created_after_fact: true`; `intent_scope_start: pre-repo conception period`
- Explicit `limits`: does not claim this file existed at repo initialization; does not
  rewrite file timestamps or commit history
- `applies_to`: all ADR, CDL, policy, keygen artifacts governed by Genesis intent

**New curated seed node:**
- `candidate_id: artifact:genesis_intent_attestation_init_authority_map`
- `canonicality_tier: retrospective_genesis_attestation`
- `source_kind: genesis_attestation`; `node_kind: authority_map`
- `core_star_map_candidate: true`
- Star map grows from 31 → 32 nodes

**Edges from the attestation node** (GOVERNS = authorizes/scope-binds; ATTESTATION =
attests to existence/authenticity of identity artifacts; NOT PROVENANCE):

| Edge type | Target |
|-----------|--------|
| GOVERNS | `adr:0004_genesis_truth_primitives` |
| GOVERNS | `adr:0029_hypergraph_substrate` |
| GOVERNS | `adr:0030_node_embedding_substrate` |
| GOVERNS | `adr:0032_temporal_hypergraph` |
| GOVERNS | `adr:0035_homoiconic_type_definition_system` |
| GOVERNS | `cdl:081_hyperedge_ecu_attribution` |
| GOVERNS | `cdl:083_panel_quorum_refutation` |
| GOVERNS | `cdl:084_provenance_chain_attribution` |
| GOVERNS | `policy:genesis_accrual_governor` |
| GOVERNS | `policy:genesis_authority_sunset` |
| GOVERNS | `policy:genesis_theta_hard_0_05` |
| GOVERNS | `policy:genesis_theta_soft_exp_minus_3` |
| GOVERNS | `policy:provenance_decay_alpha_0_45` |
| ATTESTATION | `ceremony:genesis_agent1_keygen_838a` |
| ATTESTATION | `artifact:genesis_agent1_pubkey_record_838a` |
| ATTESTATION | `genesis_agent:01` |

Do NOT use PROVENANCE for any of these edges (PROVENANCE = historical derivation/lineage,
not intent-authorization). Do NOT add fake intermediate nodes.

### 5.2 Regeneration chain (Phase 1142)

After creating the attestation document and editing the curated seed:
```bash
python tools/crawl_genesis_node_candidates.py
python tools/compare_genesis_star_map_to_repo_graph.py
# Phase 1142 also modifies genesis_compile_coverage_diagnostic.py — then run:
python tools/genesis_compile_coverage_diagnostic.py
```

Output paths:
- `out/genesis_core_star_map_v0.1.json` (updated — 32 nodes after attestation node)
- `out/genesis_compile_coverage_diagnostic_v0.1.json` (updated — new reachability classes)
- `out/genesis_core_star_map_gap_analysis_v0.1.json` (updated in-place)

### 5.3 GENESIS-COMPILE-01 checkpoint #1 (Phase 1143)

Phase 1143 gates on `authority_traceable_core_nodes ≥ 28/32`. The diagnostic reports:
- `derivation_reachability`: forward BFS from truth primitives/axioms/genesis hard-coded
  roots (the existing single-BFS class, kept for continuity)
- `authority_traceability`: nodes reachable via GOVERNS/ATTESTATION from
  `artifact:genesis_intent_attestation_init_authority_map`

Phase 1143 also explicitly asserts: `0 semantically unjustified Tier-1 edges` — confirming
that the graph was not shaped to satisfy a traversal metric.

The 32-node patched star map + restructured diagnostic become the S1 topology baseline
for SIM-SPECTRAL-03.

---

## §6. SIM-SPECTRAL-03 Scope

### 6.1 Research question

Can the patched 32-node Genesis core star map — representing the actual ILC protocol
governance topology including the retrospective genesis intent attestation — serve as a
more realistic S1 (healthy growth) seed topology than 3 Genesis axioms + 97 synthetic
artifacts, and does this change materially improve S3 Sybil discrimination relative to
the corrected Run 02 baseline?

This is the operative CDL-085 gate question. If S3/S1 ratio under Genesis-seed S1
drops materially below the corrected Run 02 S3/S1 ratio, Phase 1146 recommends CDL-085
authorization.

### 6.2 Scope

SIM-SPECTRAL-03 re-runs SIM-SPECTRAL-02 Track A + all gaming probes (S3, G2 are the
critical discriminators for the CDL-085 gate), plus S1/S2/S4/G1/G3 for completeness.
Track B/C (alternative topology tracks) and Track D (connectivity sweep) are optional
if the window is time-constrained — Track A + gaming probes are the minimum.

**What changes vs. Run 02:**
- S1 topology seed: 32-node patched Genesis core star map (from Phase 1142/1143,
  including genesis intent attestation node) instead of 3 Genesis axioms + 97 synthetic artifacts

**What does NOT change:**
- Harness version: same fixed harness (`58c4687f`)
- Greek weights: α=β=γ=δ=1.0 base matrix (same as corrected Run 02)
- k values and weight profiles: same as Run 02 (to isolate topology variable)
- Scenario definitions: S1/S2/S3/S4/G1/G2/G3 unchanged
- Seeds: 42, 1337, 2026

**One variable at a time:** The corrected Run 02 baseline (Phase 1140) isolates the
formula fix. SIM-SPECTRAL-03 then isolates the topology change. This two-step approach
ensures any change in slope values or S3/S1 ratio can be attributed to the correct cause.

### 6.3 CDL-085 gate condition

The Phase 1146 disposition recommends CDL-085 authorization if:
1. SIM-SPECTRAL-03 S3/S1 ratio (Track A, corrected formula) drops materially below the
   corrected Run 02 S3/S1 ratio established in Phase 1141. "Materially" means a sustained
   reduction across at least 2 of 3 seeds; a single-seed result is not sufficient.
2. The V_t slope for S1 under Genesis seed is positive and larger than the corrected
   Run 02 S1 slope.
3. G2 (coordinated PROVENANCE reuse) discrimination also improves or holds steady.

If any of these three conditions fails, Phase 1146 produces a conditional or negative
recommendation, and CDL-085 authorization is deferred to SIM-SPECTRAL-04 or an
alternative research path.

### 6.4 Output files

| File | Description |
|------|-------------|
| `out/sim_spectral_03_run01_summary.json` | SIM-SPECTRAL-03 results (Track A + probes minimum) |
| `docs/sims/sim_spectral_03/run01_raw_notes_1145.md` | Raw run notes |
| `docs/sims/sim_spectral_03/disposition_1146_v0.1.md` | Disposition + CDL-085 recommendation |

Create `docs/sims/sim_spectral_03/` directory in Phase 1144 (harness update).

---

## §7. CDL Number Assignments

| CDL | Title (candidate) | Decision digest anchor | Opening phase | Ratification phase |
|-----|-------------------|----------------------|---------------|-------------------|
| CDL-085 | Werner φ-bound epistemic efficiency KPI | TBD — SIM-SPECTRAL-03 evidence required | Not this window | Not this window |

**Note:** CDL-085 authorization requires SIM-SPECTRAL-03 positive result + human GO token.
Authorization is NOT the same as opening — authorization is the human decision to allow
CDL-085 to open; the opening itself is Phase 1149 (Window 1148+). Phase 1146 produces
the recommendation; human authorizes (or defers) before Window 1148 guidance is drafted.

No CDL mutations occur in Window 1139-1147. `ILC_CDL_MUTATION_AUTHORIZED` is not
required for any phase.

---

## §8. Candidate Phase Table

| Order | Phase | Topic | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 1139 | Window 1139–1147 sequence lock | Foundation | NON-SENSITIVE |
| 2 | 1140 | SIM-SPECTRAL-02 Run 02 Fix2 corrected baseline (333-entry rerun, fixed harness) | Simulation | NON-SENSITIVE |
| 3 | 1141 | Corrected Run 02 disposition addendum — old vs. corrected slopes; updated Scenario B/C verdict | Synthesis | NON-SENSITIVE |
| 4 | 1142 | Atlas Tier-1: genesis intent attestation node + diagnostic restructure (32-node star map) | Atlas/Sim | NON-SENSITIVE |
| 4S | 1142s | Genesis node attestation signing ceremony — ML-DSA-65 manifest signature by genesis_agent:01 | Signing | **SENSITIVE** |
| 5 | 1143 | GENESIS-COMPILE-01 checkpoint #1 — authority_traceability class, 32-node post-Tier-1 | Simulation | NON-SENSITIVE |
| 6 | 1144 | SIM-SPECTRAL-03 harness update + program spec (32-node Genesis seed topology) | Simulation | NON-SENSITIVE |
| 7 | 1145 | SIM-SPECTRAL-03 Run 01 (Track A + gaming probes minimum) | Simulation | NON-SENSITIVE |
| 8 | 1146 | SIM-SPECTRAL-03 disposition + CDL-085 authorization recommendation | Synthesis | NON-SENSITIVE |
| 9 | 1147 | Coherence + capsule v5.39 + closure gate | Gate | **SENSITIVE** |

### Strike Force batch groupings

| Batch | Phases | Rationale |
|-------|--------|-----------|
| **Batch A** | 1139 + 1140 | Sequence lock + corrected rerun; no disposition decision needed between them |
| **Batch B** | 1141 alone | Disposition addendum must be reviewed before Atlas work proceeds |
| **Batch C** | 1142 alone | Genesis attestation node + diagnostic restructure — output reviewed before signing |
| **Batch C-S** | 1142s alone | SENSITIVE signing ceremony — requires human GO token + human local key ceremony |
| **Batch D** | 1143 alone | Checkpoint requires Phase 1142s signature artifact to be present |
| **Batch E** | 1144 alone | Harness update depends on checkpoint #1 passing; must confirm before SIM runs |
| **Batch F** | 1145 alone | Computational phase; results may require human review before disposition |
| **Batch G** | 1146 alone | Disposition may trigger CDL-085 authorization decision; human review before closure |
| **Batch H** | 1147 alone | SENSITIVE — human GO token required |

### Note on Phase 1143 gate

Phase 1143 is a hard gate. `authority_traceable_core_nodes ≥ 28/32` is required. If the
attestation node edges did not produce ≥ 28/32 authority-traceable nodes, add more
GOVERNS/ATTESTATION edges to the curated seed (Phase 1142 iteration). Do NOT add
BFS-gaming edges. Phase 1142s (signing) must have completed before Phase 1143 proceeds —
the checkpoint report includes the signature manifest reference.

### Note on SIM-SPECTRAL-03 scope (Phases 1145–1146)

If SIM-SPECTRAL-03 Run 01 results are ambiguous (e.g., S3/S1 improvement is marginal or
seed-dependent), Phase 1146 scope may require a Run 02 (fine sweep). If that becomes
necessary, the window will need to extend or Phase 1147 will become a provisional closure
gate. Codex must flag this to the human if Run 01 results are inconclusive.

---

## §9. Sensitivity Classification

### SENSITIVE phases

- **Phase 1142s — Genesis signing ceremony:** Cryptographic event. Requires explicit
  human GO token before execution. Human (Jamison) must perform the local ML-DSA-65
  signing ceremony to produce the signature artifact. Agents must not handle private
  key material.
- **Phase 1147 — Closure gate:** Structural window boundary. Requires explicit human GO
  token before execution. No CDL mutation, but classified SENSITIVE per standard
  closure-gate policy.

### NON-SENSITIVE phases

- **Phase 1139 — Sequence lock:** Doc-only. No CDL mutation. No `ilc_core/` changes.
- **Phase 1140 — Corrected Run 02 rerun:** Executes `tools/sim_spectral_02.py` (fixed
  harness). Writes `out/sim_spectral_02_run02_fix2_summary.json`. No mutation of any
  governed file. No CDL.
- **Phase 1141 — Corrected disposition addendum:** Analysis document only. No `ilc_core/`
  changes. No CDL env var.
- **Phase 1142 — Atlas Tier-1 patch:** Edits the curated seed JSON and regenerates
  `out/` atlas files. The curated seed is a research artifact, not a governed runtime
  file. No `ilc_core/` changes. No CDL.
- **Phase 1143 — GENESIS-COMPILE-01 checkpoint #1:** Runs diagnostic tool chain.
  Read-only analysis; updates `out/` JSON artifacts in-place. No `ilc_core/` changes.
  No CDL.
- **Phase 1144 — SIM-SPECTRAL-03 harness update:** Creates `docs/sims/sim_spectral_03/`
  directory and program spec. Updates harness (or creates new harness variant). No
  `ilc_core/` changes. No CDL.
- **Phase 1145 — SIM-SPECTRAL-03 Run 01:** Executes harness. Writes
  `out/sim_spectral_03_run01_summary.json`. No mutation.
- **Phase 1146 — SIM-SPECTRAL-03 disposition:** Analysis document. CDL-085 recommendation
  (advisory only — not an opening). No CDL env var. No `ilc_core/` changes.

### Conditional phases rule

All phases 1139–1146 are NON-SENSITIVE. Phase 1147 is SENSITIVE. No CDL conditional
branching applies because no CDL opens or ratifies in this window. However, Phases 1144
and 1145 are **sequencing-conditional** on Phase 1143 result: Codex must not proceed
past Phase 1143 until GENESIS-COMPILE-01 checkpoint #1 confirms ≥ 28/31
basis-reachable core nodes. If the checkpoint fails, Phase 1142 iterates before 1144
proceeds.

### Pre-commit hook

The `ILC_CDL_MUTATION_AUTHORIZED` hook is **not required for any phase** in
Window 1139-1147. No CDL mutations occur in this window.

---

## §10. Scope Notes for Fixed Phases

### Phase 1139 — Window 1139–1147 Sequence Lock (NON-SENSITIVE)

No GO token required. Doc-only commit.

**Deliverables:**
- `docs/specs/ilc_phase_1139_1147_sequence_lock_v0.1.md`

**Required content tokens:**
```
window_1139_1147_sequence_lock_committed_phase_1139
run02_fix2_corrected_baseline_phase_1140
atlas_tier1_patch_phase_1142
genesis_compile_checkpoint_1_phase_1143
sim_spectral_03_phases_1144_1146
window_1139_1147_closure_gate_phase_1147_sensitive
```

Phase table (6 columns): Order / Phase / Topic / Character / Sensitivity / Batch.

Constraints to enumerate:
1. No CDL opening in this window
2. No `ilc_core/` runtime mutations in this window
3. Run 02 Fix2 corrected baseline (Phase 1140) must complete before Atlas Tier-1 (Phase 1142)
4. Atlas Tier-1 (Phase 1142) must complete and pass GENESIS-COMPILE-01 checkpoint #1
   (Phase 1143) before SIM-SPECTRAL-03 harness work begins (Phase 1144)
5. Phase 1147 (closure gate) requires explicit human GO token
6. The corrected Run 02 baseline — not the original Run 02 — is the operative comparison
   baseline for SIM-SPECTRAL-03

**Commit subject:** `docs(seq-lock): window 1139-1147 sequence lock`

---

### Phase 1140 — Run 02 Fix2 Corrected Baseline (NON-SENSITIVE)

No GO token required.

**Deliverables:**
- `out/sim_spectral_02_run02_fix2_summary.json` — 333-entry rerun with fixed harness
- `docs/sims/sim_spectral_02/run02_fix2_raw_notes_1140.md` — brief narrative of rerun

**Rerun specification:**
- Harness: `tools/sim_spectral_02.py` at current HEAD (post-`58c4687f`)
- Seed topology: homoiconic model (3 Genesis axioms + 97 synthetic artifacts) — same as Run 02
- All parameters identical to Run 02 matrix (same k values, weight profiles, seeds,
  scenarios, track groupings)
- Greek weights: α=β=γ=δ=1.0 (defaults; do not vary in this rerun)
- All 333 matrix entries must be re-run; partial reruns are not acceptable

**Raw notes must include:**
1. Confirmation that the harness version is post-`58c4687f`
2. Sample of 3–5 entries showing non-zero `structural_impedance_per_epoch` values
   (if λ₂ < THETA_FLOOR is never triggered in connected graphs, notes must say so
   explicitly and report the minimum observed normalized λ₂ across all entries)
3. Any infrastructure differences from the original Run 02

**Test structure:** Minimum 4 tests:
- F1: `out/sim_spectral_02_run02_fix2_summary.json` exists and is valid JSON
- F2: entry count == 333
- F3: at least one entry has `v_t_per_epoch` values that differ from the corresponding
  Run 02 entry (confirms the formula changed — delta may be small but must be non-zero
  if structural impedance ever activated; if structural_impedance is still all-zeros,
  test must assert this explicitly and the raw notes must explain why)
- F4: `docs/sims/sim_spectral_02/run02_fix2_raw_notes_1140.md` exists and contains
  `run02_fix2_corrected_baseline_committed_phase_1140`

**Commit subject:** `sim(spectral-02): Run 02 Fix2 corrected baseline phase 1140`

---

### Phase 1141 — Corrected Run 02 Disposition Addendum (NON-SENSITIVE)

No GO token required.

**Deliverables:**
- `docs/sims/sim_spectral_02/run02_fix2_disposition_addendum_1141_v0.1.md`

**Required content:**
1. Side-by-side slope table: original Run 02 vs. corrected Run 02, per scenario and track
   group (S1/S2/S3/S4/G1/G2/G3 × Track A minimum)
2. Corrected S3/S1 ratio — this becomes the operative gate number for CDL-085. Supersedes
   0.647 from the broken Run 02. If the corrected ratio is > 0.647, the Scenario B
   advisory weakens; if < 0.647, it strengthens.
3. Updated Scenario B/C verdict: does the corrected run support, weaken, or overturn
   the Phase 1136 advisory?
4. Structural impedance calibration note: what fraction of epochs saw non-zero structural
   impedance? Was THETA_FLOOR (0.001) ever triggered? If not, what was the minimum
   normalized λ₂ observed, and what THETA_FLOOR value would engage the term in future runs?
5. Explicit statement: "The corrected Run 02 slope values in this document supersede the
   Run 02 values in `docs/sims/sim_spectral_02/run02_disposition_1136_v0.1.md` as the
   operative comparison baseline for SIM-SPECTRAL-03."
6. CDL-085 gate threshold declaration: state the corrected S3/S1 ratio and the improvement
   threshold required for CDL-085 recommendation in Phase 1146.

**Closing token:** `run02_fix2_disposition_addendum_committed_phase_1141`

**Test structure:** Minimum 4 tests:
- A1: addendum doc exists and contains closing token
- A2: addendum contains both "original" and "corrected" slope table (assert presence of
  both keywords)
- A3: addendum declares a corrected S3/S1 ratio (numeric value present in doc)
- A4: addendum explicitly states it supersedes Phase 1136 Run 02 values

**Commit subject:** `sim(spectral-02): Run 02 Fix2 disposition addendum phase 1141`

---

### Phase 1142 — Atlas Tier-1: Genesis Attestation Node + Diagnostic Restructure (NON-SENSITIVE)

No GO token required.

**Deliverables:**
- `docs/specs/ilc_genesis_intent_attestation_and_init_authority_map_v0.1.md` (new)
- `docs/sims/sim_spectral_02/genesis_core_star_map_curated_seed_v0.1.json` (amended — new node + 16 edges)
- `out/genesis_core_star_map_v0.1.json` (regenerated — 32 nodes)
- `out/genesis_core_star_map_gap_analysis_v0.1.json` (regenerated)
- `tools/genesis_compile_coverage_diagnostic.py` (updated — derivation + authority classes)
- `out/genesis_compile_coverage_diagnostic_v0.1.json` (regenerated — new classes block)
- `tests/test_phase_1142_atlas_tier1_genesis_attestation.py`

**See Phase 1142 prompt in `docs/Antigravity_tasks/` for full specification.**

**Commit subject:** `atlas(tier-1): genesis attestation node + diagnostic restructure phase 1142`

---

### Phase 1143 — GENESIS-COMPILE-01 Checkpoint #1 (NON-SENSITIVE)

No GO token required.

**Deliverables:**
- `docs/sims/sim_spectral_02/genesis_compile_checkpoint_1_1143_v0.1.md` — checkpoint
  evidence report
- `tests/test_phase_1143_genesis_compile_checkpoint_1.py` — evidence tests

**Checkpoint report required content:**
1. Reachability class summary: `derivation_reachability` count and `authority_traceability` count
2. `core_explainable_sources_ratio_of_observed` (compare to 31% baseline)
3. For each of the 14 previously-unreachable nodes: which class now covers it (or why uncovered)
4. `basis_reachable_core_nodes` (legacy single-BFS count, for continuity)
5. Explicit assertion: `0 semantically unjustified Tier-1 edges added`
6. Verdict token:
   - `genesis_compile_checkpoint_1_pass` if `authority_traceable_core_nodes ≥ 28/32`
   - `genesis_compile_checkpoint_1_conditional` if authority_traceable 22–27/32 and diagnostic is valid
   - `genesis_compile_checkpoint_1_fail_iteration_required` if diagnostic restructure absent or broken
7. Approval statement: patched 32-node star map + restructured diagnostic approved as S1
   topology baseline for SIM-SPECTRAL-03 (if verdict not fail)

**Test structure:** Minimum 5 tests:
- C1: checkpoint report exists and contains a verdict token
- C2: `out/genesis_compile_coverage_diagnostic_v0.1.json` contains `authority_traceability` key
- C3: `authority_traceable_core_nodes ≥ 28` (hard gate — test fails if < 28 out of 32)
- C4: report accounts for all 14 previously-unreachable nodes
- C5: report contains `atlas_tier1_patch_phase_1142` reference

**Gate rule:** C3 failing → Phase 1142 iterates (add more attestation edges, not BFS-gaming
edges). C2 failing → diagnostic restructure not landed; do not proceed.

**Commit subject:** `atlas(checkpoint-1): GENESIS-COMPILE-01 checkpoint 1 phase 1143`

---

### Phase 1144 — SIM-SPECTRAL-03 Harness Update (NON-SENSITIVE)

No GO token required. Prerequisite: Phase 1143 gate passed (≥ 28/31).

**Deliverables:**
- `docs/sims/sim_spectral_03/` directory (create if not exists)
- `docs/sims/sim_spectral_03/program.md` — SIM-SPECTRAL-03 program spec
- Harness update: `tools/sim_spectral_02.py` updated to accept `--s1-topology-file`
  parameter pointing to a JSON star map, OR a new `tools/sim_spectral_03.py` harness
  that imports the patched star map as the S1 topology seed. The choice is Codex's, but
  the SIM-SPECTRAL-03 run must use the patched 31-node star map as S1 seed.

**Program spec (program.md) must include:**
1. The single research question: does Genesis-seed S1 topology improve S3/S1
   discrimination relative to the corrected Run 02 baseline?
2. S1 topology source: `out/genesis_core_star_map_v0.1.json` (post-Tier-1 patch)
3. Pass/fail thresholds: SIM-SPECTRAL-03 recommends CDL-085 if
   S3/S1 ratio (Track A, corrected formula) drops materially below the corrected
   Run 02 S3/S1 ratio from Phase 1141
4. What "materially" means: sustained reduction across ≥ 2 of 3 seeds; single-seed
   result is not sufficient
5. Minimum run scope: Track A + all gaming probes (S3, G2 are primary discriminators;
   S1/S2/S4/G1/G3 for completeness)
6. Output file: `out/sim_spectral_03_run01_summary.json`
7. Token: `sim_spectral_03_program_committed_phase_1144`

**Test structure:** Minimum 4 tests:
- P1: `docs/sims/sim_spectral_03/program.md` exists with token
- P2: harness accepts a star map file as S1 topology input (or sim_spectral_03.py exists)
- P3: harness can load `out/genesis_core_star_map_v0.1.json` without error
- P4: `docs/sims/sim_spectral_03/` directory exists

**Commit subject:** `sim(spectral-03): harness update + program spec phase 1144`

---

### Phase 1145 — SIM-SPECTRAL-03 Run 01 (NON-SENSITIVE)

No GO token required. Prerequisite: Phase 1144 complete.

**Deliverables:**
- `out/sim_spectral_03_run01_summary.json`
- `docs/sims/sim_spectral_03/run01_raw_notes_1145.md`

**Run scope:** Track A + all gaming probes minimum. Same k values and weight profiles as
corrected Run 02 (Phase 1140). Seeds 42, 1337, 2026. α=β=γ=δ=1.0.
S1 seed topology: patched 31-node Genesis core star map.

**Raw notes must include:**
1. Confirmation of S1 topology source file and node count
2. S1/S3/G2 slopes (Track A) per seed — these are the primary CDL-085 gate inputs
3. Any anomalies during the run

**Test structure:** Minimum 4 tests:
- R1: `out/sim_spectral_03_run01_summary.json` exists and is valid JSON
- R2: results contain entries for all required scenarios (S1, S2, S3, S4, G1, G2, G3
  at minimum for Track A)
- R3: raw notes exist and contain `sim_spectral_03_run01_committed_phase_1145`
- R4: at least one entry confirms `s1_topology` field references Genesis seed
  (not the 3-axiom synthetic seed from Run 02)

**Commit subject:** `sim(spectral-03): Run 01 results phase 1145`

---

### Phase 1146 — SIM-SPECTRAL-03 Disposition (NON-SENSITIVE)

No GO token required. No CDL env var. Human reviews before Phase 1147 closure gate.

**Deliverables:**
- `docs/sims/sim_spectral_03/disposition_1146_v0.1.md`

**Required content:**
1. Comparison table: corrected Run 02 slopes (from Phase 1141) vs. SIM-SPECTRAL-03 slopes,
   per scenario and seed
2. Corrected S3/S1 ratio under Genesis seed, per seed; multi-seed summary
3. CDL-085 recommendation: one of:
   - **RECOMMEND** — S3/S1 improvement satisfies Phase 1144 program spec thresholds;
     human GO token needed before CDL-085 opens in Window 1148
   - **CONDITIONAL** — improvement is present but below threshold or seed-dependent;
     state conditions required before authorization
   - **DEFER** — no improvement or regression; CDL-085 remains SIM-gated; state next
     research step
4. G2 (coordinated reuse) and S2 (partition) disposition alongside S3
5. THETA_FLOOR calibration note (carry-forward from Phase 1141 findings)
6. Genesis seed topology assessment: did the 31-node seed produce a more realistic S1
   trajectory than the 3-axiom synthetic seed?
7. Closing token: `sim_spectral_03_disposition_committed_phase_1146`

**Test structure:** Minimum 4 tests:
- D1: disposition doc exists with closing token
- D2: disposition contains a CDL-085 recommendation verdict (RECOMMEND, CONDITIONAL, or DEFER)
- D3: disposition contains corrected Run 02 comparison table
- D4: disposition does not contain `ILC_CDL_MUTATION_AUTHORIZED` (no CDL mutation happened)

**Commit subject:** `sim(spectral-03): disposition + CDL-085 recommendation phase 1146`

---

### Phase 1147 — Window 1139–1147 Closure Gate (SENSITIVE)

**Requires explicit human GO token before execution.**

**Deliverables:**
- `tests/test_phase_1147_window_1139_1147_closure_gate.py`
- `docs/specs/ilc_window_1139_1147_handoff_1147_v0.1.md`
- `docs/phases/phase_1147_window_1139_1147_closure_gate_walkthrough.md`
- `STATUS.md` update: Window 1139-1147 entry
- Capsule v5.39: `docs/specs/ilc_antigravity_context_capsule_v5.39.md`
- Coherence report: `docs/specs/ilc_integration_coherence_report_1147_v0.1.md`

**Gate tests (minimum 18):**

| Cat | Tests | Content |
|-----|-------|---------|
| 0 | 1 | Selftest guard: `ILC_PHASE_1147_GATE_SELFTEST=1` required |
| 1 | 2 | Sequence lock doc exists; all 9 phases listed; sequence lock token present |
| 2 | 3 | Run 02 Fix2: corrected baseline JSON exists (333 entries); addendum doc exists with closing token; corrected S3/S1 ratio declared |
| 3 | 3 | Atlas Tier-1: curated seed edge count ≥ 48; checkpoint #1 report exists with PASS verdict; `basis_reachable_core_nodes` ≥ 28 |
| 4 | 3 | SIM-SPECTRAL-03: run01 summary JSON exists; disposition doc exists with closing token; CDL-085 recommendation verdict present |
| 5 | 2 | CDL-084 constants unchanged: `PROVENANCE_DECAY_ALPHA = Decimal("0.45")`; runtime version unchanged |
| 6 | 2 | Capsule v5.39 exists, supersedes v5.38; coherence report exists with pass verdict |
| 7 | 2 | Handoff doc exists; scoped regression passes (baseline 358 + new tests) |

**Handoff doc required sections:**
1. Window identity and closure basis
2. Run 02 Fix2 outcome: corrected slope table, updated S3/S1 ratio, Scenario B/C verdict
3. Atlas Tier-1 outcome: checkpoint #1 verdict, basis-reachable node count, patched seed
4. SIM-SPECTRAL-03 outcome: Genesis-seed vs. corrected Run 02 comparison, CDL-085 recommendation
5. CDL-085 authorization status (RECOMMEND / CONDITIONAL / DEFER) from Phase 1146
6. Carry-forward items: CDL-085 (status from Phase 1146), Atlas Tier-2, SIM-HYPEREDGE-01, ADR-0035
7. Next-window entry criteria and routing
8. MemPalace refresh disposition

**Coherence report required sections:**
- §1 Purpose: Window 1139-1147; three-lane window
- §2 Run 02 Fix2 outcome and corrected baseline summary
- §3 Atlas Tier-1 and GENESIS-COMPILE-01 checkpoint #1 outcome
- §4 SIM-SPECTRAL-03 outcome and CDL-085 recommendation
- §5 CDL chain unchanged (CDL-084 still the frontier)
- §6 Runtime chain unchanged (no `ilc_core/` mutations)
- §7 Audit findings (or explicit: window clean)
- Closing token: `coherence_report_1147_verdict=pass`

**Capsule v5.39** supersedes v5.38. Must include opening tokens:
```
capsule_v5_39_supersedes_v5_38
window_1139_1147_three_lane_complete
run02_fix2_corrected_baseline_committed
sim_spectral_03_disposition_phase_1146
```

**Commit subject:** `gate(window): phase 1147 window 1139-1147 closure gate`

---

## §11. Key Dependencies and Open Questions

### Must-resolve at window entry (all confirmed)

| Dependency | Status |
|------------|--------|
| `tools/sim_spectral_02.py` at `58c4687f` (normalized-λ₂ fix) | Confirmed — all 8 fix2 tests pass |
| `out/sim_spectral_02_run02_summary.json` exists (original Run 02) | Confirmed — 333 entries; combinatorial λ₂ harness (structural impedance term silently zero — see §4.1) |
| `out/genesis_core_star_map_v0.1.json` exists (31 nodes, 35 edges) | Confirmed — Phase 1136A `61e9b7f8` |
| GENESIS-COMPILE-01 tool chain available | Confirmed — Phase 1136A `08facab6` |
| CDL-084 fully resolved | Confirmed — Phase 1129 |
| Planning bridge §3 Bucket 1 gap list | Confirmed — `1d9a3e85` |

### Sequencing constraints (hard)

1. Phase 1140 (corrected rerun) must complete before Phase 1142 (Atlas Tier-1)
2. Phase 1142 + 1143 (Atlas patch + checkpoint) must complete and gate ≥ 28/31 before
   Phase 1144 (SIM-SPECTRAL-03 harness)
3. Phase 1144 must complete before Phase 1145 (SIM-SPECTRAL-03 Run)
4. Phase 1146 (disposition) must complete and be reviewed by human before Phase 1147
5. Phase 1147 requires explicit human GO token

### Open questions (resolve during window)

| Question | Resolves at |
|----------|-------------|
| Does normalized λ₂ ever fall below THETA_FLOOR (0.001) in connected simulation graphs? If not, structural_impedance will still be near-zero even with the fix | Phase 1140/1141 |
| What THETA_FLOOR would engage the structural impedance term for the simulation's graph density range? | Phase 1141 commentary |
| Does the 31-node Genesis seed topology produce a materially different λ₂ profile than the 3-axiom synthetic seed? | Phase 1145 |
| Will Phase 1142 iteration be needed (Atlas patch does not reach 28/31 in first attempt)? | Phase 1143 gate |

### Permanently deferred (not in scope this window)

- CDL-085 opening (Phase 1149, Window 1148+ — only authorized after human GO post Phase 1146)
- SIM-HYPEREDGE-01 (Window 1148+)
- SIM-ECU-STABILITY-01 (candidate, not authorized)
- Atlas Tier-2 (Window 1148+)
- Atlas Tier-3 (Window 1166+)
- ADR-0035 implementation CDL (planning/authorization gated)
- Star expansion (H-011 patent gate)
- Conley Index formalization (deferred pre-RC1.0)

---

## §12. Known Patterns and Technical Constraints

### Novel pattern: corrected-baseline-before-SIM pattern

This is the first window to insert a corrected baseline rerun before a new SIM run to
isolate a formula fix from a topology change. The pattern: (1) rerun the prior SIM with
the fixed formula, same parameters; (2) publish disposition addendum superseding the
broken run's values; (3) run the new SIM against the corrected baseline. This pattern
should be followed any time a harness fix is discovered between SIM runs.

### Structural impedance THETA_FLOOR calibration note

The original THETA_FLOOR (0.001) was set for the normalized Laplacian context by the
`laplacian_analytics.py` substrate. However, for synthetic simulation graphs (N=100
nodes, dense connectivity), the normalized λ₂ is likely to be much larger than 0.001
even for Sybil cluster topologies. If Phase 1140 confirms structural_impedance is still
near-zero after the fix, Phase 1141 should document the minimum observed normalized λ₂
and the THETA_FLOOR value that would engage the term. This is a diagnostic note, not
an authorization to change THETA_FLOOR — that change would require a separate CDL or
phase authorization.

### Atlas curated seed editing protocol

The curated seed (`genesis_core_star_map_curated_seed_v0.1.json`) is a
human-reviewable JSON file. When adding edges:
- Match existing node naming conventions exactly
- Use edge types that are already defined in the seed (do not invent new edge types
  without documenting them)
- Add a brief `authority_basis` field to each new edge explaining why the authority
  chain exists
- After editing, always regenerate by running the full three-tool chain (crawl →
  compare → diagnostic); never manually edit `out/genesis_core_star_map_v0.1.json`

### SIM-SPECTRAL-03 comparison baseline is Phase 1141, not Phase 1136

All references to "Run 02 baseline" in SIM-SPECTRAL-03 phases mean the corrected
baseline from Phase 1141, not the broken Phase 1136 values. Codex must read Phase 1141
addendum before writing the Phase 1146 disposition comparison table.

### Closure gate selftest guard chain

Phase 1147 gate must include `ILC_PHASE_1147_GATE_SELFTEST=1` in category 0. Codex
must read `tests/test_phase_1138_window_1130_1138_closure_gate.py` directly to
understand the established pattern — do not reason by analogy.

### Read-only constraint on `ilc_core/`

`ilc_core/analysis/laplacian_analytics.py`, `spectral_trajectory.py`,
`local_spectral_analytics.py`, and `spectral_utils.py` must NOT be modified in this
window. The SIM harness uses them as reference only. Any updates to the analytics
substrate require a separate authorization.

---

## §13. Non-Goals and Explicitly Deferred Items

- No CDL opening, prelock, or ratification
- No `ilc_core/` runtime changes of any kind
- No settlement rule changes
- No QATPS parameter changes
- No THETA_FLOOR changes (even if Phase 1141 finds it is calibrated wrong for the SIM;
  calibration change requires separate authorization)
- No CDL-085 opening (Phase 1146 produces the recommendation; the opening is Phase 1149
  in Window 1148+ after human authorization)
- No SIM-HYPEREDGE-01 (separate lane, Window 1148+)
- No SIM-ECU-STABILITY-01 (not authorized)
- No Star expansion (H-011 patent gate)
- No Atlas Tier-2 or Tier-3 (separate future windows)
- No ADR ratification or adoption
- No MemPalace modifications (rebuild runs in parallel outside the phase sequence)
- No Conley Index formalization (deferred pre-RC1.0)
- No re-running of SIM-SPECTRAL-01, SIM-PROVENANCE-01, or any prior SIM for comparison

---

## §14. Key Canonical Anchors for Prompt Drafting

Codex must reference these in every phase prompt:

- **(PRIMARY)** Capsule v5.38: `docs/specs/ilc_antigravity_context_capsule_v5.38.md`
- Window 1139-1147 sequence lock: `docs/specs/ilc_phase_1139_1147_sequence_lock_v0.1.md`
  (produced Phase 1139)
- Window 1130-1138 handoff: `docs/specs/ilc_window_1130_1138_handoff_1138_v0.1.md`
- Planning bridge (authoritative atlas backlog): `docs/specs/ilc_window_1130_1138_to_rc_planning_bridge_v0.1.md`
- Run 02 original (broken baseline): `out/sim_spectral_02_run02_summary.json`
- Run 02 Fix2 corrected baseline: `out/sim_spectral_02_run02_fix2_summary.json` (Phase 1140)
- Corrected disposition addendum: `docs/sims/sim_spectral_02/run02_fix2_disposition_addendum_1141_v0.1.md` (Phase 1141)
- Fixed harness (post-fix): `tools/sim_spectral_02.py` at `58c4687f`+
- Genesis curated seed (Tier-1 mutation target): `docs/sims/sim_spectral_02/genesis_core_star_map_curated_seed_v0.1.json`
- Genesis core star map (patched in Phase 1142): `out/genesis_core_star_map_v0.1.json`
- GENESIS-COMPILE-01 checkpoint #1 report: `docs/sims/sim_spectral_02/genesis_compile_checkpoint_1_1143_v0.1.md` (Phase 1143)
- SIM-SPECTRAL-03 program: `docs/sims/sim_spectral_03/program.md` (Phase 1144)
- SIM-SPECTRAL-03 run results: `out/sim_spectral_03_run01_summary.json` (Phase 1145)
- CDL register: `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- Phase completion log: `docs/phases/STATUS.md`
- ADM-003 reference agent architecture: carry-forward unchanged (see capsule v5.38 §3)
- For closure gate (Phase 1147): all Phase 1139–1146 test files and artifact paths in §10.

`window_1139_1147_guidance_doc_v0.1`
