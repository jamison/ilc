# ILC Antigravity Context Capsule v1.5

Supersedes: docs/specs/ilc_antigravity_context_capsule_v1.4.md

This capsule is self-contained.

## 1. Project identity

ILC remains a governance-first constitutional protocol with bounded runtime implementation lanes, explicit phase sequencing, and commit-anchored mutation guardrails.

## 2. Core architectural invariants

- Constitutional mutation remains decision-log scoped and auditable.
- Runtime mutation scope remains phase-authorized and test-anchored.
- Envelope separation remains mandatory for authored, protocol-interpretation, and transport boundaries.
- Wallet-agnostic signing remains mandatory at protocol boundary.
- Ratified constants and dependency tokens remain machine-auditable once promoted into runtime.

## 3. Project state (as of Phase 412 completion)

Phase 412 complete.

Phase 413 next.

Window 402-413 is in closure-prep state with constitutional settlement complete through CDL-046, SIM-008 evidence commissioned, and the first D2e runtime block implemented.

## 4. Constitutional ratification state

CDL-039, CDL-040, CDL-041, CDL-043, CDL-044, CDL-042, CDL-045, and CDL-046 are ratified in the current constitutional register.

CDL-042 is ratified as of Phase 407 and closes the agent identity namespace gate for D2e Agent SDK implementation.

CDL-045 is ratified as of Phase 408 with the automated circuit breaker with CDL-V3 diversity quorum trigger and CDL-V6 sunset.

CDL-046 is ratified as of Phase 409 and closes the CDL-035 timed_out amendment obligation for orphan recovery.

## 5. Runtime implementation state

CDL-V1 temporal decay, CDL-V2 sybil resistance, CDL-V3 diversity floor, and CDL-V7 Popperian gate are computationally enforced.

D2e runtime block status:
- `ilc_core/identity/agent_id_runtime.py` implements Phase-410 agent identity derivation with `AGENT_ID_RUNTIME_VERSION = "agent_id_runtime_410.v0.1"`, `CDL_042_DEPENDENCY = "cdl_042_ratified_407.v0.1"`, and `NODE_SCHEMA_DEPENDENCY = "cdl_038_ratified_353.v0.1"`.
- `ilc_core/node/timed_out_lifecycle_runtime_411.py` implements Phase-411 timed-out lifecycle constants with `TIMED_OUT_LIFECYCLE_RUNTIME_VERSION = "timed_out_lifecycle_runtime_411.v0.1"`, `CDL_046_DEPENDENCY = "cdl_046_ratified_409.v0.1"`, and `LIFECYCLE_BASE_DEPENDENCY = "cdl_035_ratified_350.v0.1"`.

## 6. Runtime-integrity and validation guarantees

Runtime-integrity note: V-series validators reject non-finite numeric inputs (NaN/Inf).

Validation guarantees remain deterministic and tokenized for invalid inputs, including non-finite values in V-series lanes and typed input validation in the D2e runtime block.

## 7. Wallet-agnostic signing continuity

Wallet-agnostic signing remains mandatory: signer-lineage lifecycle is protocol-layer and signing-provider key custody is an operator concern.

ADM-003 v0.2 remains the active signing-provider interface closure for wallet-agnostic implementation lanes.

## 8. Window 413 and 414+ forward boundary

Phase 413 closes the 402-413 block with gate verification and handoff synthesis.

SIM-008 post-issuance transition modeling results are available as evidence for Window-414+ Treasury Governance and ECU mandatory conversion deadline CDL planning.

Window 414+ is the earliest authorized boundary for the deferred D2e CLI integration lane and for the next economic constitutional openings.

## 9. Change log from v1.4

Changed relative to v1.4:
- constitutional state updated to include CDL-042, CDL-045, and CDL-046 ratified closure,
- added SIM-008 carry-forward for Window-414+ economic CDL planning,
- added D2e runtime block state for Phase 410 and Phase 411,
- updated forward-boundary framing from Window 401 closure readiness to Window 413 closure readiness,
- preserved wallet-agnostic signing and runtime-integrity carry-forward unchanged.

## 10. Key canonical anchors

- `docs/specs/ilc_antigravity_context_capsule_v1.4.md`
- `docs/specs/ilc_phase_402_413_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_042_agent_identity_namespace_ratification_evidence_407_v0.1.md`
- `docs/specs/ilc_cdl_045_operational_emergency_response_ratification_evidence_408_v0.1.md`
- `docs/specs/ilc_cdl_046_timed_out_amendment_ratification_evidence_409_v0.1.md`
- `docs/specs/ilc_sim_008_commissioning_results_406_v0.1.md`
- `docs/specs/ilc_integration_coherence_report_412_v0.1.md`
- `docs/specs/ilc_d2e_agent_id_runtime_handoff_410_v0.1.md`
- `docs/specs/ilc_d2e_timed_out_lifecycle_runtime_handoff_411_v0.1.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.2.md`
