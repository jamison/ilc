# ILC Graph Dependency Contract Preparation Sequence Candidate v0.1

Status: Non-normative planning artifact — candidate docs-only sequence
Date: 2026-03-18
Owner: GPT-5 Codex
Purpose: Offload the current graph dependency/linkage/serviceability/accounting workstream into a
planned and auditable docs-only preparation sequence without widening the active Window 441-449
consensus lane.

## 1. Planning boundary

This document does not open a numbered main-track window and does not authorize runtime changes.

It exists because the current research chain has become large enough that ad hoc memo growth is no
longer ideal.

The recommendation is:
- keep the current consensus window focused,
- but represent this graph-contract workstream as a planned docs-only preparation sequence so it can
  be reviewed, audited, and handed off cleanly later.

## 2. Why a preparation sequence is justified

The current chain now spans at least these distinct but coupled surfaces:
- dependency-closure preservation
- host admission and serviceability
- node-level vs host-level accounting
- canonical linkage contract
- primitive-specific link templates
- receipts and payout traceability

That is enough coupled design material that:
- a single memo is too diffuse,
- but runtime implementation would be premature.

So the right next level of discipline is:
- a bounded docs-only sequence.

## 3. Recommended posture

Recommended posture:
- do not widen Window 441-449 into this lane
- do not treat this as a Treasury lane
- do not treat this as a runtime lane yet
- do treat it as a dependency-contract preparation lane for later schema/economics work

The right goal is:
- prepare one stable docs-only baseline that future schema/runtime/economics lanes can rely on.

## 4. Sequence shape

Suggested shape:
- 5 docs-only phases

This is small enough to audit and large enough to separate concerns cleanly.

## 5. Candidate phase sequence

| Order | Candidate phase | Topic | Character | Sensitivity |
|---|---|---|---|---|
| 1 | GDC-01 | Graph linkage contract freeze | Contract / Architecture | NON-SENSITIVE |
| 2 | GDC-02 | Primitive-to-link-template and dependency-class matrix freeze | Contract / Architecture | NON-SENSITIVE |
| 3 | GDC-03 | Host admission, serviceability, and challenge-target contract | Architecture / Operations | NON-SENSITIVE |
| 4 | GDC-04 | Receipt envelope and payout-trace lane freeze | Accounting / Audit | NON-SENSITIVE |
| 5 | GDC-05 | Coherence, anti-refactor handoff, and future-lane pointer | Synthesis / Handoff | NON-SENSITIVE |

These are candidate labels only.

They are not official phase numbers and should not be mistaken for the active main track.

## 6. Phase objectives

### GDC-01 — Graph linkage contract freeze

Objective:
- settle the docs-only linkage vocabulary and linkage object shape

Minimum outputs:
- one canonical docs-only linkage contract candidate
- one explicit required-vs-reference distinction
- one duplicate/equivalence/supersession vocabulary baseline

Non-goals:
- no runtime schema mutation
- no payout logic

### GDC-02 — Primitive-to-link-template and dependency-class matrix freeze

Objective:
- map the working primitive family to legal linkage patterns

Minimum outputs:
- one primitive/link matrix
- one dependency-pressure interpretation
- one anti-gaming note for weak citation links

Non-goals:
- no ratification of the full primitive family as final law
- no runtime validation engine

### GDC-03 — Host admission, serviceability, and challenge-target contract

Objective:
- settle the host-side operational meaning of "serviceable"

Minimum outputs:
- `stored` vs `serviceable` distinction
- dependency resolvability obligations
- challenge target semantics
- repair-window direction

Non-goals:
- no live slashing logic
- no routing implementation

### GDC-04 — Receipt envelope and payout-trace lane freeze

Objective:
- settle the minimum accounting lanes and envelope concepts

Minimum outputs:
- node usefulness lane
- host service lane
- allocation lane
- challenge/audit outcome lane
- candidate receipt types and allocation classes

Non-goals:
- no final payout formulas
- no ledger/runtime implementation

### GDC-05 — Coherence, anti-refactor handoff, and future-lane pointer

Objective:
- consolidate the docs-only baseline and state what should happen later

Minimum outputs:
- one coherent handoff summary
- one explicit list of what belongs in future schema work
- one explicit list of what belongs in future economics/runtime work

Non-goals:
- no premature main-track activation

## 7. Expected downstream outputs after the sequence

If the sequence succeeds, the project should have:
- one stable linkage contract baseline
- one stable primitive/link interpretation layer
- one stable host serviceability model
- one stable receipt/payout traceability baseline
- one cleaner TODO/handoff surface for later schema and runtime work

That would be enough to substantially reduce later refactor risk.

## 8. Estimated extra steps beyond the current memo chain

Beyond the documents already created, I estimate the remaining work in this chain falls into three
bands.

### 8.1 Docs-only consolidation band

Still needed:
- linkage contract candidate
- receipt envelope candidate
- cross-document coherence pass

This is mostly now underway or complete.

### 8.2 Contract-normalization band

Likely next after the docs-only sequence:
- normalize vocabulary across research/architecture/spec docs
- decide whether the working primitive family survives unchanged or is reduced
- define a future schema-target list

### 8.3 Future implementation-prep band

Only after the above:
- define actual node-schema deltas
- define actual receipt envelope schema
- define actual challenge evidence shapes
- define accounting hooks without yet coding formulas

This should remain later.

## 9. Recommended interpretation relative to Window 441-449

This sequence should be interpreted as:
- parallel planning and architecture prep
or:
- post-449 docs-only prep

It should not be interpreted as:
- a reason to widen the current consensus window,
- or proof that graph-economics runtime work should start now.

The active consensus lane remains the higher immediate dependency.

## 10. Bottom line

Yes, this workstream is now large enough that it should be planned, not just improvised.

The correct planning move is not a new active runtime window.

It is:
- a small docs-only preparation sequence,
- clearly separated from the active consensus window,
- with enough structure that future schema/economics lanes inherit one auditable baseline instead of
  a pile of loosely related memos.
