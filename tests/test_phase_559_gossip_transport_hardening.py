from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.network.d2d import gossip_transport

CANARY_PATH = Path('tools/run_mutation_canary_phase_297.py')
TEST_PATH = Path('tests/test_phase_559_gossip_transport_hardening.py')
TRANSPORT_PATH = Path('ilc_core/network/d2d/gossip_transport.py')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_559_SUBJECT_TOKEN = 'phase 559 gossip transport adapter hardening'
EXACT_REQUIRED_MAIN_PATHS = {
    str(CANARY_PATH),
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


def _resolve_phase_559_commit_ref() -> str:
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
        if 'phase 559' not in lowered or 'hardening' not in lowered:
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_559_commit_subject_present_but_no_qualifying_hardening_commit')
    raise AssertionError('phase_559_commit_not_present_in_local_history')


def _base_headers() -> dict[str, str]:
    return gossip_transport.build_gossip_headers(
        gossip_type='centrality_delta',
        channel='cid:9f7a8c42bb11ddee99aa22cc33ff44aa',
        epoch=7,
        hop_count=1,
        signature='sig-abc',
    )


def test_cdl_039_creator_agent_id_is_in_forbidden_set() -> None:
    assert 'creator_agent_id' in gossip_transport.FORBIDDEN_HEADER_KEYS


def test_cdl_039_node_id_variants_are_in_forbidden_set() -> None:
    assert 'node_id' in gossip_transport.FORBIDDEN_HEADER_KEYS
    assert 'ILC-Node-Id' in gossip_transport.FORBIDDEN_HEADER_KEYS
    assert 'ILC-Creator-Agent-Id' in gossip_transport.FORBIDDEN_HEADER_KEYS


def test_validate_gossip_headers_rejects_all_four_forbidden_keys_and_hop_count_failures() -> None:
    for key in gossip_transport.FORBIDDEN_HEADER_KEYS:
        headers = _base_headers()
        headers[key] = 'forbidden'
        try:
            gossip_transport.validate_gossip_headers(headers)
        except ValueError as exc:
            assert 'cdl_039_violation' in str(exc)
        else:
            raise AssertionError(f'expected ValueError for forbidden key {key}')

    missing_hop_headers = _base_headers()
    missing_hop_headers.pop('ILC-Hop-Count')
    try:
        gossip_transport.validate_gossip_headers(missing_hop_headers)
    except ValueError as exc:
        assert 'missing_required_header:ILC-Hop-Count' == str(exc)
    else:
        raise AssertionError('expected ValueError for missing hop-count header')

    bad_hop_headers = _base_headers()
    bad_hop_headers['ILC-Hop-Count'] = '2'
    try:
        gossip_transport.validate_gossip_headers(bad_hop_headers)
    except ValueError as exc:
        assert 'cdl_060_hop_count_violation' in str(exc)
    else:
        raise AssertionError('expected ValueError for hop-count two')


def test_build_gossip_headers_cbor_default_json_permitted_and_whitespace_channel_rejected() -> None:
    default_headers = _base_headers()
    assert default_headers['Content-Type'] == 'application/cbor'

    json_headers = gossip_transport.build_gossip_headers(
        gossip_type='centrality_delta',
        channel='cid:9f7a8c42bb11ddee99aa22cc33ff44aa',
        epoch=7,
        hop_count=1,
        signature='sig-abc',
        content_type='application/json',
    )
    assert json_headers['Content-Type'] == 'application/json'

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


def test_build_gossip_headers_unsupported_content_type_rejected() -> None:
    try:
        gossip_transport.build_gossip_headers(
            gossip_type='centrality_delta',
            channel='cid:9f7a8c42bb11ddee99aa22cc33ff44aa',
            epoch=7,
            hop_count=1,
            signature='sig-abc',
            content_type='text/plain',
        )
    except ValueError as exc:
        assert str(exc) == 'unsupported_content_type'
    else:
        raise AssertionError('expected ValueError for unsupported content type')


def test_canary_probe_6_dry_run_lists_transport_cdl_039_probe() -> None:
    result = subprocess.run(
        ['python3', str(CANARY_PATH), '--dry-run'],
        capture_output=True,
        check=True,
        text=True,
    )
    assert 'gossip_transport_cdl_039_forbidden_key_guard' in result.stdout


def test_phase_559_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_559_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_559_main_commit_does_not_touch_cdl_or_ilc_core() -> None:
    commit_ref = _resolve_phase_559_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert str(TRANSPORT_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
