import json
import ssl
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

from ilc_core.ledger.canon_bundle_key_registry_fetch import (
    _copy_response_bounded,
    _extract_archive,
)
from ilc_core.ledger.persistent_backend import FileLedgerBackend
from ilc_core.network.d2d import truth_primitive_fetch_runtime as fetch_rt
from ilc_core.network.d2d import truth_primitive_gossip_runtime as gossip_rt
from ilc_core.network.d2d.http_gossip_transport_runtime import (
    HttpGossipTransportRuntime,
    TransportRuntimeConfig,
)
from tools.check_sensitive_runtime_coding_taboos import find_violations


class _FakeResponse:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload

    def read(self, size: int = -1) -> bytes:
        if size < 0:
            size = len(self.payload)
        out = self.payload[:size]
        self.payload = self.payload[size:]
        return out


def test_fix1_fetch_tls_verification_default_and_insecure_opt_out_ignored(monkeypatch):
    monkeypatch.delenv("ILC_D2D_PUBLIC_MODE", raising=False)
    monkeypatch.delenv("ILC_D2D_INSECURE_SKIP_TLS_VERIFY", raising=False)
    verified = fetch_rt._client_ssl_context()
    assert verified.verify_mode == ssl.CERT_REQUIRED
    assert verified.check_hostname is True

    monkeypatch.setenv("ILC_D2D_INSECURE_SKIP_TLS_VERIFY", "1")
    verified = fetch_rt._client_ssl_context()
    assert verified.verify_mode == ssl.CERT_REQUIRED
    assert verified.check_hostname is True


def test_fix81_fetch_tls_public_mode_ignores_insecure_opt_out(monkeypatch):
    monkeypatch.setenv("ILC_D2D_PUBLIC_MODE", "1")
    monkeypatch.setenv("ILC_D2D_INSECURE_SKIP_TLS_VERIFY", "1")

    verified = fetch_rt._client_ssl_context()

    assert verified.verify_mode == ssl.CERT_REQUIRED
    assert verified.check_hostname is True


def test_fix81_gossip_tls_public_mode_ignores_insecure_opt_out(monkeypatch):
    monkeypatch.setenv("ILC_D2D_PUBLIC_MODE", "1")
    monkeypatch.setenv("ILC_D2D_INSECURE_SKIP_TLS_VERIFY", "1")

    verified = gossip_rt._client_ssl_context()

    assert verified.verify_mode == ssl.CERT_REQUIRED
    assert verified.check_hostname is True


def test_fix81_gossip_tls_dev_opt_out_ignored(monkeypatch):
    monkeypatch.delenv("ILC_D2D_PUBLIC_MODE", raising=False)
    monkeypatch.setenv("ILC_D2D_INSECURE_SKIP_TLS_VERIFY", "1")

    verified = gossip_rt._client_ssl_context()

    assert verified.verify_mode == ssl.CERT_REQUIRED
    assert verified.check_hostname is True


def test_fix1_http_gossip_tls_verification_default_and_testbed_opt_out_ignored(monkeypatch, tmp_path):
    monkeypatch.delenv("ILC_D2D_PUBLIC_MODE", raising=False)
    cert = tmp_path / "cert.pem"
    key = tmp_path / "key.pem"
    cert.write_text("placeholder", encoding="utf-8")
    key.write_text("placeholder", encoding="utf-8")

    default_runtime = HttpGossipTransportRuntime(
        TransportRuntimeConfig("http", "127.0.0.1", 0, str(cert), str(key))
    )
    verified = default_runtime._client_ssl_context()
    assert verified.verify_mode == ssl.CERT_REQUIRED
    assert verified.check_hostname is True

    insecure_runtime = HttpGossipTransportRuntime(
        TransportRuntimeConfig(
            "http",
            "127.0.0.1",
            0,
            str(cert),
            str(key),
            verify_peer_tls=False,
        )
    )
    verified = insecure_runtime._client_ssl_context()
    assert verified.verify_mode == ssl.CERT_REQUIRED
    assert verified.check_hostname is True
    assert insecure_runtime.state["event_log"][-1]["event"] == "tls_insecure_bypass_ignored"


def test_fix81_http_gossip_public_mode_overrides_testbed_opt_out(monkeypatch, tmp_path):
    cert = tmp_path / "cert.pem"
    key = tmp_path / "key.pem"
    cert.write_text("placeholder", encoding="utf-8")
    key.write_text("placeholder", encoding="utf-8")
    monkeypatch.setenv("ILC_D2D_PUBLIC_MODE", "1")

    runtime = HttpGossipTransportRuntime(
        TransportRuntimeConfig(
            "http",
            "127.0.0.1",
            0,
            str(cert),
            str(key),
            verify_peer_tls=False,
        )
    )
    verified = runtime._client_ssl_context()

    assert verified.verify_mode == ssl.CERT_REQUIRED
    assert verified.check_hostname is True
    assert runtime.state["event_log"][-1]["event"] == "tls_insecure_bypass_ignored"


def test_fix2_no_runtime_tls_client_disables_certificate_verification() -> None:
    for path in (
        Path(fetch_rt.__file__),
        Path(gossip_rt.__file__),
        Path("ilc_core/network/d2d/http_gossip_transport_runtime.py"),
    ):
        source = path.read_text(encoding="utf-8")
        assert "ssl.CERT_NONE" not in source
        assert "verify_mode = " not in source


def test_fix1_want_block_oversize_response_fails_closed():
    class _MockOpener:
        def open(self, _req, **_kw):
            return _ContextResponse(b"x" * (fetch_rt._MAX_RESPONSE_BYTES + 1))

    class _ContextResponse:
        def __init__(self, payload: bytes) -> None:
            self.response = _FakeResponse(payload)

        def __enter__(self):
            return self.response

        def __exit__(self, exc_type, exc, tb):
            return None

    with patch("urllib.request.build_opener", return_value=_MockOpener()):
        with pytest.raises(fetch_rt.FetchTransportError) as exc:
            fetch_rt.want_block("node-1", "https://peer.example")
    assert exc.value.token == "fetch_response_too_large"


def test_fix1_registry_download_copy_is_bounded(tmp_path):
    response = _FakeResponse(b"x" * 12)
    result = _copy_response_bounded(response, tmp_path / "bundle.zip", max_bytes=10)
    assert result == {"ok": False, "error": "source_download_too_large"}


def test_fix1_registry_archive_extract_size_is_bounded(tmp_path):
    archive = tmp_path / "bundle.zip"
    extract_dir = tmp_path / "extract"
    extract_dir.mkdir()
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("bundle/file.txt", "x" * 20)

    result = _extract_archive(archive, extract_dir, max_extract_bytes=10)
    assert result == {"ok": False, "error": "archive_extract_size_exceeded"}


def test_fix1_file_ledger_backend_writes_canonical_json(tmp_path):
    backend = FileLedgerBackend(str(tmp_path))
    target = tmp_path / "canonical.json"
    backend._atomic_write(str(target), {"z": 1, "a": 2})
    text = target.read_text(encoding="utf-8")

    assert text.index('"a"') < text.index('"z"')
    assert json.loads(text) == {"a": 2, "z": 1}

    with pytest.raises(ValueError):
        backend._atomic_write(str(tmp_path / "nan.json"), {"bad": float("nan")})


def test_fix1_serve_reputation_no_longer_uses_wall_clock_epoch_source():
    source = Path(fetch_rt.__file__).read_text(encoding="utf-8")
    assert "int(time.time() // 60)" not in source
    assert "serve_epoch" in source


def test_fix1_sensitive_runtime_guardrail_passes():
    assert find_violations() == []
