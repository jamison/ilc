# ILC CDL-040 Admission Control and Identity Envelope Prelock 383 v0.1

Status: prelock evidence (open, non-ratifying)  
Date: 2026-03-07  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

This artifact opens CDL-040 and records prelock evidence for admission-control policy and identity-envelope semantics with constitutional/document boundaries only.

## 2. CDL-040 opening state

- decision id: `CDL-040`
- status: open
- phase: 383
- ratification: deferred

No runtime implementation occurs in Phase 383.

## 3. Identity-envelope disambiguation

CDL-040 identity envelope is a structured extension of the Authored Payload envelope defined in CDL-034, not a fourth envelope type; CDL-034's authorship attribution requirement is inherited without modification.

## 4. Admission-control scope boundary

Admission control is a network-layer governance mechanism and is explicitly separate from knowledge-claim evaluation governed by CDL-V7 and the 7+1 evaluation panel; admission does not constitute knowledge-claim acceptance.

## 5. Calibration constants and exclusivity boundary

Prelock calibration parameters for CDL-040 are tracked in this section only:
- `identity_binding_grace_epochs` - candidate range under review
- `admission_stake_floor` - candidate floor under review
- `admission_quorum_floor` - candidate floor under review

## 6. CDL-039 dependency and enforceability

CDL-040 admission control enforceability is conditional on CDL-039 ratification providing Transport Envelope privacy invariants; CDL-039 is ratified in Phase 379.

## 7. Deferral and phase-boundary constraints

- Phase 383 is opening/prelock only.
- No CDL-040 ratification action occurs in this phase.
- No companion CDL-034 amendment row is opened in this phase.
- Any runtime implementation is deferred to a later authorized runtime window.

## 8. Canonical anchors

- `docs/adr/ADR_0014_Identity_Sybil_and_Admission_Control_Envelope.md`
- `docs/specs/ilc_phase_378_391_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_039_p2p_transport_and_topology_privacy_ratification_evidence_379_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
