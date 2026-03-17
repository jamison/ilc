# ILC Window 434+: Flexible Candidate Phase Grouping

**Author:** GPT-5 Codex (independent planning draft)
**Date:** 2026-03-17
**Baseline:** Window 424-433 CLOSED (Phase 433 verdict: pass). `CDL-049` ratified. Treasury `P_e` stabilization carried forward under Scenario B. Release-engineering runtime tranche identified. Capsule v1.7 current.
**Planning note:** This document is a candidate grouping, not a locked sequence. A fixed 10-phase window is not a protocol requirement. The correct window size is whatever preserves lane discipline without speculative phase padding or unsafe compression.

---

## 1. Planning posture

Window planning should follow the actual dependency graph, not a habit of filling ten slots.

For the current state, the disciplined baseline is:
- a **numbered main-track runtime tranche** in Window 434+,
- a **non-ratifying Treasury `P_e` readiness review** before any new CDL opening,
- a **parallel release-engineering packaging/bootstrap track** that remains outside numbered constitutional phases unless governance explicitly changes that rule.

Recommended default shape:
- **baseline window:** 7 phases,
- **extendable window:** 8-10 phases only if mid-window evidence justifies it,
- **not recommended:** locking a 10-phase constitutional/infrastructure sequence up front before the Treasury `P_e` prerequisites are satisfied.

---

## 2. Settled inheritance from Window 424-433

The following is already settled and must not be reopened casually:

- `CDL-049` is ratified.
- `CDL-050` was **not** opened in Window 424-433.
- Treasury `P_e` trigger and limit constants remain **unratified**.
- The pair `0.2 / 0.02` is a **provisional planning anchor only**, not a constitutional lock.
- Window 434+ may advance the Treasury `P_e` constitutional lane only after satisfying at least one Phase 431 prerequisite:
  - a recovery criterion decoupled from the trigger threshold,
  - an explicit treasury-risk tolerance judgment,
  - additional simulation evidence that discriminates intervention-limit trade-offs.
- Window 434+ must cherry-pick the release-track runtime tranche before any public repo packaging commits are merged.
- Release engineering remains a **parallel administrative track**, not a numbered constitutional lane, unless that rule is explicitly revised.

---

## 3. Track inventory arriving at Window 434+

### Track A — Main-track runtime tranche

This is the strongest immediate main-track candidate for numbered phases.

Current runtime tranche inherited from the release-engineering handoff:
- `ilc_core/network/peer.py` — real HTTP peer fanout bridge,
- `ilc_core/cli/main.py` — CLI refactor tied to the runtime tranche,
- `ilc_core/node/node_dissemination_runtime_362.py` — dissemination runtime carry-in,
- `tools/runtime_baseline.py` — benchmark harness.

This tranche belongs on `main` with clear attribution and must not arrive as an opaque bulk packaging merge.

### Track B — Treasury `P_e` constitutional readiness

This track is **not yet** a firm `CDL-050` lane.

What is authorized now:
- assess whether any Phase 431 prerequisite has actually been satisfied,
- decide whether `CDL-050` can be opened cleanly,
- otherwise keep Treasury `P_e` as a carry-forward item.

What is **not** authorized now:
- treating `SIM-008` as sufficient for Treasury `P_e` locking,
- treating `0.2 / 0.02` as ratification-ready,
- pre-authorizing `CDL-050` before the prerequisite review is complete.

### Track C — Release-engineering packaging/bootstrap

This track remains parallel administrative work.

It should continue to own:
- allowlist/manifest updates,
- export/sync tooling,
- public repo bootstrap method,
- packaging checklist and staged export validation.

It should **not** consume numbered main-track phases by default.

---

## 4. Recommended baseline window: 434-440 (7 phases)

This is the recommended default grouping.

| Order | Phase | Topic | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 434 | Sequence lock + runtime tranche intake freeze | Foundation / Control | **SENSITIVE** |
| 2 | 435 | Runtime tranche I: peer fanout integration | Runtime | **SENSITIVE** |
| 3 | 436 | Runtime tranche II: benchmark harness + tranche completion | Runtime / Tooling | **SENSITIVE** |
| 4 | 437 | Runtime tranche findings memo and regression hardening | Review / Stabilization | NON-SENSITIVE |
| 5 | 438 | Treasury `P_e` prerequisite-satisfaction review | Governance review | NON-SENSITIVE |
| 6 | 439 | Coherence + capsule v1.8 | Synthesis | NON-SENSITIVE |
| 7 | 440 | Closure gate + next-window handoff | Gate | **SENSITIVE** |

This 7-phase baseline does **not** open `CDL-050`.

That is intentional. It matches the current evidence state rather than pretending the constitutional lane is already ready.

---

## 5. Phase-by-phase intent for the 7-phase baseline

### Phase 434 — Sequence lock + runtime tranche intake freeze

**SENSITIVE.**

Purpose:
- lock the Window 434+ baseline around the runtime tranche first,
- record the release-track merge-timing rule,
- freeze the exact runtime tranche import set by commit hash or by an exact qualifying path set,
- explicitly keep packaging/bootstrap outside numbered phases.

Required outputs should include:
- `docs/specs/ilc_phase_434_440_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_434_runtime_tranche_intake_434_v0.1.md`

Phase 434 must not assume that every release-track change belongs in the numbered window. It should isolate the runtime tranche from the packaging tranche.

### Phase 435 — Runtime tranche I

**SENSITIVE.**

Purpose:
- land the first runtime tranche subset on `main`,
- prioritize observable distributed-execution progress over release-surface administration.

Recommended first priority:
- `ilc_core/network/peer.py` real delivery attempts,
- any directly required caller/interface adjustments.

This phase should use exact path-scoped runtime mutation checks, not generic no-runtime guards.

### Phase 436 — Runtime tranche II

**SENSITIVE.**

Purpose:
- land `tools/runtime_baseline.py`,
- finish the remaining runtime tranche wiring needed for a coherent benchmarkable path,
- address code-health hotspots tripped by the tranche.

This phase is still runtime work, even if one output lives under `tools/`.

### Phase 437 — Runtime tranche findings memo and regression hardening

**NON-SENSITIVE.**

Purpose:
- consolidate what actually landed in Phases 435-436,
- record measured behavior and open runtime gaps,
- harden any pre-tranche tests that need historicalization or path-scope tightening.

This phase should not become a vague planning tree. It is a findings memo plus test hardening only.

### Phase 438 — Treasury `P_e` prerequisite-satisfaction review

**NON-SENSITIVE.**

Purpose:
- decide whether any Phase 431 prerequisite has been satisfied strongly enough to justify a future `CDL-050` opening,
- explicitly state one of the following outcomes:
  1. `CDL-050` still not justified,
  2. `CDL-050` opening is justified in the next window,
  3. a narrow non-CDL follow-up is needed first.

This phase is the constitutional decision point. It is not itself an opening or ratification phase.

### Phase 439 — Coherence + capsule v1.8

**NON-SENSITIVE.**

Purpose:
- consolidate the Window 434+ runtime tranche state,
- record the Treasury `P_e` review outcome,
- keep release-track packaging/bootstrap explicitly outside the numbered window unless governance changed.

### Phase 440 — Closure gate + handoff

**SENSITIVE.**

Purpose:
- close the runtime tranche window cleanly,
- verify the runtime tranche landed with the promised separation from packaging work,
- hand off the Treasury `P_e` outcome and release-track merge state to the next window.

---

## 6. Extension rule: only grow the window if the evidence justifies it

If Phase 438 concludes that a future `CDL-050` opening is justified, there are two disciplined options:

### Option A — Keep Window 434-440 lean

Recommended default.

- Close Window 434-440 at Phase 440.
- Start a new window for the constitutional lane.
- Use the next window for `CDL-050` opening, prelock, and ratification.

### Option B — Extend the current window to 443

Acceptable only if Phase 438 makes the case explicitly and a sequence-lock amendment is written.

Extension shape:
- Phase 441 — `CDL-050` opening (**SENSITIVE**)
- Phase 442 — `CDL-050` prelock hardening (NON-SENSITIVE)
- Phase 443 — `CDL-050` ratification or closure gate depending on the amendment design (**SENSITIVE**)

Do **not** pre-allocate this extension before Phase 438. The extension is conditional, not assumed.

---

## 7. Release-engineering policy for Window 434+

Release engineering should remain outside numbered phases unless the operator deliberately changes that rule.

That means:
- public export staging,
- allowlist changes,
- public repo bootstrap method,
- packaging checklists,
- public test-surface curation,

should continue on the release-engineering track as administrative work.

The numbered main-track window only needs to care about two release-track facts:
1. the runtime tranche must be imported with clear attribution and separated from packaging commits,
2. the closure/handoff must confirm that packaging commits were **not** merged ahead of the runtime tranche.

This is the minimum coupling needed between the two lanes.

---

## 8. Treasury `P_e` constraints for any future `CDL-050` lane

If `CDL-050` ever opens, its evidence basis must come from the settled Phase 430/431 record, not from a retroactive claim that `SIM-008` was sufficient all along.

Any future `CDL-050` opening must explicitly address:
- why the trigger-coupled recovery criterion no longer invalidates a lock attempt,
- how the intervention-limit sub-choice is being distinguished beyond the weak `0.20` cluster,
- whether the decision depends on new simulation evidence, an explicit treasury-risk tolerance judgment, or both.

Without that, `CDL-050` remains premature.

---

## 9. Sensitivity mapping

Recommended sensitivity map for the baseline 7-phase window:
- **SENSITIVE:** 434, 435, 436, 440
- **NON-SENSITIVE:** 437, 438, 439

Rationale:
- sequence locking and closure gates remain sensitive,
- direct runtime tranche imports from the release track should be treated as sensitive,
- review/synthesis phases remain non-sensitive until they mutate constitutional or runtime state.

---

## 10. Canonical anchors for prompt drafting

Prompt authors should anchor Window 434+ work to:
- `docs/specs/ilc_window_424_433_handoff_433_v0.1.md`
- `docs/specs/ilc_pe_stabilization_carry_forward_decision_431_v0.1.md`
- `docs/specs/ilc_sim_009_results_synthesis_and_pe_stabilization_disposition_430_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v1.7.md`
- `docs/phases/STATUS.md`

At Phase 434 entry, the operator should also provide the current release-track runtime tranche handoff and merge-note context so the exact import set can be frozen locally on `main`.

If Phase 434 freezes an exact runtime tranche commit list, that artifact becomes the primary resolver anchor for Phases 435-440.

---

## 11. Rationale for the flexible grouping

This plan is intentionally not a forced 10-phase tree.

Reasons:
1. The strongest justified next step is the runtime tranche, not immediate `CDL-050` ratification planning.
2. Treasury `P_e` is still in a prerequisite-satisfaction state, not a ratification-ready state.
3. Release engineering already has a separate administrative lane; folding it wholesale into numbered phases adds governance noise without improving safety.
4. A 7-phase baseline keeps the next window honest. If the evidence later supports a constitutional extension, the window can be extended deliberately rather than padded speculatively on day one.

**Recommendation:** Use this 7-phase Window 434-440 baseline as the default planning source of truth, and treat any move to 441+ as a later amendment, not an assumption.
