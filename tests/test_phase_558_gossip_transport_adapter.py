from __future__ import annotations

import importlib
import subprocess
from pathlib import Path

from ilc_core.network.d2d import gossip_transport

TRANSPORT_PATH = Path('ilc_core/network/d2d/gossip_transport.py')
TEST_PATH = Path('tests/test_phase_558_gossip_transport_adapter.py')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_558_SUBJECT_TOKEN = 'phase 558 http gossip transport adapter'
EXACT_REQUIRED_MAIN_PATHS = {
    str(TRANSPORT_PATH),
    str(TEST_PATH),
}


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _name_status_for_commit(commit_ref: str) -> dict[str, str]:
    result = subprocess.run(
        ['git', 'show', '--name-status', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    statuses: dict[str, str] = {}
    for line in result.stdout.splitlines():
        parts = line.split('\t')
        if len(parts) != 2:
            continue
        status, path = parts
        statuses[path] = status
    return statuses


def _resolve_phase_558_commit_ref() -> str:
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
        lowered = subject.lower()
        if 'phase 558' not in lowered or 'gossip transport' not in lowered:
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_558_commit_subject_present_but_no_qualifying_transport_commit')
    raise AssertionError('phase_558_commit_not_present_in_local_history')


def _assert_phase_558_runtime_mutation_scope(commit_ref: str) -> None:
    changed_paths = _changed_paths_for_commit(commit_ref)
    name_status = _name_status_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert all(
        not path.startswith('ilc_core/') or path.startswith('ilc_core/network/d2d/')
        for path in changed_paths
    )
    assert 'ilc_core/network/d2d/gossip.py' not in changed_paths
    assert 'ilc_core/network/d2d/peer.py' not in changed_paths
    assert 'ilc_core/network/d2d/interface.py' not in changed_paths
    assert name_status[str(TRANSPORT_PATH)] == 'A'


def test_module_imports_without_error_and_exposes_constants() -> None:
    module = importlib.import_module('ilc_core.network.d2d.gossip_transport')
    assert module.GOSSIP_TRANSPORT_RUNTIME_VERSION == 'gossip_transport_runtime_558.v0.1'
    assert module.REQUIRED_HEADERS == gossip_transport.REQUIRED_HEADERS


def test_all_constants_have_exact_expected_values() -> None:
    assert gossip_transport.GOSSIP_TRANSPORT_RUNTIME_VERSION == 'gossip_transport_runtime_558.v0.1'
    assert gossip_transport.CDL_061_DEPENDENCY == 'cdl_061_ratified_561.v0.1'
    assert gossip_transport.CDL_039_DEPENDENCY == 'cdl_039_ratified_379.v0.1'
    assert gossip_transport.CDL_060_GOSSIP_RUNTIME_DEPENDENCY == 'cdl_060_gossip_runtime_548.v0.1'
    assert gossip_transport.HOP_COUNT_SINGLE == 1
    assert gossip_transport.GOSSIP_URL_PREFIX == '/ilc/gossip/'


def test_gossip_request_path_returns_expected_path() -> None:
    assert gossip_transport.gossip_request_path('centrality_delta') == '/ilc/gossip/centrality_delta'


def test_gossip_request_path_rejects_empty_string() -> None:
    try:
        gossip_transport.gossip_request_path('')
    except ValueError as exc:
        assert str(exc) == 'gossip_message_type_must_be_non_empty_string'
    else:
        raise AssertionError('expected ValueError for empty message type')


def test_gossip_type_header_rejects_oversized_value() -> None:
    oversized = 'g' * (gossip_transport.MAX_GOSSIP_TYPE_BYTES + 1)
    try:
        gossip_transport.gossip_request_path(oversized)
    except ValueError as exc:
        assert str(exc) == 'gossip_message_type_too_long'
    else:
        raise AssertionError('expected ValueError for oversized gossip type')

    headers = gossip_transport.build_gossip_headers(
        gossip_type='centrality_delta',
        channel='cid:9f7a8c42bb11ddee99aa22cc33ff44aa',
        epoch=7,
        hop_count=1,
        signature='sig-abc',
    )
    headers['ILC-Gossip-Type'] = oversized
    try:
        gossip_transport.validate_gossip_headers(headers)
    except ValueError as exc:
        assert str(exc) == 'gossip_message_type_too_long'
    else:
        raise AssertionError('expected ValueError for oversized gossip type header')


def test_build_gossip_headers_returns_exact_required_header_set() -> None:
    headers = gossip_transport.build_gossip_headers(
        gossip_type='centrality_delta',
        channel='cid:9f7a8c42bb11ddee99aa22cc33ff44aa',
        epoch=7,
        hop_count=1,
        signature='sig-abc',
    )
    assert set(headers) == gossip_transport.REQUIRED_HEADERS
    assert headers['ILC-Gossip-Type'] == 'centrality_delta'
    assert headers['ILC-Hop-Count'] == '1'
    assert headers['Content-Type'] == 'application/cbor'


def test_build_gossip_headers_rejects_non_single_hop_count() -> None:
    try:
        gossip_transport.build_gossip_headers(
            gossip_type='centrality_delta',
            channel='cid:9f7a8c42bb11ddee99aa22cc33ff44aa',
            epoch=7,
            hop_count=2,
            signature='sig-abc',
        )
    except ValueError as exc:
        assert 'cdl_060_hop_count_must_be_single' in str(exc)
    else:
        raise AssertionError('expected ValueError for non-single hop count')


def test_build_gossip_headers_rejects_whitespace_only_channel() -> None:
    try:
        gossip_transport.build_gossip_headers(
            gossip_type='centrality_delta',
            channel='   ',
            epoch=7,
            hop_count=1,
            signature='sig-abc',
        )
    except ValueError as exc:
        assert 'cdl_039_channel_must_be_opaque' in str(exc)
    else:
        raise AssertionError('expected ValueError for whitespace-only channel')


def test_validate_gossip_headers_accepts_valid_headers() -> None:
    headers = gossip_transport.build_gossip_headers(
        gossip_type='centrality_delta',
        channel='cid:9f7a8c42bb11ddee99aa22cc33ff44aa',
        epoch=7,
        hop_count=1,
        signature='sig-abc',
    )
    assert gossip_transport.validate_gossip_headers(headers) is True


def test_validate_gossip_headers_rejects_forbidden_creator_agent_id_header() -> None:
    headers = gossip_transport.build_gossip_headers(
        gossip_type='centrality_delta',
        channel='cid:9f7a8c42bb11ddee99aa22cc33ff44aa',
        epoch=7,
        hop_count=1,
        signature='sig-abc',
    )
    headers['creator_agent_id'] = 'agent-1'
    try:
        gossip_transport.validate_gossip_headers(headers)
    except ValueError as exc:
        assert 'cdl_039_violation' in str(exc)
    else:
        raise AssertionError('expected ValueError for forbidden creator_agent_id header')


def test_validate_gossip_headers_rejects_hop_count_two() -> None:
    headers = gossip_transport.build_gossip_headers(
        gossip_type='centrality_delta',
        channel='cid:9f7a8c42bb11ddee99aa22cc33ff44aa',
        epoch=7,
        hop_count=1,
        signature='sig-abc',
    )
    headers['ILC-Hop-Count'] = '2'
    try:
        gossip_transport.validate_gossip_headers(headers)
    except ValueError as exc:
        assert 'cdl_060_hop_count_violation' in str(exc)
    else:
        raise AssertionError('expected ValueError for hop-count violation')


def test_phase_558_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_558_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_558_main_commit_scope_is_limited_to_new_transport_file() -> None:
    commit_ref = _resolve_phase_558_commit_ref()
    _assert_phase_558_runtime_mutation_scope(commit_ref)
