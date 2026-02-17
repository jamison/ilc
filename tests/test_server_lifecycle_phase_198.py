from __future__ import annotations

from fastapi.testclient import TestClient

from ilc_core.asgi import app
from ilc_core.server import create_app


def test_phase_198_create_app_returns_distinct_instances() -> None:
    app_a = create_app()
    app_b = create_app()
    assert app_a is not app_b


def test_phase_198_create_app_initializes_runtime_state_per_instance() -> None:
    local_app = create_app()
    client = TestClient(local_app)

    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

    assert hasattr(local_app.state, "graph")
    assert hasattr(local_app.state, "consensus")
    assert hasattr(local_app.state, "agent")
    assert hasattr(local_app.state, "peer_manager")


def test_phase_198_module_level_app_remains_routable() -> None:
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
