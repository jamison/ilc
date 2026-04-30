# ILC Window 1118–1123: Candidate Phase Grouping

**Author:** Claude Sonnet 4.6 (local architectural reviewer)
**Date:** 2026-04-30
**Baseline:** Window 1110–1117 CLOSED (Phase 1117, commit `0437fcb1`). CDL-084 ratified
             (Phase 1113). PROVENANCE settlement active (Phase 1114). Capsule v5.35.
**Planning note:** This is a candidate grouping, not a locked sequence. Phases 1118–1119
are the hard minimum lane (sequence lock + FLOAT-KILL-01). Phases 1120–1122 are
primary-track slots conditional on FLOAT-KILL-01 completing within a single phase.
Phase 1123 is the closure gate.

---

## 1. Window Identity and Scope

Window 1118–1123 is a **runtime hardening + SIM commissioning window** with no CDL
mutations. The constitutional lane is quiet — no CDL opens, no ratifications, no GO token
required except the closure gate.

The two obligations that enter this window from prior carry-forward are:

1. **FLOAT-KILL-01 (CRITICAL):** Codebase-wide float→Decimal conversion for ECU/stake/reward
   amounts in active protocol paths, plus `import random` → `secrets` in
   `spectral_routing_runtime.py`. Identified in Phase 1117 A11 audit. Must precede any new
   runtime module that consumes ECU amounts from the contaminated surfaces.

2. **SIM-PROVENANCE-01 (OBLIGATED):** Alpha calibration simulation for `PROVENANCE_DECAY_ALPHA`.
   Q2 token `q2_geometric_decay_alpha_decimal_0_5_provisional` remains provisional until this
   SIM runs. AutoResearch-pattern harness. Must log per-node PROVENANCE descendant counts as
   time series (required for SIM-SPECTRAL-02 input).

The window also carries forward SIM-ECU-STABILITY-01 (candidate, not yet authorized) and
the deferred items (Werner φ-bound CDL, ADR-0035 CDL, star expansion) which do not advance
in this window.

**Tail-slot policy:** Phase 1120 is conditional — it becomes FLOAT-KILL-02 if Phase 1119
Commit 3 hits the `consensus/engine.py` blast-radius limit (defined in the FLOAT-KILL-01
prompt). If FLOAT-KILL-02 is triggered, SIM-PROVENANCE-01 commissioning shifts to Phase
1121 and execution either fits in Phase 1122 or defers to Window 1124+.

---

## 2. Baseline and Inheritance

### Ratified CDL chain (relevant to this window)

| CDL | Status | Phase | Dependency |
|-----|--------|-------|------------|
| CDL-081 | Ratified | 943 | `REUSE_ATTRIBUTION_RATE = Decimal("0.20")` |
| CDL-083 | Ratified | 1105 | H-CON-02 panel quorum + REFUTATION attribution |
| CDL-084 | **Ratified** | **1113** | PROVENANCE chain attribution; `PROVENANCE_DECAY_ALPHA = Decimal("0.5")` provisional |

### Active runtime chain (affected by FLOAT-KILL-01)

| Module | Version | Phase | Status |
|--------|---------|-------|--------|
| `epoch_attribution_settle_runtime.py` | `v0.3` | 1114 | Decimal-clean ✓ |
| `passive_ecu_attribution_runtime.py` | — | — | **Float-contaminated — FLOAT-KILL-01 target** |
| `epoch_ledger.py` | — | — | **Float-contaminated — FLOAT-KILL-01 target** |
| `spectral_routing_runtime.py` | — | — | **PRNG-contaminated — FLOAT-KILL-01 target** |
| `consensus/engine.py` | — | — | **Float-contaminated — may trigger FLOAT-KILL-02** |
| `consensus/governance.py` | — | — | **Float-contaminated — FLOAT-KILL-01 target** |
| `server.py` | — | — | **Non-finite Decimal exploit vector — FLOAT-KILL-01 priority** |

### Inherited canonical anchors

- Capsule: `docs/specs/ilc_antigravity_context_capsule_v5.35.md`
- Handoff: `docs/specs/ilc_window_1110_1117_handoff_1117_v0.1.md`
- Prior seq lock: `docs/specs/ilc_phase_1110_1117_sequence_lock_v0.1.md`
- CDL log: `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- STATUS.md
- FLOAT-KILL-01 prompt: `docs/antigravity_tasks/antigravity_prompt__phase_tbd_float_kill_01_ilc_core_float_prng_hardening.md`
  → rename to `antigravity_prompt__phase_1119_float_kill_01_ilc_core_float_prng_hardening.md`

### Next fresh CDL number

**CDL-085** — not opening in this window. Werner φ-bound CDL remains SIM-gated.
ADR-0035 implementation CDL remains planning/authorization-gated.

---

## 3. Track Inventory

### Constitutionally obligated

| Item | Token | Gate |
|------|-------|------|
| FLOAT-KILL-01: float→Decimal + PRNG hardening | `float_kill_01_prng_hardening`, `float_kill_01_active_ecu_path_decimal`, `float_kill_01_interface_decimal_cleanup` | Phase 1119; must precede new ECU-consuming runtime |
| SIM-PROVENANCE-01: alpha calibration | `q2_geometric_decay_alpha_decimal_0_5_provisional`; `q8_epoch_mint_source_sim_provenance_01_required` | Phase 1120 (tight path) or 1121 (FLOAT-KILL-02 path) |

### Deferred governance

| Item | Status |
|------|--------|
| Werner φ-bound CDL (CDL-085 candidate) | Deferred — SIM evidence required; not opening this window |
| ADR-0035 implementation CDL | Deferred — planning/authorization gated; not opening this window |
| Star expansion implementation | Deferred — H-011 patent assessment ongoing; explicit human authorization required |
| SIM-ECU-STABILITY-01 | Candidate — not yet authorized; no commissioning this window |
| SIM-SPECTRAL-02 | Deferred — awaits SIM-PROVENANCE-01 time-series data |
| SIM-HYPEREDGE-01 | Gate clear (CDL-083 ✓); may be planned but not this window |

### Simulation-conditional

| SIM | Condition | This window |
|-----|-----------|-------------|
| SIM-PROVENANCE-01 | FLOAT-KILL-01 Commits 1+2 complete | Phase 1120 (tight) or 1121 (FLOAT-KILL-02 path) |
| SIM-ECU-STABILITY-01 | Human authorization required | Not this window |
| SIM-SPECTRAL-02 | SIM-PROVENANCE-01 time-series data required | Not this window |

---

## 4. FLOAT-KILL-01 Scope

**Source prompt:** `docs/antigravity_tasks/antigravity_prompt__phase_tbd_float_kill_01_ilc_core_float_prng_hardening.md`
(rename header and filename to Phase 1119 after this guidance doc is reviewed).

### Why FLOAT-KILL-01 precedes SIM-PROVENANCE-01

SIM-PROVENANCE-01 imports exclusively from Decimal-clean paths (`epoch_attribution_settle_runtime.py`,
`ilc_core/types.py`). It does NOT consume from the float-contaminated surfaces. Therefore
SIM-PROVENANCE-01 could technically run before FLOAT-KILL-01.

**However:** FLOAT-KILL-01 is sequenced first because:

1. Any new runtime that a SIM or subsequent phase writes might import from the contaminated
   interfaces and inadvertently extend the float surface.
2. The `server.py` non-finite Decimal exploit (infinite-money vector) is a live security
   issue, not a future concern.
3. The `spectral_routing_runtime.py` PRNG violation is an active Sybil-protection gap.
4. Establishing Decimal correctness before commissioning SIM-PROVENANCE-01 ensures the
   SIM's evaluator doesn't inadvertently compare Decimal payout outputs against float
   accumulation baselines pulled from `epoch_ledger.py`.

**Sequencing verdict:** FLOAT-KILL-01 at Phase 1119, SIM-PROVENANCE-01 at Phase 1120.
This is not overrideable without explicit human authorization.

### FLOAT-KILL-01 three-commit structure (inherited from prompt)

| Commit | Scope | Blocker? |
|--------|-------|---------|
| Commit 1 — PRNG kill | `spectral_routing_runtime.py`, `rl_agents.py` | Highest security priority; must land first |
| Commit 2 — Active ECU path | `server.py` (non-finite guard), `passive_ecu_attribution_runtime.py`, `rc/economic_cycle_runtime.py`, `epoch_ledger.py` | Highest economic priority |
| Commit 3 — Interface cleanup | `governance.py`, `engine.py`, `agent.py`, `onboarding.py`, `exceptions.py`, `genesis/work_task.py` | May trigger FLOAT-KILL-02 scope boundary if `engine.py` blast radius > ~10 sites |

### FLOAT-KILL-02 trigger condition

If `consensus/engine.py` has more than ~10 `node_stakes` usage sites requiring Decimal
arithmetic conversion (not just type annotation + coercion), Commit 3 stops at annotation
only and Phase 1120 becomes FLOAT-KILL-02. This triggers the FLOAT-KILL-02 conditional
path (see §8 conditional note).

---

## 5. SIM-PROVENANCE-01 Scope

### Why Phase 1120 and not later

SIM-PROVENANCE-01 is the primary PROVENANCE lane obligation. `PROVENANCE_DECAY_ALPHA`
is provisionally `Decimal("0.5")` and must not be constitutionally locked until this SIM
runs. Sequencing it at Phase 1120 (immediately after FLOAT-KILL-01) is correct because:

- FLOAT-KILL-01 Commits 1+2 will have landed by Phase 1119 completion
- SIM-PROVENANCE-01 imports only from Decimal-clean `epoch_attribution_settle_runtime.py`
  and `ilc_core/types.py` — it is not blocked by any remaining FLOAT-KILL-02 work
- Deferring to Window 1124+ would leave alpha provisional for two full windows

**Decision: SIM-PROVENANCE-01 at Phase 1120. This does not require FLOAT-KILL-02 to be
complete. FLOAT-KILL-02 (if triggered) runs at Phase 1120 and SIM-PROVENANCE-01 shifts
to Phase 1121.**

### AutoResearch harness (from Phase 1116 §D)

Phase 1116 recorded the artifact specification. Phase 1120 writes the actual artifacts:

1. **`docs/specs/sim_provenance_01_program.md`** (or `docs/sims/sim_provenance_01/program.md`)
   — human-readable research objective, constraints, and hard metric:
   - Objective: sweep `PROVENANCE_DECAY_ALPHA` (0.3–0.7), chain-depth distributions,
     creator-overlap rates, identify the parameter regime where payout concentration
     (Gini coefficient) stays below threshold without collapsing attribution breadth
   - Hard metric: Gini coefficient of PROVENANCE payout distribution per epoch < 0.6
     across N simulated epochs; no single creator receives > 40% of total PROVENANCE
     ECU in any 100-epoch window
   - Secondary metric: per-node PROVENANCE descendant count time series (required output
     for SIM-SPECTRAL-02)

2. **`tools/sim_provenance_01.py`** (mutable harness)
   — imports `settle_attribution_batch`, `AttributionEvent`, `EpochAttributionBatch`
   from `ilc_core/`; exposes `ALPHA`, `chain_depth_distribution`, `creator_overlap_rate`,
   `n_epochs` as top-level parameters; the agent mutates these

3. **Evaluator** — embedded in the harness; returns:
   - Gini coefficient of payout distribution
   - Total mint surface (ECU per epoch)
   - Alpha sensitivity (Δpayout / Δalpha)
   - Per-node PROVENANCE descendant count time series (dict: node_id → list of epoch counts)

### Commissioning vs. execution

Phase 1120 covers commissioning (writing `program.md` + harness skeleton + evaluator
structure) and the first AutoResearch run (agent sweeps the parameter space, records
results). If the first run requires overnight execution that cannot complete in one phase,
Phase 1120 delivers commissioning artifacts only; Phase 1121 records execution results
and writes evidence. Codex decides at Phase 1120 execution time whether one phase suffices.

---

## 6. CDL Number Assignments

No CDLs open or ratify in this window.

| CDL | Status | Note |
|-----|--------|------|
| CDL-085 | Reserved, not opening | Next unallocated; Werner φ-bound is SIM-gated |

---

## 7. Candidate Phase Table

| Order | Phase | Topic | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 1118 | Window sequence lock | Foundation | NON-SENSITIVE |
| 2 | 1119 | FLOAT-KILL-01: float→Decimal + PRNG hardening (3 commits) | Runtime | NON-SENSITIVE |
| 3 | 1120 | SIM-PROVENANCE-01 commissioning + first run (tight path) **OR** FLOAT-KILL-02: `engine.py` arithmetic cleanup (FLOAT-KILL-02 path) | Simulation **OR** Runtime | NON-SENSITIVE |
| 4 | 1121 | SIM-PROVENANCE-01 execution results + evidence (tight path) **OR** SIM-PROVENANCE-01 commissioning (FLOAT-KILL-02 path) | Simulation | NON-SENSITIVE |
| 5 | 1122 | Coherence report + capsule v5.36 (tight path) **OR** SIM-PROVENANCE-01 first run + results (FLOAT-KILL-02 path) | Synthesis **OR** Simulation | NON-SENSITIVE |
| 6 | 1123 | Window 1118–1123 closure gate | Gate | **SENSITIVE** |

### Conditional note on Phases 1120–1122

**Tight path (FLOAT-KILL-01 completes in one phase, no FLOAT-KILL-02):**

| Phase | Assignment |
|-------|-----------|
| 1120 | SIM-PROVENANCE-01 commissioning + first AutoResearch run |
| 1121 | SIM-PROVENANCE-01 results, evidence, tests |
| 1122 | Coherence report + capsule v5.36 |
| 1123 | Closure gate |

**FLOAT-KILL-02 path (engine.py blast radius exceeded in Phase 1119 Commit 3):**

| Phase | Assignment |
|-------|-----------|
| 1120 | FLOAT-KILL-02: `consensus/engine.py` Decimal arithmetic cleanup |
| 1121 | SIM-PROVENANCE-01 commissioning + first AutoResearch run |
| 1122 | SIM-PROVENANCE-01 results + evidence **OR** coherence report if SIM execution defers |
| 1123 | Closure gate (SIM execution may defer to Window 1124+ if overnight run incomplete) |

**FLOAT-KILL-02 path — SIM execution deferral rule:**
If Phase 1122 cannot fit both SIM results AND coherence in one phase, coherence takes
the slot and SIM execution defers to Window 1124+. The window closes on FLOAT-KILL work
complete + SIM-PROVENANCE-01 commissioned, which satisfies the primary FLOAT-KILL-01
obligation. SIM-PROVENANCE-01 alpha lock remains provisional and carries forward.

### Note on Phase 1119 non-ratifying structure

Phase 1119 has no CDL doc changes and no CDL env var. The three commits are purely runtime
and security hardening. The pre-commit hook will enforce the separation automatically —
no manual override needed.

### Note on Phase 1120 SIM commissioning structure

`sim_provenance_01.py` is written to `tools/` (not `tests/` or `ilc_core/`). It is a
mutable research harness, not a production module and not a test. Tests written in Phase
1121 assert on the evaluator's output characteristics (Gini below threshold, time-series
shape correct), not on the simulation's internal parameter choices.

---

## 8. Sensitivity Classification

### SENSITIVE phases (require human GO token before execution)

- **Phase 1123** — Window closure gate; structural boundary; requires GO token.

No CDL mutations in this window. No other SENSITIVE phases.

### NON-SENSITIVE phases

- **Phase 1118** — Sequence lock only; no mutation, no CDL changes.
- **Phase 1119** — Pure runtime hardening; no CDL env var; pre-commit hook enforces
  separation automatically.
- **Phase 1120** — SIM commissioning (harness + program.md) or FLOAT-KILL-02 runtime
  cleanup; neither touches CDL docs.
- **Phase 1121** — SIM execution + results or commissioning; no CDL changes.
- **Phase 1122** — Coherence report or SIM results; no CDL changes.

### Conditional phases rule

No conditional phases in this window — all slots are NON-SENSITIVE regardless of which
path (tight vs. FLOAT-KILL-02) is active.

### Pre-commit hook

No phases in this window require `ILC_CDL_MUTATION_AUTHORIZED`. The pre-commit hook
remains active and will block any accidental CDL doc mutation.

---

## 9. Scope Notes for Fixed Phases

### Phase 1118 — Window Sequence Lock

NON-SENSITIVE. No GO token required.

**Deliverables:**
- `docs/specs/ilc_phase_1118_1123_sequence_lock_v0.1.md` (new)

**Required content:**
- Window identity, baseline, locked phase table
- Sequencing constraints (5 constraints minimum; see §10)
- FLOAT-KILL-01 scope summary (file list, three-commit structure, FLOAT-KILL-02 trigger condition)
- SIM-PROVENANCE-01 scope summary (harness artifact spec, hard metric)
- Sensitivity classification

**Commit subject:** `docs(g8): phase 1118 window 1118-1123 sequence lock`

---

### Phase 1119 — FLOAT-KILL-01

NON-SENSITIVE. No GO token required. No CDL env var.

**Source prompt:** Rename `antigravity_prompt__phase_tbd_float_kill_01_ilc_core_float_prng_hardening.md`
to `antigravity_prompt__phase_1119_float_kill_01_ilc_core_float_prng_hardening.md` and
update the **Phase:** header field from `TBD` to `1119`. No other prompt changes required.

**Deliverables:**
- Three commits (see FLOAT-KILL-01 prompt §§Commit 1–3)
- `docs/phases/phase_1119_float_kill_01_ilc_core_float_prng_hardening_walkthrough.md`
- STATUS.md update

**Test structure:** Update any test assertions that were asserting float return types;
do not re-introduce float casts to make tests pass.

**Regression gate after each commit:**
```bash
PATH=.venv/bin:$PATH python3 -m pytest -q
```

**Scope boundary:** If `consensus/engine.py` Decimal arithmetic cleanup exceeds ~10
usage sites in Commit 3, stop at annotation + coercion only. Flag FLOAT-KILL-02 in
the walkthrough. This activates the FLOAT-KILL-02 path for Phase 1120.

**Commit subjects** (three commits):
```
fix(security): replace Mersenne Twister PRNG with secrets in routing and rl_agents
fix(security): float→Decimal for active ECU paths + non-finite Decimal rejection
fix(security): float→Decimal for consensus/agent/onboarding/genesis ECU interfaces
```

**Phantom edit guard:**
```bash
grep -n "float\|import random" \
  ilc_core/economics/epoch_attribution_settle_runtime.py \
  ilc_core/types.py
```
Must return zero float/random violations in these two Decimal-clean files. If found,
escalate — they indicate a phantom edit.

---

### Phase 1123 — Window 1118–1123 Closure Gate

**SENSITIVE** — human GO token required before execution.

**Deliverables:**
- `tests/test_phase_1123_window_1118_1123_closure_gate.py`
- `docs/specs/ilc_window_1118_1123_handoff_1123_v0.1.md`
- `docs/phases/phase_1123_window_1118_1123_closure_gate_walkthrough.md`
- STATUS.md update
- Append closure status to `docs/specs/ilc_window_1118_1123_candidate_phase_grouping_v0.1.md`

**Gate test categories:**
- Cat 0: Selftest guard
- Cat 1: Phase 1118 sequence lock present and correctly tokened
- Cat 2: FLOAT-KILL-01 Commits 1+2 complete — verify `import random` absent from routing,
  `float(ecu_estimate_decimal)` absent from rc/economic_cycle_runtime.py,
  non-finite Decimal guard present in server.py
- Cat 3: FLOAT-KILL-01 or FLOAT-KILL-02 Commit 3 complete — verify `passive_ecu_attribution_runtime.py`
  returns Decimal, `epoch_ledger.py` fields are Decimal
- Cat 4: SIM-PROVENANCE-01 commissioned — `program.md` exists, `tools/sim_provenance_01.py` exists
- Cat 5: SIM-PROVENANCE-01 results present (skip if execution deferred to Window 1124+;
  in that case assert commissioning artifacts present and time-series output field defined)
- Cat 6: Coherence report + capsule v5.36 present and correctly tokened
- Cat 7: No regression — full suite passes

**Pre-commit hook:** None (no CDL mutation).
**Required: `ILC_PHASE_1123_GATE_SELFTEST=1`** in category 0.

**Selftest guard chain:** Read prior gate test files for category structure rather than
reasoning by analogy — specifically read `tests/test_phase_1117_window_1110_1117_closure_gate.py`
as the format reference.

---

## 10. Key Dependencies and Open Questions

### Must-resolve at window entry

1. Confirm Phase 1117 complete and committed (`0437fcb1`).
2. Confirm capsule v5.35 is the current capsule.
3. Rename FLOAT-KILL-01 prompt file (TBD → 1119) and update Phase header before Phase 1119 executes.

### Sequencing constraints

1. Phase 1118 (seq lock) must precede all other phases.
2. Phase 1119 Commit 1 (PRNG kill) must precede Commit 2 (ECU path); Commit 2 must precede Commit 3.
3. FLOAT-KILL-01 Commits 1+2 must complete before SIM-PROVENANCE-01 commissioning begins.
   (Commit 3 / FLOAT-KILL-02 need not be complete — SIM imports only Decimal-clean paths.)
   Exception: if Phase 1119 Commit 1 or Commit 2 discovers direct float/PRNG contamination
   of the PROVENANCE simulation path (`epoch_attribution_settle_runtime.py`, `ilc_core/types.py`,
   or their SIM-PROVENANCE-01 imports), stop and escalate; SIM-PROVENANCE-01 may not
   commission until the contamination is resolved.
4. SIM-PROVENANCE-01 commissioning must precede SIM-PROVENANCE-01 execution.
5. All phases 1118–1122 must precede Phase 1123 (coherence cites all window work; gate
   cites coherence).

### Open questions

| Question | Resolution path |
|----------|-----------------|
| Does `consensus/engine.py` Decimal arithmetic blast radius exceed ~10 sites? | Codex reads file at Phase 1119 Commit 3 and decides |
| Can SIM-PROVENANCE-01 execution (overnight run) complete within one phase? | Codex decides at Phase 1120 execution; defer to Window 1124+ if not |
| Is SIM-ECU-STABILITY-01 ready for authorization? | Human decision; not blocking this window |

### Permanently deferred from this window

- Werner φ-bound CDL (CDL-085) — SIM evidence required
- ADR-0035 implementation CDL — planning/authorization required
- Star expansion implementation — H-011 patent gate + explicit human authorization
- SIM-SPECTRAL-02 — awaits SIM-PROVENANCE-01 time-series data
- SIM-HYPEREDGE-01 commissioning — not this window

---

## 11. Known Patterns and Technical Constraints

### Novel patterns this window

1. **First AutoResearch-pattern SIM harness in ILC history:** `sim_provenance_01.py` is
   a mutable research harness placed in `tools/`, not `tests/` or `ilc_core/`. The
   evaluator function is embedded in the harness. Tests in Phase 1121 assert on the
   evaluator's output characteristics, not the harness internals.

2. **First window with no CDL lifecycle phases:** All phases are Runtime, Simulation,
   Synthesis, or Gate. No SENSITIVE CDL mutation phases except the structural closure gate.

3. **FLOAT-KILL-02 conditional path:** First use of a FixN prompt for a phase that may
   need a second pass due to blast-radius scope. FLOAT-KILL-02 prompt to be drafted at
   Phase 1119 walkthrough time if triggered.

### Historical prelock hardening

No CDL phases this window — no prelock assertions to add.

### Phantom edit guard

FLOAT-KILL-01 modifies multiple `ilc_core/` files. After all three commits, run:
```bash
grep -rn "import random" ilc_core/ --include="*.py" \
  --exclude-dir=sim --exclude-dir=analysis | grep -v devnet | grep -v benchmark
# Expected: zero results

grep -n "float(ecu\|float(stake\|float(reward\|float(.*[Dd]ecimal" \
  ilc_core/economics/passive_ecu_attribution_runtime.py \
  ilc_core/rc/economic_cycle_runtime.py \
  ilc_core/economics/epoch_ledger.py
# Expected: zero results
```

The Decimal-clean files must not be touched by FLOAT-KILL-01:
```bash
git show HEAD -- ilc_core/economics/epoch_attribution_settle_runtime.py \
                 ilc_core/types.py
# Expected: no diff (these files must not appear in any FLOAT-KILL-01 commit)
```

### Pre-commit hook clean-state guard

The pre-commit hook enforces that CDL doc mutations require `ILC_CDL_MUTATION_AUTHORIZED`.
Since no CDL mutations occur in this window, the hook acts as a safety net only. No bypass
or workaround is needed.

### Closure gate selftest guard chain

Phase 1123 gate test must include `ILC_PHASE_1123_GATE_SELFTEST=1` in category 0.
Read `tests/test_phase_1117_window_1110_1117_closure_gate.py` for the canonical selftest
guard pattern before writing Phase 1123's gate test.

---

## 12. Non-Goals and Explicitly Deferred Items

- **No CDL-085 opening** — Werner φ-bound CDL is SIM-gated; not this window
- **No ADR-0035 CDL** — planning/authorization gated; not this window
- **No star expansion implementation** — H-011 patent gate + human authorization required
- **No SIM-ECU-STABILITY-01 commissioning** — candidate only; authorization not granted
- **No SIM-SPECTRAL-02** — awaits SIM-PROVENANCE-01 time-series data
- **No SIM-HYPEREDGE-01** — gate clear but not scheduled this window
- **Do not lock `PROVENANCE_DECAY_ALPHA`** — remains provisional until SIM-PROVENANCE-01
  confirms the alpha value; do not change the `_provisional` token
- **Do not modify `epoch_attribution_settle_runtime.py` or `ilc_core/types.py`** —
  these are Decimal-clean; FLOAT-KILL-01 must not touch them
- **Do not attempt SIM-SPECTRAL-02 speculation** without SIM-PROVENANCE-01 data

---

## 13. Key Canonical Anchors for Prompt Drafting

Every phase prompt in this window must reference:

- `docs/specs/ilc_antigravity_context_capsule_v5.35.md` **(PRIMARY)**
- `docs/specs/ilc_window_1110_1117_handoff_1117_v0.1.md`
- `docs/specs/ilc_phase_1118_1123_sequence_lock_v0.1.md` (once written at Phase 1118)
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/phases/STATUS.md`

For Phase 1119 specifically:
- `docs/antigravity_tasks/antigravity_prompt__phase_1119_float_kill_01_ilc_core_float_prng_hardening.md`
  (renamed from TBD before execution)

For Phase 1120 (tight path — SIM commissioning):
- `docs/specs/ilc_cdl_084_provenance_chain_attribution_opening_1111_v0.1.md` §3.4 (PROVENANCE settlement spec)
- `ilc_core/economics/epoch_attribution_settle_runtime.py` (runtime to import from)
- `ilc_core/types.py` (constants: `PROVENANCE_DECAY_ALPHA`, `PROVENANCE_MAX_DEPTH`, `REUSE_ATTRIBUTION_RATE`)
- `docs/research/ilc_relative_directional_energy_meter_and_epistemic_efficiency_plan_v0.1.md`
  (SIM-SPECTRAL-02 forward obligation — time series data requirement)

For Phase 1123 (closure gate):
- All Phase 1118–1122 test files and artifacts.
- `tests/test_phase_1117_window_1110_1117_closure_gate.py` (selftest guard format reference)

**Status:** PENDING — awaiting human review before Phase 1118 executes.
