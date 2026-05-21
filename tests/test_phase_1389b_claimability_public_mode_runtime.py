"""Phase 1389b public-mode claimability runtime admission tests."""

from __future__ import annotations

from ilc_core.ledger.cdl048_conversion_sweeper_runtime import (
    conversion_receipt_payload,
    convert_ecu_lot,
    empty_conversion_sweeper_state,
    register_ecu_lot,
)
from ilc_core.ledger.claimability_proof_binding_runtime import (
    build_claimability_proof_binding,
    claimability_proof_payload,
)
from ilc_core.sidecars.claim_nullifier_registry_v1 import (
    ACCEPTED,
    CLAIMABILITY_VERIFIER_PUBLIC_MODE_READY_TOKEN,
    CLAIM_NULLIFIER_REGISTRY_ACTIVE_TOKEN,
    DUPLICATE_CLAIM_REGISTRY_ACTIVE_TOKEN,
    ClaimNullifierRegistry,
)
from ilc_core.sidecars.claimability_receipt_verifier import (
    ACCEPTED_LOCAL_ONLY_DECISION,
    REJECTED_DECISION,
    build_claimability_verifier_presentation,
    canonical_decision_json,
    claimability_receipt_verifier_tokens,
    verify_claimability_receipt_presentation,
)


def _valid_presentation(
    *,
    agent_id: str = "agent:phase-1389b-public-mode",
    lot_id: str = "lot-phase-1389b",
    transport_principal_ref: str = "transport_principal_ref:d2d:phase-1389b",
) -> dict:
    epoch_id = "epoch-1389b"
    wallet_state_root = f"wallet_state_sha256:{'a' * 64}"
    settled_runtime_root = f"settled_runtime_sha256:{'b' * 64}"
    history_digest = f"history_sha256:{'c' * 64}"

    state = register_ecu_lot(
        empty_conversion_sweeper_state(),
        lot_id=lot_id,
        agent_id=agent_id,
        amount_ecu="13",
        issue_epoch=10,
        origin="phase-1389b-test-fixture",
        funding_provenance=("phase-1389b-public-mode",),
    )
    result = convert_ecu_lot(
        state,
        lot_id=lot_id,
        agent_id=agent_id,
        conversion_epoch=12,
        settled_runtime_epoch=12,
        wallet_state_root=wallet_state_root,
        settled_runtime_root=settled_runtime_root,
    )
    conversion_receipt = conversion_receipt_payload(result.receipt)
    latest_balance_receipt = {
        "balance_after_ilc": "13",
        "epoch_id": epoch_id,
        "reward_delta_ilc": "0",
        "settlement_status": "applied",
    }
    proof_binding = build_claimability_proof_binding(
        agent_id=agent_id,
        epoch_id=epoch_id,
        settled_runtime_root=settled_runtime_root,
        wallet_state_root=wallet_state_root,
        latest_balance_receipt=latest_balance_receipt,
        history_digest=history_digest,
        conversion_receipt=conversion_receipt,
    )
    return build_claimability_verifier_presentation(
        canonical_agent_identity=agent_id,
        epoch_id=epoch_id,
        settled_runtime_root=settled_runtime_root,
        wallet_state_root=wallet_state_root,
        latest_balance_receipt=latest_balance_receipt,
        history_digest=history_digest,
        claimability_proof=claimability_proof_payload(proof_binding),
        conversion_receipt=conversion_receipt,
        transport_principal_ref=transport_principal_ref,
    )


def test_phase_1389b_verifier_tokens_and_empty_public_mode_blockers() -> None:
    tokens = claimability_receipt_verifier_tokens()
    assert CLAIM_NULLIFIER_REGISTRY_ACTIVE_TOKEN in tokens
    assert DUPLICATE_CLAIM_REGISTRY_ACTIVE_TOKEN in tokens
    assert CLAIMABILITY_VERIFIER_PUBLIC_MODE_READY_TOKEN in tokens

    decision = verify_claimability_receipt_presentation(_valid_presentation())

    assert decision["decision"] == ACCEPTED_LOCAL_ONLY_DECISION
    assert decision["public_mode_blockers"] == []
    assert decision["public_api_enabled"] is False
    assert decision["public_claimability_activated"] is False
    assert canonical_decision_json(decision).startswith('{"canonical_decision_sha256"')


def test_phase_1389b_nullifier_registry_rejects_replayed_presentation() -> None:
    registry = ClaimNullifierRegistry()
    presentation = _valid_presentation()

    first = verify_claimability_receipt_presentation(
        presentation,
        claim_registry=registry,
        current_issuance_epoch=12,
    )
    second = verify_claimability_receipt_presentation(
        presentation,
        claim_registry=registry,
        current_issuance_epoch=12,
    )

    assert first["decision"] == ACCEPTED_LOCAL_ONLY_DECISION
    assert second["decision"] == REJECTED_DECISION
    assert second["rejection_reasons"] == ["claim_nullifier_replay_rejected_phase_1389b"]
    records = registry.records()
    assert len(records) == 1
    assert records[0].status == ACCEPTED
    assert records[0].decision_ref == f"claimability_decision_sha256:{first['canonical_decision_sha256']}"


def test_phase_1389b_duplicate_claim_rejected_before_verifier_processing() -> None:
    registry = ClaimNullifierRegistry()
    first_presentation = _valid_presentation(
        transport_principal_ref="transport_principal_ref:d2d:first"
    )
    duplicate_material = _valid_presentation(
        transport_principal_ref="transport_principal_ref:d2d:second"
    )

    first = verify_claimability_receipt_presentation(
        first_presentation,
        claim_registry=registry,
        current_issuance_epoch=12,
    )
    second = verify_claimability_receipt_presentation(
        duplicate_material,
        claim_registry=registry,
        current_issuance_epoch=12,
    )

    assert first["decision"] == ACCEPTED_LOCAL_ONLY_DECISION
    assert first_presentation["presentation_id"] != duplicate_material["presentation_id"]
    assert second["decision"] == REJECTED_DECISION
    assert second["rejection_reasons"] == ["duplicate_claim_rejected_at_api_layer"]


def test_phase_1389b_invalid_reserved_presentation_does_not_block_later_valid_claim() -> None:
    registry = ClaimNullifierRegistry()
    invalid = _valid_presentation()
    invalid["conversion_receipt"]["amount_ecu"] = "14"
    valid = _valid_presentation()

    rejected = verify_claimability_receipt_presentation(
        invalid,
        claim_registry=registry,
        current_issuance_epoch=12,
    )
    assert registry.records() == ()

    accepted = verify_claimability_receipt_presentation(
        valid,
        claim_registry=registry,
        current_issuance_epoch=12,
    )

    assert rejected["decision"] == REJECTED_DECISION
    assert rejected["rejection_reasons"] == [
        "claimability_conversion_receipt_hash_mismatch_phase_1305"
    ]
    assert accepted["decision"] == ACCEPTED_LOCAL_ONLY_DECISION
    statuses = [record.status for record in registry.records()]
    assert ACCEPTED in statuses


def test_phase_1389b_registry_record_limit_fails_closed() -> None:
    registry = ClaimNullifierRegistry(max_records=1)
    first = verify_claimability_receipt_presentation(
        _valid_presentation(lot_id="lot-phase-1389b-limit-1"),
        claim_registry=registry,
        current_issuance_epoch=12,
    )
    second = verify_claimability_receipt_presentation(
        _valid_presentation(lot_id="lot-phase-1389b-limit-2"),
        claim_registry=registry,
        current_issuance_epoch=12,
    )

    assert first["decision"] == ACCEPTED_LOCAL_ONLY_DECISION
    assert second["decision"] == REJECTED_DECISION
    assert second["rejection_reasons"] == [
        "claim_nullifier_registry_record_limit_exceeded_phase_1428_audit_fix"
    ]


def test_phase_1389b_registry_expire_stale_records_prunes_indexes() -> None:
    registry = ClaimNullifierRegistry(max_records=1)
    first = verify_claimability_receipt_presentation(
        _valid_presentation(lot_id="lot-phase-1389b-expire-1"),
        claim_registry=registry,
        current_issuance_epoch=12,
    )
    expired = registry.expire_stale_records(20)
    second = verify_claimability_receipt_presentation(
        _valid_presentation(lot_id="lot-phase-1389b-expire-2"),
        claim_registry=registry,
        current_issuance_epoch=12,
    )

    assert first["decision"] == ACCEPTED_LOCAL_ONLY_DECISION
    assert expired == 1
    assert second["decision"] == ACCEPTED_LOCAL_ONLY_DECISION
    assert len(registry.records()) == 1


def test_phase_1389b_registry_rejects_closed_or_premature_claim_window() -> None:
    registry = ClaimNullifierRegistry()

    closed = verify_claimability_receipt_presentation(
        _valid_presentation(lot_id="lot-phase-1389b-closed"),
        claim_registry=registry,
        current_issuance_epoch=15,
    )
    premature = verify_claimability_receipt_presentation(
        _valid_presentation(lot_id="lot-phase-1389b-premature"),
        claim_registry=registry,
        current_issuance_epoch=9,
    )

    assert closed["decision"] == REJECTED_DECISION
    assert closed["rejection_reasons"] == ["claim_window_closed_phase_1389b"]
    assert premature["decision"] == REJECTED_DECISION
    assert premature["rejection_reasons"] == ["claim_window_not_open_phase_1389b"]
