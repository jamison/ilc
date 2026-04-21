# ILC Coherence Report 762 v0.1

**Phase:** 762  
**Window:** Mysticeti convergence window  
**Date:** 2026-04-21  
**Author:** Codex

## 1. Window verdict

The Mysticeti convergence window closes honestly with a mixed but coherent
result:

- `CW-1`: artifact re-verification passed,
- `CW-2`: row `5` runtime closure failed honestly and remains
  `spec_closed_runtime_pending`,
- `CW-3`: row `7` censorship-resistance runtime closure passed,
- `CW-4`: row `7` strong-exitability runtime closure passed,
- `CW-5`: Option B graduation-gate synthesis returned `no-go` with two explicit
  blockers,
- `CW-6`: closure surfaces now record the result without inflation.

Window-level conclusion:

- one row is fully closed at runtime (`row 7`),
- one honest fail is recorded (`row 5`),
- row `8` remains criteria-locked with no candidate evaluation,
- Option B remains not selectable,
- `CDL-017` remains open and unratified.

## 2. Phase-by-phase coherence

### 2.1 CW-1 — artifact re-verification

`CW-1` verified all three required convergence artifact classes:

- M-020 row-7 runtime bundle,
- M-021 `SIM-LEAKAGE-01` results,
- M-022 strong-exitability handoff evidence.

That gate was load-bearing and remained satisfied throughout `CW-2` through
`CW-6`.

### 2.2 CW-2 — row-5 runtime-closure evaluation

`CW-2` compared the committed M-021 leakage measurements against the Phase
`740` closure bands and recorded the honest fail:

- operator-path recall: `1.0 > 0.60`,
- hosted-query structural recall: `1.0 > 0.45`,
- repeated-contributor structural recall: `1.0 > 0.45`.

Row `5` therefore remains `spec_closed_runtime_pending`.

### 2.3 CW-3 and CW-4 — row-7 runtime closure

`CW-3` discharged the censorship-resistance side by checking the live
censoring-validator bundle against the Phase `741` Section `3.2` contract and
recording the required post-CRIT-001 framing:

- `EpochCheckpointMsg`, not `EpochSettlementTx`, carries the production
  evidence weight.

`CW-4` discharged the strong-exitability side by quoting physical evidence for:

1. export,
2. independent verify,
3. replay on a fresh node,
4. migration without original-operator consent.

Together these two phases moved row `7` to `runtime_closed`.

### 2.4 CW-5 — row-8 disposition and Option B gate synthesis

`CW-5` recorded the honest row-8 posture:

- criteria locked under Phase `673` plus Phase `675`,
- no specific substrate candidate evaluated,
- candidate evaluation still pending.

Against ADR-0028, the Option B gate therefore landed:

- row-7 proof obligations: `PASS`,
- row-8 candidate evaluation: `PENDING`,
- `CDL-017` ratification: `PENDING`,
- overall gate verdict: `no-go`.

That result is coherent with the convergence evidence rather than in tension
with it. Row `7` closure is a positive milestone; it is not sufficient by
itself to make Option B selectable.

## 3. Constitutional and runtime posture at close

At convergence close:

- row `7` is `runtime_closed`,
- row `5` remains `spec_closed_runtime_pending`,
- row `8` remains an inherited criteria lock with no candidate evaluation,
- `CDL-068` remains ratified from Phase `743`,
- `CDL-017` remains open and unratified,
- Option D remains the active posture under ADR-0028,
- no constitutional decision-log mutation occurred in this window,
- no `ilc_core/` or `ilc_consensus/` mutation occurred in this window.

The convergence window therefore consumed committed Gemini runtime evidence and
produced governance-side synthesis without introducing any new runtime or
constitutional mutation.

## 4. Track B verification and cross-lane posture

Track B was re-read from the live `STATUS.md` tail at execution start:

- `M-022` complete,
- convergence window next.

At close, the planning surfaces advance that live frontier honestly to:

- `M-022` remains complete,
- convergence window is now closed,
- the next lane is the later `CDL-017` ratification window, but only pending
  reviewer approval of `CW-5` and `CW-6`.

Cross-lane posture at close:

- Gemini delivered the runtime evidence required to test rows `5` and `7`,
- Codex consumed that evidence without softening the row-5 fail,
- the later `CDL-017` window remains sequenced after convergence,
- the later Option B route remains blocked by row-8 candidate evaluation and
  `CDL-017` ratification.

## 5. Carry-forward and reviewer gate

The remaining carry-forward is explicit and bounded:

1. row `5` privacy remediation:
   AgentID log-hygiene plus a real transfer-privacy layer capable of driving
   linkage recall below the inherited bands,
2. row `8` candidate evaluation:
   a concrete substrate candidate must be named and checked against the Phase
   `673` exclusion matrix and the Phase `675` lock,
3. `CDL-017` ratification:
   the later ratification window remains pending reviewer approval after review
   of `CW-5` and `CW-6`,
4. hypergraph Tier `2` and Tier `3` research carry-forward:
   Tier `1` substrate additions are complete, but the SIM-gated and
   CDL/patent-gated lanes remain deferred.

The convergence window closes cleanly because it was designed to produce an
honest row evaluation and Option B gate synthesis, not to force all remaining
gates to positive closure in one pass.
