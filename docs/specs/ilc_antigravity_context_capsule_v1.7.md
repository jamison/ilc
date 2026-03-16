# ILC Antigravity Context Capsule v1.7

Supersedes: docs/specs/ilc_antigravity_context_capsule_v1.6.md

This capsule is self-contained.

## 1. Project identity

ILC remains a governance-first constitutional protocol with bounded runtime implementation lanes,
explicit phase sequencing, and commit-anchored mutation guardrails.

## 2. Core architectural invariants

- Constitutional mutation remains decision-log scoped and auditable.
- Runtime mutation scope remains phase-authorized and test-anchored.
- Envelope separation remains mandatory for authored, protocol-interpretation, and transport
  boundaries.
- Wallet-agnostic signing remains mandatory at protocol boundary.
- Ratified constants and dependency tokens remain machine-auditable once promoted into runtime.

## 3. Project state (as of Phase 432 completion)

Phase 432 complete.

Phase 433 next.

Window 424-433 is in closure-prep state with the obligated CDL-049 constitutional lane complete and
the Treasury P_e branch explicitly carried forward rather than force-fit into unsafe in-window
constitutional compression.

## 4. Constitutional ratification and carry-forward state

CDL-047, CDL-048, and CDL-049 are ratified in the current constitutional register.

`CDL-050` remains unopened in Window 424-433.

Treasury P_e constitutional lane carries into Window 434+ with provisional planning anchor 0.2 / 0.02 and no locked P_e constants.

## 5. Runtime implementation state

CDL-V1 temporal decay, CDL-V2 sybil resistance, CDL-V3 diversity floor, and CDL-V7 Popperian gate
are computationally enforced.

The active Popperian runtime and forward-facing analysis corpus now use bounded_existential as the admitted bounded claim-form token.

D2e runtime and CLI block status:
- `ilc_core/identity/agent_id_runtime.py` implements Phase-410 agent identity derivation with `AGENT_ID_RUNTIME_VERSION = "agent_id_runtime_410.v0.1"`.
- `ilc_core/node/timed_out_lifecycle_runtime_411.py` implements Phase-411 timed-out lifecycle constants with `TIMED_OUT_LIFECYCLE_RUNTIME_VERSION = "timed_out_lifecycle_runtime_411.v0.1"`.
- `ilc_core/cli/d2e_agent_cli.py` implements Phase-420 agent CLI wiring with `D2E_AGENT_CLI_VERSION = "d2e_agent_cli_420.v0.1"`.
- `ilc_core/cli/d2e_lifecycle_cli.py` implements Phase-421 lifecycle CLI wiring with `D2E_LIFECYCLE_CLI_VERSION = "d2e_lifecycle_cli_421.v0.1"`.

## 6. Treasury P_e branch state

Phase 426 authorized Scenario B.

Phase 429 commissioned SIM-009, Phase 430 synthesized its limitations, and Phase 431 published the
carry-forward decision.

Treasury P_e trigger and limit constants remain unratified because the current evidence basis is
insufficient for immediate constitutional locking.

## 7. Wallet-agnostic signing and runtime-integrity continuity

Wallet-agnostic signing remains mandatory: signer-lineage lifecycle is protocol-layer and signing-provider key custody is an operator concern.

Runtime-integrity note: V-series validators reject non-finite numeric inputs (NaN/Inf).

## 8. Window 433 and 434+ forward boundary

Window 433 is the closure-gate lane for Window 424-433.

Window 434+ is the default continuation boundary for Treasury P_e constitutional work; any future CDL-050 opening remains contingent and not pre-authorized by Window 424-433.

## 9. Change log from v1.6

Changed relative to v1.6:
- constitutional state updated to include CDL-049 ratified closure,
- added the Treasury P_e Scenario B carry-forward state from Phases 426, 430, and 431,
- updated Popperian runtime state to bounded-existential vocabulary,
- updated forward-boundary framing from Window 423 closure readiness to Window 433 closure readiness,
- preserved wallet-agnostic signing and runtime-integrity carry-forward unchanged.

## 10. Key canonical anchors

- `docs/specs/ilc_antigravity_context_capsule_v1.6.md`
- `docs/specs/ilc_phase_424_433_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_049_bounded_existential_alignment_ratification_evidence_427_v0.1.md`
- `docs/specs/ilc_treasury_pe_stabilization_governance_review_426_v0.1.md`
- `docs/specs/ilc_sim_009_pe_stabilization_commissioning_429_v0.1.md`
- `docs/specs/ilc_sim_009_results_synthesis_and_pe_stabilization_disposition_430_v0.1.md`
- `docs/specs/ilc_pe_stabilization_carry_forward_decision_431_v0.1.md`
- `docs/specs/ilc_integration_coherence_report_432_v0.1.md`
