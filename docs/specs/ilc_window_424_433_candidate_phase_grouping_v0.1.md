# ILC Window 424-433: Candidate Phase Grouping

**Author:** Claude Sonnet 4.6 (local architectural reviewer)
**Date:** 2026-03-16
**Baseline:** Window 414-423 CLOSED (Phase 423 verdict: pass). CDL-047 (treasury governance) and CDL-048 (ECU mandatory conversion deadline) ratified. D2e Agent CLI (Phase 420, `d2e_agent_cli_420.v0.1`) and D2e Lifecycle CLI (Phase 421, `d2e_lifecycle_cli_421.v0.1`) complete. Capsule v1.6 current.

**Planning note:** This is a candidate grouping, not a locked sequence. Phases 424-428 are the hard minimum lane. Phases 429-431 are conditional tail slots and must not compress constitutional discipline if Phase 426 discovers a larger-than-expected P_e stabilization scope.

---

## 1. Track inventory arriving from Phase 423

### Constitutionally obligated (non-negotiable)

- CDL-049 (bounded-existential claim-form alignment) — must begin under Window 424's own sequence lock; locked by the Phase 423 handoff; Phase 417 MODERATE finding identified the governance and runtime wording gap in `popperian_gate_runtime.py` and CDL-V7 review corpus

### Deferred governance work (conditionally authorized)

- Treasury P_e stabilization follow-on — CDL-047 authorizes the treasury-governance framework but does not lock P_e stabilization trigger or limit constants; Phase 423 handoff restores this as the canonical Window-424+ obligation
- D2e CLI follow-on expansion — Phases 420/421 delivered agent and node command families; further CLI subcommand expansion is conditional on identified operational gaps and must preserve the `ilc_core/cli/` namespace discipline

### Simulation-conditional

- SIM-009 commissioning — reserved; authorized only if new coherence gaps or insufficient Treasury P_e calibration data warrant it; not pre-authorized by Window 414-423

---

## 2. CDL-049 scope (constitutional lane)

CDL-049 is the bounded-existential claim-form alignment lane. Its scope is narrowly defined by the Phase 417 MODERATE finding:

1. `ilc_core/consensus/popperian_gate_runtime.py` — `_ADMISSIBLE_CLAIM_FORMS` currently includes `"existential"` (unqualified); CDL-049 must replace this with `"bounded_existential"`.
2. `docs/specs/ilc_popper_ilc_analysis_v0.1.md` — review corpus language references existential forms without the bounded qualifier; CDL-049 must update or supersede the relevant active sections. If a passage is preserved as a historical quotation or citation, the correct fix is a superseding note or adjacent alignment note rather than rewriting the quoted historical text itself.
3. Downstream propagation — active forward-facing runtime, analysis, and current-context sources consuming CDL-V7 semantics must be aligned if they still use unqualified `existential` vocabulary. Historical ratification evidence artifacts, quoted historical source passages, closed-window handoffs, and closed-phase walkthroughs/prompts are read-only and are not mutated.

Non-goal: `docs/specs/ilc_cdl_v7_agent_decomposition_criteria_ratification_evidence_335_v0.1.md` is a historical ratification evidence artifact named by the Phase 417 finding, but CDL-049 does not patch it. The correct fix is to narrow future active runtime and forward-facing references, not to rewrite historical evidence.

CDL-049 does not reopen or mutate the historical CDL-V7 row or its ratification evidence. CDL-V7 remains ratified as a historical constitutional artifact. CDL-049 instead ratifies a downstream narrowing override for future active runtime and forward-facing references: the admitted claim-form vocabulary becomes `bounded_existential` rather than unqualified `existential`.

---

## 3. Treasury P_e and SIM-009 branch

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

## 4. Candidate Window 424-433: "Bounded-Existential Alignment + P_e Governance Stabilization" (10 phases)

| Phase | Topic | Character |
|---|---|---|
| 424 | Seq lock + CDL-049 opening (bounded-existential claim-form alignment) | Foundation / Constitutional (first action) |
| 425 | CDL-049 prelock hardening | Constitutional |
| 426 | Treasury P_e stabilization governance review (SIM-009 authorization gate) | Governance review |
| 427 | CDL-049 ratification evidence assembly (vocabulary propagation scope + runtime-patch contract) | Constitutional / Runtime-prep |
| 428 | CDL-049 ratification (runtime patch + bounded-vocabulary propagation) | Constitutional / Runtime |
| 429 | Conditional tail slot 1: P_e constitutional continuation, SIM-009 commissioning, or D2e CLI Part 3 only if constitutional tail is not consumed | Conditional |
| 430 | Conditional tail slot 2: P_e constitutional continuation, SIM-009 results processing, or reserve / gap closure | Conditional |
| 431 | Conditional tail slot 3: P_e constitutional continuation, reserve / gap closure, or carry-forward decision publication | Conditional |
| 432 | Coherence + capsule v1.7 | Synthesis |
| 433 | Closure gate | Gate |

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

## 5. Key dependencies and open questions

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

## 6. Parallel administrative track: public export and release engineering

The public-export / release-engineering track identified in `TODO.txt` remains active, but it is not part of the numbered constitutional window. It should run as a parallel administrative track rather than consuming Phases 424-433 tail slots that are reserved for constitutional uncertainty around `CDL-049`, Treasury `P_e`, and possible `SIM-009` follow-on.

Recommended scope for the parallel track:

1. define the public allowlist / denylist manifest,
2. implement the allowlist-based export or sync script for ongoing publication,
3. document the one-time public repo bootstrap method (including whether `git filter-repo` is used once for initial history shaping),
4. prepare the public release packaging checklist for wheel / container / tarball outputs.

This track may proceed in parallel with Window 424-433 so long as it does not mutate constitutional artifacts, interfere with active phase execution, or force premature refactoring of legacy namespaces solely for packaging purposes. If release engineering begins during this window, it should use a separate working context and treat the private canonical repo as the source of truth.

---

## 7. Rationale for single-window scope

Window 424-433 is proposed as a single 10-phase candidate window because:

1. Phases 424-428 form a coherent minimum lane: sequence lock, CDL-049 opening, CDL-049 hardening, and CDL-049 ratification with the required runtime narrowing patch.
2. The Treasury P_e branch is real but still unresolved; reserving Phases 429-431 as conditional tail slots keeps the decision local to Phase 426 instead of pretending the branch is already settled.
3. D2e CLI expansion is explicitly lower priority than the constitutional tail and can be absorbed only if the constitutional branch does not consume the remaining slots.
4. No additional non-conditional constitutional queue is currently authorized beyond CDL-049.

This means the single-window proposal is intentionally front-loaded and conditional, not guaranteed end-to-end. If Phase 426 identifies a P_e stabilization scope that cannot fit the remaining slots without compressing constitutional discipline, the correct action is to carry the P_e lane into the next window rather than forcing it into 429-431.
