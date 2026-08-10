from __future__ import annotations

import copy

import pytest

from ilc_core.sidecars.registry_manifest import build_sidecar_registry_manifest
from ilc_core.sidecars.wallet_action_semantics_preflight import (
    ILC_SETTLEMENT_AUTHORIZED_PHASE_1592_TOKEN,
    PUBLIC_CLAIMABILITY_AUTHORIZED_PHASE_1592_TOKEN,
    WALLET_WITHDRAWAL_TRANSFER_SPEND_NOT_ACTIVATED_TOKEN,
    WalletActionSemanticsPreflightError,
    build_wallet_action_semantics_preflight_packet,
    validate_wallet_action_semantics_preflight_packet,
    wallet_action_semantics_preflight_manifest,
    wallet_action_semantics_preflight_required_tokens,
)


def test_preflight_accepts_claimability_authorized_at_rc() -> None:
    packet = build_wallet_action_semantics_preflight_packet(current_epoch=1592)

    assert packet["authorization_flags"]["public_claimability_activated"] is True
    assert PUBLIC_CLAIMABILITY_AUTHORIZED_PHASE_1592_TOKEN in packet["tokens"]
    assert validate_wallet_action_semantics_preflight_packet(packet) == packet


def test_preflight_accepts_ilc_settlement_authorized_at_rc() -> None:
    packet = build_wallet_action_semantics_preflight_packet(current_epoch=1592)

    assert packet["authorization_flags"]["ilc_settlement_authorized"] is True
    assert ILC_SETTLEMENT_AUTHORIZED_PHASE_1592_TOKEN in packet["tokens"]
    assert validate_wallet_action_semantics_preflight_packet(packet) == packet


def test_preflight_still_rejects_transfer_enabled_at_rc() -> None:
    with pytest.raises(WalletActionSemanticsPreflightError) as exc:
        build_wallet_action_semantics_preflight_packet(
            current_epoch=1592,
            wallet_transfer_enabled=True,
        )

    assert exc.value.token == WALLET_WITHDRAWAL_TRANSFER_SPEND_NOT_ACTIVATED_TOKEN


def test_preflight_still_rejects_withdrawal_enabled_at_rc() -> None:
    with pytest.raises(WalletActionSemanticsPreflightError) as exc:
        build_wallet_action_semantics_preflight_packet(
            current_epoch=1592,
            wallet_withdrawal_enabled=True,
        )

    assert exc.value.token == WALLET_WITHDRAWAL_TRANSFER_SPEND_NOT_ACTIVATED_TOKEN


def test_preflight_still_rejects_spend_signing_and_ledger_write_at_rc() -> None:
    for flag in (
        "wallet_spend_enabled",
        "wallet_signing_authorized",
        "wallet_ledger_write_authorized",
        "public_claim_endpoint_enabled",
        "transfer_endpoint_enabled",
        "withdrawal_endpoint_enabled",
        "spend_endpoint_enabled",
        "external_chain_bridge_enabled",
    ):
        with pytest.raises(WalletActionSemanticsPreflightError):
            build_wallet_action_semantics_preflight_packet(current_epoch=1592, **{flag: True})


def test_preflight_requires_both_phase_1592_authorized_flags() -> None:
    for flag in ("public_claimability_activated", "ilc_settlement_authorized"):
        with pytest.raises(WalletActionSemanticsPreflightError) as exc:
            build_wallet_action_semantics_preflight_packet(current_epoch=1592, **{flag: False})

        assert exc.value.token == f"wallet_action_semantics_{flag}_required_phase_1592"


def test_validation_rejects_tampered_phase_1592_authorized_flags() -> None:
    packet = build_wallet_action_semantics_preflight_packet(current_epoch=1592)

    for flag in ("public_claimability_activated", "ilc_settlement_authorized"):
        tampered = copy.deepcopy(packet)
        tampered["authorization_flags"][flag] = False
        with pytest.raises(WalletActionSemanticsPreflightError) as exc:
            validate_wallet_action_semantics_preflight_packet(tampered)

        assert exc.value.token == f"wallet_action_semantics_{flag}_required_phase_1592"


def test_manifest_and_registry_integrity_record_phase_1592_activation() -> None:
    manifest = wallet_action_semantics_preflight_manifest()
    registry = build_sidecar_registry_manifest()
    integrity = registry["package_profile_integrity"][
        "wallet_action_semantics_preflight_manifest"
    ]

    assert manifest["public_claimability_activated"] is True
    assert manifest["ilc_settlement_authorized"] is True
    assert integrity == manifest
    assert wallet_action_semantics_preflight_required_tokens().count(
        PUBLIC_CLAIMABILITY_AUTHORIZED_PHASE_1592_TOKEN
    ) == 1
    assert wallet_action_semantics_preflight_required_tokens().count(
        ILC_SETTLEMENT_AUTHORIZED_PHASE_1592_TOKEN
    ) == 1
