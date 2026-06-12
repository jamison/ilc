"""Phase 1559 — HB-002 minimal serving receipt tests.

PUBLIC_RC_EXCLUDE: phase_1559_private_runtime_selftest
PUBLIC_RC_EXCLUDE_REASON: Private pre-RC HB-002 serving receipt selftest. No live Tailscale calls.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import ilc_core.genesis.serving_receipt as serving_receipt
from ilc_core.bundle.layer0_protocol_bundle import generate_layer0_protocol_bundle
from ilc_core.bundle.layer1_genesis_bundle import generate_layer1_genesis_bundle
from ilc_core.genesis.serving_receipt import (
    MAX_SERVING_RESPONSE_BYTES,
    SERVING_HTTP_TIMEOUT_SECONDS,
    SERVING_RULE_VERSION,
    ServingReceiptError,
    build_serving_receipt,
    serve_genesis_bundle,
    verify_received_bundle,
    write_serving_receipt_json,
)


class _FakeResponse:
    def __init__(self, body: bytes) -> None:
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self, limit: int = -1) -> bytes:
        if limit < 0:
            return self.body
        return self.body[:limit]


class _FakeOpener:
    def __init__(self, body: bytes, capture: dict[str, object]) -> None:
        self.body = body
        self.capture = capture

    def open(self, request: object, *, timeout: int):
        self.capture["timeout"] = timeout
        self.capture["url"] = getattr(request, "full_url", "")
        self.capture["data"] = getattr(request, "data", b"")
        return _FakeResponse(self.body)


class _RaisingOpener:
    def __init__(self, error: BaseException) -> None:
        self.error = error

    def open(self, request: object, *, timeout: int):
        raise self.error


def _layer0_fixture():
    return generate_layer0_protocol_bundle(
        bundle_id="phase1559-layer0",
        version="v0.1-private",
        schemas=[{"type_name": "Node", "required": ["node_id"]}],
        parameters={"truth_primitives": 7},
        include_truth_primitive_schemas=True,
    )


def _layer1_fixture(layer0):
    return generate_layer1_genesis_bundle(
        bundle_id="phase1559-layer1",
        layer0_sha256=layer0.sha256,
        layer0_cidv1=layer0.cidv1,
        seed_claims=[{"claim_id": "seed-001", "truth_primitive": "assert.truth"}],
        initial_agent_roster=[{"agent_id": "agent-a"}],
        initial_shard_topology={"shards": [], "version": "v0.1-private"},
        genesis_signing_key_refs=[{"key_ref": "key-a"}],
    )


def test_build_serving_receipt_is_deterministic_and_spec_shaped() -> None:
    layer0 = _layer0_fixture()
    receipt_a = build_serving_receipt(
        "agent-genesis",
        "layer0",
        layer0_protocol_bundle_sha256=layer0.sha256,
        layer0_protocol_bundle_cidv1=layer0.cidv1,
        serving_epoch=0,
    )
    receipt_b = build_serving_receipt(
        "agent-genesis",
        "layer0",
        layer0_protocol_bundle_sha256=layer0.sha256,
        layer0_protocol_bundle_cidv1=layer0.cidv1,
        serving_epoch=0,
    )

    assert receipt_a == receipt_b
    assert receipt_a.serving_receipt_id.startswith("serving_receipt:")
    assert receipt_a.serving_rule_version == SERVING_RULE_VERSION
    assert receipt_a.serving_epoch == 0
    assert receipt_a.layer0_protocol_bundle_sha256 == layer0.sha256
    assert receipt_a.layer0_protocol_bundle_cidv1 == layer0.cidv1


def test_build_serving_receipt_rejects_wall_clock_like_float_epoch() -> None:
    layer0 = _layer0_fixture()
    with pytest.raises(ServingReceiptError, match="serving_receipt_float_not_allowed"):
        build_serving_receipt(
            "agent-genesis",
            "layer0",
            layer0_protocol_bundle_sha256=layer0.sha256,
            serving_epoch=0.5,  # type: ignore[arg-type]
        )


def test_build_serving_receipt_rejects_invalid_epoch_bool() -> None:
    layer0 = _layer0_fixture()
    with pytest.raises(ServingReceiptError, match="serving_receipt_invalid_protocol_epoch"):
        build_serving_receipt(
            "agent-genesis",
            "layer0",
            layer0_protocol_bundle_sha256=layer0.sha256,
            serving_epoch=True,  # type: ignore[arg-type]
        )


def test_write_serving_receipt_json_uses_canonical_atomic_output(tmp_path: Path) -> None:
    layer0 = _layer0_fixture()
    receipt = build_serving_receipt(
        "agent-genesis",
        "layer0",
        layer0_protocol_bundle_sha256=layer0.sha256,
        layer0_protocol_bundle_cidv1=layer0.cidv1,
        serving_epoch=0,
    )
    out = tmp_path / "receipt.json"

    write_serving_receipt_json(receipt, out)

    written = out.read_text(encoding="utf-8")
    assert written.endswith("\n")
    parsed = json.loads(written)
    assert parsed["serving_receipt_id"] == receipt.serving_receipt_id
    assert list(parsed) == sorted(parsed)
    assert not list(tmp_path.glob("*.tmp"))


def test_serve_genesis_bundle_posts_to_known_peer_with_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    layer0 = _layer0_fixture()
    layer1 = _layer1_fixture(layer0)
    capture: dict[str, object] = {}

    def fake_build_opener(*_args: object) -> _FakeOpener:
        return _FakeOpener(b'{"accepted":true}', capture)

    monkeypatch.setattr(serving_receipt.urllib.request, "build_opener", fake_build_opener)

    receipt = serve_genesis_bundle("https://100.64.0.10:8443", layer0, layer1)

    assert capture["timeout"] == SERVING_HTTP_TIMEOUT_SECONDS
    assert capture["url"] == "https://100.64.0.10:8443/ilc/genesis/serve"
    assert receipt.served_layer == "layer0+layer1"
    assert receipt.layer0_protocol_bundle_cidv1 == layer0.cidv1
    body = json.loads(capture["data"].decode("utf-8"))  # type: ignore[union-attr]
    assert body["receipt"]["serving_receipt_id"] == receipt.serving_receipt_id
    assert body["layer0"]["sha256"] == layer0.sha256
    assert body["layer1"]["sha256"] == layer1.sha256


def test_verify_received_bundle_posts_expected_cid_with_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    layer0 = _layer0_fixture()
    capture: dict[str, object] = {}
    body = json.dumps(
        {"verified": True, "layer0_cidv1": layer0.cidv1},
        sort_keys=True,
    ).encode("utf-8")

    def fake_build_opener(*_args: object) -> _FakeOpener:
        return _FakeOpener(body, capture)

    monkeypatch.setattr(serving_receipt.urllib.request, "build_opener", fake_build_opener)

    assert verify_received_bundle("https://100.64.0.11:8443", layer0.cidv1) is True
    assert capture["timeout"] == SERVING_HTTP_TIMEOUT_SECONDS
    assert capture["url"] == "https://100.64.0.11:8443/ilc/genesis/verify"


def test_verify_received_bundle_rejects_cid_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    layer0 = _layer0_fixture()

    def fake_build_opener(*_args: object) -> _FakeOpener:
        return _FakeOpener(b'{"verified":true,"layer0_cidv1":"different"}', {})

    monkeypatch.setattr(serving_receipt.urllib.request, "build_opener", fake_build_opener)

    assert verify_received_bundle("https://100.64.0.12:8443", layer0.cidv1) is False


def test_serving_response_size_is_bounded(monkeypatch: pytest.MonkeyPatch) -> None:
    layer0 = _layer0_fixture()
    oversized = b"{" + (b" " * (MAX_SERVING_RESPONSE_BYTES + 1)) + b"}"

    def fake_build_opener(*_args: object) -> _FakeOpener:
        return _FakeOpener(oversized, {})

    monkeypatch.setattr(serving_receipt.urllib.request, "build_opener", fake_build_opener)

    with pytest.raises(ServingReceiptError, match="serving_receipt_response_too_large"):
        serve_genesis_bundle("https://100.64.0.13:8443", layer0)


def test_serving_response_rejects_invalid_json(monkeypatch: pytest.MonkeyPatch) -> None:
    layer0 = _layer0_fixture()

    def fake_build_opener(*_args: object) -> _FakeOpener:
        return _FakeOpener(b"{not-json", {})

    monkeypatch.setattr(serving_receipt.urllib.request, "build_opener", fake_build_opener)

    with pytest.raises(ServingReceiptError, match="serving_receipt_response_invalid_json"):
        serve_genesis_bundle("https://100.64.0.15:8443", layer0)


def test_serving_transport_os_errors_are_stable(monkeypatch: pytest.MonkeyPatch) -> None:
    layer0 = _layer0_fixture()

    def fake_build_opener(*_args: object) -> _RaisingOpener:
        return _RaisingOpener(TimeoutError("timed out"))

    monkeypatch.setattr(serving_receipt.urllib.request, "build_opener", fake_build_opener)

    with pytest.raises(ServingReceiptError, match="serving_receipt_transport_error"):
        serve_genesis_bundle("https://100.64.0.16:8443", layer0)


def test_known_peer_surface_rejects_non_https_endpoint() -> None:
    layer0 = _layer0_fixture()
    with pytest.raises(ValueError, match="peer_endpoint_must_use_https"):
        serve_genesis_bundle("http://100.64.0.14:8443", layer0)
