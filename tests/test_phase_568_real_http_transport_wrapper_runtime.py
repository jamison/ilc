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
    MIIDCTCCAfGgAwIBAgIUJyHAyiCrnelqu8A0dVbG9QA7mIkwDQYJKoZIhvcNAQEL
    BQAwFDESMBAGA1UEAwwJbG9jYWxob3N0MB4XDTI2MDQwMTA3MTUzOVoXDTI2MDQw
    MjA3MTUzOVowFDESMBAGA1UEAwwJbG9jYWxob3N0MIIBIjANBgkqhkiG9w0BAQEF
    AAOCAQ8AMIIBCgKCAQEAmuEqPXvtZPoMGeBS3RQLDDAQDL2dSQOA1OQroSUYqzxq
    GItc1SnDbMrwmpH5f3tr12ynlUGsmHE2yMmbh3bCzt4UVWPEY9Vqkn/28TCSlPZ7
    MQ9dHRTj9a22jw25PE/76HzU0pCKXqHRXG/2+IJwT8B9iUkHGN+Gb4behEm7D7qh
    xOQkr2EKuTGCFO5bAGKee4bBAavpLcQk0SW++7hKTSFgE2WWQvTyqe30a2UFvIPU
    F9m5eVzrSlElh+1Gnehrk6yk5N+MofjoMmyAX5PbsgG+sAq1Arj2hRVvrBIojQ3q
    qEHe9gE07leREMNqWQnD6aOcdKN3jJ7Q1RlOyS5wPwIDAQABo1MwUTAdBgNVHQ4E
    FgQUlURz0tvvmz3zvJeiA3xiGt7N9ngwHwYDVR0jBBgwFoAUlURz0tvvmz3zvJei
    A3xiGt7N9ngwDwYDVR0TAQH/BAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAQEAWDa+
    eX311yStBkHDDSDq1gYqYJIsmnCj4ikaEqM+99Jed3V4C0IeFPcKuCm9K4JJSPy2
    t9qmP2gSWTk7qEmhkeL9q9yakXvmrplXLUrBpJJTjJe5fnk8hlYGD4Fn3gxVajAF
    lVRRcOb2JQpf3U1Q36/YqyuQWEFZL+0s6S71F+pA//KAhF+xSZHHjABnpYLWI9Wq
    t0L8vc+ulxcjvH0+MbIdARIg/U4vLMMtaP7tUjzW4Da4k49yyG+norSxH3Fjny3L
    xLNUe5UQw5w5MKzMHZnLOaOejYDR4X14nJQGic9dOi//j85C99nRAoARj9mzKZ+/
    HvxRTHxHMY2Mgd+IEA==
    -----END CERTIFICATE-----
    """
)

_KEY_PEM = textwrap.dedent(
    """\
    -----BEGIN PRIVATE KEY-----
    MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCa4So9e+1k+gwZ
    4FLdFAsMMBAMvZ1JA4DU5CuhJRirPGoYi1zVKcNsyvCakfl/e2vXbKeVQayYcTbI
    yZuHdsLO3hRVY8Rj1WqSf/bxMJKU9nsxD10dFOP1rbaPDbk8T/vofNTSkIpeodFc
    b/b4gnBPwH2JSQcY34Zvht6ESbsPuqHE5CSvYQq5MYIU7lsAYp57hsEBq+ktxCTR
    Jb77uEpNIWATZZZC9PKp7fRrZQW8g9QX2bl5XOtKUSWH7Uad6GuTrKTk34yh+Ogy
    bIBfk9uyAb6wCrUCuPaFFW+sEiiNDeqoQd72ATTuV5EQw2pZCcPpo5x0o3eMntDV
    GU7JLnA/AgMBAAECggEAPYyi6TlBL+JRAc2MkLAg7dCB6FZIVdZPEgu1LP6djZte
    PG/RziKhN7B0qrC9OsTVKBDVjnLBgPlpAKViKhTvuR83bHHP/662Ag9ZlyMq9Yj4
    jxggdGizaRSGWtZk2Uud/BfzydRIMPBUz8vtFXhc4szH9tFvQRq/hb3O2zqj3M07
    m7q0gWX4qday7xuhrBoVmhoe3O7gNxENIvzpZCYdgbWFruqGFSFeJloYQ+YCtr8B
    WO6M03Sry/WDbUw9u0hAUBcoDju5ezfqxqvDs7H0S5u+EOO5zcM85ZtKPJFzo0k7
    NtAU4vkmOkpXD0fLdeXTd145CATPb/uGSZpm2lhsUQKBgQDNLB7NHvVz6kD4H7C8
    v5CYFOksHmzJ5eenjW6wQg0BNw8+nvXIkbotWUIppRyhq5t2tuYMmSeprDRyuPYf
    UnBQ8QuV8PB7DBbV+TSONeWqVlcKeqRD15Go+z0B4DF3KQdvZd2e3nVzYCMIN9hd
    0yd/+M85dbWuAxJxiW4L5bdfsQKBgQDBP4M2gdBpsE2NGa/s9ZMJYdicqsUR509g
    oFni8J6xTazQ3+TTm6jbREsk4ArxFHu/7uDp2h0m/lze0PRIdW+G6q7vnPYQqDxG
    ZtJCAwPmVciZH2EtMuiQzBQas1yLnoLY2pJBLDOwLsgKNcCxJIlIJBArcCUHTUt+
    +qskza467wKBgHdYlMoomgrFVul+NaZ1oDx23XPGdu2yiGAUizCIG1x7lKiOetYi
    vrOmWjAzVUZNtm8F0Se+5y1xeEjLgo+Rure6n0ynDJvm2lm5TnLysxe0hYkY8fhs
    qtQq4L/4k42HFkYccR/6s0NbxsT/ByL8sttj9dasu/Pu4YmdsZ/GDjbhAoGBAJif
    wNHb1O6j/5vhHcDYcziFvr59YQey2E5IVrWVtL/zyPlu2xsFZWdHmNGW4Q1mUBZW
    Y+xOB5g0bMTN4yEXHu4/i8pS/URKmtA/hO/90aapObU1w1ofSu6RP4+W+RCMMGt0
    tO4kKu6LBBKMQZOmd4YydVLZT2Vk9qti7qgyidihAoGAfCkCMVVaoJwLya4G6lRg
    MwmTr33+KmZPgDXHrhK61nmnZV+dj06Y5FKXyBuiY2kCm4sTfae6UDRCzwXVpY52
    INm9arf6osBw5qoWlmNcOWVt5R2bbptHgNFfdeVtqNQLq7A4phhqpJgbTwfAySdd
    7r7LPPxpLIkIn0gKmleNDMc=
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
    assert runtime.HTTP_GOSSIP_TRANSPORT_RUNTIME_VERSION == 'http_gossip_transport_runtime_568.v0.1'
    assert runtime.CDL_061_DEPENDENCY == 'cdl_061_ratified_561.v0.1'
    assert runtime.GOSSIP_TRANSPORT_DEPENDENCY == 'gossip_transport_runtime_558.v0.1'
    assert runtime.GOSSIP_PEER_REGISTRY_DEPENDENCY == 'gossip_peer_registry_562.v0.1'
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
    cert_path, key_path = _write_tls_material(tmp_path)
    config = runtime.TransportRuntimeConfig(
        transport_kind='http',
        bind_host='127.0.0.1',
        bind_port=0,
        tls_cert_path=cert_path,
        tls_key_path=key_path,
    )
    assert config.verify_peer_tls is True
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

    def fake_build(*, gossip_type: str, channel: str, epoch: int, hop_count: int, signature: str, content_type: str) -> dict[str, str]:
        calls['args'] = {
            'gossip_type': gossip_type,
            'channel': channel,
            'epoch': epoch,
            'hop_count': hop_count,
            'signature': signature,
            'content_type': content_type,
        }
        return {
            'ILC-Gossip-Type': gossip_type,
            'ILC-Channel': channel,
            'ILC-Epoch': str(epoch),
            'ILC-Hop-Count': '1',
            'ILC-Signature': signature,
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
        endpoint = f"https://127.0.0.1:{server_transport.state['bound_port']}"
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
        endpoint = f"https://127.0.0.1:{server_transport.state['bound_port']}"
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
