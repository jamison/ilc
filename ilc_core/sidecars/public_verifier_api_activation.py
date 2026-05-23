"""Phase 1439 public claimability verifier API activation constants."""

from __future__ import annotations

PUBLIC_VERIFIER_API_ACTIVATED_PHASE_1439_TOKEN = (
    "public_verifier_api_activated_phase_1439"
)
CLAIMABILITY_API_SERVING_PATH_WIRED_PHASE_1439_TOKEN = (
    "claimability_api_serving_path_wired_phase_1439"
)
ECU_MINT_NOT_AUTHORIZED_PHASE_1439_TOKEN = "ecu_mint_not_authorized_phase_1439"
ILC_SETTLEMENT_NOT_AUTHORIZED_PHASE_1439_TOKEN = (
    "ilc_settlement_not_authorized_phase_1439"
)
WALLET_OPS_NOT_AUTHORIZED_PHASE_1439_TOKEN = "wallet_ops_not_authorized_phase_1439"
PUBLIC_RC_NOT_ACTIVATED_PHASE_1439_TOKEN = "public_rc_not_activated_phase_1439"

ACCEPTED_PUBLIC_VERIFIER_API_DECISION = "accepted_public_verifier_api_phase_1439"

PHASE_1439_PUBLIC_VERIFIER_API_TOKENS: tuple[str, ...] = (
    PUBLIC_VERIFIER_API_ACTIVATED_PHASE_1439_TOKEN,
    CLAIMABILITY_API_SERVING_PATH_WIRED_PHASE_1439_TOKEN,
    ECU_MINT_NOT_AUTHORIZED_PHASE_1439_TOKEN,
    ILC_SETTLEMENT_NOT_AUTHORIZED_PHASE_1439_TOKEN,
    WALLET_OPS_NOT_AUTHORIZED_PHASE_1439_TOKEN,
    PUBLIC_RC_NOT_ACTIVATED_PHASE_1439_TOKEN,
)


def public_verifier_api_activation_manifest() -> dict[str, object]:
    return {
        "accepted_decision_token": ACCEPTED_PUBLIC_VERIFIER_API_DECISION,
        "claimability_api_serving_path_wired": True,
        "ecu_mint_authorized": False,
        "ilc_settlement_authorized": False,
        "public_api_enabled": True,
        "public_claimability_activated": True,
        "public_rc_activated": False,
        "public_verifier_api_enabled": True,
        "receipt_verifier_public_serving_enabled": True,
        "route": "/api/v1/claimability/verify",
        "tokens": list(PHASE_1439_PUBLIC_VERIFIER_API_TOKENS),
        "wallet_ops_authorized": False,
    }


__all__ = [
    "ACCEPTED_PUBLIC_VERIFIER_API_DECISION",
    "CLAIMABILITY_API_SERVING_PATH_WIRED_PHASE_1439_TOKEN",
    "ECU_MINT_NOT_AUTHORIZED_PHASE_1439_TOKEN",
    "ILC_SETTLEMENT_NOT_AUTHORIZED_PHASE_1439_TOKEN",
    "PHASE_1439_PUBLIC_VERIFIER_API_TOKENS",
    "PUBLIC_RC_NOT_ACTIVATED_PHASE_1439_TOKEN",
    "PUBLIC_VERIFIER_API_ACTIVATED_PHASE_1439_TOKEN",
    "WALLET_OPS_NOT_AUTHORIZED_PHASE_1439_TOKEN",
    "public_verifier_api_activation_manifest",
]
