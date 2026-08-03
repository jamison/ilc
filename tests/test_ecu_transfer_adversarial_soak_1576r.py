# SPDX-License-Identifier: AGPL-3.0-only
from decimal import Decimal
from unittest.mock import patch

import pytest

from ilc_core.ecu.ecu_fast_path_intent import (
    PRE_RC_TRANSFER_CAP_ECU,
    ECUFastPathIntent,
    TransferClass,
    validate_intent,
)
from ilc_core.ecu.ecu_transfer_adapter import ECUTransferAdapter
from ilc_core.ecu.ecu_transfer_context_verifier import (
    ECUContextVerificationError,
    ECUTransferContextVerifier,
    _intent_to_micro_ecu,
)


class _GraphReader:
    def __init__(self, nodes: dict[str, object]) -> None:
        self._nodes = nodes

    def get_node(self, anchor: str) -> object | None:
        return self._nodes.get(anchor)


class _RecordingBridge:
    def __init__(self) -> None:
        self.payloads: list[dict[str, object]] = []

    def submit(self, payload: dict[str, object], *, sender_key_material: object) -> str:
        self.payloads.append(payload)
        return f"transfer-ref-{len(self.payloads)}"


def _intent(**overrides: object) -> ECUFastPathIntent:
    fields = {
        "sender_agent_id": "agent_sender",
        "recipient_agent_id": "agent_recipient",
        "amount_ecu": Decimal("3.25"),
        "transfer_class": TransferClass.CONTRIBUTION,
        "graph_context_anchor": "node:artifact:abc123",
        "express_consent": None,
        "nonce": "550e8400-e29b-41d4-a716-446655440000",
        "created_epoch": 0,
    }
    fields.update(overrides)
    return ECUFastPathIntent(**fields)


def _raises_value_token(intent: ECUFastPathIntent, token: str) -> None:
    with pytest.raises(ValueError, match=f"^{token}$"):
        validate_intent(intent)


def test_double_submit_same_nonce_gap_documented() -> None:
    intent = _intent()
    bridge = _RecordingBridge()
    adapter = ECUTransferAdapter(bridge)

    with (
        patch("ilc_core.ecu.ecu_transfer_adapter.ECU_FAST_PATH_TRANSFER_ENABLED", True),
        patch("ilc_core.ecu.ecu_transfer_context_verifier.ECU_FAST_PATH_TRANSFER_ENABLED", True),
    ):
        assert adapter.submit(intent, b"sender-key") == "transfer-ref-1"
        assert adapter.submit(intent, b"sender-key") == "transfer-ref-2"

    assert intent.nonce
    assert [payload["nonce"] for payload in bridge.payloads] == [intent.nonce, intent.nonce]


def test_non_finite_decimal_nan_rejected() -> None:
    _raises_value_token(_intent(amount_ecu=Decimal("NaN")), "invalid_amount_non_finite")


def test_non_finite_decimal_inf_rejected() -> None:
    _raises_value_token(_intent(amount_ecu=Decimal("Infinity")), "invalid_amount_non_finite")


def test_self_transfer_rejected_by_intent() -> None:
    _raises_value_token(_intent(recipient_agent_id="agent_sender"), "self_transfer_prohibited")


def test_contribution_without_anchor_rejected_by_intent() -> None:
    _raises_value_token(
        _intent(graph_context_anchor=None),
        "contribution_class_requires_graph_context_anchor",
    )


def test_contribution_without_anchor_rejected_by_verifier() -> None:
    intent = _intent(graph_context_anchor=None)
    with patch("ilc_core.ecu.ecu_transfer_context_verifier.ECU_FAST_PATH_TRANSFER_ENABLED", True):
        with pytest.raises(
            ECUContextVerificationError,
            match="^contribution_class_requires_graph_context_anchor_verifier$",
        ):
            ECUTransferContextVerifier().verify(intent)


def test_u64_overflow_amount_rejected_at_conversion_boundary() -> None:
    with pytest.raises(ECUContextVerificationError, match="^amount_micro_ecu_exceeds_u64_max$"):
        _intent_to_micro_ecu(Decimal("18446744073709.551616"))


def test_zero_amount_rejected() -> None:
    _raises_value_token(_intent(amount_ecu=Decimal("0")), "invalid_amount_non_positive")


def test_negative_amount_rejected() -> None:
    _raises_value_token(_intent(amount_ecu=Decimal("-1")), "invalid_amount_non_positive")


def test_unknown_graph_anchor_rejected_by_verifier() -> None:
    verifier = ECUTransferContextVerifier(graph_reader=_GraphReader({}))

    with patch("ilc_core.ecu.ecu_transfer_context_verifier.ECU_FAST_PATH_TRANSFER_ENABLED", True):
        with pytest.raises(ECUContextVerificationError, match="^graph_context_anchor_not_found$"):
            verifier.verify(_intent())


def test_payment_without_anchor_accepted() -> None:
    intent = _intent(transfer_class=TransferClass.PAYMENT, graph_context_anchor=None)
    validate_intent(intent)
    with patch("ilc_core.ecu.ecu_transfer_context_verifier.ECU_FAST_PATH_TRANSFER_ENABLED", True):
        ECUTransferContextVerifier().verify(intent)


def test_payment_express_consent_preserved() -> None:
    intent = _intent(
        transfer_class=TransferClass.PAYMENT,
        graph_context_anchor=None,
        express_consent="USER_CONSENTS_TO_PUBLIC_PAYMENT_LANE",
    )
    validate_intent(intent)
    payload = ECUTransferAdapter(_RecordingBridge())._build_transfer_payload(intent)

    assert intent.express_consent == "USER_CONSENTS_TO_PUBLIC_PAYMENT_LANE"
    assert payload["express_consent"] == "USER_CONSENTS_TO_PUBLIC_PAYMENT_LANE"


def test_activation_guard_blocks_adapter_submit() -> None:
    bridge = _RecordingBridge()
    adapter = ECUTransferAdapter(bridge)

    with pytest.raises(ValueError, match="^transfer_not_enabled_activation_guard_blocks_submit$"):
        adapter.submit(_intent(), b"sender-key")

    assert bridge.payloads == []


def test_per_transfer_cap_enforced() -> None:
    _raises_value_token(
        _intent(amount_ecu=PRE_RC_TRANSFER_CAP_ECU + Decimal("1")),
        "invalid_amount_exceeds_pre_rc_cap",
    )


def test_amount_precision_decimal_not_float() -> None:
    exact_decimal_amount = Decimal("0.1") + Decimal("0.2")

    assert exact_decimal_amount == Decimal("0.3")
    assert 0.1 + 0.2 != 0.3

    intent = _intent(
        amount_ecu=exact_decimal_amount,
        transfer_class=TransferClass.PAYMENT,
        graph_context_anchor=None,
    )
    validate_intent(intent)
    assert isinstance(intent.amount_ecu, Decimal)
    assert not isinstance(intent.amount_ecu, float)
