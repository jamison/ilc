# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1438 CDL-088 public claimability authority sidecar.

This module records the public-claimability authority flip only. The HTTP
serving route remains Phase 1439 scope, and ECU mint, ILC settlement, wallet
operations, public RC publication, native Rust P2P, and epoch transition remain
unauthorized.
"""

from __future__ import annotations

CDL088_PUBLIC_CLAIMABILITY_ACTIVATED: bool = True
PUBLIC_CLAIMABILITY_ACTIVATION_PHASE: str = "phase_1438"

CDL_088_PUBLIC_CLAIMABILITY_AUTHORITY_TOKEN = (
    "cdl_088_is_public_claimability_api_authority_phase_1389a"
)
PUBLIC_CLAIMABILITY_ACTIVATED_PHASE_1438_TOKEN = (
    "public_claimability_activated_phase_1438"
)
CDL088_PUBLIC_CLAIMABILITY_ACTIVATION_COMMITTED_PHASE_1438_TOKEN = (
    "cdl088_public_claimability_activation_committed_phase_1438"
)
ECU_MINT_NOT_AUTHORIZED_PHASE_1438_TOKEN = "ecu_mint_not_authorized_phase_1438"
ILC_SETTLEMENT_NOT_AUTHORIZED_PHASE_1438_TOKEN = (
    "ilc_settlement_not_authorized_phase_1438"
)
WALLET_OPS_NOT_AUTHORIZED_PHASE_1438_TOKEN = "wallet_ops_not_authorized_phase_1438"
PUBLIC_RC_NOT_ACTIVATED_PHASE_1438_TOKEN = "public_rc_not_activated_phase_1438"
NATIVE_RUST_P2P_NOT_ACTIVATED_PHASE_1438_TOKEN = (
    "native_rust_p2p_not_activated_phase_1438"
)
EPOCH_TRANSITION_NOT_TRIGGERED_PHASE_1438_TOKEN = (
    "epoch_transition_not_triggered_phase_1438"
)

PHASE_1438_ACTIVATION_TOKENS: tuple[str, ...] = (
    PUBLIC_CLAIMABILITY_ACTIVATED_PHASE_1438_TOKEN,
    CDL088_PUBLIC_CLAIMABILITY_ACTIVATION_COMMITTED_PHASE_1438_TOKEN,
    ECU_MINT_NOT_AUTHORIZED_PHASE_1438_TOKEN,
    ILC_SETTLEMENT_NOT_AUTHORIZED_PHASE_1438_TOKEN,
    WALLET_OPS_NOT_AUTHORIZED_PHASE_1438_TOKEN,
    PUBLIC_RC_NOT_ACTIVATED_PHASE_1438_TOKEN,
    NATIVE_RUST_P2P_NOT_ACTIVATED_PHASE_1438_TOKEN,
    EPOCH_TRANSITION_NOT_TRIGGERED_PHASE_1438_TOKEN,
)


def cdl088_public_claimability_activation_manifest() -> dict[str, object]:
    return {
        "activation_phase": PUBLIC_CLAIMABILITY_ACTIVATION_PHASE,
        "cdl_088_authority_token": CDL_088_PUBLIC_CLAIMABILITY_AUTHORITY_TOKEN,
        "ecu_mint_authorized": False,
        "epoch_transition_triggered": False,
        "ilc_settlement_authorized": False,
        "native_rust_p2p_activated": False,
        "public_claimability_activated": CDL088_PUBLIC_CLAIMABILITY_ACTIVATED,
        "public_rc_activated": False,
        "tokens": list(PHASE_1438_ACTIVATION_TOKENS),
        "wallet_ops_authorized": False,
    }


__all__ = [
    "CDL088_PUBLIC_CLAIMABILITY_ACTIVATED",
    "CDL088_PUBLIC_CLAIMABILITY_ACTIVATION_COMMITTED_PHASE_1438_TOKEN",
    "CDL_088_PUBLIC_CLAIMABILITY_AUTHORITY_TOKEN",
    "ECU_MINT_NOT_AUTHORIZED_PHASE_1438_TOKEN",
    "EPOCH_TRANSITION_NOT_TRIGGERED_PHASE_1438_TOKEN",
    "ILC_SETTLEMENT_NOT_AUTHORIZED_PHASE_1438_TOKEN",
    "NATIVE_RUST_P2P_NOT_ACTIVATED_PHASE_1438_TOKEN",
    "PHASE_1438_ACTIVATION_TOKENS",
    "PUBLIC_CLAIMABILITY_ACTIVATED_PHASE_1438_TOKEN",
    "PUBLIC_CLAIMABILITY_ACTIVATION_PHASE",
    "PUBLIC_RC_NOT_ACTIVATED_PHASE_1438_TOKEN",
    "WALLET_OPS_NOT_AUTHORIZED_PHASE_1438_TOKEN",
    "cdl088_public_claimability_activation_manifest",
]
