# ILC CDL-039 P2P Transport Baseline and Topology Privacy Evidence Prelock v0.1

Status: pre-ratification evidence prelock artifact
Date: 2026-03-05
Phase: 359

## 1. Purpose and scope

This artifact opens CDL-039 as a constrained prelock lane for P2P transport baseline governance.

Scope is constitutional opening only. No runtime implementation is authorized in this phase.

## 2. CDL-039 opening state

- decision_id: CDL-039
- status: open
- ratification state: not ratified
- lane role: constitutional opening with deferred prelock finalization

## 3. Option inventory and current candidate

Option inventory carried on row opening:
- centrally coordinated relay transport
- federated relay mesh
- brokerless peer-to-peer gossip baseline

Current candidate:
- brokerless peer-to-peer gossip baseline

## 4. No-central-broker baseline constraints

The no-central-broker invariant is the baseline requirement for CDL-039 and remains mandatory through prelock and ratification.

Operational framing is carried forward from roadmap v0.4:
- D2d wire protocol is elevated from technical plumbing to a communication resilience layer.
- Gossip-based discovery is the protocol immune system.
- partition-tolerant epoch consensus remains required.

## 5. Topology privacy constraints

Topology-privacy constraints are locked as open requirements in this phase:
- topology-opaque
- cluster membership comparison must not be derivable from public protocol data
- COSE kid must be a protocol-internal opaque identifier
- gossip topology privacy constraints

These remain requirement tokens and are not finalized mechanism choices in Phase 359.

## 6. Authoritative prelock evidence requirements (open, not finalized)

Section 6 is authoritative for later ratification when it is more specific than the compressed CDL row shorthand.

Authoritative evidence-prelock items:
- no-central-broker invariant evidence requirement
- topology privacy constraint requirement set
- partition divergence evidence dependency
- epoch timing attack-surface evidence dependency
- transport identity opacity requirement
- candidate mechanism comparison requirement

No finalized CDL-039 prelock invariants are locked in Phase 359.

## 7. Deferral and phase-boundary constraints

Phase boundary constraints:
- Phase 374 finalizes CDL-039 prelock design after SIM-004 and SIM-005 evidence.
- Levin gossip + coordinate mechanism proposals are deferred to Window 368 sequence-lock drafting.
- Phase 359 only opens the constitutional row and carries constrained requirement tokens.
- Schema changes still require CDL opening, evidence prelock, ratification, and closure-gate process.

## 8. Canonical anchors

- `docs/specs/ilc_phase_358_367_sequence_lock_v0.1.md`
- `docs/specs/ilc_distribution_architecture_roadmap_v0.4.md`
- `docs/specs/ilc_open_requirements_and_unknown_unknowns_analysis_354_v0.1.md`

