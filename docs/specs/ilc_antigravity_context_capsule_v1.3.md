# ILC Antigravity Context Capsule v1.3

Supersedes: docs/specs/ilc_antigravity_context_capsule_v1.2.md

This capsule is self-contained.

## 1. Project identity

ILC remains a ratification-first constitutional protocol for epistemic-graph coordination with bounded runtime implementation authorization and commit-anchored mutation guardrails.

## 2. Core architectural invariants

- Decision-log mutation remains CDL-governed and explicitly auditable.
- Envelope separation remains mandatory (authored payload, transport envelope, protocol interpretation).
- D2d runtime enforcement and constitutional lane outputs remain separated by sensitivity and mutation-scope contracts.
- Governance-procedural V-series work remains distinct from computational V-series implementation.

## 3. Project state (as of Phase 390 completion)

Phase 390 complete.

Phase 391 next.

Window 378-391 is in closure-prep state with ratified CDL-039, implemented D2d runtime surfaces, and implemented CDL-V1/V2 computational runtimes.

## 4. CDL-039 ratification and carry-forward obligation state

CDL-039 is ratified as of Phase 379 with calibration constants locked.

CDL-039 ratification forward obligation: retention_epochs requires a named CDL amendment to be opened as the first constitutional action of Window 392+.

## 5. D2d runtime enforcement state

D2d wire protocol is implemented in ilc_core/network/d2d/ and enforces CDL-039 transport invariants.

Implemented surfaces:
- `ilc_core/network/d2d/interface.py`
- `ilc_core/network/d2d/peer.py`
- `ilc_core/network/d2d/gossip.py`

## 6. CDL-040/041/043 prelock state

CDL-040/041/043 prelocks are complete and non-ratifying; ratification is deferred to Window 392+.

## 7. V-series runtime state

CDL-V1 temporal decay and CDL-V2 sybil resistance are computationally enforced as of Phases 388/389.

V-series runtime modules:
- `ilc_core/reputation/temporal_decay_runtime.py`
- `ilc_core/identity/sybil_resistance_runtime.py`

## 8. CDL-V3/V7 governance state

CDL-V3 and CDL-V7 governance resolution: deferred to Window 392+.

## 9. Window 392+ forward boundary

Window 392+ begins with:
- named retention_epochs amendment opening,
- CDL-040/041/043 ratification planning,
- CDL-042 opening,
- CDL-V3/V7 governance resolution.

## 10. Change log from v1.2

Changed relative to v1.2:
- CDL-039 status updated from prelock-finalized/open to ratified,
- added named retention_epochs forward-obligation token,
- added D2d runtime implementation state summary,
- added CDL-V1/V2 computational-enforcement state summary,
- updated forward-boundary framing for Window 392+.

## 11. Key canonical anchors

- `docs/specs/ilc_antigravity_context_capsule_v1.2.md`
- `docs/specs/ilc_phase_378_391_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_039_p2p_transport_and_topology_privacy_ratification_evidence_379_v0.1.md`
- `docs/specs/ilc_d2d_abstract_interface_runtime_handoff_380_v0.1.md`
- `docs/specs/ilc_d2d_peering_runtime_handoff_381_v0.1.md`
- `docs/specs/ilc_d2d_gossip_runtime_handoff_382_v0.1.md`
- `docs/specs/ilc_cdl_040_admission_control_and_identity_envelope_prelock_383_v0.1.md`
- `docs/specs/ilc_cdl_041_shard_lifecycle_prelock_384_v0.1.md`
- `docs/specs/ilc_cdl_043_storage_economics_prelock_385_v0.1.md`
- `docs/specs/ilc_sim_006_007_commissioning_results_386_v0.1.md`
- `docs/specs/ilc_v_series_implementation_authorization_lock_387_v0.1.md`
- `docs/specs/ilc_cdl_v1_temporal_decay_runtime_handoff_388_v0.1.md`
- `docs/specs/ilc_cdl_v2_sybil_resistance_runtime_handoff_389_v0.1.md`
- `docs/specs/ilc_integration_coherence_report_390_v0.1.md`
