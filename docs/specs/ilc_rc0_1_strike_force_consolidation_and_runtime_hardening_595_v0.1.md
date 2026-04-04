# ILC RC0.1 Strike Force Consolidation and Runtime Hardening 595 v0.1

Status: locked
Date: 2026-04-04
Phase: 595
Owner lane: G8 RC0.1 strike force

## 1. Consolidation mandate and historical boundary

Phase 595 executes the remaining bounded RC0.1 testnet closure work after
Window 585-594 closed first.

This packet does not claim that candidate Phases 582-584 executed historically.
It absorbs those unexecuted units as present-tense execution scope and records
that supersession honestly.

Required governance tokens:
- `phase_595_consolidates_remaining_rc0_1_testnet_closure_and_hardening`
- `phase_595_supersedes_unexecuted_582_584_as_execution_units_not_historical_inputs`
- `cdl_v7_reproducibility_disposition_must_be_explicit_in_post_594_form`
- `outbound_http_machine_payment_skill_must_be_attached_or_explicitly_deferred`
- `phase_583_and_584_closure_obligations_are_absorbed_here`
- `runtime_hardening_must_preserve_576_581_boundaries`
- `wallet_history_query_and_export_must_remain_read_only_and_durable`
- `settlement_replay_negative_path_and_release_gate_must_be_committed_head_green`
- `release_candidate_and_release_gate_outputs_must_remain_machine_legible`
- `rc0_1_testnet_claims_remain_bounded_not_public_legitimacy_claims`
- `curated_genesis_testnet_posture_remains_in_force_without_public_upgrade`
- `genesis_carry_forward_queue_remains_explicit_not_silently_closed`
- `inbound_http_machine_payment_ingress_remains_deferred_to_later_window`
- `phase_595_outputs_feed_window_595_plus_planning_without_replacing_it`

## 2. Dependency tiers, inherited canon, and allowed runtime surfaces

Minimum dependency bundle carried by this packet:
- `docs/specs/ilc_phase_575_584_sequence_lock_v0.1.md`
- `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md`
- `docs/specs/ilc_rc0_1_persisted_graph_contract_lock_577_v0.1.md`
- `docs/specs/ilc_rc0_1_curated_genesis_bootstrap_lineage_lock_578_v0.1.md`
- `docs/specs/ilc_rc0_1_agent_behavioral_loop_runtime_cutover_579_v0.1.md`
- `docs/specs/ilc_rc0_1_7_plus_1_panel_live_submission_integration_580_v0.1.md`
- `docs/specs/ilc_rc0_1_ecu_settlement_wallet_query_integration_581_v0.1.md`
- `docs/specs/ilc_post_586_strike_force_runtime_hardening_packet_v0.1.md`
- `docs/specs/ilc_rc0_1_readiness_checklist_v0.1.md`
- `docs/specs/ilc_window_585_594_handoff_594_v0.1.md`
- `docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md`
- `docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`
- `tools/agent_loop_v1.py`
- `tools/query_rc0_1_economic_state.py`
- `tools/check_rc0_1_economic_state.py`
- `tools/run_rc0_1_economic_proof.py`
- `tools/testbed/run_economic_replay_drills.py`
- `tools/testbed/run_economic_negative_path_drills.py`
- `tools/run_rc0_1_release_gate.py`
- `tools/check_rc0_1_release_gate.py`
- `tools/run_rc0_1_release_candidate.py`
- `tools/run_rc0_1_release_claim.py`
- `tools/check_rc0_1_release_claim.py`
- `tools/render_rc0_1_readiness_delta.py`

Tier and boundary labels:
- the 585-594 outputs are frozen public-boundary inputs, not surfaces reopened by this phase
- the runtime and release tools are bounded RC0.1 implementation surfaces, not self-executing public law
- the curated Genesis/testnet posture from Phase 578 remains in force for RC0.1 and does not imply public Genesis-governance closure
- the Genesis carry-forward queue from the 594 handoff remains explicit, open, and non-equal-canon for this phase

Inherited canon carried into this packet:
- the Phase 576 settlement and wallet meaning remains accounting-only and read-only
- the Phase 577 durable graph contract remains authoritative for bounded query and proof surfaces
- the Phase 578 curated Genesis/bootstrap lineage remains testnet-only and operator-managed
- the Phase 579 and 580 agent-loop and panel cutover remain bounded runtime inputs, not fresh design space
- the Phase 581 settled wallet-query anchor set remains the current runtime anchor set
- the Phase 585-594 public boundary remains frozen and must not be widened here

Allowed runtime surfaces in this packet are limited to the current agent loop,
economic proof, wallet-query, replay drill, negative-path drill, release gate,
release candidate, release claim, and readiness-delta surfaces already present
in the repository.

## 3. Residual Phase 582-584 obligations absorbed here

`phase_595_supersedes_unexecuted_582_584_as_execution_units_not_historical_inputs`.

`cdl_v7_reproducibility_disposition_must_be_explicit_in_post_594_form`.

The reproducibility disposition in this packet is explicit and bounded. It must
state that the current agent loop, 7+1 panel, durable settlement, wallet
query, and release tooling are the operative RC0.1 bridge surfaces and that
protocol completeness is not implied by silence.

The reproducibility disposition must include surviving known approximations and
support-lane caveats. In the current bounded RC0.1 lane, the reproducibility
memo records that `centrality_score` is derived from `agreement_score` in the
agent-loop panel output and that this remains a bounded testnet approximation
rather than silent protocol law.

`outbound_http_machine_payment_skill_must_be_attached_or_explicitly_deferred`.

In this packet, the outbound `HTTP machine-payment skill` lane is recorded here as an explicit defer. It does not block the RC0.1 correctness gate, it does not reopen the protocol boundary, and it does not authorize inbound payment ingress.

`phase_583_and_584_closure_obligations_are_absorbed_here`.

The coherence and closure obligations assigned to candidate Phases 583-584 are
absorbed by this packet through the spec, the phase 595 runner/checker, the
walkthrough, and the status record rather than being silently skipped.

## 4. Runtime hardening tranche executed here

`runtime_hardening_must_preserve_576_581_boundaries`.

`wallet_history_query_and_export_must_remain_read_only_and_durable`.

`settlement_replay_negative_path_and_release_gate_must_be_committed_head_green`.

The runtime hardening tranche executed here covers wallet/history hardening,
settlement idempotency tightening, runtime-store integrity checks, durable
query closure, multi-cycle economic proof, economic negative-path expansion,
and release-gate tightening at committed head.

Any code or tooling changes in this phase must preserve the Phase 576 accounting-only wallet boundary, the Phase 577 durable graph contract, the Phase 578 curated Genesis/testnet lineage posture, and the Phase 581 settled-wallet-query anchor set.

Committed-head replay, negative-path, release-gate, release-candidate, and
release-claim surfaces must remain green before this packet can pass.

## 5. Deterministic release evidence, claim discipline, and gate tightening

`release_candidate_and_release_gate_outputs_must_remain_machine_legible`.

`rc0_1_testnet_claims_remain_bounded_not_public_legitimacy_claims`.

Release-candidate, release-gate, release-claim, and readiness-delta outputs
remain machine-legible and consume the current committed-head runtime and
economic evidence directly.

Bounded RC0.1 claims remain operator-auditable testnet evidence. They are not
public-legitimacy closure, not public claimability, and not public
minting/governance closure.

The checker and runner fail closed if the reproducibility disposition,
settlement/query anchors, release-gate evidence, release-claim evidence, or
Genesis/testnet boundary disclosures are missing.

## 6. Genesis/testnet posture and public-boundary non-goals

`curated_genesis_testnet_posture_remains_in_force_without_public_upgrade`.

`genesis_carry_forward_queue_remains_explicit_not_silently_closed`.

The RC0.1 curated Genesis/testnet posture remains bounded, operator-managed,
and distinct from the public-release Genesis authority and sunset closure work.

This phase does not silently settle Genesis governance dilution,
freshness-gate provenance, accrual-governor provenance, or the separate
post-Genesis capability-proof lane.

Any reference to Genesis in this packet stays within RC0.1 lineage, bootstrap,
accounting visibility, and explicit defer language.

## 7. Forbidden interpretations and exclusions

The following interpretations are forbidden:
- claiming that candidate Phases 582-584 executed historically when they did not
- treating the post-594 consolidation packet as authority to reopen public-release law
- treating bounded RC0.1 evidence as equivalent to public legitimacy or mainnet readiness
- treating wallet visibility, wallet export, or release-gate green status as spend or transfer authority
- treating the curated Genesis/testnet posture as a silent public Genesis-governance upgrade
- treating inbound `HTTP machine-payment ingress` as part of this phase
- treating harness/product surfaces as protocol correctness dependencies

## 8. Explicit deferrals to later windows and lanes

`inbound_http_machine_payment_ingress_remains_deferred_to_later_window`.

`phase_595_outputs_feed_window_595_plus_planning_without_replacing_it`.

Deferred beyond Phase 595:
- inbound `HTTP machine-payment ingress` to a later window
- Genesis governance dilution closure to its dedicated carry-forward lane
- freshness-gate provenance closure to its dedicated carry-forward lane
- Genesis accrual-governor provenance reconciliation to its dedicated carry-forward lane
- the post-Genesis capability-proof lane to its separate future vehicle
- post-RC hardening items such as `mTLS`, automatic fallback, and dynamic discovery

This packet feeds Window 595+ planning without replacing it.
