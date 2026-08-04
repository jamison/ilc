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
_RUST_ECU_TRANSFER_KEYS = frozenset(
    {"object_ref", "to", "amount_micro_ecu", "transfer_class", "sender_sig"}
)
_OBJECT_REF_KEYS = frozenset({"agent", "version"})
_U64_MAX = 18446744073709551615
_MAX_SENDER_SIG_BYTES = 4096


class ECUTransferAdapter:
    """Default-off adapter requiring bridge-built Rust ECUTransfer payloads."""

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

    def submit(self, intent: ECUFastPathIntent) -> str:
        if ECU_FAST_PATH_TRANSFER_ENABLED is False:
            raise ValueError("transfer_not_enabled_activation_guard_blocks_submit")

        self._verifier.verify(intent)
        bridge_payload = self._build_transfer_payload(intent)
        build_ecu_transfer = getattr(self._bridge, "build_ecu_transfer", None)
        if not callable(build_ecu_transfer):
            raise ValueError("consensus_bridge_missing_build_ecu_transfer")
        rust_payload = build_ecu_transfer(bridge_payload)
        self._validate_rust_transfer_payload(rust_payload, intent)

        submit = getattr(self._bridge, "submit", None)
        if not callable(submit):
            raise ValueError("consensus_bridge_missing_submit")

        result = submit(rust_payload)
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
        """Build the command; the Rust bridge adds ObjectRef/signature locally."""
        validate_intent(intent)
        amount_micro_ecu = _intent_to_micro_ecu(intent.amount_ecu)
        transfer_class = _bridge_transfer_class(intent)
        return {
            "bridge_payload_version": ECU_TRANSFER_ADAPTER_VERSION,
            "amount_micro_ecu": amount_micro_ecu,
            "express_consent": intent.express_consent,
            "graph_context_anchor": intent.graph_context_anchor,
            "nonce": intent.nonce,
            "sender_agent_id": intent.sender_agent_id,
            "to": intent.recipient_agent_id,
            "transfer_class": transfer_class,
        }

    def _validate_rust_transfer_payload(
        self,
        payload: Any,
        intent: ECUFastPathIntent,
    ) -> None:
        validate_rust_transfer_payload(payload, intent)


def _bridge_transfer_class(intent: ECUFastPathIntent) -> dict[str, Any]:
    if intent.transfer_class is TransferClass.CONTRIBUTION:
        return {"type": "Contribution"}
    if intent.transfer_class is TransferClass.PAYMENT:
        express = None
        if intent.express_consent is not None:
            express = {
                "agent_acknowledged_timing_disclosure": True,
                "consent_epoch": intent.created_epoch,
            }
        return {"type": "Payment", "express": express}
    raise ValueError("unknown_transfer_class")


def _rust_serde_transfer_class(intent: ECUFastPathIntent) -> Any:
    if intent.transfer_class is TransferClass.CONTRIBUTION:
        return "Contribution"
    if intent.transfer_class is TransferClass.PAYMENT:
        express = None
        if intent.express_consent is not None:
            express = {
                "agent_acknowledged_timing_disclosure": True,
                "consent_epoch": intent.created_epoch,
            }
        return {"Payment": {"express": express}}
    raise ValueError("unknown_transfer_class")


def validate_rust_transfer_payload(payload: Any, intent: ECUFastPathIntent) -> None:
    if not isinstance(payload, dict):
        raise ValueError("rust_ecu_transfer_payload_invalid_type")
    if set(payload) != _RUST_ECU_TRANSFER_KEYS:
        raise ValueError("rust_ecu_transfer_payload_field_set_invalid")

    object_ref = payload["object_ref"]
    if not isinstance(object_ref, dict) or set(object_ref) != _OBJECT_REF_KEYS:
        raise ValueError("rust_ecu_transfer_object_ref_invalid")
    if object_ref["agent"] != intent.sender_agent_id:
        raise ValueError("rust_ecu_transfer_object_ref_agent_mismatch")
    version = object_ref["version"]
    if isinstance(version, bool) or not isinstance(version, int) or version < 0 or version > _U64_MAX:
        raise ValueError("rust_ecu_transfer_object_ref_version_invalid")

    if payload["to"] != intent.recipient_agent_id:
        raise ValueError("rust_ecu_transfer_recipient_mismatch")
    if payload["amount_micro_ecu"] != _intent_to_micro_ecu(intent.amount_ecu):
        raise ValueError("rust_ecu_transfer_amount_mismatch")
    if payload["transfer_class"] != _rust_serde_transfer_class(intent):
        raise ValueError("rust_ecu_transfer_class_mismatch")

    sender_sig = payload["sender_sig"]
    if isinstance(sender_sig, bytes):
        if not sender_sig or len(sender_sig) > _MAX_SENDER_SIG_BYTES:
            raise ValueError("rust_ecu_transfer_sender_sig_invalid")
    elif isinstance(sender_sig, str):
        if not sender_sig or sender_sig != sender_sig.strip() or len(sender_sig) > _MAX_SENDER_SIG_BYTES * 2:
            raise ValueError("rust_ecu_transfer_sender_sig_invalid")
    else:
        raise ValueError("rust_ecu_transfer_sender_sig_invalid")


__all__ = [
    "ECU_TRANSFER_ADAPTER_VERSION",
    "ECUTransferAdapter",
    "ECUContextVerificationError",
    "validate_rust_transfer_payload",
]
