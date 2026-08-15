# SPDX-License-Identifier: AGPL-3.0-only
"""Schema-only ILC transfer intent envelope.

This module defines the Python value-action shape used by the LIVE-RC lane.
It does not sign, submit, settle, or activate transfer capability.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from ilc_core.epoch.genesis_settlement_destination import GENESIS_AGENT1_AGENT_ID
from ilc_core.genesis.genesis_value_action_guard import (
    GenesisValueActionPolicyCertificate,
    enforce_genesis_value_guard,
)
from ilc_core.ledger.exact_numeric import decimal_to_canonical_string

ILC_TRANSFER_INTENT_VERSION = "ilc_transfer_intent_01.v0.1"
ILC_TRANSFER_ENABLED = True  # Activated: Phase GAP-VALUE-ACTION-LIVE-RC-08

_AGENT_ID_HEX_LENGTH = 96
_AGENT_ID_RE = re.compile(r"^[0-9a-f]{96}$")
_MEMO_MAX_BYTES = 256
_NONCE_MAX_BYTES = 256         # generous ceiling; valid nonce is ~123 ASCII bytes
_GRAPH_CONTEXT_ANCHOR_MAX_BYTES = 512
_COSE_SIGNATURE_MAX_BYTES = 16 * 1024
_MICRO_ILC_FACTOR = Decimal("1000000")
_U64_MAX = 18_446_744_073_709_551_615
GENESIS_ILC_ACTION_CLASS = "PAYMENT"


class ActionType(str, Enum):
    """Agent action discriminator values."""

    ILC_TRANSFER = "ILC_TRANSFER"


@dataclass(frozen=True)
class AgentActionEnvelope:
    """Canonical schema for a value-action submitted by an AgentID."""

    action_type: ActionType
    sender_agent_id: str
    recipient_agent_id: str
    amount_ilc: Decimal
    nonce: str
    epoch: int
    memo: str | None = None
    graph_context_anchor: str | None = None
    cose_signature: bytes | None = None
    signed_at_epoch: int | None = None


def _require_agent_id(value: str, token: str) -> None:
    if not isinstance(value, str):
        raise ValueError(token)
    if len(value) != _AGENT_ID_HEX_LENGTH:
        raise ValueError(token)
    if _AGENT_ID_RE.fullmatch(value) is None:
        raise ValueError(token)


def _require_epoch(value: int, token: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(token)
    if value < 0:
        raise ValueError(token)


def _require_canonical_non_empty_string(value: str | None, token: str) -> None:
    if not isinstance(value, str):
        raise ValueError(token)
    if not value:
        raise ValueError(token)
    if value != value.strip():
        raise ValueError(token)


def _require_utf8_max_bytes(value: str, max_bytes: int, token: str) -> None:
    if len(value.encode("utf-8")) > max_bytes:
        raise ValueError(token)


def validate_envelope(env: AgentActionEnvelope) -> None:
    """Validate an AgentActionEnvelope and fail closed with stable tokens."""
    if not isinstance(env, AgentActionEnvelope):
        raise TypeError("invalid_envelope_type")
    if env.action_type != ActionType.ILC_TRANSFER:
        raise ValueError("invalid_envelope_action_type")

    _require_agent_id(env.sender_agent_id, "invalid_envelope_sender_agent_id")
    _require_agent_id(env.recipient_agent_id, "invalid_envelope_recipient_agent_id")
    if env.sender_agent_id == env.recipient_agent_id:
        raise ValueError("invalid_envelope_self_transfer")

    if not isinstance(env.amount_ilc, Decimal):
        raise TypeError("invalid_envelope_amount_not_decimal")
    if not env.amount_ilc.is_finite():
        raise ValueError("invalid_amount_non_finite")
    if env.amount_ilc <= Decimal("0"):
        raise ValueError("invalid_envelope_amount_not_positive")
    decimal_to_canonical_string(env.amount_ilc)
    _amount_ilc_to_micro_ilc(env.amount_ilc)

    _require_canonical_non_empty_string(env.nonce, "invalid_envelope_empty_nonce")
    _require_utf8_max_bytes(env.nonce, _NONCE_MAX_BYTES, "invalid_envelope_nonce_too_long")
    _require_epoch(env.epoch, "invalid_envelope_epoch")
    if env.signed_at_epoch is not None:
        _require_epoch(env.signed_at_epoch, "invalid_envelope_signed_at_epoch")
    if env.memo is not None:
        if not isinstance(env.memo, str):
            raise ValueError("invalid_envelope_memo")
        _require_utf8_max_bytes(env.memo, _MEMO_MAX_BYTES, "invalid_envelope_memo_too_long")
    if env.graph_context_anchor is not None:
        _require_canonical_non_empty_string(
            env.graph_context_anchor,
            "invalid_envelope_graph_context_anchor",
        )
        _require_utf8_max_bytes(
            env.graph_context_anchor,
            _GRAPH_CONTEXT_ANCHOR_MAX_BYTES,
            "invalid_envelope_graph_context_anchor_too_long",
        )
    if env.cose_signature is not None:
        if not isinstance(env.cose_signature, bytes) or len(env.cose_signature) == 0:
            raise ValueError("invalid_envelope_cose_signature")
        if len(env.cose_signature) > _COSE_SIGNATURE_MAX_BYTES:
            raise ValueError("invalid_envelope_cose_signature_too_long")


def enforce_genesis_envelope_guard(
    env: AgentActionEnvelope,
    *,
    genesis_value_certificate: GenesisValueActionPolicyCertificate | None,
    current_epoch_spent_micro_ilc: int | None,
) -> None:
    """Apply the CDL-110 Genesis source-agent guard to ILC transfer envelopes.

    Settled ILC transfers are classified as CDL-110 PAYMENT actions. The
    pre-RC path reads the effective epoch from the signed envelope; a later
    consensus-bound path should inject the current protocol epoch instead.
    """
    if env.sender_agent_id != GENESIS_AGENT1_AGENT_ID:
        return
    enforce_genesis_value_guard(
        source_agent_id=env.sender_agent_id,
        certificate=genesis_value_certificate,
        action_class=GENESIS_ILC_ACTION_CLASS,
        amount_micro_unit=_amount_ilc_to_micro_ilc(env.amount_ilc),
        current_epoch=env.epoch,
        recipient_agent_id=env.recipient_agent_id,
        graph_context_anchor=env.graph_context_anchor,
        consent_or_agreement_reference=env.memo,
        unit="ILC",
        current_epoch_spent_micro_unit=current_epoch_spent_micro_ilc,
    )


def _amount_ilc_to_micro_ilc(amount_ilc: Decimal) -> int:
    if not isinstance(amount_ilc, Decimal):
        raise TypeError("invalid_envelope_amount_not_decimal")
    if not amount_ilc.is_finite():
        raise ValueError("invalid_amount_non_finite")
    scaled_amount = amount_ilc * _MICRO_ILC_FACTOR
    if scaled_amount != scaled_amount.to_integral_value():
        raise ValueError("invalid_envelope_amount_fractional_micro_ilc")
    amount_micro_ilc = int(scaled_amount)
    if amount_micro_ilc <= 0:
        raise ValueError("invalid_envelope_amount_not_positive")
    if amount_micro_ilc > _U64_MAX:
        raise ValueError("amount_micro_ilc_exceeds_u64_max")
    return amount_micro_ilc


class ILCTransferIntent:
    """Factory and validator for ILC_TRANSFER AgentActionEnvelope instances."""

    @staticmethod
    def create(
        sender_agent_id: str,
        recipient_agent_id: str,
        amount_ilc: Decimal,
        nonce: str,
        epoch: int,
        memo: str | None = None,
        graph_context_anchor: str | None = None,
    ) -> AgentActionEnvelope:
        env = AgentActionEnvelope(
            action_type=ActionType.ILC_TRANSFER,
            sender_agent_id=sender_agent_id,
            recipient_agent_id=recipient_agent_id,
            amount_ilc=amount_ilc,
            nonce=nonce,
            epoch=epoch,
            memo=memo,
            graph_context_anchor=graph_context_anchor,
        )
        validate_envelope(env)
        return env


__all__ = [
    "ActionType",
    "AgentActionEnvelope",
    "GENESIS_ILC_ACTION_CLASS",
    "ILCTransferIntent",
    "ILC_TRANSFER_ENABLED",
    "ILC_TRANSFER_INTENT_VERSION",
    "MAX_COSE_SIGNATURE_BYTES",
    "MAX_GRAPH_CONTEXT_ANCHOR_BYTES",
    "MAX_GRAPH_CONTEXT_ANCHOR_CHARS",
    "MAX_MEMO_BYTES",
    "MAX_NONCE_BYTES",
    "MAX_NONCE_CHARS",
    "enforce_genesis_envelope_guard",
    "validate_envelope",
]

# Public aliases for the byte-size caps so tests can import them symbolically.
MAX_MEMO_BYTES = _MEMO_MAX_BYTES
MAX_NONCE_BYTES = _NONCE_MAX_BYTES
MAX_GRAPH_CONTEXT_ANCHOR_BYTES = _GRAPH_CONTEXT_ANCHOR_MAX_BYTES
MAX_COSE_SIGNATURE_BYTES = _COSE_SIGNATURE_MAX_BYTES

# Backward-compatible aliases retained for older tests; caps are byte-based.
MAX_NONCE_CHARS = _NONCE_MAX_BYTES
MAX_GRAPH_CONTEXT_ANCHOR_CHARS = _GRAPH_CONTEXT_ANCHOR_MAX_BYTES
