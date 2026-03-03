# ILC Window 338-347 Node Schema Program Plan v0.1

Status: planning proposal  
Date: 2026-03-03  
Owner lane: Constitution Cluster A / Protocol Layer

---

## 1. Purpose

This document proposes a concrete Window 338-347 work program that turns the node-schema packet into an executable sequence of phases.

The goal is not to implement the runtime in Window 338-347. The goal is to resolve the architectural and constitutional prerequisites so that the following window can ratify the missing schema contracts cleanly and only then authorize implementation without improvising core semantics.

This plan takes the current project state seriously:

- Window 328-337 is closed.
- `CDL-024` and `CDL-V1` through `CDL-V7` are ratified.
- `CDL-021` remains open and deferred.
- `ADM-003` still omits the 7+1 evaluation panel and graph-observation role.
- The unified node schema does not yet exist as a ratified canonical artifact.

---

## 2. Planning Stance

### 2.1 What Window 338-347 should do

Window 338-347 should:
- resolve the `ADM-003` role gap,
- open the minimum new constitutional decision-log entries required for node-schema work,
- produce evidence-prelock / contract artifacts for each major node-schema surface,
- produce a coherence/readiness package for the following ratification window,
- leave runtime implementation deferred until after the relevant node-schema CDLs are ratified.

### 2.2 What Window 338-347 should not do

Window 338-347 should not:
- begin runtime implementation of node-schema logic in `ilc_core/`,
- improvise a reputation engine without the lifecycle contract,
- let the 7+1 evaluation panel silently become the constitutional governance mechanism,
- mix authored payload semantics with transport/runtime convenience fields,
- treat the completion of open-row and prelock work as permission to implement unratified schema surfaces.

---

## 3. New CDL Set Proposed

The node-schema packet is too large to ratify under one monolithic CDL. The recommended split is:

| Proposed CDL | Scope | Why separate |
|---|---|---|
| `CDL-034` | Unified node schema envelope + reserved fields + primitive/core field taxonomy | establishes the object boundary and immutable authored payload shape |
| `CDL-035` | Validation lifecycle + gate-verdict attachment semantics | lifecycle semantics are load-bearing and need independent scrutiny |
| `CDL-036` | Node dissemination header + fetch contract | transport/header concerns should not be embedded into authored payload ratification |
| `CDL-037` | Executable node descriptor + safety contract model | executable nodes are a distinct risk domain |
| `CDL-038` | Private-to-public promotion provenance and economic continuity | privacy/economic continuity needs its own explicit governance choice |

Notably deferred from this window as a separate CDL candidate:

| Deferred topic | Reason |
|---|---|
| reputation model | depends on lifecycle semantics and should remain derived until those semantics settle |
| `CDL-021` Rust/WASM runtime | still milestone-triggered and not required for prelock work |
| validator-core ordering choice | transport/header contract matters first; permanent orderer selection can remain open |

---

## 4. Recommended Phase Sequence

## Phase 338 — Sequence Lock

**Sensitivity:** Non-sensitive  
**Scope:** Lock Window 338-347 ordering, authorize node-schema program scope, carry forward the `ADM-003` prerequisite from Phase 337.

**Outputs:**
- sequence lock artifact,
- phase-order test,
- explicit note that Window 338-347 is a pre-ratification, pre-implementation contract window.

## Phase 339 — ADM-003 Role Resolution

**Sensitivity:** Non-sensitive  
**Scope:** Update `ADM-003` to separate:
- evaluation panel role,
- graph observation / schema evolution role.

**Why first:** Multiple later phases depend on this distinction. Without it, custom-field elevation, lifecycle governance, and panel-operational semantics remain blurry.

**Outputs:**
- `ADM-003` update artifact,
- focused tests,
- handoff note authorizing schema work to proceed.

## Phase 340 — CDL-034 Opening + Node Schema Core Prelock

**Sensitivity:** Sensitive  
**Scope:**
- add `CDL-034` as a new open decision-log row,
- publish the unified node-schema core contract/evidence prelock.

**Required topics:**
- three-envelope model,
- canonical use of `Node`,
- reserved field set,
- custom-extension namespace boundary and reserved-field collision rules,
- `primitive_type` candidate set,
- `epistemic_type` / `gate_routing` boundary,
- single-primary-epistemic-lane rule,
- explicit ban on in-place historical payload mutation.

## Phase 341 — CDL-035 Opening + Validation Lifecycle Prelock

**Sensitivity:** Sensitive  
**Scope:**
- add `CDL-035` as a new open row,
- publish validation lifecycle + gate-verdict attachment prelock.

**Required topics:**
- `validation_state` state machine,
- `gate_verdict` attachment by reference,
- bounded operational relevance for recursive verdict challenges,
- quarantine semantics,
- relationship to `CDL-V1`, `CDL-V3`, `CDL-V7`.

## Phase 342 — CDL-036 Opening + Dissemination/Header Prelock

**Sensitivity:** Sensitive  
**Scope:**
- add `CDL-036` as a new open row,
- publish node-header / fetch contract prelock.

**Required topics:**
- header-first dissemination,
- CID-addressed pull fetch,
- signature scope over header + payload reference,
- visibility/channel interaction,
- transport/orderer-agnostic stance,
- explicit note that Narwhal/Tusk/Bullshark remains a reference pattern, not a locked constitutional choice.

## Phase 343 — CDL-037 Opening + Executable Node Prelock

**Sensitivity:** Sensitive  
**Scope:**
- add `CDL-037` as a new open row,
- publish executable-node descriptor + safety-contract prelock.

**Required topics:**
- structured descriptor, not raw executable code,
- nodes recommend logic; they do not self-authorize execution,
- agent-side sandboxing,
- safety contract model,
- decomposition requirements under `CDL-V7`,
- genesis-trusted vs non-genesis executable descriptors.

## Phase 344 — CDL-038 Opening + Promotion Continuity Prelock

**Sensitivity:** Sensitive  
**Scope:**
- add `CDL-038` as a new open row,
- publish private-to-public promotion continuity prelock.

**Required topics:**
- provenance continuity,
- `promotion_receipt` structure,
- no automatic public corroboration/reuse credit carry-forward,
- disclosed lineage and audit history rules,
- interaction with private/semi-private/public visibility.

## Phase 345 — Reputation and Agent-Profile Adjoint Contract

**Sensitivity:** Non-sensitive  
**Scope:** Publish a non-ratifying adjunct contract that answers:
- how reputation is derived,
- global integrity vs domain-scoped competency,
- how `Agent Profile` should carry derived trust data,
- why mutable inline node-level reputation fields remain forbidden,
- why reputation remains downstream of lifecycle semantics.

**Reason for non-sensitive classification:** This phase should not yet add a CDL row. It should constrain the future space and explicitly decide whether reputation deserves its own CDL lane later.

## Phase 346 — Node Schema Coherence / Readiness Package

**Sensitivity:** Non-sensitive  
**Scope:**
- cross-check `CDL-034` through `CDL-038` prelocks for consistency,
- update context capsule to v0.9,
- publish ratification-readiness report for Window 348+.

**Must include:**
- authored/protocol/transport boundary statement,
- unresolved risks,
- explicit list of what ratification work is authorized next,
- explicit list of what runtime work remains deferred until after ratification.

## Phase 347 — Closure Gate and 348+ Handoff

**Sensitivity:** Sensitive  
**Scope:**
- close Window 338-347,
- verify the contract stack,
- verify that `CDL-034` through `CDL-038` remain open and unratified at window close,
- publish the handoff that authorizes the first node-schema ratification lane in Window 348+ rather than runtime implementation.

---

## 5. Why This Sequence Is Recommended

### 5.1 ADM-003 first

The project already knows `ADM-003` is a prerequisite. The correct move is to resolve it before proliferating dependent schema claims.

### 5.2 Open-CDL phases are paired with their prelock artifacts

Each sensitive opening lane should land both:
- the new CDL row,
- the corresponding contract/evidence prelock artifact.

This avoids the anti-pattern of opening constitutional topics with no structured evidence plan behind them.

### 5.3 Runtime implementation is deferred deliberately

This is a disciplined choice.

The node-schema packet shows that the dangerous ambiguity is not in the code shape. It is in the semantics. If implementation starts before the semantics are split cleanly, the project will harden the wrong abstractions.

---

## 6. Concrete Window-348+ Entry Conditions Produced by This Plan

If Window 338-347 executes cleanly, Window 348+ should be able to start with a much tighter ratification scope:

1. ratify `CDL-034` through `CDL-038` in a controlled sequence,
2. keep runtime implementation barred until the relevant CDL is ratified,
3. convert the three-envelope model from prelock assumption into constitutional contract,
4. decide whether reputation remains an adjunct contract or opens its own CDL lane,
5. authorize implementation only for the ratified surfaces that emerge from that window.

In other words, Window 338-347 should make Window 348+ ratification narrow, not exploratory, and should make later implementation possible without semantic improvisation.

---

## 7. Risks in This Plan

### 7.1 Too many sensitive phases

This plan intentionally uses multiple sensitive phases because adding new CDL rows is a constitutional operation. That is acceptable if the prompt discipline remains strong. It is better than hiding constitutional mutation inside supposedly non-sensitive document phases.

### 7.2 Reputation may still need its own CDL

Phase 345 is intentionally a decision-forcing contract phase. It may conclude that reputation needs a dedicated CDL lane in Window 348+ or later. That is acceptable.

### 7.3 Ordering-stack deferral may frustrate some implementation work

True. But the transport/header contract is the higher-value invariant. Prematurely locking the validator-core ordering mechanism would be a more expensive mistake.

### 7.4 Prelock completion may be mistaken for implementation authorization

This is the main planning failure mode. If Window 338-347 only opens `CDL-034` through `CDL-038` and publishes prelocks, then runtime implementation is still constitutionally unauthorized. The closure handoff must say that explicitly.

---

## 8. Recommended Immediate Next Action

The best immediate next action is:

- commit this plan after adversarial review,
- then use the committed plan as the basis for the Phase 338 sequence-lock prompt.

That adversarial pass should attack:
- whether `CDL-034` through `CDL-038` are the right decomposition,
- whether Phase 345 should exist or be deferred,
- whether any of the opening phases should be merged or split,
- whether implementation should begin sooner than Phase 348.

---

## 9. Relationship to the Node-Schema Packet

This document is downstream of:
- `docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md`
- `docs/specs/ilc_cil_window_336_node_schema_session_v0.1.md`
- `docs/specs/ilc_node_schema_concretization_proposals_v0.1.md`

Use the packet like this:
- synthesis = what the architecture currently implies,
- CIL = what needs tracking and follow-up,
- concretization = proposed answers,
- this plan = proposed execution sequence.
