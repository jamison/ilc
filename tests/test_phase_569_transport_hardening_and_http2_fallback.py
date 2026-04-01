from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ilc_core.network.d2d import gossip_transport
from ilc_core.network.d2d import http_gossip_transport_runtime as runtime
from tests.test_phase_568_real_http_transport_wrapper_runtime import _write_tls_material


RUNTIME_PATH = Path('ilc_core/network/d2d/http_gossip_transport_runtime.py')
CANARY_PATH = Path('tools/run_mutation_canary_phase_297.py')
TEST_PATH = Path('tests/test_phase_569_transport_hardening_and_http2_fallback.py')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_569_SUBJECT_TOKEN = 'phase 569 transport hardening and explicit fallback'
EXACT_REQUIRED_MAIN_PATHS = {
    str(RUNTIME_PATH),
    str(CANARY_PATH),
    str(TEST_PATH),
}


def _config(tmp_path: Path, *, transport_kind: str = runtime.TRANSPORT_KIND_HTTP) -> runtime.TransportRuntimeConfig:
    cert_path, key_path = _write_tls_material(tmp_path)
    return runtime.TransportRuntimeConfig(
        transport_kind=transport_kind,
        bind_host='127.0.0.1',
        bind_port=0,
        tls_cert_path=cert_path,
        tls_key_path=key_path,
    )


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _dry_run_output() -> str:
    result = subprocess.run(
        ['python3', str(CANARY_PATH), '--dry-run'],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout


def _resolve_phase_569_commit_ref() -> str:
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
        if PHASE_569_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    raise AssertionError('phase_569_commit_not_present_in_local_history')


def test_explicit_http_fallback_path_succeeds_in_loopback_mode(tmp_path: Path) -> None:
    server_transport = runtime.HttpGossipTransportRuntime(_config(tmp_path / 'server'))
    client_transport = runtime.HttpGossipTransportRuntime(_config(tmp_path / 'client'))
    server_transport.start()
    try:
        endpoint = f"https://127.0.0.1:{server_transport.state['bound_port']}"
        status = client_transport.send_gossip(
            endpoint,
            gossip_type='centrality_delta',
            channel='cid:1234567890abcdef',
            epoch=9,
            signature='sig-9',
        )
        assert status == gossip_transport.HTTP_STATUS_BUFFERED
        assert server_transport.state['explicit_fallback_proof'] is True
    finally:
        server_transport.stop()


def test_explicit_quic_path_fails_deterministically(tmp_path: Path) -> None:
    transport = runtime.HttpGossipTransportRuntime(_config(tmp_path, transport_kind='quic'))
    with pytest.raises(ValueError, match='transport_kind_quic_not_operationalized'):
        transport.start()


def test_missing_tls_inputs_fail_with_deterministic_tokens() -> None:
    runtime_missing = runtime.HttpGossipTransportRuntime(
        runtime.TransportRuntimeConfig('http', '127.0.0.1', 0, '', '')
    )
    with pytest.raises(ValueError, match='tls_cert_path_required'):
        runtime_missing.start()
    runtime_missing_file = runtime.HttpGossipTransportRuntime(
        runtime.TransportRuntimeConfig('http', '127.0.0.1', 0, 'missing-cert.pem', 'missing-key.pem')
    )
    with pytest.raises(ValueError, match='tls_cert_path_not_found'):
        runtime_missing_file.start()


def test_request_failure_path_produces_structured_transport_error_output(tmp_path: Path) -> None:
    transport = runtime.HttpGossipTransportRuntime(_config(tmp_path))
    with pytest.raises(runtime.TransportRuntimeError, match='transport_request_failed') as exc_info:
        transport.send_gossip(
            'https://127.0.0.1:65530',
            gossip_type='centrality_delta',
            channel='cid:1234567890abcdef',
            epoch=10,
            signature='sig-10',
        )
    assert exc_info.value.token == 'transport_request_failed'
    assert exc_info.value.transport_kind == 'http'
    assert transport.state['last_error']['token'] == 'transport_request_failed'
    assert transport.state['last_error']['transport_kind'] == 'http'


def test_selected_transport_kind_is_observable_in_runtime_state(tmp_path: Path) -> None:
    transport = runtime.HttpGossipTransportRuntime(_config(tmp_path))
    transport.start()
    try:
        assert transport.state['transport_kind'] == 'http'
        assert transport.state['explicit_fallback_proof'] is True
    finally:
        transport.stop()


def test_runtime_does_not_silently_downgrade_from_quic_to_http(tmp_path: Path) -> None:
    transport = runtime.HttpGossipTransportRuntime(_config(tmp_path, transport_kind='quic'))
    with pytest.raises(ValueError, match='transport_kind_quic_not_operationalized'):
        transport.start()
    assert transport.state['transport_kind'] == 'quic'
    assert transport.state.get('explicit_fallback_proof') is None


def test_canary_dry_run_contains_probe_9_transport_runtime_version_guard() -> None:
    output = _dry_run_output()
    assert output.count('] ') == 9
    assert 'http_gossip_transport_runtime_version_guard' in output


def test_phase_569_main_commit_scope_is_exact() -> None:
    commit_ref = _resolve_phase_569_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert 'ilc_core/network/d2d/gossip_transport.py' not in changed_paths
    assert 'ilc_core/network/d2d/gossip_peer_registry.py' not in changed_paths
