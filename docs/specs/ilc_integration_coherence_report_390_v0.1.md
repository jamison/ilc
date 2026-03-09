# ILC Integration Coherence Report 390 v0.1

Status: Phase-390 coherence artifact  
Date: 2026-03-09  
Owner lane: G8 Constitution Cluster A

## 1. Scope and non-ratifying boundary

This artifact consolidates Window 378-391 outputs through Phase 389 into a coherent handoff state for Phase 391 closure preparation.

No decision-log mutation occurred. No ilc_core runtime files were changed.

## 2. CDL-039 ratification and hardening closure

CDL-039 is ratified as of Phase 379 with calibration constants locked.

Ratification closure points:
- CDL-036 header-field reconciliation is in effect in the ratification evidence lane.
- Four-prelock hardening chain (`359`, `372`, `373`, `374`) remains verifiable through the ratification test chain.
- Ratification evidence document remains `docs/specs/ilc_cdl_039_p2p_transport_and_topology_privacy_ratification_evidence_379_v0.1.md`.

The four-prelock hardening chain (`359`, `372`, `373`, `374`) remains mandatory for ratification continuity checks.

CDL-039 ratification created a named forward obligation: retention_epochs operational value requires a subsequent CDL amendment before deployment. This amendment must be opened as the first constitutional action of Window 392+.

## 3. D2d runtime implementation state

D2d wire protocol implementation is active under `ilc_core/network/d2d/` with three runtime surfaces:
- `interface.py` (Phase 380)
- `peer.py` (Phase 381)
- `gossip.py` (Phase 382)

Computationally enforced CDL-039 transport invariants include:
- no `creator_agent_id` in transport headers,
- opaque channel routing field validation,
- cluster membership non-inferrability enforcement token in gossip runtime.

## 4. CDL-040/041/043 prelock state and ratification boundary

Current prelock state:
- `CDL-040`: open (admission control and identity envelope prelock)
- `CDL-041`: open (shard lifecycle prelock)
- `CDL-043`: open (storage economics prelock)

Ratification boundary:
- all three prelocks remain non-ratifying,
- ratification planning for this cluster is deferred to Window 392+.

## 5. SIM-006/007 governance evidence state

SIM-006 and SIM-007 commissioning outputs are locked as non-ratifying governance evidence.

Evidence-use boundaries:
- SIM-006 feeds CDL-V7 extension planning and capability-heterogeneity governance analysis.
- SIM-007 feeds CDL-035 timed_out extension planning and D2d-10/11 wire-spec planning.
- both manifests include explicit epoch contexts and deterministic artifact digests.

## 6. CDL-V1/V2 runtime implementation state

Runtime implementation state:
- CDL-V1 temporal decay runtime implemented in `ilc_core/reputation/temporal_decay_runtime.py` with dependency lock `CDL_V1_DEPENDENCY = "cdl_v1_temporal_decay_388.v0.1"`.
- CDL-V2 sybil-resistance runtime implemented in `ilc_core/identity/sybil_resistance_runtime.py` with dependency lock `CDL_V2_DEPENDENCY = "cdl_v2_sybil_resistance_389.v0.1"`.
- runtime dependency chain is continuous (`CDL_V2` imports and locks `CDL_V1_DEPENDENCY`).

Test-state summary:
- `tests/test_cdl_v1_temporal_decay_runtime_388.py`: 12 passed.
- `tests/test_cdl_v2_sybil_resistance_runtime_389.py`: 12 passed.

## 7. CDL-V3/V7 declaration and Window 392+ forward boundary

CDL-V3 and CDL-V7 governance resolution remains deferred to Window 392+ based on current SIM-006 evidence state.

Wallet-agnostic signing carry-forward remains active: ILC protocol signing is wallet-agnostic, signer-lineage lifecycle is protocol-layer, and signing-provider key custody remains an operator concern.

Window 392+ forward boundary open items:
- first constitutional action must open the named retention_epochs amendment required by CDL-039 ratification.
- ratification planning for CDL-040/041/043 prelocks.
- CDL-042 opening (agent identity namespace).
- CDL-V3/V7 governance resolution lane.

## 8. Non-goals and canonical anchors

Non-goals in this phase:
- no decision-log mutation,
- no runtime implementation,
- no ratification action,
- no mutation of `ilc_core/`.

Canonical anchors:
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
