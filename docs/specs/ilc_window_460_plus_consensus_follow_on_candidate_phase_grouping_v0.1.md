# ILC Post-468 Consensus Follow-on Candidate Phase Grouping

Author: GPT-5 Codex (planning draft)
Date: 2026-03-27
Current baseline: Window `450-459` is closed and Window `460-468` is now the active
candidate block for `CDL-052` scope freeze, gate clearing, and ratification.

Planning note: this is a deferred candidate grouping only. It does not amend the active
`460-468` candidate block, does not pre-authorize any post-`468` execution, and does not
override the active CDL-052-first posture already recorded for Window `460-468`.

This document is no longer the canonical immediate `460+` scheduling guide. It is retained as
background planning for a later post-`468` consensus follow-on lane.

---

## 1. Preferred planning posture

The next substantive consensus lane should not compete with the active CDL-052 window.

Use this split:
- Window `460-468` remains the main numbered track for CDL-052 scope freeze, gate clearing,
  and ratification.
- consensus follow-on work should either:
  - land as a narrow `Fix1` / `Fix2` prompt only if a bounded post-audit correction is needed,
    or
  - wait for a dedicated post-`468` consensus window if the work changes constitutional
    semantics, runtime behavior, or measurement scope in a material way.

Practical rule:
- use `Phase XXX Fix1/Fix2` nomenclature for corrective hardening,
- do not use `Fix1/Fix2` nomenclature to hide a new substantive consensus program.

---

## 2. Why a follow-on consensus lane still exists

Phase `446` proved the local prototype is fast and deterministic enough to move forward, but it
did not close the deeper consensus questions.

The main remaining gaps are:
- `CDL-V3` diversity-floor enforcement is still absent from the runtime finality path.
- measurement evidence is still local, single-process, and non-degraded.
- the bridge exercise is valid but bounded to a local JSON-path exercise.
- adversarial regression coverage is still incomplete for malformed quorum data, replay-like
  paths, epoch mismatches, candidate ambiguity, and cross-cluster concentration behavior.
- current timing wins are not the main bottleneck; governance correctness and quorum semantics are.

These are not cosmetic gaps. They are the natural next obligations after the first consensus
runtime tranche.

---

## 3. Fixpack versus new window rule

### Use a `Fix1` / `Fix2` phase only if all of the following are true

- the work is bounded corrective hardening to already-ratified `CDL-051` behavior,
- no new constitutional lane or new decision-log row is required,
- no new runtime subsystem is introduced,
- the work can be reviewed as a fixpack rather than a new tranche.

Examples that fit `Fix1` / `Fix2`:
- evidence-record alignment,
- test historicalization,
- environment-sensitive import cleanup,
- missing deterministic error token coverage,
- a narrow adversarial regression that hardens already-ratified behavior without expanding scope.

### Use a new post-`468` numbered lane if any of the following are true

- diversity-floor semantics change how finality is determined,
- new distributed or degraded-network measurement harnesses are introduced,
- bridge realism requires a broader transport exercise,
- the runtime contract expands beyond corrective hardening,
- new constitutional language or a `CDL-051` amendment is needed.

That is the likely case for most of the follow-on items below.

---

## 4. Candidate follow-on window theme after Window 460-468

Suggested title:
- **Window 469+: Consensus Diversity, Distributed Measurement, and Adversarial Hardening**

This lane should stay narrow:
- no CDL-052 spillover,
- no packaging/bootstrap work,
- no broad network-stack rewrite unless explicitly elevated,
- no unrelated governance compilation work unless separately authorized.

---

## 5. Candidate obligations to carry forward

### Obligation A - Diversity-floor enforcement

Purpose:
- translate the inherited `CDL-V3` diversity-floor concern into explicit consensus/runtime
  semantics,
- prevent flat aggregate quorum logic from being mistaken for constitutionally sufficient
  finality.

Expected output:
- one auditable contract stating whether finality needs cluster-diversity minima,
  anti-concentration rules, or both.

### Obligation B - Distributed measurement

Purpose:
- move from local single-process timings to multi-validator, multi-process, and
  degraded-network measurement,
- make the consensus evidence representative of actual distributed operation.

Expected output:
- a measurement contract and reproducible benchmark/report lane for non-local consensus runs.

### Obligation C - Bridge realism

Purpose:
- test a more realistic transport/bridge path than the bounded local `PeerManager` exercise,
- keep the scope bounded so the work does not silently become a native-P2P rewrite.

Expected output:
- a constrained adversarial bridge exercise with explicit non-goals.

### Obligation D - Adversarial coverage expansion

Purpose:
- add regression coverage for the cases that matter more than micro-optimization:
  malformed quorum data, epoch mismatches, replay-like paths, candidate ambiguity, and
  cross-cluster concentration behavior.

Expected output:
- an expanded adversarial regression suite and a findings artifact that states which cases are
  now closed and which remain open.

### Obligation E - Governance correctness priority

Purpose:
- preserve the priority rule that consensus correctness matters more than further sub-millisecond
  wins,
- prevent later work from optimizing the wrong thing.

Expected output:
- explicit phase language and handoff language stating that semantics, diversity, and auditability
  outrank raw micro-benchmark gains.

---

## 6. Candidate baseline grouping after Window 460-468

With Window `460-468` reserved for the CDL-052 lane, the earliest clean slot for a substantive
consensus follow-on is a later post-`468` window. A minimal candidate grouping is:

| Order | Candidate phase | Topic | Character | Sensitivity |
|-------|-----------------|-------|-----------|-------------|
| 1 | 469 | Consensus diversity-floor contract / amendment decision | Constitutional / Architecture | SENSITIVE |
| 2 | 470 | Runtime diversity-floor enforcement in finality evaluation | Runtime | SENSITIVE |
| 3 | 471 | Distributed and degraded-network measurement harness | Runtime / Tooling / Measurement | SENSITIVE |
| 4 | 472 | Bridge-realism and adversarial transport exercise | Runtime / Adversarial | SENSITIVE |
| 5 | 473 | Expanded adversarial regression hardening + findings memo | Review / Stabilization | SENSITIVE |
| 6 | 474 | Closure gate and next-handoff | Gate | SENSITIVE |

This is intentionally smaller than Window `441-449`.

If later evidence shows that diversity-floor work alone is much larger than expected, split the
window rather than overloading a single phase.

---

## 7. Interaction with `Fix1` / `Fix2` nomenclature

Recommended naming rule:
- `446 Fix1` / `446 Fix2` or `447 Fix1` / `447 Fix2` remain available for bounded corrective
  hardening discovered during audits,
- but the candidate `460+` work above should not be disguised as `446 Fix3` or `447 Fix3`.

Reason:
- the follow-on items are not patch-level cleanup,
- they change what the consensus prototype must prove,
- and some may require constitutional clarification before runtime changes are legitimate.

Short version:
- narrow correction -> `Fix1` / `Fix2`,
- new semantic or runtime tranche -> new numbered lane.

---

## 8. Recommended current stance

For now:
- keep the new obligations recorded as planning/TODO material,
- keep Window `460-468` focused on the CDL-052 gate-and-ratification lane,
- allow only bounded consensus fixpacks during that active CDL-052 window if an audit finds a real
  corrective gap,
- queue the substantive consensus follow-on as a post-`468` candidate lane.

That is the cleanest way to preserve both priorities:
- close the CDL-052 constitutional lane cleanly,
- and avoid losing the important consensus follow-on work identified after Phase `446`.
