# ILC Window 441+: Candidate Phase Grouping

Author: GPT-5 Codex (independent planning draft)
Date: 2026-03-18
Baseline: Window 434-440 CLOSED (Phase 440 verdict: pass). The numbered runtime tranche is complete. `CDL-049` remains ratified. `CDL-050` remains unopened and not pre-authorized. Public packaging/bootstrap remains on the parallel release-engineering track.
Planning note: this is a candidate grouping, not a locked sequence. The window should follow dependency order, not a fixed ten-phase template.

---

## 1. Preferred planning posture

My preferred next window is a **constitutional-first consensus and epoch-finality block**, not a Treasury `P_e` window and not a packaging window.

Reasoning:
- the mainline now has a real network bridge (`ilc_core/network/peer.py`) and a benchmark harness (`tools/runtime_baseline.py`),
- Treasury `P_e` remains blocked by prerequisites that were not satisfied in Phase 438,
- packaging/bootstrap is explicitly outside numbered phases,
- the highest-leverage missing system primitive is still distributed agreement / epoch finality,
- if consensus logic is going to land on `main`, its governing rules must be constitutionally ratified before runtime implementation,
- consensus semantics are safer to prototype over transparent JSON-first state than while simultaneously forcing a storage-format cutover.

Recommended default shape:
- baseline window: **9 phases**,
- no pre-allocation of a Treasury constitutional lane in the same window,
- no release-packaging work on the numbered main track,
- no production DAG-CBOR cutover in the baseline window.

---

## 2. Settled inheritance from Window 434-440

The following is already settled and should be treated as inherited boundary state:
- `CDL-049` is ratified and unaffected.
- `CDL-050` was not opened in Window 434-440.
- Treasury `P_e` trigger and limit constants remain unratified.
- Phase 438 concluded that all three Phase-431 prerequisites remain unsatisfied.
- the numbered runtime tranche authorized by Phase 434 completed in Phases 435 and 436.
- release-track runtime work landed on `main` before any packaging merge.
- public packaging/bootstrap remains a parallel administrative track.
- any move beyond Window 434-440 requires a new sequence lock or amendment.

Implication:
- the next numbered window should not assume Treasury work is next by default,
- the next numbered window should not spend scarce phase slots on release packaging,
- the next numbered window should constitutionally ground any new consensus runtime before implementation.

---

## 3. Preferred next-window theme

### Theme: Constitutional Consensus and Epoch-Finality Block

This window should answer one narrow question:

Can the project constitutionally define and then implement a deterministic, auditable epoch-finality / quorum-state path on top of the newly landed network bridge and runtime harness, without reopening Treasury governance or entangling storage-format migration?

This is the right next block because:
- Treasury `P_e` eventually needs stronger system-level execution assumptions than the current local-only state model,
- the system now has enough runtime surface to measure consensus-path behavior meaningfully,
- DAG-CBOR production cutover is important, but it is more safely done after the semantics of the consensus path are stable,
- release packaging progress can continue in parallel and does not need numbered main-track phases,
- existing ratified surfaces (`CDL-V3`, `CDL-039`, `CDL-040`, `CDL-045`) provide useful inherited constraints but do not yet define a full epoch-finality engine.

---

## 4. Recommended baseline window: 441-449 (9 phases)

Suggested title:
- **Window 441-449: Constitutional Consensus and Epoch-Finality Block**

| Order | Phase | Topic | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 441 | Sequence lock + `CDL-051` opening | Foundation / Constitutional | SENSITIVE |
| 2 | 442 | `CDL-051` prelock hardening | Constitutional | SENSITIVE |
| 3 | 443 | `CDL-051` ratification | Constitutional | SENSITIVE |
| 4 | 444 | Consensus runtime I: epoch-state and quorum-record surfaces | Runtime | SENSITIVE |
| 5 | 445 | Consensus runtime II: deterministic finality evaluator and fork-resolution rules | Runtime | SENSITIVE |
| 6 | 446 | Consensus runtime III: harness integration, network-bridge exercise, and bounded hotspot cleanup | Runtime / Tooling | SENSITIVE |
| 7 | 447 | Consensus findings memo and adversarial regression hardening | Review / Stabilization | SENSITIVE |
| 8 | 448 | Coherence + capsule v1.9 | Synthesis | NON-SENSITIVE |
| 9 | 449 | Closure gate + 450+ handoff | Gate | SENSITIVE |

This baseline intentionally does **not** open `CDL-050`.

Note on numbering:
- consensus should use `CDL-051` or later,
- `CDL-050` remains notionally reserved for the Treasury `P_e` lane if that lane is ever constitutionally opened.

---

## 5. Phase-by-phase scope

### Phase 441 - Sequence lock + `CDL-051` opening

Purpose:
- lock the window around a consensus lane,
- open the new consensus constitutional row,
- explicitly preserve Treasury `P_e` non-authorization,
- explicitly preserve the release-engineering boundary,
- explicitly defer DAG-CBOR production cutover to a later window unless a hard blocker emerges.

Required boundaries:
- no `CDL-050` opening,
- no Treasury constant locking,
- no packaging/bootstrap merge work,
- no full storage-format migration,
- no transport rewrite that forecloses native P2P replacement.

### Phase 442 - `CDL-051` prelock hardening

Purpose:
- define the constitutional state machine for the consensus prototype,
- lock the epoch-state and quorum-record structures that runtime will later implement,
- define deterministic fork/tie-break categories and explicit non-goals,
- document which constants are ratified law versus prototype-local defaults.

Scope guidance:
- this phase should state exactly what finality means,
- it should identify the admissible conflict states and the deterministic resolution rule family,
- it should avoid algorithmic sprawl beyond the minimum needed to ratify a runtime lane cleanly.

### Phase 443 - `CDL-051` ratification

Purpose:
- ratify the consensus prototype constitutional surface,
- lock the governing contract that later runtime phases must implement,
- harden all opening/prelock tests in the normal constitutional pattern.

Scope guidance:
- do not implement runtime here,
- do not smuggle in Treasury or storage-format work,
- make explicit what remains intentionally unratified.

### Phase 444 - Consensus runtime I: epoch-state and quorum-record surfaces

Purpose:
- implement the ratified epoch-state and quorum-record surfaces,
- keep the contract machine-auditable,
- keep prototype defaults clearly separated from ratified constants.

Scope guidance:
- focus on state objects, transitions, and provenance,
- no broad architectural rewrite,
- no DAG-CBOR cutover in this phase.

### Phase 445 - Consensus runtime II: deterministic finality evaluator and fork-resolution rules

Purpose:
- land the actual deterministic evaluation path for epoch-finality / quorum-state progression,
- implement deterministic tie-break and fork-resolution logic for conflicting quorum states,
- preserve behavioral determinism under fixed inputs.

Scope guidance:
- JSON-first / transparent state is acceptable and preferred here,
- the phase must not be happy-path only,
- conflict resolution must be explicit, testable, and deterministic.

### Phase 446 - Consensus runtime III: harness integration, network-bridge exercise, and bounded hotspot cleanup

Purpose:
- exercise the consensus path through the existing runtime harnesses,
- connect the new prototype to the current network bridge or local multi-node harness where needed,
- clean up only the code-health hotspots directly caused by the tranche.

Scope guidance:
- extend measurement/reporting so the tranche yields concrete timing and behavior evidence,
- do not use this phase to reopen unrelated runtime areas,
- do not convert the window into a native-P2P transport program.

### Phase 447 - Consensus findings memo and adversarial regression hardening

Purpose:
- record what the prototype actually proves,
- document failure modes, missing measurements, and unresolved assumptions,
- add or tighten adversarial regression guards required by the tranche.

Scope guidance:
- findings memo, not planning sprawl,
- regression hardening only where the new tranche exposed a concrete gap,
- explicitly state what remains unimplemented,
- treat the phase as sensitive because it touches security-significant guardrails.

### Phase 448 - Coherence + capsule v1.9

Purpose:
- consolidate the post-440 runtime tranche plus the new consensus state,
- preserve Treasury `P_e` carry-forward and `CDL-050` non-authorization,
- preserve release-engineering separation.

### Phase 449 - Closure gate + 450+ handoff

Purpose:
- close the consensus block cleanly,
- verify no accidental Treasury authorization occurred,
- publish the next-window pointer based on actual findings.

---

## 6. Sooner-rather-than-later anti-refactor tasks

These are the main anti-refactor tasks I would queue early to avoid avoidable rework later in the consensus lane.

### 6.1 Governance-source taxonomy

Before runtime implementation, publish a small taxonomy that classifies new consensus surfaces as one of:
- `kernel_resident`,
- `graph_compiled`,
- `runtime_derived`,
- `operator_local`.

This prevents constants and policy surfaces from being scattered ad hoc across runtime code.

### 6.2 Prototype-default provenance

Require any new consensus constant or rule-like default introduced in runtime phases to carry a traceable provenance note:
- ratified source,
- prelock source,
- prototype-local default,
- or operator-local override.

This is the cheapest way to avoid future archaeology and policy drift.

### 6.3 Deterministic tie-break vocabulary

Define the canonical terminology for:
- fork,
- conflicting quorum state,
- stale quorum state,
- superseding quorum state,
- tie-break rule,
- finality decision.

Do this before runtime phases so tests, docs, and code do not diverge semantically.

### 6.4 Graph-native compilation boundary

Record the future architectural boundary for graph-native governance compilation now, even if implementation is later:
- keep a small audited kernel,
- move bounded declarative rules and governance constants toward graph-native compilation,
- do not treat core imperative runtime as graph-defined by default.

This reduces the risk of building the next few windows around assumptions that will later be reversed.

### 6.5 Measurement provenance in harness outputs

Extend any new consensus harness/report output so it can distinguish:
- ratified law,
- prototype defaults,
- measured runtime outputs.

Without this, later governance review will confuse observations with constitutionally chosen parameters.

### 6.6 Evidence-source ladder and historical reconciliation

Before `CDL-051` prelock hardening, publish a small evidence-source ladder for consensus planning:
- current ratified CDL and active handoffs,
- active specs and runtime artifacts,
- filtered historical extracts,
- raw `Z_Past_Chats` material as hypothesis input only.

This keeps older research useful without letting stale assumptions silently override live constitutional state.

---

## 7. Out-of-scope items for this preferred window

These items should remain outside the baseline 441-449 window unless an explicit amendment says otherwise:
- `CDL-050` opening, prelock, or ratification,
- Treasury `P_e` constants,
- public packaging/bootstrap merge work,
- bulk public test-surface curation,
- full DAG-CBOR production cutover for runtime state,
- native P2P transport replacement as a primary lane.

This is not because those items lack value. It is because they are not the highest-leverage next dependencies to settle on the numbered main track.

---

## 8. Why I do not prefer a Treasury window next

I do not recommend using the next numbered window for `CDL-050` work.

Reasoning:
- Phase 438 already concluded the prerequisites are still not satisfied,
- no new evidence has landed since then that changes the constitutional posture,
- reopening Treasury review immediately would likely produce another formal `not yet`,
- the system gets more leverage from improving execution semantics than from re-reviewing blocked governance.

The Treasury lane should stay parked until either:
- a new consensus/runtime window changes the evidentiary footing materially, or
- new targeted simulation/governance work outside the lane resolves one of the unsatisfied prerequisites.

---

## 9. Why I do not prefer a DAG-CBOR/storage window next

I also do not recommend making the next numbered window primarily about DAG-CBOR/runtime-state cutover.

Reasoning:
- the repo already has DAG-CBOR foundations and related TODOs, but the more pressing missing primitive is distributed agreement behavior,
- forcing a storage-format migration while consensus semantics are still unstable increases debugging ambiguity,
- once the consensus-path state machine is clearer, the later DAG-CBOR cutover becomes a narrower refactor with better acceptance criteria.

So my preferred order is:
1. constitutional consensus lane,
2. consensus runtime tranche,
3. then decide between DAG-CBOR cutover, Treasury re-review, or native-P2P follow-on based on the findings.

---

## 10. Future architectural lane: graph-native governance compilation

Long-horizon direction:
- move hard-coded governance constants and bounded declarative policy surfaces toward graph-native, governable knowledge nodes compiled by a deterministic kernel.
- treat historically anchored knowledge nodes as the preferred future source class for governable values once the epistemic graph and distribution layer are stable enough to support them safely.

Important boundary:
- this does **not** imply that the whole imperative runtime should become graph-defined.

Preferred architecture:
- small audited kernel,
- deterministic compiler/loader,
- graph-native governed inputs for bounded rules and constants,
- compiled artifacts consumed by runtime,
- explicit provenance and admissibility controls.

This future lane should be tracked now so later consensus/runtime work does not harden assumptions that conflict with it.

---

## 11. Conditional follow-on options after Window 449

Phase 449 should not guess the next window in advance, but the likely branches are:

### Branch A - DAG-CBOR runtime-state cutover window

Use this if the consensus prototype is structurally sound and the main pain point is JSON/runtime-state fidelity or performance.

### Branch B - Treasury `P_e` readiness re-review window

Use this only if the consensus prototype or new evidence materially changes the justification for revisiting `CDL-050`.

### Branch C - Native P2P / D2d hardening window

Use this if the consensus prototype proves that the HTTP bridge is now the main limiting factor and the architecture boundary remains ready for transport replacement.

My default preference after Window 449 would be **Branch A first**, unless the findings memo shows a stronger case for Branch C.

---

## 12. Sensitivity map

Recommended sensitivity map for the baseline 9-phase window:
- SENSITIVE: 441, 442, 443, 444, 445, 446, 447, 449
- NON-SENSITIVE: 448

Rationale:
- sequence locks and closure gates remain sensitive,
- constitutional phases remain sensitive,
- direct runtime prototype phases remain sensitive,
- adversarial regression hardening remains sensitive,
- coherence/capsule remains non-sensitive until it mutates runtime or constitutional state.

---

## 13. Bottom line

If I were choosing the next window today, I would choose:
- **Window 441-449**
- **Theme:** constitutional consensus and epoch-finality block
- **Do not include:** Treasury constitutional work, packaging work, or a storage-format cutover in the baseline window
- **Goal:** ratify the consensus lane first, then implement a measurable prototype for distributed agreement, then decide the next major lane from evidence rather than habit
