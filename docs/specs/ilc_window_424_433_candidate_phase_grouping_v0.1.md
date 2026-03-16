# ILC Window 424-433: Candidate Phase Grouping

**Author:** Claude Sonnet 4.6 (local architectural reviewer)
**Date:** 2026-03-16
**Baseline:** Window 414-423 CLOSED (Phase 423 verdict: pass). CDL-047 (treasury governance) and CDL-048 (ECU mandatory conversion deadline) ratified. D2e Agent CLI (Phase 420, `d2e_agent_cli_420.v0.1`) and D2e Lifecycle CLI (Phase 421, `d2e_lifecycle_cli_421.v0.1`) complete. Capsule v1.6 current.

**Planning note:** This is a candidate grouping, not a locked sequence. Phases 424-428 are the hard minimum lane. Phases 429-431 are conditional tail slots and must not compress constitutional discipline if Phase 426 discovers a larger-than-expected P_e stabilization scope.

---

## 1. Window identity and scope

**Window 424-433**: Bounded-Existential Claim-Form Alignment + Treasury P_e Governance Stabilization

This window ratifies CDL-049, which narrows the Popperian claim-form vocabulary in `popperian_gate_runtime.py` from unqualified `existential` to `bounded_existential`. CDL-049 is constitutionally obligated by the Phase 417 MODERATE finding and is the first constitutional action of Window 424 under its own sequence lock.

The conditional tail (Phases 429-431) is reserved for Treasury P_e stabilization governance (CDL-047 amendment or new CDL-050) and for D2e CLI Part 3 if a gap-analysis artifact confirms materially missing CLI scope. Phase 426 is the non-ratifying governance review that authorizes the tail.

---

## 2. Baseline and inheritance from Window 414-423 closure

The following is fully settled at Phase 423 close and carries forward without reopening:

**Ratified CDL chain (current complete set):**
- CDL-034 through CDL-038: node-schema ratified (Phases 349-353)
- CDL-039 through CDL-046: all ratified
- CDL-047: treasury governance framework ratified (Phase 418) — bounty_cap 0.15×B_e, burn_floor 0.05, velocity_alert_floor 0.91
- CDL-048: ECU mandatory conversion deadline ratified (Phase 419) — ecu_conversion_deadline 4 issuance epochs
- CDL-V1 through CDL-V7: all ratified. CDL-V4, CDL-V5, CDL-V6 are governance procedures with no runtime module. CDL-V7 (`popperian_gate_runtime`) is the runtime target for CDL-049's vocabulary amendment.
- CDL-021: permanently deferred (Rust/WASM)

**Active runtime chain:**
- V-series runtime: `temporal_decay_runtime` (V1), `sybil_resistance_runtime` (V2), `diversity_floor_runtime` (V3), `popperian_gate_runtime` (V7) — four modules only; V4/V5/V6 have no runtime module
- D2e CLI: `d2e_agent_cli_420.v0.1` + `d2e_lifecycle_cli_421.v0.1`
- D2e runtime: `agent_id_runtime` (Phase 410) + `timed_out_lifecycle_runtime_411` (Phase 411)

**Canonical anchors inherited:**
- `docs/specs/ilc_antigravity_context_capsule_v1.6.md` — PRIMARY context doc
- `docs/specs/ilc_window_414_423_handoff_423_v0.1.md` — Window 414-423 closure handoff
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.2.md` — wallet-agnostic signing (unchanged)
- `docs/specs/ilc_popperian_claim_form_governance_review_417_v0.1.md` — Phase 417 MODERATE finding (CDL-049 scope source)
- `ilc_core/consensus/popperian_gate_runtime.py` — CDL-049 runtime mutation target

**Next fresh CDL number**: CDL-049

---

## 3. Track inventory arriving from Phase 423

### Constitutionally obligated (non-negotiable)

- CDL-049 (bounded-existential claim-form alignment) — must begin under Window 424's own sequence lock; locked by the Phase 423 handoff; Phase 417 MODERATE finding identified the governance and runtime wording gap in `popperian_gate_runtime.py` and CDL-V7 review corpus

### Deferred governance work (conditionally authorized)

- Treasury P_e stabilization follow-on — CDL-047 authorizes the treasury-governance framework but does not lock P_e stabilization trigger or limit constants; Phase 423 handoff restores this as the canonical Window-424+ obligation
- D2e CLI follow-on expansion — Phases 420/421 delivered agent and node command families; further CLI subcommand expansion is conditional on identified operational gaps and must preserve the `ilc_core/cli/` namespace discipline

### Simulation-conditional

- SIM-009 commissioning — reserved; authorized only if new coherence gaps or insufficient Treasury P_e calibration data warrant it; not pre-authorized by Window 414-423

---

## 4. CDL-049 scope (constitutional lane)

CDL-049 is the bounded-existential claim-form alignment lane. Its scope is narrowly defined by the Phase 417 MODERATE finding:

1. `ilc_core/consensus/popperian_gate_runtime.py` — `_ADMISSIBLE_CLAIM_FORMS` currently includes `"existential"` (unqualified); CDL-049 must replace this with `"bounded_existential"`.
2. `docs/specs/ilc_popper_ilc_analysis_v0.1.md` — review corpus language references existential forms without the bounded qualifier; CDL-049 must update or supersede the relevant active sections. If a passage is preserved as a historical quotation or citation, the correct fix is a superseding note or adjacent alignment note rather than rewriting the quoted historical text itself.
3. Downstream propagation — active forward-facing runtime, analysis, and current-context sources consuming CDL-V7 semantics must be aligned if they still use unqualified `existential` vocabulary. Historical ratification evidence artifacts, quoted historical source passages, closed-window handoffs, and closed-phase walkthroughs/prompts are read-only and are not mutated.

Non-goal: `docs/specs/ilc_cdl_v7_agent_decomposition_criteria_ratification_evidence_335_v0.1.md` is a historical ratification evidence artifact named by the Phase 417 finding, but CDL-049 does not patch it. The correct fix is to narrow future active runtime and forward-facing references, not to rewrite historical evidence.

CDL-049 does not reopen or mutate the historical CDL-V7 row or its ratification evidence. CDL-V7 remains ratified as a historical constitutional artifact. CDL-049 instead ratifies a downstream narrowing override for future active runtime and forward-facing references: the admitted claim-form vocabulary becomes `bounded_existential` rather than unqualified `existential`.

---

## 5. Treasury P_e and SIM-009 branch

CDL-047 ratified three governance constants (bounty_cap = 0.15 × B_e, burn_floor = 0.05, velocity_alert_floor = 0.91) as a framework. The P_e price-stabilization trigger and limit constants are explicitly outside that framework and require a separate governance assessment.

Phase 426 (proposed) is a non-ratifying governance review to determine whether:

- SIM-008 results provide a sufficient calibration basis for locking P_e trigger/limit constants without a new simulation round, OR
- SIM-009 must be commissioned to generate additional P_e calibration data.

The Phase 426 verdict drives the conditional Phases 429-431 tail slots. Phase 426 must explicitly classify the P_e branch into one of three outcomes:

- **Direct amendment/new-lane path fits this window:** SIM-008 is sufficient and the remaining constitutional work can still respect the normal opening/prelock/ratification pattern without over-compressing the tail. If this resolves to a new `CDL-050` lane rather than a `CDL-047` amendment, the three tail slots are presumed fully consumed by opening, prelock, and ratification.
- **SIM-009 required:** additional calibration is needed, so SIM-009 can be commissioned in-window, but the downstream P_e constitutional lane may need to carry into the next window if the remaining slots are insufficient.
- **No immediate constitutional follow-on:** P_e stabilization remains a Window 434+ carry-forward item and any spare runtime capacity may be used for D2e CLI follow-on work instead.

D2e CLI Part 3 is lower priority than the constitutionally grounded P_e branch. It may use a tail slot only if Phase 426 determines that doing so does not force the P_e constitutional lane into an over-compressed pattern and only after a short gap-analysis artifact identifies materially missing D2e-01 through D2e-11 coverage.

---

## 6. CDL number assignments for Window 424-433

| CDL | Title (candidate) | Decision digest anchor | Opening phase | Ratification phase |
|-----|-------------------|----------------------|---------------|-------------------|
| CDL-049 | bounded-existential claim-form alignment | `bounded_existential in _ADMISSIBLE_CLAIM_FORMS, ilc_popper_ilc_analysis vocabulary aligned` | Phase 424 | Phase 428 |
| CDL-050 | Treasury P_e stabilization trigger and limit constants (conditional) | TBD at Phase 426 governance review | Phase 429 (conditional) | Phase 431 (conditional) |

CDL-049 is the only pre-authorized CDL for this window. CDL-050 is conditional on Phase 426 verdict. If Phase 426 concludes a CDL-047 amendment is preferred over a new CDL row, CDL-050 is not used and the amendment inherits CDL-047's number.

---

## 7. Candidate phase table (424-433)

| Order | Phase | Topic | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 424 | Seq lock + CDL-049 opening (bounded-existential claim-form alignment) | Foundation / Constitutional (first action) | **SENSITIVE** |
| 2 | 425 | CDL-049 prelock hardening | Constitutional | constitutional |
| 3 | 426 | Treasury P_e stabilization governance review (SIM-009 authorization gate) | Governance review | NON-SENSITIVE |
| 4 | 427 | CDL-049 ratification evidence assembly (vocabulary propagation scope + runtime-patch contract) | Constitutional / Runtime-prep | NON-SENSITIVE |
| 5 | 428 | CDL-049 ratification (runtime patch + bounded-vocabulary propagation) | Constitutional / Runtime | **SENSITIVE** |
| 6 | 429 | Conditional tail slot 1: P_e constitutional continuation, SIM-009 commissioning, or D2e CLI Part 3 only if constitutional tail is not consumed | Conditional | **conditional** |
| 7 | 430 | Conditional tail slot 2: P_e prelock, SIM-009 results processing, or reserve / gap closure | Conditional | NON-SENSITIVE |
| 8 | 431 | Conditional tail slot 3: P_e ratification, carry-forward decision publication, or reserve | Conditional | **conditional** |
| 9 | 432 | Coherence + capsule v1.7 | Synthesis | NON-SENSITIVE |
| 10 | 433 | Closure gate | Gate | **SENSITIVE** |

### Conditional note on Phases 429-431

Three baseline scenarios are possible depending on Phase 426 outcome and D2e CLI gap assessment:

**Scenario A1 (SIM-008 sufficient; P_e amendment path fits in-window):** Phase 429 = `CDL-047` amendment opening; Phase 430 = `CDL-047` amendment prelock; Phase 431 = `CDL-047` amendment ratification. Under this path, D2e CLI Part 3 is deferred rather than compressed into the same tail.

**Scenario A2 (SIM-008 sufficient; new CDL-050 lane required):** Phase 429 = `CDL-050` opening; Phase 430 = `CDL-050` prelock; Phase 431 = `CDL-050` ratification. Under this path, D2e CLI Part 3 is deferred rather than compressed into the same tail.

**Scenario B (SIM-009 warranted):** Phase 429 = SIM-009 commissioning; Phase 430 = SIM-009 results synthesis and disposition; Phase 431 = publish the carry-forward decision for the P_e constitutional lane unless a sequence-lock amendment proves the remaining constitutional work still fits cleanly. Default assumption: P_e constitutional mutation carries into the next window under this scenario.

**Scenario C (no immediate P_e constitutional follow-on; D2e gap identified):** Phase 429 = D2e CLI Part 3, but only after a brief written gap-analysis artifact confirms materially missing CLI scope. Phases 430-431 = reserve / governance gap closure / carry-forward planning note for the deferred P_e lane.

In all scenarios, Phases 432 and 433 remain synthesis and closure gate respectively. The tail slots are intentionally conditional and must not be used to compress constitutional opening-prelock-ratification discipline into an unsafe pattern.

### Note on Phase 426 non-ratifying boundary

Phase 426 is a governance review phase (parallel to Phase 417 in Window 414-423). It does not open, amend, or ratify any CDL row. It produces a disposition assessment: if the P_e assessment identifies a CRITICAL defect in the SIM-008 basis, the P_e constitutional lane is deferred and SIM-009 or next-window carry-forward becomes mandatory; if CLEAN or MODERATE, the conditional 429-431 slots may proceed under the selected scenario, subject to preserving constitutional lane discipline.

### Note on Phase 428 runtime mutation pattern

Phase 428 is the first CDL ratification in ILC history that directly amends an already-ratified runtime file (`popperian_gate_runtime.py`). The commit resolver must qualify via at least these paths being present in the commit's changed files: the CDL path, `ilc_core/consensus/popperian_gate_runtime.py`, the Phase 427 evidence artifact, the new Phase 428 ratification test, and the historicalized Phase 424 prelock test. The test must implement a custom runtime-mutation scope check (NOT `assert_head_commit_touched_no_runtime_files`) and must assert:

- `"bounded_existential" in popperian_gate_runtime_text` (positive vocabulary token)
- the exact quoted legacy token is absent from the `_ADMISSIBLE_CLAIM_FORMS` source-text block, e.g. `'"existential"' not in admissible_claim_forms_block`, rather than a loose whole-file word search
- CDL-049 row carries ratification metadata (status, ratified_phase, ratified_date)
- only the `CDL-049` row may change inside `docs/specs/ilc_constitutional_decision_log_v0.1.md`; non-target row shield remains mandatory
- the Phase 424 prelock test is patched in the same Phase 428 commit to read the historical pre-ratification decision log state and assert `CDL-049` remained `open` at that historical commit

---

## 8. Sensitivity classification and Human GO requirements

**SENSITIVE phases (require `GO Phase NNN` human token before execution begins):**
- Phase 424: opens CDL-049 row (constitutional mutation authorized by Window-424 sequence lock)
- Phase 428: ratifies CDL-049 and patches `popperian_gate_runtime.py` (constitutional mutation + runtime mutation)
- Phase 429: SENSITIVE only in Scenarios A1/A2 (CDL-047 amendment opening or CDL-050 opening); NON-SENSITIVE in Scenarios B (SIM-009 commissioning) and C (D2e CLI Part 3)
- Phase 431: SENSITIVE only in Scenarios A1/A2 (CDL amendment or CDL-050 ratification); NON-SENSITIVE in Scenarios B (carry-forward publication) and C (gap closure)
- Phase 433: closure gate (structural boundary — always SENSITIVE)

**NON-SENSITIVE phases (no Human GO required):**
- Phase 425: CDL-049 prelock hardening — no CDL mutation, no runtime mutation
- Phase 426: Treasury P_e governance review — document only, no CDL mutation, no runtime mutation
- Phase 427: CDL-049 ratification evidence assembly — document only, no CDL mutation, no runtime mutation
- Phase 430: NON-SENSITIVE in all scenarios (prelock in A1/A2 = no CDL mutation; SIM-009 results synthesis in B = no CDL mutation; reserve in C = no CDL mutation)
- Phase 432: coherence and capsule v1.7 — synthesis only, no CDL mutation

**Rule for conditional phases:** Before executing any Phase 429 or 431, confirm with the human whether the selected scenario assigns a CDL mutation to that slot. If yes, require `GO Phase NNN` before proceeding. If no, the phase is NON-SENSITIVE.

**Pre-commit hook for CDL mutations:**
```
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=<phase>
```
Required for Phase 424, Phase 428, and any tail slot that opens or ratifies a CDL row.

---

## 9. Scope notes for fixed phases (424-428)

> Phases 429-431 scope depends on Phase 426 verdict and selected scenario; see Section 7 conditional notes above.

### Phase 424 — Window sequence lock + CDL-049 opening

**SENSITIVE.** Requires `GO Phase 424` human token.

**Deliverables:**
- `docs/specs/ilc_phase_424_433_sequence_lock_v0.1.md` — sequence lock artifact
- `docs/specs/ilc_cdl_049_bounded_existential_alignment_opening_stub_424_v0.1.md` — CDL-049 opening stub
- Constitutional mutation: one new row appended to `docs/specs/ilc_constitutional_decision_log_v0.1.md` for CDL-049 (`status: open`)

**Sequence lock required content:**
- Window identity: "Bounded-Existential Claim-Form Alignment + Treasury P_e Governance Stabilization"
- Inherited closure state from Phase 423 (CDL-047/048 ratification, D2e CLI version constants)
- Locked phase table (424-433) with character and sensitivity columns
- CDL-049 constitutional obligation statement (first action of this window, obligated by Phase 423 handoff)
- Phase 426 governance review non-ratifying boundary statement
- Conditional tail slots statement: Phases 429-431 depend on Phase 426 verdict
- CDL number assignment: CDL-049 (bounded-existential alignment); CDL-050 conditional on Phase 426
- Explicit statement: CDL-050 is NOT pre-authorized; it depends on Phase 426 outcome only
- Non-goals: no prelock, no ratification, no runtime mutation in Phase 424

**Test structure:** 5+2 pre-commit split. Four-path commit resolver: CDL + sequence lock + CDL-049 opening stub + test file. Direct dict equality for all pre-existing rows.

**Pre-commit hook:** `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=424`

**Commit subject:** `docs(g8): phase 424 window sequence lock and cdl-049 opening`

---

### Phase 425 — CDL-049 prelock hardening

**NON-SENSITIVE.** No CDL mutation.

**Deliverables:**
- `docs/specs/ilc_cdl_049_bounded_existential_alignment_prelock_hardening_425_v0.1.md`

**Prelock artifact required sections:**
1. Scope and non-ratifying boundary
2. CDL-049 open-state evidence anchor (Phase 424 commit)
3. Phase 417 MODERATE finding as the constitutional evidence basis for the winning candidate
4. Winning candidate: narrow `existential` → `bounded_existential` in `_ADMISSIBLE_CLAIM_FORMS`; update `ilc_popper_ilc_analysis_v0.1.md` active vocabulary sections
5. Rejected candidates with rationale: leave the runtime unchanged (rejected — governance gap persists); replace entire runtime module (rejected — over-broad scope beyond CDL-049 boundary)
6. Vocabulary propagation scope: active documents vs. read-only historical artifacts
7. Section-N ratification readiness evidence checklist (adapted from Phase 407/408 Section-7 pattern)
8. Non-goals

**Test structure:** 5+2 pre-commit split. `assert_head_commit_touched_no_runtime_files` is valid (no runtime files change in this phase).

**Commit subject:** `docs(g8): phase 425 cdl-049 bounded existential alignment prelock hardening`

---

### Phase 426 — Treasury P_e stabilization governance review

**NON-SENSITIVE.** No CDL mutation, no runtime mutation.

**Deliverables:**
- `docs/specs/ilc_treasury_pe_stabilization_governance_review_426_v0.1.md`

**Governance review required content:**
- Review scope: SIM-008 calibration basis adequacy for P_e trigger/limit constant locking
- SIM-008 P_e evidence assessment (reference `ilc_sim_008_commissioning_results_406_v0.1.md`)
- Explicit disposition verdict: one of three outcomes (direct amendment/CDL-050 path fits; SIM-009 required; no immediate constitutional follow-on)
- If direct path: CDL-047 amendment vs. new CDL-050 structuring recommendation
- Constitutional boundary statement: Phase 426 does not open, amend, or ratify any CDL row
- Forward assignment for Phases 429-431 based on verdict

**Explicit blocking rule:** A CRITICAL finding in the SIM-008 basis does NOT block Phases 427 or 428 (CDL-049 track is independent of the P_e branch). It affects only the tail slots.

**Commit subject:** `docs(g8): phase 426 treasury pe stabilization governance review`

---

### Phase 427 — CDL-049 ratification evidence assembly

**NON-SENSITIVE.** No CDL mutation, no runtime mutation.

**Deliverables:**
- `docs/specs/ilc_cdl_049_bounded_existential_alignment_ratification_evidence_427_v0.1.md`

**Evidence artifact required sections:**
1. Scope and ratification boundary
2. CDL-049 open-state anchor (Phase 424 commit)
3. Phase 417 MODERATE finding as constitutional evidence for the winning candidate
4. Phase 425 prelock hardening anchor
5. Runtime patch scope contract: `_ADMISSIBLE_CLAIM_FORMS` set change, vocabulary propagation plan for `ilc_popper_ilc_analysis_v0.1.md` active sections
6. Section-N ratification readiness evidence checklist satisfaction
7. Governance decision tokens for CDL-049 (exact ratification decision text — these will be tested in Phase 428)
8. Non-goals and boundary (explicitly: CDL-V7 historical ratification evidence is read-only and not patched)
9. Canonical anchors

**Commit subject:** `docs(g8): phase 427 cdl-049 ratification evidence assembly`

---

### Phase 428 — CDL-049 ratification

**SENSITIVE.** Requires `GO Phase 428` human token.

**Deliverables:**
- `ilc_core/consensus/popperian_gate_runtime.py` — `_ADMISSIBLE_CLAIM_FORMS` patched: `"existential"` → `"bounded_existential"`
- `docs/specs/ilc_popper_ilc_analysis_v0.1.md` — active vocabulary sections updated or annotated with superseding notes
- CDL-049 row mutation: `status: open → ratified`, add `ratified_phase: 428`, `ratified_date`, `evidence_document`
- `tests/test_phase_424_cdl_049_opening.py` — Phase 424 prelock test hardened to read CDL at Phase-424 historical commit and assert CDL-049 was `open`

**Test structure:** 7 tests (5+2 split). Custom 5-path commit resolver: CDL + Phase 427 evidence artifact + new Phase 428 test + Phase 424 prelock test + `popperian_gate_runtime.py`. Custom runtime-mutation scope check (NOT `assert_head_commit_touched_no_runtime_files`).

**Pre-commit hook:** `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=428`

**Phantom edit guard:** The CDL-049 canary probe will contain both the old token `"existential"` and the new token `"bounded_existential"` as adjacent literals. Copilot has historically applied these mutations to the source file during canary execution. Run `git diff HEAD -- ilc_core/` before every CDL commit. Fix: `git restore ilc_core/consensus/popperian_gate_runtime.py`.

**Commit subject:** `docs(g8): phase 428 cdl-049 bounded existential alignment ratification`

---

## 10. Key dependencies and open questions

### Must be resolved at Phase 424 entry

- Phase 423 handoff carries the CDL-049 constitutional obligation token as the mandatory first action of Window 424 (confirmed in Phase 423 handoff Section 5 and Section 7); no additional authorization required

### Sequencing constraints (non-negotiable)

- Phase 424 must open CDL-049 — this is the constitutional first action of the window
- CDL-049 must ratify (Phase 428) before any downstream phase uses `bounded_existential` as an assertion target or generates new agent-decomposition claims under the updated vocabulary
- Phase 426 (P_e governance review) must precede any SIM-009 commissioning or P_e amendment/new CDL; it is the authorization gate for the conditional branch
- If Phase 426 concludes that a new CDL-050 lane is required, do not compress opening, prelock, and ratification into fewer than the standard constitutional steps; either use the available tail slots cleanly or carry the lane into the next window
- D2e CLI Part 3, if pursued, must not reuse or call into the legacy `ilc_core/agent.py` entrypoint; the `ilc_core/cli/` namespace discipline is mandatory

### Open question: P_e CDL number

If Treasury P_e stabilization requires a new CDL row (new governance lane) rather than a CDL-047 amendment, it would be assigned CDL-050. If it amends CDL-047 directly (bounded extension of already-ratified framework), no new CDL number is needed. Phase 426 should resolve the structuring question.

### Open question: D2e CLI Part 3 scope

The D2e-01 through D2e-11 specification was the original target for D2e CLI implementation. Phases 420 and 421 covered the new agent (derive/inspect) and node (constants/timed-out-inspect/timed-out-d2d) command families on top of an already-existing CLI surface. Before committing to Phase 429 = D2e CLI Part 3, a brief gap analysis against the D2e-01 through D2e-11 scope should confirm whether any materially missing operations remain, rather than restating query / verify / bundle functionality that already exists in `ilc_core/cli/main.py`.

### Permanently deferred

- CDL-021 (Rust/WASM) — defer indefinitely (unchanged)
- CDL-V4/V5/V6 procedural extensions — governance-procedural-only, implementation-barred (unchanged)

---

## 11. Parallel administrative track: public export and release engineering

The public-export / release-engineering track identified in `TODO.txt` remains active, but it is not part of the numbered constitutional window. It should run as a parallel administrative track rather than consuming Phases 424-433 tail slots that are reserved for constitutional uncertainty around `CDL-049`, Treasury `P_e`, and possible `SIM-009` follow-on.

Recommended scope for the parallel track:

1. define the public allowlist / denylist manifest,
2. implement the allowlist-based export or sync script for ongoing publication,
3. document the one-time public repo bootstrap method (including whether `git filter-repo` is used once for initial history shaping),
4. prepare the public release packaging checklist for wheel / container / tarball outputs.

This track may proceed in parallel with Window 424-433 so long as it does not mutate constitutional artifacts, interfere with active phase execution, or force premature refactoring of legacy namespaces solely for packaging purposes. If release engineering begins during this window, it should use a separate working context and treat the private canonical repo as the source of truth.

See `docs/antigravity_tasks/codex_brief__release_engineering_parallel_track_424_plus.md` for full scope and execution slices.

---

## 12. Known patterns and technical constraints

### CDL-049 is the first amendment-of-existing-runtime ratification

Prior CDL ratifications either (a) created new runtime modules (CDL-V1/V2/V3/V7 in Phases 330-335, D2e runtimes in Phases 410-411) or (b) ratified doc-only CDLs with no runtime mutation. CDL-049 directly amends the already-ratified `popperian_gate_runtime.py`. Consequences:
- The custom runtime-mutation scope check must assert `popperian_gate_runtime.py` IS in changed paths (not merely absent from forbidden paths)
- The commit resolver must qualify via the runtime file being present (5-path resolver)
- The standard `assert_head_commit_touched_no_runtime_files` MUST NOT be used in Phase 428

### Historical prelock hardening (Phase 424 prelock test in Phase 428 commit)

After CDL-049 ratification, the Phase 424 prelock test must be hardened to assert `"status: open" in text` using a historical CDL reference (Phase-424 commit ref). This is the same pattern used in Phases 349-353 (node-schema ratification) and Phases 418-419 (economic CDL ratification). The hardened test reads the CDL at the historical opening commit, not the current HEAD.

### Phantom edit guard (popperian_gate_runtime.py is a CDL-049 canary target)

The CDL-049 canary probe will contain adjacent literal strings `"existential"` (old) and `"bounded_existential"` (new). Copilot has historically applied these vocabulary mutations to the actual source file during canary execution (the same pattern documented for `signer_lineage_runtime.py` in Windows 338-347). Run `git diff HEAD -- ilc_core/` before every CDL commit. Fix: `git restore ilc_core/consensus/popperian_gate_runtime.py`.

### Pre-commit hook ilc_core/ clean-state guard

The pre-commit hook (`.githooks/pre-commit`) blocks CDL-authorized commits when any `ilc_core/` file differs from HEAD (staged or worktree). For Phase 428 this guard must pass with only the intended `popperian_gate_runtime.py` change staged. Run `git diff HEAD --name-only -- ilc_core/` immediately before the CDL commit.

### Closure gate selftest guard chain (Phase 433 CRITICAL)

The Phase 433 closure gate script must include selftest guards for all prior window gate tests in the regression chain. The current chain at Window 423 close runs through Phase 337. The full env setup for category 3 must include:
`ILC_PHASE_423_GATE_SELFTEST=1`, `ILC_PHASE_413_GATE_SELFTEST=1`, `ILC_PHASE_401_GATE_SELFTEST=1`, `ILC_PHASE_391_GATE_SELFTEST=1`, `ILC_PHASE_377_GATE_SELFTEST=1`, `ILC_PHASE_367_GATE_SELFTEST=1`, `ILC_PHASE_357_GATE_SELFTEST=1`, `ILC_PHASE_347_GATE_SELFTEST=1`, `ILC_PHASE_337_GATE_SELFTEST=1`.

The correct audit is to read each prior gate test file and confirm it has `pytest.skip()` guarded by the selftest env var. Do NOT reason by analogy from what prior windows include — read the actual files.

---

## 13. Non-goals and explicitly deferred items

The following are explicitly NOT in scope for Window 424-433:

- CDL-021 (Rust/WASM): permanently deferred
- Any modification to CDL-V7 itself: CDL-V7 remains ratified as a historical constitutional artifact; CDL-049 narrows downstream vocabulary without reopening CDL-V7
- Patching `docs/specs/ilc_cdl_v7_agent_decomposition_criteria_ratification_evidence_335_v0.1.md`: read-only historical artifact, not mutated by CDL-049
- CDL-047 or CDL-028 modification for the P_e framework itself: CDL-047 ratified the framework; the trigger/limit operational mechanics are the subject of Phase 426 and the conditional tail only
- Any modification to CDL-030 (P_e clamp range [0.75, 1.30]): unchanged
- ADM-003 revision: ADM-003 v0.2 carries forward without change
- CDL-V4/V5/V6 procedural extensions: governance-procedural-only, implementation-barred
- CDL-050 pre-authorization: CDL-050 is conditional on Phase 426 verdict only; it is not pre-authorized
- Adaptive fee-burn ratio transition curve: not locked in this window
- Wallet-agnostic signing protocol modifications: ADM-003 v0.2 carries forward unchanged
- Any refactoring of `ilc_core/agent.py` or other legacy namespaces solely for packaging purposes in constitutional phases

---

## 14. Key canonical anchors for Window 424-433 prompt drafting

Codex should reference these in every Phase 424+ prompt:

- `docs/specs/ilc_antigravity_context_capsule_v1.6.md` — current context capsule (PRIMARY)
- `docs/specs/ilc_window_414_423_handoff_423_v0.1.md` — Window 414-423 closure baseline
- `docs/specs/ilc_phase_414_423_sequence_lock_v0.1.md` — prior sequence lock (format reference for Phase 424 sequence lock)
- `docs/specs/ilc_popperian_claim_form_governance_review_417_v0.1.md` — Phase 417 MODERATE finding (CDL-049 scope basis)
- `ilc_core/consensus/popperian_gate_runtime.py` — CDL-049 runtime mutation target
- `docs/specs/ilc_popper_ilc_analysis_v0.1.md` — review corpus vocabulary update target
- `docs/specs/ilc_constitutional_decision_log_v0.1.md` — CDL register
- `docs/phases/STATUS.md` — phase completion log
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.2.md` — wallet-agnostic signing (carry-forward only)
- `docs/specs/ilc_sim_008_commissioning_results_406_v0.1.md` — SIM-008 calibration data (Treasury P_e basis for Phase 426)
- `docs/specs/ilc_cdl_047_treasury_governance_ratification_evidence_418_v0.1.md` — CDL-047 framework baseline (P_e governance context)

For CDL-049 ratification phases (427-428): the prelock artifact from Phase 425.
For closure gate (Phase 433): all Phase 424-432 test files and artifacts.

---

## 15. Rationale for single-window scope

Window 424-433 is proposed as a single 10-phase candidate window because:

1. Phases 424-428 form a coherent minimum lane: sequence lock, CDL-049 opening, CDL-049 hardening, and CDL-049 ratification with the required runtime narrowing patch.
2. The Treasury P_e branch is real but still unresolved; reserving Phases 429-431 as conditional tail slots keeps the decision local to Phase 426 instead of pretending the branch is already settled.
3. D2e CLI expansion is explicitly lower priority than the constitutional tail and can be absorbed only if the constitutional branch does not consume the remaining slots.
4. No additional non-conditional constitutional queue is currently authorized beyond CDL-049.

This means the single-window proposal is intentionally front-loaded and conditional, not guaranteed end-to-end. If Phase 426 identifies a P_e stabilization scope that cannot fit the remaining slots without compressing constitutional discipline, the correct action is to carry the P_e lane into the next window rather than forcing it into 429-431.
