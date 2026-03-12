# ILC Antigravity Context Capsule v1.4

Supersedes: docs/specs/ilc_antigravity_context_capsule_v1.3.md

This capsule is self-contained.

## 1. Project identity

ILC remains a governance-first constitutional protocol with bounded runtime implementation lanes and commit-anchored mutation guardrails.

## 2. Core architectural invariants

- Constitutional mutation remains decision-log scoped and auditable.
- Runtime mutation scope remains phase-authorized and test-anchored.
- Envelope separation remains mandatory for authored, protocol-interpretation, and transport boundaries.
- Wallet-agnostic signing remains mandatory at protocol boundary.

## 3. Project state (as of Phase 400 completion)

Phase 400 complete.

Phase 401 next.

Window 392-401 is in closure-prep state with constitutional settlement complete through CDL-044 and V-series runtime enforcement active.

## 4. Constitutional ratification state

CDL-039/040/041/043/044 are ratified in the current constitutional register.

CDL-044 is ratified as of Phase 399 and closes the retention_epochs constitutional amendment obligation created by CDL-039 ratification.

## 5. Runtime implementation state

CDL-V1 temporal decay, CDL-V2 sybil resistance, CDL-V3 diversity floor, and CDL-V7 Popperian gate are computationally enforced.

Active runtime modules:
- `ilc_core/reputation/temporal_decay_runtime.py`
- `ilc_core/identity/sybil_resistance_runtime.py`
- `ilc_core/consensus/diversity_floor_runtime.py`
- `ilc_core/consensus/popperian_gate_runtime.py`

## 6. Runtime-integrity and validation guarantees

Runtime-integrity note: V-series validators reject non-finite numeric inputs (NaN/Inf).

Validation guarantees remain deterministic and tokenized for invalid inputs, including non-finite values.

## 7. Wallet-agnostic signing continuity

Wallet-agnostic signing remains mandatory: signer-lineage lifecycle is protocol-layer and signing-provider key custody is an operator concern.

ADM-003 v0.2 adds explicit signing-provider interface contract closure for wallet-agnostic implementation lanes.

## 8. Window 401 and 402+ forward boundary

Window 401 closes the 392-401 block with gate verification and handoff synthesis.

Window 402+ starts with deferred constitutional openings (including CDL-042) and next-window expansion lanes.

## 9. Change log from v1.3

Changed relative to v1.3:
- constitutional state updated to include CDL-044 ratified closure,
- added explicit runtime-integrity non-finite guard carry-forward,
- added ADM-003 v0.2 signing-provider interface closure reference,
- updated boundary framing from Window 392+ startup to Window 401 closure readiness.

## 10. Key canonical anchors

- `docs/specs/ilc_antigravity_context_capsule_v1.3.md`
- `docs/specs/ilc_phase_392_401_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_044_retention_epochs_amendment_ratification_evidence_399_v0.1.md`
- `docs/specs/ilc_integration_coherence_report_400_v0.1.md`
- `docs/specs/ilc_cdl_v3_diversity_floor_runtime_handoff_397_v0.1.md`
- `docs/specs/ilc_cdl_v7_popperian_gate_runtime_handoff_398_v0.1.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.2.md`
