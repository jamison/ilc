# ILC Post-582 Harness and SDK Lane v0.1

Status: planning spec
Date: 2026-04-03
Owner lane: post-582 harness/operator track

## 1. Purpose

This document turns the accepted protocol-vs-harness boundary into an explicit
planning lane.

The goal is to improve agent/operator usability and public-RC product readiness
without polluting protocol truth, settlement semantics, or wallet authority.

This lane is subordinate to:
- RC0.1 runtime correctness,
- Phase 576 wallet boundary,
- ADR-0022 local-first/private-use constraints,
- and the Phase 585+ public cryptographic-economic coupling packet.

## 2. Boundary rule

Protocol logic stays in:
- `ilc_core`
- settlement/runtime semantics
- graph legitimacy surfaces
- canonical wallet/accounting authority

Harness/operator/product logic sits on top through:
- CLI surfaces,
- query surfaces,
- machine-readable logs,
- receipts,
- manifests,
- and later thin UX wrappers.

## 3. Pull in now

These are the immediate post-582 harness priorities.

### 3.1 Workflow state persistence

Required shape:
- explicit machine states for:
  - submit
  - evaluate
  - settle
  - replay
  - query
- crash-safe recovery
- replay-safe transitions

Why now:
- reduces real failure risk in the current RC path
- directly supports settlement and replay integrity

### 3.2 System event log

Required shape:
- structured, machine-readable action log
- not chat transcript
- suitable for operator audit and agent resumption

Why now:
- strengthens diagnostics and operator truth
- improves harness interoperability

### 3.3 Tool and permission metadata

Required shape:
- read/write/admin tiers
- input/output contracts
- failure-token contracts
- non-mutation expectations where applicable

Why now:
- keeps future harnesses agent-usable without hard-coding one harness model

### 3.4 Harness verification

Required shape:
- tests asserting:
  - permissions are enforced,
  - replay remains safe,
  - state transitions are legal,
  - read-only surfaces do not mutate,
  - event logging is present for critical actions

Why now:
- de-risks future harness/product expansion

## 4. Pull in later

These belong in a later public-RC-facing harness/product layer.

### 4.1 QuotaMiner harness

Allowed only in the harness/operator layer.

Inputs:
- provider budget
- token caps
- active hours / overnight window
- risk policy
- allowed task classes
- local node status
- current ILC work surfaces

Outputs:
- selected bounded work
- run decisions
- stop conditions
- cost/accounting reports
- protocol receipts consumed and displayed

### 4.2 Simple onboarding flow

Preferred shape:
- `ilc init`
- `ilc status`
- `ilc mine`

`ilc init` should cover:
- operator label / local name
- wallet create/import/export
- backup guidance
- provider or local-model connection
- safe defaults

`ilc status` should cover:
- node health
- wallet/accounting visibility
- current mode
- last work / receipts

`ilc mine` should cover:
- conservative mode
- overnight mode
- budget-capped mode
- selected task-class mode

### 4.3 Minimal status/accounting surface

Allowed public-RC metrics:
- verified work completed
- ECU / settled ILC accounting

No unstable or gamable "intelligence score" style metrics.

### 4.4 Optional tiny dashboard

Allowed only if:
- it remains thin over the same CLI/state surfaces,
- it does not define protocol truth,
- it does not become a correctness dependency.

## 5. Never / probably not for ILC core

The following are explicitly outside ILC core direction unless a later strong
architectural case is made:

- Ink / terminal-OS style UI as a core direction
- Anthropic-style fixed agent archetypes
- transcript compaction as a protocol concern
- tool-pool assembly as a first-class protocol priority
- QuotaMiner inside protocol economics/runtime
- vanity metrics affecting consensus/rewards

## 6. Wallet scope boundary

This lane must preserve the Phase 576 wallet boundary.

Allowed:
- create
- import
- export
- backup guidance
- accounting visibility

Not authorized here:
- spend
- transfer
- withdrawal
- broad signing semantics

## 7. Genesis-driven auto-configuration boundary

Allowed:
- auto-configuration from signed canonical Genesis/bootstrap artifacts,
- canonical manifests,
- canonical receipts.

Not allowed:
- vague configuration download from arbitrary graph state,
- treating non-canonical graph objects as trusted config authority.

## 8. Sequence

Recommended execution order:
1. workflow state persistence
2. system event log
3. tool/permission metadata
4. harness verification
5. wallet/bootstrap init UX
6. provider/local-model connection UX
7. QuotaMiner harness
8. minimal status/accounting view
9. optional tiny dashboard
10. restrained leaderboard metrics

## 9. Relationship to existing lanes

This planning spec does not reopen:
- the Window 575-584 runtime closure gate,
- the Phase 576 wallet boundary,
- the Phase 585+ public cryptographic-economic coupling packet.

It is a parallel harness/operator planning lane intended to sit on top of the
protocol rather than inside it.

## 10. Related references

- `docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md`
- `docs/adr/ADR_0022_Local_First_Private_Use_and_Publication_Bound_Economics.md`
- `docs/research/ilc_agentic_harness_lessons_learned_classification_v0.1.md`
- `docs/research/ilc_cryptographic_economic_coupling_memo_v0.1.md`
- `docs/research/ilc_rc_phase_575_execution_packets_v0.1.md`
