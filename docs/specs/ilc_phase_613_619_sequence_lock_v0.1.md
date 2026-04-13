# ILC Phase 613-619 Sequence Lock v0.1

Status: locked
Date: 2026-04-13
Phase: 613
Owner lane: G8 MVP gate spec lane

## 1. Window summary

Window 613-619 is the MVP gate spec lane that opens after the Phase 612
settlement-substrate closure memo and carries only the first post-612 spec
packet required for the minimum participant-touch package.

This window is a seven-phase MVP spec lane only. It covers the public
init/admission contract, the visible ECU-to-ILC lifecycle contract, the public
receipt schema and query contract, the public wallet surface contract, the MVP
gate synthesis and coherence report, and the closure gate/handoff that records
spec-form closure honestly without overstating runtime completion.

Agent Skills is explicitly deferred to a post-619 window per the Phase 612
carry-forward priority rule
`post_612_work_must_prioritize_receipts_lifecycle_wallet_touchpoints_and_init`.
Opening Agent Skills as a parallel track inside this window is prohibited.

Required lock tokens:
- `mvp_gate_spec_lane_window_613_619_primary_gate`
- `spec_form_closure_necessary_but_not_sufficient_for_mvp_gate`
- `interface_runtime_form_required_window_623_plus`
- `broader_public_rc_claims_blocked_until_spec_and_runtime_both_complete`
- `agent_skills_deferred_per_phase_612_priority_rule`
- `no_wallet_widening_in_window_613_619`
- `no_payment_runtime_in_window_613_619`
- `no_chain_implementation_in_window_613_619`
- `post_612_priority_rule_receipts_lifecycle_wallet_init_precede_new_sub_lanes`

## 2. Hard pass condition

Window 613-619 only passes if all of the following are true:
1. the init/admission contract spec is closed and tests pass
2. the ECU-to-ILC lifecycle contract spec is closed and tests pass
3. the public receipt schema and query contract spec is closed and tests pass
4. the public wallet surface contract spec is closed and tests pass
5. the coherence report explicitly states spec-form closure is necessary but
   NOT sufficient for the full MVP gate
6. the coherence report explicitly states interface/runtime form (Window 623+)
   is still required
7. the closure gate passes at the 6-category structural standard matching the
   Phase 605 pattern (prompt_contract_validation, mvp_spec_band_tests,
   synthesis_and_coherence_tests, mutation_canary, closure_gate_cli_contract,
   walkthrough_hygiene)
8. no broader public RC claims are opened by this window

`mvp_gate_spec_lane_window_613_619_primary_gate`.
`spec_form_closure_necessary_but_not_sufficient_for_mvp_gate`.
`interface_runtime_form_required_window_623_plus`.
`broader_public_rc_claims_blocked_until_spec_and_runtime_both_complete`.

## 3. Mandatory dependency bundle

Every Phase 613-619 artifact must carry the mandatory dependency bundle from
`docs/specs/ilc_window_613_619_candidate_phase_grouping_v0.1.md`.

Binding references for the window:
- `docs/specs/ilc_settlement_substrate_closure_and_mvp_gated_replan_612_v0.1.md`
- `docs/specs/ilc_phase_607_612_sequence_lock_v0.1.md`
- `docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md`
- `docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md`
- `docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`
- `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md`
- `docs/specs/ilc_rc0_1_ecu_settlement_wallet_query_integration_581_v0.1.md`
- `docs/specs/ilc_public_receipt_representation_cluster_lock_586_v0.1.md`
- `docs/specs/ilc_public_identity_activation_and_namespace_boundary_lock_587_v0.1.md`
- `docs/specs/ilc_settlement_linked_public_legitimacy_and_payout_traceability_lock_589_v0.1.md`
- `docs/specs/ilc_public_release_claim_and_operator_honesty_package_592_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

The Phase 612 closure memo remains the governing carry-forward law for this
window. No Phase 613-619 output may silently supersede the Phase 612 closure
packet by implication.

## 4. Pre-lock blockers

The following blockers are mandatory before any Window 613-619 execution lock
may pass:
- the Phase 612 closure memo is the governing input; it may not be silently
  superseded by any individual phase output
- the locked wallet boundary from Phase 576 and Phase 581 is not widened
  inside this window
- Agent Skills is explicitly deferred per the Phase 612 priority rule and may
  not be introduced as a parallel track in this window
- spec-form closure in this window does NOT open broader public RC claims
- the interface/runtime gate (Window 623+) remains required before broader
  public RC claims may proceed

`agent_skills_deferred_per_phase_612_priority_rule`.
`no_wallet_widening_in_window_613_619`.
`post_612_priority_rule_receipts_lifecycle_wallet_init_precede_new_sub_lanes`.

## 5. Phase table

| Phase | Description | Primary output | Sensitive? |
|---|---|---|---|
| 613 | Window 613-619 sequence lock | `ilc_phase_613_619_sequence_lock_v0.1.md` | YES |
| 614 | Public init/admission contract spec | init/admission contract spec | YES |
| 615 | Visible ECU-to-ILC lifecycle contract spec | ECU lifecycle contract spec | YES |
| 616 | Public receipt schema and query contract spec | receipt schema/query contract spec | No |
| 617 | Public wallet surface contract spec | wallet surface contract spec | YES |
| 618 | MVP gate spec synthesis + coherence report + capsule v3.3 | coherence report + capsule v3.3 | No |
| 619 | Window 613-619 closure gate and handoff | gate script + handoff | YES |

## 6. Locked implementation decisions

The following decisions are locked for the full Window 613-619 execution lane:
- Window 613-619 is an MVP spec lane, not an implementation or runtime window
- Agent Skills is deferred to a post-619 window per the Phase 612 priority
  rule `post_612_work_must_prioritize_receipts_lifecycle_wallet_touchpoints_and_init`
- spec-form closure is necessary but NOT sufficient for the full MVP gate
- interface/runtime form (Window 623+) is still required
- broader public RC claims remain blocked until both spec AND runtime forms
  complete
- no wallet write, transfer, withdrawal, or spend authority is introduced
- the current read-only posture from Phase 576 and Phase 581 is preserved

`mvp_gate_spec_lane_window_613_619_primary_gate`.
`spec_form_closure_necessary_but_not_sufficient_for_mvp_gate`.
`interface_runtime_form_required_window_623_plus`.
`broader_public_rc_claims_blocked_until_spec_and_runtime_both_complete`.
`agent_skills_deferred_per_phase_612_priority_rule`.

## 7. Protected boundaries and anti-pattern exclusions

The following exclusions are mandatory for Window 613-619:
- opening Agent Skills or any other new sub-lane inside Window 613-619
- claiming the MVP gate is fully satisfied after spec-form closure only
- any wallet widening beyond the Phase 576 and Phase 581 read-only boundary
- any payment runtime implementation
- any chain implementation
- treating spec closure as authorization for broader public RC claims

`no_wallet_widening_in_window_613_619`.
`no_payment_runtime_in_window_613_619`.
`no_chain_implementation_in_window_613_619`.

## 8. Sequence integrity rule

Window 613-619 must execute in this order:
1. Phase 613 sequence lock.
2. Phase 614 public init/admission contract spec.
3. Phase 615 visible ECU-to-ILC lifecycle contract spec.
4. Phase 616 public receipt schema and query contract spec.
5. Phase 617 public wallet surface contract spec.
6. Phase 618 MVP gate spec synthesis + coherence report + capsule v3.3.
7. Phase 619 Window 613-619 closure gate and handoff.

This ordering preserves the Phase 612 priority rule by forcing the minimum
participant-touch package to close in spec form before the MVP gate synthesis
and by blocking any silent transition from spec closure to broader public RC
claims before the later interface/runtime gate is complete.
