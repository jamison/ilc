# DEPRECATED — do not use this file as the canonical Window 434+ planning base.
#
# Superseded by:
# `docs/specs/ilc_window_434_plus_candidate_phase_grouping_v0.1.md`
#
# Reason:
# this draft pre-authorizes `CDL-050`, regresses the Treasury `P_e` evidence basis,
# and collapses release-engineering packaging/bootstrap into numbered phases.
#
# It is retained only as a historical comparison artifact.
#
# ILC Window 434-443: Candidate Phase Grouping

**Author:** Claude Sonnet 4.7 (local architectural reviewer)
**Date:** 2026-03-17
**Baseline:** Window 424-433 CLOSED (Phase 433 verdict: pass). CDL-049 (bounded-existential alignment) ratified. Treasury P_e stabilization carries forward into this window as the default continuation target. Release-engineering parallel track export staging is ready. Capsule v1.7 current.
**Planning note:** This is a candidate grouping, not a locked sequence. Phases 434-443 are presented as a firm 10-phase sequence given the dual obligations of release-engineering integration and Treasury P_e stabilization.

---

## 1. Window identity and scope

**Window 434-443**: Release Engineering Bootstrap + Treasury P_e Stabilization

This window resolves the parallel release engineering track that ran concurrently with Window 424-433. It integrates the export tooling, bootstraps the public distribution repository, and curates the public test suite. 

Concurrently, it opens, hardens, and ratifies CDL-050 to formally lock the Treasury P_e (price-stabilization) trigger and limit constants, fulfilling the carry-forward obligation from Phase 431.

---

## 2. Baseline and inheritance from Window 424-433 closure

The following is fully settled at Phase 433 close and carries forward without reopening:

**Ratified CDL chain (current complete set):**
- CDL-034 through CDL-049: all ratified. (CDL-049 aligned claim-form vocabulary).
- CDL-021: permanently deferred (Rust/WASM).

**Active runtime chain:**
- `popperian_gate_runtime.py` natively enforces `bounded_existential` terminology.
- D2e CLI: `d2e_agent_cli_420.v0.1` + `d2e_lifecycle_cli_421.v0.1`

**Release-Engineering status:**
- The `release-engineering-track` branch holds canonical export tooling (`tools/public_export_sync.py`), the allowlist, and the initial staging tree (`out/public_export/initial_public_source/`).
- Merge-timing rule inherited: 4 `ilc_core/` runtime commits from the release track must be cherry-picked to main BEFORE public repo packaging commits are merged.

**Treasury P_e Status:**
- CDL-047 is ratified, providing the framework structure but no locked constants for P_e.
- Window 434+ is the mandated default boundary for completing the P_e stabilization lane.
- A provisional planning anchor of `0.2` (trigger) and `0.02` (limit) has been advised via Phase 431 but remains unratified.

**Canonical anchors inherited:**
- `docs/specs/ilc_antigravity_context_capsule_v1.7.md` — PRIMARY context doc
- `docs/specs/ilc_window_424_433_handoff_433_v0.1.md` — Window 424-433 closure handoff
- `docs/specs/ilc_pe_stabilization_carry_forward_decision_431_v0.1.md` — Treasury P_e carry-forward decision

**Next fresh CDL number**: CDL-050

---

## 3. Track inventory arriving from Phase 433

### Constitutionally obligated (non-negotiable)

- Treasury P_e stabilization (CDL-050) — Carried forward from Phase 431. The Phase 433 handoff formally dispositioned this as the primary constitutional obligation for this window.

### Deferred governance work (conditionally authorized)

- None currently queued beyond CDL-050.

### Simulation-conditional

- SIM-010 commissioning — None anticipated. SIM-008 results are deemed the baseline calibration for CDL-050. 

### Parallel track obligations

- Release-Engineering Integration — The parallel track staging is complete (passing RE-05 through RE-08 gates) and explicitly bound to a merge-timing checklist in the Phase 433 handoff.

---

## 4. Release Engineering Bootstrap Scope

The public export bootstrapping follows a strict phase separation to prioritize safety:

1. **Runtime Sync (Phase 435):** Cherry-pick the 4 `ilc_core/` runtime commits from the release track. This synchronizes the main track's core engine with the enhancements built for the export pipeline (e.g., identity injection, dependency decoupling) while preserving main-track history.
2. **Packaging Merge (Phase 436):** Merge the remaining release engineering commits (the `out/public_export` staging tree, sync tool, docs).
3. **Public Test Suite (Phase 437):** Extract and curate a subset of `tests/` focusing strictly on core runtime logic (cryptography, routing, schema validation, economics, consensus). Historical closure-gate tests and snapshot dependencies remain exclusively internal and are NOT exported. This addresses finding F-7 from the RE-08 gate review.

---

## 5. CDL-050 scope (Treasury P_e stabilization)

The constitutional lane for Treasury P_e (price-stabilization) trigger and limit constants is treated as a new row (CDL-050) to cleanly demarcate the constants from the foundational CDL-047 framework. 

1. **Trigger Constant:** Locks the variance threshold that initiates stabilization actions based on SIM-008 baseline (`0.2`).
2. **Limit Constant:** Locks the maximum single-epoch intervention bound based on SIM-008 baseline (`0.02`).

This lane follows the standard 3-phase constitutional sequence: Opening (438), Prelock hardening (439), Ratification (440).

---

## 6. CDL number assignments for Window 434-443

| CDL | Title (candidate) | Decision digest anchor | Opening phase | Ratification phase |
|-----|-------------------|----------------------|---------------|-------------------|
| CDL-050 | Treasury P_e stabilization trigger and limit constants | `trigger: 0.2, limit: 0.02` | Phase 438 | Phase 440 |

CDL-050 is the sole pre-authorized CDL for this window.

---

## 7. Candidate phase table (434-443)

| Order | Phase | Topic | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 434 | Seq lock + Release Engineering Readiness Assessment | Foundation / Control | **SENSITIVE** |
| 2 | 435 | Release Eng runtime cherry-pick merge (4 commits) | Execution / Runtime | **SENSITIVE** |
| 3 | 436 | Release Eng packaging merge & initial export bootstrap | Infrastructure | **SENSITIVE** |
| 4 | 437 | Curated Public Test Suite construction | Testing | NON-SENSITIVE |
| 5 | 438 | CDL-050 opening (Treasury P_e stabilization) | Constitutional | **SENSITIVE** |
| 6 | 439 | CDL-050 prelock hardening | Constitutional | constitutional |
| 7 | 440 | CDL-050 ratification | Constitutional | **SENSITIVE** |
| 8 | 441 | Reserve slot for export-tree validation checks | Infrastructure | NON-SENSITIVE |
| 9 | 442 | Coherence + capsule v1.8 | Synthesis | NON-SENSITIVE |
| 10 | 443 | Closure gate | Gate | **SENSITIVE** |

### Conditional note on Phases 434-443
Because the dual obligations (Release Engineering and CDL-050) fit perfectly into a standard 10-phase span without compression, there are no explicitly conditional tail slots in this window. The sequence is treated as firm.

---

## 8. Sensitivity classification and Human GO requirements

**SENSITIVE phases (require `GO Phase NNN` human token before execution begins):**
- **Phase 434:** Sequence Lock (locks the window structure).
- **Phase 435:** Directly alters main-track `ilc_core/` runtime via cherry-pick.
- **Phase 436:** Merges public-facing documentation and executes bootstrap.
- **Phase 438:** Opens CDL-050 row (constitutional mutation).
- **Phase 440:** Ratifies CDL-050 (constitutional mutation).
- **Phase 443:** Closure gate (structural boundary).

**NON-SENSITIVE phases (no Human GO required):**
- **Phase 437:** Curating tests is a non-runtime, non-constitutional separation effort.
- **Phase 439:** CDL prelock (document-only hardening `constitutional`).
- **Phase 441:** Infrastructure reserve slot.
- **Phase 442:** Coherence synthesis and capsule formulation.

**Conditional phases rule:**
All phases in this window are firm. The standard sensitivity mapping applies statically.

**Pre-commit hook block:**
```
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=<phase>
```
Required for Phase 438 and Phase 440.

---

## 9. Scope notes for fixed phases (434-443)

### Phase 434 — Window sequence lock + Readiness Assessment

**SENSITIVE.** Requires `GO Phase 434` token.

**Deliverables:**
- `docs/specs/ilc_phase_434_443_sequence_lock_v0.1.md`
- `docs/specs/ilc_release_engineering_integration_readiness_434_v0.1.md`

**Required content spec:**
- Sequence lock: Window identity ("Release Engineering Bootstrap + Treasury P_e Stabilization"), locked phase table, CDL-050 mandate, merge-timing rule lock.
- Readiness assessment: Validates that the RE-08 gate passed and `release-engineering-track` is staged.

**Test structure:** 5+2 pre-commit split. Three-path commit resolver. 

**Pre-commit hook:** None (no CDL mutation or runtime).

**Commit subject:** `docs(g8): phase 434 window sequence lock and release engineering readiness`

---

### Phase 435 — Release Eng runtime cherry-pick merge

**SENSITIVE.** Requires `GO Phase 435` token.

**Deliverables:**
- `ilc_core/` modifications resulting strictly from cherry-picking the 4 designated runtime commits from the `release-engineering-track` branch.

**Test structure:** Custom test to verify the 4 commits are successfully integrated into the linear main history and `ilc_core/` tests pass.

**Commit subject:** `feat(g8): phase 435 release engineering runtime cherry-picks`

---

### Phase 436 — Release Eng packaging merge & initial export

**SENSITIVE.** Requires `GO Phase 436` token.

**Deliverables:**
- `out/public_export` directory (from merge).
- `tools/public_export_sync.py` and related toolchain scripts.

**Test structure:** Custom test to verify the public export artifact tree builds cleanly using the sync tool.

**Commit subject:** `build(g8): phase 436 release engineering packaging merge`

---

### Phase 437 — Curated Public Test Suite construction

**NON-SENSITIVE.** No GO token required.

**Deliverables:**
- A designated subset of `tests/` clearly marked or segregated as safe for public export.

**Commit subject:** `test(g8): phase 437 curated public test suite construction`

---

### Phase 438 — CDL-050 opening

**SENSITIVE.** Requires `GO Phase 438` token.

**Deliverables:**
- `docs/specs/ilc_cdl_050_treasury_pe_stabilization_opening_stub_438_v0.1.md`
- Constitutional mutation: one new row appended to `docs/specs/ilc_constitutional_decision_log_v0.1.md` for CDL-050 (`status: open`)

**Test structure:** 5+2 pre-commit split. Four-path commit resolver. Direct dict equality for all pre-existing rows.

**Pre-commit hook:** `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=438`

**Commit subject:** `docs(g8): phase 438 cdl-050 treasury pe stabilization opening`

---

### Phase 439 — CDL-050 prelock hardening

**NON-SENSITIVE.** No GO token required.

**Deliverables:**
- `docs/specs/ilc_cdl_050_treasury_pe_stabilization_prelock_hardening_439_v0.1.md`

**Required content spec:**
- CDL-050 open-state evidence anchor (Phase 438 commit).
- SIM-008 calibration data as the constitutional evidence basis.

**Test structure:** 5+2 pre-commit split. `assert_head_commit_touched_no_runtime_files` is valid.

**Commit subject:** `docs(g8): phase 439 cdl-050 treasury pe stabilization prelock hardening`

---

### Phase 440 — CDL-050 ratification

**SENSITIVE.** Requires `GO Phase 440` token.

**Deliverables:**
- `docs/specs/ilc_cdl_050_treasury_pe_stabilization_ratification_evidence_440_v0.1.md`
- CDL-050 row mutation: `status: open → ratified`, add `ratified_phase: 440`, `ratified_date`, `evidence_document`.
- `tests/test_phase_438_cdl_050_opening.py` — Phase 438 prelock test hardened.

**Test structure:** 7 tests (5+2 split). Custom 5-path commit resolver. 

**Pre-commit hook:** `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=440`

**Commit subject:** `docs(g8): phase 440 cdl-050 treasury pe stabilization ratification`

---

### Phase 442 — Coherence and capsule v1.8

**NON-SENSITIVE.** 

**Deliverables:**
- `docs/specs/ilc_integration_coherence_report_442_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v1.8.md`

**Commit subject:** `docs(g8): phase 442 coherence report and context capsule v1.8`

---

### Phase 443 — Closure gate

**SENSITIVE.** Requires `GO Phase 443` token.

**Deliverables:**
- `tools/check_window_434_443_closure_gate_phase_443.sh`
- `tests/test_window_434_443_closure_gate_443.py`
- `docs/specs/ilc_window_434_443_handoff_443_v0.1.md`

**Pre-commit hook:** None.

**Commit subject:** `docs(g8): phase 443 window 434-443 closure gate and 444-plus handoff`

---

## 10. Key dependencies and open questions

### Must be resolved at Phase 434 entry
- Phase 433 handoff carries the merged-timing rule for the release engineering track. This is the mandatory dependency for Phases 435 and 436.

### Sequencing constraints (non-negotiable)
- The 4 runtime commits MUST be cherry-picked onto `main` (Phase 435) BEFORE the packaging commits are merged (Phase 436). Failing to observe this order invalidates the integrity of the public source tree.
- CDL-050 must follow the strict opening-prelock-ratification order.

---

## 11. Known patterns and technical constraints

### Historical prelock hardening
After CDL-050 ratification, the Phase 438 prelock test must be hardened to assert `"status: open" in text` using a historical CDL reference (Phase-438 commit ref). 

### Pre-commit hook ilc_core/ clean-state guard
The pre-commit hook blocks CDL-authorized commits when any `ilc_core/` file differs from HEAD. For Phase 440 this guard must pass completely clean (no unexpected runtime changes).

### Closure gate selftest guard chain
The Phase 443 closure gate script must include selftest guards for all prior window gate tests in the regression chain. The full env setup for category 3 must include all windows from 337 to 433.

---

## 12. Non-goals and explicitly deferred items

The following are explicitly NOT in scope for Window 434-443:

- **Any modification to CDL-049:** Remains ratified as a historical constitutional artifact.
- **Immediate implementation of the P_e logic:** Phase 440 locks the constants, but the architectural wiring of the Treasury controller using these constants is deferred to a future implementation window. 
- **CDL-021 (Rust/WASM):** Deferred indefinitely.

---

## 13. Key canonical anchors for Window 434-443 prompt drafting

Codex should reference these in every Phase 434+ prompt:

- `docs/specs/ilc_antigravity_context_capsule_v1.7.md` — current context capsule (PRIMARY)
- `docs/specs/ilc_window_424_433_handoff_433_v0.1.md` — prior window closure handoff
- `docs/specs/ilc_phase_424_433_sequence_lock_v0.1.md` — prior sequence lock
- `docs/specs/ilc_constitutional_decision_log_v0.1.md` — CDL register
- `docs/phases/STATUS.md` — phase completion log
- `docs/specs/ilc_pe_stabilization_carry_forward_decision_431_v0.1.md` — Treasury P_e basis

For closure gate (Phase 443): all Phase 434-442 test files and artifacts.

---

## 14. Rationale for single-window scope

Window 434-443 is proposed as a single 10-phase candidate window because:

1. The Release Engineering merge is a multi-step operation (cherry-pick, merge, curate) that benefits from strict phase-isolation prior to constitutional CDL work.
2. The Treasury P_e (CDL-050) stabilization possesses a clear 3-phase structure backed by existing SIM-008 data, leaving no ambiguity for a multi-window spread.
3. The remaining slots comfortably accommodate infrastructure verification, coherence reporting, and the mandatory closure gate without introducing dangerous compression.
