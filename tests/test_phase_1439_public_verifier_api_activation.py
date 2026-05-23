from __future__ import annotations

from fastapi.testclient import TestClient

from ilc_core.ledger.cdl048_conversion_sweeper_runtime import (
    convert_ecu_lot,
    conversion_receipt_payload,
    empty_conversion_sweeper_state,
    register_ecu_lot,
)
from ilc_core.ledger.claimability_proof_binding_runtime import (
    build_claimability_proof_binding,
    claimability_proof_payload,
)
from ilc_core.server import create_app
from ilc_core.sidecars.claimability_receipt_verifier import (
    MAX_CLAIMABILITY_VERIFIER_PAYLOAD_BYTES,
    REJECTED_DECISION,
    build_claimability_verifier_presentation,
    claimability_receipt_verifier_manifest,
    claimability_receipt_verifier_tokens,
)
from ilc_core.sidecars.public_verifier_api_activation import (
    ACCEPTED_PUBLIC_VERIFIER_API_DECISION,
    CLAIMABILITY_API_SERVING_PATH_WIRED_PHASE_1439_TOKEN,
    ECU_MINT_NOT_AUTHORIZED_PHASE_1439_TOKEN,
    ILC_SETTLEMENT_NOT_AUTHORIZED_PHASE_1439_TOKEN,
    PUBLIC_RC_NOT_ACTIVATED_PHASE_1439_TOKEN,
    PUBLIC_VERIFIER_API_ACTIVATED_PHASE_1439_TOKEN,
    WALLET_OPS_NOT_AUTHORIZED_PHASE_1439_TOKEN,
    public_verifier_api_activation_manifest,
)


def _valid_presentation() -> dict:
    agent_id = "agent:phase-1439-public-verifier"
    epoch_id = "epoch-1439"
    wallet_state_root = f"wallet_state_sha256:{'a' * 64}"
    settled_runtime_root = f"settled_runtime_sha256:{'b' * 64}"
    history_digest = f"history_sha256:{'c' * 64}"

    state = register_ecu_lot(
        empty_conversion_sweeper_state(),
        lot_id="lot-phase-1439",
        agent_id=agent_id,
        amount_ecu="13",
        issue_epoch=10,
        origin="phase-1439-test-fixture",
        funding_provenance=("phase-1439-public-api",),
    )
    result = convert_ecu_lot(
        state,
        lot_id="lot-phase-1439",
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
    )


def test_phase_1439_manifest_flips_public_verifier_api_without_value_authority() -> None:
    activation = public_verifier_api_activation_manifest()
    verifier = claimability_receipt_verifier_manifest()
    tokens = claimability_receipt_verifier_tokens()

    assert activation["public_verifier_api_enabled"] is True
    assert activation["route"] == "/api/v1/claimability/verify"
    assert verifier["local_only"] is False
    assert verifier["non_loopback_claimability_api_enabled"] is True
    assert verifier["public_api_enabled"] is True
    assert verifier["receipt_verifier_public_serving_enabled"] is True
    assert verifier["public_claimability_activated"] is True
    assert verifier["ecu_mint_authorized"] is False
    assert verifier["ilc_settlement_authorized"] is False
    assert PUBLIC_VERIFIER_API_ACTIVATED_PHASE_1439_TOKEN in tokens
    assert CLAIMABILITY_API_SERVING_PATH_WIRED_PHASE_1439_TOKEN in tokens
    assert ECU_MINT_NOT_AUTHORIZED_PHASE_1439_TOKEN in tokens
    assert ILC_SETTLEMENT_NOT_AUTHORIZED_PHASE_1439_TOKEN in tokens
    assert WALLET_OPS_NOT_AUTHORIZED_PHASE_1439_TOKEN in tokens
    assert PUBLIC_RC_NOT_ACTIVATED_PHASE_1439_TOKEN in tokens


def test_phase_1439_public_route_accepts_canonical_presentation() -> None:
    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/claimability/verify",
            json={
                "presentation": _valid_presentation(),
                "current_issuance_epoch": 12,
            },
        )

    assert response.status_code == 200
    decision = response.json()
    assert decision["decision"] == ACCEPTED_PUBLIC_VERIFIER_API_DECISION
    assert decision["rejection_reasons"] == []
    assert decision["non_loopback_claimability_api_enabled"] is True
    assert decision["public_api_enabled"] is True
    assert decision["public_claimability_activated"] is True
    assert decision["receipt_verifier_public_serving_enabled"] is True
    assert decision["ecu_mint_authorized"] is False
    assert decision["ilc_settlement_authorized"] is False
    assert decision["wallet_spend_enabled"] is False
    assert decision["wallet_transfer_enabled"] is False
    assert decision["wallet_withdrawal_enabled"] is False
    assert PUBLIC_VERIFIER_API_ACTIVATED_PHASE_1439_TOKEN in decision["tokens"]


def test_phase_1439_public_route_rejects_duplicate_claims_through_nullifier_registry() -> None:
    presentation = _valid_presentation()
    with TestClient(create_app()) as client:
        accepted = client.post(
            "/api/v1/claimability/verify",
            json={"presentation": presentation, "current_issuance_epoch": 12},
        )
        duplicate = client.post(
            "/api/v1/claimability/verify",
            json={"presentation": presentation, "current_issuance_epoch": 12},
        )

    assert accepted.status_code == 200
    assert accepted.json()["decision"] == ACCEPTED_PUBLIC_VERIFIER_API_DECISION
    assert duplicate.status_code == 200
    duplicate_decision = duplicate.json()
    assert duplicate_decision["decision"] == REJECTED_DECISION
    assert duplicate_decision["rejection_reasons"] == [
        "claim_nullifier_replay_rejected_phase_1389b"
    ]
    assert duplicate_decision["public_api_enabled"] is True
    assert duplicate_decision["receipt_verifier_public_serving_enabled"] is True


def test_phase_1439_public_route_fails_closed_on_malformed_presentation() -> None:
    malformed = _valid_presentation()
    malformed["latest_balance_receipt"]["balance_after_ilc"] = "NaN"

    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/claimability/verify",
            json={"presentation": malformed, "current_issuance_epoch": 12},
        )

    assert response.status_code == 200
    decision = response.json()
    assert decision["decision"] == REJECTED_DECISION
    assert decision["rejection_reasons"] == [
        "claimability_latest_balance_receipt_invalid_phase_1305"
    ]
    assert decision["public_api_enabled"] is True


def test_phase_1439_public_route_rejects_oversized_payload_before_verification() -> None:
    body = b'{"presentation":"' + (b"x" * MAX_CLAIMABILITY_VERIFIER_PAYLOAD_BYTES) + b'"}'
    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/claimability/verify",
            content=body,
            headers={"content-type": "application/json"},
        )

    assert response.status_code == 413
    assert response.json()["detail"] == "claimability_public_api_payload_too_large_phase_1439"
