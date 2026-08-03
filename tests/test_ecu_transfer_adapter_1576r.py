# SPDX-License-Identifier: AGPL-3.0-only
import inspect
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from ilc_core.ecu.ecu_fast_path_intent import ECUFastPathIntent, TransferClass
from ilc_core.ecu.ecu_transfer_adapter import (
    ECU_TRANSFER_ADAPTER_VERSION,
    ECUTransferAdapter,
    validate_rust_transfer_payload,
)
from ilc_core.ecu.ecu_transfer_context_verifier import ECUContextVerificationError


class _Bridge:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls
        self.bridge_payloads: list[dict[str, object]] = []
        self.rust_payloads: list[dict[str, object]] = []

    def build_ecu_transfer(
        self,
        payload: dict[str, object],
    ) -> dict[str, object]:
        self.calls.append("builder")
        self.bridge_payloads.append(payload)
        rust_payload = _rust_payload()
        self.rust_payloads.append(rust_payload)
        return rust_payload

    def submit(self, payload: dict[str, object]) -> str:
        self.calls.append("bridge")
        assert payload == self.rust_payloads[-1]
        return "transfer-ref-001"


class _Verifier:
    def __init__(self, calls: list[str], *, fail: bool = False) -> None:
        self.calls = calls
        self.fail = fail

    def verify(self, intent: ECUFastPathIntent) -> None:
        self.calls.append("verifier")
        if self.fail:
            raise ECUContextVerificationError("verifier_failed_for_test")


class _BuildOnlyBridge:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def build_ecu_transfer(
        self,
        payload: dict[str, object],
    ) -> dict[str, object]:
        self.calls.append("builder")
        assert payload["bridge_payload_version"] == ECU_TRANSFER_ADAPTER_VERSION
        return _rust_payload()


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


def _rust_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "object_ref": {"agent": "agent_sender", "version": 0},
        "to": "agent_recipient",
        "amount_micro_ecu": 1_500_000,
        "transfer_class": "Contribution",
        "sender_sig": "b" * 192,
    }
    payload.update(overrides)
    return payload


def test_adapter_calls_verifier_before_bridge() -> None:
    calls: list[str] = []
    adapter = ECUTransferAdapter(_Bridge(calls), verifier=_Verifier(calls))

    with patch("ilc_core.ecu.ecu_transfer_adapter.ECU_FAST_PATH_TRANSFER_ENABLED", True):
        assert adapter.submit(_intent()) == "transfer-ref-001"

    assert calls == ["verifier", "builder", "bridge"]


def test_activation_guard_blocks_submission_before_verifier_or_bridge() -> None:
    calls: list[str] = []
    bridge = _Bridge(calls)
    verifier = _Verifier(calls)
    adapter = ECUTransferAdapter(bridge, verifier=verifier)

    with pytest.raises(ValueError, match="^transfer_not_enabled_activation_guard_blocks_submit$"):
        adapter.submit(_intent())

    assert calls == []
    assert bridge.bridge_payloads == []


def test_payload_conversion_produces_correct_micro_ecu() -> None:
    payload = ECUTransferAdapter(_Bridge([]))._build_transfer_payload(_intent())

    assert payload["amount_micro_ecu"] == 1_500_000
    assert isinstance(payload["amount_micro_ecu"], int)


def test_contribution_class_maps_to_correct_wire_tag() -> None:
    payload = ECUTransferAdapter(_Bridge([]))._build_transfer_payload(_intent())

    assert payload["transfer_class"] == {"type": "Contribution"}
    assert payload["express_consent"] is None


def test_payment_class_maps_to_correct_wire_tag() -> None:
    payload = ECUTransferAdapter(_Bridge([]))._build_transfer_payload(
        _intent(
            transfer_class=TransferClass.PAYMENT,
            graph_context_anchor=None,
            express_consent="express-consent:test",
        )
    )

    assert payload["transfer_class"] == {
        "type": "Payment",
        "express": {
            "agent_acknowledged_timing_disclosure": True,
            "consent_epoch": 0,
        },
    }
    assert payload["express_consent"] == "express-consent:test"


def test_verifier_failure_prevents_bridge_call() -> None:
    calls: list[str] = []
    bridge = _Bridge(calls)
    adapter = ECUTransferAdapter(bridge, verifier=_Verifier(calls, fail=True))

    with patch("ilc_core.ecu.ecu_transfer_adapter.ECU_FAST_PATH_TRANSFER_ENABLED", True):
        with pytest.raises(ECUContextVerificationError, match="^verifier_failed_for_test$"):
            adapter.submit(_intent())

    assert calls == ["verifier"]
    assert bridge.bridge_payloads == []


def test_missing_bridge_builder_fails_after_verifier() -> None:
    calls: list[str] = []
    adapter = ECUTransferAdapter(object(), verifier=_Verifier(calls))

    with patch("ilc_core.ecu.ecu_transfer_adapter.ECU_FAST_PATH_TRANSFER_ENABLED", True):
        with pytest.raises(ValueError, match="^consensus_bridge_missing_build_ecu_transfer$"):
            adapter.submit(_intent())

    assert calls == ["verifier"]


def test_bridge_object_result_transfer_reference_is_accepted() -> None:
    bridge = Mock()
    bridge.build_ecu_transfer.return_value = _rust_payload()
    bridge.submit.return_value = SimpleNamespace(transfer_reference="transfer-ref-obj")
    adapter = ECUTransferAdapter(bridge, verifier=_Verifier([]))

    with patch("ilc_core.ecu.ecu_transfer_adapter.ECU_FAST_PATH_TRANSFER_ENABLED", True):
        assert adapter.submit(_intent()) == "transfer-ref-obj"


def test_bridge_object_result_proposal_id_is_accepted() -> None:
    bridge = Mock()
    bridge.build_ecu_transfer.return_value = _rust_payload()
    bridge.submit.return_value = SimpleNamespace(proposal_id="proposal-ref-obj")
    adapter = ECUTransferAdapter(bridge, verifier=_Verifier([]))

    with patch("ilc_core.ecu.ecu_transfer_adapter.ECU_FAST_PATH_TRANSFER_ENABLED", True):
        assert adapter.submit(_intent()) == "proposal-ref-obj"


@pytest.mark.parametrize("bridge_result", [None, ""])
def test_bridge_empty_result_fails_closed(bridge_result: object) -> None:
    bridge = Mock()
    bridge.build_ecu_transfer.return_value = _rust_payload()
    bridge.submit.return_value = bridge_result
    adapter = ECUTransferAdapter(bridge, verifier=_Verifier([]))

    with patch("ilc_core.ecu.ecu_transfer_adapter.ECU_FAST_PATH_TRANSFER_ENABLED", True):
        with pytest.raises(ValueError, match="^consensus_bridge_submit_reference_invalid$"):
            adapter.submit(_intent())


def test_no_key_material_parameter_on_submit() -> None:
    sig = inspect.signature(ECUTransferAdapter.submit)

    assert "sender_key_material" not in sig.parameters


def test_bridge_build_call_passes_no_key_material() -> None:
    received_kwargs: list[dict[str, object]] = []

    class _CapturingBridge:
        def build_ecu_transfer(
            self,
            payload: dict[str, object],
            **kwargs: object,
        ) -> dict[str, object]:
            received_kwargs.append(kwargs)
            return _rust_payload()

        def submit(self, payload: dict[str, object]) -> str:
            return "transfer-ref-001"

    adapter = ECUTransferAdapter(_CapturingBridge(), verifier=_Verifier([]))
    with patch("ilc_core.ecu.ecu_transfer_adapter.ECU_FAST_PATH_TRANSFER_ENABLED", True):
        assert adapter.submit(_intent()) == "transfer-ref-001"

    assert received_kwargs == [{}]


def test_missing_bridge_submit_fails_after_rust_payload_build() -> None:
    calls: list[str] = []
    bridge = _BuildOnlyBridge(calls)
    adapter = ECUTransferAdapter(bridge, verifier=_Verifier(calls))

    with patch("ilc_core.ecu.ecu_transfer_adapter.ECU_FAST_PATH_TRANSFER_ENABLED", True):
        with pytest.raises(ValueError, match="^consensus_bridge_missing_submit$"):
            adapter.submit(_intent())

    assert calls == ["verifier", "builder"]


def test_rust_payload_field_set_is_exact() -> None:
    intent = _intent()
    validate_rust_transfer_payload(_rust_payload(), intent)

    bad_payload = _rust_payload(nonce=intent.nonce)
    with pytest.raises(ValueError, match="^rust_ecu_transfer_payload_field_set_invalid$"):
        validate_rust_transfer_payload(bad_payload, intent)


def test_rust_payload_object_ref_must_match_sender() -> None:
    intent = _intent()
    bad_payload = _rust_payload(object_ref={"agent": "agent_other", "version": 0})

    with pytest.raises(ValueError, match="^rust_ecu_transfer_object_ref_agent_mismatch$"):
        validate_rust_transfer_payload(bad_payload, intent)


def test_rust_payload_sender_sig_required() -> None:
    intent = _intent()
    bad_payload = _rust_payload(sender_sig="")

    with pytest.raises(ValueError, match="^rust_ecu_transfer_sender_sig_invalid$"):
        validate_rust_transfer_payload(bad_payload, intent)


def test_rust_payload_transfer_class_uses_rust_serde_shape() -> None:
    default_payment_intent = _intent(
        transfer_class=TransferClass.PAYMENT,
        graph_context_anchor=None,
    )
    validate_rust_transfer_payload(
        _rust_payload(transfer_class={"Payment": {"express": None}}),
        default_payment_intent,
    )

    payment_intent = _intent(
        transfer_class=TransferClass.PAYMENT,
        graph_context_anchor=None,
        express_consent="express-consent:test",
    )
    validate_rust_transfer_payload(
        _rust_payload(
            transfer_class={
                "Payment": {
                    "express": {
                        "agent_acknowledged_timing_disclosure": True,
                        "consent_epoch": 0,
                    }
                }
            }
        ),
        payment_intent,
    )

    bad_payload = _rust_payload(
        transfer_class={
            "type": "Payment",
            "express": {
                "agent_acknowledged_timing_disclosure": True,
                "consent_epoch": 0,
            },
        }
    )
    with pytest.raises(ValueError, match="^rust_ecu_transfer_class_mismatch$"):
        validate_rust_transfer_payload(bad_payload, payment_intent)


def test_bridge_payload_is_intermediate_not_rust_struct() -> None:
    payload = ECUTransferAdapter(_Bridge([]))._build_transfer_payload(_intent())

    assert set(payload) == {
        "amount_micro_ecu",
        "bridge_payload_version",
        "express_consent",
        "graph_context_anchor",
        "nonce",
        "sender_agent_id",
        "to",
        "transfer_class",
    }
    assert {"object_ref", "sender_sig"}.isdisjoint(payload)


def test_adapter_version_constant_accessible() -> None:
    assert ECU_TRANSFER_ADAPTER_VERSION == "ecu_transfer_adapter_03.v0.1"
