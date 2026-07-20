from __future__ import annotations

import logging
from decimal import Decimal

from fastapi.testclient import TestClient

from ilc_core.asgi import app
from ilc_core.types import Node


client = TestClient(app)


def _build_valid_payload(content: str) -> dict:
    node = Node(
        id="placeholder",
        type="claim",
        content=content,
        agent_id="agent:gossip:contract",
        signature="sig:gossip:contract",
        net_stake=Decimal("1.0"),
    )
    node.id = node.compute_id()
    return node.model_dump(mode="json")


def test_gossip_id_mismatch_maps_to_rejected_token(
    caplog,
) -> None:
    payload = _build_valid_payload("gossip_contract_mismatch")
    payload["id"] = "invalid_hash"

    caplog.set_level(logging.WARNING)
    response = client.post("/gossip/receive", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid Gossip"
    assert any(
        "gossip_receive_rejected" in record.getMessage()
        and "gossip_node_id_mismatch" in record.getMessage()
        for record in caplog.records
    )


def test_gossip_missing_signature_maps_to_rejected_token(
    caplog,
) -> None:
    payload = _build_valid_payload("gossip_contract_signature_missing")
    payload["signature"] = ""

    caplog.set_level(logging.WARNING)
    response = client.post("/gossip/receive", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid Gossip"
    assert any(
        "gossip_receive_rejected" in record.getMessage()
        and "gossip_signature_missing" in record.getMessage()
        for record in caplog.records
    )


def test_gossip_unverified_signature_maps_to_not_wired_token(
    caplog,
) -> None:
    payload = _build_valid_payload("gossip_contract_signature_not_wired")

    caplog.set_level(logging.WARNING)
    response = client.post("/gossip/receive", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid Gossip"
    assert any(
        "gossip_receive_rejected" in record.getMessage()
        and "gossip_signature_verification_not_wired_phase_1575h_fix1" in record.getMessage()
        for record in caplog.records
    )
