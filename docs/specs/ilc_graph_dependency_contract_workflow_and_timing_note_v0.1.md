# ILC Graph Dependency Contract Workflow and Timing Note v0.1

Status: Non-normative planning artifact — workflow/timing note
Date: 2026-03-18
Owner: GPT-5 Codex
Purpose: Explain how the graph dependency contract workstream should fit the repo's normal planning
pattern so it can be advanced at the right time and with the right artifact types.

## 1. Why this note exists

The current graph-contract chain now has enough structure that the next question is no longer:
- "what are the ideas?"

The next question is:
- "how does this fit the repo's normal workflow, and when should it actually move?"

This note exists to answer that.

## 2. Short answer

No, `GDC-01` is not meant to be a new main-track runtime phase right now.

It is a label inside a candidate docs-only preparation sequence.

That sequence is meant to follow the repo's established pattern:
- research memos first,
- then docs-only contract candidates,
- then planning/TODO placement,
- then execution only when the right slot exists in the broader plan.

That is the right methodology here.

## 3. The normal repo pattern

The repo already uses a recognizable pattern for architecture and contract work:

### 3.1 Research/exploration layer

Use:
- `docs/research/`

Purpose:
- clarify ideas
- separate good concepts from noise
- identify missing distinctions

This is where the current graph-preservation and host/accounting memos belong.

### 3.2 Docs-only contract/planning layer

Use:
- `docs/specs/`

Purpose:
- turn exploration into auditable contract candidates or planning artifacts
- freeze vocabulary and scope before runtime

This is where the new linkage contract candidate, receipt candidate, and prep-sequence candidate
belong.

### 3.3 TODO / planning placement

Use:
- `TODO.txt`
- candidate sequence docs
- window planning artifacts where appropriate

Purpose:
- place the work relative to other lanes
- record anti-refactor items
- keep future work dependency-ordered

This is already underway for the graph-contract lane.

### 3.4 Execution artifact only at the proper moment

Use:
- a proper phase/sequence artifact or prompt only when the broader plan actually gives this lane a
  slot

Purpose:
- avoid pseudo-executing work that is not yet sequenced

This is the point that matters most here.

## 4. Where ADRs fit and where they do not

An ADR is best when:
- a real architectural decision is mature enough to state as a decision,
- alternatives are known,
- and the project is ready to say "this is the chosen boundary."

The current graph-contract lane is not fully there yet.

Why:
- the linkage/accounting/serviceability surfaces are still being normalized,
- the primitive-facing layer is still a working model,
- and there is not yet a final schema/runtime target.

So at this moment:
- a planning artifact and docs-only contract candidates are more appropriate than a final ADR.

An ADR may become appropriate later for something like:
- founder vs steward economics boundary,
- host serviceability boundary,
- or node-level vs host-level accounting separation,

but not yet as the first step.

## 5. What GDC-01 actually means

`GDC-01` is best understood as:
- the first step in a future docs-only preparation sequence,
- not a numbered constitutional/main-track phase,
- not a runtime phase,
- not a Treasury phase.

In practical terms, it would mean:
- take the current linkage candidate and freeze it as the docs-only baseline,
- normalize terminology,
- and prepare the handoff into later schema/economics work.

That is all.

## 6. Proper timing relative to Window 441-449

The active planning priority is still:
- Window `441-449`
- consensus / epoch-finality constitutional-first work

So the graph-contract lane should be treated as:
- parallel docs-only prep,
or:
- post-`449` docs-only prep,

not:
- a reason to widen or interrupt the active consensus sequence.

That is the correct timing discipline.

## 7. Recommended workflow from here

The clean workflow is:

### Step A — keep the current stack as planning baseline

Baseline docs now are:
- `docs/research/ilc_dependency_closure_preservation_architecture_memo_v0.1.md`
- `docs/specs/ilc_graph_linkage_and_dependency_contract_candidate_v0.1.md`
- `docs/specs/ilc_graph_dependency_contract_prep_sequence_candidate_v0.1.md`

### Step B — treat the new sequence candidate as the planning container

Meaning:
- if this workstream moves again, it should move under that sequence container,
- not as ad hoc memo branching.

### Step C — only create a true execution artifact when scheduling is real

That means:
- only write an actual GDC-01-style execution prompt or formal docs-only phase artifact when one
  of these is true:
  - it is explicitly scheduled as a parallel docs-only lane,
  - or Window `449` closure points to it as the next preparation lane,
  - or a new planning lock/amendment gives it an actual slot.

Until then, the candidate sequence is enough.

## 8. What "proper moment" means here

In this repo, the proper moment is not:
- "we have enough ideas."

It is:
- the work has a defined slot relative to other active windows,
- dependencies are clear,
- non-goals are explicit,
- and the artifact type matches the work.

For this lane, that means:
- now: research + docs-only candidates + planning placement
- later: docs-only sequence execution if scheduled
- later still: schema/runtime/economics work if explicitly opened

## 9. Recommended immediate next step

The best immediate step is not a runtime phase and not a new ADR.

It is:
- keep the current graph-contract sequence candidate as the planning baseline,
- use it to stop further drift,
- and wait until the broader sequence timing is appropriate before turning it into a true execution
  artifact.

That preserves discipline without losing the work.

## 10. Bottom line

The proper workflow here is the normal repo workflow:
- research,
- then docs-only contract candidates,
- then TODO/planning placement,
- then execution only when the lane has a real slot.

So yes:
- we should plan it now,
- we should not execute it as if it were a live numbered phase yet,
- and the current candidate sequence is the correct "holding structure" until timing catches up.
