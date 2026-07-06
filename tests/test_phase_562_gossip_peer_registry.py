from __future__ import annotations

import importlib
import subprocess
from pathlib import Path

from ilc_core.network.d2d import gossip_peer_registry

REGISTRY_PATH = Path('ilc_core/network/d2d/gossip_peer_registry.py')
TEST_PATH = Path('tests/test_phase_562_gossip_peer_registry.py')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_562_SUBJECT_TOKEN = 'phase 562 static gossip peer registry'
EXACT_REQUIRED_MAIN_PATHS = {
    str(REGISTRY_PATH),
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


def _resolve_phase_562_commit_ref() -> str:
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
        if 'phase 562' not in lowered or 'peer registry' not in lowered:
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_562_commit_subject_present_but_no_qualifying_registry_commit')
    raise AssertionError('phase_562_commit_not_present_in_local_history')


def _assert_phase_562_runtime_mutation_scope(commit_ref: str) -> None:
    changed_paths = _changed_paths_for_commit(commit_ref)
    name_status = _name_status_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert all(
        not path.startswith('ilc_core/') or path.startswith('ilc_core/network/d2d/')
        for path in changed_paths
    )
    assert 'ilc_core/network/d2d/gossip_transport.py' not in changed_paths
    assert 'ilc_core/network/d2d/gossip.py' not in changed_paths
    assert 'ilc_core/network/d2d/peer.py' not in changed_paths
    assert 'ilc_core/network/d2d/interface.py' not in changed_paths
    assert name_status[str(REGISTRY_PATH)] == 'A'


def test_module_imports_without_error_and_exposes_required_constants() -> None:
    module = importlib.import_module('ilc_core.network.d2d.gossip_peer_registry')
    assert module.GOSSIP_PEER_REGISTRY_VERSION == 'gossip_peer_registry_1571.v0.1'
    assert module.PEER_DISCOVERY_MODE == 'static_v1'


def test_all_constants_have_exact_expected_values() -> None:
    assert gossip_peer_registry.GOSSIP_PEER_REGISTRY_VERSION == 'gossip_peer_registry_1571.v0.1'
    assert gossip_peer_registry.CDL_061_DEPENDENCY == 'cdl_061_ratified_561.v0.1'
    assert gossip_peer_registry.CDL_039_DEPENDENCY == 'cdl_039_ratified_379.v0.1'
    assert gossip_peer_registry.GOSSIP_TRANSPORT_DEPENDENCY == 'gossip_transport_runtime_1572.v0.1'
    assert gossip_peer_registry.PEER_DISCOVERY_MODE == 'static_v1'
    assert gossip_peer_registry.MAX_PEERS == 16


def test_validate_peer_endpoint_accepts_https_with_port() -> None:
    assert (
        gossip_peer_registry.validate_peer_endpoint('https://node1.example.com:8443')
        == 'https://node1.example.com:8443'
    )


def test_validate_peer_endpoint_rejects_http_scheme() -> None:
    try:
        gossip_peer_registry.validate_peer_endpoint('http://node1.example.com')
    except ValueError as exc:
        assert 'peer_endpoint_must_use_https' in str(exc)
    else:
        raise AssertionError('expected ValueError for non-https endpoint')


def test_registry_peer_count_reflects_registered_peers() -> None:
    registry = gossip_peer_registry.GossipPeerRegistry([
        'https://a.example.com',
        'https://b.example.com',
    ])
    assert registry.peer_count() == 2


def test_get_peers_returns_copy_not_internal_reference() -> None:
    registry = gossip_peer_registry.GossipPeerRegistry(['https://a.example.com'])
    peers = registry.get_peers()
    peers.append('https://b.example.com')
    assert registry.get_peers() == ['https://a.example.com']


def test_registry_rejects_peer_lists_larger_than_max_peers() -> None:
    peers = [f'https://node{i}.example.com' for i in range(17)]
    try:
        gossip_peer_registry.GossipPeerRegistry(peers)
    except ValueError as exc:
        assert str(exc) == 'peer_registry_exceeds_max_peers'
    else:
        raise AssertionError('expected ValueError for oversized registry')


def test_select_fanout_peers_returns_lexicographic_peers_after_exclusions() -> None:
    registry = gossip_peer_registry.GossipPeerRegistry([
        'https://node-c.example.com',
        'https://node-a.example.com',
        'https://node-e.example.com',
        'https://node-b.example.com',
        'https://node-d.example.com',
    ])
    assert registry.select_fanout_peers(3, exclude=['https://node-a.example.com']) == [
        'https://node-b.example.com',
        'https://node-c.example.com',
        'https://node-d.example.com',
    ]


def test_select_fanout_peers_rejects_non_positive_fanout() -> None:
    registry = gossip_peer_registry.GossipPeerRegistry(['https://a.example.com'])
    try:
        registry.select_fanout_peers(0)
    except ValueError as exc:
        assert 'fanout_must_be_positive' in str(exc)
    else:
        raise AssertionError('expected ValueError for non-positive fanout')


def test_source_contains_cdl_039_topology_invariant_assert() -> None:
    assert 'cdl_039_topology_privacy' in REGISTRY_PATH.read_text(encoding='utf-8')


def test_phase_562_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_562_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_562_main_commit_scope_is_limited_to_new_registry_file() -> None:
    commit_ref = _resolve_phase_562_commit_ref()
    _assert_phase_562_runtime_mutation_scope(commit_ref)
