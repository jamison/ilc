from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import threading
from typing import Any, Callable, Iterator, Mapping

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from ilc_core.encoding.cidv1 import node_id_from_obj
from ilc_core.release import upgrade_check
from ilc_core.release.constants import (
    MAX_UPGRADE_ASSERTION_BYTES,
    UPGRADE_CHECK_D2D_HOP_COUNT_HEADER,
    UPGRADE_CHECK_D2D_HOP_COUNT_VALUE,
)
from ilc_core.release.installable_release_signature import (
    DEFAULT_GENESIS_LINEAGE_REF,
    DEFAULT_PRIOR_RELEASE_ENVELOPE_REF,
    DEFAULT_RELEASE_KEY_REGISTRATION_REF,
    SIGNED_PREIMAGE_DOMAIN,
    compute_signed_preimage_sha256,
)


LATEST_PATH = "/.well-known/ilc/software-release/latest.json"


def _release_keypair() -> tuple[Ed25519PrivateKey, str]:
    private_key = Ed25519PrivateKey.generate()
    public_key_hex = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    ).hex()
    return private_key, public_key_hex


def _release_assertion_payload(
    *,
    private_key: Ed25519PrivateKey,
    public_key_hex: str,
    version: str = "0.4.33",
    signature_hex: str | None = None,
) -> dict[str, Any]:
    artifact_id = f"ilc-artifact:ilc-core-python-wheel-{version.replace('.', '')}@phase-1628"
    artifact_sha256 = "55" * 32
    signed_preimage_sha256 = compute_signed_preimage_sha256(
        release_id=f"ilc-core-{version}",
        artifact_id=artifact_id,
        artifact_sha256=artifact_sha256,
    )
    artifact_body = {
        "artifact_id": artifact_id,
        "artifact_type": "wheel",
        "filename": f"ilc_core-{version}-py3-none-any.whl",
        "node_kind": "ArtifactNode",
        "package_name": "ilc-core",
        "package_version": version,
        "pypi_url": "https://example.test/release.whl",
        "schema_version": "artifact_node.v0.1",
        "sha256": artifact_sha256,
        "size_bytes": 1234,
    }
    artifact = {**artifact_body, "cid": node_id_from_obj(artifact_body)}
    recipe_body = {
        "build_command": "python -m build",
        "build_date": "2026-10-09T12:00:00Z",
        "build_env_hash": "66" * 32,
        "build_toolchain": "python-build",
        "builder_agent_id": "phase:http-peer-test",
        "node_kind": "BuildRecipeNode",
        "reproducibility_hash": "77" * 32,
        "schema_version": "build_recipe_node.v0.1",
        "source_commit": "44" * 32,
    }
    recipe = {**recipe_body, "cid": node_id_from_obj(recipe_body)}
    release_body = {
        "artifact_cids": [artifact["cid"]],
        "build_recipe_cid": recipe["cid"],
        "changelog_hash": "33" * 32,
        "node_kind": "SoftwareReleaseNode",
        "package_name": "ilc-core",
        "release_channel": "public_rc",
        "release_date": "2026-10-09T12:00:00Z",
        "release_key_pubkey": public_key_hex,
        "release_signature_ref": "release-attestation:wheel",
        "schema_version": "software_release_node.v0.1",
        "source_commit": "44" * 32,
        "version": version,
    }
    release = {**release_body, "cid": node_id_from_obj(release_body)}
    edge = {
        "artifact_id": artifact_id,
        "artifact_sha256": artifact_sha256,
        "attestation_date": "2026-10-09T12:00:00Z",
        "edge_type": "RELEASE_ATTESTS_ARTIFACT",
        "genesis_lineage_ref": DEFAULT_GENESIS_LINEAGE_REF,
        "prior_release_envelope_ref": DEFAULT_PRIOR_RELEASE_ENVELOPE_REF,
        "release_key_registration_ref": DEFAULT_RELEASE_KEY_REGISTRATION_REF,
        "schema_version": "release_attestation_edge.v0.1",
        "signed_preimage_domain": SIGNED_PREIMAGE_DOMAIN,
        "signed_preimage_sha256": signed_preimage_sha256,
        "signer_public_key_hex": public_key_hex,
        "signature_hex": signature_hex
        or private_key.sign(bytes.fromhex(signed_preimage_sha256)).hex(),
        "signing_algorithm": "Ed25519",
        "source": release["cid"],
        "target": artifact["cid"],
    }
    body = {
        "artifact_nodes": [artifact],
        "build_recipe_nodes": [recipe],
        "release_attestation_edges": [edge],
        "schema_version": "software_release_assertion.v0.1",
        "software_release_node": release,
    }
    return {**body, "assertion_cid": node_id_from_obj(body)}


def _fixed_now() -> datetime:
    return datetime(2026, 10, 9, 12, 30, 0, tzinfo=timezone.utc)


def _write_bootstrap_fetch_peers(path: Path, endpoints: list[str]) -> None:
    path.write_text(
        json.dumps(
            {"peer_endpoints": endpoints, "schema_version": "bootstrap_fetch_peers.v0.1"},
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def _fallback(payload: Mapping[str, Any]) -> Callable[[str, float], Mapping[str, Any]]:
    def _fetcher(endpoint: str, timeout: float) -> Mapping[str, Any]:
        return payload

    return _fetcher


def _fail_fallback(endpoint: str, timeout: float) -> Mapping[str, Any]:
    raise AssertionError("HTTPS fallback must not be used")


def _header_value(headers: Mapping[str, str], name: str) -> str | None:
    for key, value in headers.items():
        if key.lower() == name.lower():
            return value
    return None


class _ServerState:
    def __init__(self) -> None:
        self.headers: dict[str, str] = {}
        self.paths: list[str] = []


@contextmanager
def _http_server(
    handler_fn: Callable[[BaseHTTPRequestHandler, _ServerState], None],
) -> Iterator[tuple[str, _ServerState]]:
    state = _ServerState()

    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - stdlib callback name.
            state.headers = {key: value for key, value in self.headers.items()}
            state.paths.append(self.path)
            handler_fn(self, state)

        def log_message(self, format: str, *args: object) -> None:
            return None

    server = HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}", state
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def _send_json(handler: BaseHTTPRequestHandler, payload: Mapping[str, Any]) -> None:
    body = json.dumps(payload, sort_keys=True).encode("utf-8")
    handler.send_response(200)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _check_for_upgrade(
    *,
    tmp_path: Path,
    public_key_hex: str,
    hints_path: Path,
    fetcher: Callable[[str, float], Mapping[str, Any]] = _fail_fallback,
    peer_fetcher: Callable[[str, float, Mapping[str, str]], Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    if peer_fetcher is not None:
        kwargs["peer_fetcher"] = peer_fetcher
    return upgrade_check.check_for_upgrade(
        bootstrap_peer_hints_paths=[hints_path],
        fetcher=fetcher,
        installed_version_resolver=lambda: "0.4.32",
        now_fn=_fixed_now,
        state_path=tmp_path / "upgrade_state.json",
        **kwargs,
    )


def test_http_peer_discovery_succeeds_through_default_fetcher(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    private_key, public_key_hex = _release_keypair()
    payload = _release_assertion_payload(private_key=private_key, public_key_hex=public_key_hex)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)

    with _http_server(lambda handler, state: _send_json(handler, payload)) as (base_url, state):
        hints_path = tmp_path / "bootstrap_fetch_peers.json"
        _write_bootstrap_fetch_peers(hints_path, [base_url])

        result = _check_for_upgrade(
            tmp_path=tmp_path,
            public_key_hex=public_key_hex,
            hints_path=hints_path,
        )

    assert result["discovery_source"] == "bootstrap_peer_hint"
    assert result["assertion_cid"] == payload["assertion_cid"]
    assert state.paths == [LATEST_PATH]
    assert _header_value(state.headers, UPGRADE_CHECK_D2D_HOP_COUNT_HEADER) == (
        UPGRADE_CHECK_D2D_HOP_COUNT_VALUE
    )


def test_http_peer_tampered_payload_isolated_then_falls_back(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    private_key, public_key_hex = _release_keypair()
    valid = _release_assertion_payload(private_key=private_key, public_key_hex=public_key_hex)
    tampered = _release_assertion_payload(
        private_key=private_key,
        public_key_hex=public_key_hex,
        signature_hex="00" * 64,
    )
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)

    with _http_server(lambda handler, state: _send_json(handler, tampered)) as (base_url, _state):
        hints_path = tmp_path / "bootstrap_fetch_peers.json"
        _write_bootstrap_fetch_peers(hints_path, [base_url])

        result = _check_for_upgrade(
            tmp_path=tmp_path,
            public_key_hex=public_key_hex,
            hints_path=hints_path,
            fetcher=_fallback(valid),
        )

    assert result["discovery_source"] == "https_fallback"


def test_explicit_endpoint_still_requires_https(tmp_path: Path) -> None:
    with pytest.raises(upgrade_check.UpgradeCheckError) as excinfo:
        upgrade_check.check_for_upgrade(
            endpoint="http://127.0.0.1:9999",
            fetcher=_fail_fallback,
            installed_version_resolver=lambda: "0.4.32",
            now_fn=_fixed_now,
            state_path=tmp_path / "upgrade_state.json",
        )

    assert excinfo.value.token == "upgrade_check_endpoint_insecure"


def test_http_peer_fetch_sends_single_hop_header(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    private_key, public_key_hex = _release_keypair()
    payload = _release_assertion_payload(private_key=private_key, public_key_hex=public_key_hex)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)

    with _http_server(lambda handler, state: _send_json(handler, payload)) as (base_url, state):
        hints_path = tmp_path / "bootstrap_fetch_peers.json"
        _write_bootstrap_fetch_peers(hints_path, [base_url])
        _check_for_upgrade(tmp_path=tmp_path, public_key_hex=public_key_hex, hints_path=hints_path)

    assert _header_value(state.headers, UPGRADE_CHECK_D2D_HOP_COUNT_HEADER) == (
        UPGRADE_CHECK_D2D_HOP_COUNT_VALUE
    )


def test_http_peer_redirect_is_not_followed_and_falls_back(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    private_key, public_key_hex = _release_keypair()
    valid = _release_assertion_payload(private_key=private_key, public_key_hex=public_key_hex)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)

    def _redirect(handler: BaseHTTPRequestHandler, state: _ServerState) -> None:
        handler.send_response(301)
        handler.send_header("Location", "http://127.0.0.1/not-followed")
        handler.send_header("Content-Length", "0")
        handler.end_headers()

    with _http_server(_redirect) as (base_url, _state):
        hints_path = tmp_path / "bootstrap_fetch_peers.json"
        _write_bootstrap_fetch_peers(hints_path, [base_url])
        result = _check_for_upgrade(
            tmp_path=tmp_path,
            public_key_hex=public_key_hex,
            hints_path=hints_path,
            fetcher=_fallback(valid),
        )

    assert result["discovery_source"] == "https_fallback"


def test_http_peer_oversized_response_isolated_then_falls_back(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    private_key, public_key_hex = _release_keypair()
    valid = _release_assertion_payload(private_key=private_key, public_key_hex=public_key_hex)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)

    def _oversized(handler: BaseHTTPRequestHandler, state: _ServerState) -> None:
        handler.send_response(200)
        handler.send_header("Content-Type", "application/json")
        handler.send_header("Content-Length", str(MAX_UPGRADE_ASSERTION_BYTES + 1))
        handler.end_headers()

    with _http_server(_oversized) as (base_url, _state):
        hints_path = tmp_path / "bootstrap_fetch_peers.json"
        _write_bootstrap_fetch_peers(hints_path, [base_url])
        result = _check_for_upgrade(
            tmp_path=tmp_path,
            public_key_hex=public_key_hex,
            hints_path=hints_path,
            fetcher=_fallback(valid),
        )

    assert result["discovery_source"] == "https_fallback"


def test_http_peer_negative_content_length_isolated_then_falls_back(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    private_key, public_key_hex = _release_keypair()
    valid = _release_assertion_payload(private_key=private_key, public_key_hex=public_key_hex)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)

    def _negative_length(handler: BaseHTTPRequestHandler, state: _ServerState) -> None:
        handler.send_response(200)
        handler.send_header("Content-Type", "application/json")
        handler.send_header("Content-Length", "-1")
        handler.end_headers()
        handler.wfile.write(json.dumps(valid).encode("utf-8"))

    with _http_server(_negative_length) as (base_url, _state):
        hints_path = tmp_path / "bootstrap_fetch_peers.json"
        _write_bootstrap_fetch_peers(hints_path, [base_url])
        result = _check_for_upgrade(
            tmp_path=tmp_path,
            public_key_hex=public_key_hex,
            hints_path=hints_path,
            fetcher=_fallback(valid),
        )

    assert result["discovery_source"] == "https_fallback"


def test_invalid_peer_hint_scheme_is_skipped_without_crash(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    private_key, public_key_hex = _release_keypair()
    valid = _release_assertion_payload(private_key=private_key, public_key_hex=public_key_hex)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)
    hints_path = tmp_path / "bootstrap_fetch_peers.json"
    _write_bootstrap_fetch_peers(hints_path, ["ftp://127.0.0.1:9999"])

    result = _check_for_upgrade(
        tmp_path=tmp_path,
        public_key_hex=public_key_hex,
        hints_path=hints_path,
        fetcher=_fallback(valid),
    )

    assert result["discovery_source"] == "https_fallback"


def test_peer_hint_with_userinfo_is_skipped_without_crash(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    private_key, public_key_hex = _release_keypair()
    valid = _release_assertion_payload(private_key=private_key, public_key_hex=public_key_hex)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)
    hints_path = tmp_path / "bootstrap_fetch_peers.json"
    _write_bootstrap_fetch_peers(hints_path, ["http://user:pass@127.0.0.1:9999"])

    result = _check_for_upgrade(
        tmp_path=tmp_path,
        public_key_hex=public_key_hex,
        hints_path=hints_path,
        fetcher=_fallback(valid),
    )

    assert result["discovery_source"] == "https_fallback"


def test_peer_hint_with_query_or_fragment_is_skipped_without_crash(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    private_key, public_key_hex = _release_keypair()
    valid = _release_assertion_payload(private_key=private_key, public_key_hex=public_key_hex)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)
    hints_path = tmp_path / "bootstrap_fetch_peers.json"
    _write_bootstrap_fetch_peers(
        hints_path,
        ["http://127.0.0.1:9999?x=1", "http://127.0.0.1:9999#frag"],
    )

    result = _check_for_upgrade(
        tmp_path=tmp_path,
        public_key_hex=public_key_hex,
        hints_path=hints_path,
        fetcher=_fallback(valid),
    )

    assert result["discovery_source"] == "https_fallback"


def test_bootstrap_fetch_peers_loader_bounds_entries_and_filters_mixed_types(
    tmp_path: Path,
) -> None:
    hints_path = tmp_path / "bootstrap_fetch_peers.json"
    endpoints = [
        "http://peer-0.example",
        1,
        True,
        *[f"http://peer-{index}.example" for index in range(1, 100)],
    ]
    _write_bootstrap_fetch_peers(hints_path, endpoints)  # type: ignore[list-item]

    loaded = upgrade_check._load_peer_hint_endpoints(hints_path)

    assert len(loaded) <= 16
    assert loaded[0] == "http://peer-0.example"
    assert all(isinstance(endpoint, str) for endpoint in loaded)


def test_bootstrap_peer_hints_loader_rejects_oversized_file(tmp_path: Path) -> None:
    hints_path = tmp_path / "bootstrap_fetch_peers.json"
    hints_path.write_text(" " * 1_000_001, encoding="utf-8")

    assert upgrade_check._load_peer_hint_endpoints(hints_path) == []


def test_https_peer_hint_still_works_with_injected_peer_fetcher(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    private_key, public_key_hex = _release_keypair()
    payload = _release_assertion_payload(private_key=private_key, public_key_hex=public_key_hex)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)
    hints_path = tmp_path / "bootstrap_fetch_peers.json"
    _write_bootstrap_fetch_peers(hints_path, ["https://example.test"])
    observed: dict[str, Any] = {}

    def _peer_fetcher(endpoint: str, timeout: float, headers: Mapping[str, str]) -> Mapping[str, Any]:
        observed["endpoint"] = endpoint
        observed["headers"] = dict(headers)
        return payload

    result = _check_for_upgrade(
        tmp_path=tmp_path,
        public_key_hex=public_key_hex,
        hints_path=hints_path,
        peer_fetcher=_peer_fetcher,
    )

    assert result["discovery_source"] == "bootstrap_peer_hint"
    assert observed["endpoint"] == "https://example.test/.well-known/ilc/software-release/latest.json"
