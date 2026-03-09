# ILC CDL-040 Ratification Evidence v0.1

Status: ratification evidence artifact
Date: 2026-03-09
Decision lane: G8 Constitution Cluster A

## 1. Purpose and scope

This artifact ratifies CDL-040 for admission-control policy and identity-envelope semantics using the Phase-383 prelock and the Phase-392 sequence-lock constraints.

## 2. Ratified decision

Ratified option:
- identity-envelope extension of authored payload

CDL-040 ratifies Option A: identity envelope is a structured extension of the Authored Payload envelope under CDL-034; no fourth envelope type is introduced.

## 3. Evidence basis

Canonical evidence anchors:
- `docs/specs/ilc_cdl_040_admission_control_and_identity_envelope_prelock_383_v0.1.md`
- `docs/specs/ilc_phase_392_401_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_039_p2p_transport_and_topology_privacy_ratification_evidence_379_v0.1.md`
- `docs/specs/ilc_window_378_391_handoff_391_v0.1.md`
- `docs/adr/ADR_0014_Identity_Sybil_and_Admission_Control_Envelope.md`

## 4. Section-3 authoritative evidence checklist satisfaction

Checklist satisfaction statements:
1. Option-A identity-envelope semantics from Phase-383 prelock are preserved,
2. admission-control scope boundary remains distinct from CDL-V7/7+1 knowledge-claim acceptance,
3. calibration dispositions from Phase-383 are resolved in Section 5,
4. CDL-039 dependency boundary remains ratified and inherited,
5. no fourth-envelope companion amendment is introduced in this phase.

## 5. Calibration constants resolution

Ratification calibration dispositions:
- `identity_binding_grace_epochs`: constitutional bound `1 <= identity_binding_grace_epochs <= 3`.
- `admission_stake_floor`: constitutional floor `admission_stake_floor >= 0.05`.
- `admission_quorum_floor`: constitutional floor `admission_quorum_floor >= 0.67`.

## 6. Scope boundary and dependency closure

Admission control remains network-layer governance and does not constitute knowledge-claim acceptance under CDL-V7 or 7+1 panel semantics.

CDL-040 enforceability remains conditional on CDL-039 transport privacy invariants ratified in Phase 379.

## 7. Carry-forward constraints

CDL-042 opening remains sequenced after CDL-040, CDL-041, and CDL-043 ratification steps defined in the Phase-392 sequence lock.

No standing compatibility profile dual-mode is introduced as a protocol feature.

## 8. Runtime deferral boundary

No runtime implementation of CDL-040 is ratified in Phase 393.

Runtime implementation remains deferred to a later authorized runtime window.

## 9. Canonical anchors

Constitutional anchors:
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_phase_392_401_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_040_admission_control_and_identity_envelope_prelock_383_v0.1.md`
- `docs/specs/ilc_window_378_391_handoff_391_v0.1.md`
