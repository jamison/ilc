# SPDX-License-Identifier: AGPL-3.0-only
from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from ilc_core.ecu.ecu_fast_path_intent import (
    ECU_FAST_PATH_INTENT_VERSION,
    ECU_FAST_PATH_TRANSFER_ENABLED,
    PRE_RC_TRANSFER_CAP_ECU,
    ECUFastPathIntent,
    TransferClass,
    validate_intent,
)


def _intent(**overrides: object) -> ECUFastPathIntent:
    fields = {
        "sender_agent_id": "agent_sender",
        "recipient_agent_id": "agent_recipient",
        "amount_ecu": Decimal("12.5"),
        "transfer_class": TransferClass.CONTRIBUTION,
        "graph_context_anchor": "node:artifact:abc123",
        "express_consent": None,
        "nonce": "550e8400-e29b-41d4-a716-446655440000",
        "created_epoch": 0,
    }
    fields.update(overrides)
    return ECUFastPathIntent(**fields)


def _raises_token(intent: ECUFastPathIntent, token: str) -> None:
    with pytest.raises(ValueError, match=f"^{token}$"):
        validate_intent(intent)


def test_happy_path_contribution() -> None:
    validate_intent(_intent())


def test_happy_path_payment_no_anchor() -> None:
    validate_intent(
        _intent(
            transfer_class=TransferClass.PAYMENT,
            graph_context_anchor=None,
        )
    )


def test_happy_path_payment_with_express_consent() -> None:
    validate_intent(
        _intent(
            transfer_class=TransferClass.PAYMENT,
            graph_context_anchor=None,
            express_consent="payment_consent:550e8400",
        )
    )


def test_contribution_without_anchor_raises() -> None:
    _raises_token(
        _intent(graph_context_anchor=None),
        "contribution_class_requires_graph_context_anchor",
    )


def test_self_transfer_raises() -> None:
    _raises_token(
        _intent(recipient_agent_id="agent_sender"),
        "self_transfer_prohibited",
    )


def test_non_finite_decimal_nan_raises() -> None:
    _raises_token(
        _intent(amount_ecu=Decimal("NaN")),
        "invalid_amount_non_finite",
    )


def test_non_finite_decimal_infinity_raises() -> None:
    _raises_token(
        _intent(amount_ecu=Decimal("Infinity")),
        "invalid_amount_non_finite",
    )


def test_amount_exactly_at_pre_rc_cap_is_accepted() -> None:
    validate_intent(_intent(amount_ecu=PRE_RC_TRANSFER_CAP_ECU))


@pytest.mark.parametrize("bad_amount", [5, 5.0])
def test_invalid_amount_type_raises(bad_amount: object) -> None:
    _raises_token(
        _intent(amount_ecu=bad_amount),
        "invalid_amount_type",
    )


def test_negative_amount_raises() -> None:
    _raises_token(
        _intent(amount_ecu=Decimal("-1")),
        "invalid_amount_non_positive",
    )


def test_zero_amount_raises() -> None:
    _raises_token(
        _intent(amount_ecu=Decimal("0")),
        "invalid_amount_non_positive",
    )


def test_amount_above_pre_rc_cap_raises() -> None:
    _raises_token(
        _intent(amount_ecu=PRE_RC_TRANSFER_CAP_ECU + Decimal("0.000001")),
        "invalid_amount_exceeds_pre_rc_cap",
    )


def test_whitespace_only_contribution_anchor_raises_required_anchor() -> None:
    _raises_token(
        _intent(graph_context_anchor=" "),
        "invalid_graph_context_anchor_whitespace",
    )


def test_padded_graph_context_anchor_raises() -> None:
    _raises_token(
        _intent(graph_context_anchor=" node:artifact:abc123 "),
        "invalid_graph_context_anchor_whitespace",
    )


def test_non_string_graph_context_anchor_raises() -> None:
    _raises_token(
        _intent(graph_context_anchor=123),
        "invalid_graph_context_anchor_type",
    )


def test_string_transfer_class_raises() -> None:
    _raises_token(
        _intent(transfer_class="CONTRIBUTION"),
        "invalid_transfer_class",
    )


def test_empty_identity_and_nonce_tokens() -> None:
    _raises_token(_intent(sender_agent_id=""), "invalid_sender_agent_id_empty")
    _raises_token(_intent(recipient_agent_id=" "), "invalid_recipient_agent_id_empty")
    _raises_token(_intent(nonce=""), "invalid_nonce_empty")


def test_invalid_epoch_raises() -> None:
    _raises_token(_intent(created_epoch=-1), "invalid_created_epoch")
    _raises_token(_intent(created_epoch=True), "invalid_created_epoch")


def test_intent_is_frozen_and_guard_is_default_off() -> None:
    intent = _intent()
    assert ECU_FAST_PATH_TRANSFER_ENABLED is False
    assert ECU_FAST_PATH_INTENT_VERSION == "ecu_fast_path_intent_01.v0.1"
    with pytest.raises(FrozenInstanceError):
        intent.amount_ecu = Decimal("2")
