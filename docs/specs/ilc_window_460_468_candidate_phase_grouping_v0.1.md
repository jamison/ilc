# ILC Window 460-468: Candidate Phase Grouping

Author: Claude Code (planning synthesis)
Date: 2026-03-20
Baseline assumption: Window 450-459 closes cleanly with `CDL-050` ratified and `CDL-051`
remaining ratified. Both synthesis documents that prepare this window
(`docs/specs/ilc_simplified_epistemic_model_synthesis_v0.1.md` and
`docs/specs/ilc_refutation_novelty_requirement_v0.1.md`) are committed at `00b57e9`.

Planning note: this is a candidate grouping only. It does not amend the active `450-459`
sequence lock and does not authorize post-`459` execution by itself.

---

## 1. Preferred planning posture

The primary purpose of Window 460-468 is to ratify `CDL-052`, which governs the three-mode
epistemic evaluation architecture for the ILC knowledge graph. The design work for CDL-052
is already captured in two committed synthesis documents; this window converts that design
into a ratified constitutional contract.

Three secondary research and architecture tracks are deferred from Window 450-459 per the
explicit planning decision recorded in that window's sequence lock:
- `ADR-0021` Epistemic Finality Claims,
- TLA+ CDL-051 shell specification,
- Genesis validator and OpenClaw architecture scoping.

These tracks are sequential phases at the end of the window, not parallel lanes. The CDL-052
ratification track is the primary lane.

The lane should not absorb:
- CDL-050 implementation work (Treasury ECU-governor runtime, deferred beyond this window),
- consensus runtime follow-on work beyond the TLA+ shell specification document,
- full OpenClaw implementation (architecture scoping only),
- full Genesis validator implementation (architecture scoping only),
- temporal decay interaction specification for Mode 1 centrality (this is a CDL-V1 extension
  requiring its own lane and is complex enough to defer beyond Window 460-468).

---

## 2. Required inherited entry conditions

This candidate window assumes the following are true at entry:
- Window `450-459` is closed.
- `CDL-050` is ratified (Treasury ECU-Governor lane).
- `CDL-051` is ratified (constitutional consensus and epoch-finality).
- the constitutional capsule has been advanced to v2.0 by Phase 459.
- both synthesis documents exist and are committed:
  `docs/specs/ilc_simplified_epistemic_model_synthesis_v0.1.md`
  `docs/specs/ilc_refutation_novelty_requirement_v0.1.md`
- `ilc_core/` is clean (no uncommitted runtime changes).

Implication:
- this window must begin by freezing the CDL-052 scope boundary before opening any
  constitutional row or producing any evidence artifact.

---

## 3. Hard closure gates for CDL-052

The window is organized around the following gates. `CDL-052` does not open unless all three
gates through Gate 3 are satisfied.

### Gate 1 — ADR-0021 compatibility

`ADR-0021 Epistemic Finality Claims` must be published and checked for scope conflicts with
the proposed CDL-052 language. ADR-0021 covers the epistemic status of finality assertions
in the ILC consensus machinery (CDL-051 domain). CDL-052 covers the epistemic evaluation
architecture for knowledge graph nodes (graph domain). These domains overlap at the boundary
where finality records are themselves knowledge nodes.

Gate 1 clears only if:
- ADR-0021 is complete and does not introduce finality-claim handling that contradicts
  the three-mode routing model in the CDL-052 design,
- any boundary conditions between the CDL-051 consensus domain and the CDL-052 knowledge
  graph domain are recorded explicitly in the CDL-052 opening stub.

### Gate 2 — Schema specification completeness

The `refutation_criterion` field formal schema specification must exist as a standalone
artifact before CDL-052 opens. The field is the single opt-in signal for Mode 2 (Popperian
elevation path); its specification must cover:
- field structure and required elements,
- validation rules at submission time,
- interaction with the node envelope taxonomy ratified by CDL-034.

Gate 2 clears only if:
- a complete schema specification artifact exists,
- the specification does not conflict with the CDL-034 three-envelope schema,
- all interaction with `normative: true` metadata is addressed.

### Gate 3 — Staking contract specification completeness

The minimal staking contract specification must exist before CDL-052 opens. Staking
requirements for node submission and refutation are the primary economic anti-gaming
mechanism; the CDL-052 constitutional language cannot be hardened without knowing what the
staking surface looks like.

Gate 3 clears only if:
- submission staking requirements are specified (at minimum: staking obligation, penalty
  on failed novelty check, reputation feed-through),
- refutation staking requirements are specified (at minimum: required stake, stake loss
  on failed challenge, reward proportionality formula),
- the specification explicitly defers full parameter calibration to a future simulation
  lane (equivalent to the CDL-050 SIM-T approach) rather than locking constants prematurely.

### CDL-052 opening authorization

Only if Gates 1-3 all pass may the lane advance to CDL-052 opening, prelock hardening, and
ratification.

---

## 4. Recommended baseline window: 460-468

Suggested title:
- **Window 460-468: Epistemic Model Ratification, Research Tracks, and Architecture Scoping**

| Order | Phase | Topic | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 460 | Sequence lock + CDL-052 lane-scope freeze | Foundation / Constitutional | SENSITIVE |
| 2 | 461 | ADR-0021 Epistemic Finality Claims | ADR / Research | SENSITIVE |
| 3 | 462 | `refutation_criterion` formal schema specification | Schema / Specification | SENSITIVE |
| 4 | 463 | Minimal staking contract specification | Economics / Specification | SENSITIVE |
| 5 | 464 | CDL-052 opening | Constitutional | SENSITIVE |
| 6 | 465 | CDL-052 prelock hardening and adversarial review | Constitutional | SENSITIVE |
| 7 | 466 | CDL-052 ratification | Constitutional | SENSITIVE |
| 8 | 467 | TLA+ CDL-051 shell specification | Research / Specification | SENSITIVE |
| 9 | 468 | Genesis validator scoping + OpenClaw architecture scoping + Window 460-468 closure gate | Architecture / Gate | SENSITIVE |

This baseline is intentionally narrower than Window 450-459. If Gate 1 (ADR-0021) reveals
a scope conflict, Phases 464-466 must not proceed until the conflict is resolved with a
CDL-052 scope amendment. The carry-forward path is the correct response, not a rushed opening.

---

## 5. CDL-052 scope

`CDL-052` governs the three-mode epistemic evaluation architecture for knowledge graph nodes.

What CDL-052 covers:
- three-mode routing model (Mode 1: default reuse-valuation; Mode 2: Popperian elevation;
  Mode 3: anomaly-triggered auditor review),
- `refutation_criterion` field as the opt-in signal for Mode 2,
- novelty requirement for valid refutations (as specified in the companion artifact),
- staking obligations for node submission and refutation,
- anomaly-triggered auditor panel activation criteria and composition,
- `corroborated_reuse` economic designation criteria (proposed vocabulary for ratification).

What CDL-052 does not cover:
- agent decomposition admissibility criteria (CDL-V7, already ratified),
- quorum diversity requirements for ratification governance (CDL-V3, already ratified),
- Sybil resistance mechanism for participant identity (CDL-V2, already ratified),
- temporal decay governance parameter for reuse centrality (CDL-V1, already ratified;
  the CDL-052 / CDL-V1 interaction is an open item deferred beyond this window),
- CDL-050 Treasury ECU-Governor runtime (implementation deferred),
- CDL-051 consensus runtime (separate lane; TLA+ shell spec is documentation only),
- Jubilee or long-horizon token-rotation,
- node-rent lifecycle or public-goods fade redesign.

CDL-052 depends on:
- CDL-034 (node schema envelope) — `refutation_criterion` must conform to the authored
  envelope structure,
- CDL-035 (validation lifecycle) — refutation outcomes feed into the validation-state machine,
- CDL-V7 (agent decomposition admissibility) — CDL-052 governs refutation of admitted claims,
- CDL-V2 (Sybil resistance) — the anti-Sybil independence check is a prerequisite for the
  collusive-friendly-refutation gate in Section 3 of the novelty requirement document.

---

## 6. Phase-by-phase scope

### Phase 460 — Sequence lock + CDL-052 lane-scope freeze

Purpose:
- open Window 460-468 as a dedicated ratification window,
- publish a sequence lock enumerating all nine phases and their gate dependencies,
- freeze the CDL-052 scope boundary (in-scope and out-of-scope) before any constitutional
  rows are touched,
- record the inherited entry conditions from Window 450-459.

Output target:
- a sequence lock artifact that states exactly what this window is trying to close and what
  it explicitly defers.

### Phase 461 — ADR-0021 Epistemic Finality Claims

Purpose:
- define the epistemic status of finality assertions in the ILC consensus machinery,
- identify the boundary between the CDL-051 consensus domain and the CDL-052 knowledge
  graph domain at the point where finality records are themselves nodes on the graph,
- explicitly clear or flag Gate 1 for the CDL-052 opening.

Primary inputs:
- CDL-051 ratification evidence (`docs/specs/ilc_cdl_051_...ratification_evidence_443_v0.1.md`),
- Phase 447 findings memo (epistemic finality research from Window 441-449),
- `docs/specs/ilc_epistemological_foundations_canonical_v0.1.md`.

Output target:
- ADR-0021 artifact with explicit Gate 1 compatibility statement.

### Phase 462 — `refutation_criterion` formal schema specification

Purpose:
- specify the `refutation_criterion` field structure, required elements, and validation rules,
- confirm conformance with the CDL-034 authored envelope taxonomy,
- resolve the interaction with `normative: true` metadata,
- clear Gate 2 for CDL-052 opening.

Output target:
- a standalone schema specification artifact that can be incorporated by reference into
  the CDL-052 opening stub.

### Phase 463 — Minimal staking contract specification

Purpose:
- specify the staking obligations for node submission and for refutation submission,
- define the penalty structure for failed novelty checks and failed challenges,
- specify the reputation feed-through mechanism,
- define the reward proportionality formula for refutation success,
- explicitly defer parameter calibration constants to a future simulation lane,
- clear Gate 3 for CDL-052 opening.

Output target:
- a staking contract specification artifact that explicitly marks constants as TBD pending
  simulation evidence. This document is a constitutional surface specification, not a
  parameter-calibrated contract.

### Phase 464 — CDL-052 opening

Purpose:
- open the CDL-052 constitutional row in the decision log (first authorized decision-log
  mutation in Window 460-468),
- record the scope boundary, dependency clauses, and the three gate-clearance references,
- keep the opening additive only (no prelock language, no ratification evidence).

Precondition:
- Gates 1-3 must be clean. Phase 464 must not proceed if any gate is open.

### Phase 465 — CDL-052 prelock hardening and adversarial review

Purpose:
- harden the CDL-052 constitutional language against adversarial scenarios,
- freeze the Mode 2/Mode 3 boundary conditions and activation thresholds at a qualitative
  level (numeric thresholds remain TBD, as established in Phase 463),
- adversarially review: check for uncapped refutation paths, circular challenge exit
  conditions, and scope creep relative to the Phase 460 scope freeze,
- update CDL-052 row to `status: prelock`.

Adversarial review must cover:
- inwardness attack defense completeness (three-layer check: novelty, reward proportionality,
  staking),
- Mode 3 activation threshold ambiguity (are the four anomaly signals specified precisely
  enough to prevent arbitrary activation?),
- `corroborated_reuse` designation loop (can a node become eligible for corroborated_reuse
  through collusive challenge-and-survival?),
- CDL-V7 boundary consistency (CDL-052 governs refutation; CDL-V7 governs decomposition
  admissibility; the handoff point between them must be explicit).

### Phase 466 — CDL-052 ratification

Purpose:
- ratify the CDL-052 epistemic evaluation architecture,
- publish the window capsule successor (v2.1, superseding v2.0),
- update CDL-052 row to `status: ratified`.

Precondition:
- Phase 465 prelock artifact must be clean.
- CDL-052 row must be `status: prelock` at Phase 466 entry.

### Phase 467 — TLA+ CDL-051 shell specification

Purpose:
- produce a TLA+ specification that formalizes CDL-051 semantics as an abstract state machine,
- cover: state variables (validators, cluster_membership, vote_weights, epoch_records,
  finality_state), the safety property `NoTwoHonestNodesFinalizeDifferentBlocks`, and
  the liveness condition for epoch advancement,
- leave numeric parameters as tunable TLA+ constants (QUORUM_THRESHOLD, CLUSTER_COUNT,
  DIVERSITY_FLOOR, VALIDATOR_COUNT) to support distributed network evolution,
- this is a specification document, not a runtime implementation; `ilc_core/` must remain
  unchanged.

Note: this phase is a research/specification deliverable, not a constitutional gate. It does
not open a new CDL row. It is positioned after CDL-052 ratification because it is a
secondary research track and should not block the primary CDL-052 lane.

### Phase 468 — Genesis validator scoping + OpenClaw architecture scoping + Window 460-468 closure gate

Purpose — Genesis validator scoping:
- scope what a genesis validator node requires for initial network bootstrap under CDL-051
  consensus machinery,
- identify the minimum viable configuration: signing keys, cluster membership initialization,
  epoch-state initialization, admission control pre-population,
- this is architecture scoping, not implementation; no `ilc_core/` changes.

Purpose — OpenClaw architecture scoping:
- scope how the CDL-052 epistemic evaluation architecture surfaces through the OpenClaw
  interface (CDL-033 ratified the skill publication contract; this phase scopes the
  architecture that would expose graph operations: node submission, refutation submission,
  novelty check status, centrality query),
- identify what additional SDK-level contracts are required beyond CDL-033,
- this is architecture scoping, not implementation.

Purpose — Window closure gate:
- publish Window 460-468 handoff artifact and closure gate script,
- update context capsule to v2.1 if Phase 466 was the last capsule update,
- point to next window.

---

## 7. Evidence discipline for the window

The evidence base for this window should follow these rules:
- primary sources first: committed synthesis artifacts (`ilc_simplified_epistemic_model_synthesis_v0.1.md`
  and `ilc_refutation_novelty_requirement_v0.1.md`), active constitutional artifacts, active
  ADRs, and the CDL-051 ratification evidence package,
- research notes and Z_Past_Chats materials remain hypothesis inputs for ADR-0021 and TLA+
  phases only; they do not constitute constitutional evidence,
- no blocker closes on prose alone for Phases 461-463 (schema, staking, and ADR-0021
  artifacts must be concrete specifications, not intentions),
- CDL-052 opening (Phase 464) must cite Phase 462 and Phase 463 artifacts explicitly as
  its gate clearance evidence,
- no retroactive rewriting of the CDL-050 or CDL-051 ratification language during this window,
- no parameter calibration constants in Phases 462-463; constants are TBD pending a future
  simulation lane (following the CDL-050 SIM-T precedent).

---

## 8. Non-goals and failure path

Non-goals for Window 460-468:
- no CDL-050 runtime implementation (Treasury ECU-governor),
- no CDL-051 consensus runtime implementation,
- no full OpenClaw implementation (scoping only),
- no full Genesis validator implementation (scoping only),
- no temporal decay interaction specification for Mode 1 centrality (CDL-V1 extension,
  deferred beyond this window),
- no Jubilee or long-horizon token-rotation,
- no knowledge-graph preservation economics redesign,
- no CDL-052 numeric parameter calibration (constants are TBD; a future simulation lane is
  the correct venue for calibration),
- no forced CDL-052 opening if any of Gates 1-3 is unresolved.

Failure path:
- if Gate 1 (ADR-0021 compatibility) reveals a scope conflict between CDL-051 finality
  semantics and the CDL-052 three-mode routing model, the correct response is a CDL-052
  scope amendment in Phase 460 or a carry-forward memo, not a forced opening,
- if Phase 462 or Phase 463 leaves a material open item that would result in uncapped paths
  or unspecified reward surfaces in CDL-052, the opening must be deferred,
- Phases 467-468 do not depend on the CDL-052 lane; if CDL-052 is deferred, Phases 467-468
  may still proceed as standalone research and scoping phases,
- the window closure gate in Phase 468 must report cleanly on all phases actually completed;
  it must not report completed phases as pending or pending phases as completed.
