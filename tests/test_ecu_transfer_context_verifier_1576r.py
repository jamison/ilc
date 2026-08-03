# SPDX-License-Identifier: AGPL-3.0-only
from decimal import Decimal
from unittest.mock import patch

import pytest

from ilc_core.ecu.ecu_fast_path_intent import ECUFastPathIntent, TransferClass
from ilc_core.ecu import ecu_fast_path_intent
from ilc_core.ecu.ecu_transfer_context_verifier import (
    ECU_TRANSFER_CONTEXT_VERIFIER_VERSION,
    ECUContextVerificationError,
    ECUTransferContextVerifier,
    _intent_to_micro_ecu,
)


class _GraphReader:
    def __init__(self, nodes: dict[str, object]) -> None:
        self._nodes = nodes

    def get_node(self, anchor: str) -> object | None:
        return self._nodes.get(anchor)


def _intent(**overrides: object) -> ECUFastPathIntent:
    fields = {
        "sender_agent_id": "agent_sender",
        "recipient_agent_id": "agent_recipient",
        "amount_ecu": Decimal("7.25"),
        "transfer_class": TransferClass.CONTRIBUTION,
        "graph_context_anchor": "node:artifact:abc123",
        "express_consent": None,
        "nonce": "550e8400-e29b-41d4-a716-446655440000",
        "created_epoch": 0,
    }
    fields.update(overrides)
    return ECUFastPathIntent(**fields)


def _raises_token(token: str, verifier: ECUTransferContextVerifier, intent: ECUFastPathIntent) -> None:
    with pytest.raises(ECUContextVerificationError, match=f"^{token}$"):
        verifier.verify(intent)


def test_happy_path_contribution_with_anchor_stub_mode() -> None:
    with patch("ilc_core.ecu.ecu_transfer_context_verifier.ECU_FAST_PATH_TRANSFER_ENABLED", True):
        ECUTransferContextVerifier().verify(_intent())


def test_happy_path_payment_no_anchor_stub_mode() -> None:
    intent = _intent(transfer_class=TransferClass.PAYMENT, graph_context_anchor=None)
    with patch("ilc_core.ecu.ecu_transfer_context_verifier.ECU_FAST_PATH_TRANSFER_ENABLED", True):
        ECUTransferContextVerifier().verify(intent)


def test_happy_path_payment_with_anchor_and_graph_reader() -> None:
    intent = _intent(transfer_class=TransferClass.PAYMENT)
    verifier = ECUTransferContextVerifier(
        graph_reader=_GraphReader({"node:artifact:abc123": object()})
    )
    with patch("ilc_core.ecu.ecu_transfer_context_verifier.ECU_FAST_PATH_TRANSFER_ENABLED", True):
        verifier.verify(intent)


def test_payment_with_anchor_and_missing_graph_node_fails_closed() -> None:
    intent = _intent(transfer_class=TransferClass.PAYMENT)
    verifier = ECUTransferContextVerifier(graph_reader=_GraphReader({}))
    with patch("ilc_core.ecu.ecu_transfer_context_verifier.ECU_FAST_PATH_TRANSFER_ENABLED", True):
        _raises_token("graph_context_anchor_not_found", verifier, intent)


def test_contribution_without_anchor_raises_in_verifier() -> None:
    with patch("ilc_core.ecu.ecu_transfer_context_verifier.ECU_FAST_PATH_TRANSFER_ENABLED", True):
        _raises_token(
            "contribution_class_requires_graph_context_anchor_verifier",
            ECUTransferContextVerifier(),
            _intent(graph_context_anchor=None),
        )


def test_activation_guard_blocks_when_disabled() -> None:
    _raises_token(
        "transfer_not_enabled_activation_guard_blocks_submission",
        ECUTransferContextVerifier(),
        _intent(),
    )


def test_source_module_activation_assignment_does_not_mutate_verifier_binding(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(ecu_fast_path_intent, "ECU_FAST_PATH_TRANSFER_ENABLED", True)

    _raises_token(
        "transfer_not_enabled_activation_guard_blocks_submission",
        ECUTransferContextVerifier(),
        _intent(),
    )


def test_u64_overflow_raises() -> None:
    with pytest.raises(ECUContextVerificationError, match="^amount_micro_ecu_exceeds_u64_max$"):
        _intent_to_micro_ecu(Decimal("18446744073709.551616"))


def test_graph_node_not_found_raises() -> None:
    verifier = ECUTransferContextVerifier(graph_reader=_GraphReader({}))
    with patch("ilc_core.ecu.ecu_transfer_context_verifier.ECU_FAST_PATH_TRANSFER_ENABLED", True):
        _raises_token("graph_context_anchor_not_found", verifier, _intent())


def test_verifier_version_constant_accessible() -> None:
    assert ECU_TRANSFER_CONTEXT_VERIFIER_VERSION == "ecu_transfer_context_verifier_02.v0.1"


def test_non_finite_decimal_to_micro_ecu_raises() -> None:
    with pytest.raises(
        ECUContextVerificationError,
        match="^invalid_amount_non_finite_in_micro_ecu_conversion$",
    ):
        _intent_to_micro_ecu(Decimal("NaN"))


def test_infinite_decimal_to_micro_ecu_raises() -> None:
    with pytest.raises(
        ECUContextVerificationError,
        match="^invalid_amount_non_finite_in_micro_ecu_conversion$",
    ):
        _intent_to_micro_ecu(Decimal("Infinity"))


def test_fractional_micro_ecu_rejected_without_truncation() -> None:
    with pytest.raises(ECUContextVerificationError, match="^invalid_amount_fractional_micro_ecu$"):
        _intent_to_micro_ecu(Decimal("0.0000001"))


def test_graph_reader_without_get_node_fails_closed() -> None:
    verifier = ECUTransferContextVerifier(graph_reader=object())
    with patch("ilc_core.ecu.ecu_transfer_context_verifier.ECU_FAST_PATH_TRANSFER_ENABLED", True):
        _raises_token("graph_reader_missing_get_node", verifier, _intent())


def test_graph_node_found_passes() -> None:
    verifier = ECUTransferContextVerifier(graph_reader=_GraphReader({"node:artifact:abc123": object()}))
    with patch("ilc_core.ecu.ecu_transfer_context_verifier.ECU_FAST_PATH_TRANSFER_ENABLED", True):
        verifier.verify(_intent())
