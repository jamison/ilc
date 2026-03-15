# ILC Antigravity Context Capsule v1.6

Supersedes: docs/specs/ilc_antigravity_context_capsule_v1.5.md

This capsule is self-contained.

## 1. Project identity

ILC remains a governance-first constitutional protocol with bounded runtime implementation lanes, explicit phase sequencing, and commit-anchored mutation guardrails.

## 2. Core architectural invariants

- Constitutional mutation remains decision-log scoped and auditable.
- Runtime mutation scope remains phase-authorized and test-anchored.
- Envelope separation remains mandatory for authored, protocol-interpretation, and transport boundaries.
- Wallet-agnostic signing remains mandatory at protocol boundary.
- Ratified constants and dependency tokens remain machine-auditable once promoted into runtime.

## 3. Project state (as of Phase 422 completion)

Phase 422 complete.

Phase 423 next.

Window 414-423 is in closure-prep state with constitutional settlement complete through CDL-048 and the D2e CLI block implemented through Phases 420 and 421.

## 4. Constitutional ratification state

CDL-047 and CDL-048 are ratified in the current constitutional register.

CDL-047 is ratified as of Phase 418 with bounty cap 0.15 x B_e, burn floor 0.05, and velocity alert floor 0.91.

CDL-048 is ratified as of Phase 419 with ecu_conversion_deadline = 4 issuance epochs.

CDL-049 remains unopened and is reserved as the Window-424+ planning boundary for bounded-existential alignment.

## 5. Runtime implementation state

CDL-V1 temporal decay, CDL-V2 sybil resistance, CDL-V3 diversity floor, and CDL-V7 Popperian gate are computationally enforced.

D2e runtime and CLI block status:
- `ilc_core/identity/agent_id_runtime.py` implements Phase-410 agent identity derivation with `AGENT_ID_RUNTIME_VERSION = "agent_id_runtime_410.v0.1"`.
- `ilc_core/node/timed_out_lifecycle_runtime_411.py` implements Phase-411 timed-out lifecycle constants with `TIMED_OUT_LIFECYCLE_RUNTIME_VERSION = "timed_out_lifecycle_runtime_411.v0.1"`.
- `ilc_core/cli/d2e_agent_cli.py` implements Phase-420 agent CLI wiring with `D2E_AGENT_CLI_VERSION = "d2e_agent_cli_420.v0.1"`.
- `ilc_core/cli/d2e_lifecycle_cli.py` implements Phase-421 lifecycle CLI wiring with `D2E_LIFECYCLE_CLI_VERSION = "d2e_lifecycle_cli_421.v0.1"`.

## 6. Runtime-integrity and validation guarantees

Runtime-integrity note: V-series validators reject non-finite numeric inputs (NaN/Inf).

Validation guarantees remain deterministic and tokenized for invalid inputs in V-series lanes, D2e runtime lanes, and D2e CLI lanes.

## 7. Wallet-agnostic signing continuity

Wallet-agnostic signing remains mandatory: signer-lineage lifecycle is protocol-layer and signing-provider key custody is an operator concern.

ADM-003 v0.2 remains the active signing-provider interface closure for wallet-agnostic implementation lanes.

## 8. Window 423 and 424+ forward boundary

Window 423 is the closure-gate lane for Window 414-423.

Window 424+ is the earliest authorized boundary for CDL-049 planning, possible D2e CLI expansion, and any SIM-009 follow-on modeling.

## 9. Change log from v1.5

Changed relative to v1.5:
- constitutional state updated to include CDL-047 and CDL-048 ratified closure,
- added D2e CLI block state for Phase 420 and Phase 421,
- added Window-424+ forward pointer for CDL-049 planning boundary,
- updated forward-boundary framing from Window 413 closure readiness to Window 423 closure readiness,
- preserved wallet-agnostic signing and runtime-integrity carry-forward unchanged.

## 10. Key canonical anchors

- `docs/specs/ilc_antigravity_context_capsule_v1.5.md`
- `docs/specs/ilc_phase_414_423_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_047_treasury_governance_ratification_evidence_418_v0.1.md`
- `docs/specs/ilc_cdl_048_ecu_mandatory_conversion_deadline_ratification_evidence_419_v0.1.md`
- `docs/specs/ilc_popperian_claim_form_governance_review_417_v0.1.md`
- `docs/specs/ilc_d2e_agent_cli_handoff_420_v0.1.md`
- `docs/specs/ilc_d2e_lifecycle_cli_handoff_421_v0.1.md`
- `docs/specs/ilc_integration_coherence_report_422_v0.1.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.2.md`
