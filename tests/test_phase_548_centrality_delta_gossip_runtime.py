from __future__ import annotations

import re
import subprocess
from decimal import Decimal
from pathlib import Path

from ilc_core.network.d2d import centrality_delta_gossip_runtime as runtime

RUNTIME_PATH = Path('ilc_core/network/d2d/centrality_delta_gossip_runtime.py')
TEST_PATH = Path('tests/test_phase_548_centrality_delta_gossip_runtime.py')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_546_DOC_PATH = Path('docs/specs/ilc_epoch_boundary_commit_semantics_decision_546_v0.1.md')
PHASE_548_SUBJECT_TOKEN = 'phase 548 cdl-060 centrality delta gossip runtime'
EXACT_REQUIRED_MAIN_PATHS = {
    str(RUNTIME_PATH),
    str(TEST_PATH),
}


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_548_commit_ref() -> str:
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
        if PHASE_548_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_548_commit_subject_present_but_no_qualifying_runtime_commit')
    raise AssertionError('phase_548_commit_not_present_in_local_history')


def _expected_accumulation_model() -> str:
    match = re.search(r'ACCUMULATION_MODEL = "([^"]+)"', _read(PHASE_546_DOC_PATH))
    if match is None:
        raise AssertionError('phase_546_accumulation_model_assignment_missing')
    return match.group(1)


def _valid_message() -> dict[str, object]:
    return {
        'cid': 'bafycentralitydelta',
        'score_delta': Decimal("0.2"),
        'epoch': 1,
        'signature': 'sig-alpha',
        'hop_count': 1,
        'fanout': 3,
        'channel': 'cid:9f7a8c42bb11ddee99aa22cc33ff44aa',
    }


def test_module_imports_and_exposes_required_constants() -> None:
    assert runtime.CDL_060_GOSSIP_RUNTIME_VERSION == 'centrality_delta_gossip_runtime_GAP_CDL060.v0.2'
    assert runtime.CDL_060_DEPENDENCY == 'cdl_060_ratified_541.v0.1'
    assert runtime.D2D_GOSSIP_DEPENDENCY == 'd2d_gossip_382.v0.1'
    assert runtime.CDL_052_DEPENDENCY == 'cdl_052_ratified_466.v0.1'
    assert runtime.MAX_FANOUT == 3
    assert runtime.U_FLOOR == Decimal("0.05")


def test_exact_constant_values_are_locked() -> None:
    assert runtime.CDL_060_GOSSIP_RUNTIME_VERSION == 'centrality_delta_gossip_runtime_GAP_CDL060.v0.2'
    assert runtime.CDL_060_DEPENDENCY == 'cdl_060_ratified_541.v0.1'
    assert runtime.D2D_GOSSIP_DEPENDENCY == 'd2d_gossip_382.v0.1'
    assert runtime.CDL_052_DEPENDENCY == 'cdl_052_ratified_466.v0.1'


def test_accumulation_model_matches_phase_546_selected_token() -> None:
    assert runtime.ACCUMULATION_MODEL == _expected_accumulation_model()


def test_validate_centrality_delta_message_accepts_valid_message() -> None:
    assert runtime.validate_centrality_delta_message(_valid_message()) is True


def test_validate_centrality_delta_message_rejects_hop_count_two() -> None:
    message = _valid_message()
    message['hop_count'] = 2
    try:
        runtime.validate_centrality_delta_message(message)
    except ValueError as exc:
        assert str(exc) == 'cdl_060_hop_count_violation: single_hop_only'
    else:
        raise AssertionError('expected hop_count=2 to be rejected')


def test_validate_centrality_delta_message_rejects_fanout_four() -> None:
    message = _valid_message()
    message['fanout'] = 4
    try:
        runtime.validate_centrality_delta_message(message)
    except ValueError as exc:
        assert str(exc) == 'cdl_060_fanout_violation: exceeds_bounded_fanout'
    else:
        raise AssertionError('expected fanout=4 to be rejected')


def test_validate_centrality_delta_message_rejects_empty_channel() -> None:
    message = _valid_message()
    message['channel'] = ''
    try:
        runtime.validate_centrality_delta_message(message)
    except ValueError as exc:
        assert str(exc) == 'cdl_060_channel_opacity_violation: channel_must_be_opaque'
    else:
        raise AssertionError('expected empty channel to be rejected')


def test_accumulate_centrality_delta_suppresses_delta_below_u_floor() -> None:
    state: dict[str, object] = {}
    updated = runtime.accumulate_centrality_delta('node-alpha', Decimal("0.01"), 1, state)
    if runtime.ACCUMULATION_MODEL == 'write_through':
        assert updated['node-alpha'] == Decimal("0E-12")
    else:
        assert updated['_pending'][1]['node-alpha'] == Decimal("0E-12")


def test_accumulate_centrality_delta_accumulates_valid_delta_per_selected_model() -> None:
    state: dict[str, object] = {}
    updated = runtime.accumulate_centrality_delta('node-alpha', Decimal("0.20"), 1, state)
    if runtime.ACCUMULATION_MODEL == 'write_through':
        assert updated['node-alpha'] == Decimal("0.200000000000")
    else:
        assert updated['_pending'][1]['node-alpha'] == Decimal("0.200000000000")
        assert 'node-alpha' not in updated


def test_accumulate_centrality_delta_caps_total_at_one() -> None:
    state: dict[str, object] = {}
    runtime.accumulate_centrality_delta('node-cap', Decimal("0.60"), 1, state)
    updated = runtime.accumulate_centrality_delta('node-cap', Decimal("0.60"), 1, state)
    if runtime.ACCUMULATION_MODEL == 'write_through':
        assert updated['node-cap'] == runtime.CENTRALITY_SCORE_CAP
    else:
        assert updated['_pending'][1]['node-cap'] == runtime.CENTRALITY_SCORE_CAP


def test_commit_epoch_buffer_behaves_per_selected_model_and_logs_zeroed_epoch() -> None:
    state: dict[str, object] = {}
    updated = runtime.accumulate_centrality_delta('node-alpha', Decimal("0.20"), 1, state)
    if runtime.ACCUMULATION_MODEL == 'write_through':
        committed = runtime.commit_epoch_buffer(1, updated)
        assert committed['node-alpha'] == Decimal("0.200000000000")
        assert '_pending' not in committed
        return

    committed = runtime.commit_epoch_buffer(1, updated)
    assert committed['node-alpha'] == Decimal("0.200000000000")
    assert 1 not in committed.get('_pending', {})

    committed['_zeroed_epochs'] = {2}
    committed = runtime.commit_epoch_buffer(2, committed)
    assert {'event': 'epoch_buffer_zeroed', 'epoch': 2, 'reason': 'crash_recovery_graceful_zero'} in committed['_event_log']


def test_phase_548_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_548_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_548_main_commit_scope_is_limited_to_new_runtime_and_test() -> None:
    commit_ref = _resolve_phase_548_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert 'ilc_core/network/d2d/gossip.py' not in changed_paths
    assert 'ilc_core/network/d2d/peer.py' not in changed_paths
    assert 'ilc_core/network/d2d/interface.py' not in changed_paths
    assert all(path.startswith('ilc_core/network/d2d/') or path == str(TEST_PATH) for path in changed_paths)
