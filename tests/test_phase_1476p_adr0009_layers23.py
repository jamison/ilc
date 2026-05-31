from dataclasses import FrozenInstanceError, replace

import pytest

from ilc_core.bundle.layer2_epoch_snapshot import (
    ADR_0009_LAYER2_NOT_PUBLIC_DISTRIBUTION,
    generate_layer2_epoch_snapshot,
    verify_layer2_epoch_snapshot,
)
from ilc_core.bundle.layer3_wire_binding import (
    ADR_0009_LAYER3_NOT_PUBLIC_DISTRIBUTION,
    generate_layer3_wire_binding,
    verify_layer3_wire_binding,
)


def _layer2_fixture(epoch_number: int = 2):
    return generate_layer2_epoch_snapshot(
        epoch_number=epoch_number,
        previous_snapshot_sha256="" if epoch_number == 1 else "b" * 64,
        layer0_sha256="a" * 64,
        graph_state_digest="graph:" + "1" * 64,
        agent_state_digest="agent:" + "2" * 64,
        active_contract_digest="contract:" + "3" * 64,
    )


def _layer3_fixture():
    return generate_layer3_wire_binding(
        message_type="claim.submit",
        layer0_schema_ref="layer0:schema:Node",
        sender_agent_id="agent-a",
        epoch_number=2,
        payload_digest="payload:" + "4" * 64,
        signature_ref="signature:fixture-a",
    )


def test_layer2_generate_produces_nonempty_fields() -> None:
    snapshot = _layer2_fixture()

    assert ADR_0009_LAYER2_NOT_PUBLIC_DISTRIBUTION is True
    assert snapshot.epoch_number == 2
    assert snapshot.layer0_protocol_bundle_sha256
    assert snapshot.canonical_json
    assert snapshot.sha256


def test_layer2_verify_accepts_valid_snapshot() -> None:
    assert verify_layer2_epoch_snapshot(_layer2_fixture()) is True


def test_layer2_verify_rejects_tampered_sha256() -> None:
    snapshot = replace(_layer2_fixture(), sha256="c" * 64)

    assert verify_layer2_epoch_snapshot(snapshot) is False


def test_layer2_epoch_regression_rejected() -> None:
    with pytest.raises(ValueError, match="layer2_epoch_snapshot_invalid_epoch_number"):
        _layer2_fixture(epoch_number=0)


def test_layer2_epoch_1_allows_empty_previous_sha256() -> None:
    snapshot = _layer2_fixture(epoch_number=1)

    assert snapshot.previous_snapshot_sha256 == ""
    assert verify_layer2_epoch_snapshot(snapshot) is True


def test_layer2_epoch_2_requires_nonempty_previous_sha256() -> None:
    with pytest.raises(ValueError, match="layer2_epoch_snapshot_missing_previous_sha256"):
        generate_layer2_epoch_snapshot(
            epoch_number=2,
            previous_snapshot_sha256="",
            layer0_sha256="a" * 64,
            graph_state_digest="graph:" + "1" * 64,
            agent_state_digest="agent:" + "2" * 64,
            active_contract_digest="contract:" + "3" * 64,
        )


def test_layer2_immutability_frozen_dataclass() -> None:
    snapshot = _layer2_fixture()

    with pytest.raises(FrozenInstanceError):
        snapshot.epoch_number = 3  # type: ignore[misc]


def test_layer3_generate_produces_nonempty_fields() -> None:
    binding = _layer3_fixture()

    assert ADR_0009_LAYER3_NOT_PUBLIC_DISTRIBUTION is True
    assert binding.message_type == "claim.submit"
    assert binding.layer0_schema_ref == "layer0:schema:Node"
    assert binding.signature_ref == "signature:fixture-a"
    assert binding.canonical_json
    assert binding.sha256


def test_layer3_verify_accepts_valid_binding() -> None:
    assert verify_layer3_wire_binding(_layer3_fixture()) is True


def test_layer3_missing_message_type_raises() -> None:
    with pytest.raises(ValueError, match="layer3_wire_binding_missing_message_type"):
        generate_layer3_wire_binding(
            message_type="",
            layer0_schema_ref="layer0:schema:Node",
            sender_agent_id="agent-a",
            epoch_number=2,
            payload_digest="payload:" + "4" * 64,
            signature_ref="signature:fixture-a",
        )


def test_layer3_immutability_frozen_dataclass() -> None:
    binding = _layer3_fixture()

    with pytest.raises(FrozenInstanceError):
        binding.message_type = "mutated"  # type: ignore[misc]
