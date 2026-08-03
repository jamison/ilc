# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

ECU_FAST_PATH_TRANSFER_ENABLED = False
ECU_FAST_PATH_INTENT_VERSION = "ecu_fast_path_intent_01.v0.1"
PRE_RC_TRANSFER_CAP_ECU = Decimal("1000")
_ZERO_ECU = Decimal("0")


class TransferClass(Enum):
    CONTRIBUTION = "CONTRIBUTION"
    PAYMENT = "PAYMENT"


@dataclass(frozen=True)
class ECUFastPathIntent:
    sender_agent_id: str
    recipient_agent_id: str
    amount_ecu: Decimal
    transfer_class: TransferClass
    graph_context_anchor: Optional[str]
    express_consent: Optional[str]
    nonce: str
    created_epoch: int


def validate_intent(intent: ECUFastPathIntent) -> None:
    if not isinstance(intent.sender_agent_id, str) or not intent.sender_agent_id.strip():
        raise ValueError("invalid_sender_agent_id_empty")
    if not isinstance(intent.recipient_agent_id, str) or not intent.recipient_agent_id.strip():
        raise ValueError("invalid_recipient_agent_id_empty")
    if intent.sender_agent_id != intent.sender_agent_id.strip():
        raise ValueError("invalid_sender_agent_id_whitespace")
    if intent.recipient_agent_id != intent.recipient_agent_id.strip():
        raise ValueError("invalid_recipient_agent_id_whitespace")
    if intent.sender_agent_id == intent.recipient_agent_id:
        raise ValueError("self_transfer_prohibited")
    if not isinstance(intent.amount_ecu, Decimal):
        raise ValueError("invalid_amount_type")
    if not intent.amount_ecu.is_finite():
        raise ValueError("invalid_amount_non_finite")
    if intent.amount_ecu <= _ZERO_ECU:
        raise ValueError("invalid_amount_non_positive")
    if intent.amount_ecu > PRE_RC_TRANSFER_CAP_ECU:
        raise ValueError("invalid_amount_exceeds_pre_rc_cap")
    if not isinstance(intent.transfer_class, TransferClass):
        raise ValueError("invalid_transfer_class")
    if intent.graph_context_anchor is not None:
        if not isinstance(intent.graph_context_anchor, str):
            raise ValueError("invalid_graph_context_anchor_type")
        if (
            not intent.graph_context_anchor
            or intent.graph_context_anchor != intent.graph_context_anchor.strip()
        ):
            raise ValueError("invalid_graph_context_anchor_whitespace")
    if intent.transfer_class is TransferClass.CONTRIBUTION and not _present(intent.graph_context_anchor):
        raise ValueError("contribution_class_requires_graph_context_anchor")
    if intent.transfer_class is TransferClass.CONTRIBUTION and intent.express_consent is not None:
        raise ValueError("contribution_class_forbids_express_consent")
    if intent.express_consent is not None:
        if not isinstance(intent.express_consent, str):
            raise ValueError("invalid_express_consent_type")
        if not intent.express_consent or intent.express_consent != intent.express_consent.strip():
            raise ValueError("invalid_express_consent_whitespace")
    if not isinstance(intent.nonce, str) or not intent.nonce.strip():
        raise ValueError("invalid_nonce_empty")
    _validate_uuid4_nonce(intent.nonce)
    if (
        not isinstance(intent.created_epoch, int)
        or isinstance(intent.created_epoch, bool)
        or intent.created_epoch < 0
    ):
        raise ValueError("invalid_created_epoch")


def _present(value: Optional[str]) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_uuid4_nonce(nonce: str) -> None:
    if nonce != nonce.strip():
        raise ValueError("invalid_nonce_whitespace")
    try:
        parsed = UUID(nonce)
    except ValueError as exc:
        raise ValueError("invalid_nonce_uuid4") from exc
    if parsed.version != 4 or str(parsed) != nonce:
        raise ValueError("invalid_nonce_uuid4")


__all__ = [
    "ECU_FAST_PATH_INTENT_VERSION",
    "ECU_FAST_PATH_TRANSFER_ENABLED",
    "PRE_RC_TRANSFER_CAP_ECU",
    "ECUFastPathIntent",
    "TransferClass",
    "validate_intent",
]
