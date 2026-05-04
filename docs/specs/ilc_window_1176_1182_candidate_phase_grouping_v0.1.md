# ILC Window 1176-1182: Candidate Phase Grouping

**Author:** Claude Sonnet 4.6 (local architectural reviewer)
**Date:** 2026-05-04
**Baseline:** Window 1166-1175 CLOSED (Phase 1175 verdict: PASS, commit `ee0f6b48`).
CDL-084 is the ratified attribution frontier; CDL-085 is open (Phase 1172) but not
ratified; `EDGE_MINT_PHI_BOUND` unset. SIM-SPECTRAL-05 passed (`sim_spectral_05_gate_pass`).
ADR-0037 and ADR-0036 accepted (`adr_0037_accepted_phase_1173`,
`adr_0036_accepted_phase_1173`). Capsule v5.42 current. Handoff:
`docs/specs/ilc_window_1166_1175_handoff_1175_v0.1.md`.
**Planning note:** This is a candidate grouping, not a locked sequence. Phases 1176–1177
are the hard minimum lane (sequence lock + CDL-085 prelock spec). Phase 1178 is a
conditional signing slot. Phases 1179–1180 are conditional tail SIM slots. Phases 1181–1182
are firm coherence + closure phases. The window runs whether or not signing authorization
is issued.

---

## 1. Window Identity and Scope

Window 1176-1182 runs three lanes, two of which are independent:

1. **CDL-085 prelock lane (obligated)** — CDL-085 opened in Phase 1172 with five
   unresolved questions (Q1–Q5 from the opening spec). The prelock phase must resolve
   all five and produce a prelock spec document: exact bound object, exact φ-bound
   expression, φ interpretation, runtime relation, and economic-flow dependency posture.
   The prelock establishes `EDGE_MINT_PHI_BOUND` candidate value and runtime scope for
   CDL-085 ratification in Window 1177+. No CDL mutation at prelock.

2. **v0.2 signing ceremony lane (conditional on explicit signing authorization)** —
   ADR-0036 and ADR-0037 are both accepted. The v0.2 candidate has 41 nodes and 73
   edges. All signing prerequisites are satisfied. This lane executes Phase 1178 only
   if an explicit human signing authorization token is issued. The two tracks are
   independent — CDL-085 prelock does not block signing and signing does not block
   CDL-085 prelock.

3. **SIM-SPECTRAL-05 deferred observer slice lane (conditional tail)** — Three slices
   were deferred from Window 1166-1175 with explicit carry-forward tokens:
   `sim_spectral_05_runtime_binding_slice_deferred_window_1176`,
   `sim_spectral_05_economic_flow_slice_deferred_window_1176`,
   `sim_spectral_05_gossip_slice_deferred_window_1176`. Phases 1179 and 1180 address
   the runtime-binding and economic-flow slices respectively. The gossip slice is
   deferred to Window 1183+ unless window capacity allows.

**Key independence note:** The CDL-085 prelock and v0.2 signing ceremony are
architecturally independent. The roadmap v0.9 §3 Gap 2 states explicitly: "v0.2 signing
is NOT blocked on CDL-085 ratification." Phase ordering in this window respects that
independence: the signing ceremony (1178) follows the prelock spec (1177) only for
capacity reasons, not dependency reasons.

**Tail-slot policy:** Phases 1178, 1179, and 1180 are conditional tail slots. The window
closes at Phase 1182 regardless of how many tail slots execute. Unexecuted tail slots
are explicitly deferred with carry-forward tokens.

---

## 2. Baseline and Inheritance

### Ratified CDL chain

- `CDL_084_DEPENDENCY = "cdl_084_provenance_chain_attribution_ratified_1113.v0.1"`
- `PROVENANCE_DECAY_ALPHA = Decimal("0.45")`
- `PROVENANCE_MAX_DEPTH = 3`
- CDL-085: **OPEN** (Phase 1172). `EDGE_MINT_PHI_BOUND` unset. No runtime mutation.
  Prelock questions Q1–Q5 unresolved.
- Next fresh CDL number for new openings: **CDL-086** (CDL-085 is already open)

### Active runtime chain

- `epoch_attribution_settle_runtime_1129_fix1.v0.5` — unchanged
- No runtime semantic mutations authorized in this window. CDL-085 ratification
  (Window 1177+) may authorize a runtime constant; prelock itself does not.

### Genesis Atlas canonical anchors

- Signed v0.1 star map: `out/genesis_core_star_map_v0.1.json` (32 nodes, 55 edges)
  — **immutable and untouched**
- Signed root envelope hash:
  `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`
- **Strictly immutable:** `out/genesis_compile_coverage_diagnostic_v0.1.json` — must
  never be regenerated
- Unsigned v0.2 candidate: `out/genesis_core_star_map_v0.2_candidate.json`
  (41 nodes, 73 edges) — signing conditional on Phase 1178 authorization

### SIM-SPECTRAL-05 evidence baseline

- Track A: `track_a_pass` — λ_max 3.18σ, spectral_gap 2.78σ, degree_gini 2.73σ vs
  `synthetic_sybil_cluster`
- Track B: `track_b_pass` — S1 convergence 0.85, S3 Sybil 0.25, separation **0.60**
  (this separation value is the primary input to the CDL-085 prelock φ-bound deliberation)
- Deferred slices: runtime-binding, economic-flow, gossip

---

## 3. Track Inventory

### Constitutionally obligated

- `cdl_085_prelock_required_after_opening_phase_1172` — must produce prelock spec this
  window; ratification deferred to Window 1177
- `edge_mint_phi_bound_value_unset_pending_cdl_085_prelock` — prelock must establish
  candidate value

### Deferred governance (carry-forward, not this window)

- CDL-085 **ratification** — Window 1177 (requires prelock from this window)
- CDL-001 (genesis_blocker / packaging track) — evaluation Window 1178+
- Tier-3 runtime linkage (`schema:*` / `runtime:*`) — Window 1178+
- Truth-primitive permanence community ratification — pre-public-RC
- Canon bundle signing repair — tooling debt; deferred
- Multi-hop centrality attribution CDL — post-CDL-085
- Cross-epoch compaction CDL — pre-network-scale

### Simulation-conditional

- `sim_spectral_05_runtime_binding_slice_deferred_window_1176` — Phase 1179 (conditional
  tail; executes if window capacity allows after Phase 1178)
- `sim_spectral_05_economic_flow_slice_deferred_window_1176` — Phase 1180 (conditional
  tail; depends on Phase 1179 completing first)
- `sim_spectral_05_gossip_slice_deferred_window_1176` — deferred to Window 1183+ (third
  slice; too many slices for one window)

---

## 4. CDL-085 Prelock Lane

### Purpose

The prelock spec is the document that locks the candidate values for CDL-085 ratification.
It does not open or mutate CDL-085 (already open). It produces a committed document at
`docs/specs/ilc_cdl_085_prelock_spec_1177_v0.1.md` that resolves Q1–Q5 from the opening
spec and establishes `EDGE_MINT_PHI_BOUND` candidate value.

### Five questions to resolve at prelock

**Q1 — Bound object:** The prelock must select among: (a) provenance-equivalent derivation
paths only; (b) all edge-mint events; (c) all claim-composition events that participate in
ECU/ILC attribution. Recommended posture: (a) provenance-equivalent derivation paths only,
scoped to paths that pass the ADR-0037 §3.2 convergence test, with (b) and (c) deferred
to a future CDL amendment once economic-flow testing is complete.

**Q2 — Bound expression:** The prelock must select among: (a) branchial convergence
separation threshold; (b) structural discriminant threshold over the three SIM-SPECTRAL-05
discriminants; (c) combined rule. Recommended posture: (c) combined rule — separation ≥
SIM-SPECTRAL-05 Track B calibration baseline, with structural discriminants as auxiliary
confirmation. The Track B separation of 0.60 is the natural φ-bound candidate.

**Q3 — φ interpretation:** Select among: (a) Werner productivity bound over edge-mint
expansion; (b) spectral-efficiency ratio; (c) governance shorthand for the combined
SIM-SPECTRAL-05 pass condition. Recommended posture: (a) Werner productivity bound — the
name is meaningful and the bound expression flows naturally from Track B.

**Q4 — Runtime relation:** Select among: (a) no runtime constant yet, constitutional
policy only; (b) future `EDGE_MINT_PHI_BOUND` constant after ratification; (c) runtime-
binding slice required before activation. Recommended posture: (b) constitutional policy
with `EDGE_MINT_PHI_BOUND` constant declared at ratification; runtime activation deferred
until the runtime-binding observer slice (Phase 1179) is complete.

**Q5 — Economic-flow dependency:** Select among: (a) no ECU/ILC change until economic-
flow slice tested; (b) constitutional ratification first, runtime/economic activation
later; (c) economic-flow SIM required before ratification. Recommended posture: (b) —
ratification proceeds on constitutional grounds; economic-flow activation explicitly
deferred until Phase 1180 observer slice passes. The economic-flow gate does not block
constitutional ratification but does block economic-flow runtime activation.

### Prelock spec document requirements

The prelock spec (`docs/specs/ilc_cdl_085_prelock_spec_1177_v0.1.md`) must include:

1. All five Q1–Q5 resolutions with selected postures and rationale
2. Candidate `EDGE_MINT_PHI_BOUND` value (expected: `Decimal("0.60")` derived from Track B
   separation baseline; subject to deliberation)
3. Statement of what the prelock does and does not authorize
4. Reference to SIM-SPECTRAL-05 evidence artifacts and ADR-0037 §3.2
5. Explicit statement that economic-flow activation is gated on Phase 1180 observer slice
6. Prelock token: `cdl_085_prelock_committed_phase_1177`

### Tests for prelock phase

The prelock phase produces tests that assert:
- Prelock spec exists and contains the five resolutions
- `cdl_085_prelock_committed_phase_1177` token present
- CDL-085 opening doc still shows `OPEN` at the Phase 1172 commit (historical hardening)
- No `EDGE_MINT_PHI_BOUND` constant in `ilc_core/` yet (prelock does not mutate runtime)

---

## 5. v0.2 Signing Ceremony Lane

### Authorization requirement

Phase 1178 is a **conditional SENSITIVE** phase. It executes only if an explicit human
signing authorization token is issued. The signing authorization is a separate, explicit
act by the human reviewer — it is not implied by the window GO token or by prior ADR
acceptances.

Expected authorization token: `v0_2_signing_ceremony_authorized_phase_1178` (human issues
this explicitly before Phase 1178 executes).

### Signing sequence (per ADR-0036 §4)

If authorized, Phase 1178 executes the following steps in a single commit:

1. **ADR-0036 §4 key registration artifact** — produce
   `docs/adr/adr_0036_release_key_registration_artifact_1178_v0.1.md` recording the
   release key identity, registration rationale, and version equivalence basis
   (ADR-0037 §3.3 governs what may be signed)
2. **Signing ceremony execution** — sign `out/genesis_core_star_map_v0.2_candidate.json`
   per ADR-0036 §4 delegation chain
3. **Release envelope binding** — produce signed release envelope artifact
   `out/genesis_atlas_v0_2_release_envelope_1178.json` per ADR-0036 §5
4. **PLANNING_INDEX.md and capsule token update** — record
   `genesis_atlas_v0_2_signed_phase_1178`

### Non-authorization scenario

If signing authorization is not issued, Phase 1178 is skipped with explicit carry-forward
token: `v0_2_signing_ceremony_deferred_pending_signing_authorization`. The window proceeds
to Phase 1179 (SIM slice) or directly to Phase 1181 (coherence).

### Version equivalence criterion

The v0.2 signing is governed by ADR-0037 §3.3. The prelock reviewer must confirm that
the 41-node / 73-edge candidate satisfies the version equivalence criterion before
signing. This is a precondition check in the Phase 1178 scope, not a governance action.

---

## 6. SIM-SPECTRAL-05 Deferred Observer Slices

### Slice priority order

Priority: runtime-binding (Phase 1179) → economic-flow (Phase 1180) → gossip
(deferred to Window 1183+). The runtime-binding slice is prerequisite for activating
`EDGE_MINT_PHI_BOUND` in `ilc_core/`. The economic-flow slice gates economic-flow
activation.

### Phase 1179 — Runtime-binding slice

**Scope:** Design and execute a SIM program testing whether the `EDGE_MINT_PHI_BOUND`
constant, once added to `ilc_core/`, would correctly gate Sybil-amplified edge-mint
events in a simulated runtime context. Produces:
- Program spec: `docs/sims/sim_spectral_05/runtime_binding_slice_program_1179_v0.1.md`
- SIM execution artifact: `out/sim_spectral_05_runtime_binding_slice_run_1179.json`
- Disposition: token `sim_spectral_05_runtime_binding_slice_pass` or
  `sim_spectral_05_runtime_binding_slice_fail`
- If pass: token `sim_spectral_05_runtime_binding_slice_deferred_window_1176_resolved`

### Phase 1180 — Economic-flow slice

**Scope:** Design and execute a SIM program testing whether φ-bound gating on
provenance-equivalent paths produces expected economic-flow outcomes (correct ECU
attribution gating, no unintended economic-flow suppression of legitimate paths).
Produces:
- Program spec: `docs/sims/sim_spectral_05/economic_flow_slice_program_1180_v0.1.md`
- SIM execution artifact: `out/sim_spectral_05_economic_flow_slice_run_1180.json`
- Disposition: token `sim_spectral_05_economic_flow_slice_pass` or
  `sim_spectral_05_economic_flow_slice_fail`
- If pass: token `sim_spectral_05_economic_flow_slice_deferred_window_1176_resolved`

The economic-flow gate result feeds into Window 1177 CDL-085 ratification deliberation:
if the economic-flow slice fails, ratification may need to carry a broader economic-flow
activation deferral clause.

---

## 7. CDL Number Assignments

| CDL | Title (candidate) | Decision digest anchor | Opening phase | Ratification phase |
|-----|-------------------|----------------------|---------------|-------------------|
| CDL-085 | Werner φ-bound Provenance Equivalence Limit | `EDGE_MINT_PHI_BOUND` (candidate `Decimal("0.60")`); bound object: provenance-equivalent derivation paths; combined structural + branchial expression; Werner productivity interpretation | Already open (Phase 1172) | Window 1177 (not this window) |

**Note:** No new CDL is opened in this window. CDL-085 prelock is a doc-only phase — no
CDL mutation. CDL-086 remains the next available number for future openings. v0.2 signing
is governed by ADR-0036/ADR-0037 and does not open a new CDL.

---

## 8. Candidate Phase Table

| Order | Phase | Topic | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 1176 | Window sequence lock | Foundation / Constitutional | **SENSITIVE** |
| 2 | 1177 | CDL-085 prelock spec: resolve Q1–Q5, commit prelock doc + tests | Constitutional | `constitutional` |
| 3 | 1178 | v0.2 signing ceremony (ADR-0036 §4 registration + envelope + PLANNING_INDEX update) | Constitutional | **conditional** |
| 4 | 1179 | SIM-SPECTRAL-05 runtime-binding observer slice: program spec + execution + disposition | Simulation | `NON-SENSITIVE` |
| 5 | 1180 | SIM-SPECTRAL-05 economic-flow observer slice: program spec + execution + disposition | Simulation | `NON-SENSITIVE` |
| 6 | 1181 | Coherence report + capsule advance | Synthesis | `NON-SENSITIVE` |
| 7 | 1182 | Window 1176-1182 closure gate | Gate | **SENSITIVE** |

### Conditional note on Phase 1178

**Scenario A (signing authorized):** Human issues explicit token
`v0_2_signing_ceremony_authorized_phase_1178`. Phase 1178 executes the full ADR-0036 §4
registration → signing ceremony → release envelope → PLANNING_INDEX/capsule token update.
Phase 1178 is **SENSITIVE** in this scenario (signs an immutable Genesis artifact).
Requires pre-commit hook:
```
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1178
```
Wait — signing is not a CDL mutation. The pre-commit hook for CDL mutations does not apply
directly. However, the signing ceremony modifies the Genesis Atlas artifact record, which
is a constitutional-boundary action of the same class. Require explicit GO token
`GO Phase 1178` after signing authorization token is issued.

**Scenario B (signing not authorized):** Phase 1178 is skipped. Codex commits a skip
record with token `v0_2_signing_ceremony_deferred_pending_signing_authorization`. Window
proceeds to Phase 1179 (or Phase 1181 if Phases 1179–1180 are also skipped).

### Conditional note on Phases 1179–1180

These are capacity-dependent conditional tail slots. Both may be executed, one may
execute, or both may be deferred. Each deferred slot must emit its own explicit carry-
forward token:

- `sim_spectral_05_runtime_binding_slice_deferred_window_1182` (if 1179 deferred)
- `sim_spectral_05_economic_flow_slice_deferred_window_1182` (if 1180 deferred)

Phase 1180 depends on Phase 1179 completing first (economic-flow analysis builds on
runtime-binding findings). If 1179 is deferred, 1180 is automatically deferred.

---

## 9. Sensitivity Classification

### SENSITIVE phases

- **Phase 1176** (sequence lock) — CDL mutation may be involved if the sequence lock
  document contains CDL state assertions that constitute a CDL-boundary action. In
  practice, sequence locks are doc-only but are treated as SENSITIVE because they are
  structural window-boundary commits. Requires `GO Phase 1176`.
- **Phase 1178** (v0.2 signing ceremony, if authorized) — Signs an immutable Genesis
  Atlas artifact. This is a constitutional-boundary action. Requires explicit signing
  authorization token AND `GO Phase 1178`.
- **Phase 1182** (closure gate) — Structural window boundary. Requires `GO Phase 1182`.

### NON-SENSITIVE phases

- **Phase 1177** (CDL-085 prelock spec) — Doc-only. No CDL mutation, no runtime
  mutation, no Genesis Atlas artifact change. Produces `docs/specs/` document and tests.
  May proceed after Phase 1176 without additional GO token.
- **Phase 1179** (SIM runtime-binding slice) — Simulation work: program spec, execution
  artifact, disposition. No CDL mutation, no runtime mutation.
- **Phase 1180** (SIM economic-flow slice) — Simulation work: same class as Phase 1179.
- **Phase 1181** (coherence + capsule) — Synthesis work. No CDL mutation, no runtime
  mutation.

### Conditional phases rule

**Phase 1178:** Before executing Phase 1178, confirm with the human whether the signing
authorization token has been issued. If yes: SENSITIVE; require explicit `GO Phase 1178`
after authorization token. If no: Phase is skipped NON-SENSITIVELY with carry-forward
token; no GO token required.

### Pre-commit hook block

Phases requiring `ILC_CDL_MUTATION_AUTHORIZED=1`:
- None in this window (no CDL mutations in Phase 1176, 1177, or 1181).
- Phase 1178 (if authorized) does not use the CDL mutation hook but requires an explicit
  Genesis signing authorization token and GO token.
- Window 1177 CDL-085 ratification (not in this window) will require the mutation hook.

---

## 10. Scope Notes for Fixed Phases

### Phase 1176 — Window Sequence Lock

**SENSITIVE.** Requires `GO Phase 1176`.

**Deliverables:**

| Artifact | Notes |
|----------|-------|
| `docs/specs/ilc_phase_1176_1182_sequence_lock_v0.1.md` | Window 1176-1182 sequence lock doc |
| `docs/phases/phase_1176_window_sequence_lock_walkthrough.md` | Phase walkthrough |
| Updated `docs/PLANNING_INDEX.md` §0 | Window handoff row → new guidance doc; confirm §0 is current |
| Updated `docs/phases/STATUS.md` | Phase 1176 entry |

**Required content (sequence lock doc):** Standard sequence lock format per
`docs/specs/ilc_phase_1166_1175_sequence_lock_v0.1.md` as format reference. Must include:
- Window identity (1176-1182)
- Baseline (Window 1166-1175 closed, ee0f6b48)
- Phase table (same as §8 above)
- Carry-forward tokens from Window 1166-1175
- Explicit: no new CDL opens in this window; CDL-085 prelock is doc-only

**Tests:** Minimum 2 — sequence lock doc exists + token present.

**Commit subject:** `feat(g8): phase 1176 window 1176-1182 sequence lock`

---

### Phase 1177 — CDL-085 Prelock Spec

**NON-SENSITIVE.** No CDL mutation. No runtime mutation. May proceed after Phase 1176
without additional GO token.

**Deliverables:**

| Artifact | Notes |
|----------|-------|
| `docs/specs/ilc_cdl_085_prelock_spec_1177_v0.1.md` | Prelock spec resolving Q1–Q5 |
| `tests/test_phase_1177_cdl_085_prelock.py` | Minimum 5 tests |
| `docs/phases/phase_1177_cdl_085_prelock_walkthrough.md` | Phase walkthrough |
| Updated `docs/phases/STATUS.md` | Phase 1177 entry |

**Required content (prelock spec):**
1. Explicit resolution of Q1–Q5 with selected posture and rationale
2. Candidate `EDGE_MINT_PHI_BOUND` value (numerical, as `Decimal`)
3. Statement that prelock does not mutate CDL-085 or `ilc_core/`
4. Reference to SIM-SPECTRAL-05 Track B separation baseline (0.60)
5. Reference to ADR-0037 §3.2 provenance equivalence criterion
6. Economic-flow activation gate: explicitly deferred until Phase 1180 slice passes
7. Runtime-binding activation gate: explicitly deferred until Phase 1179 slice passes
8. Token: `cdl_085_prelock_committed_phase_1177`

**Tests (minimum 5):**
1. Prelock spec exists at expected path
2. `cdl_085_prelock_committed_phase_1177` token present in prelock spec
3. Prelock spec contains all five Q-resolutions (pattern-check for Q1 through Q5)
4. CDL-085 opening doc shows `OPEN` at Phase 1172 commit ref (historical hardening:
   `git show ee0f6b48:docs/specs/ilc_cdl_085_werner_phi_bound_opening_1172_v0.1.md`
   — check for `cdl_085_open_phase_1172`)
5. No `EDGE_MINT_PHI_BOUND` constant present in `ilc_core/` (prelock does not mutate runtime)

**Pre-commit split:** 5+0 (all tests in main commit; no CDL-mutation commit).

**Commit subject:** `feat(cdl): phase 1177 cdl-085 prelock spec Q1-Q5 resolved`

---

### Phase 1181 — Coherence Report + Capsule Advance

**NON-SENSITIVE.**

**Deliverables:**

| Artifact | Notes |
|----------|-------|
| `docs/specs/ilc_integration_coherence_report_1181_v0.1.md` | Coherence report |
| `docs/specs/ilc_antigravity_context_capsule_v5.43.md` | Capsule advance (supersedes v5.42) |
| `docs/phases/phase_1181_coherence_capsule_v5_43_walkthrough.md` | Phase walkthrough |
| Updated `docs/phases/STATUS.md` | Phase 1181 entry |
| Updated `docs/PLANNING_INDEX.md` §0 | Capsule row → v5.43 |

**Required content (capsule):**
- CDL-085 prelock committed (`cdl_085_prelock_committed_phase_1177`)
- v0.2 signing outcome (signed or deferred with token)
- SIM observer slice outcomes (each: pass/deferred with token)
- Next window entry criteria (CDL-085 ratification prerequisites)
- Token: `capsule_v5_43_supersedes_v5_42`

**Tests:** Minimum 3 — coherence report exists, capsule exists + supersedes token,
capsule contains CDL-085 prelock token.

**Commit subject:** `feat(capsule): phase 1181 coherence report + capsule v5.43`

---

### Phase 1182 — Closure Gate

**SENSITIVE.** Requires `GO Phase 1182`.

**Deliverables:**

| Artifact | Notes |
|----------|-------|
| `docs/specs/ilc_window_1176_1182_handoff_1182_v0.1.md` | Window closure handoff |
| `tests/test_phase_1182_window_1176_1182_closure_gate.py` | Minimum 14 tests |
| `docs/phases/phase_1182_window_1176_1182_closure_gate_walkthrough.md` | Walkthrough |
| Updated `docs/PLANNING_INDEX.md` | §0 window handoff row → closure handoff |
| Updated `docs/phases/STATUS.md` | Phase 1182 entry + window closure |

**Required closure gate checks (minimum 14):**

| # | Check | Gate |
|---|-------|------|
| 1 | Sequence lock doc exists | Seq lock |
| 2 | `window_1176_1182_sequence_lock_committed` token present | Seq lock |
| 3 | CDL-085 prelock spec exists | Prelock |
| 4 | `cdl_085_prelock_committed_phase_1177` token present | Prelock |
| 5 | CDL-085 prelock spec contains all five Q-resolutions | Prelock completeness |
| 6 | No `EDGE_MINT_PHI_BOUND` in `ilc_core/` (unless runtime-binding slice authorized) | Runtime stability |
| 7 | Phase 1178 signed v0.2 OR `v0_2_signing_ceremony_deferred_pending_signing_authorization` token | Signing routing |
| 8 | Phase 1179 runtime-binding slice pass OR deferred token | SIM slice routing |
| 9 | Phase 1180 economic-flow slice pass OR deferred token | SIM slice routing |
| 10 | Coherence report 1181 exists | Synthesis |
| 11 | Capsule v5.43 exists with `capsule_v5_43_supersedes_v5_42` | Capsule |
| 12 | Signed Genesis v0.1 unchanged: hash `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c` | Immutability |
| 13 | `out/genesis_compile_coverage_diagnostic_v0.1.json` not regenerated | Immutability |
| 14 | Runtime chain unchanged (`epoch_attribution_settle_runtime_1129_fix1.v0.5`) | Runtime stability |

**Selftest guard:** Test file must include `ILC_PHASE_1182_GATE_SELFTEST=1` guard.
Self-test skip pattern: if `SELFTEST_MODE is False`, call `pytest.skip(...)` (not `assert
SELFTEST_MODE is True` — that form fails in regression; see Phase 1165 fix).

**Closure tokens:**
- `window_1176_1182_closed_phase_1182`
- `window_1176_1182_closure_gate_verdict=pass`

**Commit subject:** `docs(phase): close window 1176-1182`

---

## 11. Key Dependencies and Open Questions

### Must-resolve at window entry

- None blocking Phase 1176 or Phase 1177. Both can proceed immediately.
- Phase 1178 (signing): must receive explicit signing authorization token before
  executing.

### Sequencing constraints

- Phase 1177 (prelock) must complete before Phase 1178 (signing) because the prelock
  spec is the evidence base for the v0.2 pre-condition check (ADR-0037 §3.3 version
  equivalence review step).
- Phase 1179 must complete before Phase 1180 (economic-flow builds on runtime-binding).
- Phase 1181 (coherence) must be after 1178, 1179, 1180 (records all outcomes).
- Phase 1182 (closure gate) is last.

### Open questions (need human input at window entry)

1. **φ-bound candidate value:** The guidance recommends `Decimal("0.60")` based on Track B
   separation. Is there any reason to use a different value (e.g., conservative floor, or
   combined expression with structural discriminants)? This should be settled before Phase
   1177 executes.

2. **Signing authorization:** Will the human issue explicit signing authorization for
   Phase 1178? If yes, Phase 1178 is a firm phase and the window should plan for it. If
   no, Phase 1178 is skipped this window. The answer determines whether this is a 5-phase
   or 7-phase window.

3. **SIM slice priority:** Should Phases 1179 and 1180 both run in this window, or is one
   sufficient? If window capacity is limited after Phase 1177 (prelock), the runtime-
   binding slice (1179) is higher priority because it gates `EDGE_MINT_PHI_BOUND` runtime
   activation.

### Permanently deferred (not open questions)

- CDL-085 ratification: Window 1177 (after prelock from this window)
- Tier-3 runtime linkage: Window 1178+
- L4 privacy / onion routing: post-RC3
- CDL-070 PQ migration ceremony: after SIM-MONETARY-01

---

## 12. Known Patterns and Technical Constraints

### Novel patterns this window

1. **First CDL prelock after spectral SIM gate lift** — CDL-085 prelock is the first
   prelock whose candidate value is derived directly from a SIM branchial convergence
   result (Track B separation 0.60). The prelock spec must explicitly cite the SIM
   evidence artifact path and the specific numerical baseline.

2. **First Genesis Atlas v0.2 signing ceremony (if Phase 1178 executes)** — This is the
   first multi-ADR-governed signing ceremony (ADR-0036 §4 registration + ADR-0037 §3.3
   version equivalence check). No prior ILC phase has executed a Genesis Atlas signing
   ceremony of this class.

3. **Deferred-slice resolution pattern** — Phases 1179 and 1180 address carry-forward
   deferred SIM slice tokens from a prior window. Each phase must emit both a result
   token (pass/fail) and a resolution token for the original deferred token.

### Historical prelock hardening

Every test that asserts CDL-085 opening state must read at the Phase 1172 historical
commit (`ee0f6b48`), not live files:

```python
result = subprocess.run(
    ["git", "show", "ee0f6b48:docs/specs/ilc_cdl_085_werner_phi_bound_opening_1172_v0.1.md"],
    capture_output=True, text=True
)
assert "cdl_085_open_phase_1172" in result.stdout
```

This applies to Phase 1177 test #4 and the closure gate test #3.

### Phantom edit guard

No `ilc_core/` file is a mutation target in this window (CDL-085 ratification, which would
add `EDGE_MINT_PHI_BOUND` to a runtime constant file, is Window 1177). However:

- Test #6 in the closure gate (`no EDGE_MINT_PHI_BOUND in ilc_core/`) acts as the
  phantom edit guard. If any tool run accidentally adds the constant, this test fails
  and the window cannot close cleanly.
- Detection: `grep -r "EDGE_MINT_PHI_BOUND" ilc_core/` (expect no output)
- Fix: `git restore` the file if accidentally modified

### Pre-commit hook clean-state guard

No CDL mutation phases in this window. The pre-commit hook (`ILC_CDL_MUTATION_AUTHORIZED`)
is NOT required for any phase in Window 1176-1182. Phase 1178 (signing) uses a different
authorization mechanism (explicit GO token after signing authorization token).

### Closure gate selftest guard chain

Phase 1182 closure gate must call `pytest.skip(msg)` in the selftest guard test — not
`assert SELFTEST_MODE is True`. See Phase 1165 fix (`b9c6d1b4`): the `assert` form fails
in regression mode without selftest env var set.

When building the Phase 1182 closure gate test, read Phase 1175 gate
(`tests/test_phase_1175_window_1166_1175_closure_gate.py`) directly rather than reasoning
by analogy. The test category structure, import pattern, and selftest guard pattern must
match.

### Signing ceremony artifact immutability

If Phase 1178 executes, the signed v0.2 release envelope
(`out/genesis_atlas_v0_2_release_envelope_1178.json`) becomes immutable from the moment
it is committed. It must be added to the immutability check list in the Phase 1182 closure
gate (add a check #15 if signing occurs).

---

## 13. Non-Goals and Explicitly Deferred Items

- CDL-085 **ratification** — Window 1177 (this window produces the prelock spec; next
  window ratifies)
- Any `ilc_core/` runtime mutation — no runtime constant added until ratification phase
- Economic-flow activation on-chain — gated on Phase 1180 slice pass AND CDL-085
  ratification
- CDL-086 or any new CDL opening — not in scope
- Tier-3 runtime linkage (`schema:*` / `runtime:*` node class) — Window 1178+
- CDL-001 (genesis_blocker / packaging track) evaluation — Window 1178+
- Persistent rate limiter — RC2 carry-forward
- Truth-primitive permanence community ratification — pre-public-RC, not this window
- SIM-SPECTRAL-05 gossip slice — deferred to Window 1183+
- SIM-MONETARY-01 / CDL-070 PQ migration ceremony — long-range
- L4 privacy (onion routing / SURB) — post-RC3
- Canon bundle signing repair — tooling debt; not this window

---

## 14. Key Canonical Anchors for Prompt Drafting

- `docs/specs/ilc_antigravity_context_capsule_v5.42.md` **(PRIMARY — Codex rehydration)**
- `docs/specs/ilc_window_1166_1175_handoff_1175_v0.1.md` — prior window closure handoff
- `docs/specs/ilc_phase_1166_1175_sequence_lock_v0.1.md` — format reference for new sequence lock
- `docs/specs/ilc_constitutional_decision_log_v0.1.md` — CDL register (CDL-085 entry)
- `docs/phases/STATUS.md` — phase completion log
- `docs/specs/ilc_cdl_085_werner_phi_bound_opening_1172_v0.1.md` — CDL-085 opening spec
  (Q1–Q5 definitions; §7 prelock requirements)
- `docs/sims/sim_spectral_05/disposition_1171_v0.1.md` — SIM-SPECTRAL-05 gate pass evidence
  (Track B separation 0.60 = φ-bound candidate baseline)
- `docs/adr/ADR_0037_Genesis_Canonical_Lineage_Contract.md` §3.2, §3.3 — provenance
  equivalence criterion (prelock anchor) and version equivalence criterion (signing anchor)
- `docs/adr/ADR_0036_Operational_Release_Key_Genesis_Binding.md` §4, §5 — key registration
  and release envelope procedures (Phase 1178 if authorized)
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.9.md` — RC milestone
  map and gap inventory (RC2 remaining gates reference)
- `docs/PLANNING_INDEX.md §0` — core forward planning docs quick-reference; update
  at end of each phase
- For Phase 1182 closure gate: all Phase 1176–1181 test files and artifacts.
