from ilc_core.sidecars import cdl088_claimability_activation as activation
from ilc_core.sidecars.claimability_receipt_verifier import (
    PUBLIC_CLAIMABILITY_ACTIVATED_PHASE_1438_TOKEN,
    PUBLIC_CLAIMABILITY_ACTIVATION_NOT_AUTHORIZED_TOKEN,
    PUBLIC_RC_REMAINS_BLOCKED_TOKEN,
    claimability_receipt_verifier_manifest,
    claimability_receipt_verifier_tokens,
)


def test_phase_1438_activation_sidecar_records_authority_and_boundaries() -> None:
    manifest = activation.cdl088_public_claimability_activation_manifest()

    assert activation.CDL088_PUBLIC_CLAIMABILITY_ACTIVATED is True
    assert manifest["public_claimability_activated"] is True
    assert manifest["ecu_mint_authorized"] is False
    assert manifest["ilc_settlement_authorized"] is False
    assert manifest["wallet_ops_authorized"] is False
    assert manifest["public_rc_activated"] is False
    assert manifest["native_rust_p2p_activated"] is False
    assert manifest["epoch_transition_triggered"] is False


def test_phase_1438_activation_tokens_are_recorded() -> None:
    assert (
        activation.PUBLIC_CLAIMABILITY_ACTIVATED_PHASE_1438_TOKEN
        == "public_claimability_activated_phase_1438"
    )
    assert (
        activation.CDL088_PUBLIC_CLAIMABILITY_ACTIVATION_COMMITTED_PHASE_1438_TOKEN
        == "cdl088_public_claimability_activation_committed_phase_1438"
    )
    assert "ecu_mint_not_authorized_phase_1438" in activation.PHASE_1438_ACTIVATION_TOKENS
    assert "ilc_settlement_not_authorized_phase_1438" in activation.PHASE_1438_ACTIVATION_TOKENS
    assert "wallet_ops_not_authorized_phase_1438" in activation.PHASE_1438_ACTIVATION_TOKENS
    assert "public_rc_not_activated_phase_1438" in activation.PHASE_1438_ACTIVATION_TOKENS
    assert "native_rust_p2p_not_activated_phase_1438" in activation.PHASE_1438_ACTIVATION_TOKENS
    assert "epoch_transition_not_triggered_phase_1438" in activation.PHASE_1438_ACTIVATION_TOKENS


def test_phase_1438_verifier_manifest_authority_true_serving_false() -> None:
    manifest = claimability_receipt_verifier_manifest()

    assert manifest["public_claimability_activated"] is True
    assert manifest["non_loopback_claimability_api_enabled"] is False
    assert manifest["public_api_enabled"] is False
    assert manifest["receipt_verifier_public_serving_enabled"] is False
    assert manifest["local_only"] is True


def test_phase_1438_verifier_tokens_replace_not_authorized_boundary() -> None:
    tokens = claimability_receipt_verifier_tokens()

    assert PUBLIC_CLAIMABILITY_ACTIVATED_PHASE_1438_TOKEN in tokens
    assert PUBLIC_CLAIMABILITY_ACTIVATION_NOT_AUTHORIZED_TOKEN not in tokens
    assert PUBLIC_RC_REMAINS_BLOCKED_TOKEN in tokens


def test_phase_1438_non_claim_tokens_remain_false_boundaries() -> None:
    manifest = activation.cdl088_public_claimability_activation_manifest()

    assert activation.ECU_MINT_NOT_AUTHORIZED_PHASE_1438_TOKEN in manifest["tokens"]
    assert activation.ILC_SETTLEMENT_NOT_AUTHORIZED_PHASE_1438_TOKEN in manifest["tokens"]
    assert activation.WALLET_OPS_NOT_AUTHORIZED_PHASE_1438_TOKEN in manifest["tokens"]
    assert activation.PUBLIC_RC_NOT_ACTIVATED_PHASE_1438_TOKEN in manifest["tokens"]
    assert activation.NATIVE_RUST_P2P_NOT_ACTIVATED_PHASE_1438_TOKEN in manifest["tokens"]
    assert activation.EPOCH_TRANSITION_NOT_TRIGGERED_PHASE_1438_TOKEN in manifest["tokens"]
