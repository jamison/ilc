# ILC Native Status Evidence 00a Schema v0.1

## Purpose

This document defines the `native_status_evidence_00a.v0.1` derived evidence object for `GAP-PUBLIC-RC-NATIVE-STATUS-EVIDENCE-00a`.

The evidence object is a verifier-facing receipt derived only from the durable Phase 1603 public-user smoke evidence at `out/phase_1603_public_user_smoke/evidence.json`. It proves that the Phase 1603 clean-install agent initialized, submitted a local graph node, received a persisted graph record, and received a Rust BalanceStore-backed ECU status response.

## Source Binding

The assembler must read `out/phase_1603_public_user_smoke/evidence.json` and compute SHA-256 over the file bytes. The only accepted source hash is:

`aabfa87fb9ec96b8f2ac234b60e647aa8c30ebb305d2925f6dedb08c0efe7437`

If the source hash differs, the assembler must stop with `source_evidence_sha256_mismatch_00a`.

The assembler must not read `raw_stdout_path` files or any `/tmp` path recorded by the source evidence. All derived fields must come from the durable source JSON.

## Evidence Object

The derived object has schema version `native_status_evidence_00a.v0.1` and records:

- `source_evidence`: durable source path, source hash, source schema version, and source phase.
- `agent_id`: the Phase 1603 clean-install agent identifier, validated as 96 lowercase hex characters.
- `graph_node`: the persisted graph node id, CIDv1 marker, persistence result, primitive type, and source reference count.
- `gossip`: the deferred gossip delivery result and the non-claim that deferred gossip is expected for this evidence level.
- `ecu_status`: the Rust BalanceStore committed aggregate status fields.
- `package`: package name, package version, clean-venv derivation, and repo import leak check status.
- `assertions_verified`: the complete assertion list verified by the assembler.
- `non_claims`: the complete non-claim list preserved by this phase.
- `output_token`: `native_status_evidence_assembled_GAP_PUBLIC_RC_NATIVE_STATUS_EVIDENCE_00a`.
- `result`: `pass`.

## Required Assertions

The assembler must verify exactly these assertion names in the produced object:

- `agent_id_is_96_hex`
- `node_id_is_cid_v1`
- `graph_persistence_is_persisted`
- `balance_ecu_source_is_rust_committed_aggregate`
- `pending_attribution_quote_is_zero`
- `committed_ecu_balance_is_zero`
- `non_claim_committed_balance_visibility_present`
- `stale_rust_bridge_marker_absent`

## Required Non-Claims

The produced object must preserve exactly these non-claims:

- `no_native_network_ingress_claim`
- `no_signed_peer_response_claim`
- `no_live_validator_acceptance_claim`
- `gossip_delivery_deferred_is_expected_not_failure`
- `no_nonzero_ecu_claim`
- `no_monthly_close_claim`
- `no_ecu_minting`
- `no_ilc_minting`
- `no_settlement_claim`
- `committed_balance_visibility_not_monthly_close_eligibility`

## Failure Tokens

The assembler must hard fail with the named token for each invariant failure:

- `source_evidence_sha256_mismatch_00a`
- `source_evidence_result_not_pass_00a`
- `agent_id_invalid_in_source_evidence_00a`
- `node_id_not_cid_v1_00a`
- `graph_persistence_not_persisted_00a`
- `balance_ecu_source_invalid_00a`
- `pending_attribution_quote_nonzero_00a`
- `committed_ecu_balance_nonzero_00a`
- `non_claim_missing_from_source_evidence_00a`
- `stale_rust_bridge_marker_present_00a`
- `source_evidence_schema_mismatch_00a`
- `node_primitive_type_invalid_00a`
- `source_refs_count_invalid_00a`
- `gossip_delivery_unexpected_00a`
- `package_identity_invalid_00a`
- `clean_venv_or_repo_import_leak_check_invalid_00a`

## Scope Boundary

This evidence object does not claim live native/network ingress, signed peer response, live validator acceptance, gossip delivery, nonzero ECU, monthly close eligibility, ECU minting, ILC minting, settlement, guard clearance, PyPI publication, or VPS mutation.
