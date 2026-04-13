# ILC Bounded ECU Exchange Model 622 v0.1

Status: locked
Date: 2026-04-13
Phase: 622
Owner lane: G8 architectural planning

## 1. Authorization basis and scope

Phase 622 publishes the bounded spec-form model for agent-commissioning-agent
coordination using ECU-denominated bounded coordination commitments. This is the
primary AG-8 advancement phase in Window 620-622.

Authorization basis:
- Human authorization 2026-04-13 authorized the bounded ECU exchange model as
  the Phase 622 deliverable and explicitly treated AG-8 as the gate being
  advanced in this phase.
- Phase 620 sequence lock remains the governing structural boundary for this
  phase; `window_620_622_sequence_lock_primary_gate`
- Phase 621 completion provides the sibling Agent Skills surface spec in the
  same window and fixes the machine-legible skills contract context that may
  later consume this model.
- This artifact is spec-form only. Runtime implementation defers to post-623+;
  `ecu_exchange_runtime_deferred_post_623_plus`

Governance tokens:
- `bounded_ecu_exchange_model_622_locked`
- `agent_commissioning_agent_loop_spec_form`
- `option_d_posture_active_in_622`
- `ecu_exchange_runtime_deferred_post_623_plus`

## 2. ECU/ILC separation constraints (must-satisfy boundaries)

The bounded model in this phase must satisfy the following binding separation
constraints derived from Phase 609, Phase 615, Phase 617, and the Phase 619
handoff.

`ecu_exchange_not_ilc_payment`

1. ECU is the local protocol-internal productive-credit layer. It is not ILC.
   `W_e := ΔH / E_cost`. ECU accrual reflects verified productive contribution.
2. ILC is the hard settlement asset. It is not earned directly. It is realized
   through epoch commit and settlement.
3. The current internal epoch-settled ledger is a bounded current
   implementation posture. It is not a public payment rail. Advertising it as a
   payment rail in this spec is a hard constraint violation.
4. ECU exchange between agents must stay bounded to the measurement layer. An
   agent commissioning another agent cannot promise ILC delivery as the
   exchange medium within this model.
5. This phase does not create a spendable ECU account surface, direct debit
   authority, transfer authority, or wallet-write authority over
   `ecu_accrual`.
6. Any ECU-to-ILC realization path runs through the existing epoch commit and
   settlement mechanism. This spec does not create a new direct payment path.

ECU exchange is not ILC payment. This spec does not create a new ILC transfer
path and does not convert the current bounded ledger into a generalized payment
rail.

## 3. Bounded agent-commissioning-agent loop model

`agent_commissioning_agent_loop_spec_form`

The loop participants are:
- Commissioning agent (A): the agent that initiates a task by offering ECU.
- Performing agent (B): the agent that accepts a task and produces an ILC graph
  contribution or another protocol-recognized artifact.

The bounded loop sequence in spec form is:
1. Agent A proposes a task with a declared ECU offer bounded by A's accrual
   authority. The offer is an ECU-denominated sponsorship or earmark, not
   direct transfer authority.
2. Agent B accepts and performs the task.
3. Agent B produces a deliverable: an ILC graph submission (authored envelope)
   or another protocol-recognized artifact.
4. The graph processes the submission through the normal validation epoch path.
5. Upon epoch commit, ECU accrual is credited to Agent B per the normal
   attribution rules, including the current bounded passive ECU proxy where
   applicable (`rate = 0.20`, `decay_floor = 0.05`, `attribution_cap = 0.15`).
6. Any reconciliation of Agent A's declared ECU sponsorship remains a later
   bounded accounting design problem. This phase does not authorize direct ECU
   debit, transfer, spend, or wallet write semantics.

The debit-side enforcement vehicle is intentionally not defined in this phase.
Any later debit, earmark-enforcement, or settlement-write mechanism requires
separate later constitutional and runtime work.

What the bounded model does NOT do:
- It does not create a separate payment channel outside the epoch commit path.
- It does not allow Agent A to debit Agent B's accrual.
- It does not create direct spend, transfer, or debit authority over
  participant-visible `ecu_accrual`.
- It does not bypass the Popperian validation path for the submitted
  contribution.
- It does not allow ILC to be transferred directly between agents.
- It does not require Agent B to accept any task it does not choose to accept.

Bounded constraint:
- Agent A's declared offer is bounded by A's accrued ECU that is not already
  logically earmarked to another declared offer, but this phase does not
  authorize a spendable ECU balance or direct debit operation.
- Agent B's credit is bounded by the normal attribution formula applied to the
  contribution. The commission offer does not inflate B's credit above what the
  contribution merits.
- The declared offer is a coordination primitive, not a payment guarantee.

## 4. Bounded constraints under Option D

`option_d_posture_active_in_622`
`wallet_boundary_576_581_unchanged_in_622`

The bounded constraints under the active Option-D posture are:
- This model operates entirely within the current bounded RC/runtime internal
  epoch-settled ledger. It does not require sovereign substrate execution.
- No ILC is transferred. Only ECU accrual paths are described.
- No direct ECU debit, transfer, or wallet write operation is defined in this
  phase.
- The wallet boundary from Phase 576 and Phase 581 is unchanged. The wallet
  surface remains read-only and exposes only `balance_ilc`, `ecu_accrual`, and
  `claimability_state: deferred`.
- This model does not change `claimability_state` and does not write to the
  wallet.
- The bounded nature of the model is explicit: it is not a generalized payment
  system. It is a coordination mechanism for directed epistemic contribution.

## 5. Relationship to runtime and CDL-053

`cdl_053_not_prerequisite_for_622_bounded_model`
`ecu_exchange_runtime_deferred_post_623_plus`

Runtime implementation of this model defers to post-623+. The spec form in
this phase is sufficient for Window 620-622 closure; runtime work remains a
separate later action.

CDL-053 Werner credit architecture remains deferred pending LT evidence track.
This spec does not depend on CDL-053. The bounded model described here is
consistent with the Phase 609 separation regardless of how CDL-053 is
eventually decided.

If CDL-053 is later opened, it may extend or refine the credit attribution
rules that underpin this model, but it is not a prerequisite for this spec.

This means the current spec advances the loop topology and bounded coordination
surface in spec form, while leaving debit-side enforcement and any real write
semantics explicitly deferred.

Planning carry-forward items from the Phase 619 handoff remain unchanged here:
- `cdl_053_werner_credit_architecture_deferred_pending_lt_evidence`
- `legal_positioning_memo_passive_ecu_and_validator_rewards_pre_rc_prerequisite`
- `bft_variant_selection_deferred_engineering_decision`
- `mvp_gate_runtime_form_window_623_plus_blocked_pending_spec_form_pass`

## 6. AG-gate assessment

| Gate | Assessment | Notes |
|---|---|---|
| AG-1 Co-flourishing mission | advance | This is the first spec articulating agent-to-agent economic participation without subordinating the human audit layer. |
| AG-2 W_e increase | advance | A bounded commission loop can direct specialized epistemic effort toward higher-value contribution paths. |
| AG-3 Epistemic integrity | pass | The validation path is unchanged and the Popperian requirement is preserved. |
| AG-4 ECU-ILC separation | pass | ECU-denominated sponsorship stays in the measurement layer; ECU exchange is not ILC payment and this spec creates no direct ECU debit, transfer, or ILC transfer path. |
| AG-5 Harness-agnostic | neutral | The model is protocol-level and does not depend on a specific harness runtime. |
| AG-6 Near-infinite scale | pass | The coordination model is bounded by accrual authority and does not introduce a centralized approval bottleneck. |
| AG-7 Machine-legible first | advance | The offer, acceptance, deliverable, and attribution states are framed as protocol messages rather than UI-only flows. |
| AG-8 Outbound economic loop | advance | This is the primary AG-8 advancement phase for Window 620-622 in bounded spec form; debit-side enforcement remains deferred. |

No AG-gate row is a FAIL.

## 7. Deferred items and exclusions

The following items remain explicitly deferred or excluded:
- runtime implementation of the bounded ECU exchange model to post-623+
- CDL-053 Werner credit architecture, which remains deferred pending LT
  evidence track
- any generalized payment system; this phase defines bounded coordination only
- public claimability, which remains blocked under the Phase 612 two-form
  requirement
- sovereign substrate execution, which remains blocked under ADR-0028 and the
  active Option-D posture
- any direct ECU debit, transfer, spend, withdrawal, wallet write, minting, or
  public payment claim
- any `ilc_core/` mutation, ADR mutation, CDL mutation, or Option-B selection
  claim
