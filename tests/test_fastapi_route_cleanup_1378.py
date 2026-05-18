from __future__ import annotations

from pathlib import Path

from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from ilc_core.server import create_app


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "ilc_core/server.py"
PHASE_1301_AUDIT = ROOT / "docs/specs/ilc_deep_no_activation_assertion_audit_1301_v0.1.md"
PHASE_1378_PROMPT = (
    ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1378_g8_legacy_fastapi_route_cleanup.md"
)
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
FORWARD_PLAN = ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1378_legacy_fastapi_route_cleanup_walkthrough.md"

REQUIRED_TOKENS = (
    "legacy_public_labeled_fastapi_routes_cleaned_phase_1378",
    "no_unauthorized_public_labeled_route_exists_phase_1378",
)

FLAGGED_ROUTE_REQUESTS = (
    ("POST", "/v1/public/init/admission"),
    ("POST", "/v1/public/receipt"),
    ("GET", "/v1/public/receipt/example-receipt"),
    ("GET", "/v1/public/receipts"),
    ("GET", "/v1/public/lifecycle/coupling-invariants"),
    ("GET", "/v1/public/lifecycle/agent-alpha"),
    ("GET", "/v1/public/wallet/agent-alpha/status"),
    ("GET", "/v1/public/wallet/agent-alpha/history"),
    ("GET", "/v1/public/wallet/agent-alpha/export"),
    ("GET", "/v1/public/wallet/agent-alpha/ledger-summary"),
)

FLAGGED_ROUTE_DECORATORS = (
    '@router.post("/v1/public/init/admission")',
    '@router.post("/v1/public/receipt")',
    '@router.get("/v1/public/receipt/{receipt_id}")',
    '@router.get("/v1/public/receipts")',
    '@router.get("/v1/public/lifecycle/coupling-invariants")',
    '@router.get("/v1/public/lifecycle/{agent_id}")',
    '@router.get("/v1/public/wallet/{agent_id}/status")',
    '@router.get("/v1/public/wallet/{agent_id}/history")',
    '@router.get("/v1/public/wallet/{agent_id}/export")',
    '@router.get("/v1/public/wallet/{agent_id}/ledger-summary")',
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def route_paths() -> set[str]:
    return {
        route.path
        for route in create_app().routes
        if isinstance(route, APIRoute)
    }


def test_phase_1301_carry_forward_and_phase_1378_prompt_are_present() -> None:
    audit = read(PHASE_1301_AUDIT)
    prompt = read(PHASE_1378_PROMPT)

    assert "legacy_public_labeled_fastapi_routes_carry_forward_phase_1301" in audit
    assert "legacy_public_labeled_fastapi_routes_not_public_rc_clean_phase_1301" in audit
    for token in REQUIRED_TOKENS:
        assert token in prompt


def test_no_v1_public_routes_are_registered_on_default_fastapi_app() -> None:
    registered_public_routes = sorted(path for path in route_paths() if path.startswith("/v1/public/"))

    assert registered_public_routes == []


def test_flagged_phase_1301_routes_no_longer_return_200() -> None:
    with TestClient(create_app()) as client:
        for method, path in FLAGGED_ROUTE_REQUESTS:
            response = client.request(method, path, json={})
            assert response.status_code != 200, (method, path, response.text)
            assert response.status_code == 404, (method, path, response.text)


def test_server_source_no_longer_contains_flagged_public_route_decorators() -> None:
    server = read(SERVER)

    for decorator in FLAGGED_ROUTE_DECORATORS:
        assert decorator not in server


def test_protocol_routes_remain_registered_and_functional() -> None:
    paths = route_paths()

    assert "/v1/protocol/schema" in paths
    assert "/v1/protocol/claim" in paths
    with TestClient(create_app()) as client:
        schema_response = client.get("/v1/protocol/schema")
        claim_response = client.post(
            "/v1/protocol/claim",
            json={
                "agent_id": "agent:phase1378",
                "content": "legacy public route cleanup preserves protocol routes",
                "net_stake": "0",
            },
        )
    assert schema_response.status_code == 200
    assert claim_response.status_code == 200
    assert claim_response.json()["claim"]["agent_id"] == "agent:phase1378"


def test_frontier_docs_record_phase_1378_cleanup_without_activation() -> None:
    combined = "\n".join(
        read(path)
        for path in (
            STATUS,
            PLANNING_INDEX,
            FORWARD_PLAN,
            WALKTHROUGH,
        )
    )

    for token in REQUIRED_TOKENS:
        assert token in combined
    assert "claim endpoint activation" in combined
    assert "no public claimability activation" in combined
    assert "Phase 1379" in combined
