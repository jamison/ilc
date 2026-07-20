from __future__ import annotations

from decimal import Decimal

from fastapi.testclient import TestClient

from ilc_core.server import create_app
from ilc_core.types import Node


def _build_gossip_payload(content: str) -> dict:
    node = Node(
        id="placeholder",
        type="claim",
        content=content,
        agent_id="agent:isolation:test",
        signature="sig:isolation:test",
        net_stake=Decimal("1.0"),
    )
    node.id = node.compute_id()
    return node.model_dump(mode="json")


def test_phase_199_graph_state_isolation_between_app_instances() -> None:
    app_a = create_app()
    app_b = create_app()

    client_a = TestClient(app_a)
    client_b = TestClient(app_b)

    client_a.get("/")
    client_b.get("/")

    payload = _build_gossip_payload("phase_199_graph_state_isolation")
    response = client_a.post("/gossip/receive", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid Gossip"

    assert payload["id"] not in app_a.state.graph.nodes
    assert payload["id"] not in app_b.state.graph.nodes


def test_phase_199_peer_manager_state_isolation_between_app_instances() -> None:
    app_a = create_app()
    app_b = create_app()

    client_a = TestClient(app_a)
    client_b = TestClient(app_b)

    client_a.get("/")
    client_b.get("/")

    client_a.post("/peers/add?host=phase-199-a.ilc.example&port=9001")
    client_a.post("/peers/add?host=phase-199-b.ilc.example&port=9002")

    assert len(app_a.state.peer_manager.peers) == 2
    assert len(app_b.state.peer_manager.peers) == 0
