from __future__ import annotations

import subprocess
import socket
import ssl
import textwrap
import time
import urllib.error
import urllib.request
from dataclasses import fields
from pathlib import Path

import pytest

from ilc_core.network.d2d import http_gossip_transport_runtime as runtime
from ilc_core.network.d2d import gossip_transport


RUNTIME_PATH = Path('ilc_core/network/d2d/http_gossip_transport_runtime.py')
TEST_PATH = Path('tests/test_phase_568_real_http_transport_wrapper_runtime.py')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_568_SUBJECT_TOKEN = 'phase 568 real http transport wrapper runtime'
EXACT_REQUIRED_MAIN_PATHS = {
    str(RUNTIME_PATH),
    str(TEST_PATH),
}

_CERT_PEM = textwrap.dedent(
    """\
    -----BEGIN CERTIFICATE-----
    MIICyTCCAbGgAwIBAgIJALJLJ4bAeT8DMA0GCSqGSIb3DQEBCwUAMBQxEjAQBgNV
    BAMMCWxvY2FsaG9zdDAeFw0yNjA3MTAxNDE4MjBaFw0zNjA3MDcxNDE4MjBaMBQx
    EjAQBgNVBAMMCWxvY2FsaG9zdDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoC
    ggEBAJE+5guqHASC9IyoFNkhOSWw+iCus2wGUZPdDRV5vXYkVTaL0mEj4Q9ezPz+
    Wiv+XtM93ureuPClQ/CnT1XVYteMoNX+qXEtqhMfQZAOB90b1pyBHQBn75M+gg+x
    9EGkulzBUttuoUIFdgmMnCqWVQS+nZSwSFwwd96473F9lAgEQ09ECY05aIduQF0A
    5tcHzI0xWNa4V3EPeezpRQabeTZycApgqFPqPN6OhphgJZeXMBvihZa9nRPUxF5M
    j+vUYL12S1Em5hZtLf2oh+2xwDBTLi2AemSgqTmJvE9d0guo8pNk8BPp3Ae6KB6V
    5yW+HaIQWPhjTLoT6zXglQ1ASqkCAwEAAaMeMBwwGgYDVR0RBBMwEYIJbG9jYWxo
    b3N0hwR/AAABMA0GCSqGSIb3DQEBCwUAA4IBAQBsDH5g6zUCQTJ7TaGecyJNN3Eu
    Dwz5dWRwyks1bDH5kQGQnsnOLfSuN2O+8b/BoJeNCGw0Sn+Kq4e32CIRFTG4GY7R
    V/j2opU6WMeqORB6HGE5FRo7uDBzyJ0FDh1kuR32UYgwbtbMNgv+/nhcDoJ44jeY
    ZS/ejGuUTsK+aewxhWVvV+6fiYOC0GmnVQQiNaG2JR5TJFeKTcykqBkbex8oXarE
    WM1NGBQlk4xlV2hBX6N2/opCbY7ICrFg8b80tDV5Qty/IqvpJdH4y8Q9M9NA2omg
    LHO1jnPCGm/LLonND1QxqEzQoe58Yl+bYtLsjnX+lNdm+9ZI+YgXmOlNpoKI
    -----END CERTIFICATE-----
    """
)

_KEY_PEM = textwrap.dedent(
    """\
    -----BEGIN PRIVATE KEY-----
    MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCRPuYLqhwEgvSM
    qBTZITklsPogrrNsBlGT3Q0Veb12JFU2i9JhI+EPXsz8/lor/l7TPd7q3rjwpUPw
    p09V1WLXjKDV/qlxLaoTH0GQDgfdG9acgR0AZ++TPoIPsfRBpLpcwVLbbqFCBXYJ
    jJwqllUEvp2UsEhcMHfeuO9xfZQIBENPRAmNOWiHbkBdAObXB8yNMVjWuFdxD3ns
    6UUGm3k2cnAKYKhT6jzejoaYYCWXlzAb4oWWvZ0T1MReTI/r1GC9dktRJuYWbS39
    qIftscAwUy4tgHpkoKk5ibxPXdILqPKTZPAT6dwHuigeleclvh2iEFj4Y0y6E+s1
    4JUNQEqpAgMBAAECggEAD9E6ujB3RqKAQUUYqCCvGYSxaJe94Fi7z492Gk2crV39
    jagibAO9QbBAQJjudvYHm5eUTB2fJE3LHU0LHbzUO8cLyOInz7R6XgS8XhS5FIIw
    l/CTmPS4qV9YSJ9Hi1KGHQ3MmSruEsOHfDi81QJ0FcUwYf3kk22P0Ehxgvl7AnhS
    YHvxjULbrrYipdxKiuWckiL0h8ZjviWPf16rsunSl3Zk/7gW5LfIEC8zueUCGxDX
    jFxtXQyBxScJZ/XKDpKzMsi7cA6NBymvogj1Aj9KI0wYW5aoa2qzJRcay5DFG5z9
    qyyElPcSJKbp0DadeVeSelXcyoQODa1Ovr21f0Lf1QKBgQDBD4Zj3Yp96J152UCm
    RC4FyLy05zVR9qQABYf2pu9bY1lWqgykrGVsVTyF9ip8cbC7A6IW8tC0ycsAJX8M
    CYpx9fJMGLDw+AV+kdAAfCTRBo05K/oxEnKcSAydGZwVVeuLdVvLgvdPZTE7ElS9
    0g9fQeYTVR1l1cN85koxsMAznwKBgQDAmNQ1MUPGzWFshLi9txvwUC8Z/dOZ9VVb
    hmIXwnAf7kBuayhW16rO4zxE0WMt04vB63OgsmvbEMwontghxKIt//DRGZ0NV0Sv
    G8OdmoCwXuMz99bZTFQyCjGe8+qISnycztRQ4isTXs+3Kt8kPCaNz9B8gSGCifI5
    AdeXFgoctwKBgDeTcop5Eg8g0YRsKBI0+lKr8LbbABxyNc/Tx8oXUDwso2ExXqZh
    AmlnOB8QODbOu6N6bkTQ7Ye9t3R5VtNuQ65+sJt7WCRmIZ7H9urM0gRiMHFO2Z0a
    xGd8zjTDVI1HyKDCzgQN1YfDh6KLql1ihQ5U+BiEngvct4PS/3TCfvHdAoGAOiMo
    E7J+WhmPKhnaRnJqvZ0GytrDMDtNe+ZR4AgynoDl9C7mq2hIyFDx1Xg7bw7npi7z
    5XNWeXdVmYFxjqfzqN0UjZokvW01b4J7By0nYZYTEZHjyg5vb/eByRCqIGATw6Xv
    k0biZ+N74jfPyflaTf6IWb0FJ4mKk8jJknL1tHsCgYEAo73O8mXYDQ6CSkG0zkjj
    1ARqufGDA+3ahE57EIdA5Q2LntdQM27L5cj2b809NIfCFtgaec21RZHNObX58m9o
    Ltfbj0pPjJWj4a4EMKVSLVVU0B+UWFZH/QWnRt4AC0rmlHVKP1Kws4Y9NU7gMum+
    PCykcpTjJERYPfRq2L4rCME=
    -----END PRIVATE KEY-----
    """
)


def _write_tls_material(tmp_path: Path) -> tuple[str, str]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    cert_path = tmp_path / 'localhost-cert.pem'
    key_path = tmp_path / 'localhost-key.pem'
    cert_path.write_text(_CERT_PEM, encoding='utf-8')
    key_path.write_text(_KEY_PEM, encoding='utf-8')
    return str(cert_path), str(key_path)


def _config(tmp_path: Path, *, transport_kind: str = runtime.TRANSPORT_KIND_HTTP) -> runtime.TransportRuntimeConfig:
    cert_path, key_path = _write_tls_material(tmp_path)
    return runtime.TransportRuntimeConfig(
        transport_kind=transport_kind,
        bind_host='127.0.0.1',
        bind_port=0,
        tls_cert_path=cert_path,
        tls_key_path=key_path,
        tls_ca_cert_path=cert_path,
        verify_peer_tls=False,
        allow_private_peer_endpoints_for_tests=True,
    )


def _raw_tls_post(
    *,
    port: int,
    path: str,
    headers: dict[str, str],
    body_prefix: bytes,
    body_suffix: bytes = b'',
    delay_after_prefix: float = 0.0,
    timeout: float = 1.0,
) -> bytes:
    request_headers = [f"POST {path} HTTP/1.1", "Host: 127.0.0.1", "Connection: close"]
    request_headers.extend(f"{key}: {value}" for key, value in headers.items())
    request = ("\r\n".join(request_headers) + "\r\n\r\n").encode("utf-8")
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    with socket.create_connection(("127.0.0.1", port), timeout=timeout) as raw_socket:
        with context.wrap_socket(raw_socket, server_hostname="127.0.0.1") as tls_socket:
            tls_socket.sendall(request)
            if body_prefix:
                tls_socket.sendall(body_prefix)
            if delay_after_prefix:
                time.sleep(delay_after_prefix)
            if body_suffix:
                try:
                    tls_socket.sendall(body_suffix)
                except OSError:
                    pass
            response = bytearray()
            while True:
                try:
                    chunk = tls_socket.recv(4096)
                except OSError:
                    break
                if not chunk:
                    break
                response.extend(chunk)
    return bytes(response)


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_568_commit_ref() -> str:
    result = subprocess.run(
        ['git', 'log', '--format=%H%x09%s'],
        capture_output=True,
        check=True,
        text=True,
    )
    matching: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if PHASE_568_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    raise AssertionError('phase_568_commit_not_present_in_local_history')


class _FakeResponse:
    def __init__(self, status_code: int) -> None:
        self._status_code = status_code

    def __enter__(self) -> '_FakeResponse':
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def getcode(self) -> int:
        return self._status_code


def test_module_imports_and_exposes_exact_constants() -> None:
    assert runtime.HTTP_GOSSIP_TRANSPORT_RUNTIME_VERSION == 'http_gossip_transport_runtime_1572.v0.1'
    assert runtime.CDL_061_DEPENDENCY == 'cdl_061_ratified_561.v0.1'
    assert runtime.GOSSIP_TRANSPORT_DEPENDENCY == 'gossip_transport_runtime_1572.v0.1'
    assert runtime.GOSSIP_PEER_REGISTRY_DEPENDENCY == 'gossip_peer_registry_1571.v0.1'
    assert runtime.TRANSPORT_KIND_QUIC == 'quic'
    assert runtime.TRANSPORT_KIND_HTTP == 'http'


def test_dep_chain_assertions_are_present() -> None:
    text = RUNTIME_PATH.read_text(encoding='utf-8')
    assert 'gossip_transport.GOSSIP_TRANSPORT_RUNTIME_VERSION != GOSSIP_TRANSPORT_DEPENDENCY' in text
    assert '_GOSSIP_PEER_REGISTRY_CHECK != GOSSIP_PEER_REGISTRY_DEPENDENCY' in text


def test_transport_runtime_config_requires_explicit_transport_kind_and_tls_fields(tmp_path: Path) -> None:
    field_names = [field.name for field in fields(runtime.TransportRuntimeConfig)]
    assert field_names[:5] == [
        'transport_kind',
        'bind_host',
        'bind_port',
        'tls_cert_path',
        'tls_key_path',
    ]
    assert 'verify_peer_tls' in field_names
    assert 'tls_ca_cert_path' in field_names
    cert_path, key_path = _write_tls_material(tmp_path)
    config = runtime.TransportRuntimeConfig(
        transport_kind='http',
        bind_host='127.0.0.1',
        bind_port=0,
        tls_cert_path=cert_path,
        tls_key_path=key_path,
    )
    assert config.verify_peer_tls is True
    assert config.tls_ca_cert_path == ''
    with pytest.raises(TypeError):
        runtime.TransportRuntimeConfig(bind_host='127.0.0.1', bind_port=0, tls_cert_path='a', tls_key_path='b')


def test_unknown_transport_kind_fails_with_deterministic_error_token(tmp_path: Path) -> None:
    transport = runtime.HttpGossipTransportRuntime(_config(tmp_path, transport_kind='udp'))
    with pytest.raises(ValueError, match='transport_kind_unsupported'):
        transport.start()


def test_missing_tls_configuration_fails_with_deterministic_tokens(tmp_path: Path) -> None:
    missing_cert = runtime.HttpGossipTransportRuntime(
        runtime.TransportRuntimeConfig('http', '127.0.0.1', 0, '', 'missing-key.pem')
    )
    with pytest.raises(ValueError, match='tls_cert_path_required'):
        missing_cert.start()
    missing_key = runtime.HttpGossipTransportRuntime(
        runtime.TransportRuntimeConfig('http', '127.0.0.1', 0, 'missing-cert.pem', '')
    )
    with pytest.raises(ValueError, match='tls_cert_path_not_found'):
        missing_key.start()


def test_selecting_quic_fails_deterministically(tmp_path: Path) -> None:
    transport = runtime.HttpGossipTransportRuntime(_config(tmp_path, transport_kind='quic'))
    with pytest.raises(ValueError, match='transport_kind_quic_not_operationalized'):
        transport.start()


def test_selecting_http_permits_loopback_listener_start_and_stop(tmp_path: Path) -> None:
    transport = runtime.HttpGossipTransportRuntime(_config(tmp_path))
    transport.start()
    try:
        assert transport.state['transport_kind'] == 'http'
        assert transport.state['running'] is True
        assert isinstance(transport.state['bound_port'], int)
        assert transport.state['bound_port'] > 0
    finally:
        transport.stop()
    assert transport.state['running'] is False


def test_send_gossip_uses_gossip_request_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    transport = runtime.HttpGossipTransportRuntime(_config(tmp_path))
    calls: dict[str, str] = {}

    def fake_path(message_type: str) -> str:
        calls['message_type'] = message_type
        return '/ilc/gossip/fake'

    class _FakeOpener:
        def open(self, request: urllib.request.Request, **_kw: object) -> _FakeResponse:
            calls['url'] = request.full_url
            return _FakeResponse(202)

    monkeypatch.setattr(runtime.gossip_transport, 'gossip_request_path', fake_path)
    monkeypatch.setattr(urllib.request, 'build_opener', lambda *_: _FakeOpener())

    status = transport.send_gossip(
        'https://127.0.0.1:9443',
        gossip_type='centrality_delta',
        channel='cid:1234567890abcdef',
        epoch=1,
        signature='sig-1',
    )

    assert status == 202
    assert calls['message_type'] == 'centrality_delta'
    assert calls['url'].endswith('/ilc/gossip/fake')


def test_send_gossip_uses_build_gossip_headers(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    transport = runtime.HttpGossipTransportRuntime(_config(tmp_path))
    calls: dict[str, object] = {}

    def fake_build(
        *,
        gossip_type: str,
        channel: str,
        epoch: int,
        hop_count: int,
        signature: str,
        sender_peer_id: str,
        key_id: str,
        content_type: str,
    ) -> dict[str, str]:
        calls['args'] = {
            'gossip_type': gossip_type,
            'channel': channel,
            'epoch': epoch,
            'hop_count': hop_count,
            'signature': signature,
            'sender_peer_id': sender_peer_id,
            'key_id': key_id,
            'content_type': content_type,
        }
        return {
            'ILC-Gossip-Type': gossip_type,
            'ILC-Channel': channel,
            'ILC-Epoch': str(epoch),
            'ILC-Hop-Count': '1',
            'ILC-Signature': signature,
            'ILC-Sender-Peer-Id': sender_peer_id,
            'ILC-Key-Id': key_id,
            'Content-Type': content_type,
        }

    class _FakeOpener:
        def open(self, request: urllib.request.Request, **_kw: object) -> _FakeResponse:
            calls['headers'] = dict(request.header_items())
            return _FakeResponse(202)

    monkeypatch.setattr(runtime.gossip_transport, 'build_gossip_headers', fake_build)
    monkeypatch.setattr(urllib.request, 'build_opener', lambda *_: _FakeOpener())

    status = transport.send_gossip(
        'https://127.0.0.1:9444',
        gossip_type='centrality_delta',
        channel='cid:1234567890abcdef',
        epoch=2,
        signature='sig-2',
        content_type='application/json',
    )

    assert status == 202
    assert calls['args'] == {
        'gossip_type': 'centrality_delta',
        'channel': 'cid:1234567890abcdef',
        'epoch': 2,
        'hop_count': 1,
        'signature': 'sig-2',
        'sender_peer_id': gossip_transport.LEGACY_UNVERIFIABLE_SENDER_PEER_ID,
        'key_id': gossip_transport.LEGACY_UNVERIFIABLE_KEY_ID,
        'content_type': 'application/json',
    }
    normalized_headers = {key.lower(): value for key, value in calls['headers'].items()}
    assert normalized_headers['ilc-gossip-type'] == 'centrality_delta'


def test_handle_gossip_request_uses_validate_gossip_headers(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    transport = runtime.HttpGossipTransportRuntime(_config(tmp_path))
    headers = gossip_transport.build_gossip_headers(
        gossip_type='centrality_delta',
        channel='cid:1234567890abcdef',
        epoch=3,
        hop_count=1,
        signature='sig-3',
    )
    calls: dict[str, dict[str, str]] = {}

    def fake_validate(value: dict[str, str]) -> bool:
        calls['headers'] = value
        return True

    monkeypatch.setattr(runtime.gossip_transport, 'validate_gossip_headers', fake_validate)

    status = transport.handle_gossip_request('/ilc/gossip/centrality_delta', headers)

    assert status == 202
    assert calls['headers'] == headers


def test_handle_gossip_request_rejects_payloads_above_cap(tmp_path: Path) -> None:
    transport = runtime.HttpGossipTransportRuntime(_config(tmp_path))
    headers = gossip_transport.build_gossip_headers(
        gossip_type='centrality_delta',
        channel='cid:1234567890abcdef',
        epoch=3,
        hop_count=1,
        signature='sig-3',
    )

    status = transport.handle_gossip_request(
        '/ilc/gossip/centrality_delta',
        headers,
        content_length=runtime.MAX_INBOUND_PAYLOAD_BYTES + 1,
    )

    assert status == gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
    assert transport.state['last_status_code'] == gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
    assert transport.state['event_log'][-1]['token'] == runtime.PAYLOAD_TOO_LARGE_TOKEN


def test_loopback_rejects_trickle_read_payload_with_timeout_token(tmp_path: Path) -> None:
    cert_path, key_path = _write_tls_material(tmp_path / 'server')
    server_transport = runtime.HttpGossipTransportRuntime(
        runtime.TransportRuntimeConfig(
            transport_kind='http',
            bind_host='127.0.0.1',
            bind_port=0,
            tls_cert_path=cert_path,
            tls_key_path=key_path,
            request_timeout_seconds=0.1,
        )
    )
    server_transport.start()
    try:
        payload = b'x' * 32
        headers = gossip_transport.build_gossip_headers(
            gossip_type='centrality_delta',
            channel='cid:1234567890abcdef',
            epoch=6,
            hop_count=1,
            signature='sig-6',
        )
        headers['Content-Length'] = str(len(payload))
        response = _raw_tls_post(
            port=int(server_transport.state['bound_port']),
            path=gossip_transport.gossip_request_path('centrality_delta'),
            headers=headers,
            body_prefix=payload[:1],
            body_suffix=payload[1:],
            delay_after_prefix=0.2,
            timeout=1.0,
        )
        assert b' 400 ' in response.splitlines()[0]
        assert server_transport.state['last_status_code'] == gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
        assert server_transport.state['event_log'][-1]['token'] == runtime.PAYLOAD_READ_TIMEOUT_TOKEN
    finally:
        server_transport.stop()


def test_loopback_send_receive_over_real_http_returns_success_status_code(tmp_path: Path) -> None:
    server_transport = runtime.HttpGossipTransportRuntime(_config(tmp_path / 'server'))
    client_transport = runtime.HttpGossipTransportRuntime(_config(tmp_path / 'client'))
    server_transport.start()
    try:
        endpoint = f"https://localhost:{server_transport.state['bound_port']}"
        status = client_transport.send_gossip(
            endpoint,
            gossip_type='centrality_delta',
            channel='cid:1234567890abcdef',
            epoch=4,
            signature='sig-4',
        )
        assert status == gossip_transport.HTTP_STATUS_BUFFERED
        assert server_transport.state['last_status_code'] == gossip_transport.HTTP_STATUS_BUFFERED
        event = server_transport.state['event_log'][-1]
        assert event['event'] == 'incoming_envelope_buffered'
        assert event['payload_bytes'] == 0
        assert event['payload_sha256'] == (
            'e3b0c44298fc1c149afbf4c8996fb924'
            '27ae41e4649b934ca495991b7852b855'
        )
        assert len(event['signature_sha256']) == 64
    finally:
        server_transport.stop()


def test_handle_gossip_request_rejects_payload_length_mismatch(tmp_path: Path) -> None:
    transport = runtime.HttpGossipTransportRuntime(_config(tmp_path))
    headers = gossip_transport.build_gossip_headers(
        gossip_type='centrality_delta',
        channel='cid:1234567890abcdef',
        epoch=8,
        hop_count=1,
        signature='sig-8',
    )

    status = transport.handle_gossip_request(
        '/ilc/gossip/centrality_delta',
        headers,
        content_length=16,
        payload=b'too-short',
    )

    assert status == gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
    assert transport.state['event_log'][-1]['token'] == runtime.PAYLOAD_INCOMPLETE_TOKEN


def test_loopback_rejects_oversized_payload_before_buffering(tmp_path: Path) -> None:
    server_transport = runtime.HttpGossipTransportRuntime(_config(tmp_path / 'server'))
    client_transport = runtime.HttpGossipTransportRuntime(_config(tmp_path / 'client'))
    server_transport.start()
    try:
        endpoint = f"https://localhost:{server_transport.state['bound_port']}"
        request = urllib.request.Request(
            url=f"{endpoint}/ilc/gossip/centrality_delta",
            data=b'x' * (runtime.MAX_INBOUND_PAYLOAD_BYTES + 1),
            headers=gossip_transport.build_gossip_headers(
                gossip_type='centrality_delta',
                channel='cid:1234567890abcdef',
                epoch=5,
                hop_count=1,
                signature='sig-5',
            ),
            method='POST',
        )
        with pytest.raises((urllib.error.HTTPError, urllib.error.URLError)) as exc_info:
            urllib.request.urlopen(
                request,
                timeout=client_transport.config.request_timeout_seconds,
                context=client_transport._client_ssl_context(),
            )
        if isinstance(exc_info.value, urllib.error.HTTPError):
            assert exc_info.value.code == gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
        assert server_transport.state['last_status_code'] == gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
        assert server_transport.state['event_log'][-1]['token'] == runtime.PAYLOAD_TOO_LARGE_TOKEN
    finally:
        server_transport.stop()


def test_loopback_rejects_chunked_transfer_encoding_without_body_drain(tmp_path: Path) -> None:
    server_transport = runtime.HttpGossipTransportRuntime(_config(tmp_path / 'server'))
    server_transport.start()
    try:
        headers = gossip_transport.build_gossip_headers(
            gossip_type='centrality_delta',
            channel='cid:1234567890abcdef',
            epoch=7,
            hop_count=1,
            signature='sig-7',
        )
        headers['Transfer-Encoding'] = 'chunked'
        response = _raw_tls_post(
            port=int(server_transport.state['bound_port']),
            path=gossip_transport.gossip_request_path('centrality_delta'),
            headers=headers,
            body_prefix=b'5\r\nhello',
            timeout=1.0,
        )
        assert b' 400 ' in response.splitlines()[0]
        assert server_transport.state['last_status_code'] == gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
        assert (
            server_transport.state['event_log'][-1]['token']
            == runtime.TRANSFER_ENCODING_UNSUPPORTED_TOKEN
        )
    finally:
        server_transport.stop()


def test_phase_568_main_commit_scope_is_exact() -> None:
    commit_ref = _resolve_phase_568_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(
        path in changed_paths
        for path in {
            'ilc_core/network/d2d/gossip_transport.py',
            'ilc_core/network/d2d/gossip_peer_registry.py',
            'ilc_core/network/d2d/gossip.py',
            'ilc_core/network/d2d/peer.py',
            'ilc_core/network/d2d/interface.py',
        }
    )
