# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from typing import Any

from ilc_core.ecu.ecu_fast_path_intent import (
    ECU_FAST_PATH_TRANSFER_ENABLED,
    ECUFastPathIntent,
    TransferClass,
    validate_intent,
)
from ilc_core.ecu.ecu_transfer_context_verifier import (
    ECUContextVerificationError,
    ECUTransferContextVerifier,
    _intent_to_micro_ecu,
)

ECU_TRANSFER_ADAPTER_VERSION = "ecu_transfer_adapter_03.v0.1"


class ECUTransferAdapter:
    """Default-off Python adapter for Rust-compatible ECUTransfer payloads."""

    def __init__(
        self,
        consensus_bridge: Any,
        *,
        verifier: ECUTransferContextVerifier | None = None,
    ) -> None:
        if consensus_bridge is None:
            raise ValueError("consensus_bridge_required")
        self._bridge = consensus_bridge
        self._verifier = verifier or ECUTransferContextVerifier()

    def submit(self, intent: ECUFastPathIntent, sender_key_material: Any) -> str:
        if ECU_FAST_PATH_TRANSFER_ENABLED is False:
            raise ValueError("transfer_not_enabled_activation_guard_blocks_submit")

        self._verifier.verify(intent)
        payload = self._build_transfer_payload(intent)
        submit = getattr(self._bridge, "submit", None)
        if not callable(submit):
            raise ValueError("consensus_bridge_missing_submit")

        result = submit(payload, sender_key_material=sender_key_material)
        if isinstance(result, str) and result:
            return result
        transfer_reference = getattr(result, "transfer_reference", None)
        if isinstance(transfer_reference, str) and transfer_reference:
            return transfer_reference
        proposal_id = getattr(result, "proposal_id", None)
        if isinstance(proposal_id, str) and proposal_id:
            return proposal_id
        raise ValueError("consensus_bridge_submit_reference_invalid")

    def _build_transfer_payload(self, intent: ECUFastPathIntent) -> dict[str, Any]:
        validate_intent(intent)
        amount_micro_ecu = _intent_to_micro_ecu(intent.amount_ecu)
        transfer_class = (
            "Contribution"
            if intent.transfer_class is TransferClass.CONTRIBUTION
            else "Payment"
        )
        return {
            "to": intent.recipient_agent_id,
            "amount_micro_ecu": amount_micro_ecu,
            "transfer_class": transfer_class,
            "express_consent": intent.express_consent,
            "nonce": intent.nonce,
            "sender_agent_id": intent.sender_agent_id,
        }


__all__ = [
    "ECU_TRANSFER_ADAPTER_VERSION",
    "ECUTransferAdapter",
    "ECUContextVerificationError",
]
