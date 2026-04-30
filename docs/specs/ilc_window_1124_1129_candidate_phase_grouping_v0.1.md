# ILC Window 1124–1129: Candidate Phase Grouping

**Author:** Claude Sonnet 4.6 (local architectural reviewer)
**Date:** 2026-04-30
**Baseline:** Window 1118–1123 CLOSED (Phase 1123, commit `2b8b05b9`). CDL-084 ratified
             (Phase 1113). PROVENANCE settlement active (Phase 1114). SIM-PROVENANCE-01
             complete (Phases 1120–1121); α=0.45 SIM recommendation; Q8 satisfied; Q2 active.
             Capsule v5.36. 247 tests.
**Planning note:** This is a candidate grouping, not a locked sequence. Phases 1124–1126
are the hard minimum lane (seq lock + CDL-084 Q2 amendment prelock + ratification). Phases
1127–1128 are primary-track synthesis slots. Phase 1129 is the closure gate.

---

## 1. Window Identity and Scope

Window 1124–1129 is a **constitutional amendment window** with a single active lane: the
CDL-084 Q2 alpha amendment that formally adopts the SIM-PROVENANCE-01 recommendation of
`PROVENANCE_DECAY_ALPHA = Decimal("0.45")`.

This is not a new CDL opening. The amendment modifies the existing CDL-084 document and
the corresponding runtime constant in `ilc_core/types.py`. The SIM evidence basis (Q8
satisfied, two runs, 3-seed robustness, α=0.45 keep rate 3/3) is already in the record.
The amendment converts that evidence into a constitutional lock.

All other deferred items (SIM-SPECTRAL-02, SIM-ECU-STABILITY-01, Werner φ-bound CDL,
ADR-0035 CDL, star expansion, Conley research, SIM-HYPEREDGE-01) do **not advance** in
this window. This window closes exactly one open obligation and hands the system to the
next window in a clean state.

**Tail-slot policy:** No conditional tail slots. The six-phase window is fully determined
by the amendment lane. If unexpected scope is discovered during prelock (Phase 1125) —
e.g., substantially more test files hardcode `Decimal("0.5")` than anticipated — Phase
1126 may absorb the additional test-update work without requiring a new phase. If the
scope truly cannot fit, escalate to the human lead before proceeding.

---

## 2. Baseline and Inheritance

### Ratified CDL chain (relevant to this window)

| CDL | Status | Phase | Note |
|-----|--------|-------|------|
| CDL-081 | Ratified | 943 | `REUSE_ATTRIBUTION_RATE = Decimal("0.20")` |
| CDL-083 | Ratified | 1105 | H-CON-02 panel quorum + REFUTATION attribution |
| CDL-084 | Ratified | 1113 | PROVENANCE chain attribution; Q2 active (α provisional at 0.5); Q8 satisfied (SIM complete) |

### Active runtime chain (affected by amendment)

| Constant | Current value | After amendment |
|----------|---------------|-----------------|
| `PROVENANCE_DECAY_ALPHA` | `Decimal("0.5")` | `Decimal("0.45")` |
| `EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION` | `"epoch_attribution_settle_runtime_1114.v0.3"` | bump to `v0.4` |

### Inherited canonical anchors

- Capsule: `docs/specs/ilc_antigravity_context_capsule_v5.36.md`
- Handoff: `docs/specs/ilc_window_1118_1123_handoff_1123_v0.1.md`
- Prior seq lock: `docs/specs/ilc_phase_1118_1123_sequence_lock_v0.1.md`
- SIM evidence: `docs/sims/sim_provenance_01/alpha_disposition_phase_1121.md`
- CDL-084 spec (amendment target): `docs/specs/ilc_cdl_084_provenance_chain_attribution_opening_1111_v0.1.md`
- CDL log: `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- STATUS.md

### Next fresh CDL number

**CDL-085** — not opening in this window. Werner φ-bound CDL remains SIM-gated.
ADR-0035 implementation CDL remains planning/authorization-gated.

---

## 3. Track Inventory

### 3a. Constitutionally obligated

| Item | Obligation source | This-window treatment |
|------|------------------|-----------------------|
| CDL-084 Q2 alpha amendment | CDL-084 Q2 token (`q2_geometric_decay_alpha_decimal_0_5_provisional`) + SIM-PROVENANCE-01 Q8 satisfaction | **Primary lane — Phases 1125–1126** |

### 3b. Deferred governance

| Item | Gate | Status |
|------|------|--------|
| Werner φ-bound CDL (CDL-085 candidate) | SIM evidence required before CDL can open | Not advancing |
| ADR-0035 implementation CDL | Planning/authorization gated | Not advancing |
| Star expansion implementation | H-011 patent assessment + explicit human authorization | Not advancing |
| SIM-HYPEREDGE-01 | Can be planned; not yet scheduled | Not advancing |

### 3c. Simulation-conditional

| Item | Status | Gate |
|------|--------|------|
| SIM-SPECTRAL-02 | Data dependency satisfied (Phase 1120 time series); non-canonical research | Not scheduling this window; deferred to Window 1130+ |
| SIM-ECU-STABILITY-01 | Candidate — not authorized | Not scheduling this window |
| Conley Index research | Deferred pre-RC1.0 | Not scheduling this window |

---

## 4. CDL-084 Q2 Amendment Scope

### What is being amended

CDL-084 Q2 currently reads:

> Geometric decay; `PROVENANCE_DECAY_ALPHA = Decimal("0.5")`; provisional pending
> SIM-PROVENANCE-01. Token: `q2_geometric_decay_alpha_decimal_0_5_provisional`.

After amendment, it will read:

> Geometric decay; `PROVENANCE_DECAY_ALPHA = Decimal("0.45")`; **locked**.
> SIM-PROVENANCE-01 Run 01 (Phase 1120) + Run 02 (Phase 1121): α=0.45 achieves keep
> rate 3/3 across seeds 42/1337/2026; α=0.50 achieves keep rate 2/3 (seed-marginal).
> Token: `q2_geometric_decay_alpha_decimal_0_45_locked`.

### Files that must be modified

**Commit 1 — Runtime (NON-CDL commit, no CDL env var):**
- `ilc_core/types.py`: `PROVENANCE_DECAY_ALPHA: Decimal = Decimal("0.45")`
  Update the comment: change "provisional pending SIM-PROVENANCE-01" to "locked Phase 1126"
  Update `CDL_084_TYPES_DEPENDENCY` token if needed (bump version suffix)
- `ilc_core/economics/epoch_attribution_settle_runtime.py`: version bump to
  `"epoch_attribution_settle_runtime_1126.v0.4"`

**Commit 2 — CDL doc (requires CDL env var):**
- `docs/specs/ilc_cdl_084_provenance_chain_attribution_opening_1111_v0.1.md`
  Q2 row: update value, remove "provisional", add "locked Phase 1126"
  Add SIM evidence tokens: cite alpha_disposition_phase_1121.md
  CDL log: update Q2 row status to locked

### Payout values that change

After amendment, the three-hop PROVENANCE payout changes:

| Hop | Old payout (α=0.50) | New payout (α=0.45) |
|-----|---------------------|---------------------|
| 1 | `Decimal("0.10")` | `Decimal("0.09")` |
| 2 | `Decimal("0.05")` | `Decimal("0.0405")` |
| 3 | `Decimal("0.025")` | `Decimal("0.018225")` |

This is the primary test-regression risk. Any test that asserts these hardcoded
payout values (instead of computing them from the live constant) will break.

### Phantom edit risk: hardcoded Decimal("0.5") assertions

**Critical prelock task (Phase 1125):** Grep all test files for hardcoded
`Decimal("0.5")` in the context of PROVENANCE payout assertions, plus any
`PROVENANCE_DECAY_ALPHA == Decimal("0.5")` live-import checks. Record all affected
tests before the ratification phase writes anything. The ratification phase must
update these in the same commit as the runtime change.

Detection command (run at Phase 1125):
```bash
grep -rn 'Decimal("0.5")' tests/ | grep -v "REUSE\|ALPHA.*0\.5\|0\.5.*ALPHA" | head -30
grep -rn 'PROVENANCE_DECAY_ALPHA' tests/
grep -rn '"0\.10"\|"0\.05"\|"0\.025"' tests/
```

Note: The Phase 1117 and 1123 closure gate tests may contain live-import payout smoke
tests that assert `Decimal("0.10")`, `Decimal("0.05")`, `Decimal("0.025")`. These
**must be updated** in Commit 1 of Phase 1126 alongside the types.py change, because
they compute live payouts from the runtime (not from git-show historical state).

Historical `git show` assertions (which read old commit file content) do NOT need
updating — they will correctly still return `Decimal("0.5")` when reading the pre-1126
commit.

### Non-goals for this amendment

- Do not change `PROVENANCE_MAX_DEPTH`
- Do not change `REUSE_ATTRIBUTION_RATE`
- Do not change any other CDL-084 Q-token decisions
- Do not alter the PROVENANCE settlement algorithm in `epoch_attribution_settle_runtime.py`
  beyond the version bump — only the constant value changes
- Do not open CDL-085 or any new CDL

---

## 5. CDL Number Assignments

| CDL | Title | Decision digest anchor | Opening phase | Amendment phase |
|-----|-------|------------------------|---------------|-----------------|
| CDL-084 (amendment) | Q2 alpha lock: `PROVENANCE_DECAY_ALPHA = Decimal("0.45")` | `q2_geometric_decay_alpha_decimal_0_45_locked` | Phase 1111 (existing) | Phase 1126 |

This is an amendment to CDL-084, not a new CDL. CDL-085 is not assigned in this window.

---

## 6. Candidate Phase Table

| Order | Phase | Topic | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 1124 | Window sequence lock | Foundation | NON-SENSITIVE |
| 2 | 1125 | CDL-084 Q2 amendment prelock hardening | Constitutional | NON-SENSITIVE |
| 3 | 1126 | CDL-084 Q2 ratification: `PROVENANCE_DECAY_ALPHA` → `Decimal("0.45")` | Constitutional / Runtime | **SENSITIVE** |
| 4 | 1127 | Amendment evidence tests | Constitutional | NON-SENSITIVE |
| 5 | 1128 | Coherence report + capsule v5.37 | Synthesis | NON-SENSITIVE |
| 6 | 1129 | Window 1124–1129 closure gate | Gate | **SENSITIVE** |

### Note on Phase 1126 two-commit structure

Phase 1126 follows the established pattern for CDL mutations that also touch a runtime file:

- **Commit 1 — Runtime:** `ilc_core/types.py` + `epoch_attribution_settle_runtime.py`
  version bump + affected test updates. No CDL env var.
- **Commit 2 — CDL doc only:** CDL-084 Q2 row update + CDL log row update.
  Requires `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1126`.

The pre-commit hook enforces that no `ilc_core/` changes appear in Commit 2.
The runtime and CDL mutations must be in separate commits.

### Note on Phase 1125 prelock scope

Phase 1125 is lighter than a full CDL prelock because no new mechanism is being
specified — only a constant value is changing. The prelock deliverable is:

1. A short prelock doc (≤ 2 pages) recording:
   - SIM evidence basis for α=0.45 (cite Run 01 + Run 02 key numbers)
   - The specific files and constants being changed
   - The hardcoded-value grep results (all tests that will need updating)
   - The historical commit ref for Phase 1113 (`3d943f32`) that will be used in the
     Phase 1127 historical assertion
2. No new runtime files
3. No CDL env var

---

## 7. Sensitivity Classification

**SENSITIVE — requires human GO token:**
- Phase 1126 — CDL mutation (CDL-084 Q2 update) + runtime mutation (`types.py`)
- Phase 1129 — closure gate; structural boundary

**NON-SENSITIVE — all other phases:**
- Phase 1124 — seq lock; no mutation
- Phase 1125 — prelock hardening; read-only audit + doc; no CDL env var; no `ilc_core/` change
- Phase 1127 — evidence tests; no CDL mutation; test file changes only
- Phase 1128 — coherence + capsule; no CDL mutation; doc only

**No conditional phases.** All six phases have deterministic sensitivity.

**Pre-commit hook (Phase 1126 Commit 2 only):**
```
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1126
```

---

## 8. Scope Notes for Fixed Phases

### Phase 1124 — Sequence Lock (NON-SENSITIVE)

**Deliverables:**
- `docs/specs/ilc_phase_1124_1129_sequence_lock_v0.1.md`

**Required content:**
- Phase table (6 phases, 1124–1129)
- Sequencing constraints:
  1. Phase 1124 precedes all others
  2. Prelock (1125) must precede ratification (1126)
  3. Evidence tests (1127) must follow ratification (1126)
  4. Phases 1124–1128 must precede closure gate (1129)
- CDL-084 Q2 amendment scope summary (constant being changed, two-commit structure)
- Tokens: `window_1124_1129_sequence_lock_committed_phase_1124`,
  `cdl_084_q2_amendment_prelock_precedes_ratification`

**Commit subject:** `docs(g8): phase 1124 window 1124-1129 sequence lock`

---

### Phase 1125 — CDL-084 Q2 Amendment Prelock (NON-SENSITIVE)

**Deliverables:**
- `docs/specs/ilc_cdl_084_q2_amendment_prelock_1125_v0.1.md`

**Required content:**
1. SIM evidence summary: Run 01 (α=0.45 pass, α=0.50 fail margin), Run 02
   (α=0.45 keep rate 3/3, α=0.50 keep rate 2/3). Cite exact mint drift values
   from `alpha_disposition_phase_1121.md`.
2. Files being changed: `ilc_core/types.py`, `epoch_attribution_settle_runtime.py`
   (version bump), CDL-084 doc, CDL log.
3. Grep results: all test files containing `Decimal("0.5")`, `Decimal("0.10")`,
   `Decimal("0.05")`, `Decimal("0.025")`, or live imports of `PROVENANCE_DECAY_ALPHA`
   that assert its value. List each file and line number.
4. Historical commit ref for Phase 1113 ratification commit (`3d943f32`) — will be
   used in Phase 1127 historical assertion.
5. Prelock token: `cdl_084_q2_prelock_hardened_phase_1125`

**No CDL env var. No `ilc_core/` mutation.**

**Commit subject:** `docs(cdl): CDL-084 Q2 alpha amendment prelock hardening (Phase 1125)`

---

### Phase 1126 — CDL-084 Q2 Ratification (SENSITIVE)

**Requires human GO token before execution.**

**Deliverables:**
- Modified `ilc_core/types.py` (PROVENANCE_DECAY_ALPHA = Decimal("0.45"))
- Modified `ilc_core/economics/epoch_attribution_settle_runtime.py` (version bump)
- Updated test files identified in Phase 1125 prelock grep (hardcoded value corrections)
- Modified `docs/specs/ilc_cdl_084_provenance_chain_attribution_opening_1111_v0.1.md`
  (Q2 row: provisional → locked, new token)
- Modified `docs/specs/ilc_constitutional_decision_log_v0.1.md` (CDL-084 Q2 status)

**Two-commit structure:**

Commit 1 (runtime — no CDL env var):
- `ilc_core/types.py`: `PROVENANCE_DECAY_ALPHA = Decimal("0.45")`; update comment; bump
  `CDL_084_TYPES_DEPENDENCY` version suffix if needed
- `ilc_core/economics/epoch_attribution_settle_runtime.py`: version bump to
  `"epoch_attribution_settle_runtime_1126.v0.4"`
- All test files that assert hardcoded PROVENANCE payout values or
  `PROVENANCE_DECAY_ALPHA == Decimal("0.5")`: update to new values/constant

Commit 2 (CDL doc — requires env var):
- `docs/specs/ilc_cdl_084_provenance_chain_attribution_opening_1111_v0.1.md`: Q2 update
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`: CDL-084 Q2 row update
- `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1126`

**New Q2 token:** `q2_geometric_decay_alpha_decimal_0_45_locked`

**Commit subjects:**
- Commit 1: `fix(cdl): CDL-084 Q2 PROVENANCE_DECAY_ALPHA Decimal("0.45") + runtime v0.4 (Phase 1126)`
- Commit 2: `docs(cdl): CDL-084 Q2 amendment ratified — alpha locked at 0.45 (Phase 1126)`

**Phantom edit guard:** After Commit 1, run:
```bash
grep -rn 'Decimal("0.5")' tests/ ilc_core/types.py
grep -rn '"0\.10"\|"0\.05"\|"0\.025"' tests/
```
Expected: zero PROVENANCE-related hits. If any remain, fix before Commit 2.

**Pre-commit hook (Commit 2 only):**
```
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1126
```

---

### Phase 1127 — Amendment Evidence Tests (NON-SENSITIVE)

**Deliverables:**
- `tests/test_phase_1127_cdl_084_q2_amendment.py` — minimum 8 tests

**Required test coverage:**

| ID | Assertion |
|----|-----------|
| E1 | `PROVENANCE_DECAY_ALPHA == Decimal("0.45")` and `isinstance(PROVENANCE_DECAY_ALPHA, Decimal)` |
| E2 | `not isinstance(PROVENANCE_DECAY_ALPHA, float)` |
| E3 | CDL-084 doc contains `q2_geometric_decay_alpha_decimal_0_45_locked` token |
| E4 | CDL-084 doc does NOT contain `q2_geometric_decay_alpha_decimal_0_5_provisional` as a live Q2 status (may appear in historical text; assert it is superseded) |
| E5 | Historical git-show assertion: Phase 1113 runtime commit (`3d943f32:ilc_core/types.py`) still contains `Decimal("0.5")` — the old value is preserved in git history |
| E6 | `EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION == "epoch_attribution_settle_runtime_1126.v0.4"` |
| E7 | Three-hop PROVENANCE payout smoke test with α=0.45: hop 1 = `Decimal("0.09")`, hop 2 = `Decimal("0.0405")`, hop 3 = `Decimal("0.018225")` |
| E8 | Prelock hardening token present: `ilc_cdl_084_q2_amendment_prelock_1125_v0.1.md` contains `cdl_084_q2_prelock_hardened_phase_1125` |

**Commit subject:** `test(cdl): CDL-084 Q2 amendment evidence tests (Phase 1127)`

**Regression baseline:** Post-Phase 1126. All prior passing tests must still pass
(including Phase 1117 and 1123 gate tests after their PROVENANCE payout smoke assertions
are updated in Phase 1126 Commit 1).

---

### Phase 1128 — Coherence Report + Capsule v5.37 (NON-SENSITIVE)

**Deliverables:**
- `docs/specs/ilc_integration_coherence_report_1128_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.37.md`
- `tests/test_phase_1128_coherence_capsule_v5_37.py` — minimum 6 tests

**Capsule v5.37 key updates from v5.36:**
- §1 frontier: Window 1124–1129 phases 1124–1128 complete; Phase 1129 gate pending
- §2 CDL chain: CDL-084 Q2 row updated — status from "active pending CDL amendment"
  to "locked Phase 1126"; `PROVENANCE_DECAY_ALPHA = Decimal("0.45")`
- §3 runtime: `PROVENANCE_DECAY_ALPHA = Decimal("0.45")` — locked
- §4 CDL-084 Q-tokens: Q2 token changed to `q2_geometric_decay_alpha_decimal_0_45_locked`
- §5 forward obligations: Remove CDL-084 Q2 alpha amendment row (complete);
  SIM-SPECTRAL-02 remains deferred; all other carry-forwards unchanged
- §6 test inventory: add Phase 1127 evidence tests (8 tests); update combined count

**Commit subject:** `docs(coherence): phase 1128 coherence report + capsule v5.37`

---

## 9. Key Dependencies and Open Questions

### Must-resolve at window entry

- Human authorization required for Phase 1126 (CDL mutation + runtime mutation).
  Without explicit GO token, Phase 1126 must not execute.
- Phase 1125 prelock grep must complete and document all hardcoded-value test sites
  before Phase 1126 begins. If the blast radius is substantially larger than expected
  (> 10 test assertion sites), escalate before proceeding with Phase 1126.

### Sequencing constraints

1. Phase 1124 seq lock precedes all phases.
2. Phase 1125 prelock must precede Phase 1126.
3. Phase 1126 Commit 1 (runtime) must precede Commit 2 (CDL doc).
4. Phase 1127 evidence tests must follow Phase 1126.
5. Phases 1124–1128 must precede Phase 1129.

### Open questions

**Q: Should α=0.45 be adopted, or should more SIM runs be commissioned first?**
The two-run evidence (Run 01 coarse sweep, Run 02 fine sweep × 3 seeds) is the basis for
the SIM recommendation. The human lead must confirm they accept this evidence basis before
Phase 1126 executes. If additional SIM runs are required, Phase 1126 becomes an extended
run phase (using `sim_provenance_01.py`) and ratification moves to the next window.
This guidance doc assumes the evidence is accepted. If not, the window scope changes
materially — flag immediately.

**Q: Are there other tests besides the identified gate tests that hardcode Decimal("0.5")?**
Answered by Phase 1125 prelock grep. The answer determines the scope of Commit 1.

### Permanently deferred (not advancing this window)

- SIM-SPECTRAL-02 — time-series data ready; scheduling deferred to Window 1130+
- SIM-ECU-STABILITY-01 — candidate; not authorized
- Werner φ-bound CDL (CDL-085) — SIM-gated
- ADR-0035 implementation CDL — planning/authorization gated
- Star expansion — H-011 patent gate
- SIM-HYPEREDGE-01 — gate clear; not scheduled
- Conley Index research — deferred pre-RC1.0

---

## 10. Known Patterns and Technical Constraints

### Novel pattern: CDL amendment (parameter lock, not new mechanism)

This is the first window in recent history where the CDL vehicle amends an existing
constitutional parameter rather than opening a new mechanism. The key distinction:

- No new `CDL_084_DEPENDENCY` token in `epoch_attribution_settle_runtime.py` —
  the existing dependency token remains but the runtime version bumps.
- The CDL-084 spec is amended in place (not a new CDL doc). The amendment adds a
  "locked Phase 1126" notation to Q2 and supersedes the `_provisional` token.
- CDL log gets a new row or sub-row for the Q2 amendment, not a new CDL entry.

### Phantom edit guard (CRITICAL)

Changing `PROVENANCE_DECAY_ALPHA` from `Decimal("0.5")` to `Decimal("0.45")` changes
the live payout arithmetic. Any test that calls `settle_attribution_batch()` with a
PROVENANCE event and asserts specific payout amounts in Decimal literals will break.

The Phase 1125 grep is mandatory. Do not estimate; run the grep and record every hit.
The Phase 1126 Commit 1 must be verified clean before Commit 2 proceeds.

### Historical prelock hardening pattern

Phase 1127 test E5 uses the pattern: `git show <commit>:<file>` where commit is the
Phase 1113 ratification commit (`3d943f32`) and file is `ilc_core/types.py`. This
asserts the old value is preserved in git history. This pattern was established in
prior ratification windows and must be used here.

### Pre-commit hook ilc_core/ guard

Phase 1126 Commit 2 (CDL doc) must contain only doc changes. The pre-commit hook will
reject any `ilc_core/` changes in the CDL commit. Commit 1 handles all runtime changes.
Do not combine the two commits.

### Closure gate selftest guard chain

Phase 1129 gate test must include `ILC_PHASE_1129_GATE_SELFTEST=1` in its category 3
(or equivalent prior gate re-execution block). Read all prior gate test files to
determine the full selftest variable list required — do not reason by analogy from
the 1123 gate. The selftest guard chain is cumulative.

---

## 11. Non-Goals and Explicitly Deferred Items

- **Do not open CDL-085** — Werner φ-bound CDL remains SIM-gated
- **Do not schedule SIM-SPECTRAL-02** — data dependency satisfied but window is full
- **Do not authorize SIM-ECU-STABILITY-01** — candidate status unchanged
- **Do not touch the PROVENANCE settlement algorithm** — only the constant changes,
  not the chain traversal, depth truncation, or visited-creator logic
- **Do not change PROVENANCE_MAX_DEPTH** — remains 3
- **Do not change REUSE_ATTRIBUTION_RATE** — remains Decimal("0.20")
- **Do not add new attribution event types** — ATTESTATION/EPOCH_BOUNDARY remain stubs
- **Do not commission Conley Index review** — deferred pre-RC1.0
- **Do not advance star expansion, ADR-0035, or SIM-HYPEREDGE-01** — deferred
- **Do not run naked full-suite pytest** — conftest.py historical gate selftest-variable
  injection workaround not in place

---

## 12. Key Canonical Anchors for Prompt Drafting

Codex must read the following before writing any phase prompt in this window:

- **`docs/specs/ilc_antigravity_context_capsule_v5.36.md`** (PRIMARY — current capsule)
- **`docs/specs/ilc_window_1118_1123_handoff_1123_v0.1.md`** (incoming obligations)
- **`docs/sims/sim_provenance_01/alpha_disposition_phase_1121.md`** (SIM evidence for Q2)
- **`docs/specs/ilc_cdl_084_provenance_chain_attribution_opening_1111_v0.1.md`** (amendment target)
- **`ilc_core/types.py`** (runtime target; confirm current value before writing 1126 prompt)
- **`ilc_core/economics/epoch_attribution_settle_runtime.py`** (version bump target)
- **`docs/specs/ilc_constitutional_decision_log_v0.1.md`** (CDL log)
- **`docs/phases/STATUS.md`** (phase completion record)
- **`docs/specs/ilc_phase_1118_1123_sequence_lock_v0.1.md`** (format reference for new seq lock)

For Phase 1125 (prelock): also run grep for `Decimal("0.5")`, `Decimal("0.10")`,
`Decimal("0.05")`, `Decimal("0.025")` in `tests/` before writing the phase prompt.

For Phase 1126 (ratification): also read Phase 1125 prelock doc after it is committed.

For Phase 1129 (closure gate): all Phase 1124–1128 test files and artifacts.

---

## 13. Rationale for Six-Phase Scope

1. **The amendment is small but requires two SENSITIVE phases.** A seq lock + prelock +
   SENSITIVE ratification + evidence tests + coherence + SENSITIVE gate is the minimum
   responsible structure for a CDL mutation, even a parameter-only one.

2. **The prelock is mandatory, not optional.** The phantom edit risk (hardcoded
   `Decimal("0.5")` in tests) must be surveyed before Phase 1126 executes — not discovered
   mid-execution. Phase 1125 eliminates that risk.

3. **SIM-SPECTRAL-02 is intentionally excluded.** The time-series data is ready, but
   adding a SIM commissioning phase to this window would compromise the focused amendment
   character. SIM-SPECTRAL-02 gets its own clean window start after the CDL-084 lane fully
   closes.

4. **No carry-forward from this window is expected.** After Phase 1129 closes, the CDL-084
   Q2 obligation will be fully discharged. The next window enters with a clean slate and
   can be scoped to SIM-SPECTRAL-02, SIM-ECU-STABILITY-01 authorization, or the next
   constitutional priority, whichever the human lead designates.

**Status:** CLOSED — Phase 1129 closure gate passed. `window_1124_1129_closed_phase_1129`
