# ILC Window 1102–1109: Candidate Phase Grouping

**Author:** Claude Sonnet 4.6 (local architectural reviewer)
**Date:** 2026-04-28
**Baseline:** Window 945–950, 1100–1101 CLOSED (Phase 1101 verdict pending). CDL-082 ratified
(Phase 950). H-012 partial settle() implemented (Phase 946, CDL_HCON_02_DEPENDENCY stub active).
Capsule v5.33.
**Planning note:** This is a candidate grouping, not a locked sequence. Phases 1102–1107 are the
hard minimum lane (seq lock + CDL-083 lifecycle + runtime). Phases 1108–1109 are synthesis and
gate (tail slots).

---

## 1. Window Identity and Scope

**Window 1102–1109: H-CON-02 — Panel Quorum Rules for Ejected Stake Treasury Distribution**

This window constitutionalises the panel quorum rules governing ejected-stake treasury
distribution (CDL-083) and implements the corresponding H-CON-02 runtime. The primary
obligation is clearing the `CDL_HCON_02_DEPENDENCY` stub active in
`ilc_core/economics/epoch_attribution_settle_runtime.py` since Phase 946.

CDL-083 has two sub-scopes that must be decided at opening:

1. **Ejected stake treasury distribution** — CDL-081 §4.5 puts ejected member stake into the
   treasury. H-CON-02 defines the panel quorum rules for distribution: who governs, quorum
   floor, vote threshold, distribution formula.

2. **REFUTATION edge attribution** — CDL-081 Q1 deferred REFUTATION edges to H-CON-02.
   When CDL-V7 Popperian gate upholds a refutation, ECU must flow somewhere. H-CON-02 defines
   the source, target, and amount.

A third scope — **PROVENANCE chain attribution** (depth cap + α-decay) — is explicitly deferred
to Window 1110+ as a separate CDL (CDL-084). PROVENANCE events are currently silently ignored
in `settle()` (§4.3 catch-all). This window does NOT scope PROVENANCE.

**Tail-slot policy:** PROVENANCE (CDL-084) may be added to this window's tail if CDL-083
ratification completes early and the human authorises scope expansion. Default is deferred.

---

## 2. Baseline and Inheritance

### Ratified CDL chain (relevant to this window)

| CDL | Content | Ratified |
|-----|---------|----------|
| CDL-081 | Hyperedge ECU attribution (`REUSE_ATTRIBUTION_RATE = Decimal("0.20")`) | Phase 943 |
| CDL-082 | H-013 gossip beacon emission threshold (`H013_CHANGE_THRESHOLD = 0.15`) | Phase 950 |

### Active runtime chain (relevant)

| Module | Version token | Phase |
|--------|--------------|-------|
| `ilc_core/economics/epoch_attribution_settle_runtime.py` | `epoch_attribution_settle_runtime_946.v0.1` | 946 |
| `ilc_core/types.py` | `EPOCH_ATTRIBUTION_BATCH_VERSION = "epoch_attribution_batch.v0.2"` | 946 |
| `ilc_core/node/node_startup_runtime.py` | `H013_CHANGE_THRESHOLD = 0.15` | 950 |

### Active stub (target of this window)

```python
# ilc_core/economics/epoch_attribution_settle_runtime.py
CDL_HCON_02_DEPENDENCY = "h_con_02_cdl_required_before_ejected_stake_treasury_executes"

elif attr_event.edge_type == EdgeType.REFUTATION:
    # §4.5 Ejected stake / refutation treasury path — H-CON-02 required.
    raise NotImplementedError(CDL_HCON_02_DEPENDENCY)
```

### Canonical anchors inherited

- CDL-081 spec: `docs/specs/ilc_cdl_081_hyperedge_ecu_attribution_opening_929_v0.1.md`
- Settle runtime: `ilc_core/economics/epoch_attribution_settle_runtime.py`
- Types: `ilc_core/types.py` — `PROVENANCE_MAX_DEPTH = 3`, `PROVENANCE_DECAY_ALPHA = 0.5`
  (provisional, not this window's scope)
- Coherence report: `docs/specs/ilc_integration_coherence_report_1100_v0.1.md`
- Capsule: `docs/specs/ilc_antigravity_context_capsule_v5.33.md`

**Next fresh CDL number:** CDL-083 (CDL-082 was the last ratified).

---

## 3. Track Inventory

### 3.1 Constitutionally obligated

| Item | Authority | Status |
|------|-----------|--------|
| H-CON-02: Panel quorum rules | CDL-081 §4.5 + Q1 REFUTATION deferral | **Primary obligation — this window** |
| CDL-083: H-CON-02 constitutional basis | CDL-081 prerequisite ✅ | **This window** |
| REFUTATION path in settle() | CDL-HCON_02_DEPENDENCY stub active | **This window** |

### 3.2 Deferred governance (not this window)

| Item | Reason | Target window |
|------|--------|--------------|
| CDL-084: PROVENANCE chain attribution | Separate scope; silently ignored is not a blocker | 1110+ |
| ADR-0035: Homoiconic type definition system | Direction accepted; CDL required before implementation | Post-CDL-083 |
| Homoiconic type CDL (CDL-085+) | Depends on ADR-0035; introduces `type="type_definition"` NodeType | TBD |
| Werner φ-bound CDL | Requires SIM evidence | TBD |
| SIM-BEACON-01 adversary revision | Separate SIM with sealed-sender constraints | TBD |
| Audit H1 (SSL cert) | Mainnet concern only | Pre-mainnet |
| Audit H2 (bootstrap exception) | Mainnet concern only | Pre-mainnet |
| Audit M2–M5 | Hardening; not constitutional | Pre-mainnet |

### 3.3 Simulation-conditional

None required for this window. CDL-081 ✅ is sufficient precedent for CDL-083. No SIM needed
to scope panel quorum rules — the values are governance/policy decisions, not empirical.

---

## 4. CDL-083 Scope: Panel Quorum Rules for Ejected Stake Distribution

### 4.1 Problem statement

CDL-081 §4.5 establishes that when a star node member is ejected, their stake is held in the
treasury. Distribution of that stake requires H-CON-02 quorum — but H-CON-02 does not yet
exist. `CDL_HCON_02_DEPENDENCY` is the active constitutional gate.

Additionally, CDL-081 Q1 established that REFUTATION edges are "conditional" on CDL-V7
Popperian gate upholding the refutation — but CDL-081 did not define the ECU flow for upheld
refutations. H-CON-02 must define this flow.

### 4.2 Human-gate questions (to be resolved at CDL-083 opening, Phase 1103)

| Question | Scope | Default position to investigate |
|----------|-------|--------------------------------|
| Q1 — Panel quorum floor | What fraction of remaining star node members must participate in a treasury distribution vote? | Majority (> 0.50) of active members |
| Q2 — Vote threshold | What fraction of participating members must agree to release ejected stake? | Exact 2/3 supermajority, evaluated by integer arithmetic (`approve_votes * 3 >= participating_voters * 2`) |
| Q3 — Distribution formula | How is released ejected stake divided among claimants? | Proportional to current stake of voting members |
| Q4 — REFUTATION ECU flow | When CDL-V7 upholds a refutation, where does ECU flow, from what source, and how much? | Refuting agent receives `REUSE_ATTRIBUTION_RATE` × refuted content's epoch ECU; sourced from emitter's epoch budget |
| Q5 — Ejected agent recovery | May an ejected agent reclaim treasury stake if later readmitted? | No — ejected stake is irrevocable; readmission starts fresh stake |

### 4.3 Runtime target

File: `ilc_core/economics/epoch_attribution_settle_runtime.py`

Changes:
- Replace `raise NotImplementedError(CDL_HCON_02_DEPENDENCY)` for REFUTATION with the
  CDL-083-ratified attribution logic.
- Add new version token: `EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION` → v0.2 (or new constant).
- Add `CDL_083_DEPENDENCY` token.

Optionally: add a new `ilc_core/economics/panel_quorum_runtime.py` if ejected stake
distribution logic is complex enough to warrant its own module.

### 4.4 Out of scope

- PROVENANCE chain attribution (CDL-084, separate window)
- ATTESTATION or EPOCH_BOUNDARY attribution changes
- Star node adoption rules (CDL-081 scope; already ratified)
- CDL-V7 Popperian gate implementation changes (CDL-052 scope; already ratified)
- Treasury governance (CDL-047 scope)

---

## 5. CDL Number Assignments

| CDL | Title | Q-digest anchor | Opening phase | Ratification phase |
|-----|-------|----------------|--------------|-------------------|
| CDL-083 | H-CON-02 panel quorum rules for ejected stake distribution + REFUTATION attribution | Q1–Q5 resolved at Phase 1103 | 1103 | 1105 |

---

## 6. Candidate Phase Table

| Order | Phase | Topic | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 1102 | Window sequence lock | Foundation / Constitutional | NON-SENSITIVE |
| 2 | 1103 | CDL-083 opening — H-CON-02 panel quorum + REFUTATION | Constitutional | **SENSITIVE** |
| 3 | 1104 | CDL-083 prelock hardening + ratification evidence doc | Constitutional | NON-SENSITIVE |
| 4 | 1105 | CDL-083 ratification (two-commit: runtime + CDL) | Constitutional / Runtime | **SENSITIVE** |
| 5 | 1106 | H-CON-02 runtime — REFUTATION path implementation | Runtime | NON-SENSITIVE |
| 6 | 1107 | H-CON-02 ratification evidence tests | Runtime | NON-SENSITIVE |
| 7 | 1108 | Coherence report + capsule v5.34 | Synthesis | NON-SENSITIVE |
| 8 | 1109 | Window 1102–1109 closure gate | Gate | **SENSITIVE** |

**Conditional tail scenario:** If the human authorises scope expansion, Phase 1106 may also
include initial PROVENANCE attribution implementation (CDL-084 scope); Phase 1107 tests would
expand accordingly. This is not the default plan.

---

## 7. Sensitivity Classification

### SENSITIVE (require human GO token before execution)

| Phase | Trigger |
|-------|---------|
| 1103 | CDL-083 row inserted in constitutional log (`ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1103`) |
| 1105 Commit 2 only | CDL-083 spec OPEN → RATIFIED + log row updated (`ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1105`) |
| 1109 | Human closure verdict required — structural window boundary |

### NON-SENSITIVE (proceed after prompt approval)

Phases 1102, 1104, 1106, 1107, 1108.

### Conditional rule

Phase 1105 Commit 1 (runtime mutation) is NON-SENSITIVE — it mutates `ilc_core/` only and does
not require CDL env var. Phase 1105 Commit 2 (CDL mutation) IS SENSITIVE.

### Pre-commit hook

```
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1103   # Phase 1103 CDL log insert
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1105   # Phase 1105 Commit 2 only
```

Pre-commit hook enforces that CDL-authorized commits must NOT touch `ilc_core/`. Phase 1105
Commit 1 (runtime mutation) must be a separate commit with NO CDL env var.

---

## 8. Scope Notes for Fixed Phases

### Phase 1102 — Sequence lock (NON-SENSITIVE)

Produce `docs/specs/ilc_phase_1102_1109_sequence_lock_v0.1.md`. Lock the phase table from
this guidance doc. Token: `window_1102_1109_sequence_lock_committed_phase_1102`.

### Phase 1103 — CDL-083 opening (SENSITIVE)

Two deliverables in one commit (CDL env var required):
1. `docs/specs/ilc_cdl_083_h_con_02_panel_quorum_ejected_stake_opening_1103_v0.1.md` — Status: OPEN
2. `docs/specs/ilc_constitutional_decision_log_v0.1.md` — CDL-083 row inserted (status: open)

Read the constitutional log before writing. Do not reconstruct the CDL log table from memory.
The two-commit pattern does NOT apply at opening — CDL opening does not touch `ilc_core/`.

Token: `cdl_083_open_phase_1103`

### Phase 1104 — Prelock hardening + evidence doc (NON-SENSITIVE)

Two deliverables:
1. CDL-083 spec: add §7 Prelock Record with the Phase 1103 introducing commit hash.
2. `docs/specs/ilc_cdl_083_h_con_02_ratification_evidence_1104_v0.1.md` — evidence doc.

Prelock assertion: use `git log --oneline --diff-filter=A` to find the Phase 1103 introducing
commit, then `git show <hash>:` to confirm Status was OPEN. Record result in evidence doc and
in CDL-083 spec §7.

Token: `cdl_083_prelock_hardening_complete_phase_1104`

### Phase 1105 — CDL-083 ratification (SENSITIVE — two commits)

- **Commit 1 (runtime mutation — non-CDL commit):** `ilc_core/economics/epoch_attribution_settle_runtime.py`
  — add CDL-083 dependency token, exact-threshold constants, and the minimum ratified
  REFUTATION recipient contract needed for ratification evidence. No
  `ILC_CDL_MUTATION_AUTHORIZED` env var.
- **Commit 2 (CDL mutation commit):** CDL-083 spec OPEN → RATIFIED; CDL log row updated.
  Requires `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1105`. Must NOT touch `ilc_core/`.

Token: `cdl_083_ratified_phase_1105`

### Phase 1106 — H-CON-02 runtime hardening and panel quorum implementation (NON-SENSITIVE)

Complete the non-constitutional runtime surface around the ratified Phase 1105 mutation:
panel quorum helpers, exact-threshold edge cases, integration tests, and any extraction to
`ilc_core/economics/panel_quorum_runtime.py`. Phase 1106 must not re-open the Q1-Q5
semantics or duplicate the REFUTATION payout decision already consumed by Phase 1105.

Token: `h_con_02_refutation_runtime_implemented_phase_1106`

### Phase 1107 — Tests (NON-SENSITIVE)

File: `tests/test_phase_1107_h_con_02_panel_quorum_settle.py`

Minimum coverage:
- REFUTATION event: CDL-V7-upheld path produces expected ECU payout
- REFUTATION event: non-upheld path produces empty payout or appropriate guard
- Ejected stake: treasury accumulation token asserted
- Panel quorum: quorum floor and threshold constants correct
- `CDL_083_DEPENDENCY` token present in runtime
- Version token updated from v0.1 to v0.2 (or new constant)
- Phantom edit guard: `CDL_HCON_02_DEPENDENCY` still present in runtime (it remains as a
  historical marker token — only the `raise NotImplementedError` call is removed)

### Phase 1108 — Coherence report + capsule v5.34 (NON-SENSITIVE)

Files:
- `docs/specs/ilc_integration_coherence_report_1108_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.34.md`

Token: `coherence_report_1108_verdict=pass`, `capsule_v5_34_supersedes_v5_33`

### Phase 1109 — Closure gate (SENSITIVE)

File: `tests/test_phase_1109_window_1102_1109_closure_gate.py`

Selftest guard: `ILC_PHASE_1109_GATE_SELFTEST=1`

Categories:
1. Sequence lock token
2. CDL-083 lifecycle (open Phase 1103, prelock Phase 1104, ratified Phase 1105)
3. H-CON-02 runtime (version token, CDL_083_DEPENDENCY, REFUTATION path live)
4. Phase 1108 coherence + capsule
5. Selftest probe

Token: `window_1102_1109_closure_gate_verdict=pass`

---

## 9. Key Dependencies and Open Questions

### Must-resolve at window entry

- Phase 1101 closure gate must pass (window 945–950, 1100–1101 must be closed before 1102 opens).
- CDL-083 Q1–Q5 (§4.2 above) must be resolved by the human at Phase 1103 opening.

### Sequencing constraints

1. Phase 1102 (seq lock) must precede all other phases.
2. Phase 1103 (CDL open) must precede Phase 1104 (prelock) — prelock asserts the open state.
3. Phase 1104 must precede Phase 1105 (ratification cites evidence doc).
4. Phase 1105 Commit 1 (runtime mutation) must precede Phase 1105 Commit 2 (CDL mutation).
5. Phase 1105 must precede Phase 1106 (ratification-enabling runtime mutation lands first; Phase 1106 hardens and tests the ratified runtime surface without re-opening CDL-083 semantics).
6. Phase 1106 must precede Phase 1107 (tests import the runtime).
7. Phases 1102–1107 must precede Phase 1108 (coherence cites all window work).
8. Phase 1108 must precede Phase 1109 (closure gate cites coherence report).

### Open questions

1. **Q1–Q5 panel quorum values** — the §4.2 "default positions to investigate" are proposals
   for the human to deliberate on, not pre-decided values. The human's answers drive Phase 1103.

2. **Panel quorum implementation complexity** — if panel quorum distribution requires a separate
   runtime module, Phase 1106 scope expands. The guidance doc allows this; the phase prompt will
   specify.

3. **REFUTATION ECU source** — CDL-083 Q4 (REFUTATION ECU flow source) needs to be compatible
   with CDL-047 treasury governance. If the ECU source is the emitter's epoch budget, no treasury
   change is required. If sourced from the treasury itself, CDL-047 interface is needed.

### Permanently deferred (from this window)

- PROVENANCE chain attribution — CDL-084, separate window (1110+).
- Werner φ-bound — needs SIM.
- Homoiconic type definition system — ADR-0035 accepted; CDL required; post-CDL-083.

---

## 10. Known Patterns and Technical Constraints

### Novel patterns this window

- **REFUTATION attribution logic** — first time REFUTATION edge produces an ECU payout (all prior
  settle() calls either process REUSE/CO_AUTHORSHIP or skip). CDL-083 chooses caller-filtering:
  only CDL-V7-upheld refutations enter the batch. The runtime must still carry an explicit
  refuting-agent recipient field and must not overload `target_creator_id` in a way that pays the
  creator of the refuted target.

- **Two-commit ratification** — same pattern as CDL-081 (Phase 942–943) and CDL-082 (Phase 950).
  Phase 1105 Commit 1 is a runtime mutation (no CDL env var); Commit 2 is a CDL mutation (CDL env
  var required, no `ilc_core/` files).

### Historical prelock hardening

Use `git log --oneline --diff-filter=A` to find the Phase 1103 introducing commit, then
`git show <hash>:` to confirm Status was OPEN. This is the same pattern used in CDL-082
(Phase 949 prelock, commit `192e58ea`).

### Phantom edit guard

Phase 1107 tests should include a phantom edit guard confirming:
- `CDL_HCON_02_DEPENDENCY` constant is still present in `epoch_attribution_settle_runtime.py`
  (the constant is a historical marker; only the `raise NotImplementedError` call is replaced)
- `CDL_083_DEPENDENCY` is present (new token added by Phase 1105 Commit 1)

### Selftest guard chain

Phase 1109 gate adds `ILC_PHASE_1109_GATE_SELFTEST=1`. This continues the chain established
at Window 945–950, 1100–1101 (`ILC_PHASE_1101_GATE_SELFTEST=1`). The Phase 1109 gate must
include `ILC_PHASE_1101_GATE_SELFTEST=1` in its Category 3 selftest-exclusion list to prevent
recursion when the prior gate tests are re-imported.

### AttributionEvent — REFUTATION upheld flag

The current `AttributionEvent` dataclass in `epoch_attribution_settle_runtime.py`:
```python
@dataclass(frozen=True)
class AttributionEvent:
    edge_type: EdgeType
    target_creator_id: str
    star_node_id: Optional[str]
    epoch: int
```

For REFUTATION events, CDL-083 Q4 selects caller-filtering: if a refutation is not upheld by
CDL-V7, it is not added to the `EpochAttributionBatch`. The settle runtime processes all
REFUTATION events in the batch as upheld by definition. The event shape still needs an explicit
refuting-agent recipient, because `target_creator_id` names the refuted target creator in the
REUSE-oriented path and is ambiguous for REFUTATION.

---

## 11. Non-Goals and Explicitly Deferred Items

- **PROVENANCE chain attribution** — CDL-084, not this window
- **Star node governance** (quorum for node creation/dissolution decisions beyond ejected stake) — future CDL
- **CDL-V7 Popperian gate changes** — CDL-052 is ratified; no changes to the gate itself
- **Treasury governance changes** — CDL-047 ratified; ECU source must be compatible but no CDL-047 amendment expected
- **Mainnet readiness** — Audit H1/H2/M2–M5 remain deferred
- **Werner φ-bound CDL** — SIM required first
- **Panel membership management** (buy-in, exit beyond ejection) — CDL-081 scope; already ratified

---

## 12. Architectural Context: ADR-0035

**ADR-0035** (Homoiconic Type Definition System) was drafted concurrently with this guidance
doc. It records the accepted direction that `hyperedge_type` values should eventually become
definition nodes in the graph — governed by CDL, disputable by jury — rather than hardcoded
string literals.

This does NOT affect Window 1102–1109. CDL-083 proceeds with the current string-based
`hyperedge_type` system. ADR-0035 is a forward obligation for a later window.

Reference: `docs/specs/ilc_adr_0035_homoiconic_type_definition_system_v0.1.md`

Key implication for CDL-083 drafting: when writing the rules for ejected stake distribution
and REFUTATION attribution, write them as if they will eventually be encoded in a
`co_authorship` definition node. Avoid runtime logic that would be difficult to extract
into a definition node later. Prefer explicit constants and clear rule boundaries.

---

## 13. Key Canonical Anchors for Prompt Drafting

- CDL-081 spec §4.5 (ejected stake treasury rule): `docs/specs/ilc_cdl_081_hyperedge_ecu_attribution_opening_929_v0.1.md`
- CDL-082 spec (ratification pattern reference): `docs/specs/ilc_cdl_082_h013_emission_threshold_amendment_opening_948_v0.1.md`
- Settle runtime: `ilc_core/economics/epoch_attribution_settle_runtime.py`
  — `CDL_HCON_02_DEPENDENCY`, `AttributionEvent`, `settle_attribution_batch()`
- Types: `ilc_core/types.py` — `EdgeType.REFUTATION`, `PROVENANCE_MAX_DEPTH`, `PROVENANCE_DECAY_ALPHA`
- Constitutional log: `docs/specs/ilc_constitutional_decision_log_v0.1.md` (read before every CDL mutation)
- Capsule v5.33: `docs/specs/ilc_antigravity_context_capsule_v5.33.md`
- Two-commit pattern precedent: CDL-082 Phase 950 (Commit 1 = `e4beb583`, Commit 2 = CDL mutation)
- Prelock hardening precedent: CDL-082 Phase 949 (commit `192e58ea`, `git show` pattern)
- Selftest guard chain: `ILC_PHASE_1101_GATE_SELFTEST=1` (prior window), `ILC_PHASE_1109_GATE_SELFTEST=1` (this window)

---

## 13. Rationale for Single-Window Scope

1. CDL-083 / H-CON-02 is the single active constitutional obligation after Phase 950.
2. REFUTATION + ejected stake is narrow enough to ratify in one CDL without a SIM.
3. PROVENANCE is explicitly deferred to keep this window at 8 phases.
4. No other pending SIMs or CDLs are unblocked by this window.

`window_1102_1109_candidate_phase_grouping_v0_1`

**Status:** CLOSED — Phase 1109 closure gate passed. `window_1102_1109_closed_phase_1109`
