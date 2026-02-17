from __future__ import annotations

from fastapi.testclient import TestClient

from ilc_core.server import create_app
from ilc_core.types import Node


def _make_node(content: str = "bridge-test") -> Node:
    return Node(
        id="",
        type="claim",
        content=content,
        agent_id="agent:bridge",
        signature="sig",
    )


def test_gossip_rejects_legacy_node_id() -> None:
    app = create_app()
    client = TestClient(app)

    node = _make_node("legacy")
    node.id = node.compute_legacy_id()

    resp = client.post("/gossip/receive", json=node.model_dump(mode="json"))
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Invalid Gossip"


def test_gossip_accepts_canonical_node_id() -> None:
    app = create_app()
    client = TestClient(app)

    node = _make_node("canonical")
    node.id = node.compute_canonical_id()

    resp = client.post("/gossip/receive", json=node.model_dump(mode="json"))
    assert resp.status_code == 200
    assert resp.json()["status"] == "accepted"


def test_gossip_rejects_mismatched_node_id() -> None:
    app = create_app()
    client = TestClient(app)

    node = _make_node("mismatch")
    node.id = "bad-node-id"

    resp = client.post("/gossip/receive", json=node.model_dump(mode="json"))
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Invalid Gossip"
