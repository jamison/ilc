# ILC Public Runtime Integration Over the Receipt Boundary 591 v0.1

Status: locked
Date: 2026-04-04
Phase: 591
Owner lane: G8 public-release integration

## 1. Public-runtime integration target

Phase 591 locks the bounded runtime integration posture for Window 585-594 after
Phases 587-590 froze the public identity, quorum, settlement, and
Genesis-lineage boundaries.

This packet records how the current RC0.1 runtime and proof lane consumes the
frozen public boundary without redefining public legitimacy through tooling,
operator visibility, or release packaging.

Required governance tokens:
- `public_runtime_integration_must_consume_frozen_587_590_boundary`
- `runtime_evidence_surfaces_must_map_to_activation_quorum_settlement_genesis_chain`
- `rc0_1_runtime_is_bounded_bridge_not_final_public_authority_runtime`
- `release_candidate_manifest_and_claim_are_operator_evidence_not_by_themselves_public_legitimacy`
- `public_runtime_integration_must_preserve_receipt_boundary_names_and_slots`
- `readiness_delta_is_claim_discipline_not_legitimacy_substitute`
- `public_runtime_integration_must_preserve_claim_batch_and_wallet_query_anchors`
- `public_runtime_integration_must_fail_closed_on_lineage_or_settlement_gap`
- `publication_pending_and_post_rc_scope_must_remain_machine_legible`
- `harness_boundary_from_adr_0026_remains_in_force`
- `bounded_runtime_visibility_not_public_legitimacy_by_itself`
- `no_runtime_shortcut_across_frozen_public_boundary`
- `phase_592_operator_honesty_package_must_consume_phase_591_runtime_boundary`

## 2. Dependency tiers, inherited canon, and runtime anchors

Minimum dependency bundle carried by this packet:
- `docs/specs/ilc_window_585_594_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_phase_585_594_sequence_lock_v0.1.md`
- `docs/specs/ilc_public_receipt_representation_cluster_lock_586_v0.1.md`
- `docs/specs/ilc_public_identity_activation_and_namespace_boundary_lock_587_v0.1.md`
- `docs/specs/ilc_public_quorum_eligibility_and_genesis_lineage_authority_boundary_lock_588_v0.1.md`
- `docs/specs/ilc_settlement_linked_public_legitimacy_and_payout_traceability_lock_589_v0.1.md`
- `docs/specs/ilc_genesis_authority_sunset_and_fork_legitimacy_coherence_lock_590_v0.1.md`
- `docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md`
- `docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`
- `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md`
- `docs/specs/ilc_rc0_1_ecu_settlement_wallet_query_integration_581_v0.1.md`
- `tools/run_rc0_1_release_candidate.py`
- `tools/run_rc0_1_release_claim.py`
- `tools/check_rc0_1_release_claim.py`
- `tools/render_rc0_1_readiness_delta.py`
- `tools/query_rc0_1_economic_state.py`

Bounded implementation-context rule:
- `tools/run_rc0_1_release_candidate.py`, `tools/run_rc0_1_release_claim.py`, `tools/check_rc0_1_release_claim.py`, and `tools/render_rc0_1_readiness_delta.py` are bounded RC0.1 implementation surfaces, not by themselves the canonical public legitimacy contract.
- `tools/query_rc0_1_economic_state.py` is operator/query visibility tooling, not by itself public claimability or settlement legitimacy.
- `harness_boundary_from_adr_0026_remains_in_force`.

Inherited canon:
- `public_identity_activation_requires_settled_admission_or_stake_binding_receipt`.
- `public_quorum_authority_requires_eligibility_receipt_or_proof`.
- `settlement_linked_public_legitimacy_requires_settled_receipt_chain`.
- `genesis_rooted_artifact_lineage_required_for_canonical_public_network`.

Bounded RC0.1 runtime anchors for this bridge packet are:
- `task_id`
- `epoch_id` or `epoch_index`
- `claim_batch_sha256`
- settlement status
- wallet-query visibility over the LMDB-backed runtime store

## 3. Runtime mapping to the frozen public boundary

`public_runtime_integration_must_consume_frozen_587_590_boundary`.

`runtime_evidence_surfaces_must_map_to_activation_quorum_settlement_genesis_chain`.

The runtime/proof lane must map its public surfaces back to the frozen
activation, quorum, settlement, and Genesis-lineage boundaries rather than
inventing replacement authority semantics.

`public_runtime_integration_must_preserve_receipt_boundary_names_and_slots`.

The bridge lane preserves the receipt-boundary names and machine-legible slots
needed to reference activation lineage, quorum eligibility/proof lineage,
settled legitimacy lineage, and Genesis-rooted canonical lineage.

`public_runtime_integration_must_preserve_claim_batch_and_wallet_query_anchors`.

The bounded RC0.1 runtime anchors for `task_id`, `epoch_id` or `epoch_index`,
`claim_batch_sha256`, settlement status, and wallet-query visibility remain
explicit reference points for the current bridge lane.

`public_runtime_integration_must_fail_closed_on_lineage_or_settlement_gap`.

The bridge lane must fail closed if lineage continuity, settled receipt-chain
continuity, or the bounded runtime/query anchors become inconsistent.

## 4. Bounded release-candidate evidence and proof lane

`rc0_1_runtime_is_bounded_bridge_not_final_public_authority_runtime`.

The current RC0.1 runtime is a bounded bridge over the frozen public boundary.
It is not the final public-authority runtime.

`release_candidate_manifest_and_claim_are_operator_evidence_not_by_themselves_public_legitimacy`.

The release-candidate manifest and release claim are operator-evidence surfaces
that summarize checked runtime state. They are not by themselves public
legitimacy roots.

`readiness_delta_is_claim_discipline_not_legitimacy_substitute`.

The readiness delta is claim discipline, not a legitimacy substitute.

`publication_pending_and_post_rc_scope_must_remain_machine_legible`.

`PUBLICATION_PENDING_ITEMS` and `POST_RC_DEFERRED_SCOPE` remain mandatory
machine-legible disclosure surfaces for the current RC lane.

The current release-candidate, release-claim, and readiness-delta surfaces are
bounded operator-evidence and proof surfaces over the frozen public boundary,
not independent sources of public legitimacy.

## 5. Operator-visible outputs and non-claim discipline

`bounded_runtime_visibility_not_public_legitimacy_by_itself`.

Operator-visible wallet, claim, query, bundle, or release output is not by
itself public legitimacy, public claimability, or canonical settlement
authority.

`no_runtime_shortcut_across_frozen_public_boundary`.

Runtime visibility may expose the current bridge state only insofar as it
preserves the frozen 587-590 boundary and the RC0.1 settlement/query anchors.
No runtime-facing output may shortcut around the frozen public boundary.

## 6. Forbidden interpretations and exclusions

The following interpretations are forbidden:
- treating release-candidate manifests, release claims, or readiness deltas as independent public-legitimacy roots
- treating runtime visibility or wallet query visibility as public claimability by itself
- treating the RC0.1 bridge runtime as equivalent to final public-authority runtime
- reopening protocol meaning through harness/product tooling
- inventing new authority slots that bypass the frozen receipt boundary

## 7. Explicit deferrals to later phases

Deferred beyond Phase 591:
- public release-claim and operator honesty packaging to Phase 592
- coherence report and capsule update to Phase 593
- closure gate and handoff to Phase 594
- any remaining Genesis dilution, freshness, or accrual-law closure to dedicated later vehicles
- any new runtime enforcement or receipt issuance implementation to later implementation lanes

`phase_592_operator_honesty_package_must_consume_phase_591_runtime_boundary`.
