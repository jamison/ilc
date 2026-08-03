# SPDX-License-Identifier: AGPL-3.0-only
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from ilc_core.ecu.ecu_fast_path_intent import ECUFastPathIntent, TransferClass
from ilc_core.ecu.ecu_transfer_adapter import (
    ECU_TRANSFER_ADAPTER_VERSION,
    ECUTransferAdapter,
)
from ilc_core.ecu.ecu_transfer_context_verifier import ECUContextVerificationError


class _Bridge:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls
        self.payloads: list[dict[str, object]] = []

    def submit(self, payload: dict[str, object], *, sender_key_material: object) -> str:
        self.calls.append("bridge")
        self.payloads.append(payload)
        assert sender_key_material == b"sender-key"
        return "transfer-ref-001"


class _Verifier:
    def __init__(self, calls: list[str], *, fail: bool = False) -> None:
        self.calls = calls
        self.fail = fail

    def verify(self, intent: ECUFastPathIntent) -> None:
        self.calls.append("verifier")
        if self.fail:
            raise ECUContextVerificationError("verifier_failed_for_test")


def _intent(**overrides: object) -> ECUFastPathIntent:
    fields = {
        "sender_agent_id": "agent_sender",
        "recipient_agent_id": "agent_recipient",
        "amount_ecu": Decimal("1.5"),
        "transfer_class": TransferClass.CONTRIBUTION,
        "graph_context_anchor": "node:artifact:abc123",
        "express_consent": None,
        "nonce": "550e8400-e29b-41d4-a716-446655440000",
        "created_epoch": 0,
    }
    fields.update(overrides)
    return ECUFastPathIntent(**fields)


def test_adapter_calls_verifier_before_bridge() -> None:
    calls: list[str] = []
    adapter = ECUTransferAdapter(_Bridge(calls), verifier=_Verifier(calls))

    with patch("ilc_core.ecu.ecu_transfer_adapter.ECU_FAST_PATH_TRANSFER_ENABLED", True):
        assert adapter.submit(_intent(), b"sender-key") == "transfer-ref-001"

    assert calls == ["verifier", "bridge"]


def test_activation_guard_blocks_submission_before_verifier_or_bridge() -> None:
    calls: list[str] = []
    bridge = _Bridge(calls)
    verifier = _Verifier(calls)
    adapter = ECUTransferAdapter(bridge, verifier=verifier)

    with pytest.raises(ValueError, match="^transfer_not_enabled_activation_guard_blocks_submit$"):
        adapter.submit(_intent(), b"sender-key")

    assert calls == []
    assert bridge.payloads == []


def test_payload_conversion_produces_correct_micro_ecu() -> None:
    payload = ECUTransferAdapter(_Bridge([]))._build_transfer_payload(_intent())

    assert payload["amount_micro_ecu"] == 1_500_000
    assert isinstance(payload["amount_micro_ecu"], int)


def test_contribution_class_maps_to_correct_wire_tag() -> None:
    payload = ECUTransferAdapter(_Bridge([]))._build_transfer_payload(_intent())

    assert payload["transfer_class"] == "Contribution"


def test_payment_class_maps_to_correct_wire_tag() -> None:
    payload = ECUTransferAdapter(_Bridge([]))._build_transfer_payload(
        _intent(
            transfer_class=TransferClass.PAYMENT,
            graph_context_anchor=None,
            express_consent="express-consent:test",
        )
    )

    assert payload["transfer_class"] == "Payment"
    assert payload["express_consent"] == "express-consent:test"


def test_verifier_failure_prevents_bridge_call() -> None:
    calls: list[str] = []
    bridge = _Bridge(calls)
    adapter = ECUTransferAdapter(bridge, verifier=_Verifier(calls, fail=True))

    with patch("ilc_core.ecu.ecu_transfer_adapter.ECU_FAST_PATH_TRANSFER_ENABLED", True):
        with pytest.raises(ECUContextVerificationError, match="^verifier_failed_for_test$"):
            adapter.submit(_intent(), b"sender-key")

    assert calls == ["verifier"]
    assert bridge.payloads == []


def test_missing_bridge_submit_fails_after_verifier() -> None:
    calls: list[str] = []
    adapter = ECUTransferAdapter(object(), verifier=_Verifier(calls))

    with patch("ilc_core.ecu.ecu_transfer_adapter.ECU_FAST_PATH_TRANSFER_ENABLED", True):
        with pytest.raises(ValueError, match="^consensus_bridge_missing_submit$"):
            adapter.submit(_intent(), b"sender-key")

    assert calls == ["verifier"]


def test_bridge_object_result_transfer_reference_is_accepted() -> None:
    bridge = Mock()
    bridge.submit.return_value = SimpleNamespace(transfer_reference="transfer-ref-obj")
    adapter = ECUTransferAdapter(bridge, verifier=_Verifier([]))

    with patch("ilc_core.ecu.ecu_transfer_adapter.ECU_FAST_PATH_TRANSFER_ENABLED", True):
        assert adapter.submit(_intent(), b"sender-key") == "transfer-ref-obj"


def test_adapter_version_constant_accessible() -> None:
    assert ECU_TRANSFER_ADAPTER_VERSION == "ecu_transfer_adapter_03.v0.1"
