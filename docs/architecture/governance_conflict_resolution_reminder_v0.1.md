# Governance Conflict Resolution Reminder v0.1

Status: Core set resolved (Phase 993)  
Date: 2026-02-16  
Owner: Governance and constitutional ratification track

## 1. Purpose

Create a single reminder artifact for the unresolved governance conflict set that currently blocks full promotion of key glossary/governance concepts into canonical architecture.

## 2. Governance Conflicts (Core Set, Resolved in Phase 993)

### 2.1 Matrix Conflict Cluster

- `raw-012616`
- `raw-012647`
- `raw-012640`
- `raw-012888`
- `raw-012660`
- `raw-012615`
- `raw-012645`

Source anchor:
- `docs/architecture/glossary_term_elevation_matrix_v0.1.md:49`

### 2.2 Open Decision-Log Governance/Founder/Boundary Items

- `CDL-006`
- `CDL-003`
- `CDL-004`
- `CDL-005`
- `CDL-008`
- `CDL-009`
- `CDL-010`

Source anchor:
- `docs/architecture/glossary_term_elevation_matrix_v0.1.md:59`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md:31`

## 3. Why This Is Blocking

- `Court Certification (7+1)` and related anti-capture semantics remain `deferred/conflict/decision_log`.
- Founder power boundaries and governance override model are still open, which blocks ratification of some governance-facing glossary promotions.
- Layer-boundary ambiguity (`fixed core` vs `policy-loaded`) increases risk of inconsistent implementation scope.

Primary evidence:
- `docs/architecture/glossary_term_elevation_matrix_v0.1.md:22`
- `docs/architecture/glossary_term_elevation_matrix_v0.1.md:47`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md:34`

## 4. Resolution Checklist (Completed for Core Set)

- [x] Ratify `CDL-006` governance override/challenge model and publish chosen rationale.
- [x] Ratify founder-boundary cluster: `CDL-003`, `CDL-004`, `CDL-010`.
- [x] Ratify constitutional/economic boundary cluster: `CDL-005`, `CDL-008`, `CDL-009`.
- [x] Map each `raw-0126xx` conflict row to one ratified `CDL-*` outcome and close mismatch.
- [x] Update canonical glossary status rows that currently depend on these open decisions.
- [x] Add deterministic conformance tests for any new governance primitives promoted from this closure.

## 5. Core-Set Closure Outputs

- Updated constitutional decision log entries marked `ratified` with selected options and evidence.
- Updated glossary elevation matrices with conflict status moved from `open` to `resolved` where applicable.
- One closure walkthrough phase documenting:
  - exact ratified decisions,
  - implementation touchpoints,
  - regression and conformance evidence.

Core mapping artifact:
- `docs/specs/ilc_governance_conflict_set_ratification_v0.1.md`
