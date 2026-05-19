# Window 1369–1390 Track Addendum: SIM-GENESIS-COMPILE-02

**Addendum version:** v0.1  
**Date:** 2026-05-19  
**Window:** 1369–1390  
**Status:** Proposed — pending human review before execution

---

## 1. Purpose of This Addendum

Window 1369–1390 was opened as a public claimability governance window. This addendum adds
a single NON-SENSITIVE SIM track — `SIM-GENESIS-COMPILE-02` — to address two accumulated
technical debts that have been visible since Phase 1339:

1. Dirty `out/` diagnostic files representing an uncommitted re-run of the genesis compiler
   (2 new source files classified; structural metrics unchanged).
2. A `PARTIAL_WITH_STRUCTURAL_GAPS` verdict on the genesis node compilation that has not
   been examined or improved since Phase 1339.

This track is independent of the SENSITIVE phases remaining in the window (1387a, 1388, 1389)
and can execute before or in parallel with them.

---

## 2. Track Inventory

| Track | Phase | Sensitivity | Gate |
|-------|-------|-------------|------|
| SIM-GENESIS-COMPILE-02 | 1387b (proposed) | NON-SENSITIVE | Human review of guidance + prompt |

Phase 1387b is proposed as a NON-SENSITIVE phase that may execute after this addendum is
reviewed and approved. It does not require `GO Phase 1387b` beyond the normal prompt-review
approval, but follows the standard workflow: guidance → prompt → execution → walkthrough.

Phase 1387a (public-only economics admission firewall, SENSITIVE) remains a separate track
requiring its own `GO Phase 1387a`. The lettering (1387b before 1387a execution) reflects
priority of readiness, not a sequencing dependency.

---

## 3. Baseline

| Item | Current state |
|------|--------------|
| Last genesis compiler run committed | Phase 1339 (`9d7e5210` area) |
| Dirty `out/` files (unstaged) | 5 files; +2 observed sources; all structural metrics unchanged |
| Diagnostic verdict | `PARTIAL_WITH_STRUCTURAL_GAPS` |
| `core_nodes_total` | 32 |
| `basis_reachable_core_nodes` | 17 / 32 (53.1%) |
| `authority_traceable_core_nodes` | 31 / 32 (96.9%) |
| Candidate manifest | 56 nodes (`genesis_node_candidates_v0.2_candidate.json`) |
| ADR-0035 spec doc | **Missing** — direction accepted, spec never written |
| `missing_decomposition_recipes` | 0 |

---

## 4. Scope of SIM-GENESIS-COMPILE-02 (Phase 1387b)

### 4.1 In scope

- Canonize the dirty `out/` files: commit updated counts reflecting repo growth since Phase 1339,
  with a record that structural metrics (basis-reachable, authority-traceable, verdict) are unchanged.
- Classify the 15 basis-unreachable core nodes into structural categories and produce a written
  disposition for each (bootstrap axiom vs. post-genesis governance vs. architecture overlay vs.
  governance-set parameter).
- Determine whether the transition basis should be expanded by the 3 bootstrap-axiom nodes
  (genesis agent pubkey record, keygen ceremony, intent attestation root) and what the revised
  basis-reachable count would be.
- Assess whether the 6 heavily-referenced governance ADRs absent from the core star map
  (ADR-0001/0002/0003/0005/0006/0008 — highest is ADR-0008 at 120+ mentions) warrant core
  inclusion or remain correctly outside.
- Produce a disposition for ADR-0035 (homoiconic type definition system): either a minimal
  spec or a formal deferral record with a completion criterion.
- Update the diagnostic verdict if the analysis supports a more precise classification.

### 4.2 Explicitly out of scope

- No CDL register mutation.
- No `ilc_core/` runtime modification.
- No public-facing surface activation.
- No new node candidates added to the manifest (analysis only; manifest changes would require
  a separate SENSITIVE phase with CDL-authority backing if they touch the Genesis attestation root).
- No claim that the genesis compilation is "COMPLETE" unless the evidence unambiguously supports it.
- ADR-0035 implementation — if the spec is drafted, it is a spec artifact only; runtime
  implementation is a separate future phase.

---

## 5. CDL Number Assignments

None. This phase does not open, prelock, or ratify any CDL.

---

## 6. Candidate Phase Table

| Order | Phase | Topic | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 1387b | SIM-GENESIS-COMPILE-02: genesis node compilation review | SIM / spec | NON-SENSITIVE |

---

## 7. Sensitivity Classification

**NON-SENSITIVE list:** Phase 1387b  
**SENSITIVE list:** (none in this addendum)

Phase 1387b does not touch the CDL register, does not modify `ilc_core/` runtimes, does not
activate any public or production surface, and does not require CDL mutation authority.
It may produce a spec artifact for ADR-0035 and a written disposition document.

---

## 8. Key Dependencies and Open Questions

**Dependencies:**
- `out/genesis_compile_coverage_diagnostic_v0.1.json` (current uncommitted state)
- `out/genesis_node_candidates_v0.2_candidate.json` (56-node manifest)
- `tools/genesis_compile_coverage_diagnostic.py` (compiler tool)
- `tools/crawl_genesis_node_candidates.py` (candidate crawler)
- `docs/adr/ADR_0033_Star_Map_Homoiconic_Epistemiological_Entity.md` (homoiconicity basis)
- Phase 1339 walkthrough (last compile pass evidence)

**Open questions to resolve:**
1. Should the transition basis be expanded to include genesis bootstrap artifacts as axiomatic
   inputs rather than derived nodes? If so, what does the revised basis-reachable metric become?
2. Is the current `PARTIAL_WITH_STRUCTURAL_GAPS` verdict a permanent steady-state (because
   post-genesis governance nodes are correctly outside the genesis derivation chain), or is it
   a gap that should close toward `COMPILE_COMPLETE`?
3. Is ADR-0035 (homoiconic type definition system) a near-term spec obligation, or can it be
   formally deferred to the post-RC architecture series?

---

## 9. Non-Goals and Explicitly Deferred Items

- Genesis star map activation — this SIM produces analysis, not activation.
- ADR-0035 runtime implementation — spec only (if written).
- CDL-088 public claimability — entirely separate track.
- Expansion of the candidate manifest beyond 56 nodes — analysis only.
