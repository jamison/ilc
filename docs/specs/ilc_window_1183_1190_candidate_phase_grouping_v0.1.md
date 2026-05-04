# ILC Window 1183-1190: Candidate Phase Grouping

**Author:** Claude Sonnet 4.6 (local architectural reviewer)
**Date:** 2026-05-04
**Baseline:** Window 1176-1182 CLOSED (Phase 1182 verdict: PASS, commit `b3f2abeb`).
CDL-085 open and prelocked (`cdl_085_prelock_committed_phase_1177`); candidate
`EDGE_MINT_PHI_BOUND = Decimal("0.60")` documented in `docs/specs/` but not yet active in
`ilc_core/`. Runtime-binding slice passed (`sim_spectral_05_runtime_binding_slice_pass`).
Economic-flow slice passed (`sim_spectral_05_economic_flow_slice_pass`). Both activation
gates for `EDGE_MINT_PHI_BOUND` are cleared. Capsule v5.43 current. Handoff:
`docs/specs/ilc_window_1176_1182_handoff_1182_v0.1.md`.
**Planning note:** This is a candidate grouping, not a locked sequence. Phases 1183–1185
are the hard minimum lane (sequence lock + prelock hardening + CDL-085 ratification).
Phase 1186 is a conditional signing slot. Phases 1187–1188 are conditional tail slots.
Phases 1189–1190 are firm coherence + closure phases.

---

## 1. Window Identity and Scope

Window 1183-1190 has one primary constitutional obligation and two conditional tracks:

1. **CDL-085 ratification lane (obligated)** — All prerequisites are satisfied:
   prelock committed, both activation-gate SIM slices passed, Q1–Q5 fully resolved.
   Phase 1184 hardens the prelock test (historical read at `509b6c6f`). Phase 1185
   ratifies CDL-085 via the two-commit pattern: CDL amendment commit first, then
   runtime constant activation commit. The runtime mutation activates
   `EDGE_MINT_PHI_BOUND = Decimal("0.60")` in `ilc_core/types.py` and adds a
   `CDL_085_DEPENDENCY` token to `ilc_core/economics/epoch_attribution_settle_runtime.py`.

2. **v0.2 signing ceremony lane (conditional on explicit signing authorization)** —
   Unchanged from Window 1176-1182: requires explicit human token
   `v0_2_signing_ceremony_authorized_phase_1186`. Carries the same skip path with
   `v0_2_signing_ceremony_deferred_pending_signing_authorization` if not issued.

3. **SIM-SPECTRAL-05 gossip slice + CDL-001 scoping (conditional tail)** — Phase 1187
   addresses the last deferred SIM-SPECTRAL-05 observer slice. Phase 1188 opens the
   CDL-001 (genesis_blocker / packaging track) scope deliberation — required for any
   public launch claim. Both are conditional on window capacity.

**Key constitutional milestone:** CDL-085 ratification in Phase 1185 completes the first
RC2 gate (`CDL-085 ratified`). This is the most significant constitutional advance since
CDL-084 ratification (Phase 1113).

**Tail-slot policy:** Phases 1186, 1187, and 1188 are conditional. The window closes at
Phase 1190 regardless.

---

## 2. Baseline and Inheritance

### Ratified CDL chain

- `CDL_084_DEPENDENCY = "cdl_084_provenance_chain_attribution_ratified_1113.v0.1"`
- `PROVENANCE_DECAY_ALPHA = Decimal("0.45")`
- `PROVENANCE_MAX_DEPTH = 3`
- CDL-085: **OPEN + PRELOCKED**. Candidate `EDGE_MINT_PHI_BOUND = Decimal("0.60")`.
  Ratification is the primary obligation of this window.
- Next fresh CDL number: **CDL-086** (CDL-085 ratification does not open CDL-086)

### Active runtime chain

- `epoch_attribution_settle_runtime_1129_fix1.v0.5` — **will be superseded by Phase 1185**
  runtime mutation commit. New version token TBD at Phase 1185 execution.
- `ilc_core/types.py:80` — `EDGE_MINT_PHI_BOUND: Optional[float] = None` — **placeholder**;
  Phase 1185 changes this to `EDGE_MINT_PHI_BOUND: Decimal = Decimal("0.60")`
- The float type must be corrected to `Decimal` (float is banned for ECU/attribution
  values per ILC coding standards §3)

### Genesis Atlas canonical anchors

- Signed v0.1: `out/genesis_core_star_map_v0.1.json` (32 nodes, 55 edges) — **immutable**
- Root envelope hash: `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`
- **Strictly immutable:** `out/genesis_compile_coverage_diagnostic_v0.1.json`
  SHA: `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56`
  ⚠ This file was silently regenerated TWICE in Window 1176-1182 by the SIM toolchain.
  Check and restore before Phase 1190 closure gate: `git restore out/genesis_compile_coverage_diagnostic_v0.1.json`
- Unsigned v0.2 candidate: `out/genesis_core_star_map_v0.2_candidate.json` (41 nodes,
  73 edges) — signing conditional on Phase 1186 authorization

### CDL-085 prelock baseline

- Prelock doc: `docs/specs/ilc_cdl_085_prelock_spec_1177_v0.1.md`
- Prelock commit: `509b6c6f` (Phase 1177)
- Token: `cdl_085_prelock_committed_phase_1177`
- Resolved Q1–Q5 with candidate `EDGE_MINT_PHI_BOUND = Decimal("0.60")`

### SIM-SPECTRAL-05 observer slice baseline

- Runtime-binding: `sim_spectral_05_runtime_binding_slice_pass` (Phase 1179, `2d50ccde`)
- Economic-flow: `sim_spectral_05_economic_flow_slice_pass` (Phase 1180, `0bef44db`)
- Gossip: `sim_spectral_05_gossip_slice_deferred_window_1176` — deferred to this window

---

## 3. Track Inventory

### Constitutionally obligated

- `cdl_085_prelock_committed_phase_1177` → ratification required this window
- Both activation gates cleared → `EDGE_MINT_PHI_BOUND` may be activated at ratification
- `sim_spectral_05_gossip_slice_deferred_window_1176` — final deferred SIM slice

### Deferred governance (not this window)

- Tier-3 runtime linkage (`schema:*` / `runtime:*`) — Window 1191+
- CDL-001 scoped this window (Phase 1188 conditional); CDL opening Window 1191+
- Truth-primitive permanence community ratification — pre-public-RC
- Canon bundle + naming-convention test repair — tooling debt
- Multi-hop centrality attribution CDL — post CDL-085
- Cross-epoch compaction CDL — pre-network-scale

### Simulation-conditional

- `sim_spectral_05_gossip_slice_deferred_window_1176` — Phase 1187 conditional tail
- SIM-MONETARY-01 — long-range; prerequisite for CDL-070 PQ migration ceremony

---

## 4. CDL-085 Ratification Lane

### Prelock hardening (Phase 1184)

The prelock hardening phase adds tests that read CDL-085 state at the Phase 1172 opening
commit and the Phase 1177 prelock commit — both historical, not live. This prevents the
recurring forward-progress test failure (Phase 1165 class: tests asserting live-file state
that becomes invalid after correct forward progress).

Phase 1184 produces a **test-only commit** — no doc mutations, no runtime mutations. It
adds two historical-hardening assertions to `tests/test_phase_1177_cdl_085_prelock.py`
(via amendment or a new companion test file):
- CDL-085 opening doc shows `OPEN` at `ee0f6b48` (Phase 1172 commit)
- CDL-085 prelock doc shows `cdl_085_prelock_committed_phase_1177` at `509b6c6f` (Phase
  1177 commit) — not just live read

This phase is separate from Phase 1185 to keep the ratification commit clean.

### Ratification (Phase 1185) — two-commit pattern

**Commit 1 — CDL amendment (SENSITIVE, requires pre-commit hook):**

Files mutated:
1. `docs/specs/ilc_constitutional_decision_log_v0.1.md` — CDL-085 row: `OPEN` → `RATIFIED`;
   add ratification phase, date, `EDGE_MINT_PHI_BOUND` value, dependency token
2. `docs/specs/ilc_cdl_085_ratification_evidence_1185_v0.1.md` — ratification evidence doc
3. `tests/test_phase_1185_cdl_085_ratification.py` — CDL/documentation tests only;
   runtime import/value tests are added in Commit 2 after `ilc_core/` activation

Pre-commit hook required:
```
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1185
```

**Commit 2 — Runtime constant activation (standard commit, no special hook):**

Files mutated:
4. `ilc_core/types.py` — change `EDGE_MINT_PHI_BOUND: Optional[float] = None` to
   `EDGE_MINT_PHI_BOUND: Decimal = Decimal("0.60")`; update comment to reference CDL-085
5. `ilc_core/economics/epoch_attribution_settle_runtime.py` — add import of
   `EDGE_MINT_PHI_BOUND` from `ilc_core.types`; add
   `CDL_085_DEPENDENCY = "cdl_085_werner_phi_bound_ratified_1185.v0.1"`; bump
   `EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION` to `"epoch_attribution_settle_runtime_1185.v0.6"`

**Important — float ban:** `ilc_core/types.py:80` currently declares
`EDGE_MINT_PHI_BOUND: Optional[float] = None`. The runtime mutation must change the type
to `Decimal`, not just set the value. Using `float` for an attribution bound violates the
ILC coding standard §3 (float banned for ECU/balance/reward/attribution values).

### Ratification evidence doc required content

File: `docs/specs/ilc_cdl_085_ratification_evidence_1185_v0.1.md`

Must include:
1. CDL-085 prelock reference and token (`cdl_085_prelock_committed_phase_1177`)
2. Both SIM observer slice pass tokens (runtime-binding + economic-flow)
3. Q1–Q5 resolutions summary (from prelock spec)
4. Exact `EDGE_MINT_PHI_BOUND` value being ratified: `Decimal("0.60")`
5. Runtime mutation scope: `ilc_core/types.py` + `epoch_attribution_settle_runtime.py`
6. Activation gate clearance statement (both slices passed → full activation authorized)
7. Ratification token: `cdl_085_ratified_phase_1185`
8. Dependency token: `CDL_085_DEPENDENCY = "cdl_085_werner_phi_bound_ratified_1185.v0.1"`

### Tests (minimum 7)

The Phase 1185 test file is intentionally built in two steps. Commit 1 must not import
`EDGE_MINT_PHI_BOUND`, because the CDL mutation commit precedes the runtime activation
commit. Commit 1 tests are CDL/documentation-only. Commit 2 adds runtime import/value
assertions after `ilc_core/` has been mutated.

```python
# Commit 1 / CDL-only test 1: CDL-085 ratified in CDL register
def test_cdl_085_ratified_in_register():
    content = open("docs/specs/ilc_constitutional_decision_log_v0.1.md").read()
    assert "cdl_085_ratified_phase_1185" in content

# Commit 1 / CDL-only test 2: Ratification evidence doc exists
def test_ratification_evidence_exists():
    assert os.path.exists("docs/specs/ilc_cdl_085_ratification_evidence_1185_v0.1.md")

# Commit 1 / CDL-only test 3: Ratification evidence carries the token/value
def test_ratification_evidence_token_and_value():
    content = open("docs/specs/ilc_cdl_085_ratification_evidence_1185_v0.1.md").read()
    assert "cdl_085_ratified_phase_1185" in content
    assert 'EDGE_MINT_PHI_BOUND = Decimal("0.60")' in content

# Commit 2 / runtime test 4: EDGE_MINT_PHI_BOUND is Decimal in types.py (not float/None)
def test_phi_bound_is_decimal():
    from ilc_core.types import EDGE_MINT_PHI_BOUND
    from decimal import Decimal
    assert isinstance(EDGE_MINT_PHI_BOUND, Decimal)
    assert EDGE_MINT_PHI_BOUND == Decimal("0.60")

# Commit 2 / runtime test 5: CDL_085_DEPENDENCY token in runtime module
def test_cdl_085_dependency_token():
    import ilc_core.economics.epoch_attribution_settle_runtime as rt
    assert rt.CDL_085_DEPENDENCY == "cdl_085_werner_phi_bound_ratified_1185.v0.1"

# Commit 2 / historical test 6: CDL-085 prelock shows correct state at Phase 1177 commit
def test_cdl_085_prelock_historical():
    result = subprocess.run(
        ["git", "show", "509b6c6f:docs/specs/ilc_cdl_085_prelock_spec_1177_v0.1.md"],
        capture_output=True, text=True
    )
    assert "cdl_085_prelock_committed_phase_1177" in result.stdout

# Commit 2 / historical test 7: CDL-085 opening doc shows OPEN at Phase 1172 commit
def test_cdl_085_opening_historical():
    result = subprocess.run(
        ["git", "show", "ee0f6b48:docs/specs/ilc_cdl_085_werner_phi_bound_opening_1172_v0.1.md"],
        capture_output=True, text=True
    )
    assert "cdl_085_open_phase_1172" in result.stdout

# Commit 2 / runtime test 8: Runtime version token updated
def test_runtime_version_updated():
    import ilc_core.economics.epoch_attribution_settle_runtime as rt
    assert "1185" in rt.EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION
```

**Pre-commit split:** Commit 1 runs tests 1-3 under the CDL-mutation env. Commit 2 runs
the full test file after runtime mutation is applied. Runtime tests must not be required
to pass before Commit 2.

---

## 5. v0.2 Signing Ceremony Lane

Unchanged from Window 1176-1182 guidance §5. Same authorization requirements, same
ADR-0036 §4 procedure, same version equivalence check (ADR-0037 §3.3). Phase 1186 is
the slot; skip path carries `v0_2_signing_ceremony_deferred_pending_signing_authorization`.

One addition: Phase 1185 (CDL-085 ratification) does not block signing. They remain
independent tracks.

---

## 6. SIM-SPECTRAL-05 Gossip Observer Slice

**Phase 1187 scope:**

Convergence question: Does φ-bound gating on provenance-equivalent paths propagate
correctly through the gossip transport layer — specifically, do gossip-relayed provenance
claims from Sybil-topology paths get correctly suppressed while gossip-relayed claims
from legitimate-topology paths pass through?

Design:
- Test A: gossip relay of S1 legitimate path claims → should arrive at receiving node
  with convergence ≥ 0.60, accepted under φ-bound
- Test B: gossip relay of S3 Sybil path claims → should arrive with convergence < 0.60,
  rejected under φ-bound
- Test C: mixed gossip batch — verify no cross-contamination (Sybil path in same gossip
  batch does not suppress legitimate path claims)

Pass condition produces: `sim_spectral_05_gossip_slice_pass` and
`sim_spectral_05_gossip_slice_deferred_window_1176_resolved`.

This completes the three-slice SIM-SPECTRAL-05 observer framework.

---

## 7. CDL-001 Genesis Blocker Scoping

**Phase 1188 scope:**

CDL-001 (genesis_blocker) is required before any public launch claim (Gap 5 in launch
roadmap v0.9 §3). This phase does **not** open CDL-001 — it produces a scoping document
that defines:
1. What CDL-001 must cover (packaging track governance, release criteria, public launch
   gate conditions)
2. Whether CDL-001 is a single CDL or a bundle
3. The deliberation questions that must be resolved before opening
4. Estimated sequencing relative to RC2 (is it on the critical path?)

Output: `docs/specs/ilc_cdl_001_genesis_blocker_scoping_1188_v0.1.md`
Token: `cdl_001_genesis_blocker_scoping_committed_phase_1188`

This is NON-SENSITIVE — no CDL mutation.

---

## 8. CDL Number Assignments

| CDL | Title | Decision digest anchor | Opening phase | Ratification phase |
|-----|-------|----------------------|---------------|--------------------|
| CDL-085 | Werner φ-bound Provenance Equivalence Limit | `EDGE_MINT_PHI_BOUND = Decimal("0.60")`; bound: provenance-equivalent paths; combined rule; Werner interpretation | Already open (Phase 1172) | **Phase 1185 — this window** |

**Note:** No new CDL is opened in this window. CDL-086 remains the next available number.
CDL-001 scoping (Phase 1188) is a planning-only phase — CDL-001 opening is Window 1191+.

---

## 9. Candidate Phase Table

| Order | Phase | Topic | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 1183 | Window sequence lock | Foundation / Constitutional | **SENSITIVE** |
| 2 | 1184 | CDL-085 prelock hardening (historical-read test updates) | Constitutional | `constitutional` |
| 3 | 1185 | CDL-085 ratification: CDL amendment + runtime activation | Constitutional / Runtime | **SENSITIVE** |
| 4 | 1186 | v0.2 signing ceremony (ADR-0036 §4 + release envelope) | Constitutional | **conditional** |
| 5 | 1187 | SIM-SPECTRAL-05 gossip observer slice | Simulation | `NON-SENSITIVE` |
| 6 | 1188 | CDL-001 genesis_blocker scoping doc | Governance review | `NON-SENSITIVE` |
| 7 | 1189 | Coherence report + capsule v5.44 | Synthesis | `NON-SENSITIVE` |
| 8 | 1190 | Window 1183-1190 closure gate | Gate | **SENSITIVE** |

### Conditional note on Phase 1186

**Scenario A (signing authorized):** Human issues `v0_2_signing_ceremony_authorized_phase_1186`.
Phase 1186 is SENSITIVE — requires GO token `GO Phase 1186` after authorization token.

**Scenario B (signing not authorized):** Phase 1186 skipped with token
`v0_2_signing_ceremony_deferred_pending_signing_authorization`. Window proceeds to Phase 1187.

### Conditional note on Phases 1187–1188

Both are independent conditional tail slots. Either or both may be deferred:
- Phase 1187 deferred: emit `sim_spectral_05_gossip_slice_deferred_window_1183`
- Phase 1188 deferred: emit `cdl_001_genesis_blocker_scoping_deferred_window_1183`
Phase 1189 must run regardless.

### Note on Phase 1185 two-commit runtime mutation pattern

Phase 1185 uses the established two-commit pattern from CDL-084 ratification:
- Commit 1 (CDL mutation only): CDL register + evidence doc + tests. Env:
  `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1185`
- Commit 2 (runtime only): `ilc_core/types.py` + `epoch_attribution_settle_runtime.py`.
  Standard commit, no special env.

The pre-commit hook enforces separation: a commit touching both CDL docs and `ilc_core/`
will be rejected. Do not attempt to combine into one commit.

---

## 10. Sensitivity Classification

### SENSITIVE phases

- **Phase 1183** (sequence lock) — structural window-boundary commit. Requires `GO Phase 1183`.
- **Phase 1185** (CDL-085 ratification) — CDL mutation (Commit 1) and runtime mutation
  (Commit 2). Requires `GO Phase 1185` before either commit. CDL mutation commit requires
  pre-commit hook: `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1185`.
- **Phase 1186** (v0.2 signing, if authorized) — Genesis Atlas constitutional-boundary
  action. Requires signing authorization token AND `GO Phase 1186`.
- **Phase 1190** (closure gate) — structural window boundary. Requires `GO Phase 1190`.

### NON-SENSITIVE phases

- **Phase 1184** (prelock hardening) — test-only commit, no CDL or runtime mutation.
- **Phase 1187** (gossip SIM) — simulation only.
- **Phase 1188** (CDL-001 scoping) — planning doc only, no CDL mutation.
- **Phase 1189** (coherence + capsule) — synthesis only.

### Conditional phases rule

**Phase 1186:** Before executing, confirm signing authorization token. If issued: SENSITIVE,
require `GO Phase 1186`. If not: skip NON-SENSITIVELY with carry-forward token.

### Pre-commit hook block

Phase 1185 Commit 1 requires:
```
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1185
```
No other phase in this window requires the CDL mutation hook.

---

## 11. Scope Notes for Fixed Phases

### Phase 1183 — Window Sequence Lock

**SENSITIVE.** Requires `GO Phase 1183`.

**Deliverables:**

| Artifact | Notes |
|----------|-------|
| `docs/specs/ilc_phase_1183_1190_sequence_lock_v0.1.md` | Window sequence lock |
| `tests/test_phase_1183_sequence_lock.py` | Minimum 2 tests |
| `docs/phases/phase_1183_window_sequence_lock_walkthrough.md` | Walkthrough |
| Updated `docs/PLANNING_INDEX.md §0` | Window guidance row; Last updated |
| Updated `docs/phases/STATUS.md` | Phase 1183 entry |

**Required content:** Window 1183-1190 identity; baseline (Window 1176-1182 closed,
`b3f2abeb`); phase table; carry-forward tokens (CDL-085 prelock, gossip slice, v0.2
signing deferred, CDL-001 not yet scoped); explicit: CDL-085 ratification authorized
this window; `EDGE_MINT_PHI_BOUND` activation authorized (both SIM gates cleared).

**Sequence lock token:** `window_1183_1190_sequence_lock_committed`

**Commit subject:** `feat(g8): phase 1183 window 1183-1190 sequence lock`

---

### Phase 1184 — CDL-085 Prelock Hardening

**NON-SENSITIVE** (constitutional class). No CDL mutation, no runtime mutation.

**Deliverables:**

| Artifact | Notes |
|----------|-------|
| `tests/test_phase_1184_cdl_085_prelock_hardening.py` | 3 hardening tests |
| `docs/phases/phase_1184_cdl_085_prelock_hardening_walkthrough.md` | Walkthrough |
| Updated `docs/phases/STATUS.md` | Phase 1184 entry |

**Hardening tests (3):**
1. CDL-085 opening doc at `ee0f6b48`: assert `cdl_085_open_phase_1172` present
2. CDL-085 prelock doc at `509b6c6f`: assert `cdl_085_prelock_committed_phase_1177` present
3. No `EDGE_MINT_PHI_BOUND` assigned (non-None) in `ilc_core/types.py` yet — this test
   must pass before Phase 1185 Commit 1; it fails after Commit 2 and should be
   marked `xfail` or removed after ratification

**Commit subject:** `test(cdl): phase 1184 cdl-085 prelock hardening tests`

---

### Phase 1185 — CDL-085 Ratification

**SENSITIVE.** Requires `GO Phase 1185`.

**Deliverables — Commit 1 (CDL mutation):**

| Artifact | Notes |
|----------|-------|
| `docs/specs/ilc_constitutional_decision_log_v0.1.md` | CDL-085 row: OPEN → RATIFIED |
| `docs/specs/ilc_cdl_085_ratification_evidence_1185_v0.1.md` | Ratification evidence doc |
| `tests/test_phase_1185_cdl_085_ratification.py` | Tests 1–3 (CDL-only assertions) |

**Deliverables — Commit 2 (runtime activation):**

| Artifact | Notes |
|----------|-------|
| `ilc_core/types.py` | `EDGE_MINT_PHI_BOUND`: `Optional[float] = None` → `Decimal = Decimal("0.60")` |
| `ilc_core/economics/epoch_attribution_settle_runtime.py` | Import `EDGE_MINT_PHI_BOUND`; add `CDL_085_DEPENDENCY`; bump version to `v0.6` |
| `docs/phases/phase_1185_cdl_085_ratification_walkthrough.md` | Walkthrough (update after both commits) |
| Updated `docs/phases/STATUS.md` | Phase 1185 entry |

**Phantom edit guard:** Before Commit 2, verify `ilc_core/types.py` was not already
modified by a prior tool run: `grep "EDGE_MINT_PHI_BOUND" ilc_core/types.py` should show
`Optional[float] = None` (the placeholder). If it shows `Decimal("0.60")` already, a
phantom edit occurred — check `git diff ilc_core/types.py` and restore if unauthorized.

**Pre-commit hook (Commit 1 only):**
```
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1185
```

**Commit 1 subject:** `feat(cdl): CDL-085 Werner φ-bound ratified — EDGE_MINT_PHI_BOUND locked`
**Commit 2 subject:** `feat(runtime): phase 1185 activate EDGE_MINT_PHI_BOUND in ilc_core`

**Ratification token:** `cdl_085_ratified_phase_1185`
**Runtime dependency token:** `CDL_085_DEPENDENCY = "cdl_085_werner_phi_bound_ratified_1185.v0.1"`
**Runtime version:** `EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION = "epoch_attribution_settle_runtime_1185.v0.6"`

---

### Phase 1189 — Coherence Report + Capsule v5.44

**NON-SENSITIVE.**

**Deliverables:**

| Artifact | Notes |
|----------|-------|
| `docs/specs/ilc_integration_coherence_report_1189_v0.1.md` | Coherence report |
| `docs/specs/ilc_antigravity_context_capsule_v5.44.md` | Capsule (supersedes v5.43) |
| `docs/phases/phase_1189_coherence_capsule_v5_44_walkthrough.md` | Walkthrough |
| Updated `docs/phases/STATUS.md` | Phase 1189 entry |
| Updated `docs/PLANNING_INDEX.md §0` | Capsule row → v5.44; Last updated |

**Key capsule state delta from v5.43:**
- CDL-085: `OPEN + PRELOCKED` → `RATIFIED`; `EDGE_MINT_PHI_BOUND = Decimal("0.60")` active
- RC2 gate 1 (CDL-085 ratified): ✓ SATISFIED
- v0.2 signing outcome: record actual (signed or deferred with token)
- Gossip slice outcome: record actual (pass/deferred)
- CDL-001 scoping outcome: record actual
- Runtime: `epoch_attribution_settle_runtime_1185.v0.6`

**Capsule token:** `capsule_v5_44_supersedes_v5_43`

**Commit subject:** `feat(capsule): phase 1189 coherence report + capsule v5.44`

---

### Phase 1190 — Closure Gate

**SENSITIVE.** Requires `GO Phase 1190`.

**Closure gate checks (minimum 16):**

| # | Check | Gate |
|---|-------|------|
| 1 | Sequence lock doc exists + `window_1183_1190_sequence_lock_committed` token | Seq lock |
| 2 | CDL-085 prelock hardening tests exist | Prelock hardening |
| 3 | CDL-085 ratification evidence doc exists | Ratification |
| 4 | `cdl_085_ratified_phase_1185` in CDL register | Ratification |
| 5 | `EDGE_MINT_PHI_BOUND == Decimal("0.60")` in `ilc_core/types.py` (isinstance Decimal) | Runtime activation |
| 6 | `CDL_085_DEPENDENCY` token in `epoch_attribution_settle_runtime.py` | Runtime activation |
| 7 | `EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION` contains `1185` | Runtime version |
| 8 | Phase 1186 signed v0.2 OR `v0_2_signing_ceremony_deferred_pending_signing_authorization` | Signing routing |
| 9 | Phase 1187 gossip slice pass OR `sim_spectral_05_gossip_slice_deferred_window_1183` | SIM routing |
| 10 | Phase 1188 CDL-001 scoping doc OR `cdl_001_genesis_blocker_scoping_deferred_window_1183` | CDL-001 routing |
| 11 | Coherence report 1189 exists | Synthesis |
| 12 | Capsule v5.44 exists + `capsule_v5_44_supersedes_v5_43` | Capsule |
| 13 | Signed Genesis v0.1 hash unchanged: `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c` | Immutability |
| 14 | `out/genesis_compile_coverage_diagnostic_v0.1.json` not regenerated (SHA `5a67a919...`) | Immutability |
| 15 | `PROVENANCE_DECAY_ALPHA` unchanged (`Decimal("0.45")`) | Runtime stability |
| 16 | `PROVENANCE_MAX_DEPTH` unchanged (3) | Runtime stability |

**Selftest guard:** `ILC_PHASE_1190_GATE_SELFTEST=1`. Use `pytest.skip(msg)` form (not
`assert SELFTEST_MODE is True`). Read `tests/test_phase_1182_window_1176_1182_closure_gate.py`
directly before writing this test — match its category structure and import pattern.

**Closure tokens:**
`window_1183_1190_closed_phase_1190`
`window_1183_1190_closure_gate_verdict=pass`

**Handoff doc:** `docs/specs/ilc_window_1183_1190_handoff_1190_v0.1.md`

**Commit subject:** `docs(phase): close window 1183-1190`

---

## 12. Key Dependencies and Open Questions

### Must-resolve at window entry

- None blocking Phases 1183–1185. CDL-085 ratification may proceed immediately after
  sequence lock.
- Phase 1186 (signing): confirm whether signing authorization will be issued.

### Sequencing constraints

- Phase 1184 (hardening) must precede Phase 1185 (ratification).
- Phase 1185 Commit 1 (CDL) must precede Commit 2 (runtime) — pre-commit hook enforces.
- Phase 1185 (ratification) must complete before Phase 1189 (coherence captures the state).
- Phase 1190 (closure) is last.
- Phases 1186, 1187, 1188 are independent of each other; all must precede Phase 1189.

### Open questions (need human input at window entry)

1. **Signing authorization:** Will `v0_2_signing_ceremony_authorized_phase_1186` be
   issued? This determines whether Phase 1186 is firm or skipped.

2. **Gossip slice priority:** Should Phase 1187 (gossip SIM) run before CDL-001 scoping
   (Phase 1188), or is CDL-001 scoping higher priority? Recommendation: gossip slice
   first (closes the three-slice set); CDL-001 scoping second.

### Permanently deferred (not open questions)

- CDL-085 **opening** — already open; ratification is the action this window
- Tier-3 runtime linkage — Window 1191+
- L4 privacy — post-RC3
- CDL-070 PQ ceremony — after SIM-MONETARY-01

---

## 13. Known Patterns and Technical Constraints

### Novel patterns this window

1. **First CDL ratification that activates a pre-placed runtime placeholder** —
   `ilc_core/types.py:80` already has `EDGE_MINT_PHI_BOUND: Optional[float] = None`.
   The runtime mutation changes the type AND value. This is different from prior
   ratifications that added a new constant to a new file. The phantom edit guard is
   especially important here: verify the placeholder still reads `None` before Commit 2.

2. **Float-to-Decimal type correction at ratification** — The placeholder uses
   `Optional[float]`. Per ILC coding standards §3, attribution bounds must be `Decimal`.
   The type correction (`Optional[float] = None` → `Decimal = Decimal("0.60")`) is part
   of the ratification activation, not a separate fix.

3. **RC2 gate 1 closure** — CDL-085 ratification satisfies the first RC2 gate. The
   ratification evidence doc and capsule v5.44 should explicitly record this milestone.

### Historical prelock hardening

Two commit refs to use in historical-hardening assertions:
- CDL-085 opening: `ee0f6b48` (Phase 1172 — Window 1166-1175 closure commit)
- CDL-085 prelock: `509b6c6f` (Phase 1177)

Both must be read via `git show <ref>:<path>` in tests — never live file reads.

### Phantom edit guard — `ilc_core/types.py`

This file is the runtime mutation target for Phase 1185. Before Commit 2, check:
```bash
grep "EDGE_MINT_PHI_BOUND" ilc_core/types.py
# Expected: Optional[float] = None
# If Decimal("0.60") already present: phantom edit — git restore ilc_core/types.py
```

Detection command: `git diff ilc_core/types.py`
Fix command: `git restore ilc_core/types.py`

### Recurring immutability hazard

`out/genesis_compile_coverage_diagnostic_v0.1.json` was regenerated by the SIM toolchain
twice in Window 1176-1182 (before Phase 1175 and before Phase 1182). The same risk
applies to Phase 1187 (gossip SIM). Check before Phase 1190 closure gate:
```bash
shasum -a 256 out/genesis_compile_coverage_diagnostic_v0.1.json
# Must equal: 5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56
# Fix if wrong: git restore out/genesis_compile_coverage_diagnostic_v0.1.json
```

### Pre-commit hook clean-state guard

Phase 1185 is the only phase requiring `ILC_CDL_MUTATION_AUTHORIZED=1`. The two-commit
split is enforced by the pre-commit hook. If Commit 1 is attempted with `ilc_core/`
files staged, the hook will reject it. Stage only CDL docs, evidence doc, and tests for
Commit 1.

### Closure gate selftest guard chain

Read `tests/test_phase_1182_window_1176_1182_closure_gate.py` directly before writing
Phase 1190 gate. Do not reason from analogy. The `pytest.skip()` selftest guard form
(not `assert`) is critical — see Phase 1165 fix `b9c6d1b4`.

---

## 14. Non-Goals and Explicitly Deferred Items

- CDL-086 or any new CDL opening — not this window
- Tier-3 runtime linkage — Window 1191+
- CDL-001 **opening** — Phase 1188 scopes it; CDL opening is Window 1191+
- Persistent rate limiter — RC2 carry-forward
- Truth-primitive permanence community ratification — pre-public-RC
- SIM-SPECTRAL-05 additional tracks — all three slices addressed after Phase 1187
- L4 privacy (onion routing / SURB) — post-RC3
- CDL-070 PQ migration ceremony — after SIM-MONETARY-01
- Canon bundle + naming-convention test repair (200 pre-existing failures) — tooling debt

---

## 15. Key Canonical Anchors for Prompt Drafting

- `docs/specs/ilc_antigravity_context_capsule_v5.43.md` **(PRIMARY — Codex rehydration)**
- `docs/specs/ilc_window_1176_1182_handoff_1182_v0.1.md` — prior window closure handoff
- `docs/specs/ilc_phase_1176_1182_sequence_lock_v0.1.md` — format reference for new
  sequence lock
- `docs/specs/ilc_constitutional_decision_log_v0.1.md` — CDL register (CDL-085 entry)
- `docs/phases/STATUS.md` — phase completion log
- `docs/specs/ilc_cdl_085_prelock_spec_1177_v0.1.md` — prelock spec (Q1–Q5 resolutions;
  candidate value `Decimal("0.60")`)
- `docs/specs/ilc_cdl_085_ratification_evidence_1185_v0.1.md` — (to be produced at Phase 1185)
- `ilc_core/types.py` — contains `EDGE_MINT_PHI_BOUND` placeholder (line ~80)
- `ilc_core/economics/epoch_attribution_settle_runtime.py` — runtime module receiving
  `CDL_085_DEPENDENCY` and version bump
- `docs/sims/sim_spectral_05/disposition_1171_v0.1.md` — original SIM evidence (Track B
  separation 0.60)
- `docs/adr/ADR_0037_Genesis_Canonical_Lineage_Contract.md` §3.2, §3.3 — provenance
  equivalence and version equivalence criteria
- `docs/adr/ADR_0036_Operational_Release_Key_Genesis_Binding.md` §4, §5 — for Phase 1186
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.9.md` §6 — RC2 gate
  status (gate 1 satisfied by this window)
- `docs/PLANNING_INDEX.md §0` — update at end of each phase
- For Phase 1190 closure gate: all Phase 1183–1189 test files and artifacts.
