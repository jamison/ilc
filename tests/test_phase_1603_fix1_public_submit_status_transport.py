from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ilc_core.cli import d2e_submit_cli
from ilc_core.cli.ecu_status_cli import normalize_ecu_status_payload
from ilc_core.encoding.cidv1 import node_id_from_obj, parse_nodeid_strict
from ilc_core.server import (
    PUBLIC_TRUTH_SUBMIT_GRAPH_STORE_ENV,
    PUBLIC_TRUTH_SUBMIT_STORE_MISSING_TOKEN,
    create_app,
)
from ilc_core.storage.truth_primitive_graph_lmdb_adapter import TruthPrimitiveGraphStore


VALID_AGENT_ID = "c" * 96


def _assert_truth_payload() -> dict[str, object]:
    return {
        "content": {"claim": "Phase 1603 transport smoke"},
        "epistemic_type": "objective",
        "parent_node_ids": [],
        "primitive_type": "observation",
    }


def _submit_namespace(endpoint: str = "") -> argparse.Namespace:
    return argparse.Namespace(
        primitive="assert.truth",
        agent_id=VALID_AGENT_ID,
        epoch=1,
        payload_json=json.dumps(_assert_truth_payload()),
        payload_file=None,
        sig="UNSIGNED",
        signing_key=None,
        source_refs=[],
        endpoint=endpoint,
    )


def test_public_truth_submit_route_persists_cdl075_node(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store_path = tmp_path / "truth_graph.lmdb"
    monkeypatch.setenv(PUBLIC_TRUTH_SUBMIT_GRAPH_STORE_ENV, str(store_path))

    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/truth/submit",
            json={
                "v": 1,
                "primitive": "assert.truth",
                "agent_id": VALID_AGENT_ID,
                "epoch": 1,
                "payload": _assert_truth_payload(),
                "sig": "UNSIGNED",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    data = body["data"]
    node_id = data["node_id"]
    parse_nodeid_strict(node_id)
    assert data["graph_persistence"] == "persisted"
    assert data["nodes_written"] == 1
    assert data["non_claims"] == [
        "no_ecu_mint",
        "no_ilc_mint",
        "no_wallet_write",
        "no_epoch_transition",
        "no_settlement_commit",
    ]

    store = TruthPrimitiveGraphStore(store_path)
    try:
        record = store.get_node(node_id)
    finally:
        store.close()
    assert record is not None
    assert record["agent_id"] == VALID_AGENT_ID
    assert record["payload"]["primitive_type"] == "observation"


def test_public_truth_submit_route_fails_closed_without_configured_store() -> None:
    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/truth/submit",
            json={
                "v": 1,
                "primitive": "assert.truth",
                "agent_id": VALID_AGENT_ID,
                "epoch": 1,
                "payload": _assert_truth_payload(),
                "sig": "UNSIGNED",
            },
        )

    assert response.status_code == 503
    assert response.json()["detail"] == PUBLIC_TRUTH_SUBMIT_STORE_MISSING_TOKEN


def test_submit_cli_posts_to_public_endpoint_and_requires_cidv1_node(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    node_id = node_id_from_obj({"phase": "1603-fix1", "kind": "submit-endpoint"})
    seen: dict[str, object] = {}

    class Response:
        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def __init__(self) -> None:
            self._sent = False

        def read(self, _limit: int) -> bytes:
            if self._sent:
                return b""
            self._sent = True
            return json.dumps(
                {
                    "ok": True,
                    "data": {
                        "node_id": node_id,
                        "edges": [],
                        "graph_persistence": "persisted",
                        "gossip_delivery": "deferred",
                    },
                }
            ).encode("utf-8")

    def fake_open(request: object, *, timeout: float) -> Response:
        seen["url"] = request.full_url
        seen["timeout"] = timeout
        seen["body"] = json.loads(request.data.decode("utf-8"))
        return Response()

    monkeypatch.setattr(d2e_submit_cli, "_open_submit_request", fake_open)

    result = d2e_submit_cli.handle_submit(
        _submit_namespace("https://validator.example/api/v1/truth/submit")
    )

    assert seen["url"] == "https://validator.example/api/v1/truth/submit"
    assert seen["body"]["payload"]["primitive_type"] == "observation"
    assert result["node_id"] == node_id
    assert result["graph_persistence"] == "persisted"
    assert result["public_submit_endpoint"] == "https://validator.example/api/v1/truth/submit"


def test_submit_cli_rejects_unsafe_endpoint() -> None:
    with pytest.raises(d2e_submit_cli.SubmitCommandError) as exc_info:
        d2e_submit_cli.handle_submit(_submit_namespace("http://validator.example/api/v1/truth/submit"))

    assert exc_info.value.token == "submit_endpoint_https_required"


def test_public_ecu_status_route_is_reachable_and_explicitly_quote_zero() -> None:
    with TestClient(create_app()) as client:
        response = client.get(
            "/api/v1/ecu/status",
            params={"agent_id": VALID_AGENT_ID},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["agent_id"] == VALID_AGENT_ID
    assert payload["pending_attribution_quote"] == "0"
    assert (
        payload["pending_attribution_quote_source"]
        == "public_status_transport_no_attribution_worker_consumed_events"
    )
    assert payload["committed_ecu_balance"] == "0"
    assert payload["balance_ecu_source"] == "public_wallet_runtime_ecu_accrual"
    assert (
        payload["pressure_model_boundary"]
        == "inverted_ecu_pressure_read_model_not_spendable_balance"
    )
    assert payload["status"] == "reachable_no_pending_attribution_events"
    assert "no_spendable_balance_claim" in payload["non_claims"]
    assert "no_inverted_ecu_spend_to_keep_activation" in payload["non_claims"]
    normalized = normalize_ecu_status_payload(
        payload,
        agent_id=VALID_AGENT_ID,
        endpoint="https://validator.example/api/v1/ecu/status",
    )
    assert normalized["pending_attribution_quote"] == "0"
    assert normalized["committed_ecu_balance"] == "0"
