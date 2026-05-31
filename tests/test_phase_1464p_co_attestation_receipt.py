import pytest

from ilc_core.harness.co_attestation_receipt import (
    build_co_attestation_receipt,
    verify_co_attestation_receipt,
)


def test_co_attestation_receipt_is_deterministic_and_verifiable() -> None:
    receipt_a = build_co_attestation_receipt(
        receipt_id="receipt-1",
        artifact_sha256="a" * 64,
        attestation_signatures=[
            {"agent_id": "agent-b", "signature": "sig-b"},
            {"agent_id": "agent-a", "signature": "sig-a"},
        ],
    )
    receipt_b = build_co_attestation_receipt(
        receipt_id="receipt-1",
        artifact_sha256="a" * 64,
        attestation_signatures=[
            {"agent_id": "agent-a", "signature": "sig-a"},
            {"agent_id": "agent-b", "signature": "sig-b"},
        ],
    )

    assert receipt_a.receipt_sha256 == receipt_b.receipt_sha256
    assert receipt_a.attestation_signatures[0]["agent_id"] == "agent-a"
    assert verify_co_attestation_receipt(receipt_a) is True

    with pytest.raises(TypeError):
        receipt_a.attestation_signatures[0]["agent_id"] = "mutated"  # type: ignore[index]
