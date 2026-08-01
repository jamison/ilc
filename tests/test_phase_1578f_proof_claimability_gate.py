# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1578f proof-claimability wallet display gate tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from ilc_core.ledger.ecu_active_layer_runtime import EcuActiveLayerRuntime
from ilc_core.ledger.ecu_ilc_lifecycle_runtime import EcuIlcLifecycleRuntime
from ilc_core.protocol.public_wallet_runtime import (
    WALLET_CLAIMABILITY_STATE_PROOF_AUTHORIZED,
    PublicWalletRuntime,
)
from ilc_core.sidecars import claimability_receipt_verifier
from ilc_core.sidecars import wallet_action_semantics_preflight
from ilc_core.sidecars.wallet_action_semantics_preflight import (
    WalletActionSemanticsPreflightError,
    build_wallet_action_semantics_preflight_packet,
    wallet_action_semantics_preflight_manifest,
)
from ilc_core.storage.lmdb_public_runtime import LmdbWalletStore


AGENT_ID = "agent-1578f-proof-claimability"


def _runtime(tmp_path: Path) -> PublicWalletRuntime:
    wallet_store = LmdbWalletStore(tmp_path / "wallet-store")
    lifecycle_runtime = EcuIlcLifecycleRuntime(
        wallet_store=wallet_store,
        ecu_runtime=EcuActiveLayerRuntime(),
    )
    lifecycle_runtime.commit_settled_epoch(
        agent_id=AGENT_ID,
        epoch_id="epoch-1578f",
        reward_delta_ilc="7.5",
    )
    return PublicWalletRuntime(
        wallet_store=wallet_store,
        lifecycle_runtime=lifecycle_runtime,
    )


def test_wallet_display_surfaces_use_proof_claimability_authorized_state(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)

    status = runtime.wallet_status(agent_id=AGENT_ID)["data"]
    history = runtime.wallet_history(agent_id=AGENT_ID)["data"]
    export = runtime.wallet_export(agent_id=AGENT_ID)["data"]
    summary = runtime.ledger_summary(agent_id=AGENT_ID)["data"]

    assert status["claimability_state"] == WALLET_CLAIMABILITY_STATE_PROOF_AUTHORIZED
    assert history["claimability_state"] == WALLET_CLAIMABILITY_STATE_PROOF_AUTHORIZED
    assert export["claimability_state"] == WALLET_CLAIMABILITY_STATE_PROOF_AUTHORIZED
    assert summary["claimability_state"] == WALLET_CLAIMABILITY_STATE_PROOF_AUTHORIZED
    assert WALLET_CLAIMABILITY_STATE_PROOF_AUTHORIZED == "proof_claimability_authorized"


def test_public_wallet_runtime_uses_named_claimability_state_constant_only() -> None:
    source = Path("ilc_core/protocol/public_wallet_runtime.py").read_text(encoding="utf-8")

    assert (
        'WALLET_CLAIMABILITY_STATE_PROOF_AUTHORIZED = "proof_claimability_authorized"'
        in source
    )
    assert source.count('"proof_claimability_authorized"') == 1
    assert '"claimability_state": "deferred"' not in source
    assert "public_claimability_activated" not in source


def test_transfer_spend_withdrawal_guards_remain_false() -> None:
    manifest = wallet_action_semantics_preflight_manifest()

    assert manifest["wallet_transfer_enabled"] is False
    assert manifest["wallet_withdrawal_enabled"] is False
    assert manifest["wallet_spend_enabled"] is False
    assert manifest["public_claimability_activated"] is False
    assert "public_claimability_activated" in wallet_action_semantics_preflight._FALSE_AUTHORIZATION_FLAGS


@pytest.mark.parametrize(
    ("field", "kwargs"),
    [
        ("wallet_transfer_enabled", {"wallet_transfer_enabled": True}),
        ("wallet_withdrawal_enabled", {"wallet_withdrawal_enabled": True}),
        ("wallet_spend_enabled", {"wallet_spend_enabled": True}),
        ("public_claimability_activated", {"public_claimability_activated": True}),
    ],
)
def test_wallet_action_preflight_still_rejects_activation_flags(
    field: str,
    kwargs: dict[str, bool],
) -> None:
    with pytest.raises(WalletActionSemanticsPreflightError):
        build_wallet_action_semantics_preflight_packet(current_epoch=0, **kwargs)


def test_sidecar_phase_1438_authority_is_prerequisite_not_wallet_write() -> None:
    manifest = claimability_receipt_verifier.claimability_receipt_verifier_manifest()

    assert manifest["public_claimability_activated"] is True
    assert manifest["tokens"].count(
        claimability_receipt_verifier.PUBLIC_CLAIMABILITY_ACTIVATED_PHASE_1438_TOKEN
    ) == 1
    assert manifest["wallet_ops_authorized"] is False
    assert manifest["ecu_mint_authorized"] is False
    assert manifest["ilc_settlement_authorized"] is False


def test_external_address_claimability_surface_absent_from_public_wallet_runtime() -> None:
    source = Path("ilc_core/protocol/public_wallet_runtime.py").read_text(encoding="utf-8")

    assert "external_address" not in source
    assert "external_chain" not in source
    assert "withdraw" not in source
    assert "transfer" not in source
    assert "spend" not in source
