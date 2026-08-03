# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from decimal import Decimal
from typing import Any

from ilc_core.ecu.ecu_fast_path_intent import (
    ECU_FAST_PATH_TRANSFER_ENABLED,
    ECUFastPathIntent,
    TransferClass,
    validate_intent,
)

ECU_TRANSFER_CONTEXT_VERIFIER_VERSION = "ecu_transfer_context_verifier_02.v0.1"
_U64_MAX = 18446744073709551615
_MICRO_ECU_FACTOR = Decimal("1000000")
_ZERO_MICRO_ECU = 0


class ECUContextVerificationError(ValueError):
    """Raised when ECU transfer context verification fails."""


def _intent_to_micro_ecu(amount_ecu: Decimal) -> int:
    if not isinstance(amount_ecu, Decimal):
        raise ECUContextVerificationError("invalid_amount_type_in_micro_ecu_conversion")
    if not amount_ecu.is_finite():
        raise ECUContextVerificationError("invalid_amount_non_finite_in_micro_ecu_conversion")

    scaled_amount = amount_ecu * _MICRO_ECU_FACTOR
    if scaled_amount != scaled_amount.to_integral_value():
        raise ECUContextVerificationError("invalid_amount_fractional_micro_ecu")

    amount_micro_ecu = int(scaled_amount)
    if amount_micro_ecu <= _ZERO_MICRO_ECU:
        raise ECUContextVerificationError("invalid_amount_micro_ecu_non_positive")
    if amount_micro_ecu > _U64_MAX:
        raise ECUContextVerificationError("amount_micro_ecu_exceeds_u64_max")
    return amount_micro_ecu


class ECUTransferContextVerifier:
    def __init__(self, graph_reader: Any = None) -> None:
        self._graph_reader = graph_reader

    def verify(self, intent: ECUFastPathIntent) -> None:
        # Activation is intentionally source-controlled for RC gates. Tests that
        # simulate activation must patch this module binding, not the imported
        # source module after import.
        if ECU_FAST_PATH_TRANSFER_ENABLED is False:
            raise ECUContextVerificationError("transfer_not_enabled_activation_guard_blocks_submission")

        try:
            validate_intent(intent)
        except ValueError as exc:
            raise ECUContextVerificationError(str(exc)) from exc

        if _present(intent.graph_context_anchor):
            if self._graph_reader is None:
                raise ECUContextVerificationError("graph_reader_required_for_graph_context_anchor")
            get_node = getattr(self._graph_reader, "get_node", None)
            if not callable(get_node):
                raise ECUContextVerificationError("graph_reader_missing_get_node")
            graph_context_anchor = intent.graph_context_anchor.strip()
            if get_node(graph_context_anchor) is None:
                raise ECUContextVerificationError("graph_context_anchor_not_found")

        # At the pre-RC cap this cannot overflow through verify(), but this
        # remains the Rust boundary guard if a later CDL raises transfer caps.
        _intent_to_micro_ecu(intent.amount_ecu)


def _present(value: str | None) -> bool:
    return isinstance(value, str) and bool(value.strip())


__all__ = [
    "ECU_TRANSFER_CONTEXT_VERIFIER_VERSION",
    "ECUContextVerificationError",
    "ECUTransferContextVerifier",
    "_intent_to_micro_ecu",
]
