# ILC CDL-039 Topology Privacy Hardening Prelock 372 v0.1

Status: Phase-372 prelock hardening artifact  
Date: 2026-03-06  
Owner lane: G8 Constitution Cluster A

## 1. Scope and non-ratifying boundary

This artifact hardens CDL-039 topology/privacy prelock requirements using Phase-359 opening constraints, Phase-371 interpretation closure, and non-ratifying SIM evidence.

Modeled outputs are non-ratifying evidence inputs.

No decision-log mutation occurred. No ilc_core runtime files were changed.

## 2. Input evidence and interpretation anchors

Primary anchors:
- `docs/specs/ilc_cdl_039_p2p_transport_baseline_and_topology_privacy_evidence_prelock_359_v0.1.md`
- `docs/specs/ilc_cdl_039_prelock_invariant_input_addendum_371_v0.1.md`
- `docs/specs/ilc_sim_003_004_005_interpretation_and_cdl_039_risk_closure_371_v0.1.md`

This artifact extends the Phase-359 prelock additively; both documents serve as CDL-039 prelock evidence for future ratification.

Phase-371 contract consumption is explicit:
- SIM taxonomy table is consumed as canonical numbering for current window,
- epoch-type interpretation table for SIM-003/SIM-004/SIM-005 is consumed unchanged,
- constant lock/readiness flags are consumed to separate Phase-372 locks from Phase-373 calibration.

## 3. Invariant 1 - transport header non-authorship

Transport Envelope routing headers MUST NOT carry creator_agent_id; authorship attribution is resolved from Authored Payload and protocol interpretation.

Current Phase-362 dissemination runtime is v0.1 state; target invariant is enforced at the authorized Window 378+ D2d/network runtime implementation boundary.

## 4. Invariant 2 - partition-state cross-cluster reference rate limiting

When partition-state is asserted by the gossip coordinate system, nodes MUST apply a cross-cluster reference creation rate limit not exceeding R_partition_cross_ref per epoch, emit deterministic backpressure signaling, and maintain release hysteresis H_release.

Interpretation lock from Phase 371:
- short-timescale controls operate in validation-epoch context,
- long-timescale partition divergence remains issuance-epoch constrained.

## 5. Invariant 3 - cluster membership non-inferrability

Dissemination headers and gossip messages MUST NOT enable a passive observer to reconstruct the membership set of any cluster.

Phase-373 adversarial tests must include passive-observer reconstruction attempts as mandatory probes.

## 6. Invariant 4 - private-visibility expiry and promotion boundary

Private-visibility nodes without a valid promotion_receipt after retention_epochs MUST be treated as expired and ineligible for direct promotion.

CDL-038 scope boundary for post-expiry recovery semantics remains an explicit open question for prelock text closure.

## 7. Invariant 5 - opaque channel routing identifier

Transport channel routing field MUST be an opaque identifier (CID or uniformly random bytes); human-readable channel labels are UI-layer concerns only.

Current Phase-362 channel enum usage is v0.1 state; target opaque-identifier invariant is enforced at the authorized Window 378+ D2d/network runtime implementation boundary.

## 8. Two-timescale CDL-039 closure requirements

short-timescale CDL-039 context: validation epoch liveness and Levin stress-cascade reconnection handling.

long-timescale CDL-039 context: issuance epoch partition divergence and highest_ecu_wins reconciliation.

A single undifferentiated epoch assumption is prohibited for CDL-039 prelock text.

## 9. Phase 373 calibration queue

Phase 373 calibrates unresolved parameters: R_partition_cross_ref, H_release, retention_epochs, timeout/recovery policy constants.

Calibration expectations:
- adversarial stress for partition-state flapping,
- adversarial stress for timeout false-positive/false-negative tradeoff,
- adversarial stress for privacy leakage under channel/header observations.

## 10. Implementation-boundary notes for Window 378+

Window 378+ carries runtime enforcement for target invariants that diverge from v0.1 runtime state:
- invariant 1 (non-authorship transport header),
- invariant 5 (opaque channel identifier).

No standing compatibility/profile dual-mode is introduced as a protocol feature.

## 11. Non-goals and unresolved questions

Non-goals:
- no CDL-039 ratification,
- no decision-log mutation,
- no runtime implementation.

Unresolved questions held for calibration or later closure:
- final values for `R_partition_cross_ref` and `H_release`,
- final value for `retention_epochs` under validated epoch interpretation and CDL-038 boundary handling,
- final timeout/recovery constant binding from SIM-005 under adversarial evidence.
