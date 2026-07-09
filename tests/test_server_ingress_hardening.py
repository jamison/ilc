from __future__ import annotations

from fastapi.testclient import TestClient

from ilc_core import server
from ilc_core.server import create_app
from ilc_core.types import Node


def _client() -> TestClient:
    return TestClient(create_app())


def _gossip_payload(content: str = "phase_1573ak_gossip") -> dict[str, object]:
    node = Node(
        id="placeholder",
        type="claim",
        content=content,
        agent_id="agent:phase1573ak",
        signature="sig:phase1573ak",
    )
    node.id = node.compute_canonical_id()
    return node.model_dump(mode="json")


def test_route_classification_covers_all_user_routes() -> None:
    app = create_app()
    actual = {
        (method, route.path)
        for route in app.routes
        for method in getattr(route, "methods", set())
        if route.path not in {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}
        and method not in {"HEAD", "OPTIONS"}
    }
    assert actual == set(server._route_classification_coverage())


def test_gossip_rejects_oversized_body() -> None:
    with _client() as client:
        response = client.post(
            "/gossip/receive",
            content=b"{" + (b'"x":' + b'"' + (b"a" * server.MAX_GOSSIP_PAYLOAD_BYTES) + b'"}'),
            headers={"content-type": "application/json"},
        )
    assert response.status_code == 413
    assert response.json()["detail"] == "gossip_payload_too_large_phase_1573ak"


def test_gossip_rejects_invalid_json() -> None:
    with _client() as client:
        response = client.post(
            "/gossip/receive",
            content=b"{not-json",
            headers={"content-type": "application/json"},
        )
    assert response.status_code == 400
    assert response.json()["detail"] == "gossip_json_invalid_phase_1573ak"


def test_gossip_rejects_non_object_json() -> None:
    with _client() as client:
        response = client.post(
            "/gossip/receive",
            content=b'["not", "an", "object"]',
            headers={"content-type": "application/json"},
        )
    assert response.status_code == 400
    assert response.json()["detail"] == "gossip_payload_not_object_phase_1573ak"


def test_gossip_rejects_missing_signature() -> None:
    payload = _gossip_payload("phase_1573ak_missing_signature")
    payload.pop("signature")
    with _client() as client:
        response = client.post("/gossip/receive", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid Gossip"


def test_peer_add_rejects_loopback_without_local_dev_override() -> None:
    with _client() as client:
        response = client.post("/peers/add?host=127.0.0.1&port=9001")
    assert response.status_code == 400
    assert response.json()["detail"] == "peer_endpoint_private_address_forbidden_phase_1332_fix4"


def test_peer_add_rejects_metadata_link_local_host() -> None:
    with _client() as client:
        response = client.post("/peers/add?host=169.254.169.254&port=9001")
    assert response.status_code == 400
    assert response.json()["detail"] == "peer_endpoint_private_address_forbidden_phase_1332_fix4"


def test_peer_add_allows_loopback_with_local_dev_override(monkeypatch) -> None:
    monkeypatch.setenv("ILC_LOCAL_DEV_PEER_ADMIN", "1")
    with _client() as client:
        response = client.post("/peers/add?host=127.0.0.1&port=9001")
    assert response.status_code == 200
    assert response.json()["status"] == "added"


def test_app_level_body_cap_rejects_declared_oversized_request() -> None:
    with _client() as client:
        response = client.post(
            "/v1/protocol/claim",
            content=b"{" + (b'"x":"' + b"a" * server.MAX_APP_REQUEST_BODY_BYTES + b'"}'),
            headers={"content-type": "application/json"},
        )
    assert response.status_code == 413
    assert response.json()["detail"] == "request_body_too_large_phase_1573ak"
