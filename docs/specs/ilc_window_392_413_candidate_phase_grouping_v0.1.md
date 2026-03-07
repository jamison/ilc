# ILC Window 392-413: Candidate Phase Grouping

**Author:** Claude Sonnet 4.6 (local architectural reviewer)
**Date:** 2026-03-07
**Baseline:** Window 378-391 IN PROGRESS (Phase 380 prompt committed). Phase 391 will close on CDL-039 ratification, D2d wire protocol, CDL-040/041/043 prelocks, SIM-006/007, CDL-V1/V2 runtime, capsule v1.3.

---

## 1. Track inventory arriving from Phase 391

### Constitutionally obligated (non-negotiable)

- `retention_epochs` CDL amendment — must be opened as the *first constitutional action* of Window 392+ (ratification evidence obligated by Phase 379)
- CDL-040 ratification — prelock complete (Phase 383), fully unblocked
- CDL-041 ratification — prelock complete (Phase 384), fully unblocked
- CDL-043 ratification — prelock complete (Phase 385), fully unblocked

### Unlocked and queueing

- CDL-042 opening (agent identity namespace) — deferred from 378-391 by CDL-039/040 scope dependency; that dependency resolves at Phase 391 close
- CDL-044 opening (operational emergency response) — SIM-005 results available since Phase 370
- CDL-035 timed_out amendment — SIM-007 results available from Phase 386

### Conditionally authorized (SIM-006 outcome from Phase 386)

- CDL-V3 governance resolution + runtime (cluster diversity floor)
- CDL-V7 governance resolution + runtime (Popperian gate)
- If SIM-006 result is unfavorable: another SIM round; these remain `requires_additional_governance_input`

### Long-deferred, now unblocked

- D2e Agent SDK/CLI — CDL-032, D2e-01 through D2e-11 (blocked on node schema + wire transport runtimes; those are done at Phase 391 close)

---

## 2. Candidate Window 392-401: "Ratification Settlement + V-series Resolution" (10 phases)

| Phase | Topic | Character |
|---|---|---|
| 392 | Seq lock + `retention_epochs` CDL amendment open | Foundation / Constitutional (first action) |
| 393 | CDL-040 ratification (admission control + identity envelope) | Constitutional |
| 394 | CDL-041 ratification (shard lifecycle) | Constitutional |
| 395 | CDL-043 ratification (storage economics) | Constitutional |
| 396 | CDL-V3/V7 governance authorization lock (SIM-006 evidence synthesis) | Authorization |
| 397 | CDL-V3 runtime (cluster diversity floor enforcement) | Runtime |
| 398 | CDL-V7 runtime (Popperian gate) | Runtime |
| 399 | `retention_epochs` evidence assembly + ratification | Constitutional |
| 400 | Coherence + capsule v1.4 | Synthesis |
| 401 | Closure gate | Gate |

### Conditional note on Phases 397-398

If Phase 396 declares CDL-V3/V7 still `requires_additional_governance_input` (unfavorable SIM-006), these phases are replaced by an SIM-008 commissioning (another simulation round with SIM-006 results as input) and a CDL-042/CDL-044 prelock pair. Window 401 closure would carry V-series runtime forward to Window 402+.

### Structural note on Phase 399

The `retention_epochs` amendment follows the CDL-039 lifecycle pattern — opened Phase 392, evidence assembled across Phases 393-398 while other work proceeds, ratified Phase 399. The 7-phase open-to-ratify gap is tighter than CDL-039's 20-phase gap but comparable to CDL-034's 9-phase gap. The evidence is narrower (a single operational parameter), so this is achievable.

---

## 3. Candidate Window 402-413: "Constitutional Expansion + D2e First Block" (12 phases)

| Phase | Topic | Character |
|---|---|---|
| 402 | Seq lock + CDL-042 opening + CDL-044 opening (two-CDL opening batch) | Foundation |
| 403 | CDL-042 prelock hardening (agent identity namespace) | Constitutional |
| 404 | CDL-044 prelock hardening (operational emergency response) | Constitutional |
| 405 | CDL-035 timed_out amendment open + prelock (SIM-007 evidence) | Constitutional |
| 406 | SIM-008/009 commissioning (CDL-V3/V7 follow-on if deferred from Window 401) | Simulation |
| 407 | CDL-042 ratification | Constitutional |
| 408 | CDL-044 ratification | Constitutional |
| 409 | CDL-035 timed_out ratification | Constitutional |
| 410 | D2e Agent SDK — Part 1 (D2e-01 through D2e-05: identity, query, verify) | Runtime |
| 411 | D2e Agent SDK — Part 2 (D2e-06 through D2e-11: bundle, epoch, balance, integration) | Runtime |
| 412 | Coherence + capsule v1.5 | Synthesis |
| 413 | Closure gate | Gate |

### Note on Phase 406

This is a conditional slot — used for a V-series SIM follow-on if Window 401 deferred CDL-V3/V7, or it becomes a CDL-V3/V7 runtime authorization lock if Window 401 resolved them. In the positive case (V-series resolved in Window 401), Phase 406 might be the CDL-V3/V7 runtime ramp-up scope declaration or a third D2e block.

---

## 4. Key dependencies and open questions

### Must be resolved at Phase 391 closure

- SIM-006 outcome verdict (unlocks the CDL-V3/V7 branch in Window 392+)
- `retention_epochs` forward obligation token in handoff (required by Phase 391 gate check)

### Sequencing constraints (non-negotiable)

- Phase 392 must be the `retention_epochs` amendment opening — this is constitutional
- CDL-040/041/043 ratifications (Phases 393-395) must come before CDL-042 is opened — CDL-042's identity namespace depends on CDL-040 admission control scope being ratified, not just prelock-complete
- D2e (Phases 410-411) is gated on CDL-042 opening existing — D2e identity subsystem references agent identity namespace — hence deferred to Window 402+

### Permanently deferred

- CDL-V4/V5/V6: governance-procedural-only, implementation-barred (no change in either window)
- CDL-021: Rust/WASM (defer indefinitely)

---

## 5. Rationale for two-window split

Window 392-401 clears the ratification debt and conditionally clears the V-series runtime debt. Window 402-413 opens the new constitutional expansion layer and begins D2e. The two-window split is preferable to a single 14-phase block because the CDL-V3/V7 conditional branch creates genuine uncertainty: if SIM-006 is unfavorable, Phases 397-398 need to be restructured, which is easier to absorb within a 10-phase window boundary than mid-stream in a 14-phase window.
