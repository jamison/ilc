# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

# SHA-384 of ML-DSA-65 root public key — 48 bytes = 96 lowercase hex chars.
# Same pattern as ilc_transfer_intent._AGENT_ID_RE and action_nonce_store._AGENT_ID_RE.
_AGENT_ID_RE = re.compile(r"^[0-9a-f]{96}$")
MAX_GRAPH_CONTEXT_ANCHOR_BYTES = 512
MAX_EXPRESS_CONSENT_BYTES = 512
MAX_NONCE_BYTES = 128

ECU_FAST_PATH_TRANSFER_ENABLED = True
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
    graph_context_anchor: str | None
    express_consent: str | None
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
    if _AGENT_ID_RE.fullmatch(intent.sender_agent_id) is None:
        raise ValueError("invalid_sender_agent_id_format")
    if _AGENT_ID_RE.fullmatch(intent.recipient_agent_id) is None:
        raise ValueError("invalid_recipient_agent_id_format")
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
        if len(intent.graph_context_anchor.encode("utf-8")) > MAX_GRAPH_CONTEXT_ANCHOR_BYTES:
            raise ValueError("invalid_graph_context_anchor_too_large")
    if intent.transfer_class is TransferClass.CONTRIBUTION and not _present(intent.graph_context_anchor):
        raise ValueError("contribution_class_requires_graph_context_anchor")
    if intent.transfer_class is TransferClass.CONTRIBUTION and intent.express_consent is not None:
        raise ValueError("contribution_class_forbids_express_consent")
    if intent.express_consent is not None:
        if not isinstance(intent.express_consent, str):
            raise ValueError("invalid_express_consent_type")
        if not intent.express_consent or intent.express_consent != intent.express_consent.strip():
            raise ValueError("invalid_express_consent_whitespace")
        if len(intent.express_consent.encode("utf-8")) > MAX_EXPRESS_CONSENT_BYTES:
            raise ValueError("invalid_express_consent_too_large")
    if not isinstance(intent.nonce, str) or not intent.nonce.strip():
        raise ValueError("invalid_nonce_empty")
    if intent.nonce != intent.nonce.strip():
        raise ValueError("invalid_nonce_whitespace")
    if len(intent.nonce.encode("utf-8")) > MAX_NONCE_BYTES:
        raise ValueError("invalid_nonce_too_large")
    if (
        not isinstance(intent.created_epoch, int)
        or isinstance(intent.created_epoch, bool)
        or intent.created_epoch < 0
    ):
        raise ValueError("invalid_created_epoch")


def _present(value: str | None) -> bool:
    return isinstance(value, str) and bool(value.strip())


__all__ = [
    "ECU_FAST_PATH_INTENT_VERSION",
    "ECU_FAST_PATH_TRANSFER_ENABLED",
    "MAX_EXPRESS_CONSENT_BYTES",
    "MAX_GRAPH_CONTEXT_ANCHOR_BYTES",
    "MAX_NONCE_BYTES",
    "PRE_RC_TRANSFER_CAP_ECU",
    "ECUFastPathIntent",
    "TransferClass",
    "validate_intent",
]
