from __future__ import annotations

from copy import deepcopy
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ilc_core.network.d2d.http_fetch_transport_runtime import (
    FetchTransportConfig,
    HttpFetchTransportRuntime,
)
from ilc_core.network.d2d import http_fetch_transport_runtime as fetch_runtime_module
from ilc_core.release import upgrade_check
from ilc_core.release.constants import (
    MAX_UPGRADE_ASSERTION_BYTES,
    UPGRADE_CHECK_D2D_HOP_COUNT_HEADER,
    UPGRADE_CHECK_D2D_HOP_COUNT_VALUE,
)
from ilc_core.storage.truth_primitive_graph_lmdb_adapter import TruthPrimitiveGraphStore


FIXTURE_PATH = Path(
    "docs/specs/"
    "ilc_core_0434_release_assertion_GAP_RC_NATIVE_DISTRIBUTION_VNEXT_SIGN_PUBLISH_00_v0.1.json"
)
LATEST_PATH = "/.well-known/ilc/software-release/latest.json"


class _StubStore:
    def __init__(self, payload: dict[str, Any] | None, *, fail: bool = False) -> None:
        self.payload = payload
        self.fail = fail
        self.channels: list[str] = []

    def get_latest_release_assertion(self, channel: str) -> dict[str, Any] | None:
        if self.fail:
            raise RuntimeError("store unavailable")
        self.channels.append(channel)
        return self.payload

    def close(self) -> None:
        return None


def _release_assertion() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _release_assertion_with(**node_updates: Any) -> dict[str, Any]:
    payload = deepcopy(_release_assertion())
    payload["software_release_node"].update(node_updates)
    return payload


def _request_json(port: int, path: str = LATEST_PATH) -> tuple[int, dict[str, Any]]:
    request = urllib.request.Request(f"http://127.0.0.1:{port}{path}", method="GET")
    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            return int(response.status), json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return int(exc.code), json.loads(exc.read().decode("utf-8"))


def _with_runtime(store: _StubStore):
    runtime = HttpFetchTransportRuntime(FetchTransportConfig(bind_host="127.0.0.1", bind_port=0))
    runtime._open_store = lambda: store  # type: ignore[method-assign]
    runtime.start()
    return runtime


def test_release_endpoint_serves_valid_full_signed_assertion() -> None:
    store = _StubStore(_release_assertion())
    runtime = _with_runtime(store)
    try:
        status, payload = _request_json(runtime.state["bound_port"])
    finally:
        runtime.stop()

    assert status == 200
    result = upgrade_check.validate_release_assertion(payload)
    assert result["release_signature_verified"] is True
    assert result["verified_attestation_count"] == 3
    assert store.channels == ["public_rc"]


def test_release_endpoint_payload_includes_full_attestation_edges() -> None:
    runtime = _with_runtime(_StubStore(_release_assertion()))
    try:
        status, payload = _request_json(runtime.state["bound_port"], f"{LATEST_PATH}?channel=public_rc")
    finally:
        runtime.stop()

    assert status == 200
    assert payload["schema_version"] == "software_release_assertion.v0.1"
    assert isinstance(payload["software_release_node"], dict)
    assert len(payload["release_attestation_edges"]) == 3
    assert all(edge["signature_hex"] for edge in payload["release_attestation_edges"])


def test_release_endpoint_missing_channel_returns_404_token() -> None:
    runtime = _with_runtime(_StubStore(None))
    try:
        status, payload = _request_json(runtime.state["bound_port"], f"{LATEST_PATH}?channel=beta")
    finally:
        runtime.stop()

    assert status == 404
    assert payload == {"channel": "beta", "token": "release_assertion_not_found"}


def test_release_endpoint_store_error_returns_503_token() -> None:
    runtime = _with_runtime(_StubStore(_release_assertion(), fail=True))
    try:
        status, payload = _request_json(runtime.state["bound_port"])
    finally:
        runtime.stop()

    assert status == 503
    assert payload == {
        "channel": "public_rc",
        "token": "release_assertion_store_unavailable",
    }


def test_release_endpoint_oversize_response_returns_503_token(monkeypatch) -> None:
    payload = _release_assertion()
    payload["oversize_padding"] = "x" * (MAX_UPGRADE_ASSERTION_BYTES + 1)
    monkeypatch.setattr(fetch_runtime_module, "validate_release_assertion", lambda _: {})
    runtime = _with_runtime(_StubStore(payload))
    try:
        status, response = _request_json(runtime.state["bound_port"])
    finally:
        runtime.stop()

    assert status == 503
    assert response == {
        "channel": "public_rc",
        "token": "release_assertion_response_too_large",
    }


def test_release_endpoint_rejects_invalid_latest_assertion() -> None:
    payload = _release_assertion()
    payload["release_attestation_edges"] = []
    runtime = _with_runtime(_StubStore(payload))
    try:
        status, response = _request_json(runtime.state["bound_port"])
    finally:
        runtime.stop()

    assert status == 503
    assert response == {
        "channel": "public_rc",
        "token": "release_assertion_invalid",
    }


def test_release_endpoint_serialization_failure_returns_503_token(monkeypatch) -> None:
    payload = _release_assertion()
    payload["non_json_extra"] = b"not-json-serializable"
    monkeypatch.setattr(fetch_runtime_module, "validate_release_assertion", lambda _: {})
    runtime = _with_runtime(_StubStore(payload))
    try:
        status, response = _request_json(runtime.state["bound_port"])
    finally:
        runtime.stop()

    assert status == 503
    assert response == {
        "channel": "public_rc",
        "token": "release_assertion_serialize_failed",
    }


def test_release_endpoint_rejects_blank_duplicate_and_long_channel() -> None:
    runtime = _with_runtime(_StubStore(_release_assertion()))
    try:
        blank_status, blank_payload = _request_json(runtime.state["bound_port"], f"{LATEST_PATH}?channel=")
        duplicate_status, duplicate_payload = _request_json(
            runtime.state["bound_port"],
            f"{LATEST_PATH}?channel=public_rc&channel=stable",
        )
        long_status, long_payload = _request_json(
            runtime.state["bound_port"],
            f"{LATEST_PATH}?channel={'a' * 129}",
        )
    finally:
        runtime.stop()

    assert blank_status == 400
    assert duplicate_status == 400
    assert long_status == 400
    assert blank_payload == {"token": "release_assertion_channel_invalid"}
    assert duplicate_payload == {"token": "release_assertion_channel_invalid"}
    assert long_payload == {"token": "release_assertion_channel_invalid"}


def test_release_endpoint_unknown_get_path_returns_404_token() -> None:
    runtime = _with_runtime(_StubStore(_release_assertion()))
    try:
        status, payload = _request_json(runtime.state["bound_port"], "/not-the-release-endpoint")
    finally:
        runtime.stop()

    assert status == 404
    assert payload == {"path": "/not-the-release-endpoint", "token": "fetch_unknown_path"}


def test_release_endpoint_unknown_get_path_echo_is_bounded() -> None:
    runtime = _with_runtime(_StubStore(_release_assertion()))
    long_path = "/" + ("x" * 1000)
    try:
        status, payload = _request_json(runtime.state["bound_port"], long_path)
    finally:
        runtime.stop()

    assert status == 404
    assert payload == {"path": long_path[:256], "token": "fetch_unknown_path"}


def test_truth_graph_store_skips_invalid_higher_version_candidate(tmp_path: Path) -> None:
    store = TruthPrimitiveGraphStore(tmp_path / "graph.lmdb")
    try:
        valid = _release_assertion()
        invalid_higher = _release_assertion_with(
            version="9.9.9",
            release_date="2026-10-07T00:00:00Z",
        )
        store.put_node_if_absent("release-valid", valid)
        store.put_node_if_absent("release-invalid-higher", invalid_higher)
        payload = store.get_latest_release_assertion("public_rc")
    finally:
        store.close()

    assert payload is not None
    assert payload["software_release_node"]["version"] == "0.4.34"


def test_truth_graph_store_extracts_release_assertion_from_native_node(tmp_path: Path) -> None:
    envelope = _release_assertion()["native_submit_envelope"]
    store = TruthPrimitiveGraphStore(tmp_path / "graph.lmdb")
    try:
        store.put_node_if_absent(
            "bafy-release-assertion-test",
            {
                "v": envelope["v"],
                "agent_id": envelope["agent_id"],
                "epoch": envelope["epoch"],
                "payload": envelope["payload"],
                "primitive": envelope["primitive"],
                "native_submit_sig": envelope["sig"],
            },
        )
        payload = store.get_latest_release_assertion("public_rc")
    finally:
        store.close()

    assert payload is not None
    result = upgrade_check.validate_release_assertion(payload)
    assert result["release_signature_verified"] is True


def test_upgrade_check_peer_path_consumes_release_endpoint_payload(tmp_path: Path) -> None:
    hints = tmp_path / "bootstrap_peer_hints.json"
    hints.write_text(
        json.dumps(
            {
                "schema_version": "bootstrap_peer_hints.v0.1",
                "known_peer_hints": [{"endpoint": "https://peer.example:8765"}],
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    observed: dict[str, Any] = {}

    def peer_fetcher(endpoint: str, timeout: float, headers: dict[str, str]) -> dict[str, Any]:
        observed["endpoint"] = endpoint
        observed["headers"] = dict(headers)
        return _release_assertion()

    def fallback_fetcher(endpoint: str, timeout: float) -> dict[str, Any]:
        raise AssertionError("https fallback must not be used")

    result = upgrade_check.check_for_upgrade(
        state_path=tmp_path / "upgrade_state.json",
        bootstrap_peer_hints_paths=[hints],
        peer_fetcher=peer_fetcher,
        fetcher=fallback_fetcher,
        evaluation_runtime=upgrade_check.UpgradeEvaluationRuntime(
            installed_version_resolver=lambda: "0.4.31",
            now_fn=lambda: datetime(2026, 10, 7, 12, 0, 0, tzinfo=timezone.utc),
        ),
    )

    assert observed["endpoint"] == "https://peer.example:8765/.well-known/ilc/software-release/latest.json"
    assert observed["headers"][UPGRADE_CHECK_D2D_HOP_COUNT_HEADER] == UPGRADE_CHECK_D2D_HOP_COUNT_VALUE
    assert result["discovery_source"] == "bootstrap_peer_hint"
    assert result["discovery_source"] != "https_fallback"
    assert result["release_signature_verified"] is True
