from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from ilc_core.network.d2d import centrality_delta_gossip_runtime as runtime

RUNTIME_PATH = Path('ilc_core/network/d2d/centrality_delta_gossip_runtime.py')
CANARY_PATH = Path('tools/run_mutation_canary_phase_297.py')
PHASE_548_TEST_PATH = Path('tests/test_phase_548_centrality_delta_gossip_runtime.py')
TEST_PATH = Path('tests/test_phase_549_centrality_delta_gossip_runtime_hardening.py')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_549_SUBJECT_TOKEN = 'phase 549 cdl-060 gossip runtime hardening'
EXACT_REQUIRED_MAIN_PATHS = {
    str(RUNTIME_PATH),
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


def _resolve_phase_549_commit_ref() -> str:
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
        if PHASE_549_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_549_commit_subject_present_but_no_qualifying_hardening_commit')
    raise AssertionError('phase_549_commit_not_present_in_local_history')


def _valid_message() -> dict[str, object]:
    return {
        'cid': 'bafycentralitydelta',
        'score_delta': 0.20,
        'epoch': 1,
        'signature': 'sig-alpha',
        'hop_count': 1,
        'fanout': 3,
        'channel': 'cid:9f7a8c42bb11ddee99aa22cc33ff44aa',
    }


def test_fanout_boundary_accepts_three_and_rejects_four() -> None:
    assert runtime.validate_centrality_delta_message(_valid_message()) is True
    message = _valid_message()
    message['fanout'] = 4
    try:
        runtime.validate_centrality_delta_message(message)
    except ValueError as exc:
        assert str(exc) == 'cdl_060_fanout_violation: exceeds_bounded_fanout'
    else:
        raise AssertionError('expected fanout=4 to be rejected')


def test_hop_count_zero_is_rejected_with_correct_token() -> None:
    message = _valid_message()
    message['hop_count'] = 0
    try:
        runtime.validate_centrality_delta_message(message)
    except ValueError as exc:
        assert str(exc) == 'cdl_060_hop_count_violation: single_hop_only'
    else:
        raise AssertionError('expected hop_count=0 to be rejected')


def test_whitespace_only_channel_is_rejected_with_correct_token() -> None:
    message = _valid_message()
    message['channel'] = '   '
    try:
        runtime.validate_centrality_delta_message(message)
    except ValueError as exc:
        assert str(exc) == 'cdl_060_channel_opacity_violation: channel_must_be_opaque'
    else:
        raise AssertionError('expected whitespace-only channel to be rejected')


def test_u_floor_boundary_is_inclusive() -> None:
    low_state: dict[str, object] = {}
    boundary_state: dict[str, object] = {}
    runtime.accumulate_centrality_delta('node-low', 0.04, 1, low_state)
    runtime.accumulate_centrality_delta('node-boundary', runtime.U_FLOOR, 1, boundary_state)

    if runtime.ACCUMULATION_MODEL == 'write_through':
        assert low_state['node-low'] == 0.0
        assert boundary_state['node-boundary'] == runtime.U_FLOOR
    else:
        assert low_state['_pending'][1]['node-low'] == 0.0
        assert boundary_state['_pending'][1]['node-boundary'] == runtime.U_FLOOR


def test_epoch_rollover_behaves_per_selected_accumulation_model() -> None:
    state: dict[str, object] = {}
    runtime.accumulate_centrality_delta('node-alpha', 0.20, 1, state)
    committed = runtime.commit_epoch_buffer(1, state)

    if runtime.ACCUMULATION_MODEL == 'write_through':
        assert committed['node-alpha'] == 0.2
        assert '_pending' not in committed
        return

    assert committed['node-alpha'] == 0.2
    assert 1 not in committed.get('_pending', {})
    runtime.accumulate_centrality_delta('node-alpha', 0.10, 2, committed)
    assert committed['_pending'][2]['node-alpha'] == 0.1
    runtime.commit_epoch_buffer(2, committed)
    assert committed['node-alpha'] == 0.3
    assert 2 not in committed.get('_pending', {})


def test_mutation_canary_dry_run_lists_new_centrality_delta_probes() -> None:
    result = subprocess.run(
        [sys.executable, 'tools/run_mutation_canary_phase_297.py', '--dry-run'],
        capture_output=True,
        check=True,
        text=True,
    )
    stdout = result.stdout
    assert 'centrality_delta_gossip_version_guard' in stdout
    assert 'centrality_delta_gossip_d2d_dependency_guard' in stdout
    assert 'ilc_core/network/d2d/centrality_delta_gossip_runtime.py' in stdout


def test_phase_549_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_549_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(PHASE_548_TEST_PATH) not in changed_paths


def test_phase_549_main_commit_scope_is_limited_to_runtime_canary_and_test() -> None:
    commit_ref = _resolve_phase_549_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert 'ilc_core/network/d2d/gossip.py' not in changed_paths
    assert 'ilc_core/network/d2d/peer.py' not in changed_paths
    assert 'ilc_core/network/d2d/interface.py' not in changed_paths
    assert all(
        path.startswith('ilc_core/network/d2d/')
        or path == str(CANARY_PATH)
        or path == str(TEST_PATH)
        for path in changed_paths
    )
