# ILC Genesis Authority Sunset Spec 1547p v0.1

**Status:** PRE-RC GOVERNANCE SPECIFICATION
**Phase:** 1547p
**Window:** 1546p-1555p
**OBL:** OBL-023
**Governance activation:** none

```text
obl_023_genesis_authority_sunset_spec_committed_phase_1547p
genesis_authority_not_sunset_phase_1547p
public_path_remains_blocked_phase_1547p
```

## 1. Purpose

This specification closes the pre-public-RC documentation gap for the Genesis
authority sunset path. It translates the existing CDL-004 founder-operational-cap
commitment, the Phase 590 Genesis coherence lock, and the Phase 1469 private
design spec into a standalone transition model.

The spec is intentionally non-activating. It defines how Genesis authority is
expected to recede, what public governance bodies inherit which functions, and
which evidence must exist before any future sunset state transition is ratified.
It does not execute that transition.

## 2. Source Basis

| Source | Role in this spec |
|---|---|
| `CDL-003` | Founder fade-out mechanics; trigger-based sunset anchor |
| `CDL-004` | Founder operational caps; hard caps and reporting anchor |
| `CDL-013` | Governance-weight normalization anchor |
| `CDL-017` | Validator governance framework and bootstrap-transition boundary |
| `CDL-V6` | Extraordinary Genesis intervention protocol with audit and sunset limits |
| `CDL-045` | Emergency circuit-breaker sunset and post-hoc review pattern |
| Phase 590 coherence lock | Genesis authority must recede through ratified mechanisms, not silence |
| Phase 1469 private spec | Three-stage Boot / Transition / Mature design target |

## 3. Governance Branches

### 3.1 House

The House is the ordinary community governance branch. Its mature role is to
ratify ordinary protocol changes, parameter migrations, public governance-node
admissions, and non-emergency policy updates under the applicable CDL process.

During Boot, the House may only provide advisory signal unless a specific CDL has
already granted binding authority for the question at issue. During Transition,
the House receives scoped binding authority over domains where the necessary
quorum, eligibility, and anti-capture safeguards are operational. During Mature
operation, the House is the primary ordinary governance branch.

### 3.2 Court

The Court is the constitutional review and dispute branch. Its role is not to
write ordinary policy. Its role is to certify whether a proposed transition,
intervention, appeal, fork-legitimacy claim, or constitutional challenge satisfies
the evidence and threshold requirements of the relevant CDL.

Court panels may reuse jury and panel-selection machinery once that machinery is
activated by later authority. Before activation, Court references are a
governance design surface only.

### 3.3 Executive / Autopilot

The Executive surface is the bounded operational execution layer for ratified
governance outcomes. In ILC's preferred mature state, many executive functions
are replaced by Autopilot: telemetry-bounded parameter adjustment within
constitutional limits.

Autopilot is not a fourth constitutional branch and cannot amend constitutional
state. It may recommend or execute only changes that a ratified rule already
authorizes. Any human-adjustable executive lever must carry a sunset fuse:
scope, evidence, expiry condition, and reporting requirement.

### 3.4 Genesis Authority

Genesis authority is the temporary bootstrap authority of the founding identity.
It exists to establish canonical lineage, perform pre-community design
completion, and handle bounded emergency cases where ratified community
governance is not yet operational. It is not permanent sovereign discretion.

Genesis authority recedes by domain. A domain recedes only when the successor
mechanism for that domain is ratified, operationally tested, and able to provide
auditability at least as strong as the Genesis path it replaces.

## 4. Staged Recession Model

| Stage | Genesis role | House role | Court role | Executive / Autopilot role |
|---|---|---|---|---|
| Boot | Primary bootstrap signer and bounded emergency authority | Advisory or CDL-scoped binding only | Certifies boundaries where a review lane exists | Executes only pre-authorized bootstrap operations |
| Transition | Veto-only or emergency-only in domains with mature successor mechanisms | Binding in scoped domains with quorum and anti-capture controls | Certifies evidence sufficiency, threshold satisfaction, and fork legitimacy | Executes ratified policies; starts sunset-fuse replacement of human levers |
| Mature | No ordinary governance role; extraordinary intervention unavailable unless a later CDL explicitly preserves a narrow residual path | Primary ordinary governance branch | Constitutional review, dispute resolution, and fork/canonicality review | Autopilot and ratified operational executors replace discretionary levers |

The transition is domain-specific. Validator governance, treasury routing,
constitutional amendment, public graph admission, emergency response, and
economic parameter changes may reach Transition or Mature status at different
times.

## 5. Sunset Trigger Framework

A future sunset transition for any domain must include all of the following:

1. A successor-authority identifier: the House, Court, Autopilot rule, validator
   governance path, or other ratified successor mechanism that takes over.
2. A domain boundary: exactly which Genesis authority function recedes.
3. Evidence of successor readiness: tests, simulations, private rehearsal,
   public operating data, or ratified review sufficient for that domain.
4. A challenge window: a bounded period during which objections can be raised.
5. A rollback or appeal rule: how erroneous sunset claims are challenged.
6. A public record artifact: a canonical graph/document record identifying the
   sunset domain, evidence, decision path, and effective epoch.
7. A non-silent fallback: if evidence is missing, ambiguous, or stale, Genesis
   authority does not silently sunset by assumption.

## 6. Minimum Domain Checklist Before Any Mature-State Claim

Before a future artifact can claim that Genesis authority has fully receded, it
must show that each domain below has a successor path:

| Domain | Successor mechanism required |
|---|---|
| Constitutional amendment | Ratified CDL path with community quorum and review |
| Emergency intervention | CDL-045 / CDL-V6 successor handling, or explicit expiry of the emergency path |
| Validator admission and ejection | CDL-017 runtime path plus activation evidence |
| Economic issuance and settlement | Default-off Block 4 runtime paths activated by the later public/economic gate |
| Public graph admission | Jury/review and type-authority machinery activated for public nodes |
| Fork legitimacy | CDL-009-facing legitimacy surface tied to canonical lineage |
| Genesis operational caps and reporting | Public reporting or machine-verifiable audit record |

## 7. Handoff Event Sequence

The canonical future handoff sequence is:

1. Successor-readiness evidence is produced for a bounded domain.
2. A public pre-deliberation artifact identifies the domain, successor authority,
   evidence, risk, and proposed effective epoch.
3. The applicable governance path ratifies or rejects the transition.
4. If ratified, a sunset record is committed with canonical identifiers and
   challenge-window metadata.
5. The effective epoch arrives only after challenge-window and publication
   requirements are satisfied.
6. Runtime or graph surfaces, if any, are updated in a separate implementation
   phase with their own tests and activation gates.
7. The next coherence or closure gate records the domain as receded.

## 8. Reporting Requirements

Until a domain has receded, Genesis actions in that domain must be reportable.
At minimum, the public or pre-public record must preserve:

- action identifier;
- authority basis;
- affected domain;
- rationale and evidence;
- challenge or review path;
- sunset effect, if any;
- non-effect statement when no authority change occurs.

## 9. Forbidden Interpretations

The following interpretations are rejected:

- Genesis authority has already sunset.
- Genesis authority can sunset by silence, elapsed wall-clock time, or informal
  intent.
- CDL-004 by itself activates a complete House/Court/Executive governance system.
- CDL-V6 is ordinary governance.
- Autopilot can amend constitutional state.
- A fork can become canonical by stripping Genesis lineage.
- This spec changes voting weight, validator authority, treasury authority, or
  public graph admission rules.

## 10. Closure of OBL-023

OBL-023 required a pre-public-RC spec for the CDL-004 Genesis authority sunset
model, including the court/house/executive structure and the Genesis-to-community
handoff path. This document provides that specification.

Actual sunset remains a future governance event. It requires separate
ratification, evidence, and implementation gates.

```text
obl_023_closed_phase_1547p
genesis_authority_not_sunset_phase_1547p
public_path_remains_blocked_phase_1547p
```

## 11. Non-Authorization

This specification does not sunset Genesis authority, amend CDL-004, invoke
CDL-V6, open or ratify a CDL, activate public governance, activate Autopilot,
write governance-node graph state, activate public RC, transition epoch, clear
guards, mint ECU, settle ILC, write wallets, write treasury state, or publish a
public repository.
